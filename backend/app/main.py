import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings, get_settings
from app.core.database import create_engine, create_session_factory
from app.core.logging import configure_logging, request_id_context
from app.domain.errors import ComplaintNotFoundError, InvalidStatusTransitionError
from app.domain.rate_limit import RateLimitExceededError
from app.providers.cache.redis import RedisJsonCache, RedisRateLimiter, RedisStatsCache
from app.providers.triage.factory import create_triage_provider
from app.providers.triage.rules import RuleBasedTriage
from app.routes.complaints import router as complaint_router
from app.routes.health import router as health_router
from app.routes.meta import router as meta_router
from app.routes.metrics import router as metrics_router
from app.routes.stats import router as stats_router
from app.services.metrics import Metrics
from app.services.triage import TriageObservability

logger = logging.getLogger("civicpulse")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        token = request_id_context.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request.app.state.metrics.observe_request(started)
            request_id_context.reset(token)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    engine = create_engine(resolved_settings)
    session_factory = create_session_factory(engine)
    redis = Redis.from_url(resolved_settings.redis_url, decode_responses=True)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await app.state.engine.dispose()
        await app.state.redis.aclose()

    app = FastAPI(title="CivicPulse API", version="0.1.0", lifespan=lifespan)
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.settings = resolved_settings
    app.state.redis = redis
    app.state.stats_cache = RedisStatsCache(redis)
    app.state.triage_cache = RedisJsonCache(redis)
    app.state.rate_limiter = RedisRateLimiter(
        redis, resolved_settings.complaint_rate_limit, resolved_settings.complaint_rate_window_seconds
    )
    app.state.triage_provider = create_triage_provider(resolved_settings)
    app.state.fallback_provider = RuleBasedTriage()
    app.state.triage_observability = TriageObservability()
    app.state.metrics = Metrics()
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)
    app.include_router(complaint_router)
    app.include_router(meta_router)
    app.include_router(stats_router)
    app.include_router(metrics_router)

    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.exception_handler(ComplaintNotFoundError)
    async def not_found_handler(request: Request, exc: ComplaintNotFoundError):
        return JSONResponse(status_code=404, content={"detail": "Complaint not found"})

    @app.exception_handler(InvalidStatusTransitionError)
    async def transition_handler(request: Request, exc: InvalidStatusTransitionError):
        logger.warning(
            "invalid complaint status transition",
            extra={"request_id": request.state.request_id},
        )
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_handler(request: Request, exc: RateLimitExceededError):
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(exc.retry_after)},
            content={"detail": str(exc)},
        )

    app.add_exception_handler(RequestValidationError, validation_error_handler)
    return app


app = create_app()
