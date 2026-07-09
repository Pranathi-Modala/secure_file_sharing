"""
==============================================
MAIN ROUTES - Flask Blueprints
==============================================
Main page and UI routes
"""

from flask import Blueprint, render_template, jsonify
from modules.auth import auth_manager
from modules.encryption import encryption_engine
from modules.file_manager import file_manager

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Render main page
    """
    return render_template('index.html')


@main_bp.route('/api/system/stats', methods=['GET'])
def system_stats():
    """
    Get overall system statistics
    GET /api/system/stats
    """
    auth_stats = auth_manager.get_auth_statistics()
    file_stats = file_manager.get_file_statistics()
    encryption_stats = encryption_engine.get_statistics()

    return jsonify({
        'success': True,
        'authentication': auth_stats,
        'files': file_stats,
        'encryption': encryption_stats
    }), 200
