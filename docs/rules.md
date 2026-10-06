# ForensiWeb — AI Development & Project Rules

**File:** `rules.md`
**Status:** Mandatory Project Rulebook
**Version:** 1.0
**Project:** ForensiWeb
**Primary AI IDE:** Antigravity IDE

---

# 1. Purpose

This document is the **official development rulebook for ForensiWeb**.

Every developer, AI coding agent, automation, or contributor working on this project must follow these rules.

The purpose of this file is to ensure that AI-assisted development remains:

* consistent;
* secure;
* predictable;
* maintainable;
* testable;
* reproducible;
* aligned with the PRD;
* aligned with the architecture;
* respectful of forensic evidence integrity;
* resistant to unnecessary scope expansion.

> **Important:** `rules.md` defines **HOW development must be performed**.
> `prd.md` defines **WHAT and WHY**.
> `architecture.md` defines **HOW THE SYSTEM IS STRUCTURED**.

---

# 2. Rule Hierarchy

When two instructions appear to conflict, use this priority order:

| Priority | Rule Source                                 | Authority            |
| -------: | ------------------------------------------- | -------------------- |
|        1 | Safety and laboratory isolation             | Highest              |
|        2 | Evidence integrity and forensic correctness | Very High            |
|        3 | `prd.md`                                    | Product scope        |
|        4 | `architecture.md`                           | System architecture  |
|        5 | `rules.md`                                  | Development behavior |
|        6 | Testing and quality requirements            | High                 |
|        7 | UI/UX and implementation preferences        | Normal               |
|        8 | Convenience or speed                        | Lowest               |

Never sacrifice a higher-priority rule merely to make implementation easier or faster.

---

# 3. Source-of-Truth Documents

Before making significant changes, the AI agent must understand the relevant project documentation.

Primary documentation:

```text
docs/
├── prd.md
├── architecture.md
├── rules.md
├── design.md
├── forensic-model.md
├── threat-model.md
├── implementation-plan.md
└── testing-strategy.md
```

The exact set of documents may evolve, but the agent must always check the currently relevant documentation before making architectural or cross-component changes.

---

# 4. Before Coding

## 4.1 Mandatory Pre-Coding Process

Before implementing a feature or making a significant change:

1. Read the relevant documentation.
2. Understand the requested behavior.
3. Inspect the existing implementation.
4. Identify reusable components.
5. Identify affected files.
6. Check existing tests.
7. Check architectural boundaries.
8. Determine whether the change affects security or forensic integrity.
9. Create an implementation plan for large changes.
10. Only then modify the code.

---

## 4.2 Do Not Code From Assumptions

The AI agent must not assume that:

* a file exists;
* an API exists;
* a database table exists;
* a component exists;
* a package is installed;
* a feature is already implemented;
* a particular architecture is being used.

Inspect the repository first.

---

# 5. Existing Code First

Before creating new functionality:

```text
Search
  ↓
Understand
  ↓
Reuse
  ↓
Extend
  ↓
Create new code only if necessary
```

### Rules

* Reuse existing utilities.
* Reuse existing components.
* Reuse existing services.
* Reuse existing schemas.
* Reuse existing validation.
* Reuse existing API patterns.
* Avoid duplicate implementations.

Do not create a second implementation of functionality that already exists.

---

# 6. Minimal Change Principle

Every change must be as small and focused as reasonably possible.

### Preferred

```text
Requested feature
      ↓
Required files
      ↓
Required implementation
      ↓
Required tests
```

### Avoid

```text
Requested feature
      ↓
Refactor entire project
      ↓
Rename unrelated files
      ↓
Change architecture
      ↓
Change dependencies
      ↓
Modify unrelated UI
```

> **Do not modify unrelated files merely because they can be improved.**

---

# 7. Scope Control

The AI must not continuously expand the project.

If a requested feature suggests additional functionality, classify it as:

| Category                     | Action                         |
| ---------------------------- | ------------------------------ |
| Required for current feature | Implement                      |
| Required for security        | Implement                      |
| Required for correctness     | Implement                      |
| Small supporting change      | Implement if justified         |
| Useful future feature        | Document as future work        |
| Unrelated improvement        | Do not implement               |
| Architecture-changing idea   | Ask/plan before implementation |

---

# 8. Product Scope Rules

The primary objective remains:

```text
Controlled Lab
      ↓
Attack Simulation
      ↓
Evidence Collection
      ↓
Forensic Processing
      ↓
Detection
      ↓
Correlation
      ↓
Attack Timeline
      ↓
Investigation
      ↓
Mitigation
      ↓
Verification
```

The project must not drift into an unrelated product.

Do not add unrelated:

* social features;
* payment systems;
* mobile applications;
* generic chatbots;
* entertainment features;
* unnecessary AI features;
* unrelated SaaS functionality.

---

# 9. AI Agent Behavior

Antigravity IDE or another AI coding agent must behave as a **repository-aware engineering assistant**, not as an autonomous project redesign system.

The agent must:

* inspect before modifying;
* preserve existing architecture;
* explain significant decisions;
* minimize unnecessary changes;
* maintain tests;
* maintain documentation;
* respect security boundaries;
* avoid speculative features.

The agent must not silently redesign the project.

---

# 10. Architecture Rules

The architecture defined in `architecture.md` must be respected.

Primary dependency direction:

```text
Frontend
   ↓
API
   ↓
Application Services
   ↓
Domain / Forensic / Detection Logic
   ↓
Repositories
   ↓
Infrastructure
```

---

## 10.1 Frontend Rules

Frontend code must:

* focus on presentation;
* communicate through defined API interfaces;
* avoid direct database access;
* avoid embedding forensic business logic;
* reuse shared components;
* use shared types where appropriate;
* handle loading, error, and empty states.

### Forbidden

```text
React Component
      ↓
Direct PostgreSQL Query
```

### Preferred

```text
React Component
      ↓
API Client
      ↓
FastAPI
      ↓
Service
      ↓
Repository
      ↓
Database
```

---

# 11. Backend Rules

The API layer must not become a container for all business logic.

Use:

```text
Route
 ↓
Service
 ↓
Domain Logic
 ↓
Repository
```

Routes should primarily handle:

* HTTP input;
* validation;
* authentication/authorization;
* service invocation;
* HTTP response formatting.

Complex forensic or detection logic must not be placed directly inside route handlers.

---

# 12. Forensic Engine Rules

The forensic engine is a core project component.

It must remain independent from:

* React;
* UI-specific state;
* browser code;
* presentation logic.

The forensic engine should operate on structured inputs and produce structured outputs.

Example:

```text
Raw Evidence
     ↓
Parser
     ↓
Normalized Event
     ↓
Validation
     ↓
Correlation
     ↓
Forensic Finding
```

---

# 13. Detection Rules

Detection logic must be:

* modular;
* explainable;
* testable;
* deterministic where possible;
* traceable to evidence.

Every important detection rule should define:

| Field               | Required |
| ------------------- | -------- |
| Rule ID             | Yes      |
| Rule Name           | Yes      |
| Description         | Yes      |
| Input Event Types   | Yes      |
| Conditions          | Yes      |
| Severity            | Yes      |
| Attack Stage        | Yes      |
| Explanation         | Yes      |
| Evidence References | Yes      |
| Test Cases          | Yes      |

A detection result must explain **why it was triggered**.

---

# 14. No Black-Box Security Conclusions

The system must not make unsupported statements such as:

```text
"Attacker definitely obtained root access."
```

when the evidence only shows:

```text
"Suspicious privileged process execution was observed."
```

Forensic conclusions must distinguish between:

### Observed Fact

Directly supported by evidence.

### Detected Indicator

A rule identified suspicious behavior.

### Analytical Conclusion

A conclusion derived from multiple pieces of evidence.

### Assumption

Something that cannot currently be verified.

### Recommendation

A proposed defensive action.

Never present an assumption as a confirmed fact.

---

# 15. Evidence Integrity Rules

Evidence is one of the most important assets of the project.

## Mandatory Rules

* Original evidence must never be modified.
* Original evidence must be preserved.
* Evidence must have a unique identifier.
* Evidence metadata must be recorded.
* SHA-256 hashing should be used for integrity verification.
* Working copies must be separated from originals.
* Derived evidence must be clearly identified.
* Evidence processing must be traceable.

---

## 15.1 Evidence Lifecycle

```text
ACQUIRED
   ↓
HASHED
   ↓
VALIDATED
   ↓
PRESERVED
   ↓
WORKING COPY
   ↓
PARSED
   ↓
NORMALIZED
   ↓
CORRELATED
   ↓
DERIVED FINDINGS
```

Never overwrite original evidence during this process.

---

# 16. Vulnerable Lab Rules

The vulnerable web application is intentionally insecure.

This does **not** mean the rest of the platform should be insecure.

Separate:

```text
Intentional Vulnerability
        ≠
Accidental Platform Vulnerability
```

---

## 16.1 Vulnerability Documentation

Every intentional vulnerability must have:

* identifier;
* purpose;
* attack stage;
* expected behavior;
* expected evidence;
* mitigation;
* test coverage.

Do not introduce vulnerabilities that are unrelated to the documented scenario.

---

# 17. Security Rules

## 17.1 Secrets

Never hard-code:

* API keys;
* passwords;
* database credentials;
* tokens;
* private keys;
* production secrets.

Use environment configuration.

Provide:

```text
.env.example
```

but never commit real secrets.

---

## 17.2 Input Validation

All external input must be validated.

Examples:

* API parameters;
* request bodies;
* uploaded evidence;
* filenames;
* case identifiers;
* scenario configuration;
* parser inputs.

Never trust input merely because it originates inside the project.

---

# 18. Authentication and Authorization

Where authentication is implemented:

* authentication must be verified server-side;
* authorization must be verified server-side;
* frontend-only access control is insufficient;
* sensitive operations must require appropriate permissions;
* passwords must never be stored in plaintext.

Frontend visibility is not a security boundary.

---

# 19. Logging Rules

Application logs should be structured and useful for debugging and auditing.

Recommended fields:

```text
timestamp
level
service
event
request_id
case_id
user_id (when appropriate)
error_code
message
```

Never log:

* passwords;
* API secrets;
* private keys;
* authentication tokens;
* unnecessary sensitive data.

---

# 20. Error Handling

Errors must be explicit and observable.

Bad:

```text
except:
    pass
```

Preferred:

```text
Catch
 ↓
Record useful diagnostic information
 ↓
Return controlled error
 ↓
Preserve relevant state/evidence
```

The system must not silently ignore:

* parser failures;
* evidence corruption;
* database failures;
* API failures;
* invalid configuration;
* detection-processing failures.

---

# 21. Evidence Processing Failures

If an evidence file cannot be parsed:

```text
Evidence
   ↓
Parser Failure
   ↓
Record Failure
   ↓
Preserve Original
   ↓
Continue Other Safe Processing
```

Do not:

* delete the evidence;
* silently skip it;
* alter it to make parsing succeed;
* falsely mark it as successfully processed.

---

# 22. Database Rules

Database access belongs in repositories or clearly defined data-access services.

Do not scatter raw SQL throughout application code.

Use:

* migrations;
* explicit schemas;
* validated models;
* transactions where required;
* indexes for frequently queried fields.

Database schema changes must be deliberate and migration-backed.

---

# 23. API Rules

API endpoints must follow consistent conventions.

Use:

```text
/api/v1/
```

Example:

```text
/api/v1/cases
/api/v1/evidence
/api/v1/events
/api/v1/detections
/api/v1/timeline
/api/v1/findings
/api/v1/reports
```

API responses should be predictable and documented.

Breaking API changes require explicit consideration and documentation.

---

# 24. Type and Schema Rules

Structured data should have explicit schemas.

Use appropriate typed models for:

* API requests;
* API responses;
* normalized events;
* evidence metadata;
* detection results;
* timeline entries;
* case metadata;
* report data.

Avoid passing unstructured dictionaries through the entire system when a stable schema is appropriate.

---

# 25. Python Development Rules

Python code should:

* use type hints;
* use clear naming;
* use small functions;
* avoid unnecessary global state;
* use meaningful exceptions;
* remain testable;
* follow project formatting/linting conventions.

Example:

```python
def normalize_event(
    raw_event: RawEvent,
) -> NormalizedEvent:
    ...
```

Prefer explicit interfaces over ambiguous functions.

---

# 26. TypeScript Development Rules

Frontend TypeScript code must:

* use meaningful types;
* avoid unnecessary `any`;
* reuse shared types;
* keep components focused;
* separate API communication from presentation;
* avoid duplicated business logic.

Do not use:

```typescript
const data: any = ...
```

when a meaningful type can be defined.

---

# 27. UI Rules

The UI must follow the project's design system once `design.md` is established.

Every relevant UI state should account for:

* loading;
* success;
* error;
* empty state;
* disabled state;
* validation state.

Do not create inconsistent UI patterns for the same interaction.

---

# 28. Reusable Components

Before creating a new UI component:

1. Search for an existing component.
2. Determine whether it can be reused.
3. Extend it if appropriate.
4. Create a new component only when necessary.

Avoid duplicate:

* buttons;
* cards;
* tables;
* modals;
* form controls;
* status badges;
* loading indicators.

---

# 29. Testing Rules

Important functionality must have tests.

Testing should exist at multiple levels:

```text
Unit Tests
    ↓
Integration Tests
    ↓
End-to-End Tests
    ↓
Laboratory Scenario Tests
```

---

## 29.1 Unit Testing

Test independently:

* parsers;
* validators;
* event normalization;
* detection rules;
* correlation logic;
* timeline logic;
* evidence hashing;
* utility functions.

---

## 29.2 Integration Testing

Test interactions between:

* API + database;
* evidence ingestion + storage;
* parser + normalized event model;
* detection engine + events;
* timeline engine + correlated events.

---

## 29.3 End-to-End Testing

Verify the complete path:

```text
Evidence
 ↓
API
 ↓
Forensic Engine
 ↓
Detection Engine
 ↓
Timeline
 ↓
Dashboard
```

---

# 30. Test Before Continuing

After implementing a feature:

1. Run relevant unit tests.
2. Run affected integration tests.
3. Run frontend tests where applicable.
4. Run lint/type checks.
5. Fix failures.
6. Re-run tests.
7. Only then continue to the next major change.

Never knowingly continue while important tests are failing.

---

# 31. Regression Rules

Existing functionality must not be broken unnecessarily.

When fixing a bug:

```text
Reproduce bug
      ↓
Write/identify regression test
      ↓
Fix bug
      ↓
Run regression suite
```

A bug fix without appropriate regression coverage should be treated as incomplete when practical.

---

# 32. Laboratory Reproducibility

A laboratory experiment should be reproducible.

The project should preserve:

* scenario definition;
* required environment;
* test data;
* expected evidence;
* expected detection results;
* expected timeline;
* reset procedure.

Preferred flow:

```text
Setup
 ↓
Verify
 ↓
Execute Scenario
 ↓
Collect Evidence
 ↓
Analyze
 ↓
Verify Expected Findings
 ↓
Reset
```

---

# 33. Deterministic Behavior

Where practical, the same scenario should produce equivalent results.

Avoid unnecessary:

* random values;
* uncontrolled timestamps;
* external dependencies;
* network-dependent behavior;
* non-deterministic detection logic.

If nondeterminism is required, document it.

---

# 34. Time Handling

Stored timestamps should use a consistent standard.

Preferred:

```text
UTC
ISO 8601
```

Example:

```text
2026-10-06T10:31:22Z
```

Do not mix arbitrary timestamp formats across event sources.

If source logs use different formats, normalize them during event processing while preserving the original timestamp information.

---

# 35. Git Rules

Version control must be used from the beginning of development.

Every meaningful change should be recoverable.

Git enables:

```text
Change
 ↓
Test
 ↓
Compare
 ↓
Rollback
```

Do not commit:

* secrets;
* generated temporary files;
* local credentials;
* unnecessary binaries;
* large temporary evidence artifacts unless explicitly intended.

---

# 36. Commit Rules

Commits should be:

* focused;
* meaningful;
* understandable;
* related to a specific change.

Prefer:

```text
feat: add evidence ingestion service
fix: preserve parser errors during ingestion
test: add log normalization regression tests
docs: update forensic event model
```

Avoid meaningless commits such as:

```text
update
changes
final
test
new
```

---

# 37. Documentation Rules

Documentation must evolve with implementation.

When behavior changes significantly, update the relevant documentation.

Examples:

| Change                  | Documentation            |
| ----------------------- | ------------------------ |
| Product scope           | `prd.md`                 |
| Architecture            | `architecture.md`        |
| Development behavior    | `rules.md`               |
| UI/UX                   | `design.md`              |
| Security model          | `threat-model.md`        |
| Forensic model          | `forensic-model.md`      |
| Implementation sequence | `implementation-plan.md` |
| Testing                 | `testing-strategy.md`    |

Do not allow documentation to describe an architecture that no longer exists.

---

# 38. Decision Rules

Significant technical decisions must be documented.

Examples:

* changing database technology;
* changing API architecture;
* introducing a major dependency;
* changing evidence storage;
* changing event schema;
* changing laboratory isolation;
* changing authentication architecture.

Use Architecture Decision Records where appropriate.

---

# 39. Dependency Rules

Before adding a dependency:

1. Check whether existing functionality already solves the problem.
2. Check whether the dependency is actively maintained.
3. Check its security implications.
4. Check licensing compatibility.
5. Check package size and complexity.
6. Check whether it introduces unnecessary coupling.

Do not add a dependency simply because an AI agent prefers it.

---

# 40. External Services

External services must not become hidden dependencies.

If an external service is required:

* document it;
* configure it through environment variables;
* provide a local/development alternative where practical;
* handle service failure gracefully;
* never hard-code credentials.

The core forensic workflow should remain functional within the intended controlled environment.

---

# 41. Performance Rules

Correctness comes before optimization.

Do not introduce complex optimization prematurely.

When performance becomes a problem:

```text
Measure
 ↓
Identify bottleneck
 ↓
Design optimization
 ↓
Implement
 ↓
Test
 ↓
Measure again
```

Prefer:

* pagination;
* indexed database queries;
* streaming/iterative evidence processing;
* efficient filtering;
* background processing for expensive tasks.

---

# 42. Security Review Rules

Before major releases or security-sensitive changes, review:

* authentication;
* authorization;
* input validation;
* secrets;
* file handling;
* command execution;
* network exposure;
* Docker configuration;
* database permissions;
* evidence integrity;
* logging;
* error handling.

---

# 43. AI-Generated Code Review

AI-generated code must be treated as **untrusted until reviewed and tested**.

The fact that code was generated by an AI does not establish correctness.

Before accepting AI-generated code:

```text
Inspect
 ↓
Understand
 ↓
Check architecture
 ↓
Check security
 ↓
Run tests
 ↓
Review output
 ↓
Accept
```

---

# 44. AI Must Not Silently Change Requirements

The AI agent must not:

* reinterpret the product scope without explanation;
* replace the selected technology stack without justification;
* remove existing functionality;
* modify security boundaries;
* remove tests to make a build pass;
* weaken validation;
* disable security controls;
* bypass evidence integrity requirements.

If a major change is genuinely necessary, it must be explicitly identified and documented before implementation.

---

# 45. No Test Bypassing

Never make tests pass by:

* deleting tests;
* weakening assertions without justification;
* skipping failing tests;
* disabling validation;
* mocking away the actual behavior being tested;
* hiding errors.

If a test is incorrect, fix the test with justification.

If implementation is incorrect, fix the implementation.

---

# 46. No Silent Failure

The system must never hide important failures.

Forbidden patterns include:

```text
except:
    pass
```

or:

```text
if error:
    return success
```

Failures should be:

* visible;
* logged appropriately;
* traceable;
* actionable.

---

# 47. Forensic Traceability Rule

Every important finding should be traceable backward:

```text
Finding
   ↓
Detection Rule
   ↓
Normalized Event
   ↓
Original Evidence
```

The analyst should be able to answer:

> "What evidence caused the system to produce this finding?"

---

# 48. Attack Timeline Rules

Timeline entries must be based on normalized/correlated evidence.

Each significant timeline entry should provide:

* timestamp;
* event type;
* source;
* actor when known;
* target;
* action;
* attack stage;
* severity when applicable;
* evidence reference.

Do not fabricate missing events.

---

# 49. Attack Stage Classification

Use the project's defined attack-stage taxonomy.

Example:

```text
RECON
LFI
LOG_POISONING
RCE
POST_EXPLOITATION
PRIVILEGE_ESCALATION
IMPACT
```

A stage must not be assigned solely from a weak indicator when multiple pieces of evidence are required.

---

# 50. Evidence vs Interpretation

The system must clearly separate:

```text
Raw Evidence
      ↓
Parsed Evidence
      ↓
Normalized Event
      ↓
Detected Indicator
      ↓
Correlation
      ↓
Analytical Finding
```

Never merge these layers in a way that makes provenance unclear.

---

# 51. Data Classification

The system should distinguish:

| Data Type | Meaning                             |
| --------- | ----------------------------------- |
| Original  | Untouched acquired artifact         |
| Working   | Copy used for analysis              |
| Derived   | Generated by processing             |
| Metadata  | Information describing an artifact  |
| Event     | Normalized representation           |
| Finding   | Analytical result                   |
| Report    | Human-readable investigation output |

---

# 52. File Handling Rules

Uploaded or collected evidence must be treated as untrusted input.

Validate:

* file type;
* file size;
* filename;
* path;
* content format;
* expected structure.

Prevent:

* path traversal;
* arbitrary file overwrite;
* unintended execution;
* unsafe extraction.

---

# 53. Configuration Rules

Configuration should be centralized and explicit.

Use:

```text
.env
.env.example
```

Configuration should cover appropriate categories such as:

* application;
* database;
* evidence storage;
* security;
* laboratory;
* logging.

Do not scatter configuration constants throughout the codebase.

---

# 54. Environment Separation

Maintain clear distinctions between:

```text
Development
Testing
Laboratory
Production-like
```

Do not accidentally use production credentials or infrastructure during laboratory testing.

---

# 55. Docker Rules

Docker configuration must prioritize isolation and reproducibility.

The vulnerable application must remain inside the controlled lab network.

Docker configuration should avoid unnecessary:

* host networking;
* privileged containers;
* host filesystem mounts;
* unrestricted capabilities;
* unrestricted outbound connectivity.

Any elevated container permission must have a documented reason.

---

# 56. Reset Rules

The laboratory must be resettable.

Reset functionality should return the environment to a known baseline.

Reset should remove:

* generated attack artifacts;
* temporary state;
* test modifications;
* generated evidence where appropriate.

Original reference fixtures must remain protected.

---

# 57. UI Data Integrity

The dashboard must display the data returned by the backend accurately.

The frontend must not:

* invent missing evidence;
* fabricate timestamps;
* silently change severity;
* silently modify forensic conclusions;
* hide critical errors.

If backend data is unavailable, display an appropriate error or unavailable state.

---

# 58. Accessibility and Usability

Where applicable, interfaces should provide:

* readable labels;
* keyboard-accessible controls;
* visible states;
* clear error messages;
* meaningful loading indicators;
* accessible forms;
* responsive layouts.

Usability improvements must not weaken security or forensic clarity.

---

# 59. Code Readability

Code should be understandable to another developer.

Prefer:

```text
clear names
small modules
explicit dependencies
typed interfaces
simple control flow
```

Avoid unnecessary:

```text
clever abstractions
deep nesting
magic values
hidden side effects
duplicate logic
```

---

# 60. Comments and Documentation in Code

Comments should explain **why**, not merely repeat **what** the code does.

Good:

```text
Preserve the original timestamp because normalized UTC
timestamps alone are insufficient for forensic provenance.
```

Avoid comments such as:

```text
# Add timestamp
timestamp = ...
```

---

# 61. Refactoring Rules

Refactoring is allowed when it improves:

* correctness;
* maintainability;
* testability;
* security;
* architecture.

But unrelated refactoring should not be mixed into a focused feature unless there is a clear reason.

Large refactors require:

1. scope definition;
2. risk assessment;
3. tests;
4. implementation plan;
5. validation.

---

# 62. Change Impact Analysis

Before modifying a shared component, identify:

```text
Component
   ↓
Direct consumers
   ↓
Indirect consumers
   ↓
Tests
   ↓
Documentation
```

Do not modify a shared interface without checking its consumers.

---

# 63. Breaking Changes

Breaking changes require explicit awareness.

Examples:

* changing API response schema;
* changing event schema;
* changing database schema;
* removing endpoints;
* changing evidence metadata;
* changing component interfaces.

Before a breaking change:

* identify affected components;
* update documentation;
* update tests;
* provide migration where appropriate.

---

# 64. Feature Completion Rules

A feature is not complete merely because the code works locally.

A feature should satisfy:

```text
Implementation
      +
Validation
      +
Testing
      +
Security Review
      +
Documentation
      =
Complete Feature
```

---

# 65. Definition of Done

A significant implementation is considered complete when:

* requirements are satisfied;
* architecture is respected;
* code is readable;
* relevant tests exist;
* tests pass;
* security concerns are reviewed;
* evidence integrity is preserved;
* errors are handled;
* documentation is updated;
* no unrelated scope has been introduced.

---

# 66. Large Task Execution Rules

For large changes, use:

```text
Understand
   ↓
Plan
   ↓
Break Into Tasks
   ↓
Implement Incrementally
   ↓
Test
   ↓
Review
   ↓
Integrate
```

Do not attempt to generate an entire complex subsystem blindly in one operation.

---

# 67. Task Breakdown Rules

Tasks should be:

* specific;
* testable;
* independently understandable;
* limited in scope.

Bad:

```text
Build the whole forensic system.
```

Better:

```text
Implement evidence metadata model.
Implement SHA-256 integrity service.
Add evidence ingestion API.
Add ingestion tests.
```

---

# 68. When Requirements Are Ambiguous

If ambiguity materially affects:

* security;
* architecture;
* database schema;
* evidence integrity;
* product scope;

do not silently choose a major design.

Instead:

1. identify the ambiguity;
2. state the possible interpretations;
3. choose the safest reasonable interpretation when possible;
4. document the decision.

---

# 69. No Unnecessary Complexity

Prefer the simplest architecture that satisfies the requirements.

Do not add:

* microservices;
* message brokers;
* distributed processing;
* Kubernetes;
* unnecessary cloud infrastructure;
* unnecessary AI models;

unless there is a documented requirement.

ForensiWeb prioritizes:

> **Reliability and forensic correctness over architectural complexity.**

---

# 70. Research and Technical Decisions

When making technical decisions:

1. Prefer official documentation.
2. Check compatibility.
3. Check security implications.
4. Check maintenance status.
5. Record important decisions.

Do not blindly copy code or architecture from random sources.

---

# 71. Development Workflow

The overall development process follows:

```text
IDEA
 ↓
RESEARCH
 ↓
DEFINE USER / OUTCOME
 ↓
PRD
 ↓
TECH STACK
 ↓
ARCHITECTURE
 ↓
DESIGN
 ↓
PROJECT RULES
 ↓
TASK BREAKDOWN
 ↓
SETUP
 ↓
DEVELOPMENT
 ↓
TESTING
 ↓
SECURITY REVIEW
 ↓
CODE REVIEW
 ↓
PREVIEW / LAB DEPLOYMENT
 ↓
QA
 ↓
RELEASE
 ↓
MONITORING
 ↓
ITERATION
```

Never use:

```text
IDEA → AI → DEPLOY
```

as the project development process.

---

# 72. Development Loop

For normal feature development:

```text
Read Documentation
        ↓
Inspect Repository
        ↓
Understand Requirement
        ↓
Plan
        ↓
Implement
        ↓
Run Tests
        ↓
Review Security
        ↓
Review Diff
        ↓
Update Documentation
        ↓
Commit
```

---

# 73. Final Review Checklist

Before considering a major change complete:

### Requirements

* [ ] Requirement understood.
* [ ] PRD remains satisfied.
* [ ] Scope was not unnecessarily expanded.

### Architecture

* [ ] Correct component was modified.
* [ ] Dependency direction is respected.
* [ ] No circular dependency introduced.
* [ ] No unnecessary architectural change introduced.

### Code

* [ ] Code is readable.
* [ ] Existing functionality was reused where appropriate.
* [ ] No unnecessary duplication exists.
* [ ] Types/schemas are defined.
* [ ] Errors are handled.

### Security

* [ ] No secrets committed.
* [ ] Input is validated.
* [ ] Authorization is enforced server-side where applicable.
* [ ] Vulnerable lab remains isolated.
* [ ] No unnecessary privileges introduced.

### Forensics

* [ ] Original evidence remains unchanged.
* [ ] Provenance is preserved.
* [ ] Findings remain traceable to evidence.
* [ ] No unsupported forensic conclusion is introduced.

### Testing

* [ ] Relevant tests added or updated.
* [ ] Tests pass.
* [ ] Regression behavior verified.
* [ ] Integration behavior checked where applicable.

### Documentation

* [ ] Relevant documentation updated.
* [ ] Architectural changes documented.
* [ ] Important decisions recorded.

---

# 74. Anti-Patterns

The following behaviors are explicitly discouraged:

| Anti-Pattern                         | Why It Is Prohibited                           |
| ------------------------------------ | ---------------------------------------------- |
| Coding without inspecting repository | Causes duplication and architectural conflicts |
| Modifying unrelated files            | Increases regression risk                      |
| Giant AI-generated changes           | Difficult to review and debug                  |
| Hard-coded secrets                   | Security risk                                  |
| Silent exception handling            | Hides failures                                 |
| Direct DB access from UI             | Breaks architecture                            |
| Business logic in routes             | Reduces maintainability                        |
| Untraceable forensic findings        | Reduces forensic credibility                   |
| Modifying original evidence          | Breaks evidence integrity                      |
| Skipping tests                       | Reduces reliability                            |
| Removing tests to pass CI            | Hides defects                                  |
| Adding unnecessary dependencies      | Increases complexity                           |
| Scope creep                          | Makes project uncontrolled                     |
| Blind AI-generated refactoring       | Can break architecture                         |
| Public exposure of vulnerable lab    | Safety risk                                    |

---

# 75. Golden Rules

The following rules are the most important rules in the entire document.

> **Rule 1 — Read Before You Build**
> Always understand the relevant documentation and existing implementation before coding.

> **Rule 2 — Reuse Before Creating**
> Search for existing functionality before creating new functionality.

> **Rule 3 — Change Only What Is Needed**
> Do not modify unrelated files or systems.

> **Rule 4 — Never Compromise Evidence Integrity**
> Original forensic evidence must remain preserved and traceable.

> **Rule 5 — Never Compromise Laboratory Isolation**
> The intentionally vulnerable environment must remain controlled.

> **Rule 6 — Security Must Be Server-Side**
> Never rely only on frontend controls for security decisions.

> **Rule 7 — Every Important Finding Must Be Explainable**
> Security conclusions must be traceable to evidence.

> **Rule 8 — Test Before Continuing**
> Important functionality must be tested before moving forward.

> **Rule 9 — Do Not Hide Failures**
> Errors must be visible, diagnosable, and appropriately handled.

> **Rule 10 — AI Does Not Override the Project**
> AI-generated suggestions must follow the project's PRD, architecture, and rules.

> **Rule 11 — Avoid Scope Creep**
> Future ideas belong in future scope unless explicitly approved.

> **Rule 12 — Correctness Before Complexity**
> Prefer a simple, reliable implementation over unnecessary sophistication.

---

# 76. Relationship With Other Project Documents

| Document                 | Primary Question                                   | Authority    |
| ------------------------ | -------------------------------------------------- | ------------ |
| `prd.md`                 | What are we building and why?                      | Product      |
| `architecture.md`        | How is the system structured?                      | Architecture |
| `rules.md`               | How must development be performed?                 | Engineering  |
| `design.md`              | How should the product look and feel?              | UI/UX        |
| `forensic-model.md`      | How is forensic evidence represented and analyzed? | Forensics    |
| `threat-model.md`        | What are the security threats and boundaries?      | Security     |
| `implementation-plan.md` | In what order should the system be built?          | Execution    |
| `testing-strategy.md`    | How do we verify correctness?                      | Quality      |

No document should silently contradict another source-of-truth document.

---

# 77. Rule Change Policy

Rules should not be changed casually.

A significant rule change must:

1. identify the reason;
2. identify affected components;
3. evaluate security impact;
4. evaluate forensic impact;
5. evaluate reproducibility impact;
6. update dependent documentation;
7. update tests if required.

Historical decisions should remain traceable through Git.

---

# 78. Final Principle

ForensiWeb is being developed with AI assistance, but AI assistance must never replace engineering discipline.

The project must follow:

```text
Documentation
      ↓
Understanding
      ↓
Planning
      ↓
Implementation
      ↓
Testing
      ↓
Security Review
      ↓
Forensic Validation
      ↓
Review
      ↓
Release
```

The ultimate objective is not simply to produce code.

The objective is to produce a:

**secure, isolated, reliable, reproducible, explainable, testable, and academically defensible forensic-analysis system.**

---

## Final Rule

> **Build deliberately.
> Change minimally.
> Test continuously.
> Preserve evidence.
> Keep the laboratory isolated.
> Make every important conclusion explainable.
> Never let AI convenience override project correctness.**
