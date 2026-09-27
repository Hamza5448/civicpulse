import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings, get_settings
from app.core.database import create_engine, create_session_factory
from app.core.logging import configure_logging
from app.domain.errors import ComplaintNotFoundError, InvalidStatusTransitionError
from app.routes.complaints import router as complaint_router
from app.routes.health import router as health_router

logger = logging.getLogger("civicpulse")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    engine = create_engine(resolved_settings)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await app.state.engine.dispose()

    app = FastAPI(title="CivicPulse API", version="0.1.0", lifespan=lifespan)
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)
    app.include_router(complaint_router)

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

    app.add_exception_handler(RequestValidationError, validation_error_handler)
    return app


app = create_app()
