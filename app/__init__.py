"""
==============================================
FLASK APPLICATION CONFIGURATION
==============================================
Main Flask app initialization
Week 5: Environment Hardening - Loads config from config.py
"""

from flask import Flask
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import configuration from config.py
import config
from modules.database import db_manager

def create_app():
    """
    Create and configure Flask application
    Uses centralized configuration from config.py

    Returns:
        Flask: Configured Flask app
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static',
                static_url_path='/static')

    # Apply configuration from config module
    app.config['SECRET_KEY'] = config.config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.config.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = str(config.config.UPLOAD_FOLDER)
    app.config['PLAIN_UPLOAD_FOLDER'] = str(config.config.PLAIN_UPLOAD_FOLDER)
    app.config['ENCRYPTED_UPLOAD_FOLDER'] = str(config.config.ENCRYPTED_UPLOAD_FOLDER)
    app.config['DATABASE_URL'] = config.config.DATABASE_URL

    # Directories are created by config.validate() during initialization
    # but ensure they exist at app creation time
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PLAIN_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ENCRYPTED_UPLOAD_FOLDER'], exist_ok=True)

    # Ensure required database tables exist before serving requests.
    if db_manager is None:
        raise RuntimeError('Database manager is not configured. Check DATABASE_URL settings.')
    db_manager.initialize_schema()

    # Register blueprints (routes)
    from routes.auth_routes import auth_bp
    from routes.file_routes import file_bp
    from routes.main_routes import main_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(file_bp, url_prefix='/api/files')
    app.register_blueprint(main_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
