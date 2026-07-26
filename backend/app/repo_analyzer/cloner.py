import os
import re
import shutil
import subprocess
from pathlib import Path


GITHUB_REPO_PATTERN = re.compile(
    r"^https://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)
BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,254}$")


class CloneError(Exception):
    pass


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
    timeout_seconds: int = 180,
) -> Path:
    owner, repo = validate_github_url(repo_url)
    canonical_url = f"https://github.com/{owner}/{repo}"
    branch = validate_branch_name(branch)
    if destination.exists() and force_refresh:
        shutil.rmtree(destination)

    if destination.exists() and any(destination.iterdir()):
        return destination

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
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=git_env,
        )
    except subprocess.TimeoutExpired as exc:
        if destination.exists():
            shutil.rmtree(destination)
        raise CloneError(
            "Repository cloning timed out. Try a smaller repository or increase the configured limit."
        ) from exc
    except subprocess.CalledProcessError as exc:
        if destination.exists():
            shutil.rmtree(destination)
        raise CloneError(
            "Unable to clone the repository. Verify that it is public and the branch exists."
        ) from exc
    return destination
