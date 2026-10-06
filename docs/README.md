# ForensiWeb — Documentation Index & Governance Guide

**Document:** `docs/README.md`  
**Status:** Approved Master Index  
**Version:** 1.0  
**Project:** ForensiWeb  
**Authority:** Documentation Governance & Architecture Source of Truth  

---

## 1. Documentation Overview

Welcome to the documentation repository for **ForensiWeb**, an academic cybersecurity and digital-forensics platform studying:

> **“Forensic Analysis of Log Poisoning and Environment Variable Manipulation in Web Applications.”**

The documents in this directory define the product requirements, system architecture, engineering rules, UI/UX design, security boundaries, forensic principles, implementation schedule, and testing strategies.

---

## 2. Document Hierarchy & Authority Matrix

When instructions or requirements appear to conflict, developers and AI coding agents must apply this strict hierarchy of authority:

| Priority | Authority Area | Source-of-Truth Document | Description |
|---|---|---|---|
| **1 (Highest)** | Safety & Lab Isolation | [`threat-model.md`](threat-model.md), [`rules.md`](rules.md) | Safety guardrails, non-weaponization, container isolation, no public egress. |
| **2 (Very High)** | Evidence Integrity | [`forensic-model.md`](forensic-model.md), [`rules.md`](rules.md) | Cryptographic SHA-256 verification, immutability, auditability, provenance. |
| **3** | Product Scope & Goals | [`PRD.md`](PRD.md) | What ForensiWeb is, why it exists, target scenarios, academic goals. |
| **4** | Technical Architecture | [`architecture.md`](architecture.md) | Component boundaries, technology choices, folder structure, data models. |
| **5** | Engineering Rules | [`rules.md`](rules.md) | Mandatory AI/developer rules, minimal change principle, commit hygiene. |
| **6** | User Experience | [`design.md`](design.md) | Design tokens, color system, component patterns, layout rules. |
| **7** | Quality Assurance | [`testing-strategy.md`](testing-strategy.md) | Test pyramid, test coverage requirements, negative testing standards. |
| **8** | Implementation Roadmap | [`implementation-plan.md`](implementation-plan.md) | Macro milestone plan, phase dependencies, phase-gate model. |
| **9** | Execution Tracking | [`task.md`](task.md) | Operational task lists, feature status tracking, active work focus. |

---

## 3. Documentation Catalog

```text
docs/
├── README.md                 # This index and governance guide
├── PRD.md                    # Product Requirements Document
├── architecture.md           # System Architecture & Technical Design
├── rules.md                  # Development Rulebook & AI Operational Guardrails
├── design.md                 # UI/UX Specification & Design System
├── threat-model.md           # Threat Model, STRIDE Matrix & Security Boundaries
├── forensic-model.md         # Digital Forensic Model & Common Event Schema
├── implementation-plan.md    # Phased Implementation Plan & Macro Milestones
├── testing-strategy.md       # Comprehensive Testing & Verification Strategy
├── task.md                   # Active Granular Phase/Feature Tracking & Checklist
└── adr/                      # Architecture Decision Records
    └── README.md             # ADR Process Guide & Decision Index
```

### 3.1 Document Descriptions

#### [`PRD.md`](PRD.md) (Product Requirements Document)
- **Authority:** Product Scope & Academic Objectives.
- **Content:** Defines the 6-stage attack chain (LFI -> Log Poisoning -> RCE -> Web Shell -> PATH Misconfiguration -> Privilege Escalation), product goals, target audience, non-goals, and evaluation criteria.

#### [`architecture.md`](architecture.md) (System Architecture)
- **Authority:** System Structure & Technical Architecture.
- **Content:** Defines components (`apps/frontend`, `apps/api`, `apps/vulnerable-web-app`, `packages/*`), technology stack (FastAPI, React, PostgreSQL, Docker), folder responsibilities, and data flows.

#### [`rules.md`](rules.md) (Development Rulebook)
- **Authority:** Engineering Constraints & Coding Guidelines.
- **Content:** Strict instructions for developers and AI coding agents: minimal change principle, one phase at a time, zero committed secrets, evidence immutability, and git hygiene.

#### [`design.md`](design.md) (UI/UX Specification)
- **Authority:** User Interface & Design System.
- **Content:** Design tokens (dark mode cybersecurity aesthetic, typography, colors, borders, spacing), application shell layout, reusable components, and accessibility guidelines.

#### [`threat-model.md`](threat-model.md) (Threat Model & Security Boundaries)
- **Authority:** Security & Laboratory Isolation.
- **Content:** Asset identification, threat actors, STRIDE analysis, Docker network isolation (`internal: true`), dropped capabilities, and defense against weaponization.

#### [`forensic-model.md`](forensic-model.md) (Forensic Model & Evidence Representation)
- **Authority:** Digital Forensics, Evidence Integrity & Analytics.
- **Content:** Evidence lifecycle (Acquisition -> Hashing -> Ingestion -> Normalization -> Detection -> Correlation -> Timeline -> Report), Common Event Model (CEM) schema, correlation ontology, and chain of custody.

#### [`implementation-plan.md`](implementation-plan.md) (Phased Implementation Plan)
- **Authority:** Macro Implementation Milestones.
- **Content:** 20-phase pipeline, dependency order, phase-gate criteria, and feature implementation lifecycle.

#### [`testing-strategy.md`](testing-strategy.md) (Testing Strategy)
- **Authority:** Quality Assurance & Correctness Verification.
- **Content:** Testing pyramid (unit, integration, lab, E2E), negative test patterns (malformed logs, corrupt hashes), test conventions, and quality gates.

#### [`task.md`](task.md) (Active Task Plan)
- **Authority:** Execution Schedule & Status Tracking.
- **Content:** Real-time status tracker, granular feature definitions, acceptance criteria, and completion checklists.

#### [`adr/README.md`](adr/README.md) (Architecture Decision Records)
- **Authority:** Architecture History & Technical Rationale.
- **Content:** Index of major architectural choices (ADR-001 through ADR-005) and standardized template for future decisions.

---

## 4. Documentation Synchronization Rules

1. **Keep Code and Docs Aligned:** Whenever code implementation changes (APIs, schemas, environment variables, directories), the affected documentation must be updated in the same change set.
2. **Never Create Conflicting Guidance:** If a conflict arises between two documents, refer to the Authority Matrix in Section 2 above to resolve it.
3. **No Phantom Architecture:** Documentation must never describe an architecture that has been deprecated or abandoned.
4. **Preserve Academic Tone:** Documentation must maintain professional, academically rigorous cybersecurity and digital forensics terminology.
