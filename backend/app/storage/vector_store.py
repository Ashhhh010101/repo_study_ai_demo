import json
from collections import Counter
from pathlib import Path
import re

from app.core.config import get_settings


TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")


class LocalVectorStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _project_index_path(self, project_id: int) -> Path:
        return self.settings.vector_store_dir / f"{project_id}.json"

    def upsert_chunks(self, project_id: int, chunks: list[dict]) -> None:
        serializable = []
        for chunk in chunks:
            tokens = TOKEN_PATTERN.findall(chunk["content"].lower())
            serializable.append(
                {
                    **chunk,
                    "token_counts": Counter(tokens),
                }
            )
        path = self._project_index_path(project_id)
        path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def search(self, project_id: int, query: str, limit: int = 6) -> list[dict]:
        path = self._project_index_path(project_id)
        if not path.exists():
            return []
        records = json.loads(path.read_text(encoding="utf-8"))
        query_tokens = Counter(TOKEN_PATTERN.findall(query.lower()))
        if not query_tokens:
            return records[:limit]

        scored = []
        for record in records:
            token_counts = Counter(record.get("token_counts", {}))
            score = sum(token_counts[token] * weight for token, weight in query_tokens.items())
            if query.lower() in record["content"].lower():
                score += 5
            if score > 0:
                scored.append((score, record))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [record for _, record in scored[:limit]]
