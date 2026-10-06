# ForensiWeb — Isolated Laboratory Docker Architecture

**Directory:** `lab/docker/`  
**Purpose:** Documentation and container manifests for the isolated laboratory environment.  
**Authority:** Security Boundaries & Laboratory Isolation  

---

## 1. Laboratory Topology

The ForensiWeb laboratory environment provides a controlled, deterministic target for evaluating the multi-stage attack scenario:
```text
LFI → Log Poisoning → RCE → Web Shell → PATH Misconfiguration → Privilege Escalation
```

```text
+-------------------------------------------------------------------------------+
|                       forensiweb-lab-net (internal: true)                     |
|                                                                               |
|  +--------------------------------+       +--------------------------------+  |
|  |   vulnerable-web-app           |       |   scenario-runner (Future)     |  |
|  |   - Python 3.12 Flask          | <===> |   - Pre-scripted replay agent  |  |
|  |   - Port: 5000 (127.0.0.1 only)|       |   - Non-interactive            |  |
|  |   - cap_drop: [ALL]            |       |   - Deterministic telemetry    |  |
|  |   - mem_limit: 512M            |       +--------------------------------+  |
|  +--------------------------------+                                           |
|                   │                                                           |
|                   ▼ (Shared Volume / Read-Only Bind Mount)                    |
|  +--------------------------------+                                           |
|  |   Evidence Collection Agent    |                                           |
|  +--------------------------------+                                           |
+-------------------------------------------------------------------------------+
```

---

## 2. Key Security & Isolation Guardrails

1. **Strict Non-Egress Network Isolation:** The `forensiweb-lab-net` network is flagged with `internal: true`. Containers inside this network cannot route traffic to the public internet or external networks, eliminating risk of remote exploitation, botnet callbacks, or data exfiltration.
2. **Localhost Binding Only:** Any service exposing ports to the host machine binds strictly to `127.0.0.1` (localhost). No container port binds to `0.0.0.0`.
3. **Dropped Capabilities (`cap_drop: [ALL]`):** Lab target containers drop all default Linux capabilities, preventing kernel-level privilege escalation or container breakout.
4. **Strict Resource Constraints:** Containers are limited to `512M` RAM and `1.0` CPU cores to prevent local host Denial of Service during intensive scenario runs.
5. **No Docker Socket Access:** The host Docker socket (`/var/run/docker.sock`) is never mounted into the vulnerable container or scenario runners.
