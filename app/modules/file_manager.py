"""
==============================================
FILE MANAGEMENT MODULE - Python Backend
==============================================
Manages file storage, sharing, and access control
Coordinates with encryption and authentication modules
Part of Week 2-3 Secure File Transfer System

OOP Architecture with File and FileManager classes
"""

import os
import hashlib
import time
from datetime import datetime
import logging
from modules.logger import system_logger


class SharedFile:
    """
    Represents a file shared between users
    """

    def __init__(self, file_id, filename, owner, encrypted_content, encryption_key, file_size, plain_file_path, encrypted_file_path, encrypted_size=None, upload_metrics=None):
        """
        Initialize shared file object

        Args:
            file_id (str): Unique file identifier
            filename (str): Original filename
            owner (str): Username of file owner
            encrypted_content (bytes): Encrypted file content
            encryption_key (str): Key needed to decrypt file
            file_size (int): Original file size
        """
        self.file_id = file_id
        self.filename = filename
        self.owner = owner
        self.encrypted_content = encrypted_content
        self.encryption_key = encryption_key
        self.file_size = file_size
        self.encrypted_size = encrypted_size if encrypted_size is not None else len(encrypted_content)
        self.plain_file_path = plain_file_path
        self.encrypted_file_path = encrypted_file_path
        self.upload_metrics = upload_metrics or {}
        self.upload_timestamp = datetime.now().isoformat()
        self.shared_with = {}  # {username: {'shared_at': timestamp, 'key_provided': bool}}
        self.download_log = []  # Track who downloaded

    def share_with_user(self, recipient_username, provide_key=True):
        """
        Share file with another user

        Args:
            recipient_username (str): Username of recipient
            provide_key (bool): Whether to provide decryption key

        Returns:
            bool: Success status
        """
        if recipient_username == self.owner:
            return False  # Cannot share with self

        self.shared_with[recipient_username] = {
            'shared_at': datetime.now().isoformat(),
            'key_provided': provide_key
        }

        return True

    def unshare_with_user(self, recipient_username):
        """
        Revoke file access from user

        Args:
            recipient_username (str): Username to revoke access from

        Returns:
            bool: Success status
        """
        if recipient_username in self.shared_with:
            del self.shared_with[recipient_username]
            return True
        return False

    def can_access(self, username):
        """
        Check if user can access file

        Args:
            username (str): Username to check

        Returns:
            bool: True if user can access
        """
        return username == self.owner or username in self.shared_with

    def log_download(self, username):
        """
        Log file download

        Args:
            username (str): Username who downloaded
        """
        self.download_log.append({
            'username': username,
            'timestamp': datetime.now().isoformat()
        })

    def to_dict(self, include_content=False):
        """
        Convert to dictionary

        Returns:
            dict: File metadata
        """
        data = {
            'file_id': self.file_id,
            'filename': self.filename,
            'owner': self.owner,
            'file_size': self.file_size,
            'encrypted_size': self.encrypted_size,
            'upload_timestamp': self.upload_timestamp,
            'shared_with': list(self.shared_with.keys()),
            'total_downloads': len(self.download_log),
            'upload_metrics': self.upload_metrics
        }

        if include_content:
            encrypted_content = self.encrypted_content
            if self.encrypted_file_path and os.path.exists(self.encrypted_file_path):
                with open(self.encrypted_file_path, 'rb') as encrypted_file:
                    encrypted_content = encrypted_file.read()
            data['encrypted_content'] = encrypted_content
            data['encryption_key'] = self.encryption_key

        return data


class FileManager:
    """
    Manages file storage, sharing, and access control
    """

    def __init__(self):
        """Initialize file manager"""
        self.files = {}  # {file_id: SharedFile object}
        self.user_files = {}  # {username: [file_ids]}
        self.file_operations = []  # Track operations for logging
        self.logger = logging.getLogger(__name__)
        self.upload_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        self.plain_upload_dir = os.path.join(self.upload_root, 'plain_uploads')
        self.encrypted_upload_dir = os.path.join(self.upload_root, 'encrypted_uploads')
        os.makedirs(self.plain_upload_dir, exist_ok=True)
        os.makedirs(self.encrypted_upload_dir, exist_ok=True)

    def _sanitize_filename(self, filename):
        """Create a safe file name for local storage."""
        return ''.join(ch for ch in filename if ch.isalnum() or ch in ('-', '_', '.')) or 'uploaded_file'

    def _calculate_speed_mbps(self, size_bytes, elapsed_ms):
        """Convert bytes and elapsed milliseconds to MB/s."""
        if not elapsed_ms:
            return 0
        elapsed_sec = elapsed_ms / 1000
        if elapsed_sec <= 0:
            return 0
        return (size_bytes / (1024 * 1024)) / elapsed_sec

    def upload_file(self, filename, owner, plain_content, encrypted_content, encryption_key, original_size, encryption_time_ms=None, encrypted_size=None):
        """
        Upload encrypted file to system

        Args:
            filename (str): Original filename
            owner (str): Username of uploader
            plain_content (bytes): Original file content
            encrypted_content (bytes): Encrypted file content
            encryption_key (str): Decryption key
            original_size (int): Original file size
            encryption_time_ms (float): Time taken to encrypt the file in milliseconds
            encrypted_size (int): Encrypted data size in bytes

        Returns:
            dict: Upload result with file_id
        """
        # Generate unique file ID
        file_id = hashlib.sha256(
            f"{owner}{filename}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        encrypted_size = encrypted_size if encrypted_size is not None else len(encrypted_content)
        safe_filename = self._sanitize_filename(filename)
        plain_file_path = os.path.join(self.plain_upload_dir, f"{file_id}_{safe_filename}")
        encrypted_file_path = os.path.join(self.encrypted_upload_dir, f"{file_id}_{safe_filename}.enc")

        plain_write_start = time.time()
        with open(plain_file_path, 'wb') as plain_file:
            plain_file.write(plain_content)
        plain_write_time_ms = (time.time() - plain_write_start) * 1000

        encrypted_write_start = time.time()
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_content)
        encrypted_write_time_ms = (time.time() - encrypted_write_start) * 1000

        upload_speed_plain_mbps = self._calculate_speed_mbps(original_size, plain_write_time_ms)
        upload_speed_encrypted_mbps = self._calculate_speed_mbps(encrypted_size, encrypted_write_time_ms)
        encryption_speed_mbps = self._calculate_speed_mbps(original_size, encryption_time_ms)
        size_overhead_percent = ((encrypted_size - original_size) / original_size * 100) if original_size else 0

        upload_metrics = {
            'plain_write_time_ms': round(plain_write_time_ms, 2),
            'encrypted_write_time_ms': round(encrypted_write_time_ms, 2),
            'upload_speed_plain_mbps': round(upload_speed_plain_mbps, 2),
            'upload_speed_encrypted_mbps': round(upload_speed_encrypted_mbps, 2),
            'encryption_speed_mbps': round(encryption_speed_mbps, 2),
            'size_overhead_percent': round(size_overhead_percent, 2)
        }

        # Create shared file object
        shared_file = SharedFile(
            file_id=file_id,
            filename=filename,
            owner=owner,
            encrypted_content=encrypted_content,
            encryption_key=encryption_key,
            file_size=original_size,
            plain_file_path=plain_file_path,
            encrypted_file_path=encrypted_file_path,
            encrypted_size=encrypted_size,
            upload_metrics=upload_metrics
        )

        # Store file
        self.files[file_id] = shared_file

        # Track in user files
        if owner not in self.user_files:
            self.user_files[owner] = []
        self.user_files[owner].append(file_id)

        # Log operation
        self._log_operation({
            'operation': 'upload',
            'username': owner,
            'filename': filename,
            'file_id': file_id,
            'file_size': original_size,
            'encrypted_size': encrypted_size,
            'encryption_time_ms': encryption_time_ms,
            'plain_write_time_ms': upload_metrics['plain_write_time_ms'],
            'encrypted_write_time_ms': upload_metrics['encrypted_write_time_ms'],
            'upload_speed_plain_mbps': upload_metrics['upload_speed_plain_mbps'],
            'upload_speed_encrypted_mbps': upload_metrics['upload_speed_encrypted_mbps'],
            'encryption_speed_mbps': upload_metrics['encryption_speed_mbps'],
            'size_overhead_percent': upload_metrics['size_overhead_percent']
        })

        formatted_encryption_time = (encryption_time_ms or 0)
        self.logger.info(
            f'File uploaded: {filename} by {owner} | size={original_size} bytes | encrypted_size={encrypted_size} bytes | encryption_time_ms={formatted_encryption_time:.2f} | upload_speed_plain_mbps={upload_metrics["upload_speed_plain_mbps"]:.2f} | upload_speed_encrypted_mbps={upload_metrics["upload_speed_encrypted_mbps"]:.2f}'
        )

        return {
            'success': True,
            'file_id': file_id,
            'message': f'File uploaded successfully',
            'upload_metrics': upload_metrics
        }

    def share_file(self, file_id, owner, recipient_username, include_key=True, share_start=None):
        """
        Share file with another user

        Args:
            file_id (str): File to share
            owner (str): Owner of file
            recipient_username (str): Recipient username
            include_key (bool): Provide decryption key
            share_start (float): Timestamp when share operation began

        Returns:
            dict: Share result
        """
        if file_id not in self.files:
            return {'success': False, 'message': 'File not found'}

        shared_file = self.files[file_id]

        # Verify ownership
        if shared_file.owner != owner:
            return {'success': False, 'message': 'Permission denied'}

        # Share file
        shared_file.share_with_user(recipient_username, include_key)

        share_time_ms = (time.time() - share_start) * 1000 if share_start else None

        # Log operation
        self._log_operation({
            'operation': 'share',
            'filename': shared_file.filename,
            'owner': owner,
            'recipient': recipient_username,
            'file_id': file_id,
            'file_size': shared_file.file_size,
            'key_provided': include_key,
            'share_time_ms': share_time_ms
        })

        formatted_share_time = (share_time_ms or 0)
        self.logger.info(
            f'File shared: {shared_file.filename} from {owner} to {recipient_username} | file_size={shared_file.file_size} bytes | share_time_ms={formatted_share_time:.2f} | key_provided={include_key}'
        )

        return {
            'success': True,
            'message': f'File shared with {recipient_username}',
            'key_provided': include_key
        }

    def get_file_for_download(self, file_id, username, download_start=None):
        """
        Get file for download if user has access

        Args:
            file_id (str): File to download
            username (str): Username requesting download
            download_start (float): Timestamp when download retrieval began

        Returns:
            dict: File data if accessible, error message otherwise
        """
        if file_id not in self.files:
            return {'success': False, 'message': 'File not found'}

        shared_file = self.files[file_id]

        # Check access
        if not shared_file.can_access(username):
            return {'success': False, 'message': 'Access denied'}

        # Check if key was provided
        if username != shared_file.owner and not shared_file.shared_with[username]['key_provided']:
            return {
                'success': False,
                'message': 'File is locked. Owner did not provide decryption key.'
            }

        # Log download
        shared_file.log_download(username)

        encrypted_read_start = time.time()
        encrypted_content = shared_file.encrypted_content
        if shared_file.encrypted_file_path and os.path.exists(shared_file.encrypted_file_path):
            with open(shared_file.encrypted_file_path, 'rb') as encrypted_file:
                encrypted_content = encrypted_file.read()
        encrypted_read_time_ms = (time.time() - encrypted_read_start) * 1000
        encrypted_download_speed_mbps = self._calculate_speed_mbps(len(encrypted_content), encrypted_read_time_ms)

        retrieval_time_ms = (time.time() - download_start) * 1000 if download_start else encrypted_read_time_ms

        return {
            'success': True,
            'file': {
                **shared_file.to_dict(include_content=True),
                'encrypted_content': encrypted_content
            },
            'download_metrics': {
                'encrypted_read_time_ms': round(encrypted_read_time_ms, 2),
                'encrypted_download_speed_mbps': round(encrypted_download_speed_mbps, 2),
                'retrieval_time_ms': round(retrieval_time_ms, 2)
            },
            'message': 'File retrieved successfully'
        }

    def list_user_files(self, username):
        """
        List files owned by user

        Args:
            username (str): Username

        Returns:
            list: File metadata list
        """
        file_ids = self.user_files.get(username, [])
        files = []

        for file_id in file_ids:
            files.append(self.files[file_id].to_dict())

        return files

    def list_shared_files(self, username):
        """
        List files shared with user

        Args:
            username (str): Username

        Returns:
            list: File metadata list
        """
        shared_files = []

        for file_id, shared_file in self.files.items():
            if username in shared_file.shared_with and username != shared_file.owner:
                shared_files.append(shared_file.to_dict())

        return shared_files

    def delete_file(self, file_id, owner):
        """
        Delete file (owner only)

        Args:
            file_id (str): File to delete
            owner (str): Username requesting deletion

        Returns:
            dict: Deletion result
        """
        if file_id not in self.files:
            return {'success': False, 'message': 'File not found'}

        shared_file = self.files[file_id]

        # Verify ownership
        if shared_file.owner != owner:
            return {'success': False, 'message': 'Permission denied'}

        # Delete file
        filename = shared_file.filename

        if shared_file.plain_file_path and os.path.exists(shared_file.plain_file_path):
            os.remove(shared_file.plain_file_path)
        if shared_file.encrypted_file_path and os.path.exists(shared_file.encrypted_file_path):
            os.remove(shared_file.encrypted_file_path)

        del self.files[file_id]
        self.user_files[owner].remove(file_id)

        # Log operation
        self._log_operation({
            'operation': 'delete',
            'filename': filename,
            'owner': owner,
            'file_id': file_id
        })

        self.logger.info(f'File deleted: {filename}')

        return {'success': True, 'message': 'File deleted successfully'}

    def unshare_file(self, file_id, owner, recipient):
        """
        Revoke file access from user

        Args:
            file_id (str): File ID
            owner (str): File owner
            recipient (str): Recipient to revoke access from

        Returns:
            dict: Result
        """
        if file_id not in self.files:
            return {'success': False, 'message': 'File not found'}

        shared_file = self.files[file_id]

        if shared_file.owner != owner:
            return {'success': False, 'message': 'Permission denied'}

        if shared_file.unshare_with_user(recipient):
            return {'success': True, 'message': f'Access revoked from {recipient}'}

        return {'success': False, 'message': 'User does not have access to file'}

    def _log_operation(self, operation):
        """Log file operation"""
        operation['timestamp'] = datetime.now().isoformat()
        self.file_operations.append(operation)

        file_name = operation.get('filename', '')
        file_type = os.path.splitext(file_name)[1].lstrip('.') if file_name else ''
        file_id = operation.get('file_id', '')
        file_size = operation.get('file_size', 0)
        owner = operation.get('owner') or operation.get('username') or operation.get('user') or ''

        event_type = operation.get('operation', '')
        if event_type == 'upload' and operation.get('encryption_time_ms') is not None:
            event_type = 'encryption'

        allowed_csv_types = {'encryption', 'share', 'download', 'decryption'}
        if event_type not in allowed_csv_types:
            return

        duration_ms = (
            operation.get('encryption_time_ms')
            if event_type == 'encryption'
            else operation.get('download_time_ms')
            if event_type == 'download'
            else operation.get('share_time_ms')
            if event_type == 'share'
            else operation.get('decryption_time_ms')
            if event_type == 'decryption'
            else 0
        )
        duration_sec = round((duration_ms or 0) / 1000, 4)
        upload_time_plain_sec = round((operation.get('plain_write_time_ms', 0) or 0) / 1000, 4)
        upload_time_encrypted_sec = round((operation.get('encrypted_write_time_ms', 0) or 0) / 1000, 4)
        download_time_plain_sec = round((operation.get('download_time_ms', 0) or 0) / 1000, 4)
        download_time_encrypted_sec = round((operation.get('encrypted_download_time_ms', 0) or 0) / 1000, 4)

        timestamp = operation['timestamp']
        date_shared = ''
        time_shared = ''
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            date_shared = dt.date().isoformat()
            time_shared = dt.time().strftime('%H:%M:%S')

        system_logger.log_file_event(
            file_id=file_id,
            file_type=file_type,
            file_size=file_size,
            event_type=event_type,
            duration_sec=duration_sec,
            owner=owner,
            date_shared=date_shared,
            time_shared=time_shared,
            upload_time_plain_sec=upload_time_plain_sec,
            upload_time_encrypted_sec=upload_time_encrypted_sec,
            download_time_plain_sec=download_time_plain_sec,
            download_time_encrypted_sec=download_time_encrypted_sec
        )

    def get_operation_logs(self, limit=10):
        """Get recent operation logs"""
        return self.file_operations[-limit:]

    def get_file_statistics(self):
        """
        Get file statistics

        Returns:
            dict: Statistics
        """
        total_downloads = sum(len(f.download_log) for f in self.files.values())

        total_uploaded_size = sum(f.file_size for f in self.files.values())
        total_encrypted_size = sum(f.encrypted_size for f in self.files.values())
        total_uploads = len([op for op in self.file_operations if op['operation'] == 'upload'])
        average_upload_size = total_uploaded_size / total_uploads if total_uploads else 0
        average_encryption_time = sum(op.get('encryption_time_ms', 0) for op in self.file_operations if op['operation'] == 'upload' and op.get('encryption_time_ms') is not None) / total_uploads if total_uploads else 0
        total_shares = len([op for op in self.file_operations if op['operation'] == 'share'])
        total_download_time = sum(op.get('download_time_ms', 0) for op in self.file_operations if op['operation'] == 'download' and op.get('download_time_ms') is not None)
        download_count = len([op for op in self.file_operations if op['operation'] == 'download'])
        average_download_time = total_download_time / download_count if download_count else 0
        total_decryption_time = sum(op.get('decryption_time_ms', 0) for op in self.file_operations if op['operation'] == 'decryption' and op.get('decryption_time_ms') is not None)
        decryption_count = len([op for op in self.file_operations if op['operation'] == 'decryption'])
        average_decryption_time = total_decryption_time / decryption_count if decryption_count else 0
        average_upload_speed_plain = sum(op.get('upload_speed_plain_mbps', 0) for op in self.file_operations if op['operation'] == 'upload') / total_uploads if total_uploads else 0
        average_upload_speed_encrypted = sum(op.get('upload_speed_encrypted_mbps', 0) for op in self.file_operations if op['operation'] == 'upload') / total_uploads if total_uploads else 0
        average_download_speed_plain = sum(op.get('download_speed_plain_mbps', 0) for op in self.file_operations if op['operation'] == 'download') / download_count if download_count else 0
        average_download_speed_encrypted = sum(op.get('download_speed_encrypted_mbps', 0) for op in self.file_operations if op['operation'] == 'download') / download_count if download_count else 0
        average_transfer_speed = sum(op.get('file_transfer_speed_mbps', 0) for op in self.file_operations if op['operation'] == 'download') / download_count if download_count else 0
        average_encryption_speed = sum(op.get('encryption_speed_mbps', 0) for op in self.file_operations if op['operation'] == 'upload') / total_uploads if total_uploads else 0
        average_decryption_speed = sum(op.get('decryption_speed_mbps', 0) for op in self.file_operations if op['operation'] == 'decryption') / decryption_count if decryption_count else 0
        average_size_overhead = sum(op.get('size_overhead_percent', 0) for op in self.file_operations if op['operation'] == 'upload') / total_uploads if total_uploads else 0

        return {
            'total_files': len(self.files),
            'total_downloads': total_downloads,
            'files_with_sharing': len([f for f in self.files.values() if f.shared_with]),
            'total_uploads': total_uploads,
            'total_shares': total_shares,
            'average_upload_size_bytes': round(average_upload_size, 2),
            'total_uploaded_size_bytes': total_uploaded_size,
            'total_encrypted_size_bytes': total_encrypted_size,
            'average_upload_speed_plain_mbps': round(average_upload_speed_plain, 2),
            'average_upload_speed_encrypted_mbps': round(average_upload_speed_encrypted, 2),
            'average_download_speed_plain_mbps': round(average_download_speed_plain, 2),
            'average_download_speed_encrypted_mbps': round(average_download_speed_encrypted, 2),
            'average_file_transfer_speed_mbps': round(average_transfer_speed, 2),
            'average_encryption_time_ms': round(average_encryption_time, 2),
            'average_encryption_speed_mbps': round(average_encryption_speed, 2),
            'average_download_time_ms': round(average_download_time, 2),
            'total_decryption_time_ms': round(total_decryption_time, 2),
            'average_decryption_time_ms': round(average_decryption_time, 2),
            'average_decryption_speed_mbps': round(average_decryption_speed, 2),
            'average_size_overhead_percent': round(average_size_overhead, 2),
            'recent_operations': self.file_operations[-5:]
        }


# Create singleton instance
file_manager = FileManager()
