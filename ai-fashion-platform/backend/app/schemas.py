"""Pydantic request/response schemas."""
from typing import Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ------- Auth -------
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=4)
    role: str = "designer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ------- Analyze -------
class AnalyzeRequest(BaseModel):
    image_url: Optional[str] = None
    prompt: str
    region: str = "Global"
    category: str = "unisex"
    season: Optional[str] = None


class AnalyzeResponse(BaseModel):
    request_id: str
    status: str


# ------- Results -------
class TrendItem(BaseModel):
    name: str
    forecast: str
    growth: float


class ColorSwatch(BaseModel):
    hex: str
    name: str
    weight: float


class DesignSpec(BaseModel):
    id: str
    title: str
    summary: str
    silhouette: str
    fabric: str
    palette: List[str]


class TechPack(BaseModel):
    title: str
    category: str
    fabric: str
    colors: List[str]
    construction: List[str]
    trims: List[str]
    measurements: dict
    care: List[str]


class ResultResponse(BaseModel):
    request_id: str
    status: str
    region: str
    prompt: str
    trends: List[TrendItem]
    colors: List[ColorSwatch]
    designs: List[DesignSpec]
    tech_pack: Optional[TechPack] = None
    confidence: float
    explanation: str
    fallback: Optional[str] = None


# ------- Design modify -------
class DesignModifyRequest(BaseModel):
    base_design_id: str
    modifier: str  # e.g. "make it more formal", "change color to pastel"


# ------- Admin -------
class AdminMetrics(BaseModel):
    total_requests: int
    total_users: int
    avg_confidence: float
    error_rate: float
    requests_by_region: dict
    top_trends: List[dict]
    confidence_distribution: dict


class AuditLogEntry(BaseModel):
    model_config = {"from_attributes": True, "protected_namespaces": ()}

    id: str
    request_id: Optional[str]
    model_version: Optional[str]
    prompt_version: Optional[str]
    confidence: Optional[float]
    created_at: datetime


class ConfigUpdate(BaseModel):
    key: str
    value: str
