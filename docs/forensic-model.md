# ForensiWeb — Forensic Model & Evidence Representation

**Document:** `forensic-model.md`  
**Status:** Approved Specification  
**Version:** 1.0  
**Project:** ForensiWeb  
**Authority:** Digital Forensics, Evidence Integrity & Analytics  

---

## 1. Executive Summary

ForensiWeb is built upon rigorous digital forensics principles. The primary academic and forensic objective is to reconstruct a coherent, evidence-backed narrative of a multi-stage web application attack chain:
```text
LFI → Log Poisoning → RCE → Web Shell → Environment Misconfiguration → Privilege Escalation
```

In digital forensics, **an assertion without cryptographically verifiable evidence is an unverified hypothesis**. This document establishes the foundational forensic model, evidence integrity protocol, the Common Event Model (CEM), event correlation ontology, and attack timeline reconstruction standards for ForensiWeb.

---

## 2. Core Forensic Principles

ForensiWeb adheres to international digital forensics standards (ISO/IEC 27037 and NIST SP 800-86):

```text
+---------------------+---------------------------------------------------------------+
| Principle           | Operational Requirement                                       |
+---------------------+---------------------------------------------------------------+
| 1. Immutability     | Original evidence is preserved in its pristine, acquired state|
|                     | and is never directly modified or parsed in-place.            |
+---------------------+---------------------------------------------------------------+
| 2. Cryptographic    | Cryptographic hashes (SHA-256) are calculated immediately     |
|    Integrity        | upon acquisition and re-verified prior to downstream analysis.|
+---------------------+---------------------------------------------------------------+
| 3. Traceability     | Every normalized event, detection alert, correlation edge, and|
|                     | report finding must link back to exact byte/line offsets in   |
|                     | the original evidence artifact.                               |
+---------------------+---------------------------------------------------------------+
| 4. Explainability   | Detections and correlation links must provide transparent,     |
|                     | deterministic reasoning rather than opaque black-box scores.   |
+---------------------+---------------------------------------------------------------+
| 5. Reproducibility  | Given the same scenario execution parameters, the identical   |
|                     | evidence set and analytical findings must be reconstructed.   |
+---------------------+---------------------------------------------------------------+
```

---

## 3. Evidence Lifecycle

The forensic pipeline processes evidence through nine distinct, sequential phases:

```text
[1. Evidence Acquisition]
          ↓
[2. Cryptographic Hashing (SHA-256) & Manifest Generation]
          ↓
[3. Storage in Immutable Original Store]
          ↓
[4. Generation of Working Copy]
          ↓
[5. Structured Parsing]
          ↓
[6. Event Normalization (Common Event Model)]
          ↓
[7. Detection Rule Evaluation]
          ↓
[8. Multi-Source Event Correlation]
          ↓
[9. Attack Timeline & Report Synthesis]
```

### Stage 1 & 2: Acquisition and Integrity Hashing
- Evidence is collected from laboratory containers (web logs, system logs, environment dumps, audit records).
- For each artifact, a cryptographic SHA-256 checksum is computed immediately.
- An integrity manifest (`manifest.json`) is generated containing file name, file size, acquisition timestamp (ISO-8601 UTC), source container ID, collector version, and SHA-256 hash.

### Stage 3 & 4: Preservation and Working Copy
- The raw artifact is placed in `data/evidence/original/{case_id}/{artifact_id}/` and marked read-only.
- A verified duplicate is created in `data/evidence/working/{case_id}/{artifact_id}/`.
- All parsing engines operate strictly on the working copy, preserving original data integrity.

### Stage 5 & 6: Parsing and Normalization
- Domain-specific parsers extract structured fields from heterogeneous log formats.
- Extracted entries are converted into the standard Common Event Model (CEM) format and stored in `data/evidence/derived/{case_id}/` and the relational database.

### Stage 7, 8 & 9: Detection, Correlation, and Timeline Reconstruction
- Detection rules evaluate normalized events against known attack signatures and behavioral heuristics.
- Correlated events are sequenced chronologically and mapped across the 6 stages of the attack chain.
- The forensic report links each conclusion directly to the supporting evidence IDs and line references.

---

## 4. Evidence Storage Layout

To ensure clean isolation and long-term reproducibility, evidence artifacts are structured as follows:

```text
data/
└── evidence/
    ├── original/                    # Read-only pristine evidence
    │   └── {case_id}/
    │       ├── manifest.json        # Hashes, timestamps, metadata
    │       ├── web_access.log
    │       ├── app_error.log
    │       ├── auditd.log
    │       └── env_dump.json
    ├── working/                     # Working copies for parser execution
    │   └── {case_id}/
    │       └── [mirrors original layout]
    └── derived/                     # Extracted, normalized, and analyzed artifacts
        └── {case_id}/
            ├── normalized_events.jsonl
            ├── detections.json
            ├── correlation_graph.json
            └── timeline.json
```

---

## 5. Common Event Model (CEM)

Heterogeneous evidence sources (Nginx logs, Flask app logs, Linux auditd records, process tables) must be unified into a standardized representation to allow cross-source correlation.

### 5.1 CEM Schema Definition

Every normalized event conforms to the following schema:

```json
{
  "event_id": "evt_01j7x4a29b00001",
  "case_id": "case_2026_001",
  "timestamp": "2026-10-06T14:32:15.123456Z",
  "source_type": "web_server",
  "source_artifact_id": "art_nginx_access_001",
  "source_location": {
    "line_number": 142,
    "byte_offset_start": 14205,
    "byte_offset_end": 14389
  },
  "attack_stage": "stage_02_log_poisoning",
  "severity": "high",
  "action": "http_request",
  "actor": {
    "ip": "172.28.0.5",
    "user_agent": "Mozilla/5.0 <?php system($_GET['cmd']); ?>",
    "user": "anonymous"
  },
  "target": {
    "host": "vulnerable-app.lab",
    "port": 5000,
    "path": "/index.php",
    "method": "GET",
    "status_code": 200
  },
  "details": {
    "injected_payload": "<?php system($_GET['cmd']); ?>",
    "query_params": {
      "page": "contact.php"
    }
  },
  "evidence_ref": {
    "artifact_name": "web_access.log",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  }
}
```

### 5.2 Field Definitions

| Field | Type | Description |
|---|---|---|
| `event_id` | String (UUID/KSUID) | Unique identifier for the normalized event. |
| `case_id` | String | Reference to the investigation case. |
| `timestamp` | String (ISO-8601 UTC) | Microsecond-precision normalized UTC event timestamp. |
| `source_type` | Enum | `web_server`, `application`, `system_audit`, `process`, `filesystem`, `auth`. |
| `source_artifact_id` | String | Identifier of the ingested source file. |
| `source_location` | Object | Exact `line_number`, `byte_offset_start`, and `byte_offset_end` in source file. |
| `attack_stage` | Enum | Stage mapping: `stage_01_lfi`, `stage_02_log_poisoning`, `stage_03_rce`, `stage_04_web_shell`, `stage_05_env_manipulation`, `stage_06_priv_esc`, or `normal`. |
| `severity` | Enum | `info`, `low`, `medium`, `high`, `critical`. |
| `action` | String | Normalized action name (e.g., `file_read`, `command_exec`, `process_fork`). |
| `actor` | Object | Identity of the initiating entity (IP address, OS user, process PID). |
| `target` | Object | Targeted resource (URL endpoint, file path, process name, env variable). |
| `details` | Object | Format-specific structured context and extracted payloads. |
| `evidence_ref` | Object | Original artifact filename and cryptographic SHA-256 checksum. |

---

## 6. Correlation Engine & Attack Stage Ontology

### 6.1 Multi-Source Correlation Heuristics

Isolated log entries do not tell the whole story. The correlation engine links events across disparate log streams using five core correlation techniques:

1. **Temporal Proximity Window:** Events occurring within a configured delta $\Delta t$ (e.g., $\le 5$ seconds) are evaluated for causal relationships.
2. **Actor & Source IP Continuity:** Linking HTTP request origins with internal socket connections and session identifiers.
3. **Resource Continuity:** A file path requested via LFI (`/var/log/nginx/access.log`) correlated with previous log-poisoning writes to that exact file.
4. **Process Lineage (PPID → PID):** Web server child process (`www-data` or `flask`) spawning unexpected shells (`/bin/sh`, `/bin/bash`, `python3`).
5. **Environment Context Mapping:** Correlation between process spawn events and inherited or modified environment variables (e.g., altered `$PATH`).

```text
[HTTP GET with Traversal Pattern] (Web Log)
                │  Δt: 2.1s
                ▼
[HTTP GET Poisoning User-Agent] (Web Log)
                │  Δt: 1.4s
                ▼
[HTTP GET executing Log via LFI] (Web Log)
                │  Δt: 0.2s
                ▼
[Process Fork: sh child of web app] (Audit Log)
                │  Δt: 15.0s
                ▼
[File Write to /tmp/bin/su] (Filesystem Log)
                │  Δt: 30.0s
                ▼
[Elevated Process Executed via modified PATH] (Audit Log)
```

### 6.2 Confidence Scoring

Each correlation link is assigned an explainable confidence score based on objective evidence factors:

| Confidence Level | Score Range | Criteria |
|---|---|---|
| **Definitive** | 0.90 – 1.00 | Direct process lineage (PID/PPID match) or cryptographically verified identical payload hash. |
| **High** | 0.75 – 0.89 | Precise temporal match ($\le 2$s) combined with identical Source IP and matching target resource. |
| **Probable** | 0.50 – 0.74 | Plausible temporal proximity with matching session context or sequential attack pattern. |
| **Low / Inconclusive** | < 0.50 | Weak temporal proximity without secondary corroborating identifiers. |

Every correlation output includes a human-readable `explanation` field detailing the exact rules and attributes used to make the deduction.

---

## 7. Attack Timeline Reconstruction

The attack timeline represents the chronological sequence of confirmed malicious activities.

### 7.1 Timeline Requirements

- **Strict Chronological Ordering:** Events are ordered by microsecond UTC timestamp.
- **Clock Drift Compensation:** If clocks between containers exhibit slight skew, the normalization engine applies calibrated timestamp offsets documented in the case manifest.
- **Gap Analysis:** Identifies time gaps where evidence may be missing or suppressed by attacker anti-forensics.
- **Stage Annotations:** Visual and tabular grouping by attack chain stage.

---

## 8. Mitigation & Verification Model

Forensics is complete only when verified against security remediations:

```text
[Baseline Attack Run] =======> Evidence Collected =======> Confirmed Attack Timeline
          │
          ▼ Apply Mitigation (Input sanitization, strict PATH, dropped capabilities)
          │
[Post-Mitigation Run] =======> Evidence Collected =======> Verified Attack Blocked / Neutralized
```

ForensiWeb records and compares:
1. **Pre-mitigation telemetry:** Attack chain executes successfully; high-severity detections generated; timeline reconstructed.
2. **Post-mitigation telemetry:** Attack vector is rejected (e.g., HTTP `400 Bad Request` or `403 Forbidden`); no unauthorized process spawns occur; evidence confirms attack chain broken at Stage 1 or 2.

---

## 9. Forensic Model Verification Checklist

Before completing each forensic feature, verify:
- [ ] Original evidence files remain byte-identical (SHA-256 checksums match manifest).
- [ ] All normalized events contain accurate line numbers and byte offsets.
- [ ] No synthetic evidence is fabricated without explicit test-fixture labels.
- [ ] Correlation logic produces deterministic, explainable results.
- [ ] Reports cite verifiable evidence identifiers.
