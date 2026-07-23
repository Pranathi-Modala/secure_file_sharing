"""
One-time migration helper: upload local encrypted files to Azure Blob Storage
and write metadata records into PostgreSQL.

Usage:
    python scripts/migrate_local_to_cloud.py
"""

from pathlib import Path
import hashlib

import config
from app.modules.cloud_storage import get_cloud_storage_client
from app.modules.file_repository import file_repository


def infer_owner_and_name(file_name):
    """Infer owner and original filename from local naming convention."""
    # Expected local format: {file_id}_{original_name}.enc
    parts = file_name.split("_", 1)
    if len(parts) == 2:
        return "migration_user", parts[1].replace(".enc", "")
    return "migration_user", file_name.replace(".enc", "")


def migrate_encrypted_files():
    if config.config.STORAGE_MODE.lower() != "cloud":
        raise RuntimeError("Set STORAGE_MODE=cloud before running migration")

    cloud_client = get_cloud_storage_client(config.config)
    encrypted_dir = Path(config.config.ENCRYPTED_UPLOAD_FOLDER)

    if not encrypted_dir.exists():
        print(f"No encrypted directory found at: {encrypted_dir}")
        return

    migrated = 0
    skipped = 0

    for file_path in encrypted_dir.glob("*.enc"):
        file_name = file_path.name
        file_id = file_name.split("_", 1)[0] if "_" in file_name else hashlib.sha256(file_name.encode()).hexdigest()[:16]
        owner, original_name = infer_owner_and_name(file_name)

        metadata = file_repository.get_file_metadata(file_id)
        if metadata:
            print(f"Skipping existing metadata for file_id={file_id}")
            skipped += 1
            continue

        encrypted_bytes = file_path.read_bytes()
        object_name = f"{owner}/{file_id}_{original_name}.enc"
        object_key = cloud_client.upload_encrypted_file(file_id, encrypted_bytes, object_name)

        file_repository.save_file_metadata(
            file_id=file_id,
            owner_username=owner,
            original_filename=original_name,
            file_type=Path(original_name).suffix.lstrip("."),
            plain_size_bytes=None,
            encrypted_size_bytes=len(encrypted_bytes),
            cloud_object_key=object_key,
            checksum_sha256=hashlib.sha256(encrypted_bytes).hexdigest(),
        )

        print(f"Migrated {file_name} -> {object_key}")
        migrated += 1

    print(f"Migration complete. migrated={migrated}, skipped={skipped}")


if __name__ == "__main__":
    migrate_encrypted_files()
