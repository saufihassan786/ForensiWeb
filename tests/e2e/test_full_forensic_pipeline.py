"""End-to-End Integration Test Suite (PHASE 16).

Verifies:
- PHASE-16-F01: Lab-to-Evidence Integration
- PHASE-16-F02: Evidence-to-Processing Integration
- PHASE-16-F03: Processing-to-Event Integration
- PHASE-16-F04: Event-to-Detection Integration
- PHASE-16-F05: Detection-to-Correlation Integration
- PHASE-16-F06: Correlation-to-Timeline Integration
- PHASE-16-F07: Timeline-to-Investigation Integration
- PHASE-16-F08: Investigation-to-Report Integration
- PHASE-16-F09: Mitigation-to-Verification Integration
- PHASE-16-F10: Full Workflow Verification
"""

import pytest
from pathlib import Path

from scripts.testing.run_e2e_pipeline import EndToEndForensicPipeline


@pytest.mark.e2e
def test_p16_complete_forensic_workflow(tmp_path):
    """Execute and verify complete end-to-end forensic lifecycle from scenario to report & mitigation."""
    pipeline = EndToEndForensicPipeline(tmp_path)
    result = pipeline.run_complete_lifecycle()

    # 1. Verification of data flow milestones
    assert result["evidence_count"] == 2
    assert result["normalized_event_count"] >= 6
    assert result["detection_count"] >= 2
    assert result["timeline_entry_count"] >= 2
    assert result["finding_count"] == 3

    # 2. Verification of Report Generation (PHASE-16-F08)
    report_file = Path(result["report_path"])
    assert report_file.exists()
    assert report_file.stat().st_size > 500

    # 3. Verification of Mitigation Application (PHASE-16-F09)
    assert result["mitigation_verified"] is True


@pytest.mark.e2e
def test_p16_reproducibility(tmp_path):
    """Verify that multiple consecutive runs yield deterministic, reproducible telemetry."""
    pipeline_a = EndToEndForensicPipeline(tmp_path / "run_a")
    res_a = pipeline_a.run_complete_lifecycle()

    pipeline_b = EndToEndForensicPipeline(tmp_path / "run_b")
    res_b = pipeline_b.run_complete_lifecycle()

    assert res_a["evidence_count"] == res_b["evidence_count"]
    assert res_a["detection_count"] == res_b["detection_count"]
    assert res_a["mitigation_verified"] == res_b["mitigation_verified"]
