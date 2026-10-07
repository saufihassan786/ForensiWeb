"""Dashboard & Analytics API v1 endpoints (PHASE-13)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.analytics import DashboardAnalytics, RiskSummary
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

_analytics_service = AnalyticsService()


def get_analytics_service() -> AnalyticsService:
    return _analytics_service


@router.get("/cases/{case_id}", response_model=DashboardAnalytics, summary="Get Case Analytics & Metrics")
async def get_case_analytics(
    case_id: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> DashboardAnalytics:
    """Retrieve evidence-backed metrics, trends, distributions, and risk scores."""
    return await service.compute_dashboard_analytics(case_id=case_id)


@router.get("/cases/{case_id}/risk-summary", response_model=RiskSummary, summary="Get Explainable Risk Summary")
async def get_case_risk_summary(
    case_id: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> RiskSummary:
    """Retrieve deterministic explainable risk summary with explicit factor breakdown."""
    analytics = await service.compute_dashboard_analytics(case_id=case_id)
    return analytics.risk_summary
