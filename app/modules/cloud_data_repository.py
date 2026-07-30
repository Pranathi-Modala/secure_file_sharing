"""
Cloud-native JSON repositories for users, file metadata/access, and metrics.
"""

import json
import secrets
from datetime import datetime, timezone
from urllib.parse import quote

import config as cfg
from modules.cloud_storage import CloudStorageError, get_cloud_storage_client


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def _safe_id(raw_value):
    return quote(str(raw_value), safe='-_')


class CloudJsonStore:
    """Simple JSON document store over the configured cloud object storage."""

    def __init__(self, cloud_client, data_prefix='app-data/'):
        self.cloud_client = cloud_client
        self.data_prefix = (data_prefix or '').strip('/')

    def _object_name(self, relative_path):
        clean_relative = relative_path.lstrip('/').strip()
        if not self.data_prefix:
            return clean_relative
        return f"{self.data_prefix}/{clean_relative}".replace('//', '/')

    def put_json(self, relative_path, payload):
        object_name = self._object_name(relative_path)
        serialized = json.dumps(payload, ensure_ascii=True, separators=(',', ':'))
        self.cloud_client.upload_text_object(object_name, serialized)
        return object_name

    def get_json(self, relative_path):
        object_name = self._object_name(relative_path)
        serialized = self.cloud_client.download_text_object(object_name)
        if serialized is None:
            return None
        return json.loads(serialized)

    def delete_json(self, relative_path):
        object_name = self._object_name(relative_path)
        return self.cloud_client.delete_object(object_name)

    def list_objects(self, relative_prefix):
        object_prefix = self._object_name(relative_prefix)
        return self.cloud_client.list_object_keys(object_prefix)

    def list_json(self, relative_prefix):
        records = []
        for object_key in self.list_objects(relative_prefix):
            serialized = self.cloud_client.download_text_object(object_key)
            if serialized is None:
                continue
            try:
                records.append(json.loads(serialized))
            except json.JSONDecodeError:
                continue
        return records


class CloudUserRepository:
    """Cloud-backed user records repository."""

    USERS_PREFIX = 'users/'

    def __init__(self, store):
        self.store = store

    def _user_doc(self, username):
        return f"{self.USERS_PREFIX}{_safe_id(username)}.json"

    def create_user(self, username, password_hash, email):
        if self.get_user_by_username(username):
            return {'success': False, 'message': 'User already exists'}

        all_users = self.get_all_users()
        email_taken = any((entry.get('email') or '').lower() == email.lower() for entry in all_users)
        if email_taken:
            return {'success': False, 'message': 'User already exists'}

        max_user_id = max((int(entry.get('user_id', 0)) for entry in all_users), default=0)
        user = {
            'user_id': max_user_id + 1,
            'username': username,
            'password_hash': password_hash,
            'email': email,
            'created_at': _utc_now_iso(),
        }
        self.store.put_json(self._user_doc(username), user)
        return {'success': True, 'user': user}

    def get_user_by_username(self, username):
        return self.store.get_json(self._user_doc(username))

    def get_all_users(self):
        users = self.store.list_json(self.USERS_PREFIX)
        users.sort(key=lambda item: int(item.get('user_id', 0)))
        return users

    def delete_user(self, username):
        return self.store.delete_json(self._user_doc(username))


class CloudFileRepository:
    """Cloud-backed file metadata and access repository."""

    FILES_PREFIX = 'files/'
    ACCESS_PREFIX = 'access/'

    def __init__(self, store):
        self.store = store

    def _file_doc(self, file_id):
        return f"{self.FILES_PREFIX}{_safe_id(file_id)}.json"

    def _access_doc(self, file_id, granted_to):
        return f"{self.ACCESS_PREFIX}{_safe_id(file_id)}__{_safe_id(granted_to)}.json"

    def _normalize(self, data):
        return dict(data) if data else None

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
        metadata = {
            'file_id': file_id,
            'owner_username': owner_username,
            'original_filename': original_filename,
            'file_type': file_type,
            'plain_size_bytes': plain_size_bytes,
            'encrypted_size_bytes': encrypted_size_bytes,
            'cloud_object_key': cloud_object_key,
            'checksum_sha256': checksum_sha256,
            'uploaded_at': _utc_now_iso(),
        }
        self.store.put_json(self._file_doc(file_id), metadata)
        return self._normalize(metadata)

    def get_file_metadata(self, file_id):
        return self._normalize(self.store.get_json(self._file_doc(file_id)))

    def list_owned_files(self, owner_username):
        all_files = self.store.list_json(self.FILES_PREFIX)
        owned_files = [item for item in all_files if item.get('owner_username') == owner_username]
        owned_files.sort(key=lambda item: item.get('uploaded_at', ''), reverse=True)
        return [self._normalize(item) for item in owned_files]

    def list_all_files(self):
        all_files = self.store.list_json(self.FILES_PREFIX)
        all_files.sort(key=lambda item: item.get('uploaded_at', ''), reverse=True)
        return [self._normalize(item) for item in all_files]

    def list_shared_files(self, username):
        access_records = self.store.list_json(self.ACCESS_PREFIX)
        shared_entries = [item for item in access_records if item.get('granted_to') == username]
        shared_entries.sort(key=lambda item: item.get('granted_at', ''), reverse=True)

        results = []
        for access in shared_entries:
            file_id = access.get('file_id')
            metadata = self.get_file_metadata(file_id)
            if not metadata:
                continue
            results.append({
                **metadata,
                'key_provided': bool(access.get('key_provided')),
                'granted_at': access.get('granted_at'),
            })
        return results

    def list_access_records(self, file_id=None, granted_to=None):
        records = self.store.list_json(self.ACCESS_PREFIX)

        if file_id is not None:
            records = [item for item in records if item.get('file_id') == file_id]

        if granted_to is not None:
            records = [item for item in records if item.get('granted_to') == granted_to]

        records.sort(key=lambda item: item.get('granted_at', ''), reverse=True)
        return [self._normalize(item) for item in records]

    def grant_access(self, file_id, granted_to, key_provided=True):
        access_record = {
            'file_id': file_id,
            'granted_to': granted_to,
            'key_provided': bool(key_provided),
            'granted_at': _utc_now_iso(),
        }
        self.store.put_json(self._access_doc(file_id, granted_to), access_record)
        return self._normalize(access_record)

    def revoke_access(self, file_id, granted_to):
        return self.store.delete_json(self._access_doc(file_id, granted_to))

    def can_user_access(self, file_id, username):
        metadata = self.get_file_metadata(file_id)
        is_owner = bool(metadata and metadata.get('owner_username') == username)

        access_record = self.store.get_json(self._access_doc(file_id, username))
        has_access = bool(access_record)
        key_provided = bool(access_record.get('key_provided')) if access_record else False

        return {
            'can_access': is_owner or has_access,
            'is_owner': is_owner,
            'key_provided': True if is_owner else key_provided,
        }

    def delete_file_metadata(self, file_id, owner_username):
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            return False
        if metadata.get('owner_username') != owner_username:
            return False

        self.store.delete_json(self._file_doc(file_id))

        access_prefix = f"{self.ACCESS_PREFIX}{_safe_id(file_id)}__"
        for object_key in self.store.list_objects(access_prefix):
            self.store.cloud_client.delete_object(object_key)

        return True


class CloudMetricsRepository:
    """Cloud-backed operational event repository."""

    EVENTS_PREFIX = 'events/'

    def __init__(self, store):
        self.store = store

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
        event_status='success',
        event_message=None,
    ):
        event_id = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}_{secrets.token_hex(6)}"
        payload = {
            'event_id': event_id,
            'file_id': file_id,
            'actor_username': actor_username,
            'event_type': event_type,
            'encryption_time_ms': encryption_time_ms,
            'decryption_time_ms': decryption_time_ms,
            'upload_time_ms': upload_time_ms,
            'download_time_ms': download_time_ms,
            'upload_speed_mbps': upload_speed_mbps,
            'download_speed_mbps': download_speed_mbps,
            'transfer_speed_mbps': transfer_speed_mbps,
            'event_status': event_status,
            'event_message': event_message,
            'created_at': _utc_now_iso(),
        }

        self.store.put_json(f"{self.EVENTS_PREFIX}{event_id}.json", payload)
        return payload

    def count_events(self):
        return len(self.store.list_objects(self.EVENTS_PREFIX))

    def list_events(self):
        events = self.store.list_json(self.EVENTS_PREFIX)
        events.sort(key=lambda item: item.get('created_at', ''), reverse=True)
        return events


def _build_cloud_store():
    cloud_client = get_cloud_storage_client(cfg.config)
    return CloudJsonStore(cloud_client, cfg.config.CLOUD_DATA_PREFIX)


def _build_cloud_repositories():
    store = _build_cloud_store()
    return (
        CloudUserRepository(store),
        CloudFileRepository(store),
        CloudMetricsRepository(store),
    )


cloud_user_repository = None
cloud_file_repository = None
cloud_metrics_repository = None
cloud_data_error = None

if cfg.config.STORAGE_MODE.lower() == 'cloud':
    try:
        cloud_user_repository, cloud_file_repository, cloud_metrics_repository = _build_cloud_repositories()
    except CloudStorageError as exc:
        cloud_data_error = str(exc)
