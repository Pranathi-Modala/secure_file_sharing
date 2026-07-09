"""
==============================================
CONFIGURATION MANAGEMENT MODULE
==============================================
Week 5: Environment Hardening
Loads and validates configuration from environment variables
Centralizes all application configuration and secrets management
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration validation fails"""
    pass


class Config:
    """
    Application configuration class
    Loads settings from environment variables with defaults
    Validates critical settings at startup
    """

    def __init__(self):
        """Initialize configuration from environment"""
        # Load .env file if it exists
        env_path = Path(__file__).parent / '.env'
        load_dotenv(env_path)

        # Flask settings
        self.SECRET_KEY = os.getenv(
            'FLASK_SECRET_KEY',
            'dev-secret-key-change-in-production'
        )
        self.ENV = os.getenv('FLASK_ENV', 'development')
        self.DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
        self.HOST = os.getenv('FLASK_HOST', '127.0.0.1')
        self.PORT = int(os.getenv('FLASK_PORT', '5000'))

        # File upload settings
        self.MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
        self.MAX_CONTENT_LENGTH = self.MAX_FILE_SIZE_MB * 1024 * 1024
        
        # Resolve folder paths relative to app root
        app_root = Path(__file__).parent
        self.UPLOAD_FOLDER = self._resolve_path(
            os.getenv('UPLOAD_FOLDER', 'app/uploads'),
            app_root
        )
        self.PLAIN_UPLOAD_FOLDER = self._resolve_path(
            os.getenv('PLAIN_UPLOAD_FOLDER', 'app/uploads/plain_uploads'),
            app_root
        )
        self.ENCRYPTED_UPLOAD_FOLDER = self._resolve_path(
            os.getenv('ENCRYPTED_UPLOAD_FOLDER', 'app/uploads/encrypted_uploads'),
            app_root
        )

        # Logging settings
        self.LOG_FOLDER = self._resolve_path(
            os.getenv('LOG_FOLDER', 'logs'),
            app_root
        )
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

        # Demo users (format: username:password:email | username:password:email)
        demo_users_str = os.getenv(
            'DEMO_USERS',
            'admin:admin123:admin@secure.com|alice:alice123:alice@secure.com|bob:bob123:bob@secure.com'
        )
        self.DEMO_USERS = self._parse_demo_users(demo_users_str)

        # Security settings
        self.SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
        self.LOCKOUT_DURATION_MINUTES = int(os.getenv('LOCKOUT_DURATION_MINUTES', '15'))

        # Encryption settings
        self.ENCRYPTION_ALGORITHM = os.getenv('ENCRYPTION_ALGORITHM', 'Fernet')
        self.KEY_ROTATION_POLICY = os.getenv('KEY_ROTATION_POLICY', 'none')

        # Storage mode
        self.STORAGE_MODE = os.getenv('STORAGE_MODE', 'in-memory')

        # Metrics/research settings
        self.METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'True').lower() in ('true', '1', 'yes')
        self.METRICS_OUTPUT_FILE = self._resolve_path(
            os.getenv('METRICS_OUTPUT_FILE', 'logs/metrics.json'),
            app_root
        )

    @staticmethod
    def _resolve_path(path_str, base_path):
        """
        Resolve a path relative to base_path

        Args:
            path_str (str): Path string (absolute or relative)
            base_path (Path): Base path for relative resolution

        Returns:
            Path: Resolved absolute path
        """
        path = Path(path_str)
        if path.is_absolute():
            return path
        return base_path / path

    @staticmethod
    def _parse_demo_users(demo_users_str):
        """
        Parse demo users from environment variable

        Format: username:password:email | username:password:email

        Args:
            demo_users_str (str): Demo users configuration string

        Returns:
            list: List of tuples (username, password, email)
        """
        users = []
        if not demo_users_str:
            return users

        for user_entry in demo_users_str.split('|'):
            parts = user_entry.strip().split(':')
            if len(parts) == 3:
                username, password, email = parts
                users.append((username.strip(), password.strip(), email.strip()))

        return users

    def validate(self):
        """
        Validate configuration and create required directories

        Raises:
            ConfigurationError: If validation fails

        Returns:
            dict: Validation report
        """
        errors = []
        warnings = []

        # Validate secret key
        if self.SECRET_KEY.startswith('dev-') and self.ENV == 'production':
            errors.append('FLASK_SECRET_KEY must be changed from default in production')

        # Validate port
        if not 1 <= self.PORT <= 65535:
            errors.append(f'FLASK_PORT must be between 1 and 65535, got {self.PORT}')

        # Validate file size
        if self.MAX_FILE_SIZE_MB < 1:
            errors.append(f'MAX_FILE_SIZE_MB must be at least 1, got {self.MAX_FILE_SIZE_MB}')
        if self.MAX_FILE_SIZE_MB > 1000:
            warnings.append(f'MAX_FILE_SIZE_MB is very large ({self.MAX_FILE_SIZE_MB}MB)')

        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL.upper() not in valid_levels:
            errors.append(f'LOG_LEVEL must be one of {valid_levels}, got {self.LOG_LEVEL}')

        # Validate storage mode
        valid_modes = ['in-memory', 'database']
        if self.STORAGE_MODE.lower() not in valid_modes:
            errors.append(f'STORAGE_MODE must be one of {valid_modes}, got {self.STORAGE_MODE}')

        # Create required directories
        try:
            self.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            self.PLAIN_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            self.ENCRYPTED_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            self.LOG_FOLDER.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f'Failed to create required directories: {str(e)}')

        # Validate demo users
        if not self.DEMO_USERS:
            warnings.append('No demo users configured (DEMO_USERS is empty)')

        if errors:
            raise ConfigurationError(f'Configuration validation failed:\n' + '\n'.join(f'  ✗ {e}' for e in errors))

        return {
            'valid': True,
            'errors': errors,
            'warnings': warnings
        }

    def to_dict(self):
        """
        Convert configuration to dictionary (excluding sensitive values)

        Returns:
            dict: Configuration as dictionary
        """
        return {
            'environment': self.ENV,
            'debug': self.DEBUG,
            'host': self.HOST,
            'port': self.PORT,
            'max_file_size_mb': self.MAX_FILE_SIZE_MB,
            'upload_folder': str(self.UPLOAD_FOLDER),
            'plain_upload_folder': str(self.PLAIN_UPLOAD_FOLDER),
            'encrypted_upload_folder': str(self.ENCRYPTED_UPLOAD_FOLDER),
            'log_folder': str(self.LOG_FOLDER),
            'log_level': self.LOG_LEVEL,
            'session_timeout_minutes': self.SESSION_TIMEOUT_MINUTES,
            'max_login_attempts': self.MAX_LOGIN_ATTEMPTS,
            'lockout_duration_minutes': self.LOCKOUT_DURATION_MINUTES,
            'encryption_algorithm': self.ENCRYPTION_ALGORITHM,
            'key_rotation_policy': self.KEY_ROTATION_POLICY,
            'storage_mode': self.STORAGE_MODE,
            'metrics_enabled': self.METRICS_ENABLED,
        }

    def __repr__(self):
        """String representation of configuration"""
        config_dict = self.to_dict()
        items = '\n  '.join([f'{k}: {v}' for k, v in config_dict.items()])
        return f'Config(\n  {items}\n)'


# Create global config instance
try:
    config = Config()
    config.validate()
except ConfigurationError as e:
    print(f'\n❌ Configuration Error:\n{str(e)}\n', file=sys.stderr)
    sys.exit(1)
