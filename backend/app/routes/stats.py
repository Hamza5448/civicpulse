from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request, Response

from app.services.stats import StatsService

router = APIRouter(prefix="/api", tags=["stats"])


async def get_stats_service(request: Request) -> AsyncIterator[StatsService]:
    async with request.app.state.session_factory() as session:
        from app.repositories.complaints import ComplaintRepository

        yield StatsService(
            ComplaintRepository(session),
            request.app.state.stats_cache,
            request.app.state.settings.stats_cache_ttl_seconds,
        )


@router.get("/stats")
async def get_stats(
    response: Response,
    service: StatsService = Depends(get_stats_service),
) -> dict:
    value, cache_hit = await service.get()
    response.headers["X-Cache"] = "HIT" if cache_hit else "MISS"
    return value
