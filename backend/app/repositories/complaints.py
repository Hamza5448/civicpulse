import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.complaint import Category, Complaint, ComplaintStatus, Priority


class ComplaintRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, complaint: Complaint) -> Complaint:
        self.session.add(complaint)
        await self.session.flush()
        await self.session.refresh(complaint)
        return complaint

    async def get_by_id(self, complaint_id: uuid.UUID) -> Complaint | None:
        return await self.session.get(Complaint, complaint_id)

    async def list(
        self,
        *,
        category: Category | None,
        priority: Priority | None,
        status: ComplaintStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Complaint], int]:
        filters = []
        if category is not None:
            filters.append(Complaint.category == category)
        if priority is not None:
            filters.append(Complaint.priority == priority)
        if status is not None:
            filters.append(Complaint.status == status)
        total = int(
            (await self.session.scalar(select(func.count()).select_from(Complaint).where(*filters)))
            or 0
        )
        query = (
            select(Complaint)
            .where(*filters)
            .order_by(Complaint.created_at.desc(), Complaint.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list((await self.session.scalars(query)).all()), total

    async def update_status(self, complaint: Complaint, status: ComplaintStatus) -> Complaint:
        complaint.status = status
        await self.session.flush()
        await self.session.refresh(complaint)
        return complaint
