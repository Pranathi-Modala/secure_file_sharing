"""
==============================================
AUTHENTICATION MODULE - Python Backend
==============================================
Manages user authentication and authorization
Handles user database and session management
Part of Week 2-3 Secure File Transfer System
Week 7: PostgreSQL-backed account storage for registration and login

OOP Architecture with User and AuthManager classes
"""

import hashlib
import os
from datetime import datetime
import logging

from modules.database import db_manager


class AuthenticationManager:
    """
    Manages user authentication and authorization
    Handles login, registration, and user management
    """

    def __init__(self, database_manager=None):
        """
        Initialize authentication manager
        """
        self.db = database_manager
        self.login_attempts = {}  # Track failed attempts
        self.active_sessions = {}  # {session_id: {username, login_time}}
        self.auth_logs = []  # Authentication event logs
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash password using SHA-256
        In production, use bcrypt or argon2

        Args:
            password (str): Password to hash
            salt (bytes): Salt for hashing (generates if None)

        Returns:
            tuple: (password_hash, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )

        return password_hash, salt

    def _create_user(self, username, password, email):
        """
        Internal method to create user

        Args:
            username (str): Username
            password (str): Plain password
            email (str): User email

        Returns:
            dict: Result with success status
        """
        if not self.db:
            return {'success': False, 'message': 'Database is not configured'}

        password_hash, salt = self.hash_password(password)
        stored_password_hash = f"{password_hash.hex()}:{salt.hex()}"
        result = self.db.create_user(
            username=username,
            password_hash=stored_password_hash,
            email=email
        )

        if result['success']:
            self.logger.info(f'✓ User created: {username}')

        return result

    def register_user(self, username, password, email):
        """
        Register new user

        Args:
            username (str): Username
            password (str): Password
            email (str): Email address

        Returns:
            dict: Registration result
        """
        # Validate input
        if not username or len(username) < 3:
            return {'success': False, 'message': 'Username must be at least 3 characters'}

        if not password or len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}

        if not email or '@' not in email:
            return {'success': False, 'message': 'A valid email is required'}

        return self._create_user(username, password, email)

    def login(self, username, password):
        """
        Authenticate user with credentials

        Args:
            username (str): Username
            password (str): Password

        Returns:
            dict: Login result with session info
        """
        start_time = datetime.now()

        user = self.get_user_by_username(username)

        # Check if user exists
        if not user:
            self._record_failed_attempt(username)
            self._log_auth_event(username, False, 'User not found')
            return {'success': False, 'message': 'Invalid username or password'}

        # Verify password
        password_hash = user.get('password_hash', '')
        if ':' not in password_hash:
            self._record_failed_attempt(username)
            self._log_auth_event(username, False, 'Corrupt password hash')
            return {'success': False, 'message': 'Invalid username or password'}

        stored_hash, salt_hex = password_hash.split(':', 1)
        salt = bytes.fromhex(salt_hex)
        provided_hash, _ = self.hash_password(password, salt)

        if provided_hash.hex() != stored_hash:
            self._record_failed_attempt(username)
            self._log_auth_event(username, False, 'Invalid password')
            return {'success': False, 'message': 'Invalid username or password'}

        # Clear failed attempts
        if username in self.login_attempts:
            del self.login_attempts[username]

        # Generate session
        session_id = os.urandom(32).hex()
        self.active_sessions[session_id] = {
            'username': username,
            'login_time': datetime.now().isoformat()
        }

        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        self._log_auth_event(username, True, 'Login successful', execution_time)

        return {
            'success': True,
            'message': f'✓ Welcome {username}!',
            'session_id': session_id,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            },
            'execution_time_ms': round(execution_time, 2)
        }

    def logout(self, session_id):
        """
        Logout user

        Args:
            session_id (str): Session identifier

        Returns:
            dict: Logout result
        """
        if session_id in self.active_sessions:
            username = self.active_sessions[session_id]['username']
            del self.active_sessions[session_id]
            self._log_auth_event(username, True, 'Logout')
            return {'success': True, 'message': '✓ Logged out successfully'}

        return {'success': False, 'message': 'Invalid session'}

    def verify_session(self, session_id):
        """
        Verify if session is active

        Args:
            session_id (str): Session identifier

        Returns:
            dict: Session info if valid, None otherwise
        """
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        return None

    def get_user_by_username(self, username):
        """
        Get user by username

        Args:
            username (str): Username

        Returns:
            User object or None
        """
        if not self.db:
            return None

        return self.db.get_user_by_username(username)

    def get_all_users(self):
        """
        Get list of all users

        Returns:
            list: List of user dictionaries
        """
        if not self.db:
            return []

        users = self.db.get_all_users()
        return [
            {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
            for user in users
        ]

    def _record_failed_attempt(self, username):
        """Record failed login attempt"""
        if username not in self.login_attempts:
            self.login_attempts[username] = 0

        self.login_attempts[username] += 1

        if self.login_attempts[username] >= 3:
            self.logger.warning(f'⚠ Multiple failed attempts for {username}')

    def _log_auth_event(self, username, success, message, execution_time=0):
        """
        Log authentication event

        Args:
            username (str): Username
            success (bool): Success status
            message (str): Event message
            execution_time (float): Execution time in ms
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'success': success,
            'message': message,
            'execution_time_ms': execution_time
        }

        self.auth_logs.append(log_entry)

    def get_auth_logs(self, limit=10):
        """
        Get recent authentication logs

        Args:
            limit (int): Maximum logs to return

        Returns:
            list: Recent authentication logs
        """
        return self.auth_logs[-limit:]

    def get_auth_statistics(self):
        """
        Get authentication statistics

        Returns:
            dict: Statistics about authentication
        """
        successful_logins = len([l for l in self.auth_logs if l['success'] and l['message'] == 'Login successful'])
        failed_logins = len([l for l in self.auth_logs if not l['success']])

        return {
            'total_users': len(self.get_all_users()),
            'active_sessions': len(self.active_sessions),
            'successful_logins': successful_logins,
            'failed_logins': failed_logins,
            'total_auth_events': len(self.auth_logs)
        }


# Create singleton instance backed by PostgreSQL
auth_manager = AuthenticationManager(database_manager=db_manager)
