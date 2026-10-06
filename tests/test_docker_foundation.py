"""
Test Docker Foundation for ForensiWeb.

Validates PHASE-01-F07: Docker Foundation.
Verifies:
- docker-compose.yml exists, is well-formed, and passes docker compose config validation.
- All core services exist: postgres, api, frontend, vulnerable-app.
- Network isolation boundaries are enforced: forensiweb-lab-net is configured as internal: true.
- Security constraints: all ports bind strictly to 127.0.0.1; vulnerable-app has cap_drop: ALL.
- Dockerfiles and .dockerignore files exist for all apps.
- lab/docker/README.md documents container architecture.
"""

from pathlib import Path
import subprocess
import shutil
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
ROOT_DOCKERIGNORE = REPO_ROOT / ".dockerignore"
LAB_DOCKER_README = REPO_ROOT / "lab" / "docker" / "README.md"

REQUIRED_DOCKERFILES = [
    "apps/api/Dockerfile",
    "apps/frontend/Dockerfile",
    "apps/vulnerable-web-app/Dockerfile",
]

REQUIRED_DOCKERIGNORES = [
    ".dockerignore",
    "apps/api/.dockerignore",
    "apps/frontend/.dockerignore",
    "apps/vulnerable-web-app/.dockerignore",
]


@pytest.mark.unit
def test_docker_compose_file_exists_and_non_empty():
    """Verify that root docker-compose.yml exists and has substantive content."""
    assert COMPOSE_FILE.is_file(), "docker-compose.yml is missing from repository root"
    content = COMPOSE_FILE.read_text(encoding="utf-8")
    assert len(content.strip()) > 500, "docker-compose.yml is too short or empty"


@pytest.mark.unit
@pytest.mark.parametrize("dockerfile_rel_path", REQUIRED_DOCKERFILES)
def test_app_dockerfiles_exist(dockerfile_rel_path):
    """Verify Dockerfiles exist for api, frontend, and vulnerable-web-app."""
    path = REPO_ROOT / dockerfile_rel_path
    assert path.is_file(), f"Missing required Dockerfile: {dockerfile_rel_path}"
    content = path.read_text(encoding="utf-8")
    assert "FROM " in content, f"Dockerfile does not specify a base image: {dockerfile_rel_path}"


@pytest.mark.unit
@pytest.mark.parametrize("dockerignore_rel_path", REQUIRED_DOCKERIGNORES)
def test_dockerignore_files_exist(dockerignore_rel_path):
    """Verify .dockerignore files exist to prevent cache and secret leakage into containers."""
    path = REPO_ROOT / dockerignore_rel_path
    assert path.is_file(), f"Missing required .dockerignore: {dockerignore_rel_path}"


@pytest.mark.unit
def test_lab_docker_documentation_exists():
    """Verify lab/docker/README.md documents container topology and isolation."""
    assert LAB_DOCKER_README.is_file(), "lab/docker/README.md is missing"
    content = LAB_DOCKER_README.read_text(encoding="utf-8")
    assert "forensiweb-lab-net" in content
    assert "internal: true" in content
    assert "cap_drop" in content


@pytest.mark.unit
def test_docker_compose_config_validation():
    """Verify docker-compose.yml passes compose validation."""
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        pytest.skip("Docker CLI not available on system")

    result = subprocess.run(
        ["docker", "compose", "config", "-q"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    assert result.returncode == 0, f"docker compose config validation failed: {result.stderr}"


@pytest.mark.unit
def test_compose_service_topology():
    """Verify compose file defines the four expected core services."""
    content = COMPOSE_FILE.read_text(encoding="utf-8")
    for service in ["postgres:", "api:", "frontend:", "vulnerable-app:"]:
        assert service in content, f"docker-compose.yml is missing service: '{service}'"


@pytest.mark.unit
def test_compose_network_isolation_configuration():
    """Verify forensiweb-lab-net is defined with internal: true."""
    content = COMPOSE_FILE.read_text(encoding="utf-8")
    assert "forensiweb-lab-net:" in content
    assert "forensiweb-mgmt-net:" in content
    assert "internal: true" in content, "Lab network must be configured with internal: true"


@pytest.mark.unit
def test_compose_security_ports_bound_to_localhost():
    """Verify all published ports in docker-compose.yml bind to 127.0.0.1."""
    content = COMPOSE_FILE.read_text(encoding="utf-8")
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("- \"") and (":5432\"" in line or ":8000\"" in line or ":5173\"" in line or ":5000\"" in line):
            assert "127.0.0.1:" in line, f"Exposed port is not bound to 127.0.0.1: {line}"
            assert "0.0.0.0:" not in line, f"Port bound to 0.0.0.0 violates security: {line}"


@pytest.mark.unit
def test_compose_vulnerable_app_security_constraints():
    """Verify vulnerable-app service drops capabilities and limits resources."""
    content = COMPOSE_FILE.read_text(encoding="utf-8")
    assert "cap_drop:" in content
    assert "- ALL" in content
    assert "memory: 512M" in content
