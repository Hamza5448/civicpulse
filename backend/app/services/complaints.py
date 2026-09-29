import hashlib
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
from app.services.metrics import Metrics
from app.services.triage import TriageObservability, TriageOutcome

logger = logging.getLogger("civicpulse.triage")


class ComplaintService:
    def __init__(
        self,
        session: AsyncSession,
        provider: TriageProvider | None = None,
        fallback_provider: TriageProvider | None = None,
        observability: TriageObservability | None = None,
        stats_invalidator=None,
        triage_cache=None,
        triage_cache_ttl_seconds: int = 86400,
        metrics: Metrics | None = None,
    ) -> None:
        self.repository = ComplaintRepository(session)
        self.session = session
        self.provider = provider or RuleBasedTriage()
        self.fallback_provider = fallback_provider or RuleBasedTriage()
        self.observability = observability
        self.stats_invalidator = stats_invalidator
        self.triage_cache = triage_cache
        self.triage_cache_ttl_seconds = triage_cache_ttl_seconds
        self.metrics = metrics

    async def create(self, data: ComplaintCreate) -> Complaint:
        complaint_id = uuid.uuid4()
        started = time.perf_counter()
        triaged_by = self.provider.name
        cache_hit = False
        fallback_used = False
        cache_key = "triage:" + hashlib.sha256(
            f"{data.text}\n{data.location}".encode()
        ).hexdigest()
        cached = await self.triage_cache.get(cache_key) if self.triage_cache else None
        if cached:
            from app.providers.triage.base import TriageResult

            result = TriageResult.model_validate(cached["result"])
            triaged_by = cached["provider"]
            cache_hit = True
        else:
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
                fallback_used = True
            if self.triage_cache:
                await self.triage_cache.set(
                    cache_key,
                    {"provider": triaged_by, "result": result.model_dump(mode="json")},
                    self.triage_cache_ttl_seconds,
                )
        latency_ms = max(0, round((time.perf_counter() - started) * 1000))
        if self.observability is not None:
            self.observability.record(
                TriageOutcome(
                    provider=triaged_by,
                    latency_ms=latency_ms,
                    fallback=triaged_by == "rules:fallback",
                    cache_hit=cache_hit,
                )
            )
        if self.metrics is not None:
            self.metrics.observe_triage(latency_ms / 1000, fallback=fallback_used)
        complaint = Complaint(
            id=complaint_id,
            text=data.text,
            location=data.location,
            reporter_contact=data.reporter_contact,
            category=result.category,
            priority=result.priority,
            ai_summary=result.summary,
            triaged_by=triaged_by,
            triage_latency_ms=latency_ms,
        )
        created = await self.repository.create(complaint)
        await self.session.commit()
        if self.stats_invalidator is not None:
            await self.stats_invalidator()
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
