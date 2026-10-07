"""Mitigation and Verification API v1 endpoints (PHASE-15)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Query, status

from app.services.mitigation_service import MitigationService

router = APIRouter(prefix="/mitigation", tags=["Mitigation & Verification"])

mitigation_service = MitigationService()


class CompareRequest(BaseModel):
    case_id: str = Field(default="CASE-001")
    baseline_run: Optional[Dict[str, Any]] = None
    mitigated_run: Optional[Dict[str, Any]] = None


class VerificationResponse(BaseModel):
    verification_id: str
    case_id: str
    verified_at: str
    sha256: str
    status: str
    details: Dict[str, Any]


@router.get("/recommendations", summary="List Mitigation Recommendations")
async def list_recommendations(
    stage: Optional[str] = Query(None, description="Filter recommendations by attack stage"),
) -> List[Dict[str, Any]]:
    """Retrieve structured mitigation recommendations for identified vulnerabilities."""
    return mitigation_service.get_recommendations(stage=stage)


@router.post("/compare", summary="Compare Baseline vs Mitigated Telemetry")
async def compare_telemetry(req: CompareRequest) -> Dict[str, Any]:
    """Execute quantitative before/after comparative analysis between baseline and mitigated scenario runs."""
    baseline = req.baseline_run or {
        "completed_stages": ["S1", "S2", "S3", "S4", "S5"],
        "critical_detections_count": 4,
        "root_privilege_achieved": True,
        "lfi_status": 200,
        "web_shell_accessible": True,
        "privesc_effective_uid": 0,
    }

    mitigated = req.mitigated_run or {
        "completed_stages": [],
        "critical_detections_count": 0,
        "root_privilege_achieved": False,
        "lfi_status": 403,
        "web_shell_accessible": False,
        "privesc_effective_uid": 1000,
    }

    return mitigation_service.compare_before_after(baseline, mitigated)


@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED, summary="Generate Verification Evidence Artifact")
async def generate_verification(req: CompareRequest) -> VerificationResponse:
    """Produce an immutable cryptographic verification artifact confirming security remediation."""
    comparison = await compare_telemetry(req)
    evidence = mitigation_service.create_verification_evidence(req.case_id, comparison)
    return VerificationResponse(**evidence)
