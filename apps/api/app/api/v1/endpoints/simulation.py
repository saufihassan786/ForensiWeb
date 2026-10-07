"""Attack Simulation and Interactive Demonstration API Endpoints."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, status

from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulation", tags=["Attack Simulation & Live Demonstration"])
simulation_service = SimulationService()


class RunScenarioRequest(BaseModel):
    mitigated: bool = Field(default=False, description="Simulate scenario with defensive mitigations enabled")


class RunStageRequest(BaseModel):
    stage_id: str = Field(..., description="Stage identifier: S1, S2, S3, S4, S5")
    custom_payload: Optional[str] = Field(default=None, description="Optional custom payload override")


class ToggleMitigationRequest(BaseModel):
    enable: bool = Field(..., description="True to activate defensive shields, False to disable")


@router.get("/status", summary="Get Laboratory Simulation Status")
async def get_simulation_status() -> Dict[str, Any]:
    """Retrieve connectivity, log counts, and mitigation status of the lab target."""
    return await simulation_service.get_lab_status()


@router.post("/run", summary="Run Complete Multi-Stage Attack Simulation")
async def run_attack_scenario(req: RunScenarioRequest) -> Dict[str, Any]:
    """Execute all 5 stages of the academic attack chain and return live forensic telemetry."""
    return await simulation_service.run_full_scenario(mitigated=req.mitigated)


@router.post("/stage", summary="Execute Single Attack Stage")
async def execute_stage(req: RunStageRequest) -> Dict[str, Any]:
    """Execute a single attack stage with custom parameters and inspect the immediate detection result."""
    try:
        return await simulation_service.execute_stage(
            stage_id=req.stage_id,
            custom_payload=req.custom_payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/mitigation/toggle", summary="Toggle Defensive Mitigation Mode")
async def toggle_mitigation(req: ToggleMitigationRequest) -> Dict[str, Any]:
    """Toggle mitigation filters on the target and return active defense policies."""
    return await simulation_service.set_mitigation(enable=req.enable)


@router.post("/reset", summary="Reset Laboratory Target State")
async def reset_lab() -> Dict[str, Any]:
    """Clear access/audit logs and restore original target baseline."""
    return await simulation_service.reset_lab()
