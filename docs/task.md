# ForensiWeb — Project Task & Phased Implementation Plan

**Project:** ForensiWeb  
**Document:** `task.md`  
**Version:** 1.0  
**Status:** Active Development Plan  
**Purpose:** Development execution and task-management source of truth

---

## 1. Document Purpose

This document defines **HOW, WHEN, and IN WHAT ORDER** ForensiWeb is to be built.

ForensiWeb is an academic cybersecurity and digital-forensics platform designed to reproduce a controlled web-application attack scenario, generate and preserve forensic artifacts, process and normalize evidence, detect and correlate activity, reconstruct an attack timeline, produce evidence-backed findings, and demonstrate mitigation and verification.

This document does **not** replace the project's other source-of-truth documents.

| Document | Responsibility |
|---|---|
| `prd.md` | Defines **what** ForensiWeb is, **why** it exists, target users, goals, scope, and product requirements |
| `architecture.md` | Defines **how** the system is technically structured, including technology choices, components, interfaces, data architecture, and project structure |
| `design.md` | Defines UI/UX behavior, visual identity, design tokens, layouts, and reusable interface patterns |
| `rules.md` | Defines mandatory rules and constraints for AI coding agents and human developers |
| `task.md` | Defines **how + when + in what order** the approved system is implemented, tested, reviewed, and completed |

### Development principle

`task.md` converts approved product and technical requirements into an executable roadmap.

It must not silently introduce product requirements, architectural decisions, visual specifications, or technology choices that belong in another source-of-truth document.

When an implementation question cannot be answered from `task.md`, the developer or AI coding agent must consult the relevant source document before making a decision.

---

# 2. Core Development Principle

## 2.1 One Phase at a Time

ForensiWeb must be developed incrementally.

```text
Phase
  ↓
Feature
  ↓
Implementation
  ↓
Testing
  ↓
Verification
  ↓
Documentation
  ↓
Feature Complete
  ↓
Phase Review
  ↓
Next Phase
```

The project must **not** be developed using a big-bang approach.

An AI coding agent must never interpret this document as permission to implement all phases in a single request.

Only the currently active phase may be implemented unless an explicit dependency investigation requires inspecting another phase.

## 2.2 One Feature at a Time

Within a phase, implementation proceeds feature-by-feature.

```text
Understand
   ↓
Inspect Dependencies
   ↓
Acceptance Criteria
   ↓
Implement
   ↓
Test
   ↓
Review
   ↓
Fix
   ↓
Verify
   ↓
Document
   ↓
Complete
```

The normal state should be:

```text
ONE ACTIVE PHASE
        +
ONE ACTIVE FEATURE
```

Parallel work is permitted only where the architecture and dependency graph explicitly allow it and where doing so does not obscure ownership, testing, or completion status.

## 2.3 No Big-Bang Development

The following behavior is prohibited:

- implementing multiple unapproved phases simultaneously;
- generating the entire backend, frontend, laboratory, and forensic engine in one operation;
- creating placeholder implementations merely to claim feature completion;
- marking features complete before their acceptance criteria are verified;
- skipping tests because a feature appears visually complete;
- proceeding around a blocking defect without documenting and resolving it;
- changing architecture simply because implementation is inconvenient;
- adding unrelated functionality during a feature implementation.

---

# 3. Source-of-Truth Rules

## 3.1 Document Authority

The documents have different responsibilities.

```text
PRD
 ↓
Product Requirements

Architecture
 ↓
Technical Structure

Design
 ↓
User Experience

Rules
 ↓
Development Constraints

Task
 ↓
Execution Order
```

### Conflict resolution

When documents appear to conflict:

1. Stop implementation of the affected feature.
2. Identify the exact conflict.
3. Determine which document owns the decision.
4. Do not silently override either document.
5. Update the appropriate source-of-truth document if a requirement has legitimately changed.
6. Update `task.md` when the implementation order or affected tasks changes.
7. Record the change when project change tracking requires it.
8. Resume implementation only after the conflict is resolved.

`task.md` must never be used to silently override `prd.md`, `architecture.md`, `design.md`, or `rules.md`.

---

# 4. Project Development Pipeline

The complete implementation follows this dependency-oriented pipeline:

```text
Project Foundation
        ↓
Backend & Database
        ↓
Frontend Design System & Application Shell
        ↓
Controlled Vulnerable Application
        ↓
Isolated Laboratory
        ↓
Evidence Collection
        ↓
Forensic Processing
        ↓
Event Normalization
        ↓
Detection
        ↓
Correlation
        ↓
Timeline & Attack Chain
        ↓
Investigation Workspace
        ↓
Dashboard & Analytics
        ↓
Reporting
        ↓
Mitigation & Verification
        ↓
End-to-End Integration
        ↓
Testing & Reliability
        ↓
Security Hardening
        ↓
Performance & UX
        ↓
Final Academic Validation
```

## 4.1 Why This Order Exists

The ordering minimizes unstable dependencies.

For example:

- forensic processing requires evidence;
- evidence requires a reproducible laboratory and collection mechanism;
- detection requires normalized events;
- correlation requires reliable events and detections;
- investigation requires correlation and evidence traceability;
- reporting requires investigation data;
- mitigation verification requires a reproducible scenario;
- end-to-end testing requires the major system components to exist;
- hardening should be performed against an integrated system rather than isolated assumptions.

Later phases may inspect earlier components, but they must not prematurely implement dependent functionality.

---

# 5. Phase Status Model

## 5.1 Phase Statuses

| Status | Meaning |
|---|---|
| `LOCKED` | Phase is not yet eligible to begin |
| `READY` | Dependencies are complete and phase may begin |
| `ACTIVE` | Phase is currently being implemented |
| `REVIEW` | Phase implementation is complete and undergoing phase-level verification |
| `BLOCKED` | Phase cannot continue because of an unresolved dependency or defect |
| `COMPLETED` | All required features and phase acceptance criteria are satisfied |

## 5.2 Feature Statuses

| Status | Meaning |
|---|---|
| `NOT_STARTED` | Feature exists in the roadmap but work has not begun |
| `PLANNED` | Feature has been analyzed and is ready for implementation |
| `IN_PROGRESS` | Implementation is currently underway |
| `TESTING` | Implementation exists and is undergoing verification |
| `BLOCKED` | Work cannot continue because of an unresolved dependency or defect |
| `NEEDS_FIX` | Testing or review identified a problem requiring correction |
| `COMPLETED` | Definition of Done and acceptance criteria are satisfied |
| `DEFERRED` | Feature is intentionally postponed with documented justification |

A feature must not move directly from `IN_PROGRESS` to `COMPLETED` without testing and verification.

---

# 6. Current Phase Tracking

The project normally has only one active phase and one active feature.

```yaml
project:
  status: completed

current_phase:
  id: PHASE-20
  name: Final Academic Validation
  status: completed

current_feature:
  id: PHASE-20-F12
  name: Final Academic Acceptance
  status: completed
```

This block is an example of the project's tracking format.

When project progress changes, the actual tracking values must be updated.

---

# 7. Standard Feature Implementation Protocol

Every feature must follow this protocol.

## STEP 1 — Understand the Requirement

Read:

- relevant `prd.md` requirements;
- relevant `architecture.md` sections;
- relevant `design.md` sections;
- relevant `rules.md` sections;
- this feature's task definition.

Do not code until the expected outcome is understood.

## STEP 2 — Inspect Existing Code and Documentation

Before creating new code:

- inspect relevant folders;
- inspect existing services;
- inspect existing components;
- inspect database models;
- inspect API routes;
- inspect tests;
- inspect configuration;
- identify reusable functionality.

Do not duplicate existing functionality.

## STEP 3 — Identify Dependencies

Determine:

- required modules;
- required database objects;
- required APIs;
- required UI components;
- required laboratory services;
- required test fixtures;
- required previous features.

If a required dependency is incomplete, do not invent a substitute without documenting the decision.

## STEP 4 — Define Acceptance Criteria

Acceptance criteria must be observable and testable.

Avoid criteria such as:

> "Feature works well."

Prefer:

> "A valid evidence object can be ingested, assigned an immutable identifier, hashed using the approved integrity mechanism, persisted with metadata, and retrieved without modification."

## STEP 5 — Create the Implementation Plan

Before coding, determine:

- files likely to change;
- interfaces involved;
- data flow;
- error paths;
- security boundaries;
- test strategy.

## STEP 6 — Implement

Implement only the current feature.

Avoid unrelated refactoring unless it is required to safely implement the feature.

## STEP 7 — Write Tests

Tests must cover appropriate:

- happy paths;
- invalid input;
- boundary conditions;
- failure paths;
- security-sensitive behavior;
- persistence behavior;
- integration behavior where applicable.

## STEP 8 — Run Tests

Run the smallest relevant test set first, followed by broader tests when appropriate.

Record and resolve failures.

## STEP 9 — Review

Review:

- correctness;
- maintainability;
- architecture;
- security;
- error handling;
- test coverage;
- evidence integrity where applicable;
- UI/UX consistency where applicable.

## STEP 10 — Fix Issues

A feature is not complete merely because the first implementation compiles or renders.

Fix identified issues before completion.

## STEP 11 — Verify

Compare implementation against every acceptance criterion.

## STEP 12 — Document

Update documentation when implementation changes:

- APIs;
- data structures;
- configuration;
- architecture;
- operational behavior;
- laboratory behavior;
- user-facing behavior.

## STEP 13 — Mark Complete

Only after the Definition of Done has been satisfied may the feature be marked `COMPLETED`.

---

# 8. Standard Phase Completion Protocol

Before moving to the next phase:

## Architecture

- [ ] Architecture remains consistent.
- [ ] Component boundaries remain intact.
- [ ] No unnecessary coupling was introduced.
- [ ] No undocumented architectural deviation exists.

## Functionality

- [ ] All required features are implemented.
- [ ] Acceptance criteria are satisfied.
- [ ] Expected error behavior is implemented.

## Testing

- [ ] Relevant unit tests pass.
- [ ] Relevant integration tests pass.
- [ ] No blocking regression exists.
- [ ] Failure paths have been tested where applicable.

## Security

- [ ] No secrets are exposed.
- [ ] Laboratory boundaries remain intact.
- [ ] Input validation is present where required.
- [ ] Security requirements from `rules.md` are satisfied.

## Documentation

- [ ] Documentation reflects actual behavior.
- [ ] API changes are documented.
- [ ] Configuration changes are documented.
- [ ] Laboratory changes are documented where applicable.

## UI/UX

- [ ] Implementation follows `design.md`.
- [ ] Loading states exist where required.
- [ ] Error states exist where required.
- [ ] Empty states exist where required.
- [ ] Responsive behavior is verified where applicable.
- [ ] Accessibility requirements are addressed.

## Phase Review

- [ ] All required features are `COMPLETED`.
- [ ] No unresolved blocking issue exists.
- [ ] Phase acceptance criteria are satisfied.
- [ ] Phase can be marked `COMPLETED`.

---

# 9. PHASE 01 — PROJECT FOUNDATION

**Status:** `LOCKED` until project setup begins.

## Objective

Create a clean, reproducible development foundation without implementing application functionality.

## Dependencies

- Approved PRD.
- Approved architecture.
- Approved design direction.
- Approved development rules.

## Project Tasks

- Initialize repository.
- Establish project structure defined by `architecture.md`.
- Establish documentation structure.
- Configure environment handling.
- Configure source control.
- Configure testing foundation.
- Configure container foundation.
- Establish development scripts.
- Establish baseline CI checks where required.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-01-F01 | Repository Structure | 1 |
| PHASE-01-F02 | Documentation Structure | 2 |
| PHASE-01-F03 | Environment Configuration | 3 |
| PHASE-01-F04 | Git Hygiene and Ignore Rules | 4 |
| PHASE-01-F05 | Development Tooling | 5 |
| PHASE-01-F06 | Test Foundation | 6 |
| PHASE-01-F07 | Docker Foundation | 7 |
| PHASE-01-F08 | Foundation Verification | 8 |

## Implementation Order

```text
F01 → F02 → F03 → F04 → F05 → F06 → F07 → F08
```

## Technical Work

Establish only the infrastructure necessary for subsequent development.

Create appropriate:

- source directories;
- test directories;
- documentation directories;
- environment templates;
- local development configuration;
- container configuration;
- standard scripts.

Do not implement business functionality.

### Environment rules

Sensitive values must never be committed.

Provide `.env.example` containing variable names and safe example values only.

## Testing

Verify:

- repository initializes correctly;
- expected directories exist;
- development commands execute;
- test runner executes;
- container foundation builds;
- environment configuration fails safely when required configuration is missing.

## Validation

A new developer or AI agent must be able to inspect the repository and understand where application, test, documentation, configuration, and infrastructure code belongs.

## Acceptance Criteria

- Repository structure matches `architecture.md`.
- No secrets are committed.
- Development tooling is reproducible.
- Test infrastructure executes.
- Container foundation builds successfully.
- Documentation locations are established.
- No application feature is implemented prematurely.

## Completion Checklist

- [x] PHASE-01-F01 complete
- [x] PHASE-01-F02 complete
- [x] PHASE-01-F03 complete
- [x] PHASE-01-F04 complete
- [x] PHASE-01-F05 complete
- [x] PHASE-01-F06 complete
- [x] PHASE-01-F07 complete
- [x] PHASE-01-F08 complete
- [x] Phase tests pass
- [x] Security baseline verified
- [x] Documentation verified
- [x] Phase review complete

---

# 10. PHASE 02 — BACKEND & DATABASE FOUNDATION

## Objective

Establish the backend application and persistent data foundation required by later forensic functionality.

## Dependencies

- PHASE-01 completed.

## Project Tasks

- Initialize backend application.
- Establish API structure.
- Establish configuration management.
- Configure PostgreSQL according to `architecture.md`.
- Establish database migrations.
- Define core domain models.
- Establish API versioning.
- Establish health checks.
- Establish consistent error handling.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-02-F01 | Backend Application Bootstrap | 1 |
| PHASE-02-F02 | Configuration System | 2 |
| PHASE-02-F03 | Database Connection | 3 |
| PHASE-02-F04 | Migration Framework | 4 |
| PHASE-02-F05 | Core Data Models | 5 |
| PHASE-02-F06 | API Versioning and Routing | 6 |
| PHASE-02-F07 | Health and Readiness Checks | 7 |
| PHASE-02-F08 | Error Handling | 8 |
| PHASE-02-F09 | Backend Verification | 9 |

## Technical Work

Core domain entities should conceptually support:

- cases;
- evidence;
- events;
- detections;
- timeline entries;
- findings;
- reports;
- audit logs.

Exact fields, relationships, indexes, naming conventions, and technology-specific implementation must follow `architecture.md`.

Do not prematurely implement advanced detection or correlation logic.

## Testing

Test:

- application startup;
- database connection;
- migrations;
- model validation;
- API error responses;
- health endpoints;
- invalid configuration;
- database unavailability.

## Validation

The backend must start consistently and communicate with its database without implementing higher-level forensic workflows.

## Acceptance Criteria

- Backend starts successfully.
- Database connection works.
- Migrations are reproducible.
- Core models are represented according to architecture.
- API versioning structure exists.
- Health/readiness behavior is available.
- Errors are returned consistently.
- Tests pass.

## Completion Checklist

- [x] PHASE-02-F01 complete
- [x] PHASE-02-F02 complete
- [x] PHASE-02-F03 complete
- [x] PHASE-02-F04 complete
- [x] PHASE-02-F05 complete
- [x] PHASE-02-F06 complete
- [x] PHASE-02-F07 complete
- [x] PHASE-02-F08 complete
- [x] PHASE-02-F09 complete
- [x] All PHASE-02 features complete
- [x] Database migration verified
- [x] Model tests pass
- [x] API foundation verified
- [x] Error handling verified
- [x] Health checks verified
- [x] Documentation updated
- [x] Phase review complete

---

# 11. PHASE 03 — FRONTEND DESIGN SYSTEM & APPLICATION SHELL

## Objective

Create the application shell and reusable UI foundation using `design.md` as the visual source of truth.

## Dependencies

- PHASE-01 completed.
- Backend foundation from PHASE-02 available where required.

## Project Tasks

- Initialize frontend.
- Establish design tokens from `design.md`.
- Establish typography.
- Establish color system.
- Create reusable components.
- Create application shell.
- Create navigation.
- Implement loading, empty, and error states.
- Establish accessibility foundation.
- Establish responsive behavior.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-03-F01 | Frontend Bootstrap | 1 |
| PHASE-03-F02 | Design Tokens | 2 |
| PHASE-03-F03 | Typography and Global Styles | 3 |
| PHASE-03-F04 | Core UI Components | 4 |
| PHASE-03-F05 | Application Shell | 5 |
| PHASE-03-F06 | Sidebar and Navigation | 6 |
| PHASE-03-F07 | Top Navigation | 7 |
| PHASE-03-F08 | Loading/Empty/Error States | 8 |
| PHASE-03-F09 | Responsive and Accessibility Foundation | 9 |
| PHASE-03-F10 | Frontend Verification | 10 |

## Technical Work

Do not duplicate `design.md`.

Reference it for:

- spacing;
- typography;
- colors;
- component appearance;
- interaction patterns;
- layout rules.

Create reusable components rather than page-specific copies.

## Testing

Test:

- rendering;
- navigation;
- responsive behavior;
- keyboard accessibility;
- loading states;
- error states;
- empty states;
- reusable component behavior.

## Acceptance Criteria

- Application shell renders.
- Navigation is consistent.
- Design tokens are centralized.
- Components are reusable.
- States are represented.
- Accessibility baseline is established.
- UI conforms to `design.md`.

## Completion Checklist

- [x] PHASE-03-F01 complete
- [x] PHASE-03-F02 complete
- [x] PHASE-03-F03 complete
- [x] PHASE-03-F04 complete
- [x] PHASE-03-F05 complete
- [x] PHASE-03-F06 complete
- [x] PHASE-03-F07 complete
- [x] PHASE-03-F08 complete
- [x] PHASE-03-F09 complete
- [x] PHASE-03-F10 complete
- [x] All PHASE-03 features complete
- [x] Frontend initialized
- [x] Design system implemented
- [x] Shell complete
- [x] Navigation complete
- [x] State components complete
- [x] Accessibility checked
- [x] Responsive behavior checked
- [x] Tests passing
- [x] Phase review complete

---

# 12. PHASE 04 — CONTROLLED VULNERABLE WEB APPLICATION

## Objective

Create the deliberately vulnerable target application required for the academic laboratory.

This application exists solely to reproduce the approved, isolated research scenario.

## Dependencies

- PHASE-01 completed.
- PHASE-02 foundation available.
- PHASE-03 foundation available where UI is required.

## Safety Boundary

The vulnerable application must remain:

- isolated;
- deterministic;
- resettable;
- documented;
- reproducible;
- limited to approved academic scenarios.

It must not become a generalized exploitation or penetration-testing framework.

Do not add unrelated vulnerabilities or offensive capabilities merely because they are technically possible.

## Project Tasks

Implement controlled scenarios representing the project's approved workflow:

```text
LFI / Path Traversal Recon
        ↓
Controlled Log Poisoning
        ↓
Controlled RCE
        ↓
Controlled Web-Shell Evidence
        ↓
Controlled Post-Exploitation Evidence
        ↓
Controlled Meterpreter-Related Laboratory Evidence
        ↓
Controlled PATH / Environment Variable Scenario
        ↓
Evidence Generation
```

The implementation must prioritize **artifact generation and forensic reproducibility**, not offensive capability.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-04-F01 | Controlled Target Application | 1 |
| PHASE-04-F02 | Controlled File-Access Scenario | 2 |
| PHASE-04-F03 | Controlled Logging Scenario | 3 |
| PHASE-04-F04 | Controlled Log-Poisoning Scenario | 4 |
| PHASE-04-F05 | Controlled RCE Evidence Scenario | 5 |
| PHASE-04-F06 | Controlled Post-Exploitation Evidence | 6 |
| PHASE-04-F07 | Controlled Environment/PATH Scenario | 7 |
| PHASE-04-F08 | Scenario Reset | 8 |
| PHASE-04-F09 | Expected Artifact Catalogue | 9 |
| PHASE-04-F10 | Vulnerable Application Verification | 10 |

## Technical Work

Each scenario must define:

```text
Scenario ID
Purpose
Preconditions
Expected behavior
Expected artifacts
Expected timestamps
Expected evidence sources
Reset procedure
Verification procedure
Failure behavior
```

The task document must not contain operational exploitation instructions beyond what is required to define the controlled software behavior.

## Testing

Verify:

- each scenario behaves deterministically;
- expected artifacts are generated;
- reset restores the expected baseline;
- unexpected external access is prevented;
- scenario boundaries remain isolated;
- malformed inputs do not escape intended laboratory boundaries.

## Acceptance Criteria

- All approved scenarios are reproducible.
- Each scenario generates documented artifacts.
- Reset functionality works.
- Laboratory boundaries are preserved.
- The target does not expose unrelated functionality.
- Tests verify expected behavior and artifact generation.

## Completion Checklist

- [x] Target application implemented
- [x] Controlled scenarios implemented
- [x] Artifact expectations documented
- [x] Reset implemented
- [x] Isolation verified
- [x] Scenario tests pass
- [x] No generalized offensive functionality added
- [x] Phase security review complete
- [x] Phase review complete

---

# 13. PHASE 05 — ISOLATED LABORATORY ENVIRONMENT

## Objective

Create a reproducible laboratory environment around the controlled vulnerable application.

## Dependencies

- PHASE-04 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-05-F01 | Lab Container Topology | 1 |
| PHASE-05-F02 | Dedicated Lab Network | 2 |
| PHASE-05-F03 | Supporting Services | 3 |
| PHASE-05-F04 | Scenario Configuration | 4 |
| PHASE-05-F05 | Lab Reset | 5 |
| PHASE-05-F06 | Lab Health Status | 6 |
| PHASE-05-F07 | Reproducibility Verification | 7 |

## Technical Work

Implement the isolation architecture defined by `architecture.md`.

The laboratory must support:

- deterministic startup;
- deterministic reset;
- known configuration;
- controlled connectivity;
- health reporting;
- scenario reproducibility.

## Testing

Test:

- clean startup;
- isolated network behavior;
- service availability;
- reset;
- repeated scenario execution;
- failure recovery;
- unauthorized connectivity assumptions.

## Acceptance Criteria

A fresh evaluator must be able to reproduce the approved laboratory state using documented procedures.

## Completion Checklist

- [x] Lab topology complete
- [x] Network isolation verified
- [x] Scenario configuration verified
- [x] Reset verified
- [x] Health checks verified
- [x] Repeated execution verified
- [x] Documentation complete
- [x] Security review complete

---

# 14. PHASE 06 — EVIDENCE COLLECTION

## Objective

Build a trustworthy evidence ingestion and preservation pipeline.

## Dependencies

- PHASE-05 completed.
- PHASE-02 database foundation completed.

## Forensic Principle

**Original evidence must remain immutable.**

The system must distinguish between:

```text
Original Evidence
      ↓
Working Copy
      ↓
Derived Evidence
      ↓
Analysis Results
```

Derived analysis must never silently replace original evidence.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-06-F01 | Evidence Storage | 1 |
| PHASE-06-F02 | Evidence Metadata | 2 |
| PHASE-06-F03 | Evidence Integrity Hashing | 3 |
| PHASE-06-F04 | Evidence Ingestion | 4 |
| PHASE-06-F05 | Evidence Validation | 5 |
| PHASE-06-F06 | Processing States | 6 |
| PHASE-06-F07 | Evidence Retrieval | 7 |
| PHASE-06-F08 | Evidence Chain Verification | 8 |

## Technical Work

Support:

- immutable originals;
- SHA-256 integrity verification;
- evidence identifiers;
- acquisition metadata;
- source metadata;
- timestamps;
- file/type metadata;
- processing status;
- validation results.

Exact schemas follow `architecture.md`.

## Testing

Test:

- valid evidence ingestion;
- duplicate evidence;
- corrupted evidence;
- hash mismatch;
- missing metadata;
- inaccessible evidence;
- interrupted ingestion;
- retrieval without modification.

## Acceptance Criteria

- Evidence can be ingested.
- Original content is preserved.
- Integrity can be independently verified.
- Metadata is persisted.
- Processing state is visible.
- Errors are retained and explainable.

## Completion Checklist

- [x] Storage implemented
- [x] Metadata implemented
- [x] SHA-256 verification implemented
- [x] Ingestion implemented
- [x] Validation implemented
- [x] Processing states implemented
- [x] Failure tests pass
- [x] Immutability verified
- [x] Traceability verified
- [x] Phase review complete

---

# 15. PHASE 07 — FORENSIC PROCESSING ENGINE

## Objective

Transform preserved evidence into structured forensic information without destroying source fidelity.

## Dependencies

- PHASE-06 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-07-F01 | Parser Framework | 1 |
| PHASE-07-F02 | Source Detection | 2 |
| PHASE-07-F03 | Web Log Parser | 3 |
| PHASE-07-F04 | Application Log Parser | 4 |
| PHASE-07-F05 | System/Process Evidence Parser | 5 |
| PHASE-07-F06 | Parser Error Handling | 6 |
| PHASE-07-F07 | Malformed Evidence Handling | 7 |
| PHASE-07-F08 | Processing Verification | 8 |

## Technical Work

Create an extensible parser architecture.

Every parser should provide enough metadata to establish:

```text
Original Evidence
      ↓
Parser
      ↓
Derived Record
      ↓
Source Location
      ↓
Evidence Reference
```

Parser failures must be observable.

Malformed records must not simply disappear.

## Testing

Test:

- valid logs;
- malformed logs;
- missing fields;
- unexpected formats;
- empty files;
- encoding issues where relevant;
- parser failures;
- partial processing;
- evidence references.

## Acceptance Criteria

- Supported evidence sources parse correctly.
- Parser errors are recorded.
- Malformed evidence does not silently disappear.
- Derived records remain traceable to original evidence.

## Completion Checklist

- [x] Parser framework complete
- [x] Required parsers complete
- [x] Error handling complete
- [x] Malformed evidence tests pass
- [x] Evidence traceability verified
- [x] Documentation updated
- [x] Phase review complete

---

# 16. PHASE 08 — COMMON EVENT MODEL / EVENT NORMALIZATION

## Objective

Create a consistent event representation across heterogeneous forensic sources.

## Dependencies

- PHASE-07 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-08-F01 | Common Event Schema | 1 |
| PHASE-08-F02 | Event Validation | 2 |
| PHASE-08-F03 | Normalization Pipeline | 3 |
| PHASE-08-F04 | Event Persistence | 4 |
| PHASE-08-F05 | Event Search | 5 |
| PHASE-08-F06 | Event Filtering | 6 |
| PHASE-08-F07 | Evidence Traceability | 7 |

## Event Model

The common event model should conceptually support:

```text
event_id
timestamp
source
event_type
severity
actor
target
action
attack_stage
evidence_id
metadata
```

Exact schema and field types must follow `architecture.md`.

## Testing

Test:

- schema validation;
- normalization;
- missing values;
- timestamp handling;
- source references;
- event persistence;
- search;
- filtering.

## Acceptance Criteria

All supported forensic sources can produce validated normalized events while retaining their original evidence references.

## Completion Checklist

- [x] Event schema defined
- [x] Validation implemented
- [x] Normalization implemented
- [x] Persistence implemented
- [x] Search implemented
- [x] Filtering implemented
- [x] Evidence references verified
- [x] Tests pass
- [x] Phase review complete

---

# 17. PHASE 09 — DETECTION ENGINE

## Objective

Create explainable, deterministic detection rules for the project's controlled scenario.

## Dependencies

- PHASE-08 completed.

## Design Principle

Detection must be explainable.

A detection rule must identify **why** an event or event group triggered.

## Detection Rule Structure

Every rule must contain:

```text
Rule ID
Name
Description
Input Event Types
Conditions
Severity
Attack Stage
Explanation
Evidence References
```

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-09-F01 | Rule Model | 1 |
| PHASE-09-F02 | Rule Registration | 2 |
| PHASE-09-F03 | Rule Evaluation | 3 |
| PHASE-09-F04 | Controlled Scenario Rules | 4 |
| PHASE-09-F05 | Detection Evidence Linking | 5 |
| PHASE-09-F06 | Detection Explanation | 6 |
| PHASE-09-F07 | Detection Testing | 7 |

## Technical Work

Detection categories should cover the approved academic scenario without becoming a generalized offensive security engine.

Examples of conceptual detection areas include:

- suspicious file-access behavior;
- anomalous log-related activity;
- controlled execution indicators;
- post-exploitation evidence;
- controlled environment/PATH indicators;
- abnormal process relationships.

Exact detection logic must be derived from approved project requirements and architecture.

## Testing

Each rule requires:

- positive test;
- negative test;
- boundary test where relevant;
- explanation verification;
- evidence-reference verification.

## Acceptance Criteria

- Rules are deterministic.
- Rules are explainable.
- Detections reference source events.
- Detections reference evidence.
- False assumptions are not presented as facts.

## Completion Checklist

- [x] Rule model implemented
- [x] Rule registration implemented
- [x] Evaluation implemented
- [x] Scenario rules implemented
- [x] Evidence linking verified
- [x] Explanations verified
- [x] Detection tests pass
- [x] No generalized offensive capability introduced
- [x] Phase review complete

---

# 18. PHASE 10 — EVENT CORRELATION ENGINE

## Objective

Combine related observations into explainable incident-level relationships.

## Dependencies

- PHASE-09 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-10-F01 | Correlation Model | 1 |
| PHASE-10-F02 | Temporal Correlation | 2 |
| PHASE-10-F03 | Source Correlation | 3 |
| PHASE-10-F04 | Process/User/Session Correlation | 4 |
| PHASE-10-F05 | Attack-Stage Correlation | 5 |
| PHASE-10-F06 | Confidence Model | 6 |
| PHASE-10-F07 | Correlation Explanation | 7 |

## Technical Work

Correlation may consider:

- temporal proximity;
- source relationships;
- process relationships;
- user relationships;
- session relationships;
- attack-stage relationships.

Where evidence is insufficient, the system must communicate uncertainty.

## Evidence Classification

Use explicit categories:

| Classification | Meaning |
|---|---|
| `Observed` | Directly represented by available evidence |
| `Likely` | Strongly supported but not directly proven |
| `Correlated` | Supported by relationships between multiple observations |
| `Inferred` | Analytical interpretation requiring explicit qualification |

The UI and reports must not present `Inferred` information as confirmed fact.

## Testing

Test:

- related events;
- unrelated events;
- temporal boundaries;
- incomplete evidence;
- conflicting evidence;
- confidence calculation;
- classification.

## Acceptance Criteria

- Correlations are traceable.
- Confidence is explicit.
- Observations and inferences are distinguished.
- Correlation explanations identify contributing evidence.

## Completion Checklist

- [x] Correlation model complete
- [x] Temporal correlation complete
- [x] Source correlation complete
- [x] Context correlation complete
- [x] Confidence model complete
- [x] Explanations complete
- [x] Tests pass
- [x] Uncertainty verified
- [x] Phase review complete

---

# 19. PHASE 11 — TIMELINE & ATTACK CHAIN

## Objective

Reconstruct the incident chronologically and visually.

## Dependencies

- PHASE-10 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-11-F01 | Timeline Data Model | 1 |
| PHASE-11-F02 | Chronological Timeline | 2 |
| PHASE-11-F03 | Attack-Stage Mapping | 3 |
| PHASE-11-F04 | Timeline Filtering | 4 |
| PHASE-11-F05 | Event Drill-Down | 5 |
| PHASE-11-F06 | Evidence References | 6 |
| PHASE-11-F07 | Attack-Chain Graph | 7 |

## Technical Work

The investigator should be able to move from:

```text
Timeline Entry
      ↓
Event
      ↓
Detection / Correlation
      ↓
Evidence
      ↓
Original Artifact
```

The attack-chain visualization must distinguish direct observations from analytical relationships.

## Testing

Test:

- chronological ordering;
- timestamp edge cases;
- filtering;
- drill-down;
- evidence links;
- attack-stage representation;
- graph consistency.

## Acceptance Criteria

An evaluator can reconstruct the controlled attack sequence from the timeline without relying solely on narrative text.

## Completion Checklist

- [x] Timeline model complete
- [x] Timeline UI complete
- [x] Filtering complete
- [x] Drill-down complete
- [x] Evidence references complete
- [x] Attack-chain graph complete
- [x] Timeline tests pass
- [x] Phase review complete

---

# 20. PHASE 12 — INVESTIGATION WORKSPACE

## Objective

Provide investigators with a unified workspace for examining cases, evidence, events, detections, and findings.

## Dependencies

- PHASE-11 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-12-F01 | Case Management | 1 |
| PHASE-12-F02 | Evidence Workspace | 2 |
| PHASE-12-F03 | Event Investigation | 3 |
| PHASE-12-F04 | Detection Investigation | 4 |
| PHASE-12-F05 | Finding Management | 5 |
| PHASE-12-F06 | Evidence-to-Finding Traceability | 6 |
| PHASE-12-F07 | Investigation Navigation | 7 |

## Critical Traceability Relationship

```text
Finding
   ↓
Detection
   ↓
Event
   ↓
Evidence
   ↓
Original Artifact
```

Every supported finding must be traceable through this chain wherever the evidence permits.

## Testing

Test:

- case creation;
- case retrieval;
- evidence navigation;
- event investigation;
- detection investigation;
- finding creation;
- traceability;
- missing-reference handling.

## Acceptance Criteria

An investigator can navigate from a finding to its supporting evidence and original artifact without losing context.

## Completion Checklist

- [x] Case management complete
- [x] Evidence workspace complete
- [x] Event investigation complete
- [x] Detection investigation complete
- [x] Finding management complete
- [x] Traceability verified
- [x] Tests pass
- [x] Phase review complete

---

# 21. PHASE 13 — DASHBOARD & ANALYTICS

## Objective

Provide a concise analytical overview without replacing detailed investigation workflows.

## Dependencies

- PHASE-12 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-13-F01 | Case Overview | 1 |
| PHASE-13-F02 | Evidence Metrics | 2 |
| PHASE-13-F03 | Event Metrics | 3 |
| PHASE-13-F04 | Detection Metrics | 4 |
| PHASE-13-F05 | Finding Metrics | 5 |
| PHASE-13-F06 | Event Trends | 6 |
| PHASE-13-F07 | Severity Distribution | 7 |
| PHASE-13-F08 | Attack-Stage Analytics | 8 |
| PHASE-13-F09 | Recent Activity | 9 |
| PHASE-13-F10 | Explainable Risk Summary | 10 |

## Technical Work

Dashboard information must derive from actual system data.

Avoid decorative metrics with no analytical meaning.

## Testing

Verify:

- metric accuracy;
- empty states;
- filtering;
- date ranges where supported;
- loading behavior;
- consistency with underlying data.

## Acceptance Criteria

Dashboard values can be traced to the underlying case, evidence, event, detection, or finding data.

## Completion Checklist

- [x] Required metrics implemented
- [x] Analytics verified
- [x] Empty states verified
- [x] Loading states verified
- [x] Accuracy tested
- [x] UX reviewed
- [x] Phase review complete

---

# 22. PHASE 14 — FORENSIC REPORTING

## Objective

Produce an academic-quality, evidence-backed forensic report.

## Dependencies

- PHASE-12 completed.
- PHASE-11 completed.
- PHASE-13 available where dashboard information is included.

## Report Structure

Reports should support:

1. Case information
2. Executive summary
3. Investigation scope
4. Evidence
5. Timeline
6. Detections
7. Attack chain
8. Findings
9. Evidence references
10. Mitigation
11. Verification
12. Limitations

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-14-F01 | Report Data Model | 1 |
| PHASE-14-F02 | Report Assembly | 2 |
| PHASE-14-F03 | Evidence References | 3 |
| PHASE-14-F04 | Timeline Section | 4 |
| PHASE-14-F05 | Findings Section | 5 |
| PHASE-14-F06 | Mitigation Section | 6 |
| PHASE-14-F07 | Limitations Section | 7 |
| PHASE-14-F08 | Report Preview | 8 |
| PHASE-14-F09 | Report Export | 9 |

## Technical Work

Reports must distinguish:

- evidence;
- detection;
- correlation;
- interpretation;
- limitations.

Do not generate unsupported claims.

## Testing

Test:

- report completeness;
- evidence references;
- missing data;
- long timelines;
- multiple findings;
- export;
- reproducibility.

## Acceptance Criteria

A report can be generated from a completed investigation and contains traceable, evidence-backed conclusions.

## Completion Checklist

- [x] Report model complete
- [x] Assembly complete
- [x] Required sections complete
- [x] Evidence references verified
- [x] Preview verified
- [x] Export verified
- [x] Accuracy reviewed
- [x] Phase review complete

---

# 23. PHASE 15 — MITIGATION & VERIFICATION

## Objective

Demonstrate that the platform can move from forensic discovery to measurable remediation verification.

## Dependencies

- PHASE-04 completed.
- PHASE-14 completed.
- Evidence, detection, and investigation pipelines completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-15-F01 | Mitigation Recommendations | 1 |
| PHASE-15-F02 | Secure Configuration State | 2 |
| PHASE-15-F03 | Before-State Capture | 3 |
| PHASE-15-F04 | Controlled Scenario Reproduction | 4 |
| PHASE-15-F05 | Mitigation Application | 5 |
| PHASE-15-F06 | After-State Capture | 6 |
| PHASE-15-F07 | Before/After Comparison | 7 |
| PHASE-15-F08 | Verification Evidence | 8 |

## Required Demonstration

```text
BEFORE
  ↓
Vulnerability / Attack Behavior
  ↓
Evidence
  ↓
Detection
  ↓
Finding

MITIGATION
  ↓
Repeat Controlled Scenario
  ↓
Compare Results
  ↓
Verify Improvement
```

## Technical Work

The verification workflow must use the same controlled laboratory assumptions as the original scenario.

Do not introduce uncontrolled attack behavior.

## Testing

Verify:

- baseline scenario;
- mitigation state;
- repeated scenario;
- evidence differences;
- detection differences;
- verification conclusion.

## Acceptance Criteria

The evaluator can see measurable evidence that the mitigation changed the relevant laboratory behavior or detection outcome.

## Completion Checklist

- [x] Mitigation recommendations implemented
- [x] Baseline captured
- [x] Scenario repeated
- [x] Mitigation state captured
- [x] Before/after comparison implemented
- [x] Verification evidence linked
- [x] Tests pass
- [x] Phase review complete

---

# 24. PHASE 16 — END-TO-END INTEGRATION

## Objective

Connect all major system components into one reproducible academic workflow.

## Dependencies

- PHASE-15 completed.

## Complete Flow

```text
Lab Scenario
      ↓
Attack Activity
      ↓
Evidence
      ↓
Evidence Collection
      ↓
Evidence Validation
      ↓
Parsing
      ↓
Normalization
      ↓
Detection
      ↓
Correlation
      ↓
Timeline
      ↓
Investigation
      ↓
Finding
      ↓
Report
      ↓
Mitigation
      ↓
Verification
```

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-16-F01 | Lab-to-Evidence Integration | 1 |
| PHASE-16-F02 | Evidence-to-Processing Integration | 2 |
| PHASE-16-F03 | Processing-to-Event Integration | 3 |
| PHASE-16-F04 | Event-to-Detection Integration | 4 |
| PHASE-16-F05 | Detection-to-Correlation Integration | 5 |
| PHASE-16-F06 | Correlation-to-Timeline Integration | 6 |
| PHASE-16-F07 | Timeline-to-Investigation Integration | 7 |
| PHASE-16-F08 | Investigation-to-Report Integration | 8 |
| PHASE-16-F09 | Mitigation-to-Verification Integration | 9 |
| PHASE-16-F10 | Full Workflow Verification | 10 |

## Testing

Execute the complete workflow from a clean laboratory state.

Repeat it enough times to establish reproducibility.

## Acceptance Criteria

A clean evaluator environment can reproduce the complete workflow from scenario execution through final report and mitigation verification.

## Completion Checklist

- [x] All system boundaries connected
- [x] End-to-end data flow verified
- [x] Traceability verified
- [x] Full scenario reproducible
- [x] Report generated
- [x] Mitigation verified
- [x] End-to-end tests pass
- [x] Phase review complete

---

# 25. PHASE 17 — TESTING & RELIABILITY

## Objective

Demonstrate that ForensiWeb is reliable and not merely visually complete.

## Dependencies

- PHASE-16 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-17-F01 | Unit Test Expansion | 1 |
| PHASE-17-F02 | Integration Tests | 2 |
| PHASE-17-F03 | End-to-End Tests | 3 |
| PHASE-17-F04 | Regression Suite | 4 |
| PHASE-17-F05 | Reproducibility Tests | 5 |
| PHASE-17-F06 | Failure Recovery | 6 |
| PHASE-17-F07 | Invalid Evidence Tests | 7 |
| PHASE-17-F08 | Parser Failure Tests | 8 |
| PHASE-17-F09 | Database Failure Tests | 9 |
| PHASE-17-F10 | Interrupted Processing Tests | 10 |

## Testing Areas

Test at minimum:

- valid workflows;
- invalid inputs;
- malformed evidence;
- parser errors;
- storage errors;
- database unavailability;
- interrupted processing;
- duplicate processing;
- repeated laboratory execution;
- regression behavior.

## Acceptance Criteria

- Critical paths have automated coverage appropriate to the architecture.
- Failure states are predictable.
- Errors are observable.
- No critical workflow silently loses evidence.
- Repeated execution produces consistent results within documented tolerances.

## Completion Checklist

- [x] Unit suite complete
- [x] Integration suite complete
- [x] E2E suite complete
- [x] Regression suite complete
- [x] Failure tests complete
- [x] Reproducibility verified
- [x] Critical defects resolved
- [x] Phase review complete

---

# 26. PHASE 18 — SECURITY HARDENING

## Objective

Harden the ForensiWeb platform while preserving the intentionally vulnerable and isolated nature of the laboratory target.

## Dependencies

- PHASE-17 completed.

## Critical Distinction

Security must be evaluated separately for:

### 1. Controlled Vulnerable Laboratory Target

The target is intentionally vulnerable within its approved scenario.

Its security objective is:

- isolation;
- containment;
- reproducibility;
- predictable artifact generation;
- safe reset.

### 2. ForensiWeb Platform

The platform itself must be developed as secure software.

Its security objective includes:

- input validation;
- authentication where required;
- authorization;
- secure configuration;
- secret protection;
- audit logging;
- dependency hygiene;
- safe error handling;
- laboratory isolation.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-18-F01 | Input Validation Review | 1 |
| PHASE-18-F02 | Authentication Review | 2 |
| PHASE-18-F03 | Authorization Review | 3 |
| PHASE-18-F04 | Secret Management Review | 4 |
| PHASE-18-F05 | Secure Configuration Review | 5 |
| PHASE-18-F06 | Laboratory Isolation Review | 6 |
| PHASE-18-F07 | Audit Logging Review | 7 |
| PHASE-18-F08 | Dependency Review | 8 |
| PHASE-18-F09 | Security Testing | 9 |
| PHASE-18-F10 | Security Findings Remediation | 10 |

## Acceptance Criteria

- No known critical security defect remains unresolved.
- Secrets are not exposed.
- Platform boundaries are enforced.
- Laboratory isolation is verified.
- Security findings are documented and addressed according to severity.

## Completion Checklist

- [x] Validation reviewed
- [x] Authentication reviewed
- [x] Authorization reviewed
- [x] Secrets reviewed
- [x] Configuration reviewed
- [x] Lab isolation tested
- [x] Dependencies reviewed
- [x] Security tests pass
- [x] Findings remediated
- [x] Security review approved

---

# 27. PHASE 19 — PERFORMANCE & UX REFINEMENT

## Objective

Improve usability, responsiveness, accessibility, and performance after functional correctness has been established.

## Dependencies

- PHASE-18 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-19-F01 | Dashboard Optimization | 1 |
| PHASE-19-F02 | Evidence Processing Optimization | 2 |
| PHASE-19-F03 | Pagination | 3 |
| PHASE-19-F04 | Search Optimization | 4 |
| PHASE-19-F05 | Loading UX | 5 |
| PHASE-19-F06 | Timeline Performance | 6 |
| PHASE-19-F07 | Responsive Refinement | 7 |
| PHASE-19-F08 | Accessibility Refinement | 8 |
| PHASE-19-F09 | UI Consistency Review | 9 |

## Technical Work

Optimization must be evidence-based.

Do not introduce unnecessary complexity merely for theoretical performance.

Prioritize:

- large evidence sets;
- event lists;
- timeline rendering;
- searches;
- dashboard aggregation;
- report generation.

## Testing

Verify:

- representative data volumes;
- large timelines;
- large event sets;
- evidence processing;
- slow operations;
- responsive layouts;
- accessibility.

## Acceptance Criteria

- No critical usability issue remains.
- Large forensic datasets remain usable within documented expectations.
- UI follows `design.md`.
- Accessibility issues identified during review are resolved or documented.

## Completion Checklist

- [x] Performance hotspots reviewed
- [x] Search optimized
- [x] Pagination verified
- [x] Timeline optimized
- [x] Loading states refined
- [x] Responsive behavior verified
- [x] Accessibility reviewed
- [x] UX review complete

---

# 28. PHASE 20 — FINAL ACADEMIC VALIDATION

## Objective

Validate the complete project as an academic cybersecurity and digital-forensics system.

## Dependencies

- PHASE-19 completed.

## Features

| ID | Feature | Order |
|---|---|---:|
| PHASE-20-F01 | Complete Controlled Attack Scenario | 1 |
| PHASE-20-F02 | Complete Forensic Reconstruction | 2 |
| PHASE-20-F03 | Evidence Traceability Audit | 3 |
| PHASE-20-F04 | Before/After Mitigation Demonstration | 4 |
| PHASE-20-F05 | Final Report Validation | 5 |
| PHASE-20-F06 | Reproducibility Demonstration | 6 |
| PHASE-20-F07 | Documentation Review | 7 |
| PHASE-20-F08 | Architecture Review | 8 |
| PHASE-20-F09 | Security Review | 9 |
| PHASE-20-F10 | Reliability Review | 10 |
| PHASE-20-F11 | UI/UX Review | 11 |
| PHASE-20-F12 | Final Academic Acceptance | 12 |

## Final Evaluator Questions

The completed system must make it possible to answer:

### What happened?

Identify the observed activity and relevant attack stages.

### When did it happen?

Provide a defensible chronological timeline.

### What evidence proves it?

Trace findings to events and original evidence.

### How was it detected?

Explain the detection rule or analytical mechanism.

### How were events correlated?

Explain the relationships and confidence.

### What was the impact?

Describe only what the available evidence supports.

### How was it mitigated?

Identify the implemented or demonstrated remediation.

### How was mitigation verified?

Show before/after evidence and comparison.

## Acceptance Criteria

- Complete controlled attack scenario executes.
- Evidence is preserved and traceable.
- Processing is reproducible.
- Events are normalized.
- Detection is explainable.
- Correlation is defensible.
- Timeline is reconstructable.
- Findings reference evidence.
- Report is generated.
- Mitigation is demonstrated.
- Verification evidence is available.
- Documentation is consistent.
- Security review is complete.
- Reliability review is complete.

## Completion Checklist

- [x] Complete laboratory scenario executed
- [x] Evidence collected
- [x] Evidence integrity verified
- [x] Evidence parsed
- [x] Events normalized
- [x] Detections generated
- [x] Correlation completed
- [x] Timeline reconstructed
- [x] Investigation completed
- [x] Findings generated
- [x] Report generated
- [x] Mitigation demonstrated
- [x] Verification completed
- [x] Documentation reviewed
- [x] Architecture reviewed
- [x] Security reviewed
- [x] Reliability reviewed
- [x] UX reviewed
- [x] Final academic acceptance completed

---

# 29. Definition of Done

## 29.1 Feature Definition of Done

A feature is `COMPLETED` only when all of the following are true:

```text
Implementation Complete
        +
Tests Written
        +
Tests Passing
        +
Acceptance Criteria Satisfied
        +
Documentation Updated
        +
Security Reviewed
        +
No Known Blocking Issue
        =
FEATURE DONE
```

Checklist:

- [ ] Implementation complete
- [ ] Relevant tests written
- [ ] Relevant tests passing
- [ ] Acceptance criteria satisfied
- [ ] Error paths reviewed
- [ ] Security requirements satisfied
- [ ] Documentation updated
- [ ] No blocking defect remains
- [ ] Feature status changed to `COMPLETED`

## 29.2 Phase Definition of Done

A phase is `COMPLETED` only when:

- every required feature is complete;
- all phase acceptance criteria are satisfied;
- relevant automated tests pass;
- integration behavior is verified;
- security review is complete;
- documentation is updated;
- no unresolved blocking issue remains.

A phase must not be marked complete merely because all code has been written.

---

# 30. Dependency Principle

The normal dependency chain is:

```text
Foundation
   ↓
Infrastructure
   ↓
Application
   ↓
Laboratory
   ↓
Evidence
   ↓
Forensics
   ↓
Detection
   ↓
Correlation
   ↓
Investigation
   ↓
Reporting
   ↓
Mitigation
   ↓
Validation
```

Later phases must not be implemented as if their dependencies already exist when those dependencies are incomplete.

For example:

- do not build sophisticated correlation before normalized events exist;
- do not build evidence-backed findings before evidence traceability exists;
- do not build final reports around fabricated data;
- do not claim mitigation verification without a reproducible baseline;
- do not optimize workflows that have not yet been proven correct.

---

# 31. Change Management

New requirements must follow a controlled process.

```text
New Requirement
      ↓
Check PRD
      ↓
Check Architecture
      ↓
Check Design
      ↓
Check Rules
      ↓
Determine Affected Phase
      ↓
Update task.md if Necessary
      ↓
Implement
      ↓
Test
      ↓
Verify
```

## Change Rules

When a new requirement appears:

1. Determine whether it is already covered.
2. Determine which source-of-truth document owns it.
3. Determine whether it changes project scope.
4. Determine which phases are affected.
5. Update the appropriate documentation.
6. Update `task.md` if implementation order changes.
7. Re-evaluate dependencies.
8. Implement only after approval of the changed scope.

Uncontrolled scope expansion is prohibited.

---

# 32. Scope Control

ForensiWeb should prioritize:

```text
DEPTH
+
RELIABILITY
+
FORENSIC TRACEABILITY
+
REPRODUCIBILITY
+
ACADEMIC QUALITY
```

over raw feature count.

The following must not be added merely to make the project appear larger:

- unrelated vulnerabilities;
- unrelated attack techniques;
- generalized penetration-testing capabilities;
- generalized exploitation modules;
- unnecessary microservices;
- unnecessary AI features;
- unnecessary dashboards;
- unrelated integrations;
- excessive animations;
- unrelated mobile applications;
- unrelated security tools;
- features with no clear forensic or academic value.

Every proposed addition must answer:

1. Does it support the approved research objective?
2. Does it improve forensic analysis?
3. Does it improve reproducibility?
4. Does it improve evidence traceability?
5. Does it belong in the existing architecture?
6. Does it justify its testing and maintenance cost?

If the answer is no, the feature should normally be rejected or deferred.

---

# 33. AI Coding-Agent Execution Rules

The AI coding agent must follow these rules throughout development.

## Rule 1 — Never Build the Entire Roadmap at Once

Only the active phase may be implemented.

## Rule 2 — Only Implement the Current Feature

Do not silently begin unrelated features.

## Rule 3 — Read Documentation Before Coding

Relevant requirements must be understood before implementation.

## Rule 4 — Inspect Existing Code First

Do not create duplicate services, components, utilities, models, or infrastructure.

## Rule 5 — Respect Architecture Boundaries

Do not bypass established boundaries for convenience.

## Rule 6 — Test After Implementation

A feature without appropriate tests is incomplete.

## Rule 7 — Fix Failing Tests

Do not move forward while known blocking test failures remain.

## Rule 8 — Do Not Hide Errors

Errors must be observable and diagnosable.

## Rule 9 — Do Not Fake Critical Functionality

Placeholder data, hard-coded success states, and simulated critical workflows must not be presented as real functionality.

Mocks may be used in appropriate automated tests but must not replace required production behavior.

## Rule 10 — Preserve Evidence Integrity

Original evidence must remain immutable.

## Rule 11 — Preserve Evidence Traceability

Derived records, detections, correlations, findings, and reports must retain appropriate links to their supporting evidence.

## Rule 12 — Keep the Laboratory Isolated

The vulnerable laboratory must remain contained and reproducible.

## Rule 13 — Do Not Build a Generalized Offensive Framework

The laboratory exists for controlled academic reproduction and forensic analysis.

## Rule 14 — Avoid Unrelated File Changes

Changes outside the current feature require justification.

## Rule 15 — Update Documentation When Behavior Changes

Documentation must reflect the actual system.

## Rule 16 — Do Not Mark Incomplete Work Complete

Acceptance criteria are mandatory.

## Rule 17 — Preserve Uncertainty

Do not turn inference into fact.

## Rule 18 — Do Not Silently Change the Technology Stack

Technology choices belong to `architecture.md`.

## Rule 19 — Reuse Before Rebuilding

Existing components and services should be reused when appropriate.

## Rule 20 — Do Not Cross a Blocking Phase Boundary

The next phase cannot begin while the current phase contains unresolved blocking issues.

---

# 34. Implementation Review Checklist

Before marking any feature complete, the agent should answer:

```text
Requirement
    ↓
What exactly was requested?

Existing System
    ↓
What already exists?

Dependencies
    ↓
What must already work?

Implementation
    ↓
What changed?

Testing
    ↓
What proves it works?

Failure Handling
    ↓
What happens when it fails?

Security
    ↓
What could go wrong?

Traceability
    ↓
Can the result be traced to its source?

Documentation
    ↓
Does documentation match reality?

Acceptance
    ↓
Are all criteria satisfied?
```

If any answer is unknown, the feature should remain incomplete.

---

# 35. Evidence Integrity Requirements

Evidence-related features must preserve the following conceptual chain:

```text
Original Artifact
      ↓
Integrity Hash
      ↓
Evidence Record
      ↓
Processing Record
      ↓
Parsed Data
      ↓
Normalized Event
      ↓
Detection
      ↓
Correlation
      ↓
Timeline
      ↓
Finding
      ↓
Report
```

The system must make it possible to move backward through this chain wherever technically applicable.

No derived record should falsely imply that it is an original artifact.

---

# 36. Academic Quality Requirements

The project should favor:

## Reproducibility

A controlled scenario should produce sufficiently consistent results to support demonstration and evaluation.

## Traceability

Claims should be connected to evidence.

## Explainability

Detection and correlation should communicate why a conclusion was reached.

## Transparency

The system should distinguish:

```text
Observed
Likely
Correlated
Inferred
```

## Limitations

Reports should explicitly document relevant limitations and uncertainty.

## Controlled Experimentation

The laboratory should provide a known baseline and reset mechanism.

## Before/After Validation

Mitigation should be evaluated rather than merely described.

---

# 37. Final Phase-Gate Model

Every phase passes through the following gate:

```text
PLANNED
   ↓
READY
   ↓
ACTIVE
   ↓
FEATURE IMPLEMENTATION
   ↓
FEATURE TESTING
   ↓
FEATURE VERIFICATION
   ↓
ALL FEATURES COMPLETE?
   ├── NO → Continue Current Phase
   └── YES
          ↓
      PHASE REVIEW
          ↓
      ACCEPTANCE
          ↓
      COMPLETED
          ↓
      NEXT PHASE READY
```

A failed phase review returns the phase to an appropriate active or blocked state.

---

# 38. Recommended Work Session Protocol

Every AI coding session should begin with:

1. Read the current phase.
2. Read the current feature.
3. Read the relevant source-of-truth documentation.
4. Inspect existing implementation.
5. Confirm dependencies.
6. State the intended implementation scope internally before making changes.
7. Implement only the current feature.
8. Run relevant tests.
9. Review the resulting changes.
10. Update task status.
11. Document necessary changes.
12. Stop when the feature is complete.

The agent should **stop after completing the requested feature** rather than proactively implementing the next feature.

---

# 39. Phase Dependency Summary

| Phase | Depends On | Primary Output |
|---|---|---|
| 01 | Documentation baseline | Reproducible development foundation |
| 02 | 01 | Backend and database foundation |
| 03 | 01, 02 | Frontend shell and design system |
| 04 | 01, 02, 03 | Controlled vulnerable target |
| 05 | 04 | Isolated reproducible laboratory |
| 06 | 05, 02 | Evidence preservation pipeline |
| 07 | 06 | Forensic processing engine |
| 08 | 07 | Common event model |
| 09 | 08 | Explainable detection |
| 10 | 09 | Event correlation |
| 11 | 10 | Timeline and attack chain |
| 12 | 11 | Investigation workspace |
| 13 | 12 | Dashboard and analytics |
| 14 | 11, 12 | Forensic reporting |
| 15 | 04, 14 | Mitigation and verification |
| 16 | 15 | Complete integrated workflow |
| 17 | 16 | Reliability validation |
| 18 | 17 | Security hardening |
| 19 | 18 | Performance and UX refinement |
| 20 | 19 | Final academic validation |

---

# 40. Final Success Model

The completed ForensiWeb system must demonstrate:

```text
Controlled Vulnerable Environment
                ↓
Reproducible Attack Scenario
                ↓
Reliable Evidence Generation
                ↓
Evidence Integrity Verification
                ↓
Evidence Parsing
                ↓
Event Normalization
                ↓
Explainable Detection
                ↓
Event Correlation
                ↓
Attack Timeline Reconstruction
                ↓
Interactive Investigation
                ↓
Evidence-Backed Findings
                ↓
Forensic Report
                ↓
Mitigation
                ↓
Before/After Verification
```

The final system is successful when it can demonstrate, with reproducible evidence:

```text
WHAT happened?
        ↓
WHEN did it happen?
        ↓
WHAT evidence proves it?
        ↓
HOW was it detected?
        ↓
HOW were events correlated?
        ↓
WHAT was the impact?
        ↓
HOW was it mitigated?
        ↓
HOW was mitigation verified?
```

The project must remain focused on controlled cybersecurity experimentation, digital forensics, evidence integrity, explainable analysis, reproducibility, and academic validation.

**One phase at a time.  
One feature at a time.  
One verified result at a time.**