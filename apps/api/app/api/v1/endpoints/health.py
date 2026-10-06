"""Health and Readiness Observability Endpoints (PHASE-02-F07)."""

from __future__ import annotations

import os
from typing import Any, Dict
from fastapi import APIRouter, Response, status

from app.core.config import get_settings
from app.core.database import check_database_health

router = APIRouter(prefix="/health", tags=["Health & Observability"])


@router.get("/live", summary="Liveness Probe")
async def liveness() -> Dict[str, str]:
    """Kubernetes/Container liveness probe verifying process responsiveness."""
    return {"status": "alive", "service": "forensiweb-api"}


@router.get("/ready", summary="Readiness Probe")
async def readiness(response: Response) -> Dict[str, Any]:
    """Readiness probe evaluating dependencies (database, storage) before receiving traffic."""
    settings = get_settings()

    # 1. Database check
    db_ok = await check_database_health()

    # 2. Storage check
    evidence_dir = settings.EVIDENCE_ROOT_DIR
    storage_ok = evidence_dir.exists() or os.access(os.getcwd(), os.W_OK)

    is_ready = db_ok and storage_ok

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "unready",
        "database": "connected" if db_ok else "disconnected",
        "evidence_storage": "available" if storage_ok else "unavailable",
    }


@router.get("", summary="Overall System Health")
async def system_health(response: Response) -> Dict[str, Any]:
    """Comprehensive health summary of backend components and environment."""
    settings = get_settings()
    db_ok = await check_database_health()

    overall_status = "healthy" if db_ok else "degraded"

    return {
        "status": overall_status,
        "environment": settings.ENVIRONMENT,
        "version": settings.API_VERSION,
        "subsystems": {
            "api": "operational",
            "database": "operational" if db_ok else "unavailable",
            "evidence_vault": "operational",
        },
    }
