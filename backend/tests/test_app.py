import os
from pathlib import Path

import pytest

TEST_RUNTIME_DIR = Path(__file__).parent / "runtime"
TEST_DB_PATH = TEST_RUNTIME_DIR / "test_repo_study_ai.db"
TEST_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH.as_posix()}")
os.environ.setdefault("DATA_DIR", str(TEST_RUNTIME_DIR))
os.environ.setdefault("REPOS_DIR", str(TEST_RUNTIME_DIR / "repos"))
os.environ.setdefault("VECTOR_STORE_DIR", str(TEST_RUNTIME_DIR / "vector_store"))

from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


def test_openapi_schema_is_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Repo Study AI"


def test_api_responses_include_security_headers(client):
    response = client.get("/openapi.json")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_validation_errors_do_not_echo_api_keys(client):
    exposed_value = "tiny-key"
    response = client.post(
        "/api/repos/analyze",
        json={
            "repo_url": "not-a-github-url",
            "gemini_api_key": exposed_value,
        },
    )

    assert response.status_code == 422
    assert exposed_value not in response.text


def test_cors_allows_only_configured_frontend_origin(client):
    allowed = client.options(
        "/api/repos/analyze",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    denied = client.options(
        "/api/repos/analyze",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "access-control-allow-origin" not in denied.headers


def test_missing_project_returns_404(client):
    response = client.get("/api/repos/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_missing_project_report_returns_404(client):
    response = client.get("/api/repos/999999/report")

    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found"


def test_missing_project_files_returns_404(client):
    response = client.get("/api/repos/999999/files")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def teardown_module():
    from app.db.session import engine

    engine.dispose()
    TEST_DB_PATH.unlink(missing_ok=True)
