"""ForensiWeb — Phase 03 Frontend Verification Protocol.

Validates that all features of Phase 3 are implemented according to
design.md and architecture.md before Phase 3 completion sign-off:
- F01: Frontend Bootstrap
- F02: Design Tokens
- F03: Typography and Global Styles
- F04: Core UI Components
- F05: Application Shell
- F06: Sidebar and Navigation
- F07: Top Navigation
- F08: Loading/Empty/Error States
- F09: Responsive and Accessibility Foundation
- F10: Scope and Premature Implementation Guard
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = REPO_ROOT / "apps" / "frontend"


def check(name: str, condition: bool, details: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    msg = f"[{status}] {name}"
    if details and not condition:
        msg += f" -> {details}"
    print(msg)
    return condition


def verify_f01_bootstrap() -> bool:
    pkg_json = FRONTEND_DIR / "package.json"
    index_html = FRONTEND_DIR / "index.html"
    main_tsx = FRONTEND_DIR / "src" / "main.tsx"
    app_tsx = FRONTEND_DIR / "src" / "App.tsx"
    dist_html = FRONTEND_DIR / "dist" / "index.html"

    files_ok = all(f.is_file() for f in [pkg_json, index_html, main_tsx, app_tsx, dist_html])
    return check("F01: Frontend Bootstrap", files_ok, "Missing bootstrap or dist files")


def verify_f02_design_tokens() -> bool:
    tokens_ts = FRONTEND_DIR / "src" / "types" / "tokens.ts"
    tailwind_cfg = FRONTEND_DIR / "tailwind.config.js"

    if not tokens_ts.is_file() or not tailwind_cfg.is_file():
        return check("F02: Design Tokens", False, "Missing tokens.ts or tailwind.config.js")

    tokens_content = tokens_ts.read_text(encoding="utf-8")
    tw_content = tailwind_cfg.read_text(encoding="utf-8")

    has_surfaces = "#050B14" in tokens_content and "#050B14" in tw_content
    has_accents = "#2F80FF" in tokens_content and "#22D3EE" in tokens_content
    has_critical = "#EF4444" in tokens_content and "#EF4444" in tw_content

    return check("F02: Design Tokens", has_surfaces and has_accents and has_critical)


def verify_f03_typography() -> bool:
    index_css = FRONTEND_DIR / "src" / "index.css"
    index_html = FRONTEND_DIR / "index.html"

    if not index_css.is_file() or not index_html.is_file():
        return check("F03: Typography and Global Styles", False, "Missing index.css or index.html")

    html_content = index_html.read_text(encoding="utf-8")
    css_content = index_css.read_text(encoding="utf-8")

    has_fonts = "Inter" in html_content and "JetBrains+Mono" in html_content
    has_custom_styles = "cyber-grid" in css_content and "focus-visible" in css_content

    return check("F03: Typography and Global Styles", has_fonts and has_custom_styles)


def verify_f04_core_components() -> bool:
    components = [
        FRONTEND_DIR / "src" / "components" / "common" / "Button.tsx",
        FRONTEND_DIR / "src" / "components" / "common" / "Badge.tsx",
        FRONTEND_DIR / "src" / "components" / "common" / "Card.tsx",
        FRONTEND_DIR / "src" / "components" / "common" / "Input.tsx",
        FRONTEND_DIR / "src" / "components" / "common" / "MetricCard.tsx",
        FRONTEND_DIR / "src" / "components" / "common" / "Modal.tsx",
    ]
    all_exist = all(c.is_file() for c in components)
    return check("F04: Core UI Components", all_exist, f"Missing components: {[c.name for c in components if not c.is_file()]}")


def verify_f05_application_shell() -> bool:
    shell_file = FRONTEND_DIR / "src" / "layouts" / "AppShell.tsx"
    if not shell_file.is_file():
        return check("F05: Application Shell", False, "Missing AppShell.tsx")

    content = shell_file.read_text(encoding="utf-8")
    has_structure = "Sidebar" in content and "TopNav" in content and "Skip to main content" in content
    return check("F05: Application Shell", has_structure)


def verify_f06_sidebar_navigation() -> bool:
    sidebar_file = FRONTEND_DIR / "src" / "layouts" / "Sidebar.tsx"
    if not sidebar_file.is_file():
        return check("F06: Sidebar and Navigation", False, "Missing Sidebar.tsx")

    content = sidebar_file.read_text(encoding="utf-8")
    has_sections = (
        "INVESTIGATION" in content
        and "ANALYSIS" in content
        and "LAB" in content
        and "SYSTEM" in content
        and "onToggleCollapse" in content
    )
    return check("F06: Sidebar and Navigation", has_sections)


def verify_f07_top_navigation() -> bool:
    topnav_file = FRONTEND_DIR / "src" / "layouts" / "TopNav.tsx"
    if not topnav_file.is_file():
        return check("F07: Top Navigation", False, "Missing TopNav.tsx")

    content = topnav_file.read_text(encoding="utf-8")
    has_features = "activeCase" in content and "Search" in content and "LAB:" in content
    return check("F07: Top Navigation", has_features)


def verify_f08_state_components() -> bool:
    states = [
        FRONTEND_DIR / "src" / "components" / "states" / "LoadingState.tsx",
        FRONTEND_DIR / "src" / "components" / "states" / "EmptyState.tsx",
        FRONTEND_DIR / "src" / "components" / "states" / "ErrorState.tsx",
    ]
    all_exist = all(s.is_file() for s in states)
    return check("F08: Loading/Empty/Error States", all_exist)


def verify_f09_accessibility_responsive() -> bool:
    shell = (FRONTEND_DIR / "src" / "layouts" / "AppShell.tsx").read_text(encoding="utf-8")
    modal = (FRONTEND_DIR / "src" / "components" / "common" / "Modal.tsx").read_text(encoding="utf-8")

    has_aria = 'role="dialog"' in modal and 'aria-modal="true"' in modal
    has_skip = "Skip to main content" in shell
    return check("F09: Responsive and Accessibility Foundation", has_aria and has_skip)


def verify_f10_vitest_and_premature_guard() -> bool:
    test_file = FRONTEND_DIR / "src" / "test" / "components.test.tsx"
    has_tests = test_file.is_file()

    # Guard: ensure no premature Phase 4/9/14 features leaked
    prohibited_files = [
        "apps/vulnerable-web-app/app/routes/lfi.py",
        "packages/detection-engine/rules/lfi_rule.py",
    ]
    premature_existing = [f for f in prohibited_files if (REPO_ROOT / f).is_file()]

    return check(
        "F10: Frontend Test Suite & Scope Guard",
        has_tests and len(premature_existing) == 0,
        f"Premature files found: {premature_existing}",
    )


def main() -> int:
    print("=================================================================")
    print("ForensiWeb — PHASE 03: Frontend Foundation Verification Protocol")
    print("=================================================================\n")

    checks = [
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
    ]

    all_passed = True
    for c in checks:
        if not c():
            all_passed = False

    print("\n-----------------------------------------------------------------")
    if all_passed:
        print("PHASE 03 VERIFICATION RESULT: ALL ACCEPTANCE CRITERIA PASSED.")
        print("Phase 03 is eligible for completion sign-off.")
        print("-----------------------------------------------------------------")
        return 0
    else:
        print("PHASE 03 VERIFICATION RESULT: FAILED.")
        print("-----------------------------------------------------------------")
        return 1


if __name__ == "__main__":
    sys.exit(main())
