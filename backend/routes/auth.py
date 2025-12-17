"""
Authentication routes - Register and Login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from schemas import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
)
from services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password
    """
    user_response = UserService.register_user(
        email=request.email,
        password=request.password,
        role=request.role.value,
        db=db
    )
    
    # Create token for the newly registered user
    result = UserService.authenticate_user(
        email=request.email,
        password=request.password,
        db=db
    )
    
    return result


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token
    """
    result = UserService.authenticate_user(
        email=request.email,
        password=request.password,
        db=db
    )
    
    return result
