"""
Test Environment Configuration for ForensiWeb.

Validates PHASE-01-F03: Environment Configuration.
Verifies:
- .env.example exists and contains all required categories from docs/architecture.md Section 32.
- No real secrets or production keys are committed.
- Safe default bindings to localhost (127.0.0.1) preserve lab isolation.
- Environment validator correctly parses valid configs and fails safely when required
  variables are missing or invalid.
"""

from pathlib import Path
import pytest
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.setup.validate_env import (
    validate_environment,
    validate_config,
    parse_env_file,
    parse_env_content,
    EnvironmentValidationError,
    ENVIRONMENT_SCHEMA,
)

ENV_EXAMPLE_PATH = REPO_ROOT / ".env.example"


def test_env_example_exists_and_non_empty():
    """Verify that .env.example exists at repo root and has substantive content."""
    assert ENV_EXAMPLE_PATH.is_file(), ".env.example is missing from repository root"
    content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    assert len(content.strip()) > 500, ".env.example appears too brief or empty"


def test_env_example_contains_all_six_categories():
    """Verify all 6 categories defined in architecture.md Section 32 are present."""
    content = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    required_categories = [
        "APPLICATION CONFIGURATION",
        "DATABASE CONFIGURATION",
        "EVIDENCE STORAGE CONFIGURATION",
        "SECURITY",
        "LABORATORY",
        "LOGGING",
    ]
    for category in required_categories:
        assert category in content, f"Missing expected category '{category}' in .env.example"


def test_env_example_parses_successfully():
    """Verify that .env.example parses and satisfies all schema rules cleanly."""
    report = validate_environment(ENV_EXAMPLE_PATH, allow_example_secrets=True)
    assert report.is_valid, f"Validation of .env.example failed: {report.errors}"
    assert len(report.errors) == 0
    assert len(report.parsed_config) >= len(ENVIRONMENT_SCHEMA)


def test_env_example_no_exposed_real_secrets():
    """Verify that placeholder passwords and secret keys indicate they are dummy values."""
    config = parse_env_file(ENV_EXAMPLE_PATH)
    secret_key = config.get("SECRET_KEY", "")
    postgres_pw = config.get("POSTGRES_PASSWORD", "")

    # Must contain placeholder indications
    assert any(term in secret_key.lower() for term in ["change-me", "dev", "placeholder", "secure"]), \
        "SECRET_KEY does not appear to be an obvious placeholder"
    assert any(term in postgres_pw.lower() for term in ["insecure", "dev", "placeholder", "password"]), \
        "POSTGRES_PASSWORD does not appear to be an obvious development placeholder"


def test_env_example_localhost_binding_for_isolation():
    """Verify API_HOST and LAB_VULN_APP_HOST are bound to 127.0.0.1 for isolation."""
    config = parse_env_file(ENV_EXAMPLE_PATH)
    assert config.get("API_HOST") == "127.0.0.1", "API_HOST must bind to 127.0.0.1 in .env.example"
    assert config.get("LAB_VULN_APP_HOST") == "127.0.0.1", "LAB_VULN_APP_HOST must bind to 127.0.0.1"


def test_validator_fails_safely_when_required_variable_missing():
    """Verify that validator fails safely when required environment variables are absent."""
    valid_raw = parse_env_file(ENV_EXAMPLE_PATH)
    
    # Remove critical variables
    incomplete_raw = valid_raw.copy()
    del incomplete_raw["DATABASE_URL"]
    del incomplete_raw["SECRET_KEY"]

    report = validate_config(incomplete_raw)
    assert not report.is_valid
    assert any("DATABASE_URL" in err for err in report.errors)
    assert any("SECRET_KEY" in err for err in report.errors)


def test_validator_fails_safely_on_invalid_types_and_choices():
    """Verify validator rejects invalid ports, invalid log levels, and bad booleans."""
    valid_raw = parse_env_file(ENV_EXAMPLE_PATH)

    # Test invalid port
    bad_port_config = valid_raw.copy()
    bad_port_config["API_PORT"] = "not_a_number"
    report = validate_config(bad_port_config)
    assert not report.is_valid
    assert any("API_PORT" in err for err in report.errors)

    # Test invalid log level
    bad_log_config = valid_raw.copy()
    bad_log_config["LOG_LEVEL"] = "SUPER_VERBOSE"
    report = validate_config(bad_log_config)
    assert not report.is_valid
    assert any("LOG_LEVEL" in err for err in report.errors)

    # Test invalid boolean
    bad_bool_config = valid_raw.copy()
    bad_bool_config["DEBUG"] = "maybe"
    report = validate_config(bad_bool_config)
    assert not report.is_valid
    assert any("DEBUG" in err for err in report.errors)


def test_validator_raises_exception_when_requested():
    """Verify EnvironmentValidationError is raised when raise_on_error is True."""
    with pytest.raises(EnvironmentValidationError) as exc_info:
        validate_config({}, allow_example_secrets=True)
        # Calling validate_environment with missing vars and raise_on_error=True
        validate_environment(env_file=None, raise_on_error=True)
    assert "Environment configuration validation failed" in str(exc_info.value)
