"""Report templates and formatters for academic digital forensic reporting."""

from __future__ import annotations

import html
from typing import Any, Dict, List


def format_markdown_report(data: Dict[str, Any]) -> str:
    """Render a comprehensive academic forensic report in Markdown format."""
    case = data.get("case", {})
    metadata = data.get("metadata", {})
    evidence_list = data.get("evidence", [])
    timeline = data.get("timeline", [])
    detections = data.get("detections", [])
    findings = data.get("findings", [])
    mitigations = data.get("mitigations", [])
    limitations = data.get("limitations", [])

    md = []
    md.append(f"# FORENSIC INCIDENT INVESTIGATION REPORT: {case.get('id', 'N/A')}")
    md.append(f"**Document Title:** {data.get('title', 'Forensic Analysis Report')}  ")
    md.append(f"**Classification:** {data.get('classification', 'CONFIDENTIAL // ACADEMIC RESEARCH')}  ")
    md.append(f"**Generated At:** {data.get('generated_at', 'UTC')}  ")
    md.append(f"**Author / Lead Investigator:** {data.get('investigator', 'ForensiWeb Automated Analysis Engine')}  ")
    md.append(f"**Case Reference:** {case.get('id', 'N/A')} - {case.get('title', 'N/A')}  ")
    md.append("")
    md.append("---")
    md.append("")

    # 1. Executive Summary
    md.append("## 1. Executive Summary")
    md.append(data.get("executive_summary", "No executive summary provided."))
    md.append("")

    # 2. Investigation Scope & Methodology
    md.append("## 2. Investigation Scope & Scientific Methodology")
    md.append(f"**Scenario Context:** {metadata.get('scenario', 'Controlled Laboratory Attack Scenario')}  ")
    md.append(f"**Target System:** {metadata.get('target', 'Isolated Virtual Application')}  ")
    md.append(data.get("methodology", "The investigation strictly followed the Common Event Model (CEM) normalization, cryptographic evidence integrity tracking, and multi-source event correlation."))
    md.append("")

    # 3. Evidence Inventory & Cryptographic Integrity
    md.append("## 3. Evidence Inventory & Cryptographic Integrity Verification")
    md.append("| Evidence ID | Source Artifact | Ingestion Time (UTC) | File Size | SHA-256 Checksum | Integrity Status |")
    md.append("|---|---|---|---|---|---|")
    for ev in evidence_list:
        md.append(
            f"| `{ev.get('id', '-')}` | `{ev.get('source_path', '-')}` | {ev.get('collected_at', '-')} | "
            f"{ev.get('size_bytes', 0)} B | `{ev.get('sha256', '-')}` | **{ev.get('status', 'VERIFIED')}** |"
        )
    md.append("")

    # 4. Chronological Incident Timeline
    md.append("## 4. Chronological Incident Timeline")
    md.append("| Timestamp (UTC) | Attack Stage | Severity | Event Description | Source & Location |")
    md.append("|---|---|---|---|---|")
    for tl in timeline:
        md.append(
            f"| `{tl.get('timestamp', '-')}` | `{tl.get('stage', '-')}` | **{tl.get('severity', '-')}** | "
            f"{tl.get('description', '-')} | `{tl.get('source_ref', '-')}` |"
        )
    md.append("")

    # 5. Explainable Detections Summary
    md.append("## 5. Detections & Automated Analysis Summary")
    md.append("| Rule ID | Rule Name | MITRE ATT&CK | Severity | Confidence | Triggering Artifact |")
    md.append("|---|---|---|---|---|---|")
    for det in detections:
        md.append(
            f"| `{det.get('rule_id', '-')}` | {det.get('rule_name', '-')} | `{det.get('mitre_id', '-')}` | "
            f"{det.get('severity', '-')} | {det.get('confidence', 1.0)*100:.0f}% | `{det.get('artifact_id', '-')}` |"
        )
    md.append("")

    # 6. Detailed Forensic Findings
    md.append("## 6. Detailed Forensic Findings")
    for idx, f in enumerate(findings, start=1):
        md.append(f"### Finding #{idx}: {f.get('title', 'Untitled Finding')}")
        md.append(f"- **Finding ID:** `{f.get('id', '-')}`")
        md.append(f"- **Severity:** **{f.get('severity', '-').upper()}**")
        md.append(f"- **Attack Chain Stage:** `{f.get('stage', '-')}`")
        md.append(f"- **Status:** {f.get('status', 'CONFIRMED')}")
        md.append(f"- **Description:** {f.get('description', '-')}")
        md.append("")
        md.append("**Evidence Traceability & Proof:**")
        refs = f.get("evidence_references", [])
        if refs:
            for r in refs:
                md.append(f"  - Artifact: `{r.get('artifact_name', '-')}` (SHA256: `{r.get('sha256', '-')[:16]}...`)")
                if "line_number" in r:
                    md.append(f"    - Location: Line {r.get('line_number')}, Offset: [{r.get('byte_offset_start')}:{r.get('byte_offset_end')}]")
                if "snippet" in r:
                    md.append(f"    - Extracted Telemetry: `{r.get('snippet')}`")
        else:
            md.append("  - *No specific evidence citations attached.*")
        md.append("")

    # 7. Remediation & Mitigation Recommendations
    md.append("## 7. Security Remediation & Mitigation Recommendations")
    if mitigations:
        for idx, m in enumerate(mitigations, start=1):
            md.append(f"{idx}. **{m.get('title', 'Recommendation')}** (`{m.get('target_component', 'System')}`)")
            md.append(f"   - {m.get('remediation', '-')}")
            if "verification_test" in m:
                md.append(f"   - *Verification Criteria:* {m.get('verification_test')}")
    else:
        md.append("No mitigation steps specified.")
    md.append("")

    # 8. Analytical Limitations & Uncertainty Statement
    md.append("## 8. Analytical Limitations & Forensic Uncertainty Statement")
    if limitations:
        for l in limitations:
            md.append(f"- {l}")
    else:
        md.append("- Analysis is constrained strictly to telemetry captured within the laboratory environment.")
        md.append("- Timestamps reflect laboratory system clock without external NTP sync.")
    md.append("")

    return "\n".join(md)


def format_html_report(data: Dict[str, Any]) -> str:
    """Render a print-ready, high-aesthetic HTML forensic report."""
    case = data.get("case", {})
    evidence_list = data.get("evidence", [])
    timeline = data.get("timeline", [])
    detections = data.get("detections", [])
    findings = data.get("findings", [])
    mitigations = data.get("mitigations", [])
    limitations = data.get("limitations", [])

    evidence_rows = "".join([
        f"""<tr>
            <td><code>{html.escape(str(ev.get('id', '-')))}</code></td>
            <td><code>{html.escape(str(ev.get('source_path', '-')))}</code></td>
            <td>{html.escape(str(ev.get('collected_at', '-')))}</td>
            <td>{ev.get('size_bytes', 0)} B</td>
            <td class="mono-hash">{html.escape(str(ev.get('sha256', '-')))}</td>
            <td><span class="badge badge-success">{html.escape(str(ev.get('status', 'VERIFIED')))}</span></td>
        </tr>"""
        for ev in evidence_list
    ])

    timeline_rows = "".join([
        f"""<tr>
            <td><code>{html.escape(str(tl.get('timestamp', '-')))}</code></td>
            <td><span class="badge badge-stage">{html.escape(str(tl.get('stage', '-')))}</span></td>
            <td><span class="badge badge-{str(tl.get('severity', 'info')).lower()}">{html.escape(str(tl.get('severity', '-')))}</span></td>
            <td>{html.escape(str(tl.get('description', '-')))}</td>
            <td><code>{html.escape(str(tl.get('source_ref', '-')))}</code></td>
        </tr>"""
        for tl in timeline
    ])

    detection_rows = "".join([
        f"""<tr>
            <td><code>{html.escape(str(d.get('rule_id', '-')))}</code></td>
            <td><strong>{html.escape(str(d.get('rule_name', '-')))}</strong></td>
            <td><code>{html.escape(str(d.get('mitre_id', '-')))}</code></td>
            <td><span class="badge badge-{str(d.get('severity', 'high')).lower()}">{html.escape(str(d.get('severity', '-')))}</span></td>
            <td>{d.get('confidence', 1.0)*100:.0f}%</td>
            <td><code>{html.escape(str(d.get('artifact_id', '-')))}</code></td>
        </tr>"""
        for d in detections
    ])

    findings_cards = "".join([
        f"""<div class="finding-card">
            <div class="finding-header">
                <div>
                    <span class="badge badge-{str(f.get('severity', 'high')).lower()}">{html.escape(str(f.get('severity', '-'))).upper()}</span>
                    <span class="badge badge-stage">{html.escape(str(f.get('stage', '-')))}</span>
                    <strong style="margin-left: 10px;">{html.escape(str(f.get('title', 'Untitled')))}</strong>
                </div>
                <code style="font-size: 11px;">{html.escape(str(f.get('id', '-')))}</code>
            </div>
            <p style="margin: 10px 0; color: #334155; line-height: 1.5;">{html.escape(str(f.get('description', '-')))}</p>
            <div class="evidence-trace">
                <strong>Supporting Evidence Citing:</strong>
                <ul>
                    {"".join([f"<li><code>{html.escape(str(r.get('artifact_name', '-')))}</code> (SHA256: <code>{html.escape(str(r.get('sha256', '-'))[:16])}...</code>) — Line {r.get('line_number', 'N/A')} [{r.get('snippet', '')}]</li>" for r in f.get('evidence_references', [])])}
                </ul>
            </div>
        </div>"""
        for f in findings
    ])

    mitigation_items = "".join([
        f"""<li>
            <strong>{html.escape(str(m.get('title', 'Remediation')))}</strong> (<code>{html.escape(str(m.get('target_component', 'System')))}</code>)<br/>
            <span>{html.escape(str(m.get('remediation', '-')))}</span>
        </li>"""
        for m in mitigations
    ])

    limitation_items = "".join([
        f"<li>{html.escape(str(l))}</li>" for l in limitations
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(str(data.get('title', 'Forensic Incident Report')))}</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0f172a;
        background: #f8fafc;
        margin: 0;
        padding: 40px;
    }}
    .report-container {{
        max-width: 960px;
        margin: 0 auto;
        background: #ffffff;
        padding: 48px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    header {{
        border-bottom: 2px solid #0284c7;
        padding-bottom: 24px;
        margin-bottom: 32px;
    }}
    h1 {{
        margin: 0 0 8px 0;
        font-size: 26px;
        color: #0369a1;
        letter-spacing: -0.5px;
    }}
    .meta-bar {{
        font-size: 13px;
        color: #64748b;
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 12px;
    }}
    h2 {{
        font-size: 18px;
        color: #0f172a;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 8px;
        margin-top: 36px;
        margin-bottom: 16px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin: 16px 0;
    }}
    th, td {{
        padding: 10px 12px;
        border: 1px solid #e2e8f0;
        text-align: left;
    }}
    th {{
        background: #f1f5f9;
        font-weight: 600;
        color: #334155;
    }}
    .mono-hash {{
        font-family: monospace;
        font-size: 11px;
        color: #0369a1;
        word-break: break-all;
    }}
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }}
    .badge-critical {{ background: #fee2e2; color: #b91c1c; }}
    .badge-high {{ background: #ffedd5; color: #c2410c; }}
    .badge-medium {{ background: #fef9c3; color: #a16207; }}
    .badge-low {{ background: #e0f2fe; color: #0369a1; }}
    .badge-info {{ background: #f1f5f9; color: #475569; }}
    .badge-success {{ background: #dcfce7; color: #15803d; }}
    .badge-stage {{ background: #ede9fe; color: #6d28d9; }}
    .finding-card {{
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
        background: #ffffff;
    }}
    .finding-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed #e2e8f0;
        padding-bottom: 8px;
    }}
    .evidence-trace {{
        background: #f8fafc;
        border-left: 3px solid #0284c7;
        padding: 8px 12px;
        margin-top: 10px;
        font-size: 12px;
    }}
    @media print {{
        body {{ background: #ffffff; padding: 0; }}
        .report-container {{ box-shadow: none; padding: 0; }}
    }}
</style>
</head>
<body>
<div class="report-container">
    <header>
        <h1>{html.escape(str(data.get('title', 'Forensic Analysis Report')))}</h1>
        <div class="meta-bar">
            <span><strong>Case:</strong> {html.escape(str(case.get('id', '-')))} ({html.escape(str(case.get('title', '-')))})</span>
            <span><strong>Generated:</strong> {html.escape(str(data.get('generated_at', 'UTC')))}</span>
            <span><strong>Classification:</strong> {html.escape(str(data.get('classification', 'CONFIDENTIAL')))}</span>
        </div>
    </header>

    <h2>1. Executive Summary</h2>
    <p style="line-height: 1.6; color: #334155;">{html.escape(str(data.get('executive_summary', '')))}</p>

    <h2>2. Evidence Inventory & Cryptographic Integrity</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Source Artifact</th>
                <th>Ingested</th>
                <th>Size</th>
                <th>SHA-256 Hash</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {evidence_rows}
        </tbody>
    </table>

    <h2>3. Chronological Incident Timeline</h2>
    <table>
        <thead>
            <tr>
                <th>Timestamp (UTC)</th>
                <th>Stage</th>
                <th>Severity</th>
                <th>Event Description</th>
                <th>Source</th>
            </tr>
        </thead>
        <tbody>
            {timeline_rows}
        </tbody>
    </table>

    <h2>4. Detections & Automated Analysis</h2>
    <table>
        <thead>
            <tr>
                <th>Rule ID</th>
                <th>Rule Name</th>
                <th>MITRE ATT&CK</th>
                <th>Severity</th>
                <th>Confidence</th>
                <th>Source Artifact</th>
            </tr>
        </thead>
        <tbody>
            {detection_rows}
        </tbody>
    </table>

    <h2>5. Detailed Forensic Findings</h2>
    {findings_cards}

    <h2>6. Security Remediation & Mitigation Recommendations</h2>
    <ol style="line-height: 1.8; color: #334155;">
        {mitigation_items}
    </ol>

    <h2>7. Limitations & Uncertainty Statement</h2>
    <ul style="line-height: 1.6; color: #64748b; font-size: 13px;">
        {limitation_items}
    </ul>
</div>
</body>
</html>
"""
