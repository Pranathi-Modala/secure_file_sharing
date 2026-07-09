# Weekly Self-Test Guide

## Purpose

Use this guide to test system functionality yourself at the end of each project week.

## Preconditions

1. Python virtual environment exists in project root
2. Dependencies installed from requirements.txt
3. Project started from the project root directory

## Start the System

Windows PowerShell:

```powershell
Set-Location "c:\Users\ADMIN\Desktop\NC Institute\FILE SHARING\secure_file_transfer"
.\venv\Scripts\python.exe run.py
```

Expected startup result:

- Flask server starts without import/runtime errors
- App reachable at http://127.0.0.1:5000

If startup fails:

- Read traceback in terminal
- Fix missing module or dependency before continuing tests

## Core Manual Test Flow (Run Every Week)

1. Authentication smoke test

- Login with alice/alice123
- Login with bob/bob123
- Try one invalid login
- Expected: valid logins succeed, invalid login fails

2. Upload and encryption smoke test

- Login as alice
- Upload a small sample file
- Expected: upload succeeds, file appears in My Files, encryption key is returned

3. Share access control smoke test

- Share Alice file with Bob
- Expected: Bob sees file under Shared with Me

4. Download and decryption smoke test

- Login as bob
- Download shared file with correct key
- Expected: file downloads and opens correctly
- Retry with wrong key
- Expected: decryption denied

5. Authorization smoke test

- Attempt delete/unshare by non-owner
- Expected: permission denied

6. Stats and logging smoke test

- Open system stats view in UI
- Check logs/system.log and logs/logs.csv updated
- Expected: operations recorded with timestamps and metrics

## Week-Specific Test Add-Ons

### Week 4 (Design Finalization)

Goal:

- Validate architecture documentation matches actual implementation.

Do:

1. Confirm each route exists and maps to intended module.
2. Execute one full flow: login -> upload -> share -> download.
3. Compare observed behavior with Week 4 sequence diagrams.

Pass criteria:

- Flow behavior matches documented sequence.
- No missing route/module mismatch.

### Week 5 (Environment and Data Hardening)

Do:

1. Start app using documented environment settings.
2. Confirm no hardcoded secret changes broke startup.
3. If database added, verify tables and basic reads/writes.

Pass criteria:

- Reproducible startup from clean shell.
- Data model behavior is stable.

### Week 6 (Authentication Strengthening)

Do:

1. Run repeated failed logins to validate lockout/backoff.
2. Validate new password policy on register.
3. Validate session/JWT guard behavior on protected routes.

Pass criteria:

- Abuse attempts blocked as designed.
- Protected endpoints reject unauthorized requests.

### Week 7 (Encryption Completion)

Do:

1. Encrypt/decrypt files at multiple sizes.
2. Validate wrong-key failure behavior.
3. Validate tampered ciphertext failure behavior.

Pass criteria:

- Correct-key decrypt succeeds reliably.
- Wrong-key/tampered data fails safely.

### Week 8 (Secure Transfer)

Do:

1. Run tests over HTTPS endpoint.
2. Upload/download across small and larger files.
3. Confirm secure channel certificate handling in test setup.

Pass criteria:

- All critical routes work over HTTPS.
- No plaintext transport for target environment.

### Week 9 (Integration)

Do:

1. Run complete end-to-end scenario with two users.
2. Validate all route interactions and stats aggregation.

Pass criteria:

- End-to-end scenario completes without manual fixes.

### Week 10 (Formal Testing)

Do:

1. Execute structured functional/security/performance test set.
2. Save outputs as evidence.

Pass criteria:

- Test report complete with pass/fail matrix.

### Week 11 (Analysis)

Do:

1. Parse logs to tables.
2. Generate required charts.

Pass criteria:

- Metrics and charts answer research questions.

### Week 12 (Final Submission)

Do:

1. Run full demo script exactly as presentation flow.
2. Verify final report references real metrics and test evidence.

Pass criteria:

- Demo and report are consistent and reproducible.

## Quick Test Evidence Template

Record this after each week:

```text
Week:
Date:
Build/commit reference:
Server start: PASS/FAIL
Auth smoke test: PASS/FAIL
Upload-encrypt test: PASS/FAIL
Share test: PASS/FAIL
Download-decrypt test: PASS/FAIL
Authorization test: PASS/FAIL
Logs/stats test: PASS/FAIL
Issues found:
Fixes applied:
Next actions:
```

## Current Known Blockers

- If startup traceback references missing modules, resolve that first.
- If encryption-related tests fail, validate app/modules/encryption.py is present and loaded.
