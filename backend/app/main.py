from contextlib import asynccontextmanager
import logging
import time
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

from app.api.routes import chat, repos
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
        allow_headers=["Content-Type"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

    @app.middleware("http")
    async def add_security_headers(
        request: Request,
        call_next: RequestResponseEndpoint,
    ):
        started = time.perf_counter()
        logger.info("request.start method=%s path=%s", request.method, request.url.path)
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
    return app


app = create_app()
