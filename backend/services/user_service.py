"""
User service layer - handles authentication and user operations
"""
from sqlalchemy.orm import Session
from models import User, RoleEnum
from schemas import UserResponse
from auth.jwt import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def register_user(email: str, password: str, role: str, db: Session) -> UserResponse:
        """
        Register a new user
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=RoleEnum(role)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at
        )
    
    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> dict:
        """
        Authenticate user and return JWT token
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create JWT token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(
                id=user.id,
                email=user.email,
                role=user.role.value,
                created_at=user.created_at
            )
        }
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
