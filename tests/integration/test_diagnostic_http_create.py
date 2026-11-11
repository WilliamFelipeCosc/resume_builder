"""FND-01/05/06/14/16/17/18: authorized, bounded durable creation."""

import io
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from resume_api.app import create_app
from resume_core.contracts import DiagnosticExecution
from resume_core.logging_policy import configure_logging
from resume_core.service import DiagnosticService

ORIGIN = "http://127.0.0.1:8000"
SENTINEL = "PRIVATE_SENTINEL_REQUEST"


@pytest.fixture
def diagnostic_http(repository, tmp_path):
    repo, clock = repository
    output = io.StringIO()
    configure_logging(stream=output)
    app = create_app(service=DiagnosticService(repo), runtime_root=tmp_path, environment="test")
    with TestClient(app, base_url=ORIGIN) as client:
        yield app, client, repo, clock, output


def login(app, client):
    response = client.post(
        "/api/session/bootstrap",
        json={"ticket": app.state.sessions.issue()},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 200


def create(client, key=None, **kwargs):
    return client.post(
        "/api/diagnostics",
        json={"idempotencyKey": str(key or uuid4())},
        headers={"Origin": ORIGIN, "X-Request-ID": SENTINEL},
        **kwargs,
    )


def test_creation_is_durable_full_contract_and_server_correlation(diagnostic_http):
    app, client, repo, _, output = diagnostic_http
    login(app, client)
    key = uuid4()
    response = create(client, key)
    assert response.status_code == 202
    execution = DiagnosticExecution.model_validate(response.json()["execution"])
    assert execution == repo.get(execution.id)
    assert execution.idempotency_key == key
    assert execution.status == "pending"
    assert execution.attempt_count == 0
    assert execution.created_at == execution.updated_at
    assert execution.created_at.utcoffset().total_seconds() == 0
    assert execution.result is execution.error is execution.delivery_warning is None
    assert str(execution.request_id) == response.headers["x-request-id"]
    assert UUID(response.headers["x-request-id"])
    assert response.headers["cache-control"] == "no-store"
    assert SENTINEL not in response.text + output.getvalue()


def test_idempotency_active_and_terminal_without_second_effect(diagnostic_http):
    app, client, repo, _, _ = diagnostic_http
    login(app, client)
    key = uuid4()
    first = create(client, key)
    original = first.json()["execution"]
    replay = create(client, key)
    assert replay.status_code == 200
    assert replay.json()["execution"] == original
    assert replay.headers["x-request-id"] != original["requestId"]
    lease = repo.claim(UUID(original["id"]))
    assert repo.complete(lease.execution.id, lease.token)
    latest = create(client, key)
    assert latest.status_code == 200
    assert latest.json()["execution"]["id"] == original["id"]
    assert latest.json()["execution"]["attemptCount"] == 1
    assert latest.json()["execution"]["result"] == {
        "message": "diagnostic_completed",
        "fixtureVersion": "m0-v1",
    }


def test_distinct_active_intention_409_no_new_row(diagnostic_http):
    app, client, repo, _, _ = diagnostic_http
    login(app, client)
    first = create(client)
    response = create(client)
    assert response.status_code == 409
    assert repo.latest().id == UUID(first.json()["execution"]["id"])
    assert response.json()["error"]["code"] == "active_diagnostic"


@pytest.mark.parametrize(
    "kind,expected",
    [("missing", 401), ("invalid", 401), ("origin", 403), ("noorigin", 403), ("host", 403)],
)
def test_denied_request_never_accesses_service(diagnostic_http, kind, expected):
    app, client, repo, _, _ = diagnostic_http
    if kind not in {"missing", "invalid"}:
        login(app, client)

    class Poison:
        def create(self, *args, **kwargs):
            raise AssertionError("unauthorized service access")

    app.state.service = Poison()
    headers = {"Origin": ORIGIN}
    if kind == "invalid":
        headers["Cookie"] = "resume_session=invalid"
    elif kind == "origin":
        headers["Origin"] = "https://evil.invalid"
    elif kind == "noorigin":
        headers = {}
    elif kind == "host":
        headers["Host"] = "evil.invalid:8000"
    response = client.post(
        "/api/diagnostics", json={"idempotencyKey": str(uuid4())}, headers=headers
    )
    assert response.status_code == expected
    assert repo.latest() is None


@pytest.mark.parametrize(
    "body",
    [
        {"idempotencyKey": SENTINEL},
        {"idempotencyKey": str(uuid4()), "fixture": SENTINEL},
        {"idempotency_key": str(uuid4())},
        {},
        {"idempotencyKey": 123},
        [SENTINEL],
    ],
)
def test_invalid_contract_never_persists_or_echoes(diagnostic_http, body):
    app, client, repo, _, output = diagnostic_http
    login(app, client)
    response = client.post("/api/diagnostics", json=body, headers={"Origin": ORIGIN})
    assert response.status_code == 422
    assert repo.latest() is None
    assert SENTINEL not in response.text + output.getvalue()


@pytest.mark.parametrize("chunked", [False, True])
def test_oversized_body_never_persists(diagnostic_http, chunked):
    app, client, repo, _, output = diagnostic_http
    login(app, client)
    content = SENTINEL.encode() * 100
    if chunked:
        content = iter([content[:500], content[500:]])
    response = client.post(
        "/api/diagnostics",
        content=content,
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert repo.latest() is None
    assert SENTINEL not in response.text + output.getvalue()


def test_unexpected_exception_sanitized(diagnostic_http):
    app, client, repo, _, output = diagnostic_http
    login(app, client)

    class Broken:
        def create(self, *args, **kwargs):
            raise RuntimeError(SENTINEL)

    app.state.service = Broken()
    response = create(client)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert repo.latest() is None
    assert SENTINEL not in response.text + output.getvalue()
    assert "Traceback" not in response.text + output.getvalue()
