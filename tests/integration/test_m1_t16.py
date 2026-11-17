from uuid import uuid4

import pytest
from alembic import command
from fastapi.testclient import TestClient
from resume_api.app import create_app
from resume_core.database import make_engine, migration_config
from resume_core.service import Clearance, PermissionDenied, Principal
from resume_core.sources.manual_notes import ManualNoteService
from resume_core.sources.storage import SourceStorage
from sqlalchemy import text

ORIGIN = "http://127.0.0.1:8000"


@pytest.fixture
def setup(tmp_path):
    engine = make_engine(tmp_path / "test.sqlite")
    command.upgrade(migration_config(engine), "head")
    storage = SourceStorage(tmp_path / "data")
    service = ManualNoteService(engine, storage)
    app = create_app(
        service=None, source_service=service, runtime_root=tmp_path, environment="test"
    )
    with TestClient(app, base_url=ORIGIN) as client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        yield client, engine, storage, service
    engine.dispose()


def test_m1_manual_note_creation_replay_and_conflict(setup):
    client, engine, storage, _ = setup
    payload = {"text": "synthetic note", "title": "synthetic title", "idempotencyKey": str(uuid4())}
    first = client.post("/api/sources/manual-notes", json=payload, headers={"Origin": ORIGIN})
    replay = client.post("/api/sources/manual-notes", json=payload, headers={"Origin": ORIGIN})
    conflict = client.post(
        "/api/sources/manual-notes", json={**payload, "text": "changed"}, headers={"Origin": ORIGIN}
    )
    assert first.status_code == 201
    assert replay.status_code == 200 and replay.json() == first.json()
    assert (
        conflict.status_code == 409 and conflict.json()["error"]["code"] == "idempotency_conflict"
    )
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT kind, private_name, privacy, storage_ref FROM source_documents WHERE id=:id"
            ),
            {"id": first.json()["sourceId"]},
        ).one()
        assert tuple(row[:3]) == ("manual_note", "synthetic title", "confidential")
        assert storage.read(row.storage_ref) == b"synthetic note"
        assert connection.execute(text("SELECT count(*) FROM mutation_receipts")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM kb_audit_events")).scalar_one() == 1
        assert connection.execute(text("SELECT count(*) FROM kb_entities")).scalar_one() == 0


def test_m1_manual_note_rejects_invalid_input_without_reflection(setup):
    client, _, _, _ = setup
    for payload in (
        {"text": "", "idempotencyKey": str(uuid4())},
        {"text": "x" * 8001, "idempotencyKey": str(uuid4())},
        {"text": "ok", "title": "x" * 257, "idempotencyKey": str(uuid4())},
        {"text": "SENTINEL", "idempotencyKey": "bad"},
    ):
        response = client.post(
            "/api/sources/manual-notes", json=payload, headers={"Origin": ORIGIN}
        )
        assert response.status_code == 422
        assert "SENTINEL" not in response.text
    response = client.post(
        "/api/sources/manual-notes",
        json={"text": "ok", "title": "x" * 257, "idempotencyKey": "bad"},
        headers={"Origin": ORIGIN},
    )
    assert {item["path"] for item in response.json()["error"]["fieldErrors"]} == {
        "title",
        "idempotencyKey",
    }


def test_m1_manual_note_denial_precedes_repository_and_storage():
    class Forbidden:
        def __getattribute__(self, name):
            raise AssertionError("unauthorized access")

    service = ManualNoteService(Forbidden(), Forbidden())
    for principal in (
        Principal("test", frozenset()),
        Principal("test", frozenset({"career:write"}), Clearance.PUBLIC),
    ):
        with pytest.raises(PermissionDenied):
            service.create(principal, text="synthetic", title=None, key=uuid4(), request_id="test")


def test_m1_manual_note_replay_requires_current_source_authority(setup):
    _, engine, storage, service = setup
    key = uuid4()
    owner = Principal("test", frozenset({"career:write", "source:read"}), Clearance.CONFIDENTIAL)
    service.create(owner, text="synthetic", title=None, key=key, request_id="test")
    with pytest.raises(PermissionDenied):
        service.create(
            Principal("test", frozenset({"career:write"}), Clearance.CONFIDENTIAL),
            text="synthetic",
            title=None,
            key=key,
            request_id="test",
        )
    with engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM source_documents")).scalar_one() == 1


def test_m1_manual_note_http_denial_writes_nothing(tmp_path):
    engine = make_engine(tmp_path / "test.sqlite")
    command.upgrade(migration_config(engine), "head")
    storage = SourceStorage(tmp_path / "data")
    app = create_app(
        service=None,
        source_service=ManualNoteService(engine, storage),
        runtime_root=tmp_path,
        environment="test",
        principal_factory=lambda: Principal("restricted", frozenset(), Clearance.SECRET),
    )
    with TestClient(app, base_url=ORIGIN) as client:
        client.post(
            "/api/session/bootstrap",
            json={"ticket": app.state.sessions.issue()},
            headers={"Origin": ORIGIN},
        )
        response = client.post(
            "/api/sources/manual-notes",
            json={"text": "synthetic", "idempotencyKey": str(uuid4())},
            headers={"Origin": ORIGIN},
        )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"
    with engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM source_documents")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM mutation_receipts")).scalar_one() == 0
    assert list(storage.root.iterdir()) == []
    engine.dispose()


def test_m1_manual_note_storage_failure_rolls_back(setup, monkeypatch):
    client, engine, storage, _ = setup

    def fail(_data):
        raise OSError("private sentinel")

    monkeypatch.setattr(storage, "install", fail)
    response = client.post(
        "/api/sources/manual-notes",
        json={"text": "synthetic", "idempotencyKey": str(uuid4())},
        headers={"Origin": ORIGIN},
    )
    assert response.status_code == 503
    assert "sentinel" not in response.text
    with engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM source_documents")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM mutation_receipts")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM kb_audit_events")).scalar_one() == 0
