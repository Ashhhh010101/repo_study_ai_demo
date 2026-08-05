from contextlib import asynccontextmanager
import logging
from collections import deque
from threading import Lock
import time
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

from app.api.routes import chat, repos, stats
from app.core.config import get_settings
from app.db.init_db import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("repo_study_ai")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Stopping application")


def create_app() -> FastAPI:
    settings = get_settings()
    request_timestamps: dict[tuple[str, str], deque[float]] = {}
    rate_limit_lock = Lock()
    app = FastAPI(
        title="Repo Study AI",
        summary="Local-first repository intelligence with bring-your-own-key AI.",
        version="0.2.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Project-Token"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.middleware("http")
    async def add_security_headers(
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        started = time.perf_counter()
        logger.info("request.start method=%s path=%s", request.method, request.url.path)
        is_analyze = request.method == "POST" and request.url.path == "/api/repos/analyze"
        is_chat = request.method == "POST" and request.url.path.startswith("/api/chat/")
        is_visit = request.method == "POST" and request.url.path == "/api/stats/visit"
        if is_analyze or is_chat or is_visit:
            bucket = "analyze" if is_analyze else "chat" if is_chat else "visit"
            limit = settings.analyze_rate_limit if bucket == "analyze" else settings.chat_rate_limit
            if bucket == "visit":
                limit = settings.visit_rate_limit
            client_host = request.client.host if request.client else "unknown"
            now = time.monotonic()
            with rate_limit_lock:
                cutoff = now - settings.rate_limit_window_seconds
                key = (client_host, bucket)
                if key not in request_timestamps and len(request_timestamps) >= settings.rate_limit_max_clients:
                    stale_keys = [
                        existing_key
                        for existing_key, values in request_timestamps.items()
                        if not values or values[-1] <= cutoff
                    ]
                    for stale_key in stale_keys:
                        request_timestamps.pop(stale_key, None)
                    if len(request_timestamps) >= settings.rate_limit_max_clients:
                        return JSONResponse(
                            status_code=503,
                            content={"detail": "The service is temporarily at capacity."},
                            headers={"Retry-After": str(settings.rate_limit_window_seconds)},
                        )
                timestamps = request_timestamps.setdefault(key, deque())
                while timestamps and timestamps[0] <= cutoff:
                    timestamps.popleft()
                if len(timestamps) >= limit:
                    retry_after = max(1, int(timestamps[0] + settings.rate_limit_window_seconds - now))
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Rate limit exceeded. Please try again later."},
                        headers={"Retry-After": str(retry_after)},
                    )
                timestamps.append(now)
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request.error method=%s path=%s duration_ms=%.1f", request.method, request.url.path, (time.perf_counter() - started) * 1000)
            raise
        logger.info("request.end method=%s path=%s status=%s duration_ms=%.1f", request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # FastAPI's default payload can echo invalid inputs. Omit all input values
        # so malformed BYOK fields never appear in response bodies or proxy logs.
        safe_errors = [
            {
                key: value
                for key, value in error.items()
                if key in {"type", "loc", "msg"}
            }
            for error in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": safe_errors})

    app.include_router(repos.router, prefix="/api/repos", tags=["repos"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
    return app


app = create_app()
