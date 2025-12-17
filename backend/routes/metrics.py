"""
Metrics and Dashboard routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models import User
from auth.dependencies import get_current_user
from schemas import (
    MetricsSummary, TokenUsageResponse, LatencyDistributionResponse,
    ErrorRateResponse
)
from services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated metrics summary for the past N days
    Returns: total tokens, total cost, average latency, error rate
    """
    return MetricsService.get_summary_metrics(current_user.id, db, days)


@router.get("/token-usage", response_model=TokenUsageResponse)
async def get_token_usage(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily token usage over time
    """
    data = MetricsService.get_token_usage_over_time(current_user.id, db, days)
    return TokenUsageResponse(data=data)


@router.get("/latency", response_model=LatencyDistributionResponse)
async def get_latency_distribution(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get latency distribution buckets
    """
    data = MetricsService.get_latency_distribution(current_user.id, db, days)
    return LatencyDistributionResponse(data=data)


@router.get("/error-rate", response_model=ErrorRateResponse)
async def get_error_rate(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily error rate over time
    """
    data = MetricsService.get_error_rate_over_time(current_user.id, db, days)
    return ErrorRateResponse(data=data)


@router.get("/cost", response_model=dict)
async def get_cost_summary(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get total cost for period (visible to all users for their own data)
    """
    total_cost = MetricsService.get_cost_summary(current_user.id, db, days)
    return {"total_cost": total_cost, "period_days": days}
