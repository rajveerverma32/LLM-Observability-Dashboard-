"""
Metrics aggregation service - computes metrics from LLM call logs
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import LLMCallLog, CostLog, LLMModel
from datetime import datetime, timedelta
from schemas import (
    MetricsSummary, TokenUsagePoint, LatencyDistributionPoint, ErrorRatePoint
)


class MetricsService:
    """Service for metrics aggregation and computation"""
    
    @staticmethod
    def get_summary_metrics(user_id: int, db: Session, days: int = 30) -> MetricsSummary:
        """
        Get aggregated metrics for the past N days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all LLM calls for user in the period
        calls = db.query(LLMCallLog).filter(
            and_(
                LLMCallLog.user_id == user_id,
                LLMCallLog.created_at >= cutoff_date
            )
        ).all()
        
        if not calls:
            return MetricsSummary(
                total_tokens=0,
                total_cost=0.0,
                average_latency=0.0,
                error_rate=0.0
            )
        
        # Calculate metrics
        total_tokens = sum(call.total_tokens for call in calls)
        total_cost = sum(
            call.cost_log.estimated_cost for call in calls if call.cost_log
        )
        average_latency = sum(call.latency_ms for call in calls) / len(calls)
        
        error_count = sum(1 for call in calls if call.status == "error")
        error_rate = (error_count / len(calls)) * 100 if calls else 0.0
        
        return MetricsSummary(
            total_tokens=total_tokens,
            total_cost=round(total_cost, 4),
            average_latency=round(average_latency, 2),
            error_rate=round(error_rate, 2)
        )
    
    @staticmethod
    def get_token_usage_over_time(
        user_id: int,
        db: Session,
        days: int = 30
    ) -> list[TokenUsagePoint]:
        """
        Get daily token usage over time
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query for daily aggregated metrics
        results = db.query(
            func.date(LLMCallLog.created_at).label("date"),
            func.sum(LLMCallLog.total_tokens).label("total_tokens"),
            func.sum(CostLog.estimated_cost).label("total_cost")
        ).join(
            CostLog, LLMCallLog.id == CostLog.llm_call_id, isouter=True
        ).filter(
            and_(
                LLMCallLog.user_id == user_id,
                LLMCallLog.created_at >= cutoff_date
            )
        ).group_by(
            func.date(LLMCallLog.created_at)
        ).order_by(
            func.date(LLMCallLog.created_at)
        ).all()
        
        return [
            TokenUsagePoint(
                date=str(row.date),
                tokens=row.total_tokens or 0,
                cost=round(row.total_cost or 0, 4)
            )
            for row in results
        ]
    
    @staticmethod
    def get_latency_distribution(
        user_id: int,
        db: Session,
        days: int = 30
    ) -> list[LatencyDistributionPoint]:
        """
        Get latency distribution buckets
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        calls = db.query(LLMCallLog).filter(
            and_(
                LLMCallLog.user_id == user_id,
                LLMCallLog.created_at >= cutoff_date
            )
        ).all()
        
        # Bucket latencies
        buckets = {
            "0-100ms": 0,
            "100-200ms": 0,
            "200-500ms": 0,
            "500-1000ms": 0,
            "1000ms+": 0
        }
        
        for call in calls:
            if call.latency_ms < 100:
                buckets["0-100ms"] += 1
            elif call.latency_ms < 200:
                buckets["100-200ms"] += 1
            elif call.latency_ms < 500:
                buckets["200-500ms"] += 1
            elif call.latency_ms < 1000:
                buckets["500-1000ms"] += 1
            else:
                buckets["1000ms+"] += 1
        
        return [
            LatencyDistributionPoint(range=label, count=count)
            for label, count in buckets.items()
        ]
    
    @staticmethod
    def get_error_rate_over_time(
        user_id: int,
        db: Session,
        days: int = 30
    ) -> list[ErrorRatePoint]:
        """
        Get daily error rate over time
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all calls for the user in the period
        calls = db.query(LLMCallLog).filter(
            and_(
                LLMCallLog.user_id == user_id,
                LLMCallLog.created_at >= cutoff_date
            )
        ).all()
        
        # Group by date and compute error rate
        daily_stats = {}
        for call in calls:
            date = str(call.created_at.date())
            if date not in daily_stats:
                daily_stats[date] = {"total": 0, "errors": 0}
            daily_stats[date]["total"] += 1
            if call.status == "error":
                daily_stats[date]["errors"] += 1
        
        return [
            ErrorRatePoint(
                date=date,
                error_rate=round((stats["errors"] / stats["total"] * 100) if stats["total"] > 0 else 0, 2),
                total_requests=stats["total"]
            )
            for date, stats in sorted(daily_stats.items())
        ]
    
    @staticmethod
    def get_cost_summary(user_id: int, db: Session, days: int = 30) -> float:
        """
        Get total cost for a period (ADMIN only)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = db.query(func.sum(CostLog.estimated_cost)).join(
            LLMCallLog, LLMCallLog.id == CostLog.llm_call_id
        ).filter(
            and_(
                LLMCallLog.user_id == user_id,
                LLMCallLog.created_at >= cutoff_date
            )
        ).scalar()
        
        return round(result or 0.0, 4)
