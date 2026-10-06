"""Vulnerable Application Verification Tests (PHASE-04-F10) for ForensiWeb.

Executes the Phase 4 Controlled Vulnerable Application Verification Protocol via pytest,
verifying that all acceptance criteria across the 10 features of Phase 4 pass cleanly.
"""

from __future__ import annotations

from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.verify_vulnerable_app import (
    verify_f01_target_application,
    verify_f02_file_access_and_containment,
    verify_f03_logging_scenario,
    verify_f04_log_poisoning_scenario,
    verify_f05_rce_evidence_scenario,
    verify_f06_post_exploitation_evidence,
    verify_f07_environment_path_scenario,
    verify_f08_scenario_reset,
    verify_f09_expected_artifact_catalogue,
    verify_f10_application_isolation,
)


@pytest.mark.unit
def test_p04_f01_target_application():
    assert verify_f01_target_application(), "PHASE-04-F01 Target application failed"


@pytest.mark.unit
def test_p04_f02_file_access_and_containment():
    assert verify_f02_file_access_and_containment(), "PHASE-04-F02 File access containment failed"


@pytest.mark.unit
def test_p04_f03_logging_scenario():
    assert verify_f03_logging_scenario(), "PHASE-04-F03 Logging scenario failed"


@pytest.mark.unit
def test_p04_f04_log_poisoning_scenario():
    assert verify_f04_log_poisoning_scenario(), "PHASE-04-F04 Log poisoning scenario failed"


@pytest.mark.unit
def test_p04_f05_rce_evidence_scenario():
    assert verify_f05_rce_evidence_scenario(), "PHASE-04-F05 RCE evidence scenario failed"


@pytest.mark.unit
def test_p04_f06_post_exploitation_evidence():
    assert verify_f06_post_exploitation_evidence(), "PHASE-04-F06 Post exploitation evidence failed"


@pytest.mark.unit
def test_p04_f07_environment_path_scenario():
    assert verify_f07_environment_path_scenario(), "PHASE-04-F07 Environment PATH scenario failed"


@pytest.mark.unit
def test_p04_f08_scenario_reset():
    assert verify_f08_scenario_reset(), "PHASE-04-F08 Scenario reset failed"


@pytest.mark.unit
def test_p04_f09_expected_artifact_catalogue():
    assert verify_f09_expected_artifact_catalogue(), "PHASE-04-F09 Artifact catalogue failed"


@pytest.mark.unit
def test_p04_f10_application_isolation():
    assert verify_f10_application_isolation(), "PHASE-04-F10 Application isolation failed"
