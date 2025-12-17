"""
System Settings routes (ADMIN only)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from models import User, SystemSettings
from auth.dependencies import get_current_user, require_admin
from schemas import SystemSettingsUpdate, SystemSettingsResponse
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SystemSettingsResponse)
async def get_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system settings (ADMIN only)
    """
    settings = db.query(SystemSettings).first()
    
    if not settings:
        # Create default settings if they don't exist
        settings = SystemSettings(
            claude_haiku_45_enabled=False,
            max_tokens_per_request=4096,
            enable_caching=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("", response_model=SystemSettingsResponse)
async def update_settings(
    request: SystemSettingsUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update system settings (ADMIN only)
    
    This endpoint allows admins to configure:
    - Claude Haiku 4.5 enable/disable for all clients
    - Max tokens per request
    - Response caching
    """
    settings = db.query(SystemSettings).first()
    
    if not settings:
        # Create default settings if they don't exist
        settings = SystemSettings()
        db.add(settings)
    
    # Update only provided fields
    if request.claude_haiku_45_enabled is not None:
        settings.claude_haiku_45_enabled = request.claude_haiku_45_enabled
    
    if request.max_tokens_per_request is not None:
        settings.max_tokens_per_request = request.max_tokens_per_request
    
    if request.enable_caching is not None:
        settings.enable_caching = request.enable_caching
    
    settings.updated_at = datetime.utcnow()
    settings.updated_by = current_user.id
    
    db.commit()
    db.refresh(settings)
    
    return settings
