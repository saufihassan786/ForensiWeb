# System Architecture & Technical Design

## 1. Document Purpose

This document defines the technical architecture, component boundaries, technology stack, communication flow, data flow, deployment model, folder structure, and engineering conventions for **ForensiWeb**.

This document is the technical source of truth for implementation.

The architecture must prioritize:

- Security
- Isolation
- Reliability
- Reproducibility
- Evidence integrity
- Explainability
- Maintainability
- Testability
- Clear separation of concerns

---

# 2. System Overview

ForensiWeb consists of four primary layers:

```text
┌───────────────────────────────────────────────────────────┐
│                    Analyst Interface                      │
│              Web Dashboard / Investigation UI             │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                    Application API Layer                   │
│       Authentication • Cases • Events • Reports           │
└─────────────────────────────┬─────────────────────────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
┌──────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Forensic Engine  │ │ Detection Engine│ │ Report Engine   │
│                  │ │                 │ │                 │
│ Parsing          │ │ Rules           │ │ Timeline        │
│ Normalization    │ │ Correlation     │ │ Evidence        │
│ Timeline         │ │ Severity        │ │ Findings        │
│ Evidence         │ │ Attack Stages   │ │ Export          │
└────────┬─────────┘ └────────┬────────┘ └────────┬────────┘
         │                    │                   │
         └────────────────────┼───────────────────┘
                              ▼
                  ┌──────────────────────┐
                  │ Evidence/Data Layer  │
                  │                      │
                  │ PostgreSQL           │
                  │ Evidence Files       │
                  │ Hashes / Metadata    │
                  └──────────┬───────────┘
                             ▲
                             │
                  Controlled Evidence Flow
                             │
                  ┌──────────┴───────────┐
                  │   Isolated Lab       │
                  │                      │
                  │ Vulnerable Web App   │
                  │ Server Logs          │
                  │ System Events        │
                  │ File Events          │
                  └──────────────────────┘
```

---

# 3. Architectural Principle

The platform must maintain a strict separation between:

```text
Target Lab
    │
    │ produces evidence
    ▼
Evidence Collection
    │
    ▼
Forensic Processing
    │
    ▼
Detection / Correlation
    │
    ▼
Analyst Interface
```

The forensic platform must **analyze evidence produced by the lab**, rather than directly modifying the target environment.

This separation improves:

- forensic integrity
- reproducibility
- debugging
- security
- modularity

---

# 4. Major Components

| Component | Responsibility | Primary Technology |
|---|---|---|
| Vulnerable Web Application | Controlled security-testing target | Python + Flask |
| Lab Runtime | Isolated execution environment | Docker Compose |
| Evidence Collector | Collect and stage supported evidence | Python |
| Log Parsers | Parse source-specific logs | Python |
| Event Normalizer | Convert raw events to common schema | Python + Pydantic |
| Forensic Engine | Analyze and correlate evidence | Python |
| Detection Engine | Rule-based security detection | Python |
| Timeline Engine | Build chronological attack timeline | Python |
| Evidence Store | Store metadata and structured events | PostgreSQL |
| Evidence Files | Preserve original artifacts | Local immutable evidence store |
| API | Backend interface | FastAPI |
| Analyst Dashboard | Investigation interface | React + TypeScript |
| Report Engine | Generate investigation reports | Python |
| Test Framework | Automated validation | Pytest |
| Infrastructure | Reproducible environment | Docker Compose |

---

# 5. Technology Stack

## 5.1 Recommended Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React | Mature component ecosystem |
| Frontend Language | TypeScript | Strong typing and maintainability |
| UI | Tailwind CSS | Consistent and fast UI development |
| Charts | Apache ECharts | Timelines, event visualization and dashboards |
| Backend API | FastAPI | Python-native, typed APIs and strong developer experience |
| Backend Language | Python 3.12+ | Excellent ecosystem for security, parsing and forensics |
| Validation | Pydantic | Strong data validation |
| ORM | SQLAlchemy | Mature relational database integration |
| Database | PostgreSQL | Reliable relational storage |
| Migration | Alembic | Controlled database schema evolution |
| Testing | Pytest | Backend/unit/integration testing |
| Frontend Testing | Vitest + React Testing Library | Component and UI testing |
| Containerization | Docker | Isolation and reproducibility |
| Orchestration | Docker Compose | Local multi-container laboratory |
| API Documentation | OpenAPI | Automatically generated API contract |
| Logging | Python structured logging | Consistent machine-readable logs |
| Configuration | Environment variables + `.env.example` | Environment-specific configuration |
| Version Control | Git | Source control and reproducibility |

---

# 6. Why Python Is the Primary Backend Language

Python is selected because the project's core logic involves:

- log parsing
- event normalization
- forensic analysis
- timestamp processing
- rule evaluation
- evidence correlation
- report generation
- security-oriented automation

Keeping these components in one primary language reduces unnecessary complexity.

The architecture should avoid creating multiple backend languages unless there is a demonstrated technical requirement.

---

# 7. Why FastAPI

FastAPI will provide the backend API boundary.

Responsibilities:

```text
Frontend
   ↓
FastAPI
   ↓
Application Services
   ↓
Forensic / Detection Engines
   ↓
Database / Evidence Store
```

FastAPI provides:

- typed request/response models
- automatic OpenAPI documentation
- asynchronous support where useful
- clean separation between routing and business logic
- strong Python ecosystem compatibility

The API layer must not contain forensic business logic directly.

---

# 8. Why PostgreSQL

PostgreSQL will store structured metadata and analysis results.

It should store:

- cases
- investigations
- normalized events
- alerts
- attack stages
- evidence metadata
- hashes
- findings
- reports
- users/analysts if authentication is implemented

Large original evidence artifacts should **not** be stored directly inside normal relational tables.

Instead:

```text
Original Evidence
      ↓
Evidence File Store
      ↓
Hash + Metadata
      ↓
PostgreSQL
```

This keeps database operations efficient while preserving evidence traceability.

---

# 9. Evidence Storage Architecture

Evidence handling must distinguish between:

### Original Evidence

The original collected artifact.

### Working Copy

A copy used for parsing and analysis.

### Derived Evidence

Results generated by the forensic engine.

Architecture:

```text
                 Evidence Acquisition
                         │
                         ▼
                ┌─────────────────┐
                │ Original Store  │
                └────────┬────────┘
                         │
                  SHA-256 Hash
                         │
                         ▼
                ┌─────────────────┐
                │ Evidence        │
                │ Metadata        │
                └────────┬────────┘
                         │
                         ▼
                  Working Copy
                         │
                         ▼
                  Parser Engine
                         │
                         ▼
                Normalized Events
                         │
                         ▼
                Detection/Analysis
```

The original artifact must remain unchanged.

---

# 10. Evidence Integrity

Each evidence artifact should have metadata similar to:

```json
{
  "evidence_id": "EV-000001",
  "source": "web-server",
  "filename": "access.log",
  "acquired_at": "2026-10-06T10:30:00Z",
  "sha256": "<hash>",
  "size_bytes": 123456,
  "media_type": "text/plain"
}
```

Required integrity fields:

| Field | Purpose |
|---|---|
| Evidence ID | Unique reference |
| Source | Where evidence originated |
| Filename | Original name |
| Acquisition time | Collection timestamp |
| SHA-256 | Integrity verification |
| Size | Artifact validation |
| MIME/media type | Artifact classification |
| Case ID | Investigation relationship |

---

# 11. Common Event Model

Different logs use different formats.

ForensiWeb therefore uses a normalized event schema.

Conceptually:

```text
Raw Evidence
     ↓
Parser
     ↓
Normalized Event
```

Example:

```json
{
  "event_id": "EVT-1001",
  "timestamp": "2026-10-06T10:31:22Z",
  "source": "web_access_log",
  "event_type": "http_request",
  "severity": "medium",
  "actor": {
    "ip": "LAB-CLIENT"
  },
  "target": {
    "service": "web"
  },
  "action": {
    "method": "GET",
    "path": "/document"
  },
  "attack_stage": "LFI",
  "evidence_id": "EV-000001"
}
```

The exact production schema must be defined in the implementation contracts and validated using Pydantic.

---

# 12. Event Lifecycle

Every event follows:

```text
RAW
 ↓
PARSED
 ↓
NORMALIZED
 ↓
VALIDATED
 ↓
CORRELATED
 ↓
CLASSIFIED
 ↓
DISPLAYED
```

An event must not be treated as a security finding merely because it was parsed successfully.

---

# 13. Forensic Processing Pipeline

```text
┌──────────────────────┐
│ Evidence Files       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Evidence Validation  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Source Detection     │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Parser               │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Event Normalization   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Validation            │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Detection Rules       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Event Correlation     │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Attack Timeline       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Findings / Alerts     │
└──────────────────────┘
```

---

# 14. Detection Architecture

The detection system must be modular.

```text
Normalized Events
       │
       ▼
┌────────────────────┐
│ Detection Manager  │
└─────────┬──────────┘
          │
     ┌────┼─────┬─────┐
     ▼    ▼     ▼     ▼
    R01  R02   R03   R04
     │    │     │     │
     └────┴─────┴─────┘
              │
              ▼
        Detection Result
```

Each rule should define:

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

Rules must be explainable.

---

# 15. Attack Stage Model

The project will use a controlled attack-stage taxonomy.

| Stage | Description |
|---|---|
| RECON | Initial probing or discovery |
| LFI | Local file inclusion/path-related activity |
| LOG_POISONING | Suspicious attacker-controlled content entering logs |
| RCE | Server-side execution anomaly |
| POST_EXPLOITATION | Shell/process activity following execution |
| PRIVILEGE_ESCALATION | Evidence indicating privilege transition |
| IMPACT | Resulting system/application impact |

The system must not infer an attack stage solely from a single weak indicator where correlation is required.

---

# 16. Correlation Engine

The correlation engine connects events based on:

- temporal proximity
- source
- session
- user
- process
- request
- evidence relationships
- attack-stage dependencies

Example:

```text
Event A
LFI-like request
     │
     │ temporal relationship
     ▼
Event B
Log anomaly
     │
     ▼
Event C
Process anomaly
     │
     ▼
Event D
Shell activity
     │
     ▼
Event E
Privilege anomaly
```

The result is an **Attack Sequence** rather than five unrelated alerts.

---

# 17. Timeline Architecture

The timeline engine consumes normalized and correlated events.

```text
Events
  ↓
Sort by normalized timestamp
  ↓
Resolve relationships
  ↓
Assign attack stages
  ↓
Generate timeline
  ↓
Expose to analyst
```

Timeline entries must reference their source evidence.

---

# 18. Report Architecture

```text
Investigation
      │
      ├── Case Metadata
      ├── Alerts
      ├── Timeline
      ├── Evidence
      ├── Findings
      └── Mitigations
              │
              ▼
        Report Generator
              │
              ▼
        Investigation Report
```

Reports must clearly distinguish:

- observed facts
- detected indicators
- analytical conclusions
- assumptions
- recommendations

The system must not present an inference as a confirmed fact.

---

# 19. Application Architecture

The backend follows a layered architecture.

```text
API / Routes
     ↓
Application Services
     ↓
Domain Logic
     ↓
Repositories
     ↓
Database / Evidence Store
```

### API Layer

Handles:

- HTTP requests
- authentication
- request validation
- response formatting

### Application Layer

Handles use cases:

- create investigation
- ingest evidence
- analyze evidence
- run detection
- generate report

### Domain Layer

Contains core security/forensic logic.

### Repository Layer

Handles persistence.

This prevents database code from being mixed with detection logic.

---

# 20. Frontend Architecture

Frontend structure:

```text
React Application
      │
      ├── Pages
      ├── Components
      ├── Hooks
      ├── API Client
      ├── State
      └── Types
```

Main screens:

| Screen | Purpose |
|---|---|
| Dashboard | Overall investigation status |
| Cases | Investigation management |
| Evidence | Evidence inventory |
| Events | Normalized event explorer |
| Alerts | Security findings |
| Timeline | Attack reconstruction |
| Investigation | Detailed analysis |
| Reports | Report generation/view |
| Lab | Controlled experiment status |
| Settings | Configuration |

---

# 21. Recommended UI Structure

```text
ForensiWeb
│
├── Dashboard
│
├── Investigations
│   ├── Overview
│   ├── Evidence
│   ├── Events
│   ├── Alerts
│   ├── Timeline
│   └── Findings
│
├── Laboratory
│   ├── Environment Status
│   ├── Scenario Status
│   └── Reset / Validation
│
└── Reports
```

The interface should prioritize investigative clarity over decorative elements.

---

# 22. Laboratory Architecture

The lab should be isolated from the forensic platform as much as practical.

Recommended conceptual deployment:

```text
                     Docker Network
                  "forensiweb-lab"
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
    ┌────────────────┐      ┌────────────────┐
    │ Vulnerable Web │      │ Lab Services   │
    │ Application    │      │ / Logging      │
    └────────────────┘      └────────────────┘

                     Controlled
                     Evidence Flow
                          │
                          ▼

                ┌─────────────────────┐
                │ ForensiWeb Platform │
                └─────────────────────┘
```

The vulnerable environment must never be exposed publicly by default.

---

# 23. Deployment Model

Development deployment:

```text
Docker Compose
    │
    ├── frontend
    ├── api
    ├── postgres
    ├── vulnerable-app
    └── lab-support services
```

The final implementation should allow the entire project to be started using a documented command sequence.

Example target experience:

```bash
docker compose up -d
```

The exact command may change during implementation, but reproducible startup is mandatory.

---

# 24. Network Isolation

The laboratory should use dedicated Docker networks.

Conceptually:

```text
                Host Machine
                     │
        ┌────────────┴────────────┐
        │                         │
   Lab Network              Management Network
        │                         │
   Vulnerable App            Forensic API
   Lab Services              Database
```

The vulnerable application should not have unrestricted outbound internet connectivity.

---

# 25. Database Architecture

Primary entities:

```text
Case
 │
 ├── Evidence
 │
 ├── Events
 │
 ├── Alerts
 │
 ├── Timeline Entries
 │
 ├── Findings
 │
 └── Reports
```

Conceptual relationships:

```text
Case 1 ──── N Evidence
Case 1 ──── N Event
Case 1 ──── N Alert
Case 1 ──── N Finding

Evidence 1 ──── N Event
Event N ─────── N Alert
Event N ─────── N TimelineEntry
```

Database migrations must be version controlled.

---

# 26. Proposed Database Tables

| Table | Purpose |
|---|---|
| `cases` | Investigation/case metadata |
| `evidence` | Evidence artifact metadata |
| `events` | Normalized forensic events |
| `detections` | Detection results |
| `timeline_entries` | Correlated attack timeline |
| `findings` | Analyst findings |
| `reports` | Generated report metadata |
| `users` | Analyst identities if authentication is implemented |
| `audit_logs` | Platform activity audit trail |

---

# 27. Folder Structure

The repository should follow this structure:

```text
forensiweb/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   ├── threat-model.md
│   ├── forensic-model.md
│   ├── implementation-plan.md
│   └── testing-strategy.md
│
├── apps/
│   │
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── layouts/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   ├── utils/
│   │   │   └── main.tsx
│   │   ├── public/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── routes/
│   │   │   │   └── dependencies.py
│   │   │   ├── core/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── main.py
│   │   │
│   │   ├── tests/
│   │   ├── alembic/
│   │   └── pyproject.toml
│   │
│   └── vulnerable-web-app/
│       ├── app/
│       │   ├── routes/
│       │   ├── services/
│       │   ├── templates/
│       │   ├── static/
│       │   └── main.py
│       ├── tests/
│       ├── Dockerfile
│       └── pyproject.toml
│
├── packages/
│   │
│   ├── forensic-engine/
│   │   ├── parsers/
│   │   ├── normalization/
│   │   ├── correlation/
│   │   ├── timeline/
│   │   ├── evidence/
│   │   └── tests/
│   │
│   ├── detection-engine/
│   │   ├── rules/
│   │   ├── models/
│   │   ├── evaluator/
│   │   └── tests/
│   │
│   └── report-engine/
│       ├── templates/
│       ├── generators/
│       └── tests/
│
├── lab/
│   ├── docker/
│   ├── scenarios/
│   ├── fixtures/
│   ├── sample-evidence/
│   ├── scripts/
│   └── reset/
│
├── data/
│   ├── evidence/
│   │   ├── original/
│   │   ├── working/
│   │   └── derived/
│   └── reports/
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   ├── fixtures/
│   └── regression/
│
└── scripts/
    ├── setup/
    ├── development/
    ├── testing/
    └── deployment/
```

---

# 28. Folder Responsibility Rules

| Directory | Rule |
|---|---|
| `apps/frontend` | UI only |
| `apps/api` | HTTP/API orchestration |
| `apps/vulnerable-web-app` | Deliberately vulnerable lab target |
| `packages/forensic-engine` | Evidence processing and forensic logic |
| `packages/detection-engine` | Detection and correlation rules |
| `packages/report-engine` | Report generation |
| `lab` | Laboratory scenarios and fixtures |
| `data/evidence/original` | Immutable original evidence |
| `data/evidence/working` | Analysis copies |
| `data/evidence/derived` | Generated artifacts |
| `tests` | Cross-component/integration tests |
| `docs` | Project documentation |

---

# 29. Dependency Direction

Dependencies must move inward toward domain logic.

Preferred:

```text
Frontend
   ↓
API
   ↓
Application Services
   ↓
Domain/Forensic Packages
   ↓
Repositories
   ↓
Infrastructure
```

Avoid:

```text
Forensic Engine
      ↓
Frontend
```

The forensic engine must remain independent of the UI.

---

# 30. API Design

The API should be REST-oriented.

Example endpoint groups:

```text
/api/v1/cases
/api/v1/evidence
/api/v1/events
/api/v1/detections
/api/v1/timeline
/api/v1/findings
/api/v1/reports
/api/v1/lab
```

Example operations:

| Endpoint | Purpose |
|---|---|
| `GET /cases` | List investigations |
| `POST /cases` | Create investigation |
| `GET /cases/{id}` | Case details |
| `POST /evidence` | Register/import evidence |
| `GET /evidence/{id}` | Evidence metadata |
| `POST /analysis` | Start analysis |
| `GET /events` | Search normalized events |
| `GET /detections` | Retrieve alerts |
| `GET /timeline/{case_id}` | Retrieve attack timeline |
| `POST /reports` | Generate report |

All APIs must use versioning.

---

# 31. Error Handling

Errors must be structured.

Example:

```json
{
  "error": {
    "code": "EVIDENCE_HASH_MISMATCH",
    "message": "Evidence integrity verification failed.",
    "request_id": "REQ-12345"
  }
}
```

The system must never hide processing failures.

If evidence cannot be parsed:

```text
Parsing Failed
     ↓
Visible Error
     ↓
Evidence Remains Preserved
```

---

# 32. Configuration Management

Configuration must not be hardcoded.

Use:

```text
.env
.env.example
```

Sensitive values must never be committed to Git.

Configuration categories:

```text
Application
Database
Evidence Storage
Security
Lab
Logging
```

The `.env.example` file must contain safe placeholder values only.

---

# 33. Logging Architecture

ForensiWeb itself must produce structured logs.

Application logs should contain:

```text
timestamp
level
service
event
request_id
case_id (when applicable)
error_code (when applicable)
```

Example:

```json
{
  "timestamp": "2026-10-06T10:30:00Z",
  "level": "INFO",
  "service": "forensic-api",
  "event": "analysis_started",
  "case_id": "CASE-001"
}
```

Do not log secrets, credentials, or unnecessary sensitive information.

---

# 34. Time and Timestamp Standard

All internal timestamps should use:

> **UTC + ISO 8601**

Example:

```text
2026-10-06T10:31:22Z
```

The UI may display local time, but stored event timestamps must remain normalized.

This is critical for reliable timeline correlation.

---

# 35. Authentication and Authorization

If analyst authentication is implemented:

```text
User
 ↓
Authentication
 ↓
Authorization
 ↓
Case Access
```

The system should use role-based access where appropriate.

Initial roles may be:

| Role | Capability |
|---|---|
| Analyst | Investigate cases |
| Administrator | Manage system |
| Viewer | Read-only access |

Authentication must never be implemented by storing plaintext passwords.

---

# 36. Security Boundaries

The major trust boundaries are:

```text
┌─────────────────────┐
│ Untrusted Lab Input │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Vulnerable Web App  │
└──────────┬──────────┘
           │
           │ Evidence
           ▼
┌─────────────────────┐
│ Evidence Boundary   │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Forensic Platform   │
└─────────────────────┘
```

The vulnerable target must not be treated as trusted infrastructure.

---

# 37. Reliability Architecture

Reliability mechanisms include:

### Input Validation

Every structured event must be validated.

### Evidence Integrity

Hashes must be verified.

### Idempotent Processing

Reprocessing the same evidence should not silently duplicate events.

### Deterministic Rules

Detection rules should produce consistent results for identical input.

### Failure Visibility

Errors must be surfaced.

### Auditability

Important analyst actions should be auditable.

### Reproducibility

Lab state must be resettable.

---

# 38. Testing Architecture

Testing must occur at multiple levels.

```text
Unit Tests
    ↓
Integration Tests
    ↓
End-to-End Tests
    ↓
Lab Reproduction Tests
    ↓
Regression Tests
```

### Unit Tests

Test:

- parsers
- validators
- detection rules
- correlation logic
- timeline generation

### Integration Tests

Test:

- API + database
- evidence ingestion
- analysis pipeline

### End-to-End Tests

Test:

```text
Evidence
 ↓
API
 ↓
Forensic Engine
 ↓
Detection
 ↓
Timeline
 ↓
Dashboard
```

### Lab Tests

Verify that the controlled scenario generates expected evidence.

---

# 39. Reproducibility Architecture

A complete experiment should be reproducible from:

```text
Git Repository
      +
Docker Configuration
      +
Scenario Definition
      +
Fixtures
      +
Expected Results
```

The project should document:

```text
1. Start environment
2. Verify services
3. Execute approved lab scenario
4. Collect evidence
5. Run analysis
6. Review results
7. Reset environment
```

---

# 40. Scenario Definition

Attack scenarios should be stored as version-controlled definitions rather than hidden inside application code.

Conceptually:

```yaml
scenario:
  id: "WEB-CHAIN-001"
  name: "Controlled LFI-to-Privilege-Escalation Investigation"

stages:
  - id: "S1"
    name: "LFI"
  - id: "S2"
    name: "Log Poisoning"
  - id: "S3"
    name: "RCE"
  - id: "S4"
    name: "Post-Exploitation"
  - id: "S5"
    name: "Privilege Escalation"
```

The exact schema will be finalized during implementation.

---

# 41. Data Flow

## 41.1 Normal Application Flow

```text
Browser
   ↓
Frontend
   ↓
FastAPI
   ↓
Service Layer
   ↓
Database
```

## 41.2 Evidence Flow

```text
Lab
 ↓
Evidence
 ↓
Evidence Store
 ↓
Parser
 ↓
Normalizer
 ↓
Detection
 ↓
Correlation
 ↓
Timeline
 ↓
Dashboard
```

## 41.3 Investigation Flow

```text
Analyst
 ↓
Case
 ↓
Evidence
 ↓
Events
 ↓
Alert
 ↓
Related Events
 ↓
Attack Timeline
 ↓
Finding
 ↓
Report
```

---

# 42. Performance Requirements

Initial project scale is intentionally modest.

The system should prioritize correctness over high-throughput distributed processing.

Target principles:

- responsive dashboard
- efficient pagination
- indexed database queries
- streaming/iterative parsing where appropriate
- no loading of unnecessarily large evidence files entirely into memory
- background processing for expensive analysis tasks

Large-scale distributed processing is out of scope unless testing demonstrates a real requirement.

---

# 43. Scalability Strategy

The architecture should remain extensible.

Future evidence sources should be addable through:

```text
New Evidence Source
       ↓
New Parser
       ↓
Common Event Model
       ↓
Existing Detection Engine
```

The core forensic engine should not need to be rewritten for every new evidence source.

---

# 44. Extensibility

Future modules may include:

- additional web log parsers
- authentication-event analysis
- Windows event analysis
- Linux audit analysis
- network-flow analysis
- additional attack scenarios
- additional detection rules
- advanced visualization
- threat-intelligence enrichment

These must remain optional extensions and must not destabilize the core project.

---

# 45. Observability

The platform should expose operational health information:

```text
API Status
Database Status
Evidence Store Status
Lab Status
Analysis Queue Status
```

A health endpoint should provide basic service availability information.

---

# 46. Backup and Recovery

The project should distinguish between:

### Source Code

Stored in Git.

### Database

Can be backed up using PostgreSQL backup mechanisms.

### Original Evidence

Must be preserved independently of derived analysis results.

### Generated Reports

Should be reproducible from case data where possible.

---

# 47. Development Environment

Recommended development tools:

| Tool | Purpose |
|---|---|
| Git | Version control |
| Docker Desktop / Docker Engine | Containers |
| Python 3.12+ | Backend |
| Node.js LTS | Frontend |
| PostgreSQL | Database |
| VS Code / Antigravity IDE | Development |
| Pytest | Backend testing |
| Vitest | Frontend testing |

The project should avoid dependency on a developer-specific machine configuration.

---

# 48. CI/CD Quality Gates

If CI is configured, every change should ideally pass:

```text
Lint
 ↓
Type Check
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
Build
```

Security-sensitive changes should receive additional review.

A failed test must block release/build where practical.

---

# 49. Architecture Decision Records

Major architectural decisions should be documented.

Example:

```text
ADR-001 — Why FastAPI?
ADR-002 — Why PostgreSQL?
ADR-003 — Why Docker-based isolation?
ADR-004 — Why a normalized event model?
ADR-005 — Why original evidence is stored outside the database?
```

This improves academic credibility and long-term maintainability.

---

# 50. Architecture Quality Principles

Every implementation decision should be evaluated against:

| Principle | Question |
|---|---|
| Security | Does this reduce unnecessary attack surface? |
| Isolation | Can the vulnerable lab affect the host/system? |
| Integrity | Can evidence be modified silently? |
| Reliability | Will the same input produce consistent results? |
| Explainability | Can an analyst understand the result? |
| Testability | Can this component be tested independently? |
| Maintainability | Can another developer understand it? |
| Reproducibility | Can the experiment be repeated? |
| Modularity | Can components be replaced independently? |

---

# 51. Recommended Implementation Order

The architecture should be implemented incrementally.

```text
Phase 1
Repository + Docker + Documentation
        ↓
Phase 2
Database + API foundation
        ↓
Phase 3
Vulnerable Web Application
        ↓
Phase 4
Evidence Collection
        ↓
Phase 5
Event Normalization
        ↓
Phase 6
Detection Engine
        ↓
Phase 7
Correlation + Timeline
        ↓
Phase 8
Frontend Dashboard
        ↓
Phase 9
Reports
        ↓
Phase 10
Hardening + Reproducibility + Testing
```

Do not implement all components simultaneously.

---

# 52. Definition of Done for Architecture

The architecture is considered implemented when:

- all major components have clear boundaries
- component responsibilities are documented
- communication paths are defined
- database entities are defined
- evidence lifecycle is defined
- normalized event model is defined
- folder structure is established
- Docker environment is reproducible
- API contracts are documented
- security boundaries are implemented
- automated tests exist for critical logic
- lab and forensic platform are appropriately isolated

---

# 53. Final Architecture

The final conceptual architecture is:

```text
                         ┌─────────────────────┐
                         │       ANALYST       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ React + TypeScript  │
                         │ Investigation UI    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │  Forensic    │      │  Detection   │      │   Report     │
      │   Engine     │      │    Engine    │      │   Engine     │
      └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │    PostgreSQL       │
                         │ Structured Metadata │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  Evidence Storage   │
                         │ Original / Working  │
                         │ / Derived Artifacts │
                         └──────────┬──────────┘
                                    ▲
                                    │
                         Controlled Evidence
                                    │
                  ┌─────────────────┴─────────────────┐
                  │        ISOLATED LAB               │
                  │                                   │
                  │  ┌─────────────────────────────┐  │
                  │  │ Deliberately Vulnerable     │  │
                  │  │ Web Application             │  │
                  │  └──────────────┬──────────────┘  │
                  │                 │                 │
                  │                 ▼                 │
                  │       Logs / System Events        │
                  │                 │                 │
                  └─────────────────┴─────────────────┘
```

---

# 54. Architectural Summary

ForensiWeb is intentionally designed as a **security research and forensic platform**, not as a generic web application.

Its architecture is centered around:

```text
                  CONTROLLED LAB
                       │
                       ▼
                 ATTACK ACTIVITY
                       │
                       ▼
                 DIGITAL EVIDENCE
                       │
                       ▼
              FORENSIC PROCESSING
                       │
                       ▼
                EVENT CORRELATION
                       │
                       ▼
                ATTACK TIMELINE
                       │
                       ▼
                  DETECTION
                       │
                       ▼
                 INVESTIGATION
                       │
                       ▼
                  MITIGATION
                       │
                       ▼
                  VERIFICATION
```

The most important architectural principle is:

> **Every security conclusion must be traceable to evidence, every major component must be independently testable, and the complete laboratory experiment must be reproducible.**