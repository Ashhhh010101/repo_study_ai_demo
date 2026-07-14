from pathlib import PurePosixPath


HIGH_VALUE_NAMES = {
    "readme.md": 25,
    "main.py": 20,
    "app.py": 20,
    "server.ts": 20,
    "index.tsx": 18,
    "main.tsx": 18,
    "package.json": 18,
    "pyproject.toml": 18,
    "requirements.txt": 16,
    "dockerfile": 16,
    "docker-compose.yml": 16,
    ".env.example": 14,
}
HIGH_VALUE_PARTS = {
    "route": 8,
    "routes": 8,
    "controller": 8,
    "service": 8,
    "model": 7,
    "schema": 7,
    "config": 7,
    "auth": 10,
    "payment": 10,
    "db": 7,
}


def score_file(file_metadata: dict) -> float:
    path = PurePosixPath(file_metadata["path"])
    score = 1.0
    score += HIGH_VALUE_NAMES.get(path.name.lower(), 0)
    for part in path.parts:
        score += HIGH_VALUE_PARTS.get(part.lower(), 0)
    if file_metadata["file_type"] == "docs":
        score += 4
    if file_metadata["file_type"] == "config":
        score += 5
    if file_metadata["size_bytes"] < 50_000:
        score += 2
    return score


def rank_files(scanned_files: list[dict]) -> list[dict]:
    ranked = []
    for file_metadata in scanned_files:
        enriched = dict(file_metadata)
        enriched["importance_score"] = score_file(file_metadata)
        ranked.append(enriched)
    return sorted(ranked, key=lambda item: (-item["importance_score"], item["path"]))
