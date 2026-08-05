import hashlib
import secrets

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db


def create_project_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_project_token(token)


def hash_project_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def require_project_access(
    project_id: int,
    db: Session = Depends(get_db),
    project_token: str | None = Header(default=None, alias="X-Project-Token"),
) -> models.RepoProject:
    project = (
        db.query(models.RepoProject)
        .filter(models.RepoProject.id == project_id)
        .first()
    )
    supplied_hash = hash_project_token(project_token) if project_token else ""
    expected_hash = project.access_token_hash if project else ""
    if not project or not expected_hash or not secrets.compare_digest(
        supplied_hash, expected_hash
    ):
        raise HTTPException(status_code=404, detail="Project not found")
    return project
