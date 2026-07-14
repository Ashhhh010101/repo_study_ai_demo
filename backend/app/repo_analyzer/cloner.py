import re
import shutil
import subprocess
from pathlib import Path


GITHUB_REPO_PATTERN = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)


class CloneError(Exception):
    pass


def validate_github_url(repo_url: str) -> tuple[str, str]:
    match = GITHUB_REPO_PATTERN.match(repo_url.strip())
    if not match:
        raise CloneError("Only public GitHub repository URLs are supported.")
    return match.group("owner"), match.group("repo")


def clone_public_repo(
    repo_url: str,
    destination: Path,
    branch: str | None = None,
    force_refresh: bool = False,
) -> Path:
    validate_github_url(repo_url)
    if destination.exists() and force_refresh:
        shutil.rmtree(destination)

    if destination.exists() and any(destination.iterdir()):
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    command = ["git", "clone", repo_url, str(destination)]
    if branch:
        command = ["git", "clone", "--branch", branch, "--single-branch", repo_url, str(destination)]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() or exc.stdout.strip()
        raise CloneError(f"Git clone failed: {stderr}") from exc
    return destination
