"""Frontend Verification Tests (PHASE-03-F10) for ForensiWeb.

Executes the Phase 3 Frontend Foundation Verification Protocol via pytest,
verifying that all acceptance criteria across the 10 features of Phase 3 pass cleanly.
"""

from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.testing.verify_frontend import (
    verify_f01_bootstrap,
    verify_f02_design_tokens,
    verify_f03_typography,
    verify_f04_core_components,
    verify_f05_application_shell,
    verify_f06_sidebar_navigation,
    verify_f07_top_navigation,
    verify_f08_state_components,
    verify_f09_accessibility_responsive,
    verify_f10_vitest_and_premature_guard,
)


@pytest.mark.unit
def test_f01_frontend_bootstrap():
    assert verify_f01_bootstrap(), "F01 Frontend Bootstrap check failed"


@pytest.mark.unit
def test_f02_design_tokens():
    assert verify_f02_design_tokens(), "F02 Design Tokens check failed"


@pytest.mark.unit
def test_f03_typography():
    assert verify_f03_typography(), "F03 Typography and Global Styles check failed"


@pytest.mark.unit
def test_f04_core_components():
    assert verify_f04_core_components(), "F04 Core UI Components check failed"


@pytest.mark.unit
def test_f05_application_shell():
    assert verify_f05_application_shell(), "F05 Application Shell check failed"


@pytest.mark.unit
def test_f06_sidebar_navigation():
    assert verify_f06_sidebar_navigation(), "F06 Sidebar and Navigation check failed"


@pytest.mark.unit
def test_f07_top_navigation():
    assert verify_f07_top_navigation(), "F07 Top Navigation check failed"


@pytest.mark.unit
def test_f08_state_components():
    assert verify_f08_state_components(), "F08 Loading/Empty/Error States check failed"


@pytest.mark.unit
def test_f09_accessibility_responsive():
    assert verify_f09_accessibility_responsive(), "F09 Responsive and Accessibility Foundation check failed"


@pytest.mark.unit
def test_f10_vitest_and_premature_guard():
    assert verify_f10_vitest_and_premature_guard(), "F10 Frontend Test Suite & Scope Guard failed"
