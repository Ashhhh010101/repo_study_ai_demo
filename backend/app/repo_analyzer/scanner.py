import hashlib
import mimetypes
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
    "target",
    ".idea",
    ".vscode",
}
IGNORED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".mp4",
    ".mov",
    ".zip",
    ".pdf",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyc",
    ".lockb",
}
TEXT_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".env",
    ".txt",
    ".css",
    ".scss",
    ".html",
    ".sql",
    ".java",
    ".go",
    ".rs",
    ".sh",
}


def is_probably_binary(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return False
    if path.suffix.lower() in IGNORED_SUFFIXES:
        return True
    mime_type, _ = mimetypes.guess_type(path.name)
    return bool(mime_type and not mime_type.startswith("text"))


def detect_language(path: Path) -> str:
    mapping = {
        ".py": "Python",
        ".ts": "TypeScript",
        ".tsx": "TypeScript React",
        ".js": "JavaScript",
        ".jsx": "JavaScript React",
        ".md": "Markdown",
        ".json": "JSON",
        ".toml": "TOML",
        ".yml": "YAML",
        ".yaml": "YAML",
        ".sql": "SQL",
        ".css": "CSS",
        ".html": "HTML",
    }
    return mapping.get(path.suffix.lower(), path.suffix.lower().lstrip(".").upper() or "Unknown")


def classify_file(path: Path) -> str:
    name = path.name.lower()
    if "readme" in name:
        return "docs"
    if name in {"package.json", "pyproject.toml", "requirements.txt", "dockerfile"}:
        return "config"
    if "test" in name:
        return "test"
    if path.suffix.lower() in {".tsx", ".jsx"}:
        return "component"
    if path.suffix.lower() in {".py", ".ts", ".js"}:
        return "code"
    return "other"


def scan_repository(root: Path, max_file_size_bytes: int) -> list[dict]:
    files: list[dict] = []
    for path in root.rglob("*"):
        if path.is_dir():
            if path.name in IGNORED_DIRS:
                continue
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.name == "package-lock.json" and path.stat().st_size > max_file_size_bytes:
            continue
        if is_probably_binary(path):
            continue
        size_bytes = path.stat().st_size
        relative_path = path.relative_to(root).as_posix()
        if size_bytes > max_file_size_bytes and "readme" not in path.name.lower():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="latin-1")
            except UnicodeDecodeError:
                continue
        files.append(
            {
                "path": relative_path,
                "absolute_path": str(path),
                "language": detect_language(path),
                "file_type": classify_file(path),
                "size_bytes": size_bytes,
                "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "content": content,
            }
        )
    return sorted(files, key=lambda item: item["path"])
