"""Unit tests for Backend Application Bootstrap (PHASE-02-F01).

Validates:
- Application instantiation via factory pattern
- App metadata and OpenAPI schema configuration
- Lifespan context manager execution (startup/shutdown)
- Root metadata endpoint ('/')
- CORS middleware behavior
- Documentation endpoint accessibility
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app, lifespan, app


@pytest.fixture
def client() -> TestClient:
    """Fixture providing a synchronized TestClient for the default application."""
    test_app = create_app(title="ForensiWeb API Test", version="0.1.0-test")
    with TestClient(test_app) as test_client:
        yield test_client


def test_app_instance_defaults() -> None:
    """Verify that the module-level app is an instantiated FastAPI instance with default metadata."""
    assert isinstance(app, FastAPI)
    assert app.title == "ForensiWeb API"
    assert app.version == "0.1.0"
    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"


def test_create_app_customization() -> None:
    """Verify that create_app respects custom configuration parameters."""
    custom_app = create_app(
        title="Custom ForensiWeb",
        version="0.2.0",
        description="Custom Test Suite Instance",
        cors_origins=["https://custom-domain.local"],
        debug=True,
    )
    assert custom_app.title == "Custom ForensiWeb"
    assert custom_app.version == "0.2.0"
    assert custom_app.description == "Custom Test Suite Instance"
    assert custom_app.debug is True


def test_root_endpoint_metadata(client: TestClient) -> None:
    """Verify GET / returns 200 OK with expected metadata structure."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "ForensiWeb API Test"
    assert data["version"] == "0.1.0-test"
    assert data["status"] == "online"
    assert "environment" in data
    assert data["docs_url"] == "/docs"
    assert data["openapi_url"] == "/openapi.json"
    assert "api_prefix" in data


def test_openapi_schema_generation() -> None:
    """Verify that the OpenAPI JSON specification is generated correctly."""
    schema = app.openapi()
    assert isinstance(schema, dict)
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "ForensiWeb API"
    assert schema["info"]["version"] == "0.1.0"
    assert "/" in schema["paths"]


def test_docs_endpoints(client: TestClient) -> None:
    """Verify that OpenAPI and Swagger documentation endpoints return 200 OK."""
    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    assert openapi_resp.headers["content-type"] == "application/json"

    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200
    assert "html" in docs_resp.headers["content-type"]


def test_cors_middleware_headers(client: TestClient) -> None:
    """Verify that CORS preflight and request headers are properly handled."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.anyio
async def test_lifespan_lifecycle() -> None:
    """Verify that the lifespan context manager executes startup and shutdown cleanly."""
    test_app = FastAPI()
    async with lifespan(test_app):
        # In-context execution simulating active application lifecycle
        pass
