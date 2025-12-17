"""
LLM Call Logging routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models import User
from auth.dependencies import get_current_user
from schemas import LLMCallLogCreate, LLMCallLogResponse
from observability.wrapper import LLMObservabilityWrapper
from observability.mock_llm import mock_llm_api_call

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/log-call", response_model=LLMCallLogResponse)
async def log_llm_call(
    request: LLMCallLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log an LLM API call with metrics.
    
    This endpoint receives LLM call metrics from clients or backend services
    and persists them to the database for observability tracking.
    
    In production, this would receive real metrics from your LLM providers.
    """
    # Create observability wrapper for this call
    wrapper = LLMObservabilityWrapper(db, current_user.id, request.model_id)
    
    # For demo purposes, we'll create the log entry directly
    # In production, you'd call the actual LLM API through the wrapper
    from models import LLMCallLog, CostLog
    from datetime import datetime
    
    log_entry = LLMCallLog(
        user_id=current_user.id,
        model_id=request.model_id,
        prompt_tokens=request.prompt_tokens,
        completion_tokens=request.completion_tokens,
        total_tokens=request.total_tokens,
        latency_ms=request.latency_ms,
        status=request.status,
        error_message=request.error_message,
        prompt_preview=request.prompt_preview,
        response_preview=request.response_preview,
        created_at=datetime.utcnow()
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    # Calculate and log cost
    model = db.query(__import__('models', fromlist=['LLMModel']).LLMModel).filter(
        __import__('models', fromlist=['LLMModel']).LLMModel.id == request.model_id
    ).first()
    
    if model:
        estimated_cost = (request.total_tokens / 1000) * model.cost_per_1k_tokens
        cost_log = CostLog(
            llm_call_id=log_entry.id,
            estimated_cost=estimated_cost,
            created_at=datetime.utcnow()
        )
        db.add(cost_log)
        db.commit()
    
    # Refresh to include relationships
    db.refresh(log_entry)
    
    return log_entry


@router.post("/seed", tags=["llm"])
async def seed_llm_data(
    days: int = Query(default=30, ge=1, le=365, description="Number of past days to generate data for"),
    per_day: int = Query(default=25, ge=1, le=1000, description="Number of logs to create per day"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate demo LLM call logs for charts and metrics.

    Creates `per_day` logs for each of the past `days` days for the current user,
    distributed across available models with random tokens, latency, and errors.
    """
    from models import LLMCallLog, CostLog, LLMModel
    from datetime import datetime, timedelta
    import random

    models = db.query(LLMModel).all()
    if not models:
        return {"created": 0, "message": "No LLM models found. Seed models first."}

    total_created = 0
    now = datetime.utcnow()

    for d in range(days):
        day_dt = now - timedelta(days=d)
        for _ in range(per_day):
            model = random.choice(models)

            # Simulate token usage and latency
            prompt_tokens = random.randint(50, 800)
            completion_tokens = random.randint(20, 1200)
            total_tokens = prompt_tokens + completion_tokens
            latency_ms = max(20, int(random.gauss(250, 120)))

            status = "success" if random.random() > 0.08 else "error"
            error_message = None if status == "success" else random.choice([
                "timeout", "rate_limit", "invalid_request", "provider_error"
            ])

            log_entry = LLMCallLog(
                user_id=current_user.id,
                model_id=model.id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=float(latency_ms),
                status=status,
                error_message=error_message,
                prompt_preview="Explain quantum computing",
                response_preview="Quantum computing uses qubits...",
                created_at=day_dt,
            )

            db.add(log_entry)
            db.flush()  # get log_entry.id without full commit

            estimated_cost = (total_tokens / 1000.0) * float(model.cost_per_1k_tokens)
            db.add(CostLog(
                llm_call_id=log_entry.id,
                estimated_cost=estimated_cost,
                created_at=day_dt,
            ))

            total_created += 1

        # Commit per day to keep memory down
        db.commit()

    return {"created": total_created, "days": days, "per_day": per_day}
