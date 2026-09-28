from collections.abc import AsyncIterator

from fastapi import Request

from app.domain.rate_limit import RateLimitExceededError
from app.providers.cache.redis import RedisHealthCheck
from app.repositories.complaints import ComplaintRepository
from app.repositories.readiness import PostgresReadinessRepository
from app.services.complaints import ComplaintService
from app.services.readiness import ReadinessService
from app.services.stats import StatsService


async def get_complaint_service(request: Request) -> AsyncIterator[ComplaintService]:
    async with request.app.state.session_factory() as session:
        yield ComplaintService(
            session,
            provider=request.app.state.triage_provider,
            fallback_provider=request.app.state.fallback_provider,
            observability=request.app.state.triage_observability,
            stats_invalidator=request.app.state.stats_cache.delete_stats,
            triage_cache=request.app.state.triage_cache,
            triage_cache_ttl_seconds=request.app.state.settings.triage_cache_ttl_seconds,
            metrics=request.app.state.metrics,
        )


async def get_stats_service(request: Request) -> AsyncIterator[StatsService]:
    async with request.app.state.session_factory() as session:
        yield StatsService(
            ComplaintRepository(session),
            request.app.state.stats_cache,
            request.app.state.settings.stats_cache_ttl_seconds,
        )


def get_readiness_service(request: Request) -> ReadinessService:
    return ReadinessService(
        PostgresReadinessRepository(request.app.state.engine),
        RedisHealthCheck(request.app.state.redis),
    )


async def enforce_complaint_rate_limit(request: Request) -> None:
    allowed, retry_after = await request.app.state.rate_limiter.check(request.client.host)
    if not allowed:
        raise RateLimitExceededError(retry_after)
