"""
Repository for operational metrics in PostgreSQL.
"""

from datetime import datetime

from psycopg2.extras import RealDictCursor

from modules.database import db_manager


class MetricsRepository:
    """Insert and query records from file_events table."""

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
        query = f"SELECT COUNT(*) AS total_events FROM {self.db.FILE_EVENTS_TABLE};"
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                row = cursor.fetchone() or {}
        return int(row.get("total_events", 0))


metrics_repository = MetricsRepository()
