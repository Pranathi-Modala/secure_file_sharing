"""
==============================================
STARTUP VALIDATION SCRIPT
==============================================
Week 5: Environment Hardening
Validates configuration, directory structure, and system readiness
Run this before starting the application
"""
from colorama import Fore, Style, init
import sys
import time
from pathlib import Path

init(autoreset=True)


def info(message):
    """Print informational message in yellow."""
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")


def success(message):
    """Print success message in green."""
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")


def fail(message):
    """Print failure message in red."""
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")


def loader(message, cycles=8, delay=0.06):
    """Show a short terminal loader animation in yellow."""
    frames = ['|', '/', '-', '\\']
    for i in range(cycles):
        frame = frames[i % len(frames)]
        print(f"\r{Fore.YELLOW}{message} {frame}{Style.RESET_ALL}", end='', flush=True)
        time.sleep(delay)
    print(f"\r{Fore.YELLOW}{message} ... done{Style.RESET_ALL}")


def pause(delay=0.15):
    """Small delay to make terminal output feel live."""
    time.sleep(delay)

def validate_startup():
    """
    Validate system startup requirements
    
    Returns:
        bool: True if all checks pass, False otherwise
    """
    info("\n" + "="*50)
    info("STARTUP VALIDATION")
    info("="*50 + "\n")
    
    checks_passed = 0
    checks_failed = 0
    total_checks = 8

    loader("Initializing validator")
    pause()
    
    # Check 1: Configuration file exists
    loader("Preparing check 1")
    info("Checking configuration file...")
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        success("   .env file found\n")
        checks_passed += 1
    else:
        fail("   .env file not found")
        info("   Copy .env.example to .env and configure\n")
        checks_failed += 1
    pause()
    
    # Check 2: Load configuration
    loader("Preparing check 2")
    info("Loading configuration...")
    try:
        import config
        success("   Configuration loaded successfully")
        info(f"   Environment: {config.config.ENV}")
        info(f"   Debug: {config.config.DEBUG}\n")
        checks_passed += 1
    except Exception as e:
        fail(f"   Failed to load configuration: {str(e)}\n")
        checks_failed += 1
        return False
    pause()
    
    # Check 3: Required directories exist
    loader("Preparing check 3")
    info("Checking required directories...")
    required_dirs = [
        config.config.UPLOAD_FOLDER,
        config.config.PLAIN_UPLOAD_FOLDER,
        config.config.ENCRYPTED_UPLOAD_FOLDER,
        config.config.LOG_FOLDER,
    ]
    
    all_dirs_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            success(f"   {dir_path}")
        else:
            fail(f"   {dir_path}")
            all_dirs_ok = False
    
    if all_dirs_ok:
        checks_passed += 1
        print()
    else:
        info("   Creating missing directories...\n")
        checks_failed += 1
    pause()
    
    # Check 4: Flask dependencies
    loader("Preparing check 4")
    info("Checking Python dependencies...")
    required_packages = {
        'flask': 'Flask',
        'cryptography': 'cryptography',
        'dotenv': 'python-dotenv',
        'psycopg2': 'psycopg2-binary',
    }

    if config.config.STORAGE_MODE.lower() == 'cloud':
        required_packages['azure.storage.blob'] = 'azure-storage-blob'
    
    all_packages_ok = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            success(f"   {package_name}")
        except ImportError:
            fail(f"   {package_name} not installed")
            all_packages_ok = False
    
    if all_packages_ok:
        checks_passed += 1
        info("   Install with: pip install -r requirements.txt\n")
    else:
        print()
        checks_failed += 1
    pause()
    
    # Check 5: Database configuration
    loader("Preparing check 5")
    info("Checking database configuration...")
    if config.config.DATABASE_URL and config.config.DATABASE_URL.startswith('postgresql://'):
        success("   DATABASE_URL is configured for PostgreSQL")
        checks_passed += 1
    else:
        fail("   DATABASE_URL is missing or invalid")
        checks_failed += 1
    print()
    pause()

    # Check 6: Database table initialization
    loader("Preparing check 6")
    info("Checking database table setup...")
    try:
        from app.modules.database import db_manager

        if db_manager is None:
            fail("   Database manager is not configured")
            checks_failed += 1
        else:
            db_manager.initialize_schema()
            required_tables = [db_manager.USER_TABLE]
            if config.config.STORAGE_MODE.lower() == 'cloud':
                required_tables.extend([
                    db_manager.FILE_TABLE,
                    db_manager.FILE_ACCESS_TABLE,
                    db_manager.FILE_EVENTS_TABLE,
                ])

            missing_tables = [table for table in required_tables if not db_manager.table_exists(table)]
            if not missing_tables:
                success(f"   Tables verified: {', '.join(required_tables)}")
                checks_passed += 1
            else:
                fail(f"   Missing tables: {', '.join(missing_tables)}")
                checks_failed += 1
    except Exception as e:
        fail(f"   Failed to verify database table: {str(e)}")
        checks_failed += 1

    print()
    pause()
    
    # Check 7: Cloud storage configuration and connectivity
    loader("Preparing check 7")
    info("Checking cloud storage readiness...")

    if config.config.STORAGE_MODE.lower() != 'cloud':
        info("   STORAGE_MODE is database (cloud checks skipped)")
        checks_passed += 1
    else:
        cloud_errors = []
        if config.config.CLOUD_PROVIDER != 'azure':
            cloud_errors.append("CLOUD_PROVIDER must be azure")

        if not config.config.AZURE_STORAGE_CONTAINER:
            cloud_errors.append("AZURE_STORAGE_CONTAINER is missing")

        has_auth = any([
            bool(config.config.AZURE_STORAGE_CONNECTION_STRING),
            bool(config.config.AZURE_STORAGE_ACCOUNT_NAME and config.config.AZURE_STORAGE_ACCOUNT_KEY),
            bool(config.config.AZURE_STORAGE_ACCOUNT_NAME and config.config.AZURE_STORAGE_SAS_TOKEN),
        ])
        if not has_auth:
            cloud_errors.append("No valid Azure auth method configured")

        if cloud_errors:
            for item in cloud_errors:
                fail(f"   {item}")
            checks_failed += 1
        else:
            try:
                from app.modules.cloud_storage import get_cloud_storage_client
                cloud_client = get_cloud_storage_client(config.config)
                healthy, message = cloud_client.health_check()
                if healthy:
                    success(f"   {message}")
                    checks_passed += 1
                else:
                    fail(f"   {message}")
                    checks_failed += 1
            except Exception as exc:
                fail(f"   Cloud startup check failed: {exc}")
                checks_failed += 1

    print()
    pause()

    # Check 8: Security settings
    loader("Preparing check 8")
    info("Checking security settings...")
    security_ok = True
    
    if config.config.ENV == 'production' and config.config.DEBUG:
        fail("   Debug mode enabled in production environment")
        security_ok = False
    else:
        success("   Debug mode appropriate for environment")
    
    if config.config.SECRET_KEY.startswith('dev-') and config.config.ENV == 'production':
        fail("   Using development secret key in production")
        security_ok = False
    else:
        success("   Secret key is configured")
    
    if security_ok:
        checks_passed += 1
    else:
        checks_failed += 1
    
    print()
    loader("Finalizing report")
    
    # Summary
    info("="*50)
    info("VALIDATION SUMMARY")
    info("="*50)
    success(f"Passed: {checks_passed}/{total_checks}")
    fail(f"Failed: {checks_failed}/{total_checks}\n")
    
    if checks_failed == 0:
        success("All checks passed! Application is ready to start.\n")
        info("Start the application with:")
        info("  python run.py\n")
        return True
    else:
        fail("Please fix the issues above before starting the application.\n")
        return False


if __name__ == '__main__':
    validation_success = validate_startup()
    sys.exit(0 if validation_success else 1)
