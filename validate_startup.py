"""
==============================================
STARTUP VALIDATION SCRIPT
==============================================
Week 5: Environment Hardening
Validates configuration, directory structure, and system readiness
Run this before starting the application
"""

import sys
import os
from pathlib import Path

def validate_startup():
    """
    Validate system startup requirements
    
    Returns:
        bool: True if all checks pass, False otherwise
    """
    print("\n" + "="*50)
    print("🔍 STARTUP VALIDATION")
    print("="*50 + "\n")
    
    checks_passed = 0
    checks_failed = 0
    
    # Check 1: Configuration file exists
    print("1️⃣  Checking configuration file...")
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("   ✓ .env file found\n")
        checks_passed += 1
    else:
        print("   ✗ .env file not found")
        print("   → Copy .env.example to .env and configure\n")
        checks_failed += 1
    
    # Check 2: Load configuration
    print("2️⃣  Loading configuration...")
    try:
        import config
        print(f"   ✓ Configuration loaded successfully")
        print(f"   → Environment: {config.config.ENV}")
        print(f"   → Debug: {config.config.DEBUG}\n")
        checks_passed += 1
    except Exception as e:
        print(f"   ✗ Failed to load configuration: {str(e)}\n")
        checks_failed += 1
        return False
    
    # Check 3: Required directories exist
    print("3️⃣  Checking required directories...")
    required_dirs = [
        config.config.UPLOAD_FOLDER,
        config.config.PLAIN_UPLOAD_FOLDER,
        config.config.ENCRYPTED_UPLOAD_FOLDER,
        config.config.LOG_FOLDER,
    ]
    
    all_dirs_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"   ✓ {dir_path}")
        else:
            print(f"   ✗ {dir_path}")
            all_dirs_ok = False
    
    if all_dirs_ok:
        checks_passed += 1
        print()
    else:
        print("   → Creating missing directories...\n")
        checks_failed += 1
    
    # Check 4: Flask dependencies
    print("4️⃣  Checking Python dependencies...")
    required_packages = {
        'flask': 'Flask',
        'cryptography': 'cryptography',
        'dotenv': 'python-dotenv',
    }
    
    all_packages_ok = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✓ {package_name}")
        except ImportError:
            print(f"   ✗ {package_name} not installed")
            all_packages_ok = False
    
    if all_packages_ok:
        checks_passed += 1
        print("   → Install with: pip install -r requirements.txt\n")
    else:
        print()
        checks_failed += 1
    
    # Check 5: Demo users configured
    print("5️⃣  Checking demo users...")
    if config.config.DEMO_USERS:
        print(f"   ✓ {len(config.config.DEMO_USERS)} demo users configured:")
        for username, password, email in config.config.DEMO_USERS:
            print(f"      - {username}")
        checks_passed += 1
        print()
    else:
        print("   ⚠️  No demo users configured (DEMO_USERS is empty)\n")
        # This is a warning, not a failure
        checks_passed += 1
        print()
    
    # Check 6: Security settings
    print("6️⃣  Checking security settings...")
    security_ok = True
    
    if config.config.ENV == 'production' and config.config.DEBUG:
        print("   ✗ Debug mode enabled in production environment")
        security_ok = False
    else:
        print("   ✓ Debug mode appropriate for environment")
    
    if config.config.SECRET_KEY.startswith('dev-') and config.config.ENV == 'production':
        print("   ✗ Using development secret key in production")
        security_ok = False
    else:
        print("   ✓ Secret key is configured")
    
    if security_ok:
        checks_passed += 1
    else:
        checks_failed += 1
    
    print()
    
    # Summary
    print("="*50)
    print(f"📊 VALIDATION SUMMARY")
    print("="*50)
    print(f"✓ Passed: {checks_passed}/6")
    print(f"✗ Failed: {checks_failed}/6\n")
    
    if checks_failed == 0:
        print("✅ All checks passed! Application is ready to start.\n")
        print("Start the application with:")
        print("  python run.py\n")
        return True
    else:
        print("❌ Please fix the issues above before starting the application.\n")
        return False


if __name__ == '__main__':
    success = validate_startup()
    sys.exit(0 if success else 1)
