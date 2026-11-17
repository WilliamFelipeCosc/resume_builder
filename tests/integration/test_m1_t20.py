from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from resume_core.career_kb.contracts import ProfileContent
from resume_core.career_kb.repository import CareerRepository, ReceiptConflict, RevisionConflict
from resume_core.database import make_engine, migration_config
from resume_core.persistence.unit_of_work import UnitOfWork
from sqlalchemy import event, text


@pytest.fixture
def database(tmp_path):
    engine = make_engine(tmp_path / "test.sqlite")
    command.upgrade(migration_config(engine), "head")
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES ('source','manual_note','hash','confidential')"
        )
    yield engine
    engine.dispose()


def write(
    repo,
    *,
    entity="entity",
    revision="revision",
    base=None,
    key="key",
    name="Synthetic",
    privacy="public",
    source="source",
    field=None,
):
    return repo.write(
        kind="profile",
        content=ProfileContent(full_name=name, phone_original="PRIVATE"),
        entity_id=entity,
        revision_id=revision,
        profile_id=None,
        base_revision_id=base,
        privacy=privacy,
        field_privacy={"phone_original": "secret"},
        source_id=source,
        source_sha256="hash",
        principal="test",
        request_id="request",
        operation="create" if base is None else "update",
        key=key,
        command_hash="hash",
        provenance_field=field,
    )


def test_m1_repository_atomic_rollback_after_identity(database):
    @event.listens_for(database, "before_cursor_execute")
    def fail_content(conn, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("INSERT INTO KB_PROFILES"):
            raise RuntimeError("synthetic failure")

    with pytest.raises(RuntimeError):
        with UnitOfWork(database) as uow:
            write(CareerRepository(uow.session))
    with database.connect() as c:
        for table in (
            "kb_entities",
            "kb_profiles",
            "kb_revisions",
            "kb_revision_fields",
            "kb_audit_events",
            "mutation_receipts",
        ):
            assert c.execute(text(f"SELECT count(*) FROM {table}")).scalar_one() == 0


def test_m1_repository_snapshot_selects_only_permitted_fields(database):
    with UnitOfWork(database) as uow:
        write(CareerRepository(uow.session))
    statements = []

    @event.listens_for(database, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, many):
        if "kb_revision_fields.value" in statement:
            statements.append((statement, parameters))

    with UnitOfWork(database) as uow:
        snapshot = CareerRepository(uow.session).snapshot("revision", {"full_name"})
    assert snapshot == {"full_name": "Synthetic"}
    assert len(statements) == 1 and "phone_original" not in str(statements[0][1])
    assert " IN " in statements[0][0].upper()


def test_m1_repository_stale_write_has_no_partial_history(database):
    with UnitOfWork(database) as uow:
        write(CareerRepository(uow.session))
    other_engine = make_engine(Path(database.url.database))
    try:
        with UnitOfWork(database) as uow:
            write(
                CareerRepository(uow.session),
                revision="next",
                base="revision",
                key="next",
                name="Updated",
            )
        with pytest.raises(RevisionConflict):
            with UnitOfWork(other_engine) as uow:
                write(CareerRepository(uow.session), revision="stale", base="revision", key="stale")
    finally:
        other_engine.dispose()
    with database.connect() as c:
        assert (
            c.execute(
                text("SELECT head_revision_id FROM kb_entities WHERE id='entity'")
            ).scalar_one()
            == "next"
        )
        assert (
            c.execute(
                text("SELECT full_name FROM kb_profiles WHERE entity_id='entity'")
            ).scalar_one()
            == "Updated"
        )
        assert c.execute(text("SELECT count(*) FROM kb_revisions")).scalar_one() == 2
        assert c.execute(text("SELECT count(*) FROM kb_audit_events")).scalar_one() == 2
        assert c.execute(text("SELECT count(*) FROM mutation_receipts")).scalar_one() == 2
        assert (
            c.execute(
                text("SELECT count(*) FROM kb_revision_fields WHERE revision_id='stale'")
            ).scalar_one()
            == 0
        )


def test_m1_repository_receipt_replay_and_conflict(database):
    with UnitOfWork(database) as uow:
        result = write(CareerRepository(uow.session))
    with UnitOfWork(database) as uow:
        repo = CareerRepository(uow.session)
        assert repo.receipt("test", "create", "key", "hash") == result
        with pytest.raises(ReceiptConflict):
            repo.receipt("test", "create", "key", "different")
        assert repo.receipt("test", "create", str(uuid4()), "hash") is None


def test_m1_profile_edit_preserves_only_unchanged_confirmations(database):
    with database.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,head_revision_id,privacy,created_at,updated_at) VALUES ('entity','profile','revision','public','now','now')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_profiles (entity_id,full_name,phone_original) VALUES ('entity','Old','PRIVATE')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_revisions (id,entity_id,action,responsible,created_at,privacy,confirmation) VALUES ('revision','entity','confirm','test','now','public','unverified')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_revision_fields (revision_id,field_key,value,privacy,confirmation) VALUES ('revision','full_name','\"Old\"','public','confirmed'), ('revision','phone_original','\"PRIVATE\"','secret','confirmed')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_field_metadata (entity_id,field_key,privacy,confirmation) VALUES ('entity','full_name','public','confirmed'), ('entity','phone_original','secret','confirmed')"
        )
    with UnitOfWork(database) as uow:
        write(
            CareerRepository(uow.session),
            revision="next",
            base="revision",
            key="next",
            name="Updated",
        )
    with database.connect() as c:
        states = dict(
            c.execute(
                text(
                    "SELECT field_key,confirmation FROM kb_revision_fields WHERE revision_id='next' AND field_key IN ('full_name','phone_original')"
                )
            ).all()
        )
        assert states == {"full_name": "unverified", "phone_original": "confirmed"}
        assert (
            c.execute(
                text(
                    "SELECT value FROM kb_revision_fields WHERE revision_id='revision' AND field_key='full_name'"
                )
            ).scalar_one()
            == '"Old"'
        )


def test_m1_revision_preserves_current_and_historical_field_sources(database):
    with database.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES ('source2','manual_note','hash','secret')"
        )
    with UnitOfWork(database) as uow:
        write(CareerRepository(uow.session), field="phone_original")
    with UnitOfWork(database) as uow:
        write(
            CareerRepository(uow.session),
            revision="next",
            base="revision",
            key="next",
            privacy="confidential",
            source="source2",
            field="full_name",
        )
    with database.connect() as c:
        assert (
            c.execute(text("SELECT privacy FROM kb_entities WHERE id='entity'")).scalar_one()
            == "confidential"
        )
        current = c.execute(
            text(
                "SELECT source_document_id,field_key FROM kb_provenance ORDER BY source_document_id"
            )
        ).all()
        assert current == [("source", "phone_original"), ("source2", "full_name")]
        old = c.execute(
            text(
                "SELECT source_document_id,field_key FROM kb_revision_provenance WHERE revision_id='revision'"
            )
        ).all()
        new = c.execute(
            text(
                "SELECT source_document_id,field_key FROM kb_revision_provenance WHERE revision_id='next' ORDER BY source_document_id"
            )
        ).all()
        assert old == [("source", "phone_original")]
        assert new == [("source", "phone_original"), ("source2", "full_name")]
