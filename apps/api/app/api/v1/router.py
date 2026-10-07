"""ForensiWeb API v1 Central Router."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    cases,
    detections,
    events,
    evidence,
    findings,
    health,
    mitigation,
    reports,
    timeline,
)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health.router)
api_v1_router.include_router(cases.router)
api_v1_router.include_router(evidence.router)
api_v1_router.include_router(events.router)
api_v1_router.include_router(detections.router)
api_v1_router.include_router(timeline.router)
api_v1_router.include_router(findings.router)
api_v1_router.include_router(reports.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(mitigation.router)

