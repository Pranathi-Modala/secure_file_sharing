"""
==============================================
DATABASE MODULE - PostgreSQL Backend
==============================================
Handles database connections and user persistence
"""

import logging
from datetime import datetime

import psycopg2
from psycopg2 import errors
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    """Manages PostgreSQL connectivity and basic user operations."""

    USER_TABLE = 'secure_file_users'

    def __init__(self, database_url):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        """Create and return a new PostgreSQL connection."""
        return psycopg2.connect(self.database_url)

    def initialize_schema(self):
        """Create required database tables if they do not exist."""
        create_users_table = f"""
        CREATE TABLE IF NOT EXISTS {self.USER_TABLE} (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_users_table)

        self.logger.info(f'✓ Database schema initialized (table: {self.USER_TABLE})')

    def table_exists(self):
        """Check whether the secure_file_users table exists."""
        query = "SELECT to_regclass(%s) AS table_name;"
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (self.USER_TABLE,))
                    row = cursor.fetchone()
            return bool(row and row.get('table_name'))
        except psycopg2.Error as exc:
            self.logger.error(f'Database error while checking table existence: {exc}')
            return False

    def create_user(self, username, password_hash, email):
        """Insert a user record into PostgreSQL."""
        query = f"""
        INSERT INTO {self.USER_TABLE} (username, password_hash, email)
        VALUES (%s, %s, %s)
        RETURNING user_id, username, email, created_at;
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (username, password_hash, email))
                    row = cursor.fetchone()

            return {
                'success': True,
                'user': self._normalize_user_row(row)
            }
        except errors.UniqueViolation:
            return {'success': False, 'message': 'User already exists'}
        except psycopg2.Error as exc:
            self.logger.error(f'Database error while creating user: {exc}')
            return {'success': False, 'message': 'Database error while creating user'}

    def get_user_by_username(self, username):
        """Fetch a user by username."""
        query = f"""
        SELECT user_id, username, password_hash, email, created_at
        FROM {self.USER_TABLE}
        WHERE username = %s;
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (username,))
                    row = cursor.fetchone()
            return self._normalize_user_row(row)
        except psycopg2.Error as exc:
            self.logger.error(f'Database error while reading user: {exc}')
            return None

    def get_all_users(self):
        """Fetch all users for admin/statistics views."""
        query = f"""
        SELECT user_id, username, email, created_at
        FROM {self.USER_TABLE}
        ORDER BY user_id ASC;
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
            return [self._normalize_user_row(row) for row in rows]
        except psycopg2.Error as exc:
            self.logger.error(f'Database error while reading all users: {exc}')
            return []

    @staticmethod
    def _normalize_user_row(row):
        """Convert DB rows into API-friendly dictionaries."""
        if not row:
            return None

        normalized = dict(row)
        created_at = normalized.get('created_at')
        if isinstance(created_at, datetime):
            normalized['created_at'] = created_at.isoformat()

        return normalized


try:
    import config as cfg

    db_manager = DatabaseManager(cfg.config.DATABASE_URL)
except ImportError:
    db_manager = None
