from math import ceil


def detect_chunk_type(file_metadata: dict) -> str:
    path = file_metadata["path"].lower()
    if "readme" in path or path.endswith(".md"):
        return "docs"
    if any(token in path for token in ("route", "router", "endpoint")):
        return "route"
    if any(token in path for token in ("model", "schema")):
        return "model"
    if "service" in path:
        return "service"
    if any(token in path for token in ("test", "spec")):
        return "test"
    if file_metadata["file_type"] == "config":
        return "config"
    if file_metadata["file_type"] == "component":
        return "component"
    return "code"


def chunk_file(file_metadata: dict, max_chars: int) -> list[dict]:
    content = file_metadata["content"]
    lines = content.splitlines() or [""]
    if len(content) <= max_chars:
        return [
            {
                "path": file_metadata["path"],
                "chunk_type": detect_chunk_type(file_metadata),
                "content": content,
                "start_line": 1,
                "end_line": len(lines),
            }
        ]

    chunks: list[dict] = []
    approx_chunks = ceil(len(content) / max_chars)
    lines_per_chunk = max(1, ceil(len(lines) / approx_chunks))
    for start_index in range(0, len(lines), lines_per_chunk):
        end_index = min(len(lines), start_index + lines_per_chunk)
        chunk_lines = lines[start_index:end_index]
        chunk_content = "\n".join(chunk_lines)
        if not chunk_content.strip():
            continue
        chunks.append(
            {
                "path": file_metadata["path"],
                "chunk_type": detect_chunk_type(file_metadata),
                "content": chunk_content[: max_chars + 250],
                "start_line": start_index + 1,
                "end_line": end_index,
            }
        )
    return chunks
