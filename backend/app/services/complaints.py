import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.complaint import Category, Complaint, ComplaintStatus, Priority
from app.domain.errors import ComplaintNotFoundError, InvalidStatusTransitionError
from app.domain.transitions import VALID_STATUS_TRANSITIONS
from app.repositories.complaints import ComplaintRepository
from app.schemas.complaints import ComplaintCreate


class ComplaintService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ComplaintRepository(session)
        self.session = session

    async def create(self, data: ComplaintCreate) -> Complaint:
        complaint = Complaint(
            text=data.text,
            location=data.location,
            reporter_contact=data.reporter_contact,
            category=data.category,
            priority=data.priority,
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
