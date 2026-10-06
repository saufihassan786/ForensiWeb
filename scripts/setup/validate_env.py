#!/usr/bin/env python3
"""
ForensiWeb Environment Configuration Validator.

Validates environment configuration files (.env, .env.example) or runtime
environment variables against the schema specified in `docs/architecture.md` (Section 32)
and security isolation boundaries in `docs/rules.md`.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

VALID_ENVIRONMENTS = {"development", "testing", "production"}
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_LOG_FORMATS = {"json", "console"}
VALID_HASH_ALGORITHMS = {"SHA-256", "sha-256", "sha256", "SHA256"}

# Core schema defining required fields, types, and constraints across 6 categories
ENVIRONMENT_SCHEMA = {
    # 1. Application
    "ENVIRONMENT": {"type": str, "required": True, "allowed": VALID_ENVIRONMENTS},
    "DEBUG": {"type": bool, "required": True},
    "API_HOST": {"type": str, "required": True},
    "API_PORT": {"type": int, "required": True, "min": 1, "max": 65535},
    "API_PREFIX": {"type": str, "required": True},
    "CORS_ORIGINS": {"type": str, "required": True},
    "FRONTEND_PORT": {"type": int, "required": True, "min": 1, "max": 65535},
    # 2. Database
    "POSTGRES_HOST": {"type": str, "required": True},
    "POSTGRES_PORT": {"type": int, "required": True, "min": 1, "max": 65535},
    "POSTGRES_DB": {"type": str, "required": True},
    "POSTGRES_USER": {"type": str, "required": True},
    "POSTGRES_PASSWORD": {"type": str, "required": True},
    "DATABASE_URL": {"type": str, "required": True},
    "DATABASE_URL_SYNC": {"type": str, "required": True},
    # 3. Evidence Storage
    "EVIDENCE_ROOT_DIR": {"type": str, "required": True},
    "EVIDENCE_ORIGINAL_DIR": {"type": str, "required": True},
    "EVIDENCE_WORKING_DIR": {"type": str, "required": True},
    "EVIDENCE_DERIVED_DIR": {"type": str, "required": True},
    "REPORTS_DIR": {"type": str, "required": True},
    "MAX_EVIDENCE_UPLOAD_MB": {"type": int, "required": True, "min": 1},
    # 4. Security
    "SECRET_KEY": {"type": str, "required": True, "min_len": 16},
    "JWT_ALGORITHM": {"type": str, "required": True},
    "ACCESS_TOKEN_EXPIRE_MINUTES": {"type": int, "required": True, "min": 1},
    "INTEGRITY_HASH_ALGORITHM": {"type": str, "required": True, "allowed": VALID_HASH_ALGORITHMS},
    # 5. Laboratory
    "LAB_NETWORK_NAME": {"type": str, "required": True},
    "LAB_VULN_APP_HOST": {"type": str, "required": True},
    "LAB_VULN_APP_PORT": {"type": int, "required": True, "min": 1, "max": 65535},
    "LAB_CONTAINER_MEMORY_LIMIT": {"type": str, "required": True},
    "LAB_CONTAINER_CPU_LIMIT": {"type": str, "required": True},
    "LAB_DATA_DIR": {"type": str, "required": True},
    "LAB_NETWORK_INTERNAL_ONLY": {"type": bool, "required": True},
    # 6. Logging
    "LOG_LEVEL": {"type": str, "required": True, "allowed": VALID_LOG_LEVELS},
    "LOG_FORMAT": {"type": str, "required": True, "allowed": VALID_LOG_FORMATS},
    "LOG_DIR": {"type": str, "required": True},
}


class EnvironmentValidationError(Exception):
    """Raised when environment configuration fails validation."""

    def __init__(self, errors: List[str], warnings: Optional[List[str]] = None):
        self.errors = errors
        self.warnings = warnings or []
        super().__init__(f"Environment configuration validation failed with {len(errors)} error(s): " + "; ".join(errors))


@dataclass
class ValidationReport:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parsed_config: Dict[str, Any] = field(default_factory=dict)


def parse_env_content(content: str) -> Dict[str, str]:
    """Parse raw key=value content from a .env file string."""
    env_dict: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        # Skip empty lines or comment lines
        if not line or line.startswith("#"):
            continue
        # Split on first '='
        if "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            # Strip outer quotes if present
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            env_dict[key] = val
    return env_dict


def parse_env_file(file_path: Path | str) -> Dict[str, str]:
    """Read and parse a .env or .env.example file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    content = path.read_text(encoding="utf-8")
    return parse_env_content(content)


def validate_config(raw_config: Dict[str, str], allow_example_secrets: bool = True) -> ValidationReport:
    """
    Validate a dictionary of raw string configuration values against ENVIRONMENT_SCHEMA.

    Checks:
    - Required variables exist.
    - Type casting (int, bool, string).
    - Allowed values / enums.
    - Ranges and constraints.
    - Laboratory isolation and port binding restrictions.
    """
    errors: List[str] = []
    warnings: List[str] = []
    parsed_config: Dict[str, Any] = {}

    # Check for missing required keys
    for key, spec in ENVIRONMENT_SCHEMA.items():
        if spec.get("required") and (key not in raw_config or raw_config[key] == ""):
            errors.append(f"Missing required environment variable: '{key}'")
            continue

        if key not in raw_config:
            continue

        raw_val = raw_config[key]
        expected_type = spec["type"]

        # Type conversion and validation
        if expected_type is bool:
            lower = raw_val.lower()
            if lower in ("true", "1", "yes"):
                parsed_config[key] = True
            elif lower in ("false", "0", "no"):
                parsed_config[key] = False
            else:
                errors.append(f"Invalid boolean value for '{key}': '{raw_val}' (must be true/false)")
                continue

        elif expected_type is int:
            try:
                int_val = int(raw_val)
                parsed_config[key] = int_val
                if "min" in spec and int_val < spec["min"]:
                    errors.append(f"'{key}' value {int_val} is below minimum allowed {spec['min']}")
                if "max" in spec and int_val > spec["max"]:
                    errors.append(f"'{key}' value {int_val} exceeds maximum allowed {spec['max']}")
            except ValueError:
                errors.append(f"Invalid integer value for '{key}': '{raw_val}'")
                continue

        elif expected_type is str:
            parsed_config[key] = raw_val
            if "min_len" in spec and len(raw_val) < spec["min_len"]:
                errors.append(f"'{key}' length ({len(raw_val)}) is shorter than minimum required {spec['min_len']}")

        # Enum / Allowed set check
        if "allowed" in spec:
            allowed = spec["allowed"]
            val_to_check = parsed_config.get(key, raw_val)
            if val_to_check not in allowed:
                errors.append(f"Invalid value for '{key}': '{val_to_check}'. Must be one of: {sorted(list(allowed))}")

    # Specific security & isolation validations
    api_host = raw_config.get("API_HOST", "")
    env_mode = raw_config.get("ENVIRONMENT", "development")
    if env_mode == "development" and api_host == "0.0.0.0":
        warnings.append(
            "Security Warning: API_HOST is set to '0.0.0.0' in development. "
            "Use '127.0.0.1' to preserve laboratory isolation."
        )

    # Check for insecure default secret key in production
    secret_key = raw_config.get("SECRET_KEY", "")
    if env_mode == "production" and ("change-me" in secret_key or "insecure" in secret_key):
        errors.append("Production Security Error: Insecure default SECRET_KEY detected in production environment.")

    # Lab network non-egress check
    lab_internal = raw_config.get("LAB_NETWORK_INTERNAL_ONLY", "")
    if lab_internal.lower() not in ("true", "1", "yes"):
        warnings.append(
            "Forensic Isolation Warning: LAB_NETWORK_INTERNAL_ONLY is not true. "
            "Laboratory containers must not have internet access."
        )

    is_valid = len(errors) == 0
    return ValidationReport(is_valid=is_valid, errors=errors, warnings=warnings, parsed_config=parsed_config)


def validate_environment(
    env_file: Optional[Path | str] = None,
    allow_example_secrets: bool = True,
    raise_on_error: bool = False
) -> ValidationReport:
    """
    Validate environment from a specified file or fall back to os.environ.
    """
    if env_file:
        raw_config = parse_env_file(env_file)
    else:
        # Pull known keys from system environment
        raw_config = {k: os.environ[k] for k in ENVIRONMENT_SCHEMA.keys() if k in os.environ}

    report = validate_config(raw_config, allow_example_secrets=allow_example_secrets)

    if not report.is_valid and raise_on_error:
        raise EnvironmentValidationError(report.errors, report.warnings)

    return report


def main() -> int:
    """CLI entrypoint for environment validation."""
    target_file = REPO_ROOT / ".env"
    example_file = REPO_ROOT / ".env.example"

    if len(sys.argv) > 1 and sys.argv[1] == "--check-example":
        print(f"Validating template: {example_file}")
        report = validate_environment(example_file, allow_example_secrets=True)
    elif target_file.is_file():
        print(f"Validating active environment: {target_file}")
        report = validate_environment(target_file, allow_example_secrets=False)
    elif example_file.is_file():
        print(f"Notice: .env not found. Validating template {example_file} instead.")
        report = validate_environment(example_file, allow_example_secrets=True)
    else:
        print("Error: Neither .env nor .env.example found.", file=sys.stderr)
        return 1

    for warn in report.warnings:
        print(f"[WARN] {warn}", file=sys.stderr)

    if report.is_valid:
        print(f"SUCCESS: Environment configuration is valid ({len(report.parsed_config)} variables checked).")
        return 0
    else:
        print(f"FAILURE: {len(report.errors)} configuration error(s) detected:", file=sys.stderr)
        for err in report.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
