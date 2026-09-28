import uuid

import pytest

from app.db.models.complaint import Category, ComplaintStatus
from app.domain.errors import ComplaintNotFoundError, InvalidStatusTransitionError
from app.schemas.complaints import ComplaintCreate
from app.services.complaints import ComplaintService


def complaint_data(**overrides) -> ComplaintCreate:
    values = {"text": "Burst water main flooding Street 12", "location": "Street 12"}
    values.update(overrides)
    return ComplaintCreate(**values)


def test_valid_complaint_input() -> None:
    complaint = complaint_data()
    assert complaint.text == "Burst water main flooding Street 12"
    assert set(complaint.model_fields_set) == {"text", "location"}


def test_invalid_complaint_input() -> None:
    with pytest.raises(ValueError):
        complaint_data(text="short")


def test_transition_table_has_required_valid_paths() -> None:
    from app.domain.transitions import VALID_STATUS_TRANSITIONS

    assert ComplaintStatus.IN_PROGRESS in VALID_STATUS_TRANSITIONS[ComplaintStatus.OPEN]
    assert ComplaintStatus.RESOLVED in VALID_STATUS_TRANSITIONS[ComplaintStatus.IN_PROGRESS]
    assert ComplaintStatus.REJECTED in VALID_STATUS_TRANSITIONS[ComplaintStatus.OPEN]


@pytest.mark.asyncio
async def test_service_creates_and_gets_complaint(session) -> None:
    service = ComplaintService(session)
    created = await service.create(complaint_data())
    found = await service.get(created.id)
    assert found.id == created.id
    assert found.status is ComplaintStatus.OPEN


@pytest.mark.asyncio
async def test_service_missing_complaint(session) -> None:
    with pytest.raises(ComplaintNotFoundError):
        await ComplaintService(session).get(uuid.uuid4())


@pytest.mark.asyncio
async def test_service_lists_and_filters_complaints(session) -> None:
    service = ComplaintService(session)
    await service.create(complaint_data(text="Burst water main flooding Street 12"))
    await service.create(complaint_data(text="Large pothole blocking the road near market"))
    items, total = await service.list(
        category=Category.WATER, priority=None, status=None, page=1, page_size=20
    )
    assert total == 1
    assert len(items) == 1


@pytest.mark.asyncio
async def test_service_allows_valid_status_transition(session) -> None:
    service = ComplaintService(session)
    created = await service.create(complaint_data())
    updated = await service.change_status(created.id, ComplaintStatus.IN_PROGRESS)
    assert updated.status is ComplaintStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_service_rejects_invalid_status_transition(session) -> None:
    service = ComplaintService(session)
    created = await service.create(complaint_data())
    await service.change_status(created.id, ComplaintStatus.IN_PROGRESS)
    await service.change_status(created.id, ComplaintStatus.RESOLVED)
    with pytest.raises(InvalidStatusTransitionError):
        await service.change_status(created.id, ComplaintStatus.OPEN)
