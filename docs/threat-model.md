# ForensiWeb — Threat Model & Security Boundaries

**Document:** `threat-model.md`  
**Status:** Approved Specification  
**Version:** 1.0  
**Project:** ForensiWeb  
**Authority:** Security & Laboratory Isolation  

---

## 1. Executive Summary

ForensiWeb is an academic cybersecurity and digital forensics research platform designed to simulate, capture, normalize, correlate, and investigate a multi-stage web application attack chain within a strictly controlled, isolated laboratory environment.

Because ForensiWeb incorporates a deliberately vulnerable web application and reproduces realistic exploit scenarios (Local File Inclusion, Log Poisoning, Remote Code Execution, and Privilege Escalation), strict threat modeling and security boundaries are required to prevent:
1. Accidental exploitation or spillover beyond the isolated laboratory containers to the host machine or local network.
2. Conversion of the platform into a generalized, offensive exploitation framework.
3. Compromise or tampering of collected digital evidence and analysis records.
4. Cross-Site Scripting (XSS) or injection attacks within the analyst dashboard when rendering poisoned log artifacts.

---

## 2. System Architecture & Assets

### 2.1 Primary Assets

| Asset ID | Asset Name | Description | Sensitivity / Integrity Requirement |
|---|---|---|---|
| **AST-01** | **Original Evidence Store** | Raw captured log files, system memory/process dumps, and network captures stored in `data/evidence/original/`. | **Critical Immutability** — Must be cryptographically hashed (SHA-256) upon acquisition and marked read-only. Tampering invalidates the forensic study. |
| **AST-02** | **Normalized Event Store** | Structured Common Event Model (CEM) records persisted in PostgreSQL and derived caches. | **High Integrity** — Must accurately reflect original evidence without synthetic fabrication or data loss. |
| **AST-03** | **Host Operating System** | The physical or virtual host executing the ForensiWeb containers and backend processes. | **Critical Isolation** — Must remain completely isolated from vulnerable target containers and simulated attack payloads. |
| **AST-04** | **Backend API & Database** | FastAPI orchestration service and PostgreSQL database containing case metadata, detection rules, and reports. | **High Confidentiality & Integrity** — Restricted access; parameterized queries; authenticated endpoints. |
| **AST-05** | **Analyst Dashboard (UI)** | Web-based investigation frontend rendering raw logs, timelines, and attack graphs. | **High Integrity** — Must prevent execution of malicious payloads embedded within log data (XSS prevention). |
| **AST-06** | **Controlled Vulnerable Application** | Deliberately vulnerable Flask application containing the study's intentional flaw chain. | **Restricted Scope** — Must only be accessible within the dedicated internal Docker bridge network (`forensiweb-lab-net`). |

---

## 3. Threat Actors & Motivations

```text
+-------------------------+-----------------------------------------------------------+
| Threat Actor            | Motivation & Capability                                   |
+-------------------------+-----------------------------------------------------------+
| Academic Researcher /   | - Evaluates forensic detection accuracy and timeline      |
| Forensic Analyst        |   reconstruction.                                         |
| (Authorized Operator)   | - Non-hostile, but could inadvertently misconfigure       |
|                         |   the environment or mishandle malicious artifacts.       |
+-------------------------+-----------------------------------------------------------+
| Simulated Exploit Agent | - Executes pre-scripted, deterministic attack payloads    |
| (Automated Scenario)    |   strictly inside the lab container network.              |
|                         | - Bound by hardcoded scenario scripts; no autonomous      |
|                         |   reconnaissance or external network access.              |
+-------------------------+-----------------------------------------------------------+
| Malicious External      | - Hostile actor attempting to exploit vulnerable targets   |
| Threat Actor            |   or pivot into the host system.                          |
| (Out-of-Scope Threat)   | - Must be prevented by ensuring NO vulnerable services   |
|                         |   are exposed to public interfaces (bound to 127.0.0.1).   |
+-------------------------+-----------------------------------------------------------+
```

---

## 4. Attack Chain & Threat Breakdown

ForensiWeb models a realistic 6-stage chained web-application attack:

```text
[Stage 1: Recon & LFI]
        ↓
[Stage 2: Log Poisoning]
        ↓
[Stage 3: Remote Code Execution (RCE)]
        ↓
[Stage 4: Post-Exploitation / Web Shell]
        ↓
[Stage 5: Environment / PATH Misconfiguration]
        ↓
[Stage 6: Privilege Escalation]
```

### Stage 1: Reconnaissance & Local File Inclusion (LFI)
- **Vulnerability:** Unsanitized file parameter in target web application (e.g., `GET /view?page=../../../../etc/passwd`).
- **Threat:** Arbitrary file read of local server files readable by the web service account (`www-data`).
- **Forensic Artifacts:** HTTP access logs (`400`/`200` status codes with directory traversal sequences `../` and `%2e%2e%2f`).
- **Boundary Control:** Target web service runs as low-privilege unprivileged user inside Docker with limited filesystem visibility.

### Stage 2: Log Poisoning
- **Vulnerability:** Target web server logs unvalidated client request headers (e.g., `User-Agent`, `Referer`, URL paths) into accessible log files (e.g., `/var/log/nginx/access.log` or `/app/logs/access.log`).
- **Threat:** Attacker injects PHP/Python executable code into HTTP request headers (e.g., `<?php system($_GET['cmd']); ?>` or Python command execution snippets).
- **Forensic Artifacts:** Web server access logs containing anomalous byte lengths, URL-encoded payload characters, or script tags; timestamped server access events.
- **Boundary Control:** Injected code is inert in the log file until evaluated by an execution vector.

### Stage 3: Remote Code Execution (RCE)
- **Vulnerability:** Combining LFI with Log Poisoning (e.g., `GET /view?page=/app/logs/access.log&cmd=id`).
- **Threat:** Code injected during Stage 2 is executed in the context of the vulnerable web server process.
- **Forensic Artifacts:** HTTP requests referencing local log paths; web process spawning shell children (`sh`, `bash`, `python`); CPU/memory spikes.
- **Boundary Control:** Lab container has dropped capabilities (`cap_drop: ALL`), restricting kernel-level exploitation.

### Stage 4: Post-Exploitation & Web Shell Activity
- **Vulnerability:** Server-side command execution via web shell or reverse shell payload.
- **Threat:** Attacker executes reconnaissance commands (`id`, `whoami`, `uname -a`, `ls -la /tmp`), writes secondary payload artifacts to temporary directories.
- **Forensic Artifacts:** File system creation events in `/tmp`, process execution logs (`auditd`, `syslog`, container exec logs), interactive shell spawn records.
- **Boundary Control:** No outbound internet connectivity; reverse shell cannot connect to external internet infrastructure.

### Stage 5: Environment / PATH Misconfiguration Exploitation
- **Vulnerability:** Predictable writable directory placed ahead of trusted system binaries in `$PATH` (e.g., `PATH=/tmp/bin:/usr/local/bin:/usr/bin`) or sensitive environment variables accessible by web process.
- **Threat:** Attacker drops a trojanized binary with the name of a commonly executed system command (e.g., `/tmp/bin/curl` or `/tmp/bin/backup`) and manipulates execution context.
- **Forensic Artifacts:** File modification events in `/tmp/bin`; environment variable manipulation logged in process execution logs.
- **Boundary Control:** Misconfiguration is strictly localized within the lab container image.

### Stage 6: Privilege Escalation
- **Vulnerability:** Scheduled cron job or administrative maintenance script running with elevated permissions executes the hijacked binary via the poisoned `$PATH`.
- **Threat:** Attacker gains root or elevated execution within the target container.
- **Forensic Artifacts:** Process table events showing elevated PID parentage, file modifications to root-owned areas, cron execution logs.
- **Boundary Control:** Container runs without `--privileged` flag; container root is namespaced and isolated from the host OS kernel.

---

## 5. Security Zones & Trust Boundaries

```text
+-----------------------------------------------------------------------------------------+
|                                    HOST MACHINE                                         |
|                                                                                         |
|  +-------------------------+   Trust Boundary A   +----------------------------------+  |
|  |     Analyst Browser     | <==================> |          Core System             |  |
|  |  (React/TypeScript UI) |                      | - FastAPI Backend (apps/api)     |  |
|  |   Port: 5173 / 80       |                      | - PostgreSQL Database            |  |
|  +-------------------------+                      | - Forensic Processing Engines    |  |
|                                                   +----------------------------------+  |
|                                                                     ||                  |
|                                                                     || Trust Boundary B |
|                                                                     || (Docker Network) |
|                                                                     \/                  |
|  +-----------------------------------------------------------------------------------+  |
|  |                      ISOLATED LAB ENVIRONMENT (Docker Bridge)                     |  |
|  |                      Network: forensiweb-lab-net (internal: true)                 |  |
|  |                                                                                   |  |
|  |  +--------------------------------+       +------------------------------------+  |  |
|  |  | Vulnerable Target Container    | <===> | Scenario Runner Container          |  |  |
|  |  | (Flask / apps/vulnerable-app)  |       | (Controlled Exploit Script)        |  |  |
|  |  | Port: 5000 (Internal Only)     |       | Non-interactive, deterministic     |  |  |
|  |  +--------------------------------+       +------------------------------------+  |  |
|  |                   ||                                                              |  |
|  |                   || Shared Read-Only Volume (Evidence Collection)                |  |
|  |                   \/                                                              |  |
|  |  +--------------------------------+                                               |  |
|  |  | Log & Artifact Collector       | = = = > Host Ingestion Pipeline               |  |
|  |  +--------------------------------+                                               |  |
|  +-----------------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------------+
```

### Trust Boundary A: Analyst Web UI to Backend API
- **Threats:** Stored XSS from analyzed poisoned logs; unauthorized API access; injection of malformed case parameters.
- **Mitigations:**
  - Strict output encoding and HTML sanitization in React UI (raw log views rendered via dedicated pre-formatted, escaped text viewer).
  - Pydantic schema validation on all API inputs.
  - JWT-based authentication for analyst session management.

### Trust Boundary B: Backend Engine to Lab Environment
- **Threats:** Lab container escape; rogue network activity; tampering with collection scripts.
- **Mitigations:**
  - Lab network configured with `internal: true` (no internet egress).
  - Target containers run with `cap_drop: [ALL]` and only necessary capabilities (`SETUID` limited to lab scenario).
  - Host mounts are strictly limited to `read-only` collection directories where possible.
  - No Docker socket (`/var/run/docker.sock`) mounted inside the target container.

### Trust Boundary C: Evidence Ingestion to Storage
- **Threats:** Post-capture evidence alteration; race conditions during log collection; directory traversal in artifact filenames.
- **Mitigations:**
  - Cryptographic SHA-256 calculation immediately upon intake into `data/evidence/original/`.
  - Immutable file permissions applied immediately.
  - Strict filename sanitization and UUID-based artifact referencing.

---

## 6. Threat Classification (STRIDE Matrix)

| STRIDE Category | Threat Description | Vulnerable Component | Likelihood | Impact | Applied Mitigation |
|---|---|---|---|---|---|
| **Spoofing** | Attacker spoofs source IP or User-Agent headers in HTTP logs to mislead forensic timeline. | Web Server Access Logs | High (Expected in Scenario) | Medium | Forensic correlation engine correlates multiple log streams (HTTP logs + kernel audit logs + process events) to detect header spoofing. |
| **Tampering** | Injected exploit attempts to overwrite or delete access logs (`shred -u access.log`). | Target Server File System | High (Expected in Scenario) | High | Evidence collector streams logs in real-time or collects snapshots; auditd captures process deletion attempts; original evidence is hashed. |
| **Tampering** | Analyst or script inadvertently alters evidence stored in `data/evidence/original`. | Evidence Repository | Low | Critical | Filesystem write-protection, checksum manifests, and integrity verification tests in CI/CD pipeline. |
| **Repudiation** | Action cannot be linked to specific container process or timeline event. | Audit Logging | Medium | High | High-resolution timestamping (ISO-8601 UTC with microsecond precision), PID/PPID mapping, and Common Event Model tracking. |
| **Information Disclosure** | Vulnerable target exposes host filesystem via path traversal flaw. | Vulnerable Web App | High (Intentional) | Critical | Containerization ensures traversal is restricted to container filesystem; no host directories mounted into target. |
| **Denial of Service** | Exploit script or log volume exhaustion freezes the host system. | Docker Storage & Host RAM | Medium | Medium | Docker resource constraints (`mem_limit: 512m`, `cpus: 1.0`, log rotation policies). |
| **Elevation of Privilege** | Container escape allows privilege escalation to host root. | Container Runtime | Very Low | Critical | Unprivileged Docker daemon execution, no `--privileged` mode, no host device mounts, dropped Linux capabilities. |

---

## 7. Mandatory AI & Developer Safety Rules

1. **No Generalized Exploitation Frameworks:** Tools developed under ForensiWeb must strictly serve the approved, reproducible research scenario. Generalized attack tooling (e.g., weaponized scanning, automated exploit generators) is prohibited.
2. **Defensive Log Parsing:** Parser logic must not execute, evaluate, or invoke system shells on log data. Never use `eval()`, `exec()`, or unsanitized shell commands during forensic parsing.
3. **Strict Port Binding:** No lab service may bind to `0.0.0.0`. Development services must bind exclusively to `127.0.0.1` (localhost).
4. **Zero Committed Secrets:** No production secrets, private keys, or credentials may be committed to source control. Use `.env.example` templates with mock values only.
5. **Deterministic Scenarios:** Simulated attacks must be reproducible, version-controlled scripts with predictable execution traces to ensure academic validity.

---

## 8. Threat Model Maintenance

This threat model must be reviewed and updated whenever:
- A new attack scenario phase is integrated.
- Changes are made to Docker container configurations or volume mounts.
- Evidence collection mechanisms or parser pipelines are altered.
- New dependencies are introduced into the backend or target applications.
