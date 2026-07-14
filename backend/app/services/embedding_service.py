from app.storage.vector_store import LocalVectorStore


class EmbeddingService:
    def __init__(self, vector_store: LocalVectorStore | None = None) -> None:
        self.vector_store = vector_store or LocalVectorStore()

    def index_project_chunks(self, project_id: int, chunks: list[dict]) -> None:
        self.vector_store.upsert_chunks(project_id, chunks)
