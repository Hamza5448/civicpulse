from fastapi import APIRouter, Request

from app.schemas.complaints import TriageOutcomeResponse, TriageProviderMetaResponse

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/providers", response_model=TriageProviderMetaResponse)
async def provider_meta(request: Request) -> TriageProviderMetaResponse:
    outcomes = request.app.state.triage_observability.recent()
    return TriageProviderMetaResponse(
        active_provider=request.app.state.triage_provider.name,
        recent_outcomes=[
            TriageOutcomeResponse.model_validate(outcome.__dict__) for outcome in outcomes
        ],
    )
