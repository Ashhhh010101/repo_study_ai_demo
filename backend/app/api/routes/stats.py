from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db

router = APIRouter()


@router.post("/visit", status_code=204)
def record_visit(db: Session = Depends(get_db)) -> None:
    db.add(models.AnalyticsEvent(event_type="visit"))
    db.commit()


@router.get("")
def get_stats(db: Session = Depends(get_db)) -> dict[str, object]:
    visits = db.query(func.count(models.AnalyticsEvent.id)).filter(models.AnalyticsEvent.event_type == "visit").scalar() or 0
    analyses = db.query(func.count(models.RepoProject.id)).scalar() or 0
    repos = db.query(models.RepoProject.repo_name, func.count(models.RepoProject.id)).group_by(models.RepoProject.repo_name).order_by(func.count(models.RepoProject.id).desc()).limit(10).all()
    return {"visits": visits, "analyses": analyses, "repositories": [{"name": name, "count": count} for name, count in repos]}
