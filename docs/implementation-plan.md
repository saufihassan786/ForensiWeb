# ForensiWeb — Phased Implementation Plan & Execution Framework

**Document:** `implementation-plan.md`  
**Status:** Approved Specification  
**Version:** 1.0  
**Project:** ForensiWeb  
**Authority:** Project Execution & Phased Milestone Planning  

---

## 1. Executive Summary

ForensiWeb is built using a strict, dependency-oriented, staged development lifecycle. To guarantee academic validity, digital forensic integrity, and architectural clean separation, the project enforces the following golden rule:

> **BUILD ONE PHASE AT A TIME.**  
> **BUILD ONE FEATURE AT A TIME.**  
> **VERIFY BEFORE PROCEEDING.**

This document outlines the macro-level implementation phases, architectural dependencies, phase-gate verification protocols, and governance standards. The granular, task-by-task tracking is maintained in [`docs/task.md`](task.md).

---

## 2. Development Pipeline & Dependency Rationale

The implementation pipeline follows a strict dependency graph designed to eliminate unstable assumptions and circular dependencies:

```text
[PHASE 01: Project Foundation]
              ↓
[PHASE 02: Backend & Database Foundation]
              ↓
[PHASE 03: Frontend Design System & Shell]
              ↓
[PHASE 04: Controlled Vulnerable Application]
              ↓
[PHASE 05: Isolated Laboratory Environment]
              ↓
[PHASE 06: Evidence Collection]
              ↓
[PHASE 07: Forensic Processing Engine]
              ↓
[PHASE 08: Common Event Model / Event Normalization]
              ↓
[PHASE 09: Detection Engine]
              ↓
[PHASE 10: Multi-Source Correlation Engine]
              ↓
[PHASE 11: Timeline Reconstruction & Attack Graph]
              ↓
[PHASE 12: Investigation Workspace]
              ↓
[PHASE 13: Dashboard & Forensic Analytics]
              ↓
[PHASE 14: Forensic Reporting Engine]
              ↓
[PHASE 15: Mitigation & Verification]
              ↓
[PHASE 16: End-to-End System Integration]
              ↓
[PHASE 17: Testing, Reliability & Stress Testing]
              ↓
[PHASE 18: Security Hardening & Isolation Review]
              ↓
[PHASE 19: Performance, Polish & UX Refinement]
              ↓
[PHASE 20: Final Academic Validation & Demonstration]
```

### Why This Order Exists:
1. **Foundation First:** Configuration, containerization, and repository structures must exist before code is written.
2. **Data & Storage Precedes Processing:** Parsers cannot parse without raw evidence; raw evidence cannot be collected without a reproducible laboratory scenario; laboratory scenarios cannot exist without the vulnerable application.
3. **Normalization Precedes Detection:** Detection rules must evaluate structured, normalized events (CEM) rather than raw, heterogeneous log formats.
4. **Correlation Precedes Timeline & Investigation:** Timeline engines and investigator workspaces depend on correlated events and explainable link graphs.
5. **Mitigation Requires a Working Baseline:** Security mitigations can only be proven effective when tested against a fully functioning, observed baseline attack scenario.

---

## 3. The 20 Implementation Phases

| Phase | Title | Core Objective | Key Deliverables |
|---|---|---|---|
| **01** | **Project Foundation** | Establish repository, documentation, environment, git, test runners, and Docker baseline. | Directory layout, documentation catalog, `.env.example`, `.gitignore`, pytest config. |
| **02** | **Backend & Database Foundation** | Initialize FastAPI backend, database connection, Alembic migrations, and core config. | FastAPI app, PostgreSQL schema, DB session manager, health check route. |
| **03** | **Frontend Foundation & Shell** | Establish React/TypeScript app, design tokens, layout shell, and navigation. | Vite setup, Vanilla CSS design tokens, sidebar, topbar, responsive layout. |
| **04** | **Controlled Vulnerable App** | Build the controlled Flask target with intentional LFI, log poisoning, and misconfig flaws. | Vulnerable web app, LFI endpoint, log write target, vulnerable script. |
| **05** | **Isolated Laboratory** | Establish isolated Docker network, container topology, and deterministic scenario runner. | `docker-compose.yml`, `forensiweb-lab-net`, scenario execution scripts. |
| **06** | **Evidence Collection** | Implement evidence extraction, SHA-256 integrity hashing, and storage architecture. | Artifact collectors, manifest generator, read-only storage manager. |
| **07** | **Forensic Processing Engine** | Build structured parsers for web server logs, application errors, and system audit logs. | Nginx/Apache log parser, Flask parser, auditd log parser. |
| **08** | **Common Event Model** | Implement normalization pipeline converting raw log events to the standard CEM schema. | Normalization schemas, Pydantic validators, event persistence layer. |
| **09** | **Detection Engine** | Implement deterministic, explainable detection rules for each attack stage. | Rule registry, LFI rule, log poisoning rule, RCE rule, priv-esc rule. |
| **10** | **Correlation Engine** | Build multi-source correlation linking events across temporal, network, and process boundaries.| Temporal window linker, process lineage tracker, correlation graph builder. |
| **11** | **Timeline Reconstruction** | Construct chronological attack timelines and interactive attack chain graphs. | Microsecond sorter, stage mapper, timeline generator, attack graph. |
| **12** | **Investigation Workspace** | Interactive investigator UI for case management, event inspection, and evidence drill-down. | Case view, event inspector, evidence viewer, finding note-taker. |
| **13** | **Dashboard & Analytics** | Executive and technical summary views with metrics, severity distributions, and event trends. | Case dashboard, Apache ECharts integrations, KPI metric cards. |
| **14** | **Forensic Reporting Engine** | Automated generation of comprehensive, evidence-backed PDF and Markdown reports. | Report generator, template engine, evidence citation manager. |
| **15** | **Mitigation & Verification** | Implement security fixes and demonstrate before/after attack neutralization. | Mitigated code patch, secure configuration, verification comparison runner. |
| **16** | **End-to-End Integration** | Connect all components into an automated, seamless end-to-end pipeline. | Orchestration workflow, end-to-end execution script, scenario automation. |
| **17** | **Testing & Reliability** | Comprehensive unit, integration, regression, and malformed-input test suites. | Pytest suite, corrupt evidence tests, scenario boundary verification. |
| **18** | **Security Hardening** | Security audits, input sanitization review, container isolation checks, secret scan. | Non-root container check, XSS review in log display, network egress block check. |
| **19** | **Performance & UX Polish** | Query optimization, log streaming pagination, UI animations, accessibility verification. | DB index tuning, lazy loading, responsive layout polish. |
| **20** | **Academic Validation** | Final academic demonstration, reproducibility audit, artifact verification, evaluation report.| Complete test run, reproducibility paper bundle, final artifact package. |

---

## 4. Phase-Gate Verification Model

A phase is considered complete and eligible for sign-off only when it passes through the strict Phase-Gate protocol:

```text
+-------------------------------------------------------------+
|                      PHASE-GATE PROTOCOL                    |
+-------------------------------------------------------------+
| 1. Functional Verification:                                 |
|    - Every feature in the phase checklist is implemented.   |
|    - All acceptance criteria are strictly satisfied.         |
|                                                             |
| 2. Quality & Automated Tests:                               |
|    - 100% of unit and integration tests for the phase pass. |
|    - No regression in earlier phases.                       |
|                                                             |
| 3. Security & Isolation:                                    |
|    - Zero secrets committed.                                |
|    - Laboratory isolation boundaries maintained.            |
|                                                             |
| 4. Forensic Correctness:                                    |
|    - Cryptographic evidence hashes remain untampered.       |
|    - Line/byte trace references are valid.                  |
|                                                             |
| 5. Documentation Synchronization:                           |
|    - task.md updated with completed statuses.               |
|    - Relevant architecture/design/API docs synchronized.    |
+-------------------------------------------------------------+
```

---

## 5. Standard Feature Implementation Protocol

Every developer and AI coding agent must execute each individual feature using the 13-step lifecycle:

1. **Step 1 — Understand Requirement:** Consult `prd.md`, `architecture.md`, `rules.md`, and `task.md`.
2. **Step 2 — Inspect Existing Code:** Examine relevant directory trees and existing interfaces.
3. **Step 3 — Scope Boundary:** Identify exactly what files must be added or altered; do not expand scope.
4. **Step 4 — Define Acceptance Criteria:** Ensure testable, observable criteria.
5. **Step 5 — Plan Implementation:** Determine interfaces, data structures, and test strategies.
6. **Step 6 — Implement Code:** Minimal, focused, clean implementation.
7. **Step 7 — Write Tests:** Cover happy paths, edge cases, invalid input, and failure paths.
8. **Step 8 — Run Tests:** Execute targeted test runners; verify zero failures.
9. **Step 9 — Code Review:** Inspect correctness, error handling, security, and maintainability.
10. **Step 10 — Resolve Defects:** Fix issues before declaring completion.
11. **Step 11 — Verify Criteria:** Confirm each acceptance criterion individually.
12. **Step 12 — Document:** Update relevant documentation and task progress.
13. **Step 13 — Complete & Stop:** Mark feature completed in `task.md`, report summary, and await next prompt.

---

## 6. Relationship with `task.md`

- **`implementation-plan.md`** provides the architectural rationale, macro milestones, and phase-gate framework.
- **`task.md`** is the active execution ledger containing granular checklists, real-time status blocks, and atomic feature IDs (`PHASE-XX-FYY`).
- If an architectural adjustment or implementation reordering is approved, both documents must be updated in sync.
