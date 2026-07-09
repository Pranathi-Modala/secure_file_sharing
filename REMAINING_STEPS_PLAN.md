# Remaining Steps Plan (Weeks 4-12)

## Current Status Snapshot

Based on the current codebase and documentation, the project has already covered much of Weeks 1-3 (proposal, baseline implementation, and basic metrics/logging). The remaining work is to complete, validate, and document the full research scope.

## Priority Gaps To Close First

1. Missing encryption module file

- Gap: Routes import `modules.encryption`, but `app/modules/encryption.py` is not present in this workspace.
- Impact: Upload/download encryption path will break at runtime.
- Action: Create `app/modules/encryption.py` with key generation, encrypt/decrypt methods, and timing metrics.
- Output: Working `encryption_engine` object used by routes.

2. Secure communication not yet implemented end-to-end

- Gap: Proposal requires secure communication (TLS/SSL), but no deployment TLS configuration is documented.
- Action: Add HTTPS for testing (self-signed cert for local), then document production TLS setup (reverse proxy + cert management).
- Output: Encrypted transport channel for all API traffic.

3. Authentication model is session-based only

- Gap: Proposal tool stack mentions JWT, but current implementation uses in-memory sessions.
- Action: Decide one of two paths and document justification:
  - Keep session model for academic prototype and document scope limitation, or
  - Add JWT access tokens + refresh strategy.
- Output: Aligned authentication design with proposal claims.

4. Quantitative evaluation package needs formalization

- Gap: Metrics exist in logs, but experimental protocol and final analysis scripts need to be formalized.
- Action: Define controlled experiments, automate repeated runs, and generate plots/tables.
- Output: Defensible quantitative results section.

## Week-by-Week Remaining Work

## Week 4 Implementation Update (Completed)

- Week 4 design deliverables have now been produced in:
  - `WEEK4_SYSTEM_DESIGN_SPEC.md`
  - `WEEKLY_SELF_TEST_GUIDE.md`
- Artifacts include architecture diagram, route-to-component mapping, sequence flows, trust boundaries, and a repeatable weekly self-test procedure.
- Week 4 status: COMPLETE.

## Week 4: System Design Finalization

What remains:

- Final architecture diagram and component interactions.
- Data flow for upload/share/download with security controls.

How it will be done:

- Freeze module boundaries: auth, encryption, file manager, logging, transport.
- Draw sequence diagrams for:
  - Upload + encrypt
  - Share + key handling
  - Download + access verification + decrypt
- Document trust boundaries and attack surface.

Expected output:

- Final design specification document.
- Architecture and sequence diagrams.

Completion check:

- All routes mapped to architecture components.
- Security controls are explicitly mapped per step.

## Week 5: Data and Environment Hardening

What remains:

- Persistent storage decision and schema (if required by course rubric).
- Environment reproducibility and configuration cleanup.

How it will be done:

- Choose storage mode:
  - Option A: Keep in-memory for prototype and justify limitations.
  - Option B: Add SQLite for users/files/share metadata/log references.
- Move secrets and config into environment variables.
- Add startup validation checks for required paths/config.

Expected output:

- Database/schema document (or scope justification if not using DB).
- Clean environment configuration guide.

Completion check:

- App starts with documented env settings.
- No hardcoded sensitive values in code.

## Week 6: Authentication Completion

What remains:

- Complete access control and security strengthening for auth.

How it will be done:

- Add account lockout/backoff thresholds.
- Add password policy and validation messages.
- If JWT path selected: implement token issue/verify/refresh and route guards.
- Add auth test cases for valid, invalid, and abuse scenarios.

Expected output:

- Completed authentication module with test evidence.

Completion check:

- Unauthorized access attempts are consistently blocked.
- Auth success/failure metrics are captured in logs.

## Week 7: Encryption Module Completion

What remains:

- Stabilize encryption implementation and key-handling controls.

How it will be done:

- Implement/restore `encryption.py` with:
  - Strong key generation
  - Encrypt/decrypt APIs
  - Error handling for invalid keys/corrupt ciphertext
  - Timing metrics (ms)
- Add integrity checks and negative test cases.
- Define key lifecycle policy for the prototype (generation, delivery, non-storage/limited storage strategy).

Expected output:

- Production-ready project encryption module for the study scope.

Completion check:

- Round-trip encryption/decryption passes for test files of varying sizes.
- Wrong-key and tampered-data cases fail safely.

## Week 8: Secure Transfer Implementation

What remains:

- End-to-end secure transport and secure file transmission validation.

How it will be done:

- Enable HTTPS in controlled test environment.
- Validate upload/download behavior over secure channel.
- Add request size/rate guardrails and improved error handling.

Expected output:

- Transfer module validated under secure transport.

Completion check:

- All core transfer routes work over HTTPS.
- Transfer metrics (time, throughput) collected under secure transport.

## Week 9: System Integration

What remains:

- Integrate all modules and remove inconsistencies between docs and code.

How it will be done:

- Run integration checklist across auth, file sharing, encryption, logging, and stats endpoints.
- Resolve doc/code mismatches (module names, dependencies, workflow).
- Freeze API contract and UI flow.

Expected output:

- Integrated and stable system build.

Completion check:

- Full workflow demo succeeds:
  - Login -> upload -> share -> recipient download -> decrypt.

## Week 10: Testing and Evaluation

What remains:

- Formal test campaign and security/performance evaluation.

How it will be done:

- Functional tests: authentication, sharing permissions, upload/download correctness.
- Security tests: unauthorized access, invalid key, tampering attempts.
- Performance tests: encryption time, decryption time, transfer throughput by file size.
- Record all results in a structured test report.

Expected output:

- Test and evaluation report with pass/fail matrix.

Completion check:

- Results are repeatable and mapped to research questions.

## Week 11: Data Analysis and Documentation

What remains:

- Analyze collected metrics and finalize report-ready figures.

How it will be done:

- Parse logs into analysis tables.
- Compute descriptive stats (mean, median, std dev, min/max).
- Create charts for:
  - Encryption/decryption time vs file size
  - Transfer efficiency vs file size
  - Authentication success/failure rates
- Write interpretation aligned to research objectives/questions.

Expected output:

- Analysis report section with charts and interpretation.

Completion check:

- Every research question is answered using evidence from data.

## Week 12: Final Report and Presentation

What remains:

- Final thesis report, polishing, and defense/demo assets.

How it will be done:

- Consolidate methodology, implementation, testing, and analysis chapters.
- Add limitations and future work section.
- Prepare presentation slides and live demo script.

Expected output:

- Final submission package (report + slides + runnable demo).

Completion check:

- Submission package is complete, coherent, and reproducible.

## Execution Method (How Work Will Be Carried Out)

1. Build in short iterations

- Implement one module improvement at a time.
- Validate immediately with targeted tests.

2. Measure everything needed for the study

- For each upload/download: capture size, encryption/decryption time, transfer time, throughput.
- For auth: capture login success/failure and failed-attempt behavior.

3. Keep evidence organized

- Store logs, test scripts, generated plots, and report drafts in consistent folders.
- Version documents after each week milestone.

4. Trace work to research questions

- After each week, map outputs to objective/question coverage.
- Avoid adding features that do not support the proposal outcomes.

## Remaining Deliverables Checklist

- [ ] Encryption module file restored/validated (`app/modules/encryption.py`)
- [ ] Secure communication configuration documented and tested
- [ ] Authentication model finalized (session or JWT) and justified
- [ ] System architecture/design package finalized
- [ ] Integration test evidence captured
- [ ] Quantitative performance dataset finalized
- [ ] Analysis plots/tables created
- [ ] Final report compiled
- [ ] Presentation/demo package prepared

## Immediate Next Actions (Next 3 Working Sessions)

Session 1:

- Restore/implement encryption module and verify upload/download flow.
- Fix any import/runtime errors.

Session 2:

- Formalize experimental protocol and add repeatable test scripts.
- Start collecting baseline metrics for multiple file sizes.

Session 3:

- Enable secure transport test setup (HTTPS) and re-run core metrics.
- Draft Week 10 test report structure.
