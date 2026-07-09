#  Secure File Transfer System - Flask Backend

## Week 2-3 Project Implementation with Python Flask

---

## 📋 Project Overview

This is a **production-ready Flask backend** for a secure file transfer system with:

-  **Python Flask** Backend (as per Week 2-3 methodology)
-  **AES-256 Encryption** using Fernet cryptography
-  **User-to-User File Sharing** with specific users
-  **Key-Based Decryption** - Recipients need key to decrypt
-  **OOP Architecture** with modular Python classes
-  **Complete Authentication System** with session management
-  **Comprehensive Logging** for audit trails
-  **Simple Non-AI Interface** (plain HTML/CSS/JS frontend)
-  **Performance Metrics** tracking
-  **Full Commented Code** explaining each block

---

##  Architecture & File Structure

```
secure_file_transfer/
├── run.py                              # Main entry point
├── run.bat                             # Windows startup script
├── run.sh                              # Linux/Mac startup script
├── requirements.txt                    # Python dependencies
├── README.md                           # This file
│
├── app/
│   ├── __init__.py                     # Flask app factory
│   ├── uploads/                        # Encrypted files storage
│   ├── templates/
│   │   └── index.html                  # Main UI interface
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css               # UI styling
│   │   └── js/
│   │       └── app.js                  # Frontend logic
│   │
│   ├── modules/                        # Backend OOP modules
│   │   ├── encryption.py               # AES-256 encryption
│   │   ├── auth.py                     # Authentication & users
│   │   ├── file_manager.py             # File sharing & access control
│   │   └── logger.py                   # System logging
│   │
│   └── routes/                         # Flask API endpoints
│       ├── auth_routes.py              # Auth API (/api/auth/*)
│       ├── file_routes.py              # File API (/api/files/*)
│       └── main_routes.py              # Main page route
│
└── logs/                               # Application logs
    └── system.log                      # Audit trail
```

---

## 🚀 Quick Start

### 1. **Install Python**

Download Python 3.8+ from [python.org](https://www.python.org)

### 2. **Navigate to Project Directory**

```bash
cd "C:\Users\ADMIN\Documents"
```

### 3. **Install Dependencies**
##### Create Virtual Environment

```bash
python -m venv venv

```

```bash
venv\scripts\activate
```

```bash
pip install -r requirements.txt
```

### 4. **Run the Application**

**Windows:**

```bash
run.bat
```

**Linux/Mac:**

```bash
bash run.sh
```

**Or directly:**

```bash
python run.py
```

### 5. **Access Application**

Open browser and go to: **http://127.0.0.1:5000**

---

## 👤 Demo Credentials

```
User 1 (Alice):
  Username: alice
  Password: alice123
  Email: alice@secure.com

User 2 (Bob):
  Username: bob
  Password: bob123
  Email: bob@secure.com

Admin:
  Username: admin
  Password: admin123
  Email: admin@secure.com
```

---

## 🏛️ Module Architecture

### 1. **Encryption Module** (`encryption.py`)

Handles AES-256 encryption using Fernet from cryptography library.

**Key Classes:**

- `EncryptionEngine` - Manages encryption operations

**Key Methods:**

```python
# Generate secure key
key = EncryptionEngine.generate_key()

# Encrypt file
result = engine.encrypt_file(file_content, key)

# Decrypt file
result = engine.decrypt_file(encrypted_content, key)

# Get statistics
stats = engine.get_statistics()
```

**Features:**

-  Generates secure random keys
-  Derives keys from passwords
-  Encrypts/decrypts file content
-  Tracks encryption performance metrics

---

### 2. **Authentication Module** (`auth.py`)

Manages user authentication, registration, and session control.

**Key Classes:**

- `User` - Represents user object
- `AuthenticationManager` - Handles authentication

**Key Methods:**

```python
# Register user
result = auth_manager.register_user(username, password, email)

# Login user
result = auth_manager.login(username, password)
# Returns: {success, message, session_id, user}

# Logout
auth_manager.logout(session_id)

# Verify session
session_info = auth_manager.verify_session(session_id)
```

**Features:**

-  User registration with validation
-  Password hashing with PBKDF2
-  Session management
-  Failed attempt tracking
-  Authentication logging

---

### 3. **File Manager Module** (`file_manager.py`)

Handles file storage, sharing, and access control.

**Key Classes:**

- `SharedFile` - Represents shared file with metadata
- `FileManager` - Manages file operations

**Key Methods:**

```python
# Upload file
result = file_manager.upload_file(filename, owner, encrypted_content, key, size)

# Share file with specific user
result = file_manager.share_file(file_id, owner, recipient, include_key=True)

# Get file for download (with access check)
result = file_manager.get_file_for_download(file_id, username)

# List user's files
files = file_manager.list_user_files(username)

# List files shared with user
shared = file_manager.list_shared_files(username)

# Delete file (owner only)
result = file_manager.delete_file(file_id, owner)

# Revoke access
result = file_manager.unshare_file(file_id, owner, recipient)
```

**Features:**

-  Upload encrypted files
-  Share specific files with specific users
-  Owner-based access control
-  Optional key sharing (recipient needs key to decrypt)
-  Download tracking
-  File deletion with permission check

---

### 4. **Logger Module** (`logger.py`)

Centralized logging for audit trail.

**Features:**

-  File and console logging
-  Timestamp on all events
-  Error tracking
-  System event recording

---

## 🔌 API Endpoints

### Authentication Routes (`/api/auth/\*)

```
POST /api/auth/register
  Body: {"username": "user", "password": "pass", "email": "email"}
  Returns: {success, message, user}

POST /api/auth/login
  Body: {"username": "user", "password": "pass"}
  Returns: {success, session_id, user}

POST /api/auth/logout
  Body: {"session_id": "id"}
  Returns: {success, message}

POST /api/auth/verify
  Body: {"session_id": "id"}
  Returns: {success, username, login_time}

GET /api/auth/users
  Returns: {success, users, count}

GET /api/auth/stats
  Returns: {success, stats}
```

### File Routes (`/api/files/\*)

```
POST /api/files/upload
  Form: file, session_id
  Returns: {success, file_id, filename, encryption_key}

POST /api/files/share
  Body: {session_id, file_id, recipient, include_key}
  Returns: {success, message, encryption_key}

POST /api/files/download/<file_id>
  Body: {session_id, encryption_key}
  Returns: Decrypted file (binary)

POST /api/files/my-files
  Body: {session_id}
  Returns: {success, files}

POST /api/files/shared-with-me
  Body: {session_id}
  Returns: {success, files}

POST /api/files/delete/<file_id>
  Body: {session_id}
  Returns: {success, message}

POST /api/files/unshare
  Body: {session_id, file_id, recipient}
  Returns: {success, message}

GET /api/files/stats
  Returns: {success, stats}
```

---

##  Security Features

### Encryption

- **Algorithm:** AES-256 using Fernet (symmetric encryption)
- **Key Generation:** Cryptographically secure random keys
- **File Encryption:** All files encrypted before storage
- **Key Distribution:** Share key with specific recipients

### Authentication

- **Password Hashing:** PBKDF2 with 100,000 iterations
- **Session Management:** Unique session IDs per login
- **Failed Attempt Tracking:** Logs suspicious activity

### Access Control

- **File Ownership:** Only owner can delete/reshare
- **Recipient Authorization:** Only shared recipients can access
- **Key-Based Access:** Recipient must have correct key to decrypt

### Audit Trail

- **Event Logging:** All operations logged with timestamp
- **Performance Tracking:** Encryption/decryption times recorded
- **Security Events:** Unauthorized access attempts logged

---

##  Usage Workflow

### 1. **User Registration**

```
User visits application
→ Clicks "Create Account"
→ Enters username, email, password
→ System hashes password with PBKDF2
→ User registered in system
```

### 2. **File Upload & Encryption**

```
Logged-in user selects file
→ System generates AES-256 encryption key
→ File encrypted with key using Fernet
→ Encrypted file stored on server
→ Key displayed to user (must save for sharing)
```

### 3. **File Sharing**

```
User clicks "Share" on their file
→ Selects recipient user
→ Chooses: "Include key" or "Key required"
→ System creates share record
→ If key included, recipient can immediately decrypt
→ If key not included, recipient must ask for key
```

### 4. **File Download & Decryption**

```
Recipient sees shared file
→ Clicks "Download"
→ Enters encryption key (or uses provided key)
→ System verifies key matches
→ File decrypted on server
→ Decrypted file sent to user
→ Download recorded in audit log
```

### 5. **File Management**

```
User can:
  - List all their uploaded files
  - See who files are shared with
  - Revoke access (unshare)
  - Delete files
  - View all files shared with them
  - Download shared files (with key)
```

---

## 🧪 Testing the System

### Test Scenario 1: File Sharing Between Users

1. **Login as Alice**
   - Username: alice, Password: alice123

2. **Upload a file**
   - Click "Upload File"
   - Select any file
   - Click "Upload"
   - System generates encryption key (example: `gAAAAABm...`)

3. **Share with Bob**
   - Click "Share" on uploaded file
   - Select "bob" as recipient
   - Check "Provide encryption key"
   - Click "Share"

4. **Login as Bob (new browser tab)**
   - Username: bob, Password: bob123

5. **Access shared file**
   - Go to "Shared with Me" section
   - See file from Alice
   - Click "Download"
   - Enter encryption key (provided by Alice)
   - File decrypts and downloads

### Test Scenario 2: File Without Key

1. **Share file WITHOUT key**
   - Uncheck "Provide encryption key" before sharing
   - Bob receives file but cannot decrypt without key

2. **Bob needs to ask for key**
   - File visible in Bob's "Shared with Me"
   - Cannot download without correct encryption key

---

##  Performance Metrics Tracked

The system tracks:

- **Encryption Time (ms)** - How long to encrypt file
- **Decryption Time (ms)** - How long to decrypt file
- **File Size** - Original and encrypted size
- **Login Time (ms)** - Authentication duration
- **Transfer Operations** - Uploads, downloads count
- **Failed Attempts** - Security incidents

View in `/logs/system.log` after running application.

---

##  Configuration

### Maximum File Size

Edit in `app/__init__.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

### Upload Folder

Edit in `app/__init__.py`:

```python
app.config['UPLOAD_FOLDER'] = os.path.join(...)
```

### Secret Key

Edit in `app/__init__.py`:

```python
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

---

## 💾 Data Storage

### Encrypted Files

Location: `app/uploads/`

- Files stored encrypted on disk
- Original filename preserved in database
- Encryption key stored separately

### User Database

In-memory during session (can be extended to SQLite/PostgreSQL)

- User credentials (hashed)
- Session information
- File metadata

### Logs

Location: `logs/system.log`

- All system events
- Authentication attempts
- File operations
- Encryption metrics

---

##  Troubleshooting

### "Flask not found" error

**Solution:** Install requirements

```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"

**Solution:** Kill process using port or change in `run.py`:

```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Cannot upload file

**Ensure:**

- User is logged in
- File size < 50MB
- File has valid format
- Disk has space

### Encryption key not working

**Check:**

- Using exact key (case-sensitive)
- File hasn't been modified
- Correct recipient used key

---

##  Code Examples

### Example 1: Upload & Encrypt File

```python
from modules.encryption import encryption_engine
from modules.file_manager import file_manager

# Read file
with open('document.pdf', 'rb') as f:
    file_content = f.read()

# Generate encryption key
key = encryption_engine.generate_key()

# Encrypt file
result = encryption_engine.encrypt_file(file_content, key)

# Store encrypted file
if result['success']:
    upload_result = file_manager.upload_file(
        filename='document.pdf',
        owner='alice',
        encrypted_content=result['encrypted_content'],
        encryption_key=key,
        original_size=len(file_content)
    )
```

### Example 2: Share & Download

```python
# Share file with bob, including key
file_manager.share_file(
    file_id='abc123',
    owner='alice',
    recipient_username='bob',
    include_key=True
)

# Bob downloads file
download_result = file_manager.get_file_for_download('abc123', 'bob')

if download_result['success']:
    file_data = download_result['file']
    key = file_data['encryption_key']

    # Decrypt
    decrypt_result = encryption_engine.decrypt_file(
        file_data['encrypted_content'],
        key
    )

    # Save decrypted file
    with open('decrypted_document.pdf', 'wb') as f:
        f.write(decrypt_result['decrypted_content'])
```

---

##  Learning Outcomes

This project demonstrates:

1. **Python OOP** - Class-based architecture
2. **Flask Basics** - Web framework fundamentals
3. **Cryptography** - Real encryption implementation
4. **Authentication** - Secure user management
5. **File Management** - Secure file operations
6. **API Design** - RESTful endpoints
7. **Security Best Practices** - Password hashing, audit trails
8. **Performance Metrics** - System monitoring

---

##  Real-World Applications

This architecture is used by:

- Cloud storage services (Dropbox, OneDrive, Google Drive)
- Secure file sharing platforms (WeTransfer, Sync.com)
- Enterprise collaboration tools
- Healthcare HIPAA-compliant systems
- Legal document management

---

## 📝 Notes

- **Demo Only:** For production, use established libraries (boto3 for S3, etc.)
- **Database:** Currently in-memory, extend with SQLAlchemy + PostgreSQL
- **Encryption:** AES-256 is production-grade but test thoroughly
- **SSL/HTTPS:** Enable in production environment
- **Rate Limiting:** Add for production to prevent abuse

---

## 🎯 Next Steps

Enhance the system with:

1. **Database Integration** - SQLAlchemy + PostgreSQL
2. **Cloud Storage** - AWS S3 or Azure Blob Storage
3. **Email Notifications** - Notify on file shared
4. **Two-Factor Authentication** - 2FA support
5. **Advanced Permissions** - View-only, comment, etc.
6. **Version Control** - Multiple file versions
7. **Search & Tagging** - Better file organization
8. **Mobile App** - React Native client

---

## 📞 Support

For issues:

1. Check `logs/system.log` for error messages
2. Verify Python version (3.8+)
3. Ensure all dependencies installed
4. Check file permissions in `app/uploads/`
5. Verify Flask is running on correct port

---

##  License & Attribution

Week 2-3 Project Implementation

- **Research Methodology:** Chapter 3, Week 2 submission
- **Data Collection:** Week 3 weekly report
- **Implementation:** Secure File Transfer System Demo

---

**Last Updated:** 2026-06-18
**Version:** 2.0 - Flask Backend Release
**Status:** Production Ready for Demo
