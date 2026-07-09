# 🚀 QUICK START GUIDE

## Secure File Transfer System - Flask Backend

### Week 2-3 Project Implementation

---

##  What's Been Created

A **complete Flask-based secure file transfer system** with:

✓ **Python Backend** (Flask) - as per your methodology
✓ **AES-256 Encryption** - Fernet cryptography library
✓ **User Authentication** - PBKDF2 password hashing
✓ **File Sharing** - Share with specific users
✓ **Key-Based Access** - Recipients need key to decrypt
✓ **OOP Architecture** - Modular Python classes
✓ **Clean Frontend** - Simple HTML/CSS/JS (no AI)
✓ **API Endpoints** - RESTful endpoints for all operations
✓ **Audit Logging** - Complete event tracking
✓ **Performance Metrics** - Encryption time tracking

---

##  Project Location

```
C:\Users\ADMIN\Desktop\NC Institute\FILE SHARING\secure_file_transfer
```

---

## ⚡ Installation & Running (Windows)

### Step 1: Install Python 3.8+

Download from: https://www.python.org/downloads/

### Step 2: Open Command Prompt

- Press `Win + R`
- Type: `cmd`
- Press Enter

### Step 3: Navigate to Project

```cmd
cd "C:\Users\ADMIN\Desktop\NC Institute\FILE SHARING\secure_file_transfer"
```

### Step 4: Run Application

```cmd
run.bat
```

**That's it!** The application will:

1. ✓ Install all dependencies
2. ✓ Start Flask server
3. ✓ Show: "Access at http://127.0.0.1:5000"

### Step 5: Open in Browser

Go to: **http://127.0.0.1:5000**

---

## 🔑 Demo Credentials

```
✓ User: alice    | Password: alice123
✓ User: bob      | Password: bob123
✓ User: admin    | Password: admin123
```

---

## 📋 Test Workflow

### Scenario: Alice Shares File with Bob

1. **Open http://127.0.0.1:5000**
2. **Login as Alice**
   - Username: alice
   - Password: alice123

3. **Upload a File**
   - Click " Upload File"
   - Select any file from your computer
   - Click "Upload"
   - System generates encryption key automatically

4. **Share with Bob**
   - File uploaded successfully
   - Modal appears to share
   - Select "bob" from dropdown
   - Check "Provide encryption key"
   - Click "Share"
   - Key is shown to Alice (can be copied)

5. **Login as Bob (New Browser Tab)**
   - Go to http://127.0.0.1:5000
   - Username: bob
   - Password: bob123

6. **Download Shared File**
   - Click " Shared with Me"
   - See file from alice
   - Click "Download"
   - Enter encryption key
   - File decrypts and downloads automatically!

---

## 🎯 Key Features to Try

### For Alice (File Owner):

- ✓ Upload files (auto-encrypted with AES-256)
- ✓ Share files with specific users
- ✓ Choose to include or exclude decryption key
- ✓ See who has access to each file
- ✓ Revoke access (unshare)
- ✓ Delete files

### For Bob (Recipient):

- ✓ See files shared with him
- ✓ Download files IF he has the key
- ✓ Cannot access without correct encryption key
- ✓ Download counter shows usage

---

##  System Architecture

```
Frontend (Browser)
    ↓ (HTTP Requests)
Flask Backend (Python)
    ├── Authentication Module
    │   └── User login, registration, sessions
    ├── Encryption Module
    │   └── AES-256 encrypt/decrypt
    ├── File Manager Module
    │   └── Upload, share, download, delete
    └── Logger Module
        └── Audit trail & performance tracking
```

---

##  How Encryption Works

1. **Upload File**

   ```
   Raw File → Generate AES-256 Key → Encrypt → Store Encrypted File
   ```

2. **Share File**

   ```
   Owner selects recipient
   ↓
   Choose: include key or require key
   ↓
   If include key: Recipient can decrypt immediately
   If exclude key: Recipient gets file but can't open
   ```

3. **Download File**
   ```
   Recipient has: Encrypted File + Encryption Key
   ↓
   Decrypt with key
   ↓
   Download original file
   ```

---

##  File Structure Explained

```
secure_file_transfer/
│
├── app/
│   ├── modules/
│   │   ├── encryption.py ─── AES-256 with Fernet
│   │   ├── auth.py ───────── User management
│   │   ├── file_manager.py ─ File operations
│   │   └── logger.py ─────── Event logging
│   │
│   ├── routes/
│   │   ├── auth_routes.py ─── /api/auth/* endpoints
│   │   ├── file_routes.py ─── /api/files/* endpoints
│   │   └── main_routes.py ─── / home page
│   │
│   ├── templates/
│   │   └── index.html ─────── UI HTML
│   │
│   ├── static/
│   │   ├── css/style.css ───── UI Styling
│   │   └── js/app.js ──────── Frontend logic
│   │
│   └── uploads/ ────────────── Encrypted files stored here
│
├── logs/
│   └── system.log ─────────── Audit trail & metrics
│
├── run.py ─────────────────── Main entry point
├── requirements.txt ──────── Python dependencies
└── README.md ──────────────── Full documentation
```

---

## 🔌 API Endpoints Overview

### Authentication

```
POST /api/auth/register      - Create account
POST /api/auth/login         - Login
POST /api/auth/logout        - Logout
GET  /api/auth/users         - List all users
```

### Files

```
POST /api/files/upload          - Upload & encrypt file
POST /api/files/share           - Share with user
POST /api/files/download/<id>   - Download & decrypt
POST /api/files/my-files        - List my files
POST /api/files/shared-with-me  - List shared with me
POST /api/files/delete/<id>     - Delete file
```

---

##  What Gets Logged

Everything is logged to `logs/system.log`:

✓ **Logins** - User, timestamp, duration
✓ **File Uploads** - Filename, size, encryption time
✓ **File Shares** - Who shared with whom, key included?
✓ **Downloads** - Who downloaded what, when
✓ **Encryption** - Time taken to encrypt/decrypt
✓ **Errors** - Any issues or unauthorized attempts

Example log entry:

```
2026-06-18 10:15:23 - Authentication successful for alice (15.3ms)
2026-06-18 10:16:45 - File uploaded: report.pdf (2.3MB) encrypted in 145.2ms
2026-06-18 10:17:12 - File shared from alice to bob with key included
```

---

##  Code Highlights

All code is fully commented. Example from `encryption.py`:

```python
def encrypt_file(self, file_content, key):
    """
    Encrypt file content using AES-256

    Args:
        file_content (bytes): Raw file data
        key (str): Base64 encryption key

    Returns:
        dict: {'success': True/False, 'encrypted_content': ...}
    """
    # Create Fernet cipher with provided key
    cipher = Fernet(key.encode())

    # Encrypt file
    encrypted = cipher.encrypt(file_content)

    # Return encrypted data
    return {'success': True, 'encrypted_content': encrypted}
```

---

##  Important Notes

1. **First Time Setup:**
   - May take 1-2 minutes first run (installing packages)
   - After that, starts in seconds

2. **Stop Server:**
   - Press `Ctrl + C` in the command prompt

3. **Restart Server:**
   - Close command prompt
   - Run `run.bat` again

4. **Clear Data:**
   - Delete `app/uploads/` folder
   - Deletes all stored encrypted files

5. **View Logs:**
   - Open `logs/system.log` with any text editor

---

##  Troubleshooting

| Issue                | Solution                                        |
| -------------------- | ----------------------------------------------- |
| "Python not found"   | Install Python 3.8+ from python.org             |
| "Module not found"   | Wait for `pip install` to complete              |
| "Port 5000 in use"   | Close other Flask apps or change port in run.py |
| "Cannot upload file" | Ensure user logged in, file < 50MB              |
| "Cannot decrypt"     | Check encryption key is exactly correct         |

---

##  For Your Session Presentation

This system demonstrates:

 **Week 2 Methodology**

- System architecture with modules
- Data collection methods (logging)
- Performance metrics tracking

 **Week 3 Data Collection**

- Real-time tracking of operations
- Authentication event logs
- Encryption performance data
- File transfer statistics

 **OOP Principles**

- EncryptionEngine class
- AuthenticationManager class
- FileManager class
- User class

 **Security Concepts**

- AES-256 encryption
- PBKDF2 password hashing
- Session management
- Access control

 **Real-World Application**

- User-to-user file sharing
- Secure key distribution
- Audit trails
- Performance analysis

---

## 📞 Next Steps

1. ✓ Install & run the application (Step-by-step above)
2. ✓ Test with Alice/Bob demo accounts
3. ✓ Try uploading and sharing files
4. ✓ Check `logs/system.log` to see metrics
5. ✓ Review code comments in `app/modules/` files
6. ✓ Use in your presentation!

---

##  Pro Tips

- **Save encryption keys:** Copy key before sharing to keep backup
- **Test different scenarios:** Try sharing without key
- **Check logs:** Review system.log to see all tracked metrics
- **Code review:** All modules have detailed comments explaining OOP
- **Customization:** Easy to add more features (email notifications, etc.)

---

**You're all set! Start with `run.bat` and access http://127.0.0.1:5000**

Happy presenting! 
