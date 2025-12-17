"""
Feedback routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db import get_db
from models import User, Feedback
from auth.dependencies import get_current_user, require_admin
from schemas import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    request: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for an LLM call
    """
    feedback = Feedback(
        llm_call_id=request.llm_call_id,
        user_id=current_user.id,
        rating=request.rating,
        comment=request.comment
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback


@router.get("", response_model=list[FeedbackResponse])
async def get_feedback(
    search: str = Query(default="", description="Search in comments"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all feedback (ADMIN only)
    Supports filtering by search term in comments
    """
    query = db.query(Feedback)
    
    if search:
        query = query.filter(Feedback.comment.ilike(f"%{search}%"))
    
    feedbacks = query.order_by(
        Feedback.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return feedbacks
