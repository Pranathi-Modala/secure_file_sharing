"""
==============================================
SYSTEM LOGGER MODULE - Python Backend
==============================================
Centralized logging for all system events
Part of Week 2-3 Secure File Transfer System
Week 5: Environment Hardening - Uses configured log folder
"""

import logging
import os
import csv
from datetime import datetime


class SystemLogger:
    """
    Centralized logging system for audit trails
    """

    def __init__(self, log_dir=None):
        """
        Initialize system logger

        Args:
            log_dir (str): Directory for log files (uses config if None)
        """
        # If no log_dir provided, try to import config
        if log_dir is None:
            try:
                import config as cfg
                log_dir = str(cfg.config.LOG_FOLDER)
            except:
                log_dir = 'logs'
        
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.csv_log_path = os.path.join(log_dir, 'logs.csv')
        self.csv_fields = [
            'file_id',
            'file_type',
            'file_size',
            'type',
            'duration_sec',
            'owner',
            'date_shared',
            'time_shared',
            'upload_time_plain_sec',
            'upload_time_encrypted_sec',
            'download_time_plain_sec',
            'download_time_encrypted_sec'
        ]
        self._initialize_csv_log()

        # Create logger
        self.logger = logging.getLogger('secure_file_transfer')
        self.logger.setLevel(logging.DEBUG)

        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'system.log')
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _initialize_csv_log(self):
        """Create CSV log file with headers if it does not exist yet."""
        if not os.path.exists(self.csv_log_path):
            with open(self.csv_log_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.csv_fields)
                writer.writeheader()
            return

        with open(self.csv_log_path, 'r', newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            existing_fields = reader.fieldnames or []
            if existing_fields == self.csv_fields:
                return
            existing_rows = list(reader)

        with open(self.csv_log_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.csv_fields)
            writer.writeheader()
            for row in existing_rows:
                migrated_row = {field: row.get(field, '') for field in self.csv_fields}
                writer.writerow(migrated_row)

    def log_file_event(self, file_id, file_type, file_size, event_type, duration_sec, owner, date_shared, time_shared, upload_time_plain_sec=0.0, upload_time_encrypted_sec=0.0, download_time_plain_sec=0.0, download_time_encrypted_sec=0.0):
        """Append one file operation event row to logs.csv."""
        with open(self.csv_log_path, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.csv_fields)
            writer.writerow({
                'file_id': file_id,
                'file_type': file_type,
                'file_size': file_size,
                'type': event_type,
                'duration_sec': duration_sec,
                'owner': owner,
                'date_shared': date_shared,
                'time_shared': time_shared,
                'upload_time_plain_sec': upload_time_plain_sec,
                'upload_time_encrypted_sec': upload_time_encrypted_sec,
                'download_time_plain_sec': download_time_plain_sec,
                'download_time_encrypted_sec': download_time_encrypted_sec
            })

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)


# Create singleton instance with log folder from config
try:
    import config as cfg
    system_logger = SystemLogger(log_dir=str(cfg.config.LOG_FOLDER))
except:
    system_logger = SystemLogger(log_dir='logs')

