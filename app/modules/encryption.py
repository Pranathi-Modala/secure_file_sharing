"""
==============================================
ENCRYPTION MODULE - Python Backend
==============================================
Provides AES-256 compatible file encryption/decryption
using Fernet (AES-CBC + HMAC) from cryptography.
"""

import time
from cryptography.fernet import Fernet, InvalidToken


class EncryptionEngine:
    """
    Handles encryption and decryption operations.
    Tracks timing metrics for quantitative analysis.
    """

    def __init__(self):
        """Initialize encryption statistics."""
        self.total_encryptions = 0
        self.total_decryptions = 0
        self.total_encryption_time_ms = 0.0
        self.total_decryption_time_ms = 0.0
        self.failed_encryptions = 0
        self.failed_decryptions = 0

    @staticmethod
    def generate_key():
        """
        Generate a new Fernet key.

        Returns:
            str: URL-safe base64 encoded key.
        """
        return Fernet.generate_key().decode("utf-8")

    @staticmethod
    def _build_cipher(key):
        """
        Build a Fernet cipher instance from string/bytes key.

        Args:
            key (str|bytes): Encryption key.

        Returns:
            Fernet: Initialized cipher.
        """
        key_bytes = key.encode("utf-8") if isinstance(key, str) else key
        return Fernet(key_bytes)

    def encrypt_file(self, plain_content, key):
        """
        Encrypt file bytes.

        Args:
            plain_content (bytes): Original file content.
            key (str|bytes): Fernet key.

        Returns:
            dict: Encryption result and metrics.
        """
        start = time.perf_counter()

        try:
            cipher = self._build_cipher(key)
            encrypted_content = cipher.encrypt(plain_content)
            elapsed_ms = (time.perf_counter() - start) * 1000

            self.total_encryptions += 1
            self.total_encryption_time_ms += elapsed_ms

            return {
                "success": True,
                "encrypted_content": encrypted_content,
                "encryption_time_ms": round(elapsed_ms, 2),
            }
        except Exception as exc:
            self.failed_encryptions += 1
            return {
                "success": False,
                "error": str(exc),
            }

    def decrypt_file(self, encrypted_content, key):
        """
        Decrypt encrypted file bytes.

        Args:
            encrypted_content (bytes): Encrypted bytes.
            key (str|bytes): Fernet key.

        Returns:
            dict: Decryption result and metrics.
        """
        start = time.perf_counter()

        try:
            cipher = self._build_cipher(key)
            decrypted_content = cipher.decrypt(encrypted_content)
            elapsed_ms = (time.perf_counter() - start) * 1000

            self.total_decryptions += 1
            self.total_decryption_time_ms += elapsed_ms

            return {
                "success": True,
                "decrypted_content": decrypted_content,
                "decryption_time_ms": round(elapsed_ms, 2),
            }
        except InvalidToken:
            self.failed_decryptions += 1
            return {
                "success": False,
                "error": "Invalid encryption key or corrupted data",
            }
        except Exception as exc:
            self.failed_decryptions += 1
            return {
                "success": False,
                "error": str(exc),
            }

    def get_statistics(self):
        """
        Return encryption engine statistics.

        Returns:
            dict: Aggregated operation metrics.
        """
        avg_encrypt = (
            self.total_encryption_time_ms / self.total_encryptions
            if self.total_encryptions
            else 0.0
        )
        avg_decrypt = (
            self.total_decryption_time_ms / self.total_decryptions
            if self.total_decryptions
            else 0.0
        )

        return {
            "total_encryptions": self.total_encryptions,
            "total_decryptions": self.total_decryptions,
            "failed_encryptions": self.failed_encryptions,
            "failed_decryptions": self.failed_decryptions,
            "average_encryption_time_ms": round(avg_encrypt, 2),
            "average_decryption_time_ms": round(avg_decrypt, 2),
            "total_encryption_time_ms": round(self.total_encryption_time_ms, 2),
            "total_decryption_time_ms": round(self.total_decryption_time_ms, 2),
        }


# Singleton instance used by routes
encryption_engine = EncryptionEngine()