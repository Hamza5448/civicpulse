import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Query, Request, status

from app.db.models.complaint import Category, ComplaintStatus, Priority
from app.schemas.complaints import (
    ComplaintCreate,
    ComplaintListResponse,
    ComplaintResponse,
    ComplaintStatusUpdate,
)
from app.services.complaints import ComplaintService

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


async def get_service(request: Request) -> AsyncIterator[ComplaintService]:
    async with request.app.state.session_factory() as session:
        yield ComplaintService(
            session,
            provider=request.app.state.triage_provider,
            fallback_provider=request.app.state.fallback_provider,
            observability=request.app.state.triage_observability,
            stats_invalidator=request.app.state.stats_cache.delete_stats,
            triage_cache=request.app.state.triage_cache,
            triage_cache_ttl_seconds=request.app.state.settings.triage_cache_ttl_seconds,
        )


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    payload: ComplaintCreate,
    request: Request,
    service: ComplaintService = Depends(get_service),
) -> ComplaintResponse:
    allowed, retry_after = await request.app.state.rate_limiter.check(request.client.host)
    if not allowed:
        from app.domain.rate_limit import RateLimitExceededError

        raise RateLimitExceededError(retry_after)
    return await service.create(payload)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_service),
) -> ComplaintResponse:
    return await service.get(complaint_id)


@router.get("", response_model=ComplaintListResponse)
async def list_complaints(
    category: Category | None = None,
    priority: Priority | None = None,
    status_filter: ComplaintStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ComplaintService = Depends(get_service),
) -> ComplaintListResponse:
    items, total = await service.list(
        category=category,
        priority=priority,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return ComplaintListResponse(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
async def update_complaint_status(
    complaint_id: uuid.UUID,
    payload: ComplaintStatusUpdate,
    service: ComplaintService = Depends(get_service),
) -> ComplaintResponse:
    return await service.change_status(complaint_id, payload.status)
