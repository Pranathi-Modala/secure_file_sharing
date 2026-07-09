"""
==============================================
AUTHENTICATION ROUTES - Flask Blueprints
==============================================
API endpoints for user authentication
"""

from flask import Blueprint, request, jsonify
from modules.auth import auth_manager
from modules.logger import system_logger
import logging

auth_bp = Blueprint('auth', __name__)

# Setup logging
logger = logging.getLogger(__name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user
    POST /api/auth/register
    
    Expected JSON:
    {
        "username": "username",
        "password": "password",
        "email": "email@example.com"
    }
    """
    try:
        data = request.get_json()

        # Validate input
        if not data or not all(key in data for key in ['username', 'password', 'email']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Register user
        result = auth_manager.register_user(
            username=data['username'],
            password=data['password'],
            email=data['email']
        )

        if result['success']:
            system_logger.info(f'✓ New user registered: {data["username"]}')
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        return jsonify({'success': False, 'message': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    POST /api/auth/login
    
    Expected JSON:
    {
        "username": "username",
        "password": "password"
    }
    """
    try:
        data = request.get_json()

        # Validate input
        if not data or not all(key in data for key in ['username', 'password']):
            return jsonify({'success': False, 'message': 'Missing credentials'}), 400

        # Login user
        result = auth_manager.login(
            username=data['username'],
            password=data['password']
        )

        if result['success']:
            system_logger.info(f'✓ User logged in: {data["username"]}')
            return jsonify(result), 200
        else:
            return jsonify(result), 401

    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return jsonify({'success': False, 'message': 'Login failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user
    POST /api/auth/logout
    
    Expected JSON:
    {
        "session_id": "session_id"
    }
    """
    try:
        data = request.get_json()

        if not data or 'session_id' not in data:
            return jsonify({'success': False, 'message': 'Missing session_id'}), 400

        result = auth_manager.logout(data['session_id'])

        if result['success']:
            system_logger.info('✓ User logged out')
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f'Logout error: {str(e)}')
        return jsonify({'success': False, 'message': 'Logout failed'}), 500


@auth_bp.route('/verify', methods=['POST'])
def verify_session():
    """
    Verify session validity
    POST /api/auth/verify
    
    Expected JSON:
    {
        "session_id": "session_id"
    }
    """
    try:
        data = request.get_json()

        if not data or 'session_id' not in data:
            return jsonify({'success': False, 'message': 'Missing session_id'}), 400

        session_info = auth_manager.verify_session(data['session_id'])

        if session_info:
            return jsonify({
                'success': True,
                'username': session_info['username'],
                'login_time': session_info['login_time']
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid or expired session'}), 401

    except Exception as e:
        logger.error(f'Session verification error: {str(e)}')
        return jsonify({'success': False, 'message': 'Verification failed'}), 500


@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    Get list of all users
    GET /api/auth/users
    """
    try:
        users = auth_manager.get_all_users()
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200

    except Exception as e:
        logger.error(f'Get users error: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to get users'}), 500


@auth_bp.route('/stats', methods=['GET'])
def get_auth_stats():
    """
    Get authentication statistics
    GET /api/auth/stats
    """
    try:
        stats = auth_manager.get_auth_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f'Get stats error: {str(e)}')
        return jsonify({'success': False, 'message': 'Failed to get statistics'}), 500
