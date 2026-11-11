"""FND-13..18: bootstrap boundary must neither leak input nor touch diagnostics."""

import io
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from resume_api.app import COOKIE_NAME, create_app
from resume_core.logging_policy import configure_logging

ORIGIN = "http://127.0.0.1:8000"
SENTINEL = "PRIVATE_SENTINEL_COOKIE_TICKET"


class NoDiagnosticAccess:
    def __getattr__(self, name):
        raise AssertionError("Bootstrap cannot access diagnostics")


@pytest.fixture
def http_app(tmp_path):
    output = io.StringIO()
    configure_logging(stream=output)
    app = create_app(service=NoDiagnosticAccess(), runtime_root=tmp_path, environment="test")
    with TestClient(app, base_url=ORIGIN) as client:
        yield app, client, output


def bootstrap(app, client, **kwargs):
    return client.post(
        "/api/session/bootstrap",
        json={"ticket": app.state.sessions.issue()},
        headers={"Origin": ORIGIN},
        **kwargs,
    )


def test_bootstrap_session_cookie_and_headers(http_app):
    app, client, output = http_app
    response = bootstrap(app, client)
    assert response.status_code == 200
    assert response.json() == {"authorized": True}
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/" in cookie
    assert all(value not in cookie.lower() for value in ["domain=", "expires=", "max-age="])
    assert app.state.sessions.authorized(client.cookies[COOKIE_NAME])
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert client.cookies[COOKIE_NAME] not in output.getvalue()


@pytest.mark.parametrize(
    "headers",
    [{}, {"Origin": "https://evil.invalid"}, {"Origin": ORIGIN, "Host": "localhost:8000"}],
)
def test_bootstrap_rejects_origin_host_before_ticket_consumption(http_app, headers):
    app, client, _ = http_app
    ticket = app.state.sessions.issue()
    response = client.post("/api/session/bootstrap", json={"ticket": ticket}, headers=headers)
    assert response.status_code == 403
    assert app.state.sessions.redeem(ticket) is not None


@pytest.mark.parametrize(
    "payload", [{"ticket": 12}, {"ticket": SENTINEL, "extra": SENTINEL}, {}, [SENTINEL]]
)
def test_bootstrap_contract_errors_do_not_echo(http_app, payload):
    _, client, output = http_app
    response = client.post("/api/session/bootstrap", json=payload, headers={"Origin": ORIGIN})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert SENTINEL not in response.text + output.getvalue()


def test_bootstrap_ticket_missing_repeated_and_expired(http_app):
    app, client, _ = http_app
    for ticket in [SENTINEL, ""]:
        response = client.post(
            "/api/session/bootstrap", json={"ticket": ticket}, headers={"Origin": ORIGIN}
        )
        assert response.status_code == 401
    ticket = app.state.sessions.issue()
    for expected in [200, 401]:
        response = client.post(
            "/api/session/bootstrap", json={"ticket": ticket}, headers={"Origin": ORIGIN}
        )
        assert response.status_code == expected
    now = [0.0]
    app.state.sessions.clock = lambda: now[0]
    expired = app.state.sessions.issue()
    now[0] = 30.0
    assert (
        client.post(
            "/api/session/bootstrap", json={"ticket": expired}, headers={"Origin": ORIGIN}
        ).status_code
        == 401
    )


def test_bootstrap_atomic_http_replay(http_app):
    app, client, _ = http_app
    ticket = app.state.sessions.issue()
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(
            pool.map(
                lambda _: client.post(
                    "/api/session/bootstrap", json={"ticket": ticket}, headers={"Origin": ORIGIN}
                ),
                range(4),
            )
        )
    assert sorted(response.status_code for response in responses) == [200, 401, 401, 401]


@pytest.mark.parametrize("kind", ["oversize", "chunked", "wrongtype", "invalidjson"])
def test_bootstrap_body_boundary(http_app, kind):
    _, client, output = http_app
    payload = (SENTINEL * 60).encode()
    headers = {"Origin": ORIGIN, "Content-Type": "application/json"}
    expected = 413
    if kind == "chunked":
        content = iter([payload[:800], payload[800:]])
    elif kind == "wrongtype":
        headers["Content-Type"] = "text/plain"
        content, expected = b"{}", 422
    elif kind == "invalidjson":
        content, expected = SENTINEL.encode(), 422
    else:
        content = payload
    response = client.post("/api/session/bootstrap", content=content, headers=headers)
    assert response.status_code == expected
    assert SENTINEL not in response.text + output.getvalue()


def test_new_api_invalidates_old_cookie_and_ticket(tmp_path):
    with TestClient(
        create_app(service=NoDiagnosticAccess(), runtime_root=tmp_path, environment="test"),
        base_url=ORIGIN,
    ) as first:
        app = first.app
        bootstrap(app, first)
        old = first.cookies[COOKIE_NAME]
        ticket = app.state.sessions.issue()
    second_app = create_app(service=NoDiagnosticAccess(), runtime_root=tmp_path, environment="test")
    with TestClient(second_app, base_url=ORIGIN) as second:
        assert not second_app.state.sessions.authorized(old)
        assert (
            second.post(
                "/api/session/bootstrap",
                json={"ticket": ticket},
                headers={"Origin": ORIGIN, "Cookie": f"{COOKIE_NAME}={old}"},
            ).status_code
            == 401
        )


def test_http_logs_are_json_sanitized_correlated(http_app):
    _, client, output = http_app
    response = client.post(
        "/api/session/bootstrap",
        json={"ticket": SENTINEL},
        headers={"Origin": ORIGIN, "Cookie": SENTINEL, "X-Request-ID": SENTINEL},
    )
    assert response.status_code == 401
    events = [json.loads(line) for line in output.getvalue().splitlines()]
    request = [event for event in events if event["event"] == "request_completed"][-1]
    assert request["request_id"] == response.headers["x-request-id"]
    assert request["status_code"] == 401
    assert SENTINEL not in output.getvalue() + response.text
