import hashlib
import mimetypes
import os
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
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
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
SENSITIVE_FILENAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
SAFE_ENV_SUFFIXES = (".example", ".sample", ".template")


class ScanLimitError(Exception):
    pass


def is_sensitive_file(path: Path) -> bool:
    name = path.name.lower()
    if name in SENSITIVE_FILENAMES:
        return True
    if name == ".env" or (name.startswith(".env.") and not name.endswith(SAFE_ENV_SUFFIXES)):
        return True
    return path.suffix.lower() in {".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"}


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


def scan_repository(
    root: Path,
    max_file_size_bytes: int,
    max_files: int = 5_000,
    max_total_bytes: int = 50_000_000,
) -> list[dict]:
    root = root.resolve()
    files: list[dict] = []
    total_bytes = 0
    for current_root, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current_root)
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORED_DIRS
            and not (current_path / dirname).is_symlink()
        ]
        for filename in filenames:
            path = current_path / filename
            try:
                relative_path_obj = path.relative_to(root)
            except ValueError:
                continue
            if path.is_symlink() or is_sensitive_file(path):
                continue
            if any(part in IGNORED_DIRS for part in relative_path_obj.parts):
                continue
            if is_probably_binary(path):
                continue
            try:
                size_bytes = path.stat().st_size
            except OSError:
                continue
            if size_bytes > max_file_size_bytes:
                continue
            if len(files) >= max_files:
                raise ScanLimitError(
                    f"Repository exceeds the configured limit of {max_files:,} scannable files."
                )
            if total_bytes + size_bytes > max_total_bytes:
                raise ScanLimitError(
                    "Repository exceeds the configured total scan-size limit."
                )
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                try:
                    content = path.read_text(encoding="latin-1")
                except (OSError, UnicodeDecodeError):
                    continue
            relative_path = relative_path_obj.as_posix()
            total_bytes += size_bytes
            files.append(
                {
                    "path": relative_path,
                    "language": detect_language(path),
                    "file_type": classify_file(path),
                    "size_bytes": size_bytes,
                    "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    "content": content,
                }
            )
    return sorted(files, key=lambda item: item["path"])
