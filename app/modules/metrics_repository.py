"""
Repository for operational metrics in PostgreSQL.
"""

import config as cfg
from datetime import datetime

from psycopg2.extras import RealDictCursor

from modules.cloud_data_repository import cloud_data_error, cloud_metrics_repository
from modules.database import db_manager


class MetricsRepository:
    """Insert and query records from file_events table."""

    def __init__(self, database_manager=None):
        self.db = database_manager or db_manager
        self.storage_mode = cfg.config.STORAGE_MODE.lower()
        self.cloud_repo = cloud_metrics_repository

        if self.storage_mode == 'cloud' and not self.cloud_repo:
            error = cloud_data_error or 'Cloud metrics repository is unavailable'
            raise RuntimeError(error)

    def _normalize_row(self, row):
        if not row:
            return None
        data = dict(row)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    def log_event(
        self,
        event_type,
        actor_username=None,
        file_id=None,
        encryption_time_ms=None,
        decryption_time_ms=None,
        upload_time_ms=None,
        download_time_ms=None,
        upload_speed_mbps=None,
        download_speed_mbps=None,
        transfer_speed_mbps=None,
        event_status="success",
        event_message=None,
    ):
        if self.storage_mode == 'cloud':
            return self.cloud_repo.log_event(
                event_type=event_type,
                actor_username=actor_username,
                file_id=file_id,
                encryption_time_ms=encryption_time_ms,
                decryption_time_ms=decryption_time_ms,
                upload_time_ms=upload_time_ms,
                download_time_ms=download_time_ms,
                upload_speed_mbps=upload_speed_mbps,
                download_speed_mbps=download_speed_mbps,
                transfer_speed_mbps=transfer_speed_mbps,
                event_status=event_status,
                event_message=event_message,
            )

        query = f"""
        INSERT INTO {self.db.FILE_EVENTS_TABLE}
        (
            file_id,
            actor_username,
            event_type,
            encryption_time_ms,
            decryption_time_ms,
            upload_time_ms,
            download_time_ms,
            upload_speed_mbps,
            download_speed_mbps,
            transfer_speed_mbps,
            event_status,
            event_message
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *;
        """

        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    (
                        file_id,
                        actor_username,
                        event_type,
                        encryption_time_ms,
                        decryption_time_ms,
                        upload_time_ms,
                        download_time_ms,
                        upload_speed_mbps,
                        download_speed_mbps,
                        transfer_speed_mbps,
                        event_status,
                        event_message,
                    ),
                )
                return self._normalize_row(cursor.fetchone())

    def count_events(self):
        if self.storage_mode == 'cloud':
            return self.cloud_repo.count_events()

        query = f"SELECT COUNT(*) AS total_events FROM {self.db.FILE_EVENTS_TABLE};"
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                row = cursor.fetchone() or {}
        return int(row.get("total_events", 0))

    def list_events(self):
        if self.storage_mode == 'cloud':
            return self.cloud_repo.list_events()

        query = f"""
        SELECT *
        FROM {self.db.FILE_EVENTS_TABLE}
        ORDER BY created_at DESC;
        """
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._normalize_row(row) for row in rows]


metrics_repository = MetricsRepository()
