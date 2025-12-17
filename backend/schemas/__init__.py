"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"


# ==================== Auth Schemas ====================
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[RoleEnum] = RoleEnum.VIEWER


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ==================== LLM Model Schemas ====================
class LLMModelCreate(BaseModel):
    name: str
    provider: str
    cost_per_1k_tokens: float


class LLMModelResponse(BaseModel):
    id: int
    name: str
    provider: str
    cost_per_1k_tokens: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== LLM Call Log Schemas ====================
class LLMCallLogCreate(BaseModel):
    model_id: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    status: str = "success"
    error_message: Optional[str] = None
    prompt_preview: Optional[str] = None
    response_preview: Optional[str] = None


class LLMCallLogResponse(BaseModel):
    id: int
    user_id: int
    model_id: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    status: str
    error_message: Optional[str]
    prompt_preview: Optional[str]
    response_preview: Optional[str]
    created_at: datetime
    model: LLMModelResponse

    class Config:
        from_attributes = True


# ==================== Cost Log Schemas ====================
class CostLogResponse(BaseModel):
    id: int
    llm_call_id: int
    estimated_cost: float
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Feedback Schemas ====================
class FeedbackCreate(BaseModel):
    llm_call_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    llm_call_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Metrics Schemas ====================
class TokenUsagePoint(BaseModel):
    date: str
    tokens: int
    cost: float


class LatencyDistributionPoint(BaseModel):
    range: str
    count: int


class ErrorRatePoint(BaseModel):
    date: str
    error_rate: float
    total_requests: int


class MetricsSummary(BaseModel):
    total_tokens: int
    total_cost: float
    average_latency: float
    error_rate: float


class TokenUsageResponse(BaseModel):
    data: List[TokenUsagePoint]


class LatencyDistributionResponse(BaseModel):
    data: List[LatencyDistributionPoint]


class ErrorRateResponse(BaseModel):
    data: List[ErrorRatePoint]


# ==================== System Settings Schemas ====================
class SystemSettingsUpdate(BaseModel):
    claude_haiku_45_enabled: Optional[bool] = None
    max_tokens_per_request: Optional[int] = None
    enable_caching: Optional[bool] = None


class SystemSettingsResponse(BaseModel):
    id: int
    claude_haiku_45_enabled: bool
    max_tokens_per_request: int
    enable_caching: bool
    updated_at: datetime

    class Config:
        from_attributes = True
