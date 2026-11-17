"""M1 error contracts never reflect rejected data."""

import pytest
from fastapi.testclient import TestClient
from resume_api.app import create_app
from resume_api.errors import HttpErrorResponse, error_response

ORIGIN = "http://127.0.0.1:8000"


@pytest.mark.parametrize(
    ("status", "code", "message"),
    [
        (404, "not_found", "Resource not found."),
        (409, "active_diagnostic", "A diagnostic is already active."),
        (413, "body_too_large", "Request body exceeds the allowed limit."),
        (415, "unsupported_media_type", "Unsupported media type."),
        (422, "invalid_request", "Request does not match the contract."),
        (429, "rate_limited", "Request limit reached."),
        (503, "storage_unavailable", "Service is temporarily unavailable."),
    ],
)
def test_error_envelope_is_typed_and_correlated(status, code, message):
    response = error_response(status, "synthetic-request")
    model = HttpErrorResponse.model_validate_json(response.body)
    assert model.error.requestId == "synthetic-request"
    assert model.error.code == code
    assert model.error.message == message


def test_validation_uses_allowlisted_paths_and_does_not_echo(tmp_path):
    app = create_app(service=None, runtime_root=tmp_path, environment="test")
    with TestClient(app, base_url=ORIGIN) as client:
        response = client.post(
            "/api/session/bootstrap",
            json={"ticket": 3, "SECRET_SENTINEL": "SECRET_SENTINEL"},
            headers={"Origin": ORIGIN},
        )
    assert response.status_code == 422
    assert response.json()["error"]["fieldErrors"] == [{"path": "ticket", "code": "invalid"}]
    assert response.json()["error"]["requestId"] == response.headers["x-request-id"]
    assert "SECRET_SENTINEL" not in response.text


def test_missing_route_is_indistinguishable_and_safe(tmp_path):
    app = create_app(service=None, runtime_root=tmp_path, environment="test")
    with TestClient(app, base_url=ORIGIN) as client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        response = client.get("/PRIVATE_SENTINEL")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["error"]["requestId"] == response.headers["x-request-id"]
    assert "PRIVATE_SENTINEL" not in response.text


def test_revision_conflicts_do_not_reflect_details():
    response = error_response(
        409,
        "synthetic-request",
        code="stale_revision",
        fields=(
            "baseRevisionId",
            "PRIVATE_SENTINEL",
        ),
    )
    assert b"PRIVATE_SENTINEL" not in response.body
    error = HttpErrorResponse.model_validate_json(response.body).error
    assert error.code == "stale_revision"
    assert [item.path for item in error.fieldErrors] == ["baseRevisionId"]
