from fastapi import APIRouter, Depends, Response

from app.core.dependencies import get_stats_service
from app.schemas.complaints import StatsResponse
from app.services.stats import StatsService

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    response: Response,
    service: StatsService = Depends(get_stats_service),
) -> StatsResponse:
    value, cache_hit = await service.get()
    response.headers["X-Cache"] = "HIT" if cache_hit else "MISS"
    return StatsResponse.model_validate(value)
