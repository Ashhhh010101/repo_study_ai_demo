from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, repos
from app.db.init_db import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Repo Study AI", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    app.include_router(repos.router, prefix="/api/repos", tags=["repos"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    return app


app = create_app()
