# Cloud Implementation Plan for Secure File Sharing

## Project Topic Alignment

Design and Implementation of a Secure Cloud-Based File Sharing System with Integrated Access Control and Encryption.

This implementation keeps encrypted files in cloud object storage and keeps only user data, access-control metadata, and performance/security logs in PostgreSQL.

## Final Data Placement Model

### Stored in Cloud Object Storage

- Encrypted file binary objects only (`.enc`).
- Optional encrypted file checksum metadata as object tags.

### Stored in PostgreSQL

- Users and authentication records.
- File metadata (owner, original filename, size, object key, checksum, upload time).
- Sharing/access-control mappings (who can access which file).
- Event/performance logs (encryption time, upload time, download speed, decryption time, failures).

### Not Stored in PostgreSQL

- Raw file content.
- Plain (unencrypted) file binaries.

## Recommended Free Cloud Option

Use Microsoft Azure Blob Storage (widely used in enterprise and strong academic alignment for cloud architecture).

Free-tier expectation (subject to Azure policy updates):

- New account credit for initial period.
- Limited free/low-cost storage and operations depending on subscription and region.

If Azure policy changes, equivalent object storage can still be used with the same architecture pattern.

## Step-by-Step Implementation

## 1. Create Free Cloud Account and Storage on Azure

1. Go to Azure portal and create a free account.
2. In the Azure Portal, create a Resource Group (example: rg-secure-file-transfer).
3. Create a Storage Account:

- Choose General-purpose v2.
- Performance: Standard.
- Redundancy: LRS for lower cost.
- Region: closest to users.

4. Open the Storage Account and go to Data storage > Containers.
5. Create a private container (example: encrypted-files).
6. Keep Public access level as Private (no anonymous access).
7. Enable secure transfer required (HTTPS only).
8. In Encryption settings, keep Microsoft-managed key enabled by default.
9. Save credentials securely (never commit to git).

## 2. Step-by-Step: Get Required Azure Parameters

### A. Storage account name

1. Open Storage Account overview.
2. Copy Storage account name.
3. Use it as AZURE_STORAGE_ACCOUNT_NAME.

### B. Container name

1. Open Data storage > Containers.
2. Copy the container name you created.
3. Use it as AZURE_STORAGE_CONTAINER.

### C. Account key (simple server-side app option)

1. Open Security + networking > Access keys.
2. Copy key1 (or key2).
3. Use it as AZURE_STORAGE_ACCOUNT_KEY.

### D. Connection string (alternative to account name + key)

1. In Access keys, copy Connection string.
2. Use it as AZURE_STORAGE_CONNECTION_STRING.
3. If you use connection string, account key variable can be optional.

### E. Endpoint suffix

1. Usually this is core.windows.net in public Azure.
2. Use AZURE_STORAGE_ENDPOINT_SUFFIX=core.windows.net unless your cloud environment requires a different suffix.

### F. Optional SAS token (for time-limited access)

1. Open Security + networking > Shared access signature.
2. Select allowed services/resources/permissions and expiry.
3. Generate SAS token.
4. Use AZURE_STORAGE_SAS_TOKEN if you prefer token-based access.

## 3. Add Environment Variables

Extend .env and .env.example with cloud settings:

- CLOUD_PROVIDER=azure
- AZURE_STORAGE_ACCOUNT_NAME=...
- AZURE_STORAGE_CONTAINER=encrypted-files
- AZURE_STORAGE_ACCOUNT_KEY=...
- AZURE_STORAGE_CONNECTION_STRING=... (optional alternative)
- AZURE_STORAGE_ENDPOINT_SUFFIX=core.windows.net
- AZURE_STORAGE_SAS_TOKEN=... (optional)
- CLOUD_OBJECT_PREFIX=encrypted/
- STORAGE_MODE=cloud

Note: keep `DATABASE_URL` for PostgreSQL exactly as current model.

## 4. Install Cloud SDK Dependency

Update requirements:

- Add azure-storage-blob to requirements.txt.

## 5. Database Schema Extension (PostgreSQL)

Your current table is `secure_file_users`. Keep it.
Add new tables:

### `secure_files`

- `file_id` (PK, text)
- `owner_username` (FK-like reference to user)
- `original_filename` (text)
- `file_type` (text)
- `plain_size_bytes` (bigint)
- `encrypted_size_bytes` (bigint)
- `cloud_object_key` (text, unique)
- `checksum_sha256` (text)
- `uploaded_at` (timestamptz)

### `file_access`

- `access_id` (serial PK)
- `file_id` (references secure_files.file_id)
- `granted_to` (username)
- `key_provided` (boolean)
- `granted_at` (timestamptz)

### `file_events`

- `event_id` (bigserial PK)
- `file_id` (nullable for failed early events)
- `actor_username` (text)
- `event_type` (`upload`, `share`, `download`, `decryption`, `delete`, `failed_access`)
- `encryption_time_ms` (numeric)
- `decryption_time_ms` (numeric)
- `upload_time_ms` (numeric)
- `download_time_ms` (numeric)
- `upload_speed_mbps` (numeric)
- `download_speed_mbps` (numeric)
- `transfer_speed_mbps` (numeric)
- `event_status` (text)
- `event_message` (text)
- `created_at` (timestamptz)

This schema directly supports your requirement to store encryption time, download speed, and related metrics in PostgreSQL.

## 6. Files to Create for Cloud Integration

Create these files:

1. `app/modules/cloud_storage.py`

- `CloudStorageClient` interface.
- `AzureBlobStorageClient` implementation.
- Methods:
  - `upload_encrypted_file(file_id, encrypted_bytes, filename) -> object_key`
  - `download_encrypted_file(object_key) -> bytes`
  - `delete_encrypted_file(object_key) -> bool`
  - `health_check() -> bool`

2. `app/modules/file_repository.py`

- DB operations for `secure_files` and `file_access`.
- Methods for insert/get/list/share/unshare metadata.

3. `app/modules/metrics_repository.py`

- Insert/read operations for `file_events` table.
- Query helpers for statistics endpoints.

4. `sql/cloud_schema.sql`

- SQL migration script creating `secure_files`, `file_access`, `file_events`.

5. `scripts/migrate_local_to_cloud.py` (optional but recommended)

- One-time script to upload existing `.enc` files from local folder to Azure Blob Storage.
- Writes cloud object keys to PostgreSQL metadata.

## 7. Files to Modify in Current Project

1. `config.py`

- Add cloud config variables.
- Change validation to accept `STORAGE_MODE=cloud`.
- Validate required Azure credentials when cloud mode is active.

2. `app/modules/database.py`

- Add schema initialization for new tables.
- Add repository-level DB methods or expose pooled connections.

3. `app/modules/file_manager.py`

- Stop writing files to `plain_uploads` and `encrypted_uploads` as primary path.
- Keep encryption logic.
- After encryption, upload encrypted bytes to cloud via `cloud_storage.py`.
- Save metadata in PostgreSQL via `file_repository.py`.
- Save performance logs in PostgreSQL via `metrics_repository.py`.

4. `app/routes/file_routes.py`

- Upload route: cloud upload + DB metadata insert.
- Download route: fetch encrypted bytes from cloud, decrypt, stream response.
- Share/unshare routes: write to `file_access` table.
- Stats route: read aggregated metrics from `file_events`.

5. `validate_startup.py`

- Add cloud readiness checks:
  - credentials loaded
  - storage account reachable
  - container reachable
  - test blob list/read permission
- Keep existing PostgreSQL checks.

6. `.env.example`

- Add all cloud variable examples.

7. `README.md`

- Add cloud setup section and architecture explanation.

## 8. Object-Key Strategy in Cloud

Use deterministic naming to support traceability:

- `encrypted/{owner_username}/{file_id}_{safe_filename}.enc`

Benefits:

- Easy ownership filtering.
- Lower collision risk.
- Clear forensic trace in logs.

## 9. Updated Upload and Download Flow

### Upload

1. User uploads file.
2. System encrypts bytes using Fernet key.
3. Encrypted bytes uploaded to Azure Blob Storage container.
4. File metadata inserted into `secure_files`.
5. Upload/encryption metrics inserted into `file_events`.
6. Return `file_id` and encryption key to owner.

### Download

1. Access check from `secure_files` + `file_access`.
2. Read encrypted bytes from Azure Blob Storage object key.
3. Validate user-provided key.
4. Decrypt in memory.
5. Stream decrypted file to user.
6. Write download/decryption metrics to `file_events`.

## 10. Security Controls to Keep

- Encrypted objects only in cloud.
- Private container (no anonymous blob access).
- Least-privilege Azure role assignments.
- Server-side encryption on storage account.
- Input filename sanitization.
- No encryption keys stored in database plaintext.
- Optional: move to customer-managed keys with Azure Key Vault later.

## 11. Validation and Test Checklist

1. Upload a file and verify blob exists in Azure container.
2. Confirm `secure_files` row created in PostgreSQL.
3. Confirm metrics row created in `file_events` with encryption/upload timings.
4. Share file with another user and verify `file_access` row.
5. Download with correct key and confirm speed/timing metrics are logged.
6. Download with wrong key and confirm failed event log entry.
7. Delete file and confirm both Azure blob and metadata rows are removed or marked deleted.

## 12. Deliverable Mapping for Report

This plan demonstrates:

- Cloud-based storage architecture.
- Integrated access control (owner/share permissions in PostgreSQL).
- End-to-end encryption workflow.
- Quantitative performance logging (encryption/decryption/transfer metrics).

It directly supports the project title by separating binary object storage (cloud) from relational control/analytics data (PostgreSQL).

## 13. Implementation Order (Practical Sequence)

1. Add env/config and dependency (`azure-storage-blob`).
2. Create cloud client module (`cloud_storage.py`).
3. Extend PostgreSQL schema and repository modules.
4. Refactor `file_manager.py` for cloud object operations.
5. Update `file_routes.py` endpoints.
6. Extend `validate_startup.py` with cloud checks.
7. Update docs and run end-to-end tests.
