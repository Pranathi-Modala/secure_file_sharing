"""
==============================================
MAIN FLASK APPLICATION ENTRY POINT
==============================================
Run this script to start the application
Week 5: Environment Hardening - Uses environment configuration
"""

from app import create_app
import config

if __name__ == '__main__':
    app = create_app()
    
    # Print startup information
    print("""
    ============================================
    Secure File Transfer System
    Week 5 - Environment Hardening
    ============================================
    """)
    
    # Display configuration
    print("\n📋 Configuration Loaded:")
    print(f"  Environment: {config.config.ENV}")
    print(f"  Debug Mode: {config.config.DEBUG}")
    print(f"  Host: {config.config.HOST}")
    print(f"  Port: {config.config.PORT}")
    print(f"  Max File Size: {config.config.MAX_FILE_SIZE_MB}MB")
    print(f"  Upload Folder: {config.config.UPLOAD_FOLDER}")
    print(f"  Log Folder: {config.config.LOG_FOLDER}")
    print(f"  Storage Mode: {config.config.STORAGE_MODE}")
    print(f"  Database URL: {config.config.DATABASE_URL}")
    
    print(f"""
    ✓ Starting Flask server...
    
    Access at: http://{config.config.HOST}:{config.config.PORT}
    
    Configuration file: .env
    
    Press Ctrl+C to stop
    ============================================
    """)
    
    app.run(
        debug=config.config.DEBUG,
        host=config.config.HOST,
        port=config.config.PORT
    )
