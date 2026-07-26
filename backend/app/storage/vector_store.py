import json
from collections import Counter
from pathlib import Path
import re
from threading import Lock

from app.core.config import get_settings


TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}")


class LocalVectorStore:
    _cache_lock = Lock()
    _records_cache: dict[int, tuple[float, list[dict]]] = {}

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
        with self._cache_lock:
            self._records_cache.pop(project_id, None)

    def _load_records(self, project_id: int) -> list[dict]:
        path = self._project_index_path(project_id)
        if not path.exists():
            return []

        modified_at = path.stat().st_mtime
        with self._cache_lock:
            cached = self._records_cache.get(project_id)
            if cached and cached[0] == modified_at:
                return cached[1]

        records = json.loads(path.read_text(encoding="utf-8"))
        with self._cache_lock:
            self._records_cache[project_id] = (modified_at, records)
        return records

    def search(self, project_id: int, query: str, limit: int = 6) -> list[dict]:
        records = self._load_records(project_id)
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
