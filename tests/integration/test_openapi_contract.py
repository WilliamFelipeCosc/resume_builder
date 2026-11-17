"""FND-20: the exported contract describes the actual protected HTTP boundary."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from resume_api.app import ERRORS, create_app
from resume_api.errors import MESSAGES


class NoData:
    def __getattr__(self, name):
        raise AssertionError("Schema and health cannot access diagnostics")


@pytest.fixture
def contract_client(tmp_path):
    app = create_app(service=NoData(), runtime_root=tmp_path, environment="test")
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        yield app, client


def test_health_is_public_and_minimal(contract_client):
    _, client = contract_client
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert client.get("/api/health", headers={"Host": "evil.invalid"}).status_code == 403


@pytest.mark.parametrize("path", ["/docs", "/openapi.json"])
def test_documentation_is_session_protected(contract_client, path):
    app, client = contract_client
    assert client.get(path).status_code == 401
    client.post(
        "/api/session/bootstrap",
        json={"ticket": app.state.sessions.issue()},
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    response = client.get(path)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    if path == "/docs":
        assert "/openapi.json" in response.text
        assert "https://" not in response.text
    else:
        assert response.json() == app.openapi()


def test_schema_describes_aliases_errors_and_cookie_auth():
    schema = create_app(service=NoData()).openapi()
    assert schema["openapi"].startswith("3.1.")
    components = schema["components"]["schemas"]
    assert components["DiagnosticCreate"]["required"] == ["idempotencyKey"]
    assert components["DiagnosticCreate"]["additionalProperties"] is False
    fields = components["DiagnosticExecution"]["properties"]
    assert set(fields) == {
        "id",
        "requestId",
        "idempotencyKey",
        "status",
        "attemptCount",
        "createdAt",
        "updatedAt",
        "result",
        "deliveryWarning",
        "error",
    }
    assert "leaseToken" not in json.dumps(schema)
    for path in ["/api/diagnostics", "/api/diagnostics/latest"]:
        operation = schema["paths"][path]["post" if path.endswith("diagnostics") else "get"]
        assert operation["security"] == [{"LocalSession": []}]
        for status in [401, 403, 413, 422, 500]:
            error = operation["responses"][str(status)]["content"]["application/json"]["schema"]
            assert error == {"$ref": "#/components/schemas/HttpErrorResponse"}
    assert schema["components"]["securitySchemes"]["LocalSession"] == {
        "type": "apiKey",
        "in": "cookie",
        "name": "resume_session",
    }
    assert "HTTPValidationError" not in components
    assert set(components["HttpError"]["properties"]["code"]["enum"]) == set(MESSAGES)
    assert {item[0] for item in ERRORS.values()} <= set(MESSAGES)
    assert {
        "not_found",
        "forbidden",
        "stale_revision",
        "idempotency_conflict",
        "dependent_changes",
        "missing_candidate_dependency",
        "body_too_large",
        "unsupported_media_type",
        "invalid_request",
        "rate_limited",
        "storage_unavailable",
        "database_busy",
        "internal_error",
    } <= set(components["HttpError"]["properties"]["code"]["enum"])


def test_offline_export_is_deterministic_without_runtime(tmp_path):
    target = tmp_path / "openapi.json"
    args = [sys.executable, "-m", "resume_api.export_openapi", "--output", str(target)]
    first = subprocess.run(args, capture_output=True, text=True, check=True)
    original = target.read_bytes()
    subprocess.run(args, capture_output=True, text=True, check=True)
    assert target.read_bytes() == original
    assert json.loads(original) == create_app(service=NoData()).openapi()
    assert first.stdout == "" and first.stderr == ""
    assert list(tmp_path.iterdir()) == [target]
    assert original == Path("packages/api-client/openapi.json").read_bytes()
