"""
Database models for LLM Observability system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base
import enum


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and RBAC
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.VIEWER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    llm_calls = relationship("LLMCallLog", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class LLMModel(Base):
    """
    LLM Model definition with pricing information
    """
    __tablename__ = "llm_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=False)  # e.g., "OpenAI", "Anthropic", "Google"
    cost_per_1k_tokens = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    llm_calls = relationship("LLMCallLog", back_populates="model", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LLMModel {self.name} ({self.provider})>"


class LLMCallLog(Base):
    """
    Core observability model - logs every LLM API call with metrics
    """
    __tablename__ = "llm_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("llm_models.id"), nullable=False, index=True)
    
    # Token tracking
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    latency_ms = Column(Float, nullable=False)  # milliseconds
    
    # Call metadata
    status = Column(String, default="success", nullable=False)  # success, error, timeout
    error_message = Column(Text, nullable=True)
    
    # Content tracking (for reference/debugging)
    prompt_preview = Column(String(500), nullable=True)
    response_preview = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="llm_calls")
    model = relationship("LLMModel", back_populates="llm_calls")
    cost_log = relationship("CostLog", back_populates="llm_call", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="llm_call", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LLMCallLog {self.id} ({self.status}, {self.latency_ms}ms)>"


class CostLog(Base):
    """
    Cost estimation for each LLM call
    """
    __tablename__ = "cost_logs"

    id = Column(Integer, primary_key=True, index=True)
    llm_call_id = Column(Integer, ForeignKey("llm_call_logs.id"), nullable=False, unique=True, index=True)
    estimated_cost = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    llm_call = relationship("LLMCallLog", back_populates="cost_log")

    def __repr__(self):
        return f"<CostLog ${self.estimated_cost}>"


class Feedback(Base):
    """
    User feedback on LLM responses for quality monitoring
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    llm_call_id = Column(Integer, ForeignKey("llm_call_logs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Rating and comment
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    llm_call = relationship("LLMCallLog", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback rating={self.rating}>"


class SystemSettings(Base):
    """
    Global system settings manageable by admin
    Stores configuration like Claude Haiku 4.5 enable/disable, token limits, caching
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Claude Haiku 4.5 feature flag
    claude_haiku_45_enabled = Column(Boolean, default=False, nullable=False)
    
    # Token and caching settings
    max_tokens_per_request = Column(Integer, default=4096, nullable=False)
    enable_caching = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    def __repr__(self):
        return f"<SystemSettings claude_haiku_45={self.claude_haiku_45_enabled}>"
