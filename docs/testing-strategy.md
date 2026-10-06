# ForensiWeb — Comprehensive Testing & Quality Assurance Strategy

**Document:** `testing-strategy.md`  
**Status:** Approved Specification  
**Version:** 1.0  
**Project:** ForensiWeb  
**Authority:** Quality Assurance, Test Architecture & Forensic Validation  

---

## 1. Executive Summary

ForensiWeb is an academic cybersecurity and digital forensics platform. In academic research and forensic science, the validity of results depends entirely on **reproducibility, correctness, and verifiable integrity**.

This document outlines the testing strategy, test pyramid, tooling, quality gates, and automated test execution policies across all components of ForensiWeb.

---

## 2. Testing Philosophy & Guiding Principles

1. **Evidence Integrity is Paramount:** Tests must verify that raw evidence is never mutated, that hashes are validated upon ingestion, and that tampering is immediately detected.
2. **Deterministic & Explainable:** Tests must confirm that detection rules and correlation heuristics produce deterministic, reproducible results without flaky behavior.
3. **Defense-in-Depth Testing:** Testing spans multiple tiers: isolated unit tests, multi-service integration tests, containerized lab scenario tests, and end-to-end user journey validations.
4. **Negative & Adversarial Testing:** Robust testing must include malformed log entries, corrupt timestamps, truncated files, out-of-order events, and synthetic evasion attempts.
5. **Zero Broken Builds:** Code must not be committed or marked complete if tests fail.

---

## 3. The Testing Pyramid

```text
               / \
              /   \
             / E2E \           <- Full Scenario & Workflow (tests/e2e)
            /-------\
           /   Lab   \         <- Docker Lab & Reproducibility (lab/tests)
          /-----------\
         / Integration \       <- Cross-component & Database (tests/integration)
        /---------------\
       /      Unit       \     <- Parsers, Rules, Schemas, Utils (apps/*/tests, packages/*/tests)
      /-------------------\
```

### 3.1 Test Levels & Responsibilities

| Test Tier | Scope & Focus | Typical Execution Time | Primary Tools |
|---|---|---|---|
| **Unit Tests** | Individual functions, schemas, parsers, normalizers, detection rules, utilities. | < 5 seconds | `pytest`, Python `unittest`, `vitest` |
| **Integration Tests** | API routes with database transactions, evidence ingestion pipeline, parser-to-normalizer flow. | 5 – 30 seconds | `pytest`, SQLite in-memory / test PostgreSQL |
| **Laboratory Tests** | Isolated container spin-up, scenario execution, log generation, container capability validation. | 30 – 90 seconds | Docker Compose, shell harnesses, `pytest` |
| **End-to-End Tests** | Complete forensic lifecycle: Lab attack -> Evidence collection -> Ingestion -> Correlation -> Report generation. | 1 – 3 minutes | Automated scenario runner, API integration |
| **Regression Tests** | Verification against known fixed defects, schema drift, and edge-case log formats. | < 15 seconds | `tests/regression/` test suite |

---

## 4. Test Categories & Methodology

### 4.1 Unit Testing
- **Evidence Parsers:** Test web log parsers (Combined Log Format, Nginx access logs), application error logs, Linux auditd logs, and process snapshots with diverse valid and malformed fixtures.
- **Normalization Engine:** Verify conversion of heterogeneous raw records into the Common Event Model (CEM). Validate Pydantic model serialization, timestamp normalization to UTC ISO-8601, and field extraction.
- **Detection Rules:** Unit test each detection rule in `packages/detection-engine/rules/` with positive matches (simulated attack events) and negative matches (benign background traffic). Verify zero false positives on standard traffic.
- **Correlation Engine:** Test temporal clustering, process tree reconstruction (PPID -> PID), and IP/actor correlation using synthesized event streams.
- **Integrity Utilities:** Verify SHA-256 calculation, manifest generation, and tampering detection routines.

### 4.2 Integration Testing
- **API Endpoints:** Test FastAPI routers using `TestClient` (HTTP GET/POST/PUT/DELETE), verifying input validation, status codes, response schemas, and authentication headers.
- **Database Layer:** Verify SQLAlchemy models, relationships (Case -> Evidence -> Events -> Detections -> Findings), and migration scripts using an isolated test database.
- **Evidence Repository:** Test writing to `data/evidence/original/` with read-only flag enforcement, working copy cloning, and derived output storage.

### 4.3 Laboratory & Reproducibility Testing
- **Isolation Verification:** Automated tests to ensure lab container network has no internet egress and cannot access host network interfaces.
- **Container Privileges:** Verify lab containers run with dropped capabilities (`cap_drop: ALL`) and without `--privileged` flag.
- **Scenario Reproducibility:** Execute the automated attack script multiple times from a clean state and assert that identical event sequences, HTTP log entries, and artifact hashes are generated.

### 4.4 Negative & Resilience Testing
- **Malformed Evidence:** Empty log files, binary garbage injected into text logs, multi-megabyte single lines, truncated records, out-of-order timestamps.
- **Tampered Evidence:** Artificially modifying 1 byte of an ingested original log file; verifying that downstream analysis immediately aborts with an `EvidenceIntegrityError`.
- **Clock Drift:** Injecting simulated clock skew between web server and auditd logs; verifying that timeline reconstruction handles skew gracefully within configured drift tolerance.

---

## 5. Directory Organization for Tests

The repository maintains tests at both the root level (for cross-cutting integration/E2E) and within individual apps/packages:

```text
forensiweb/
├── tests/
│   ├── integration/          # Multi-component & database integration tests
│   ├── e2e/                  # Full pipeline end-to-end scenario tests
│   ├── fixtures/             # Reusable sample logs, synthetic events, manifests
│   ├── regression/           # Defect regression tests
│   ├── test_repository_structure.py
│   └── test_documentation_structure.py
├── apps/
│   ├── frontend/
│   │   └── src/**/__tests__/ # UI component and state tests
│   ├── api/
│   │   └── tests/            # API router and database service tests
│   └── vulnerable-web-app/
│       └── tests/            # Vulnerable target route and scenario tests
└── packages/
    ├── forensic-engine/
    │   └── tests/            # Parsers, normalization, and timeline tests
    ├── detection-engine/
    │   └── tests/            # Rule unit tests and evaluator tests
    └── report-engine/
        └── tests/            # Report synthesis and template tests
```

---

## 6. Testing Tooling & Conventions

### 6.1 Tooling Stack
- **Python Test Runner:** `pytest` (version 8+)
- **Async Test Support:** `pytest-asyncio`
- **Mocking:** `pytest-mock` / standard library `unittest.mock`
- **Coverage Tool:** `pytest-cov` (target coverage $\ge 85\%$ for core parsing and detection packages)
- **Frontend Testing:** `vitest` with `@testing-library/react` and `jsdom`

### 6.2 Test Naming & Structure Conventions
- Test files must follow the pattern `test_<component_name>.py`.
- Test functions must use descriptive names following the pattern:
  `test_<functionality>_<condition>_<expected_result>()`
  - *Example:* `test_web_log_parser_given_poisoned_user_agent_extracts_payload()`
  - *Example:* `test_ingest_evidence_when_checksum_mismatch_raises_integrity_error()`
- Tests must adhere to the **AAA pattern (Arrange, Act, Assert)**.

---

## 7. Quality Gates & Definition of Done for Testing

Before any feature or phase is declared complete:
1. **All Tests Pass:** `pytest` runs cleanly with 0 errors and 0 failures.
2. **Coverage Maintained:** Code coverage does not degrade.
3. **No Flaky Tests:** Tests execute deterministically without depending on external network state or system timing race conditions.
4. **Fast Feedback:** Unit test suite must execute in under 10 seconds locally.
5. **No Secret Commits:** Tests must not use or output live credentials or private keys.
