from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.dependencies import get_readiness_service
from app.services.readiness import ReadinessService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(service: ReadinessService = Depends(get_readiness_service)) -> JSONResponse:
    failed_dependency = await service.failed_dependency()
    if failed_dependency is not None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "dependency": failed_dependency},
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ready"})
