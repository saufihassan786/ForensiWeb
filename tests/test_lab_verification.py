"""Laboratory Environment Verification Tests (PHASE-05-F07) for ForensiWeb.

Executes the Phase 5 Isolated Laboratory Environment Verification Protocol via pytest,
verifying that all acceptance criteria across the 7 features of Phase 5 pass cleanly.
"""

from __future__ import annotations

from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.verify_lab import (
    verify_f01_container_topology,
    verify_f02_dedicated_lab_network,
    verify_f03_supporting_services,
    verify_f04_scenario_configuration,
    verify_f05_lab_reset,
    verify_f06_lab_health_status,
    verify_f07_reproducibility_verification,
)


@pytest.mark.lab
def test_p05_f01_container_topology():
    assert verify_f01_container_topology(), "PHASE-05-F01 Lab container topology check failed"


@pytest.mark.lab
def test_p05_f02_dedicated_lab_network():
    assert verify_f02_dedicated_lab_network(), "PHASE-05-F02 Dedicated lab network check failed"


@pytest.mark.lab
def test_p05_f03_supporting_services():
    assert verify_f03_supporting_services(), "PHASE-05-F03 Supporting services check failed"


@pytest.mark.lab
def test_p05_f04_scenario_configuration():
    assert verify_f04_scenario_configuration(), "PHASE-05-F04 Scenario configuration check failed"


@pytest.mark.lab
def test_p05_f05_lab_reset():
    assert verify_f05_lab_reset(), "PHASE-05-F05 Lab reset check failed"


@pytest.mark.lab
def test_p05_f06_lab_health_status():
    assert verify_f06_lab_health_status(), "PHASE-05-F06 Lab health status check failed"


@pytest.mark.lab
def test_p05_f07_reproducibility_verification():
    assert verify_f07_reproducibility_verification(), "PHASE-05-F07 Reproducibility verification check failed"
