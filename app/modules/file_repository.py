"""
Repository for secure file metadata and access records.
"""

from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from modules.database import db_manager


class FileRepository:
    """CRUD operations for secure_files and file_access tables."""

    def __init__(self, database_manager=None):
        self.db = database_manager or db_manager

    def _normalize_row(self, row):
        if not row:
            return None
        data = dict(row)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    def save_file_metadata(
        self,
        file_id,
        owner_username,
        original_filename,
        file_type,
        plain_size_bytes,
        encrypted_size_bytes,
        cloud_object_key,
        checksum_sha256,
    ):
        query = f"""
        INSERT INTO {self.db.FILE_TABLE}
        (
            file_id,
            owner_username,
            original_filename,
            file_type,
            plain_size_bytes,
            encrypted_size_bytes,
            cloud_object_key,
            checksum_sha256
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *;
        """

        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    (
                        file_id,
                        owner_username,
                        original_filename,
                        file_type,
                        plain_size_bytes,
                        encrypted_size_bytes,
                        cloud_object_key,
                        checksum_sha256,
                    ),
                )
                return self._normalize_row(cursor.fetchone())

    def get_file_metadata(self, file_id):
        query = f"SELECT * FROM {self.db.FILE_TABLE} WHERE file_id = %s;"
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (file_id,))
                return self._normalize_row(cursor.fetchone())

    def list_owned_files(self, owner_username):
        query = f"""
        SELECT *
        FROM {self.db.FILE_TABLE}
        WHERE owner_username = %s
        ORDER BY uploaded_at DESC;
        """
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (owner_username,))
                rows = cursor.fetchall()
                return [self._normalize_row(row) for row in rows]

    def list_shared_files(self, username):
        query = f"""
        SELECT f.*, a.key_provided, a.granted_at
        FROM {self.db.FILE_TABLE} f
        INNER JOIN {self.db.FILE_ACCESS_TABLE} a ON a.file_id = f.file_id
        WHERE a.granted_to = %s
        ORDER BY a.granted_at DESC;
        """
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (username,))
                rows = cursor.fetchall()
                return [self._normalize_row(row) for row in rows]

    def grant_access(self, file_id, granted_to, key_provided=True):
        query = f"""
        INSERT INTO {self.db.FILE_ACCESS_TABLE} (file_id, granted_to, key_provided)
        VALUES (%s, %s, %s)
        ON CONFLICT (file_id, granted_to)
        DO UPDATE SET key_provided = EXCLUDED.key_provided, granted_at = NOW()
        RETURNING *;
        """
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (file_id, granted_to, key_provided))
                return self._normalize_row(cursor.fetchone())

    def revoke_access(self, file_id, granted_to):
        query = f"""
        DELETE FROM {self.db.FILE_ACCESS_TABLE}
        WHERE file_id = %s AND granted_to = %s;
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (file_id, granted_to))
                return cursor.rowcount > 0

    def can_user_access(self, file_id, username):
        query = f"""
        SELECT
            EXISTS (
                SELECT 1
                FROM {self.db.FILE_TABLE}
                WHERE file_id = %s AND owner_username = %s
            ) AS is_owner,
            EXISTS (
                SELECT 1
                FROM {self.db.FILE_ACCESS_TABLE}
                WHERE file_id = %s AND granted_to = %s
            ) AS has_access,
            COALESCE((
                SELECT key_provided
                FROM {self.db.FILE_ACCESS_TABLE}
                WHERE file_id = %s AND granted_to = %s
                LIMIT 1
            ), FALSE) AS key_provided;
        """

        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (file_id, username, file_id, username, file_id, username))
                row = cursor.fetchone() or {}

        is_owner = bool(row.get("is_owner"))
        has_access = bool(row.get("has_access"))
        key_provided = bool(row.get("key_provided"))

        return {
            "can_access": is_owner or has_access,
            "is_owner": is_owner,
            "key_provided": True if is_owner else key_provided,
        }

    def delete_file_metadata(self, file_id, owner_username):
        query = f"""
        DELETE FROM {self.db.FILE_TABLE}
        WHERE file_id = %s AND owner_username = %s;
        """
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (file_id, owner_username))
                return cursor.rowcount > 0


file_repository = FileRepository()
