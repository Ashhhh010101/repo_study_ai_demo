from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.repo_analyzer.context_builder import build_file_tree
from app.schemas.repo import (
    AnalyzeResponse,
    RepoAnalysisResponse,
    RepoAnalyzeRequest,
    RepoFileResponse,
    RepoProjectResponse,
)
from app.services.repo_service import RepoService

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_repo(payload: RepoAnalyzeRequest, db: Session = Depends(get_db)):
    service = RepoService()
    project, analysis = service.analyze_repository(
        db=db,
        repo_url=payload.repo_url,
        branch=payload.branch,
        gemini_api_key=payload.gemini_api_key,
    )
    return AnalyzeResponse(
        project_id=project.id,
        status=project.status,
        report=RepoAnalysisResponse.model_validate(analysis),
    )


@router.get("/{project_id}", response_model=RepoProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.RepoProject).filter(models.RepoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/report", response_model=RepoAnalysisResponse)
def get_project_report(project_id: int, db: Session = Depends(get_db)):
    analysis = db.query(models.RepoAnalysis).filter(models.RepoAnalysis.project_id == project_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Report not found")
    return analysis


@router.get("/{project_id}/files")
def get_project_files(project_id: int, db: Session = Depends(get_db)):
    files = (
        db.query(models.RepoFile)
        .filter(models.RepoFile.project_id == project_id)
        .order_by(models.RepoFile.importance_score.desc(), models.RepoFile.path.asc())
        .all()
    )
    serialized_files = [RepoFileResponse.model_validate(file).model_dump() for file in files]
    return {
        "files": serialized_files,
        "tree": build_file_tree(serialized_files),
    }
