import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, Index, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Category(str, enum.Enum):
    WATER = "water"
    ELECTRICITY = "electricity"
    SANITATION = "sanitation"
    ROADS = "roads"
    STREETLIGHTS = "streetlights"
    OTHER = "other"


class Priority(str, enum.Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ComplaintStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint(
            "length(text) >= 10 AND length(text) <= 2000", name="ck_complaints_text_length"
        ),
        CheckConstraint(
            "length(location) >= 3 AND length(location) <= 200",
            name="ck_complaints_location_length",
        ),
        CheckConstraint(
            "triage_latency_ms IS NULL OR triage_latency_ms >= 0",
            name="ck_complaints_latency_nonnegative",
        ),
        Index("ix_complaints_status_priority", "status", "priority"),
        Index("ix_complaints_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    reporter_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Use values_callable so SQLAlchemy sends the lowercase value ("water") instead of the uppercase member name ("WATER")
    category: Mapped[Category] = mapped_column(
        Enum(
            Category,
            name="category_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(
            Priority,
            name="priority_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    status: Mapped[ComplaintStatus] = mapped_column(
        Enum(
            ComplaintStatus,
            name="complaint_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=ComplaintStatus.OPEN,
    )

    ai_summary: Mapped[str | None] = mapped_column(String(140), nullable=True)
    triaged_by: Mapped[str | None] = mapped_column(String(32), nullable=True)
    triage_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )