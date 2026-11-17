import hashlib
from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from resume_api.app import create_app
from resume_core.database import make_engine, migration_config
from resume_core.service import Clearance, PermissionDenied, Principal
from resume_core.sources.manual_notes import ManualNoteService
from resume_core.sources.queries import SourceQueries
from resume_core.sources.storage import SourceStorage
from sqlalchemy import event, text

ORIGIN = "http://127.0.0.1:8000"


@pytest.fixture
def setup(tmp_path):
    engine = make_engine(tmp_path / "test.sqlite")
    command.upgrade(migration_config(engine), "head")
    storage = SourceStorage(tmp_path / "data")
    service = ManualNoteService(engine, storage)
    queries = SourceQueries(engine, storage)
    owner = Principal("test", frozenset({"career:write", "source:read"}), Clearance.SECRET)
    source_id, _ = service.create(
        owner, text="synthetic note", title="synthetic title", key=uuid4(), request_id="test"
    )
    yield tmp_path, engine, storage, queries, source_id
    engine.dispose()


def client_for(tmp_path, queries, principal):
    app = create_app(
        service=None,
        source_queries=queries,
        runtime_root=tmp_path,
        environment="test",
        principal_factory=lambda: principal,
    )
    client = TestClient(app, base_url=ORIGIN)
    return app, client


def test_m1_source_metadata_and_attachment(setup):
    root, _, _, queries, source_id = setup
    principal = Principal("test", frozenset({"source:read"}), Clearance.CONFIDENTIAL)
    app, client = client_for(root, queries, principal)
    with client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        metadata = client.get(f"/api/sources/{source_id}")
        content = client.get(f"/api/sources/{source_id}/content")
    assert metadata.status_code == 200
    assert metadata.json() == {
        "id": source_id,
        "kind": "manual_note",
        "sha256": hashlib.sha256(b"synthetic note").hexdigest(),
        "title": "synthetic title",
        "mediaType": "text/plain; charset=utf-8",
        "pageCount": None,
        "privacy": "confidential",
    }
    assert content.status_code == 200 and content.content == b"synthetic note"
    assert content.headers["content-disposition"] == 'attachment; filename="source.txt"'
    assert content.headers["cache-control"] == "no-store"


def test_m1_source_hidden_matches_missing_and_sql_filters_before_values(setup):
    _, engine, _, queries, source_id = setup
    principal = Principal("test", frozenset({"source:read", "career:read"}), Clearance.PUBLIC)
    statements = []

    @event.listens_for(engine, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, many):
        statements.append(statement.lower())

    assert queries.metadata(principal, source_id) is None
    assert queries.metadata(principal, str(uuid4())) is None
    assert all("source_documents.privacy in" in statement for statement in statements)


def test_m1_source_hidden_http_is_404_and_fact_access_does_not_grant_source(setup):
    root, _, _, queries, source_id = setup
    principal = Principal("test", frozenset({"source:read", "career:read"}), Clearance.PUBLIC)
    app, client = client_for(root, queries, principal)
    with client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        hidden = client.get(f"/api/sources/{source_id}")
        absent = client.get(f"/api/sources/{uuid4()}")
        content = client.get(f"/api/sources/{source_id}/content")
    assert hidden.status_code == absent.status_code == content.status_code == 404
    assert hidden.json()["error"]["code"] == absent.json()["error"]["code"] == "not_found"


def test_m1_source_corrupt_or_missing_content_is_blocked(setup):
    root, engine, storage, queries, source_id = setup
    principal = Principal("test", frozenset({"source:read"}), Clearance.SECRET)
    with engine.connect() as connection:
        ref = connection.execute(
            text("SELECT storage_ref FROM source_documents WHERE id=:id"), {"id": source_id}
        ).scalar_one()
    path = storage.root / ref
    app, client = client_for(root, queries, principal)
    with client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        path.write_bytes(b"tampered")
        assert client.get(f"/api/sources/{source_id}/content").status_code == 503
        path.unlink()
        assert client.get(f"/api/sources/{source_id}/content").status_code == 503


def test_m1_source_denial_precedes_repository():
    class Forbidden:
        def __getattribute__(self, name):
            raise AssertionError("unauthorized access")

    queries = SourceQueries(Forbidden(), Forbidden())
    with pytest.raises(PermissionDenied):
        queries.content(
            Principal("test", frozenset({"career:read"}), Clearance.SECRET), str(uuid4())
        )
