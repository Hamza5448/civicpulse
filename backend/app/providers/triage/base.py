from typing import Protocol

from pydantic import BaseModel, Field

from app.db.models.complaint import Category, Priority


class TriageResult(BaseModel):
    category: Category
    priority: Priority
    summary: str = Field(max_length=140)
    confidence: float = Field(ge=0.0, le=1.0)


class TriageProvider(Protocol):
    name: str

    async def triage(self, text: str, location: str) -> TriageResult:
        """Classify a complaint and return validated structured output."""
