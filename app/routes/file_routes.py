"""
==============================================
FILE MANAGEMENT ROUTES - Flask Blueprints
==============================================
API endpoints for file operations
"""

from flask import Blueprint, request, jsonify, send_file
from modules.auth import auth_manager
from modules.file_manager import file_manager
from modules.encryption import encryption_engine
from modules.logger import system_logger
import logging
import io
import time

file_bp = Blueprint('files', __name__)

# Setup logging
logger = logging.getLogger(__name__)


def verify_session(session_id):
    """
    Helper function to verify session
    
    Args:
        session_id (str): Session identifier
        
    Returns:
        tuple: (session_info, error_response) or (None, None) if valid
    """
    session_info = auth_manager.verify_session(session_id)
    if not session_info:
        return None, (jsonify({'success': False, 'message': 'Invalid or expired session'}), 401)
    return session_info, None


@file_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload file with encryption
    POST /api/files/upload
    
    Expected:
    - session_id: str (form data)
    - file: File object
    """
    try:
        # Verify session
        session_id = request.form.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Get file
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        # Read file content
        file_content = file.read()
        original_size = len(file_content)

        # Generate encryption key
        encryption_key = encryption_engine.generate_key()

        # Encrypt file
        encrypt_result = encryption_engine.encrypt_file(file_content, encryption_key)

        if not encrypt_result['success']:
            return jsonify({
                'success': False,
                'message': 'Encryption failed',
                'error': encrypt_result.get('error')
            }), 500

        # Upload encrypted file
        upload_result = file_manager.upload_file(
            filename=file.filename,
            owner=username,
            plain_content=file_content,
            encrypted_content=encrypt_result['encrypted_content'],
            encryption_key=encryption_key,
            original_size=original_size,
            encryption_time_ms=encrypt_result['encryption_time_ms'],
            encrypted_size=len(encrypt_result['encrypted_content'])
        )

        if upload_result['success']:
            system_logger.info(f'File uploaded: {file.filename} by {username}')
            return jsonify({
                'success': True,
                'file_id': upload_result['file_id'],
                'filename': file.filename,
                'encryption_key': encryption_key,
                'message': 'File uploaded and encrypted successfully',
                'encryption_time_ms': encrypt_result['encryption_time_ms'],
                'upload_metrics': upload_result.get('upload_metrics', {})
            }), 201
        else:
            return jsonify(upload_result), 500

    except Exception as e:
        logger.error(f'Upload error: {str(e)}')
        system_logger.error(f'Upload error: {str(e)}')
        return jsonify({'success': False, 'message': 'Upload failed'}), 500


@file_bp.route('/share', methods=['POST'])
def share_file():
    """
    Share file with another user
    POST /api/files/share
    
    Expected JSON:
    {
        "session_id": "session_id",
        "file_id": "file_id",
        "recipient": "username",
        "include_key": true/false
    }
    """
    try:
        data = request.get_json()

        # Verify session
        session_id = data.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Validate input
        if not all(key in data for key in ['file_id', 'recipient']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        include_key = data.get('include_key', True)

        # Share file
        share_start = time.time()
        result = file_manager.share_file(
            file_id=data['file_id'],
            owner=username,
            recipient_username=data['recipient'],
            include_key=include_key,
            share_start=share_start
        )

        if result['success']:
            system_logger.info(
                f'File shared from {username} to {data["recipient"]}'
            )

            # Get the file to return encryption key if needed
            shared_file = file_manager.files.get(data['file_id'])
            if shared_file:
                return jsonify({
                    'success': True,
                    'message': result['message'],
                    'encryption_key': shared_file.encryption_key if include_key else None
                }), 200

        return jsonify(result), 400

    except Exception as e:
        logger.error(f'Share error: {str(e)}')
        system_logger.error(f'✗ Share error: {str(e)}')
        return jsonify({'success': False, 'message': 'Share failed'}), 500


@file_bp.route('/download/<file_id>', methods=['POST'])
def download_file(file_id):
    """
    Download and decrypt file
    POST /api/files/download/<file_id>
    
    Expected JSON:
    {
        "session_id": "session_id",
        "encryption_key": "key"
    }
    """
    try:
        data = request.get_json()

        # Verify session
        session_id = data.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Get file
        download_start = time.time()
        file_result = file_manager.get_file_for_download(file_id, username, download_start=download_start)

        if not file_result['success']:
            return jsonify(file_result), 403

        shared_file = file_result['file']
        download_metrics = file_result.get('download_metrics', {})
        encryption_key = data.get('encryption_key')

        # Verify encryption key
        if encryption_key != shared_file['encryption_key']:
            system_logger.warning(
                f'⚠ Incorrect encryption key used to download {file_id} by {username}'
            )
            return jsonify({
                'success': False,
                'message': 'Incorrect encryption key'
            }), 403

        # Decrypt file
        decrypt_result = encryption_engine.decrypt_file(
            shared_file['encrypted_content'],
            encryption_key
        )

        if not decrypt_result['success']:
            return jsonify({
                'success': False,
                'message': 'Decryption failed',
                'error': decrypt_result.get('error')
            }), 500

        # Log decryption timing in file operations
        decryption_time_ms = decrypt_result.get('decryption_time_ms', 0)
        decrypted_size = len(decrypt_result['decrypted_content'])
        encrypted_size = len(shared_file['encrypted_content'])
        decryption_speed_mbps = ((decrypted_size / (1024 * 1024)) / (decryption_time_ms / 1000)) if decryption_time_ms else 0
        download_total_time_ms = (time.time() - download_start) * 1000
        plain_download_speed_mbps = ((decrypted_size / (1024 * 1024)) / (download_total_time_ms / 1000)) if download_total_time_ms else 0
        encrypted_download_speed_mbps = download_metrics.get('encrypted_download_speed_mbps', 0)
        file_transfer_speed_mbps = ((encrypted_size / (1024 * 1024)) / (download_total_time_ms / 1000)) if download_total_time_ms else 0

        file_manager._log_operation({
            'operation': 'download',
            'filename': shared_file['filename'],
            'user': username,
            'file_id': file_id,
            'file_size': decrypted_size,
            'encrypted_size': encrypted_size,
            'download_time_ms': round(download_total_time_ms, 2),
            'encrypted_download_time_ms': round(download_metrics.get('encrypted_read_time_ms', 0), 2),
            'download_speed_plain_mbps': round(plain_download_speed_mbps, 2),
            'download_speed_encrypted_mbps': round(encrypted_download_speed_mbps, 2),
            'file_transfer_speed_mbps': round(file_transfer_speed_mbps, 2)
        })

        file_manager._log_operation({
            'operation': 'decryption',
            'filename': shared_file['filename'],
            'user': username,
            'file_id': file_id,
            'file_size': encrypted_size,
            'decryption_time_ms': decryption_time_ms,
            'decryption_speed_mbps': round(decryption_speed_mbps, 2)
        })

        system_logger.info(
            f'File downloaded and decrypted: {shared_file["filename"]} by {username} | download_time_ms={download_total_time_ms:.2f} | encrypted_download_speed_mbps={encrypted_download_speed_mbps:.2f} | plain_download_speed_mbps={plain_download_speed_mbps:.2f} | decryption_time_ms={decryption_time_ms:.2f} | decryption_speed_mbps={decryption_speed_mbps:.2f} | file_transfer_speed_mbps={file_transfer_speed_mbps:.2f}'
        )

        # Return decrypted file
        return send_file(
            io.BytesIO(decrypt_result['decrypted_content']),
            as_attachment=True,
            download_name=shared_file['filename'],
            mimetype='application/octet-stream'
        )

    except Exception as e:
        logger.error(f'Download error: {str(e)}')
        system_logger.error(f'✗ Download error: {str(e)}')
        return jsonify({'success': False, 'message': 'Download failed'}), 500


@file_bp.route('/my-files', methods=['POST'])
def list_my_files():
    """
    List files uploaded by user
    POST /api/files/my-files
    
    Expected JSON:
    {
        "session_id": "session_id"
    }
    """
    try:
        data = request.get_json()

        # Verify session
        session_id = data.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Get files
        files = file_manager.list_user_files(username)

        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        }), 200

    except Exception as e:
        logger.error(f'List files error: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to list files'}), 500


@file_bp.route('/shared-with-me', methods=['POST'])
def list_shared_files():
    """
    List files shared with user
    POST /api/files/shared-with-me
    
    Expected JSON:
    {
        "session_id": "session_id"
    }
    """
    try:
        data = request.get_json()

        # Verify session
        session_id = data.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Get shared files
        files = file_manager.list_shared_files(username)

        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        }), 200

    except Exception as e:
        logger.error(f'List shared files error: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to list shared files'}), 500


@file_bp.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    """
    Delete file (owner only)
    POST /api/files/delete/<file_id>
    
    Expected JSON:
    {
        "session_id": "session_id"
    }
    """
    try:
        data = request.get_json()

        # Verify session
        session_id = data.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Delete file
        result = file_manager.delete_file(file_id, username)

        if result['success']:
            system_logger.info(f'File deleted by {username}')

        return jsonify(result), 200 if result['success'] else 403

    except Exception as e:
        logger.error(f'Delete error: {str(e)}')
        return jsonify({'success': False, 'message': 'Delete failed'}), 500


@file_bp.route('/unshare', methods=['POST'])
def unshare_file():
    """
    Revoke file access from user
    POST /api/files/unshare
    
    Expected JSON:
    {
        "session_id": "session_id",
        "file_id": "file_id",
        "recipient": "username"
    }
    """
    try:
        data = request.get_json()

        # Verify session
        session_id = data.get('session_id')
        session_info, error = verify_session(session_id)
        if error:
            return error

        username = session_info['username']

        # Validate input
        if not all(key in data for key in ['file_id', 'recipient']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Unshare file
        result = file_manager.unshare_file(
            file_id=data['file_id'],
            owner=username,
            recipient=data['recipient']
        )

        if result['success']:
            system_logger.info(f'File access revoked by {username}')

        return jsonify(result), 200 if result['success'] else 403

    except Exception as e:
        logger.error(f'Unshare error: {str(e)}')
        return jsonify({'success': False, 'message': 'Unshare failed'}), 500


@file_bp.route('/stats', methods=['GET'])
def get_file_stats():
    """
    Get file operation statistics
    GET /api/files/stats
    """
    try:
        stats = file_manager.get_file_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f'Get stats error: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to get statistics'}), 500
