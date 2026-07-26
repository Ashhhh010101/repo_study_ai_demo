from pathlib import Path

import pytest
from pydantic import SecretStr

from app.core.security import redact_sensitive_text
from app.repo_analyzer.cloner import CloneError, validate_branch_name, validate_github_url
from app.repo_analyzer.scanner import ScanLimitError, scan_repository
from app.schemas.repo import RepoAnalyzeRequest, RepoProjectResponse
from app.services.llm_service import LLMService


def test_byok_schema_redacts_secret_representation():
    raw_key = "provider-key-that-must-never-appear-in-a-representation"
    payload = RepoAnalyzeRequest(
        repo_url="https://github.com/openai/openai-python",
        gemini_api_key=raw_key,
    )

    assert raw_key not in repr(payload)
    assert isinstance(payload.gemini_api_key, SecretStr)


def test_project_api_schema_does_not_expose_server_path():
    assert "local_path" not in RepoProjectResponse.model_json_schema()["properties"]


def test_supported_repository_and_branch_validation():
    assert validate_github_url("https://github.com/openai/openai-python.git") == (
        "openai",
        "openai-python",
    )
    assert validate_branch_name("feature/security-hardening") == "feature/security-hardening"

    with pytest.raises(CloneError):
        validate_github_url("https://example.com/owner/repo")
    with pytest.raises(CloneError):
        validate_branch_name("--upload-pack=malicious")
    with pytest.raises(CloneError):
        validate_branch_name("refs/heads/../escape")


def test_sensitive_values_are_redacted_before_provider_calls():
    provider_key = "provider-secret-value-that-must-be-redacted"
    google_key = "AI" + "za" + "abcdefghijklmnopqrstuvwxyz123456789"
    github_token = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"
    text = (
        f"provider={provider_key}\n"
        f"google={google_key}\n"
        "api_key='a-very-sensitive-application-value'\n"
        f"token={github_token}"
    )

    result = redact_sensitive_text(text, extra_values=(provider_key,))

    assert provider_key not in result
    assert google_key not in result
    assert "a-very-sensitive-application-value" not in result
    assert github_token not in result
    assert "[REDACTED]" in result


def test_provider_key_uses_header_and_never_enters_url_or_prompt(monkeypatch):
    captured: dict = {}
    raw_key = "provider-key-that-must-remain-out-of-the-url"

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "safe response"}]}}]}

    class FakeClient:
        def __init__(self, **_: object):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_: object):
            return None

        def post(self, url: str, *, headers: dict, json: dict):
            captured.update(url=url, headers=headers, payload=json)
            return FakeResponse()

    monkeypatch.setattr("app.services.llm_service.httpx.Client", FakeClient)

    result = LLMService().generate_text(
        f"Repository content accidentally contains {raw_key}",
        SecretStr(raw_key),
    )

    assert result == "safe response"
    assert raw_key not in captured["url"]
    assert captured["headers"]["x-goog-api-key"] == raw_key
    assert raw_key not in str(captured["payload"])


def test_scanner_skips_sensitive_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("print('safe')", encoding="utf-8")
    (tmp_path / ".env").write_text("API_KEY=do-not-read", encoding="utf-8")
    (tmp_path / ".env.example").write_text("API_KEY=replace-me", encoding="utf-8")
    (tmp_path / "private.pem").write_text("private material", encoding="utf-8")

    files = scan_repository(tmp_path, max_file_size_bytes=10_000)
    paths = {item["path"] for item in files}

    assert "app.py" in paths
    assert ".env.example" in paths
    assert ".env" not in paths
    assert "private.pem" not in paths


def test_scanner_enforces_repository_limits(tmp_path: Path):
    (tmp_path / "one.py").write_text("one", encoding="utf-8")
    (tmp_path / "two.py").write_text("two", encoding="utf-8")

    with pytest.raises(ScanLimitError):
        scan_repository(
            tmp_path,
            max_file_size_bytes=10_000,
            max_files=1,
            max_total_bytes=10_000,
        )


def test_scanner_does_not_follow_file_symlinks(tmp_path: Path):
    outside_file = tmp_path.parent / "outside-scanner-fixture.txt"
    outside_file.write_text("must not be scanned", encoding="utf-8")
    link = tmp_path / "linked.txt"
    try:
        link.symlink_to(outside_file)
    except OSError:
        pytest.skip("Creating symlinks is not available in this environment")

    files = scan_repository(tmp_path, max_file_size_bytes=10_000)

    assert "linked.txt" not in {item["path"] for item in files}
