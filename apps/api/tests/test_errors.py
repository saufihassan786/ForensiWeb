"""Unit tests for Centralized Error Handling Framework (PHASE-02-F08).

Validates:
- Structured error response schema matching architecture.md section 31
- Automatic X-Request-ID propagation in headers and error body
- Custom domain exceptions (AppException, EvidenceIntegrityError, NotFoundError)
- Validation errors (422) formatting
- Unhandled internal errors (500) formatting
"""

from __future__ import annotations

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors import EvidenceIntegrityError, NotFoundError
from app.main import create_app


@pytest.fixture
def error_test_client() -> TestClient:
    """Fixture with test routes triggering various exceptions."""
    test_app = create_app()

    router = APIRouter(prefix="/test-errors")

    @router.get("/integrity-error")
    def trigger_integrity_error():
        raise EvidenceIntegrityError("Evidence SHA-256 hash does not match artifact manifest.")

    @router.get("/not-found-error")
    def trigger_not_found():
        raise NotFoundError("Investigation record CASE-999 not found.")

    @router.get("/unhandled-error")
    def trigger_unhandled():
        raise RuntimeError("Unexpected low-level failure.")

    test_app.include_router(router)
    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield client


def test_custom_evidence_integrity_error(error_test_client: TestClient) -> None:
    """Verify EvidenceIntegrityError serializes into structured JSON with EVIDENCE_HASH_MISMATCH code."""
    resp = error_test_client.get("/test-errors/integrity-error")
    assert resp.status_code == 400
    assert "X-Request-ID" in resp.headers

    data = resp.json()
    assert "error" in data
    err = data["error"]
    assert err["code"] == "EVIDENCE_HASH_MISMATCH"
    assert "Evidence SHA-256" in err["message"]
    assert err["request_id"] == resp.headers["X-Request-ID"]


def test_custom_not_found_error(error_test_client: TestClient) -> None:
    """Verify custom NotFoundError serializes with 404 status."""
    resp = error_test_client.get("/test-errors/not-found-error")
    assert resp.status_code == 404
    data = resp.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "CASE-999" in data["error"]["message"]


def test_http_404_routing_error(error_test_client: TestClient) -> None:
    """Verify non-existent routes return structured 404 error."""
    resp = error_test_client.get("/api/v1/cases/non-existent-case-id-12345")
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"


def test_validation_error_formatting(error_test_client: TestClient) -> None:
    """Verify invalid payloads return structured 422 validation details."""
    # POST to /api/v1/cases with missing required field
    resp = error_test_client.post("/api/v1/cases", json={})
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data
    err = data["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "details" in err
    assert "errors" in err["details"]


def test_unhandled_exception_returns_500(error_test_client: TestClient) -> None:
    """Verify unexpected runtime errors are caught and sanitized to 500 without leaking traceback."""
    resp = error_test_client.get("/test-errors/unhandled-error")
    assert resp.status_code == 500
    data = resp.json()
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "unexpected server error" in data["error"]["message"].lower()
