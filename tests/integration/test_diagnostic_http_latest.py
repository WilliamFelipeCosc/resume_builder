"""FND-04/11/14/16/18: latest state reconciles before authorized read."""

from uuid import UUID

import pytest
from resume_core.contracts import DiagnosticExecution
from test_diagnostic_http_create import (
    SENTINEL,
    create,
    login,
)
from test_diagnostic_http_create import (
    diagnostic_http as diagnostic_http,
)


def test_latest_empty_envelope(diagnostic_http):
    app, client, _, _, _ = diagnostic_http
    login(app, client)
    response = client.get("/api/diagnostics/latest")
    assert response.status_code == 200
    assert response.json() == {"execution": None}
    assert response.headers["cache-control"] == "no-store"


def test_latest_restores_persisted_full_result(diagnostic_http):
    app, client, repo, _, output = diagnostic_http
    login(app, client)
    creation = create(client).json()["execution"]
    execution_id = UUID(creation["id"])
    lease = repo.claim(execution_id)
    assert repo.complete(execution_id, lease.token)
    response = client.get("/api/diagnostics/latest", headers={"X-Request-ID": SENTINEL})
    assert response.status_code == 200
    assert DiagnosticExecution.model_validate(response.json()["execution"]) == repo.get(
        execution_id
    )
    assert response.json()["execution"]["result"] == {
        "message": "diagnostic_completed",
        "fixtureVersion": "m0-v1",
    }
    assert response.headers["x-request-id"] != creation["requestId"]
    assert response.json()["execution"]["requestId"] == creation["requestId"]
    assert SENTINEL not in response.text + output.getvalue()


def test_read_reconciles_exact_total_deadline(diagnostic_http):
    app, client, repo, clock, _ = diagnostic_http
    login(app, client)
    before = create(client).json()["execution"]
    clock.advance(120)
    response = client.get("/api/diagnostics/latest")
    execution = response.json()["execution"]
    assert execution["id"] == before["id"]
    assert execution["status"] == "failed"
    assert execution["error"] == {
        "code": "deadline_exceeded",
        "message": "Diagnostic deadline exceeded.",
    }
    assert repo.latest().status == "failed"


def test_polling_does_not_modify_timestamp(diagnostic_http):
    app, client, _, clock, _ = diagnostic_http
    login(app, client)
    original = create(client).json()["execution"]
    clock.advance(1)
    first = client.get("/api/diagnostics/latest")
    second = client.get("/api/diagnostics/latest")
    assert first.json()["execution"] == second.json()["execution"] == original


@pytest.mark.parametrize(
    "kind,expected", [("missing", 401), ("invalid", 401), ("host", 403), ("origin", 403)]
)
def test_latest_denied_before_service(diagnostic_http, kind, expected):
    app, client, repo, _, _ = diagnostic_http
    if kind in {"host", "origin"}:
        login(app, client)

    class Poison:
        def latest(self, *args):
            raise AssertionError("Unauthorized read")

    app.state.service = Poison()
    headers = {}
    if kind == "invalid":
        headers["Cookie"] = "resume_session=invalid"
    elif kind == "host":
        headers["Host"] = "evil.invalid:8000"
    elif kind == "origin":
        headers["Origin"] = "https://evil.invalid"
    response = client.get("/api/diagnostics/latest", headers=headers)
    assert response.status_code == expected
    assert repo.latest() is None


def test_oversized_read_body_is_bounded(diagnostic_http):
    app, client, repo, _, _ = diagnostic_http
    login(app, client)
    response = client.request("GET", "/api/diagnostics/latest", content=b"x" * 1025)
    assert response.status_code == 413
    assert repo.latest() is None
