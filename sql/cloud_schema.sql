-- Cloud metadata schema for PostgreSQL
-- Execute against the same database used by the application.

CREATE TABLE IF NOT EXISTS secure_files (
    file_id TEXT PRIMARY KEY,
    owner_username VARCHAR(100) NOT NULL,
    original_filename TEXT NOT NULL,
    file_type TEXT,
    plain_size_bytes BIGINT,
    encrypted_size_bytes BIGINT,
    cloud_object_key TEXT UNIQUE,
    checksum_sha256 TEXT,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_owner_username
        FOREIGN KEY(owner_username)
        REFERENCES secure_file_users(username)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS file_access (
    access_id SERIAL PRIMARY KEY,
    file_id TEXT NOT NULL,
    granted_to VARCHAR(100) NOT NULL,
    key_provided BOOLEAN NOT NULL DEFAULT TRUE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_access_file
        FOREIGN KEY(file_id)
        REFERENCES secure_files(file_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_access_user
        FOREIGN KEY(granted_to)
        REFERENCES secure_file_users(username)
        ON DELETE CASCADE,
    CONSTRAINT uq_file_recipient UNIQUE (file_id, granted_to)
);

CREATE TABLE IF NOT EXISTS file_events (
    event_id BIGSERIAL PRIMARY KEY,
    file_id TEXT,
    actor_username VARCHAR(100),
    event_type TEXT NOT NULL,
    encryption_time_ms NUMERIC,
    decryption_time_ms NUMERIC,
    upload_time_ms NUMERIC,
    download_time_ms NUMERIC,
    upload_speed_mbps NUMERIC,
    download_speed_mbps NUMERIC,
    transfer_speed_mbps NUMERIC,
    event_status TEXT,
    event_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_event_file
        FOREIGN KEY(file_id)
        REFERENCES secure_files(file_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_event_actor
        FOREIGN KEY(actor_username)
        REFERENCES secure_file_users(username)
        ON DELETE SET NULL
);
