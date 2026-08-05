import os
import re
import shutil
import subprocess
import logging
from pathlib import Path

import httpx


GITHUB_REPO_PATTERN = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)
BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,254}$")


class CloneError(Exception):
    pass


logger = logging.getLogger(__name__)


def _check_remote_repo_size(owner: str, repo: str, max_bytes: int) -> None:
    """Reject repositories GitHub reports as too large before cloning."""
    try:
        response = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "repo-study-ai",
            },
            timeout=10,
            follow_redirects=False,
        )
        if response.status_code == 404:
            raise CloneError("The repository was not found or is not public.")
        response.raise_for_status()
        size_bytes = int(response.json().get("size", 0)) * 1024
        if size_bytes > max_bytes:
            raise CloneError(
                f"Repository exceeds the configured clone-size limit of {max_bytes:,} bytes."
            )
    except CloneError:
        raise
    except (httpx.HTTPError, TypeError, ValueError):
        logger.warning("GitHub repository-size preflight was unavailable")


def _directory_exceeds_limit(path: Path, max_bytes: int) -> bool:
    total = 0
    for current_root, _, filenames in os.walk(path, followlinks=False):
        for filename in filenames:
            file_path = Path(current_root) / filename
            if file_path.is_symlink():
                continue
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
            if total > max_bytes:
                return True
    return False


def validate_github_url(repo_url: str) -> tuple[str, str]:
    match = GITHUB_REPO_PATTERN.match(repo_url.strip())
    if not match:
        raise CloneError("Only public GitHub repository URLs are supported.")
    return match.group("owner"), match.group("repo")


def validate_branch_name(branch: str | None) -> str | None:
    if branch is None or not branch.strip():
        return None
    branch = branch.strip()
    invalid = (
        not BRANCH_PATTERN.fullmatch(branch)
        or ".." in branch
        or "@{" in branch
        or "//" in branch
        or branch.endswith(("/", ".", ".lock"))
    )
    if invalid:
        raise CloneError("The branch name is not a valid Git reference.")
    return branch


def clone_public_repo(
    repo_url: str,
    destination: Path,
    branch: str | None = None,
    force_refresh: bool = False,
    commit: str | None = None,
    timeout_seconds: int = 180,
    max_clone_bytes: int = 200_000_000,
) -> Path:
    owner, repo = validate_github_url(repo_url)
    canonical_url = f"https://github.com/{owner}/{repo}"
    branch = validate_branch_name(branch)
    _check_remote_repo_size(owner, repo, max_clone_bytes)
    if destination.exists() and force_refresh:
        shutil.rmtree(destination)

    marker = destination / ".repo-study-meta.json"
    if destination.exists() and marker.exists() and not force_refresh:
        if _directory_exceeds_limit(destination, max_clone_bytes):
            shutil.rmtree(destination, ignore_errors=True)
            raise CloneError(
                f"Repository exceeds the configured clone-size limit of {max_clone_bytes:,} bytes."
            )
        logger.info("Using cached repository path=%s", destination)
        return destination

    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "git",
        "clone",
        "--depth",
        "1",
        "--no-tags",
        "--single-branch",
    ]
    if branch:
        command.extend(["--branch", branch])
    command.extend(["--", canonical_url, str(destination)])

    git_env = os.environ.copy()
    git_env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_LFS_SKIP_SMUDGE": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )

    try:
        logger.info("Cloning repository branch=%s pinned_commit=%s", branch or "default", bool(commit))
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=git_env,
        )
    except subprocess.TimeoutExpired as exc:
        logger.warning("Repository clone timed out")
        if destination.exists():
            shutil.rmtree(destination)
        raise CloneError(
            "Repository cloning timed out. Try a smaller repository or increase the configured limit."
        ) from exc
    except subprocess.CalledProcessError as exc:
        logger.warning("Repository clone failed")
        if destination.exists():
            shutil.rmtree(destination)
        raise CloneError(
            "Unable to clone the repository. Verify that it is public and the branch exists."
        ) from exc
    if commit:
        try:
            subprocess.run(["git", "-C", str(destination), "fetch", "--depth", "1", "origin", commit], check=True, capture_output=True, timeout=timeout_seconds, env=git_env)
            subprocess.run(["git", "-C", str(destination), "checkout", "--detach", commit], check=True, capture_output=True, timeout=timeout_seconds, env=git_env)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            shutil.rmtree(destination, ignore_errors=True)
            raise CloneError("The requested commit is not available in the selected shallow clone.") from exc
    if _directory_exceeds_limit(destination, max_clone_bytes):
        shutil.rmtree(destination, ignore_errors=True)
        raise CloneError(
            f"Repository exceeds the configured clone-size limit of {max_clone_bytes:,} bytes."
        )
    return destination
