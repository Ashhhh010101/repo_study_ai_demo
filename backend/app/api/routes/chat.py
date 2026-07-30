from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.repo_analyzer.prompt_manager import REPO_QA_PROMPT
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService, ProviderError
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/{project_id}", response_model=ChatResponse)
def chat_with_repo(project_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    project = db.query(models.RepoProject).filter(models.RepoProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    analysis = db.query(models.RepoAnalysis).filter(models.RepoAnalysis.project_id == project_id).first()
    if not analysis:
        raise HTTPException(status_code=400, detail="Project has not been analyzed yet")

    session = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.project_id == project_id)
        .order_by(models.ChatSession.created_at.asc())
        .first()
    )
    if not session:
        session = models.ChatSession(project_id=project_id, title="Default Session")
        db.add(session)
        db.commit()
        db.refresh(session)

    retrieval_service = RetrievalService()
    used_chunks = retrieval_service.retrieve_for_question(db, project_id, payload.message, limit=8)
    history = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )
    history_summary = "\n".join(f"{message.role}: {message.content}" for message in reversed(history))
    retrieved_text = "\n\n".join(
        [
            f"File: {chunk.get('file_path')}"
            f" ({chunk.get('start_line')}-{chunk.get('end_line')})\n{chunk.get('content', '')[:2500]}"
            for chunk in used_chunks
        ]
    )
    prompt = REPO_QA_PROMPT.format(
        question=payload.message,
        report_summary=analysis.generated_report_markdown[:6000],
        retrieved_chunks=retrieved_text or "No relevant chunks found.",
        chat_history=history_summary or "No prior history.",
    )

    llm_service = LLMService()
    try:
        answer = llm_service.generate_text(prompt, payload.gemini_api_key, model=payload.model, provider=payload.provider)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    db.add(
        models.ChatMessage(
            session_id=session.id,
            role="user",
            content=payload.message,
            used_chunks_json=[],
        )
    )
    db.add(
        models.ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            used_chunks_json=used_chunks,
        )
    )
    db.commit()

    return ChatResponse(answer=answer, used_chunks=used_chunks)
