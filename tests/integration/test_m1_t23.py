import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from resume_api.app import create_app
from resume_core.career_kb.create import CareerCreateService
from resume_core.career_kb.queries import CareerQueries, ResponseTooLarge
from resume_core.database import make_engine, migration_config
from resume_core.service import Clearance, Principal
from sqlalchemy import text

ORIGIN = "http://127.0.0.1:8000"
SAMPLES = {
    "profile": {"fullName": "Synthetic"},
    "experience": {"companyNameOriginal": "Synthetic Co", "jobTitleOriginal": "Engineer"},
    "statement": {"textOriginal": "Synthetic"},
    "project": {"title": "Synthetic"},
    "achievement": {"textOriginal": "Synthetic"},
    "skill": {"name": "Synthetic"},
    "education": {"institution": "Synthetic", "programOriginal": "Course"},
    "language": {"language": "Synthetic", "proficiencyOriginal": "basic"},
    "evidence": {"description": "Synthetic", "evidenceKind": "manual_note"},
}


@pytest.fixture
def setup(tmp_path):
    engine = make_engine(tmp_path / "http.sqlite")
    command.upgrade(migration_config(engine), "head")
    source = str(uuid4())
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES (:id,'manual_note','hash','confidential')"
            ),
            {"id": source},
        )
    app = create_app(
        service=None,
        career_create=CareerCreateService(engine),
        career_queries=CareerQueries(engine),
        runtime_root=tmp_path,
        environment="test",
    )
    with TestClient(app, base_url=ORIGIN) as client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        yield client, app, engine, source
    engine.dispose()


def payload(kind, source, profile=None):
    content = dict(SAMPLES[kind])
    if kind == "evidence":
        content["sourceDocumentId"] = source
    return {
        "content": content,
        "sourceDocumentId": source,
        "profileId": profile,
        "idempotencyKey": str(uuid4()),
    }


@pytest.mark.parametrize("kind", SAMPLES)
def test_m1_concrete_routes_create_list_and_detail(setup, kind):
    client, _, _, source = setup
    profile = client.post(
        "/api/career/profile", json=payload("profile", source), headers={"Origin": ORIGIN}
    ).json()["id"]
    body = payload(kind, source, None if kind == "profile" else profile)
    created = client.post(f"/api/career/{kind}", json=body, headers={"Origin": ORIGIN})
    assert created.status_code == 201
    replay = client.post(f"/api/career/{kind}", json=body, headers={"Origin": ORIGIN})
    assert replay.status_code == 200 and replay.json() == created.json()
    result = client.get(f"/api/career/{kind}/{created.json()['id']}")
    assert result.status_code == 200 and result.json()["id"] == created.json()["id"]
    assert result.json()["revisionId"] == created.json()["revisionId"]
    for key, value in body["content"].items():
        assert result.json()["content"][key] == value
    page = client.get(f"/api/career/{kind}?offset=0&limit=2&archived=false")
    assert page.status_code == 200 and page.json()["limit"] == 2
    assert created.json()["id"] in [item["id"] for item in page.json()["items"]]


def test_m1_http_query_parsing_and_profile_field_filter(setup):
    client, _, _, source = setup
    first = client.post(
        "/api/career/profile", json=payload("profile", source), headers={"Origin": ORIGIN}
    )
    page = client.get(
        "/api/career/profile?offset=0&limit=25&archived=false&confirmation=unverified&confirmationField=fullName"
    )
    assert page.status_code == 200 and page.json()["total"] == 1
    assert page.json()["items"][0]["id"] == first.json()["id"]
    for query in (
        "limit=101",
        "offset=10001",
        "confirmation=confirmed",
        "confirmationField=fullName",
        "sort=bad",
    ):
        assert client.get(f"/api/career/profile?{query}").status_code == 422
    assert (
        client.get(
            "/api/career/skill?confirmation=confirmed&confirmationField=fullName"
        ).status_code
        == 422
    )


def test_m1_http_errors_auth_origin_and_hidden_source(setup, request):
    client, _, engine, source = setup
    body = payload("profile", source)
    assert client.post("/api/career/profile", json=body).status_code == 403
    assert (
        client.post(
            "/api/career/profile", json=body, headers={"Origin": "http://evil.test"}
        ).status_code
        == 403
    )
    invalid = client.post(
        "/api/career/profile",
        json=body | {"principal": "SECRET_SENTINEL"},
        headers={"Origin": ORIGIN},
    )
    assert invalid.status_code == 422 and "SECRET_SENTINEL" not in invalid.text
    invalid_field = client.post(
        "/api/career/profile",
        json=body | {"content": {"fullName": ""}},
        headers={"Origin": ORIGIN},
    )
    assert invalid_field.status_code == 422
    assert invalid_field.json()["error"]["fieldErrors"] == [{"path": "fullName", "code": "invalid"}]
    with engine.begin() as c:
        c.execute(text("UPDATE source_documents SET privacy='secret' WHERE id=:id"), {"id": source})
    runtime = Path(tempfile.mkdtemp(prefix="rb-t23-"))
    request.addfinalizer(lambda: shutil.rmtree(runtime))
    app = create_app(
        service=None,
        career_create=CareerCreateService(engine),
        career_queries=CareerQueries(engine),
        runtime_root=runtime,
        environment="test",
        principal_factory=lambda: Principal(
            "test",
            frozenset({"career:write", "career:read", "source:read"}),
            Clearance.CONFIDENTIAL,
        ),
    )
    with TestClient(app, base_url=ORIGIN) as restricted:
        assert restricted.get("/api/career/profile").status_code == 401
        restricted.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        response = restricted.post("/api/career/profile", json=body, headers={"Origin": ORIGIN})
        assert response.status_code == 404 and response.json()["error"]["code"] == "not_found"
        assert (
            restricted.get("/api/career/profile", headers={"Host": "evil.test"}).status_code == 403
        )


def test_m1_http_response_budget_is_explicit(setup):
    client, app, _, _ = setup

    class Budget:
        def list(self, *args):
            raise ResponseTooLarge

    app.state.career_queries = Budget()
    response = client.get("/api/career/profile")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "response_too_large"
    assert "smaller page" in response.json()["error"]["message"]


def test_m1_http_incomplete_entity_is_not_exposed(setup):
    client, _, engine, _ = setup
    incomplete = str(uuid4())
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES (:id,'profile','public','now','now')"
            ),
            {"id": incomplete},
        )
    assert client.get(f"/api/career/profile/{incomplete}").status_code == 404
    assert client.get("/api/career/profile").json()["total"] == 0


def test_m1_http_redacts_fields_and_provenance_for_restricted_reader(setup, request):
    client, _, engine, source = setup
    body = payload("profile", source) | {
        "content": {"fullName": "Synthetic", "phoneOriginal": "PRIVATE"},
        "privacy": "public",
        "fieldPrivacy": {"phoneOriginal": "secret"},
    }
    created = client.post("/api/career/profile", json=body, headers={"Origin": ORIGIN})
    assert created.status_code == 201
    changed = client.post(
        "/api/career/profile",
        json=body | {"content": {"fullName": "Changed"}},
        headers={"Origin": ORIGIN},
    )
    assert changed.status_code == 409 and changed.json()["error"]["code"] == "idempotency_conflict"
    runtime = Path(tempfile.mkdtemp(prefix="rb-t23-"))
    request.addfinalizer(lambda: shutil.rmtree(runtime))
    app = create_app(
        service=None,
        career_queries=CareerQueries(engine),
        runtime_root=runtime,
        environment="test",
        principal_factory=lambda: Principal("reader", frozenset({"career:read"}), Clearance.PUBLIC),
    )
    with TestClient(app, base_url=ORIGIN) as reader:
        reader.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        result = reader.get(f"/api/career/profile/{created.json()['id']}")
    assert result.status_code == 200
    assert result.json()["content"]["fullName"] == "Synthetic"
    assert result.json()["content"]["phoneOriginal"] is None
    assert result.json()["restrictedFields"] == ["phoneOriginal"]
    assert result.json()["provenance"] == [] and "PRIVATE" not in result.text


def test_m1_openapi_has_unique_concrete_models_and_no_storage_io(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("offline export accessed data")

    monkeypatch.setattr("resume_core.database.make_engine", fail)
    app = create_app(service=None)
    schema = app.openapi()
    operations = [
        operation["operationId"] for path in schema["paths"].values() for operation in path.values()
    ]
    assert len(operations) == len(set(operations))
    for kind in SAMPLES:
        path = schema["paths"][f"/api/career/{kind}"]
        assert path["post"]["operationId"] == f"create_{kind}"
        assert "$ref" in path["post"]["requestBody"]["content"]["application/json"]["schema"]
        assert path["get"]["operationId"] == f"list_{kind}"
