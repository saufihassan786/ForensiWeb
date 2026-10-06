"""ForensiWeb Centralized Error Handling Framework (PHASE-02-F08).

Implements:
- Structured error response schema matching architecture.md section 31
- Domain-specific exception hierarchy
- Global exception handlers for AppException, HTTPException, RequestValidationError, and unexpected Exceptions
- Request ID middleware and tracing header injection (X-Request-ID)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("forensiweb.errors")


class AppException(Exception):
    """Base application domain exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppException):
    def __init__(self, message: str, code: str = "RESOURCE_NOT_FOUND", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ValidationError(AppException):
    def __init__(self, message: str, code: str = "VALIDATION_FAILED", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class ConflictError(AppException):
    def __init__(self, message: str, code: str = "RESOURCE_CONFLICT", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_409_CONFLICT, details=details)


class EvidenceIntegrityError(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            code="EVIDENCE_HASH_MISMATCH",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ServiceUnavailableError(AppException):
    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=code, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns and propagates a unique request ID across request state and response headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        req_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
        request.state.request_id = req_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
        except Exception as exc:
            return await generic_exception_handler(request, exc)


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", f"REQ-{uuid.uuid4().hex[:8].upper()}")


def build_error_response(
    status_code: int,
    code: str,
    message: str,
    request: Request,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Build standardized JSON error response following architecture specification."""
    req_id = _get_request_id(request)
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": req_id,
            "details": details or {},
        }
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={"X-Request-ID": req_id},
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("Application exception [%s]: %s (req_id=%s)", exc.code, exc.message, _get_request_id(request))
    return build_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        request=request,
        details=exc.details,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = f"HTTP_{exc.status_code}"
    message = str(exc.detail)
    return build_error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        request=request,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    details = {"errors": [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in errors]}
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request payload validation failed.",
        request=request,
        details=details,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled server exception: %s (req_id=%s)", exc, _get_request_id(request), exc_info=True)
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred during processing.",
        request=request,
    )


def setup_error_handling(application: FastAPI) -> None:
    """Register RequestID middleware and global exception handlers on the FastAPI app."""
    application.add_middleware(RequestIDMiddleware)
    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)
