import logging
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.complaint import Category, Complaint, ComplaintStatus, Priority
from app.domain.errors import ComplaintNotFoundError, InvalidStatusTransitionError
from app.domain.transitions import VALID_STATUS_TRANSITIONS
from app.providers.triage.base import TriageProvider
from app.providers.triage.rules import RuleBasedTriage
from app.repositories.complaints import ComplaintRepository
from app.schemas.complaints import ComplaintCreate
from app.services.triage import TriageObservability, TriageOutcome

logger = logging.getLogger("civicpulse.triage")


class ComplaintService:
    def __init__(
        self,
        session: AsyncSession,
        provider: TriageProvider | None = None,
        fallback_provider: TriageProvider | None = None,
        observability: TriageObservability | None = None,
    ) -> None:
        self.repository = ComplaintRepository(session)
        self.session = session
        self.provider = provider or RuleBasedTriage()
        self.fallback_provider = fallback_provider or RuleBasedTriage()
        self.observability = observability

    async def create(self, data: ComplaintCreate) -> Complaint:
        complaint_id = uuid.uuid4()
        started = time.perf_counter()
        triaged_by = self.provider.name
        try:
            result = await self.provider.triage(data.text, data.location)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "triage provider failed; using fallback",
                extra={
                    "complaint_id": str(complaint_id),
                    "provider": self.provider.name,
                    "error_class": type(exc).__name__,
                },
            )
            result = await self.fallback_provider.triage(data.text, data.location)
            triaged_by = "rules:fallback"
        if self.observability is not None:
            self.observability.record(
                TriageOutcome(
                    provider=triaged_by,
                    latency_ms=max(0, round((time.perf_counter() - started) * 1000)),
                    fallback=triaged_by == "rules:fallback",
                )
            )
        complaint = Complaint(
            id=complaint_id,
            text=data.text,
            location=data.location,
            reporter_contact=data.reporter_contact,
            category=result.category,
            priority=result.priority,
            ai_summary=result.summary,
            triaged_by=triaged_by,
            triage_latency_ms=max(0, round((time.perf_counter() - started) * 1000)),
        )
        created = await self.repository.create(complaint)
        await self.session.commit()
        return created

    async def get(self, complaint_id: uuid.UUID) -> Complaint:
        complaint = await self.repository.get_by_id(complaint_id)
        if complaint is None:
            raise ComplaintNotFoundError(str(complaint_id))
        return complaint

    async def list(
        self,
        *,
        category: Category | None,
        priority: Priority | None,
        status: ComplaintStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Complaint], int]:
        return await self.repository.list(
            category=category,
            priority=priority,
            status=status,
            page=page,
            page_size=page_size,
        )

    async def change_status(
        self, complaint_id: uuid.UUID, new_status: ComplaintStatus
    ) -> Complaint:
        complaint = await self.get(complaint_id)
        if new_status not in VALID_STATUS_TRANSITIONS[complaint.status]:
            raise InvalidStatusTransitionError(complaint.status.value, new_status.value)
        updated = await self.repository.update_status(complaint, new_status)
        await self.session.commit()
        return updated
