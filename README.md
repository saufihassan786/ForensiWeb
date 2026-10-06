# ForensiWeb

> **Forensic Analysis of Log Poisoning and Environment Variable Manipulation in Web Applications**

ForensiWeb is an academic cybersecurity research and digital-forensics platform designed to reproduce, observe, detect, correlate, and investigate a multi-stage web application attack chain within a strictly controlled and isolated laboratory environment.

---

## 1. Project Overview

ForensiWeb demonstrates the complete digital forensic lifecycle for a chained web attack:
1. **Reconnaissance & LFI / Path Traversal**
2. **Log Poisoning**
3. **Remote Code Execution (RCE)**
4. **Post-Exploitation & Web Shell Activity**
5. **Environment / PATH Misconfiguration**
6. **Privilege Escalation**

The platform emphasizes evidence preservation, event normalization, detection rules, multi-source event correlation, timeline reconstruction, explainable forensic findings, and mitigation verification.

---

## 2. Repository Structure

The repository adheres to the architecture defined in [`docs/architecture.md`](docs/architecture.md):

```text
forensiweb/
├── README.md
├── docs/                      # Core specification & architecture documents
├── apps/
│   ├── frontend/              # Analyst investigation dashboard (React + TypeScript)
│   ├── api/                   # Backend orchestration API (FastAPI)
│   └── vulnerable-web-app/    # Controlled vulnerable laboratory target (Flask)
├── packages/
│   ├── forensic-engine/       # Evidence parsing, normalization, correlation, timeline
│   ├── detection-engine/      # Detection rules and correlation evaluator
│   └── report-engine/         # Forensic reporting and export engine
├── lab/                       # Docker environments, scenarios, and lab fixtures
├── data/                      # Evidence storage (original, working, derived) and reports
├── tests/                     # Integration, E2E, fixtures, and regression tests
└── scripts/                   # Setup, development, testing, and deployment scripts
```

---

## 3. Project Documentation

Project source-of-truth documents are located in `docs/`:

- [`PRD.md`](docs/PRD.md): Product Requirements Document
- [`architecture.md`](docs/architecture.md): System Architecture & Technical Design
- [`design.md`](docs/design.md): UI/UX Design System
- [`rules.md`](docs/rules.md): AI Development & Engineering Rules
- [`task.md`](docs/task.md): Implementation Roadmap & Task Management
