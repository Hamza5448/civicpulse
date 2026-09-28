import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.complaint import Category, ComplaintStatus, Priority


class ComplaintCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    location: str = Field(min_length=3, max_length=200)
    reporter_contact: str | None = Field(default=None, max_length=255)
    category: Category = Category.OTHER
    priority: Priority = Priority.NORMAL


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    location: str
    reporter_contact: str | None
    category: Category
    priority: Priority
    status: ComplaintStatus
    ai_summary: str | None
    triaged_by: str | None
    triage_latency_ms: int | None
    created_at: datetime
    updated_at: datetime


class ComplaintListResponse(BaseModel):
    items: list[ComplaintResponse]
    total: int
    page: int
    page_size: int


class TriageOutcomeResponse(BaseModel):
    provider: str
    latency_ms: int
    fallback: bool


class TriageProviderMetaResponse(BaseModel):
    active_provider: str
    recent_outcomes: list[TriageOutcomeResponse]
