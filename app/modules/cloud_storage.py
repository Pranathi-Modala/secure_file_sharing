"""
Cloud storage abstractions and Azure Blob implementation.
"""

from abc import ABC, abstractmethod

import config as cfg


class CloudStorageError(Exception):
    """Raised when cloud storage operations fail."""


class CloudStorageClient(ABC):
    """Abstract cloud storage client."""

    @abstractmethod
    def upload_encrypted_file(self, file_id, encrypted_bytes, object_name):
        """Upload encrypted bytes and return cloud object key."""

    @abstractmethod
    def download_encrypted_file(self, object_key):
        """Download encrypted bytes by cloud object key."""

    @abstractmethod
    def delete_encrypted_file(self, object_key):
        """Delete encrypted object by cloud object key."""

    @abstractmethod
    def health_check(self):
        """Validate connectivity and permissions."""


class AzureBlobStorageClient(CloudStorageClient):
    """Azure Blob Storage client for encrypted file objects."""

    def __init__(self, config_obj=None):
        self.config = config_obj or cfg.config
        self.container_name = self.config.AZURE_STORAGE_CONTAINER
        self.object_prefix = (self.config.CLOUD_OBJECT_PREFIX or "encrypted/").strip("/")

        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError as exc:
            raise CloudStorageError(
                "azure-storage-blob is not installed. Install from requirements.txt"
            ) from exc

        self._blob_service_client = self._build_blob_service_client(BlobServiceClient)
        self._container_client = self._blob_service_client.get_container_client(self.container_name)

    def _build_blob_service_client(self, blob_service_client_cls):
        if self.config.AZURE_STORAGE_CONNECTION_STRING:
            return blob_service_client_cls.from_connection_string(
                self.config.AZURE_STORAGE_CONNECTION_STRING
            )

        account_name = self.config.AZURE_STORAGE_ACCOUNT_NAME
        endpoint_suffix = self.config.AZURE_STORAGE_ENDPOINT_SUFFIX or "core.windows.net"
        account_url = f"https://{account_name}.blob.{endpoint_suffix}"

        credential = self.config.AZURE_STORAGE_ACCOUNT_KEY or self.config.AZURE_STORAGE_SAS_TOKEN
        if not credential:
            raise CloudStorageError(
                "No Azure credential configured. Set connection string, account key, or SAS token."
            )

        return blob_service_client_cls(account_url=account_url, credential=credential)

    def _normalize_object_key(self, object_name):
        clean_name = object_name.lstrip("/")
        if not self.object_prefix:
            return clean_name
        return f"{self.object_prefix}/{clean_name}".replace("//", "/")

    def upload_encrypted_file(self, file_id, encrypted_bytes, object_name):
        object_key = self._normalize_object_key(object_name)
        blob_client = self._container_client.get_blob_client(object_key)
        blob_client.upload_blob(encrypted_bytes, overwrite=True)
        return object_key

    def download_encrypted_file(self, object_key):
        blob_client = self._container_client.get_blob_client(object_key)
        stream = blob_client.download_blob()
        return stream.readall()

    def delete_encrypted_file(self, object_key):
        blob_client = self._container_client.get_blob_client(object_key)
        blob_client.delete_blob(delete_snapshots="include")
        return True

    def health_check(self):
        try:
            self._container_client.get_container_properties()
            # Validate list permission with tiny call.
            list(self._container_client.list_blobs(name_starts_with=self.object_prefix, results_per_page=1))
            return True, "Azure Blob container is reachable"
        except Exception as exc:
            return False, f"Azure Blob health check failed: {exc}"


def get_cloud_storage_client(config_obj=None):
    """Factory for configured cloud storage client."""
    active_config = config_obj or cfg.config
    provider = (active_config.CLOUD_PROVIDER or "").lower()

    if provider == "azure":
        return AzureBlobStorageClient(active_config)

    raise CloudStorageError(f"Unsupported cloud provider: {provider}")
