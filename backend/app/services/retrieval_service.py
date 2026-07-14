from sqlalchemy.orm import Session

from app.db import models
from app.storage.vector_store import LocalVectorStore


class RetrievalService:
    def __init__(self, vector_store: LocalVectorStore | None = None) -> None:
        self.vector_store = vector_store or LocalVectorStore()

    def retrieve_for_question(self, db: Session, project_id: int, question: str, limit: int = 6) -> list[dict]:
        matches = self.vector_store.search(project_id, question, limit=limit)
        if matches:
            return matches

        chunks = (
            db.query(models.CodeChunk)
            .filter(models.CodeChunk.project_id == project_id)
            .limit(limit)
            .all()
        )
        return [
            {
                "chunk_id": chunk.id,
                "file_path": chunk.file.path if chunk.file else "",
                "content": chunk.content,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "summary": chunk.summary,
            }
            for chunk in chunks
        ]
