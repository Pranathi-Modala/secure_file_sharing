/**
 * ============================================
 * FRONTEND JAVASCRIPT - Client-side logic
 * ============================================
 * Handles UI interactions and API communication
 */

class SecureFileTransferClient {
  constructor() {
    this.sessionId = null;
    this.currentUser = null;
    this.files = [];
    this.sharedFiles = [];
    this.initializeEventListeners();
    this.checkExistingSession();
  }

  // ============ INITIALIZATION ============

  initializeEventListeners() {
    // Auth buttons
    document
      .getElementById("btn-login")
      ?.addEventListener("click", () => this.handleLogin());
    document
      .getElementById("btn-register-submit")
      ?.addEventListener("click", () => this.handleRegister());
    document
      .getElementById("btn-toggle-register")
      ?.addEventListener("click", () => this.toggleRegister());
    document
      .getElementById("btn-toggle-login")
      ?.addEventListener("click", () => this.toggleRegister());
    document
      .getElementById("btn-logout")
      ?.addEventListener("click", () => this.handleLogout());

    // File operations
    document
      .getElementById("btn-upload")
      ?.addEventListener("click", () => this.handleUpload());
    document
      .getElementById("btn-refresh-files")
      ?.addEventListener("click", () => this.loadMyFiles());
    document
      .getElementById("btn-refresh-shared")
      ?.addEventListener("click", () => this.loadSharedFiles());

    // Sidebar navigation
    document.querySelectorAll(".sidebar button").forEach((btn) => {
      btn.addEventListener("click", (e) =>
        this.switchSection(e.target.dataset.section),
      );
    });

    // Modal
    document
      .getElementById("btn-share-cancel")
      ?.addEventListener("click", () => this.closeShareModal());
    document
      .getElementById("btn-share-confirm")
      ?.addEventListener("click", () => this.confirmShare());
  }

  checkExistingSession() {
    const saved = localStorage.getItem("sft_session");
    if (saved) {
      const session = JSON.parse(saved);
      this.sessionId = session.sessionId;
      this.currentUser = session.user;
      this.showDashboard();
      this.loadMyFiles();
      this.loadSharedFiles();
    }
  }

  // ============ AUTHENTICATION ============

  async handleLogin() {
    const username = document.getElementById("input-login-username").value;
    const password = document.getElementById("input-login-password").value;

    if (!username || !password) {
      this.showMessage("Please enter username and password", "error");
      return;
    }

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (data.success) {
        this.sessionId = data.session_id;
        this.currentUser = data.user;

        // Save session
        localStorage.setItem(
          "sft_session",
          JSON.stringify({
            sessionId: this.sessionId,
            user: this.currentUser,
          }),
        );

        this.showMessage(`✓ Welcome ${username}!`, "success");
        this.showDashboard();
        this.loadMyFiles();
        this.loadSharedFiles();
      } else {
        this.showMessage(data.message, "error");
      }
    } catch (error) {
      console.error("Login error:", error);
      this.showMessage("Login failed", "error");
    }
  }

  async handleRegister() {
    const username = document.getElementById("input-register-username").value;
    const password = document.getElementById("input-register-password").value;
    const email = document.getElementById("input-register-email").value;

    if (!username || !password || !email) {
      this.showMessage("Please fill all fields", "error");
      return;
    }

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email }),
      });

      const data = await response.json();

      if (data.success) {
        this.showMessage("✓ Registration successful! Now login.", "success");
        this.toggleRegister();
        document.getElementById("input-login-username").value = username;
        document.getElementById("input-login-password").value = "";
      } else {
        this.showMessage(data.message, "error");
      }
    } catch (error) {
      console.error("Registration error:", error);
      this.showMessage("Registration failed", "error");
    }
  }

  handleLogout() {
    localStorage.removeItem("sft_session");
    this.sessionId = null;
    this.currentUser = null;
    this.showMessage("✓ Logged out", "success");
    this.showAuthPanel();
  }

  toggleRegister() {
    const loginBox = document.querySelector('[data-form="login"]');
    const registerBox = document.querySelector('[data-form="register"]');

    if (loginBox.style.display === "none") {
      loginBox.style.display = "block";
      registerBox.style.display = "none";
    } else {
      loginBox.style.display = "none";
      registerBox.style.display = "block";
    }
  }

  // ============ FILE OPERATIONS ============

  async handleUpload() {
    const fileInput = document.getElementById("input-file");
    if (!fileInput.files.length) {
      this.showMessage("Please select a file", "error");
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_id", this.sessionId);

    try {
      this.showMessage("Uploading and encrypting file...", "info");

      const response = await fetch("/api/files/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        this.showMessage(
          `✓ File uploaded! Encryption key: ${data.encryption_key.substring(0, 20)}...`,
          "success",
        );
        fileInput.value = "";
        this.loadMyFiles();

        // Show share option
        this.currentShareFileId = data.file_id;
        this.currentEncryptionKey = data.encryption_key;
        this.showShareModal();
      } else {
        this.showMessage(data.message, "error");
      }
    } catch (error) {
      console.error("Upload error:", error);
      this.showMessage("Upload failed", "error");
    }
  }

  async loadMyFiles() {
    try {
      const response = await fetch("/api/files/my-files", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: this.sessionId }),
      });

      const data = await response.json();

      if (data.success) {
        this.files = data.files;
        this.renderMyFiles();
      }
    } catch (error) {
      console.error("Load files error:", error);
    }
  }

  async loadSharedFiles() {
    try {
      const response = await fetch("/api/files/shared-with-me", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: this.sessionId }),
      });

      const data = await response.json();

      if (data.success) {
        this.sharedFiles = data.files;
        this.renderSharedFiles();
      }
    } catch (error) {
      console.error("Load shared files error:", error);
    }
  }

  renderMyFiles() {
    const container = document.getElementById("my-files-list");
    if (!container) return;

    if (this.files.length === 0) {
      container.innerHTML =
        '<p style="text-align: center; color: #999;">No files uploaded yet</p>';
      return;
    }

    container.innerHTML = this.files
      .map(
        (file) => `
      <div class="file-item">
        <div class="file-info">
          <div class="file-name"> ${file.filename}</div>
          <div class="file-meta">
            Size: ${this.formatFileSize(file.file_size)} | 
            Uploaded: ${new Date(file.upload_timestamp).toLocaleDateString()} |
            Shared with: ${file.shared_with.length}
          </div>
        </div>
        <div class="file-actions">
          <button class="btn-primary" onclick="app.prepareShare('${file.file_id}')">Share</button>
          <button class="btn-danger" onclick="app.deleteFile('${file.file_id}')">Delete</button>
        </div>
      </div>
    `,
      )
      .join("");
  }

  renderSharedFiles() {
    const container = document.getElementById("shared-files-list");
    if (!container) return;

    if (this.sharedFiles.length === 0) {
      container.innerHTML =
        '<p style="text-align: center; color: #999;">No files shared with you yet</p>';
      return;
    }

    container.innerHTML = this.sharedFiles
      .map(
        (file) => `
      <div class="file-item">
        <div class="file-info">
          <div class="file-name"> ${file.filename}</div>
          <div class="file-meta">
            Size: ${this.formatFileSize(file.file_size)} | 
            Owner: ${file.owner} |
            ID: ${file.file_id.substring(0, 8)}...
          </div>
        </div>
        <div class="file-actions">
          <button class="btn-primary" onclick="app.downloadFile('${file.file_id}')">Download</button>
        </div>
      </div>
    `,
      )
      .join("");
  }

  async deleteFile(fileId) {
    if (!confirm("Delete this file?")) return;

    try {
      const response = await fetch(`/api/files/delete/${fileId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: this.sessionId }),
      });

      const data = await response.json();

      if (data.success) {
        this.showMessage("✓ File deleted", "success");
        this.loadMyFiles();
      } else {
        this.showMessage(data.message, "error");
      }
    } catch (error) {
      console.error("Delete error:", error);
      this.showMessage("Delete failed", "error");
    }
  }

  // ============ SHARING ============

  prepareShare(fileId) {
    this.currentShareFileId = fileId;
    const file = this.files.find((f) => f.file_id === fileId);
    if (file) {
      this.currentEncryptionKey =
        file.encryption_key || "Key will be generated";
    }
    this.showShareModal();
  }

  async confirmShare() {
    const recipient = document.getElementById("input-share-recipient").value;
    const includeKey = document.getElementById("checkbox-include-key").checked;

    if (!recipient) {
      this.showMessage("Please select recipient", "error");
      return;
    }

    try {
      const response = await fetch("/api/files/share", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          file_id: this.currentShareFileId,
          recipient: recipient,
          include_key: includeKey,
        }),
      });

      const data = await response.json();

      if (data.success) {
        const keyText = includeKey
          ? `\n\nEncryption Key: ${data.encryption_key}`
          : "";
        this.showMessage(
          `✓ File shared with ${recipient}${keyText}`,
          "success",
        );
        this.closeShareModal();
        this.loadMyFiles();
      } else {
        this.showMessage(data.message, "error");
      }
    } catch (error) {
      console.error("Share error:", error);
      this.showMessage("Share failed", "error");
    }
  }

  async downloadFile(fileId) {
    const key = prompt("Enter encryption key to decrypt file:");
    if (!key) return;

    try {
      this.showMessage("Downloading and decrypting...", "info");

      const response = await fetch(`/api/files/download/${fileId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: this.sessionId,
          encryption_key: key,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = this.sharedFiles.find(
          (f) => f.file_id === fileId,
        ).filename;
        a.click();
        this.showMessage("✓ File downloaded", "success");
      } else {
        const error = await response.json();
        this.showMessage(error.message || "Download failed", "error");
      }
    } catch (error) {
      console.error("Download error:", error);
      this.showMessage("Download failed", "error");
    }
  }

  showShareModal() {
    const modal = document.getElementById("share-modal");
    const userSelect = document.getElementById("input-share-recipient");

    // Populate users
    fetch("/api/auth/users")
      .then((r) => r.json())
      .then((data) => {
        userSelect.innerHTML = data.users
          .filter((u) => u.username !== this.currentUser.username)
          .map(
            (u) =>
              `<option value="${u.username}">${u.username} (${u.email})</option>`,
          )
          .join("");
      });

    modal.classList.add("active");
  }

  closeShareModal() {
    document.getElementById("share-modal").classList.remove("active");
  }

  // ============ UI UTILITIES ============

  showAuthPanel() {
    document.getElementById("auth-container").style.display = "flex";
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("user-status").textContent = "Not logged in";
  }

  showDashboard() {
    document.getElementById("auth-container").style.display = "none";
    document.getElementById("dashboard").style.display = "grid";
    document.getElementById("user-status").innerHTML = `
      <span>${this.currentUser.username}</span>
      <button class="btn-secondary" id="btn-logout" style="width: auto;">Logout</button>
    `;
    document
      .getElementById("btn-logout")
      .addEventListener("click", () => this.handleLogout());
    this.switchSection("upload");
    this.loadSystemStats();
  }

  switchSection(sectionName) {
    document
      .querySelectorAll(".section")
      .forEach((s) => s.classList.remove("active"));
    document
      .querySelectorAll(".sidebar button")
      .forEach((b) => b.classList.remove("active"));

    const section = document.getElementById(`section-${sectionName}`);
    if (section) {
      section.classList.add("active");
    }

    document
      .querySelector(`[data-section="${sectionName}"]`)
      ?.classList.add("active");

    if (sectionName === "stats") {
      this.loadSystemStats();
    }
  }

  async loadSystemStats() {
    try {
      const response = await fetch("/api/system/stats");
      const data = await response.json();

      if (data.success) {
        this.renderStats(data);
      }
    } catch (error) {
      console.error("Stats load error:", error);
    }
  }

  renderStats(systemStats) {
    const container = document.getElementById("stats-container");
    if (!container) return;

    const auth = systemStats.authentication || {};
    const files = systemStats.files || {};

    const cards = [
      { label: "Total Files", value: files.total_files ?? 0 },
      { label: "Users Online", value: auth.active_sessions ?? 0 },
      { label: "Downloads", value: files.total_downloads ?? 0 },
      {
        label: "Upload Speed (Plain)",
        value: `${(files.average_upload_speed_plain_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "Upload Speed (Encrypted)",
        value: `${(files.average_upload_speed_encrypted_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "Download Speed (Plain)",
        value: `${(files.average_download_speed_plain_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "Download Speed (Encrypted)",
        value: `${(files.average_download_speed_encrypted_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "File Transfer Speed",
        value: `${(files.average_file_transfer_speed_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "Encryption Speed",
        value: `${(files.average_encryption_speed_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "Encryption Time",
        value: `${(files.average_encryption_time_ms ?? 0).toFixed(2)} ms`,
      },
      {
        label: "Decryption Speed",
        value: `${(files.average_decryption_speed_mbps ?? 0).toFixed(2)} MB/s`,
      },
      {
        label: "Decryption Time",
        value: `${(files.average_decryption_time_ms ?? 0).toFixed(2)} ms`,
      },
      {
        label: "Plain Size (Total)",
        value: this.formatFileSize(files.total_uploaded_size_bytes ?? 0),
      },
      {
        label: "Encrypted Size (Total)",
        value: this.formatFileSize(files.total_encrypted_size_bytes ?? 0),
      },
      {
        label: "Encryption Size Overhead",
        value: `${(files.average_size_overhead_percent ?? 0).toFixed(2)}%`,
      },
    ];

    container.innerHTML = cards
      .map(
        (card) => `
      <div class="stat-card">
        <div class="stat-value">${card.value}</div>
        <div class="stat-label">${card.label}</div>
      </div>
    `,
      )
      .join("");
  }

  showMessage(message, type) {
    const container = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = `message ${type}`;
    div.textContent = message;
    container.appendChild(div);

    setTimeout(() => div.remove(), 5000);
  }

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(2) + " " + sizes[i];
  }
}

// Initialize on page load
let app;
document.addEventListener("DOMContentLoaded", () => {
  app = new SecureFileTransferClient();
});
