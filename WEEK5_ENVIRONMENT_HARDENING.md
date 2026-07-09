# Week 5: Data and Environment Hardening

## 📋 Week 5 Summary

**Dates:** Current Implementation Period  
**Focus:** Environment Configuration, Secrets Management, and Startup Validation  
**Status:** ✅ COMPLETE

---

## 🎯 Objectives Achieved

### 1. ✅ Environment Configuration System

**Objective:** Move hardcoded configuration to environment variables  
**Completion:** 100%

- **Created centralized config module** (`config.py`)
  - Loads settings from `.env` file using `python-dotenv`
  - Validates all configuration on startup
  - Provides typed configuration access throughout application
  - Graceful fallback for missing config items

- **Configuration managed areas:**
  - Flask app settings (SECRET_KEY, DEBUG, HOST, PORT)
  - File upload settings (MAX_FILE_SIZE_MB, folder paths)
  - Logging configuration (log folder, log level)
  - Demo users (configurable list with format)
  - Security settings (session timeout, login attempts)
  - Encryption settings (algorithm, key rotation policy)
  - Storage mode (in-memory vs. future database)
  - Research/metrics settings

### 2. ✅ Secrets Management

**Objective:** Eliminate hardcoded secrets from source code  
**Completion:** 100%

**Before (Hardcoded):**

```python
app.config['SECRET_KEY'] = 'secure-file-transfer-demo-key-2024'
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
demo_users = [('admin', 'admin123', ...), ...]
```

**After (Environment-based):**

```python
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
# Demo users loaded from config.DEMO_USERS
```

**Updated Files:**

- `app/__init__.py` - Uses config module
- `run.py` - Loads and displays configuration
- `app/modules/auth.py` - Demo users from config
- `app/modules/logger.py` - Log folder from config

### 3. ✅ Environment Files Created

**Objective:** Provide example and local configuration templates  
**Completion:** 100%

**Files Created:**

1. **`.env.example`** - Template with all configuration options
   - Comprehensive comments explaining each setting
   - Secure defaults recommended
   - NOT to be committed to version control

2. **`.env`** - Local development configuration
   - Pre-configured with development defaults
   - Contains demo user credentials for testing
   - Should be added to `.gitignore`

**Configuration Categories in .env:**

```
FLASK_SECRET_KEY           # Session encryption key
FLASK_ENV                  # development or production
DEBUG                      # Enable Flask debug mode
FLASK_HOST                 # Server host (127.0.0.1)
FLASK_PORT                 # Server port (5000)

MAX_FILE_SIZE_MB           # Max upload (50 MB)
UPLOAD_FOLDER              # Upload directory path
PLAIN_UPLOAD_FOLDER        # Unencrypted files directory
ENCRYPTED_UPLOAD_FOLDER    # Encrypted files directory

LOG_FOLDER                 # Logging directory
LOG_LEVEL                  # DEBUG, INFO, WARNING, ERROR, CRITICAL

DEMO_USERS                 # Pipe-separated user credentials
SESSION_TIMEOUT_MINUTES    # Session duration
MAX_LOGIN_ATTEMPTS         # Before temporary lockout
LOCKOUT_DURATION_MINUTES   # Lockout window

ENCRYPTION_ALGORITHM       # Fernet (AES-256)
KEY_ROTATION_POLICY        # none, periodic, on-access

STORAGE_MODE               # in-memory or database (future)
METRICS_ENABLED            # Enable research metrics
METRICS_OUTPUT_FILE        # Metrics storage path
```

### 4. ✅ Startup Validation System

**Objective:** Validate system readiness before application start  
**Completion:** 100%

**Created `validate_startup.py`** - Performs 6 validation checks:

1. **Configuration File Validation**
   - Checks `.env` file exists
   - Reports if missing and suggests action

2. **Configuration Loading**
   - Verifies config.py can be imported
   - Tests configuration parsing
   - Displays loaded environment

3. **Directory Structure Validation**
   - Verifies all required folders exist:
     - UPLOAD_FOLDER
     - PLAIN_UPLOAD_FOLDER
     - ENCRYPTED_UPLOAD_FOLDER
     - LOG_FOLDER
   - Automatically creates missing directories

4. **Python Dependencies Check**
   - Verifies Flask is installed
   - Verifies cryptography library
   - Verifies python-dotenv
   - Suggests pip install if missing

5. **Demo Users Validation**
   - Confirms demo users are configured
   - Lists available demo users
   - Warns if no users configured (non-fatal)

6. **Security Settings Validation**
   - Flags debug mode in production
   - Validates SECRET_KEY in production
   - Ensures appropriate security posture

**Usage:**

```bash
python validate_startup.py
```

**Output Example:**

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

... [more checks] ...

📊 VALIDATION SUMMARY
==================================================
✓ Passed: 6/6
✗ Failed: 0/6

✅ All checks passed! Application is ready to start.
```

### 5. ✅ Application Entry Point Updated

**Objective:** Display configuration at startup and validate environment  
**Completion:** 100%

**Updated `run.py`:**

- Imports config module early (triggers validation)
- Displays configuration on startup
- Shows demo users available
- Reports any configuration issues before Flask starts

**Startup Output:**

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

Configuration file: .env

Press Ctrl+C to stop
```

### 6. ✅ Storage Mode Decision

**Objective:** Document persistent storage approach  
**Completion:** 100%

**Decision: In-Memory Storage (Academic Prototype)**

**Rationale:**

- **Prototype Scope:** System is designed as an academic demonstration
- **Simplicity:** Enables focus on encryption, transfer, and metrics
- **Research Goals:** Emphasis on timing measurements and protocol validation
- **Course Requirements:** Meets academic evaluation needs

**Implementation:**

- All user data stored in memory: `AuthenticationManager.users`
- All file metadata stored in memory: `FileManager.files`
- Session management in-memory: `active_sessions`
- Logs and metrics written to CSV/files (persistent)

**Configuration:**

```env
STORAGE_MODE=in-memory
```

**Future Path (Not in Week 5):**

- Option B (Week 5+ Future): Migrate to SQLite
  - Add `DATABASE_URL=sqlite:///secure_file_transfer.db`
  - Define schema for users, files, shares, audit logs
  - Implement persistence layer between modules and database
  - Expected Week 9-10 if course requires it

**Advantages of Current Approach:**

- ✅ No external database dependencies
- ✅ Fast iteration and testing
- ✅ Fits academic timeline
- ✅ Clear data model visibility
- ✅ Perfect for metrics collection

**Limitations (Documented):**

- ❌ Data lost on application restart
- ❌ Not suitable for production multi-user deployment
- ❌ No persistence across sessions
- ❌ Single-instance only

---

## 📦 Files Created/Modified

### New Files

| File                  | Purpose                                         |
| --------------------- | ----------------------------------------------- |
| `config.py`           | Centralized configuration management module     |
| `.env`                | Local development configuration (with defaults) |
| `.env.example`        | Configuration template for new deployments      |
| `validate_startup.py` | Startup validation and system readiness checker |

### Modified Files

| File                    | Changes                                       |
| ----------------------- | --------------------------------------------- |
| `app/__init__.py`       | Import config, use environment settings       |
| `run.py`                | Load config, display configuration on startup |
| `app/modules/auth.py`   | Load demo users from config                   |
| `app/modules/logger.py` | Load log folder from config                   |
| `requirements.txt`      | Already includes `python-dotenv` ✓            |

---

## 🔒 Security Improvements

### Before Week 5

```
❌ Hardcoded SECRET_KEY in app/__init__.py
❌ Hardcoded demo credentials in auth.py
❌ Hardcoded paths and ports
❌ No environment validation
❌ No startup checks
```

### After Week 5

```
✅ SECRET_KEY from environment (.env)
✅ Demo credentials configurable via environment
✅ All paths configurable
✅ Comprehensive startup validation
✅ Security checks (debug in production, weak keys)
✅ Clear separation of configuration and code
✅ Template for production deployment
```

---

## 🚀 How to Use

### Initial Setup

```bash
# 1. Copy template to .env
cp .env.example .env

# 2. Edit .env if needed (optional - defaults are good for development)
# - Change FLASK_SECRET_KEY to a secure random value for production
# - Adjust port/host if default conflicts
# - Configure demo users if needed

# 3. Validate configuration
python validate_startup.py

# 4. Start application
python run.py
```

### Configuration for Different Environments

**Development (Default .env):**

```env
FLASK_ENV=development
DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

**Testing:**

```env
FLASK_ENV=testing
DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5001  # Different port to avoid conflicts
```

**Production (Never hardcoded - use actual secrets):**

```env
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=<use-strong-random-value-here>
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
```

### Environment Variables Reference

**Flask Settings**

```env
FLASK_SECRET_KEY=your-secure-key          # Change for production!
FLASK_ENV=development|production|testing  # Environment mode
DEBUG=True|False                           # Enable debug mode
FLASK_HOST=127.0.0.1                      # Server host
FLASK_PORT=5000                           # Server port
```

**File Management**

```env
MAX_FILE_SIZE_MB=50                        # Max upload size
UPLOAD_FOLDER=app/uploads                 # Upload base path
PLAIN_UPLOAD_FOLDER=app/uploads/plain_uploads
ENCRYPTED_UPLOAD_FOLDER=app/uploads/encrypted_uploads
```

**Logging**

```env
LOG_FOLDER=logs                            # Log directory
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL
```

**Security**

```env
SESSION_TIMEOUT_MINUTES=30                 # Session duration
MAX_LOGIN_ATTEMPTS=5                       # Failed attempts before lockout
LOCKOUT_DURATION_MINUTES=15                # Lockout window
```

**Demo Users**

```env
DEMO_USERS=username:password:email | username:password:email | ...
# Example: admin:admin123:admin@secure.com | alice:alice123:alice@secure.com
```

---

## ✅ Week 5 Completion Checklist

- [x] Created centralized configuration module (`config.py`)
- [x] Moved hardcoded secrets to environment variables
- [x] Created `.env.example` template
- [x] Created `.env` local configuration
- [x] Updated `app/__init__.py` to use config
- [x] Updated `run.py` to load and display config
- [x] Updated `auth.py` to use configured demo users
- [x] Updated `logger.py` to use configured log folder
- [x] Created `validate_startup.py` validation script
- [x] Implemented configuration validation
- [x] Created directory structure verification
- [x] Added security checks (debug mode, secret key)
- [x] Documented storage mode decision (in-memory)
- [x] Tested configuration loading
- [x] Tested startup validation
- [x] Created comprehensive Week 5 documentation

---

## 🔍 Validation Tests

**Test 1: Configuration Loading**

```bash
python validate_startup.py
# Expected: All checks pass
```

**Test 2: Application Startup**

```bash
python run.py
# Expected: Server starts with no errors, configuration displayed
```

**Test 3: Login with Configured Users**

```bash
# Access http://127.0.0.1:5000
# Login with: admin / admin123
# Expected: Login succeeds
```

**Test 4: Configuration Modification**

```bash
# Edit .env
# Change: FLASK_PORT=5001
# Run: python run.py
# Expected: Server starts on port 5001
```

---

## 📊 Configuration Impact Analysis

| Component            | Before          | After         | Status      |
| -------------------- | --------------- | ------------- | ----------- |
| **Secrets**          | Hardcoded       | Environment   | ✅ Fixed    |
| **Demo Users**       | Hardcoded list  | Configurable  | ✅ Fixed    |
| **Directories**      | Hardcoded paths | Configurable  | ✅ Fixed    |
| **Port/Host**        | Hardcoded       | Configurable  | ✅ Fixed    |
| **Validation**       | None            | Comprehensive | ✅ Added    |
| **Deployment Ready** | ❌ No           | ✅ Yes        | ✅ Improved |

---

## 🎓 Academic Context

**Course Goal:** Develop a secure file transfer system with encryption and metrics collection.

**Week 5 Contribution:**

- ✅ Professional environment management practices
- ✅ Security-first configuration approach
- ✅ System validation and reliability
- ✅ Foundation for reproducible experiments

**Research Implication:**

- Configuration can be easily changed for different test scenarios
- Metrics output paths configurable for organized collection
- Demo users consistent and reproducible across test runs
- Clear audit trail of environment settings for research validity

---

## 🚦 Next Steps (Week 6 Preview)

**Week 6: Authentication Completion**

- Account lockout after failed attempts (configured: MAX_LOGIN_ATTEMPTS)
- Password policy implementation
- JWT token option (if chosen over sessions)
- Enhanced auth logging and metrics

**Configuration prepared for Week 6:**

- `MAX_LOGIN_ATTEMPTS` - Already configurable
- `LOCKOUT_DURATION_MINUTES` - Already configurable
- `SESSION_TIMEOUT_MINUTES` - Already configurable
- Demo users ready for testing

---

## 📝 Version Information

- **Week 5 Completion Date:** [Current Date]
- **Configuration Format:** `.env` (python-dotenv compatible)
- **Python Version:** 3.7+
- **Flask Version:** 2.3.3+
- **Dependencies:** See requirements.txt

---

## 💡 Key Takeaways

1. **No Secrets in Code:** All sensitive values moved to environment
2. **Flexible Configuration:** Different configs for dev/test/prod
3. **Validation-First:** System validates before startup
4. **Deployment Ready:** `.env.example` and guides for deployment
5. **Security Posture:** Detection of insecure configurations
6. **Reproducible:** Configuration-driven setup for research validity
7. **Auditable:** Configuration displayed on startup and logged

---

_Week 5 complete. Configuration system production-ready for academic deployment._
