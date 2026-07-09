# Environment Setup Guide for Week 5+

## Overview

This guide explains how to set up your local environment after Week 5 environment hardening implementation.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `flask` - Web framework
- `cryptography` - Encryption library
- `python-dotenv` - Environment variable management

## Step 2: Configure Environment

### Option A: Development (Recommended for local testing)

```bash
# Copy the template
cp .env.example .env

# No additional changes needed - defaults are configured for development
```

Your `.env` file will contain:

```env
FLASK_ENV=development
DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### Option B: Testing

```bash
# Copy template
cp .env.example .env

# Edit to use different port
nano .env
# Change: FLASK_PORT=5001
```

### Option C: Production (Important security steps!)

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env

# CRITICAL CHANGES REQUIRED:
# 1. Set secure random SECRET_KEY (don't use the default)
#    FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
# 2. Set environment
#    FLASK_ENV=production
# 3. Disable debug
#    DEBUG=False
# 4. Configure server host
#    FLASK_HOST=0.0.0.0
```

## Step 3: Validate Setup

```bash
python validate_startup.py
```

Expected output:

```
==================================================
🔍 STARTUP VALIDATION
==================================================

1️⃣  Checking configuration file...
   ✓ .env file found

2️⃣  Loading configuration...
   ✓ Configuration loaded successfully
   → Environment: development
   → Debug: True

3️⃣  Checking required directories...
   ✓ app/uploads
   ✓ app/uploads/plain_uploads
   ✓ app/uploads/encrypted_uploads
   ✓ logs

4️⃣  Checking Python dependencies...
   ✓ Flask
   ✓ cryptography
   ✓ python-dotenv

5️⃣  Checking demo users...
   ✓ 3 demo users configured:
      - admin
      - alice
      - bob

6️⃣  Checking security settings...
   ✓ Debug mode appropriate for environment
   ✓ Secret key is configured

📊 VALIDATION SUMMARY
==================================================
✓ Passed: 6/6
✗ Failed: 0/6

✅ All checks passed! Application is ready to start.
```

## Step 4: Start Application

```bash
python run.py
```

Expected output:

```
============================================
Secure File Transfer System
Week 5 - Environment Hardening
============================================

📋 Configuration Loaded:
  Environment: development
  Debug Mode: True
  Host: 127.0.0.1
  Port: 5000
  Max File Size: 50MB
  Upload Folder: app/uploads
  Log Folder: logs
  Storage Mode: in-memory

👥 Demo Users Available:
  - admin / admin123 (admin@secure.com)
  - alice / alice123 (alice@secure.com)
  - bob / bob123 (bob@secure.com)

✓ Starting Flask server...

Access at: http://127.0.0.1:5000
```

## Access Application

Open your browser to: `http://127.0.0.1:5000`

## Demo Credentials

Use these to test the application:

- **Username:** admin, alice, or bob
- **Password:** admin123, alice123, or bob123

## Configuration Reference

### Core Settings

```env
FLASK_SECRET_KEY          # Session encryption key (change for production!)
FLASK_ENV                 # environment: development, testing, production
DEBUG                     # Enable Flask debug mode (False for production)
FLASK_HOST                # Server host (127.0.0.1 for local, 0.0.0.0 for network)
FLASK_PORT                # Server port (5000 default)
```

### File Management

```env
MAX_FILE_SIZE_MB          # Maximum file upload size (50 MB default)
UPLOAD_FOLDER             # Base upload directory
PLAIN_UPLOAD_FOLDER       # Unencrypted files directory
ENCRYPTED_UPLOAD_FOLDER   # Encrypted files directory
```

### Logging

```env
LOG_FOLDER                # Directory for logs
LOG_LEVEL                 # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Security

```env
SESSION_TIMEOUT_MINUTES   # Session duration
MAX_LOGIN_ATTEMPTS        # Failed attempts before lockout
LOCKOUT_DURATION_MINUTES  # Lockout window duration
```

### Demo Users (for testing)

```env
DEMO_USERS                # Format: username:password:email|username:password:email|...
```

## Environment-Specific Examples

### Development

```env
FLASK_SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### Testing

```env
FLASK_SECRET_KEY=test-secret-key
FLASK_ENV=testing
DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5001
```

### Production

```env
FLASK_SECRET_KEY=<use-secure-random-value-from-key-generator>
FLASK_ENV=production
DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
MAX_LOGIN_ATTEMPTS=3
SESSION_TIMEOUT_MINUTES=15
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Solution:**

```bash
pip install python-dotenv
```

### Issue: "Address already in use"

**Solution:** Change FLASK_PORT in .env

```env
FLASK_PORT=5001  # Use a different port
```

### Issue: "Configuration validation failed"

**Solution:** Run validation to see what's missing

```bash
python validate_startup.py
```

### Issue: "Permission denied" on logs

**Solution:** Ensure logs directory is writable

```bash
mkdir -p logs
chmod 755 logs
```

## .gitignore Setup

**Important:** Ensure `.env` is in `.gitignore` to prevent committing secrets!

Add to `.gitignore`:

```
.env
.env.local
*.pyc
__pycache__/
logs/
app/uploads/
venv/
.vscode/
.idea/
```

This prevents accidental commits of:

- `.env` files with secrets
- Uploaded files
- Log files
- Virtual environment
- IDE settings

## Generating Secure Secret Key

For production, generate a cryptographically secure key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or using Python:

```python
import secrets
secret_key = secrets.token_hex(32)
print(f"FLASK_SECRET_KEY={secret_key}")
```

## Next Steps After Setup

1. ✅ Validate environment setup
2. ✅ Start the application
3. ✅ Test login with demo users
4. ✅ Upload a test file
5. ✅ Check logs in `logs/` folder

## Support

For issues or questions about environment setup:

1. Check validation output: `python validate_startup.py`
2. Review configuration: `nano .env`
3. Check logs: `logs/system.log`
4. Refer to `WEEK5_ENVIRONMENT_HARDENING.md` for detailed documentation

---

_Week 5 Environment Configuration Guide - Complete_
