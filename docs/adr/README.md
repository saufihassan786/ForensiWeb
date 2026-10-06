# Architecture Decision Records (ADRs)

**Directory:** `docs/adr/`  
**Purpose:** Record significant architectural, technical, and forensic design decisions for ForensiWeb.  
**Authority:** System Architecture & Long-Term Maintainability  

---

## 1. What is an ADR?

An Architecture Decision Record (ADR) is a lightweight document capturing an important architectural choice made in ForensiWeb, along with its context, considered alternatives, and consequences.

ADRs preserve academic context and design rationale, explaining **why** the system is built a certain way to future researchers, evaluators, and developers.

---

## 2. ADR Structure & Template

Every ADR must follow this standard format:

```markdown
# ADR-XXX: [Short Decision Title]

**Status:** [Proposed | Accepted | Superseded | Deprecated]  
**Date:** YYYY-MM-DD  
**Deciders:** [Architecture Team / AI Coding Agent]  
**Context Phase:** [PHASE-XX]  

### 1. Context & Problem Statement
What technical, forensic, or security challenge are we solving? What constraints exist?

### 2. Decision
What architecture, framework, pattern, or data model did we choose?

### 3. Rationale & Alternatives Considered
Why did we choose this over alternatives?
- Alternative A: Pros and cons.
- Alternative B: Pros and cons.

### 4. Consequences
What are the trade-offs, positive benefits, and obligations of this decision?
- Positive: ...
- Negative / Costs: ...

### 5. Compliance & Verification
How is this decision verified in code and tests?
```

---

## 3. ADR Index

| ADR ID | Title | Status | Primary Rationale |
|---|---|---|---|
| **ADR-001** | Python & FastAPI for Core Backend | Accepted | Native forensic tool ecosystem, Pydantic type safety, async HTTP, auto OpenAPI documentation. |
| **ADR-002** | PostgreSQL for Relational Case & Event Metadata | Accepted | ACID compliance, JSONB support for unstructured log details, indexed queries. |
| **ADR-003** | Docker-Based Isolated Laboratory Network | Accepted | Reproducibility, strict non-egress network isolation (`internal: true`), safe scenario replay. |
| **ADR-004** | Common Event Model (CEM) for Normalization | Accepted | Decouples heterogeneous log sources from detection rules; enables multi-source correlation. |
| **ADR-005** | File-Based Storage for Original Raw Evidence | Accepted | Preserves raw byte immutability and file system forensics; prevents database bloat. |
