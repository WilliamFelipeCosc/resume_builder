"""Synthetic migration tests: history and cross-entity references are protected."""

import pytest
from alembic import command
from resume_core.career_kb.models import Entity, Revision, RevisionField
from resume_core.database import make_engine, migration_config
from resume_core.persistence.unit_of_work import UnitOfWork
from sqlalchemy.exc import IntegrityError


def setup_db(tmp_path):
    engine = make_engine(tmp_path / "foundation.sqlite3")
    config = migration_config(engine)
    with engine.begin() as c:
        c.exec_driver_sql("CREATE TABLE unrelated (value TEXT)")
        c.exec_driver_sql("INSERT INTO unrelated VALUES ('keep')")
    command.upgrade(config, "head")
    return engine, config


def add_entity_and_revision(engine):
    with UnitOfWork(engine) as work:
        work.session.add(
            Entity(
                id="entity",
                kind="profile",
                head_revision_id="revision",
                privacy="professional",
                created_at="now",
                updated_at="now",
            )
        )
        work.session.flush()
        work.session.add(
            Revision(
                id="revision",
                entity_id="entity",
                action="create",
                responsible="test",
                created_at="now",
                privacy="professional",
                confirmation="unverified",
            )
        )
        work.session.flush()
        work.session.add(
            RevisionField(
                revision_id="revision",
                field_key="full_name",
                value="Synthetic",
                privacy="professional",
            )
        )


def test_roundtrip_populated_foundation_preserves_m0_and_unrelated(tmp_path):
    engine, config = setup_db(tmp_path)
    add_entity_and_revision(engine)
    with engine.connect() as c:
        assert (
            c.exec_driver_sql("SELECT value FROM kb_revision_fields").scalar_one() == '"Synthetic"'
        )
        assert c.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    command.downgrade(config, "0001_diagnostics")
    with engine.connect() as c:
        assert c.exec_driver_sql("SELECT value FROM unrelated").scalar_one() == "keep"
        assert c.exec_driver_sql("SELECT count(*) FROM diagnostic_runs").scalar_one() == 0
    command.upgrade(config, "head")
    with engine.connect() as c:
        assert c.exec_driver_sql("PRAGMA foreign_key_check").all() == []


@pytest.mark.parametrize(
    "statement",
    [
        "UPDATE kb_revisions SET action='changed'",
        "DELETE FROM kb_revisions",
        "UPDATE kb_revision_fields SET value='changed'",
        "DELETE FROM kb_revision_fields",
        "UPDATE kb_audit_events SET action='changed'",
        "DELETE FROM kb_audit_events",
        "UPDATE mutation_receipts SET command_hash='changed'",
        "DELETE FROM mutation_receipts",
    ],
)
def test_history_and_receipts_are_immutable(tmp_path, statement):
    engine, _ = setup_db(tmp_path)
    add_entity_and_revision(engine)
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_audit_events (id,responsible,action,created_at,request_id) VALUES ('a','test','create','now','r')"
        )
        c.exec_driver_sql(
            "INSERT INTO mutation_receipts (id,principal,operation,idempotency_key,command_hash,result) VALUES ('r','test','create','key','hash','{}')"
        )
    with engine.connect() as c:
        with pytest.raises(IntegrityError, match="immutable history"):
            c.exec_driver_sql(statement)
        c.rollback()


def test_head_revision_must_belong_to_entity_and_bad_fk_fails(tmp_path):
    engine, _ = setup_db(tmp_path)
    add_entity_and_revision(engine)
    with engine.connect() as c:
        with pytest.raises(IntegrityError):
            c.exec_driver_sql(
                "INSERT INTO kb_revision_fields (revision_id,field_key,privacy) VALUES ('missing','x','public')"
            )
        c.rollback()
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,head_revision_id,privacy,created_at,updated_at) VALUES ('other','profile','revision','public','now','now')"
        )
        with pytest.raises(IntegrityError):
            c.commit()
        c.rollback()


def test_active_link_uniqueness_and_fk_check(tmp_path):
    engine, config = setup_db(tmp_path)
    add_entity_and_revision(engine)
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES ('other','skill','public','now','now')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_links (id,kind,from_entity_id,to_entity_id,privacy,revision_id) VALUES ('link','skill','entity','other','public','lr')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_link_revisions (id,link_id,kind,from_entity_id,to_entity_id,responsible,created_at,action,privacy) VALUES ('lr','link','skill','entity','other','test','now','create','public')"
        )
    with engine.connect() as c:
        with pytest.raises(IntegrityError):
            c.exec_driver_sql(
                "INSERT INTO kb_links (id,kind,from_entity_id,to_entity_id,privacy,revision_id) VALUES ('duplicate','skill','entity','other','public','lr2')"
            )
        c.rollback()
        with pytest.raises(IntegrityError, match="immutable history"):
            c.exec_driver_sql("UPDATE kb_link_revisions SET action='changed'")
        c.rollback()
        assert c.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    command.downgrade(config, "0001_diagnostics")
    command.upgrade(config, "head")
    with engine.connect() as c:
        assert c.exec_driver_sql("PRAGMA foreign_key_check").all() == []
        assert c.exec_driver_sql("SELECT value FROM unrelated").scalar_one() == "keep"


def test_model_and_migration_have_matching_columns(tmp_path):
    from resume_core.career_kb.models import Base
    from sqlalchemy import inspect

    engine, _ = setup_db(tmp_path)
    inspector = inspect(engine)
    for table in Base.metadata.tables.values():
        assert set(table.columns.keys()) == {
            column["name"] for column in inspector.get_columns(table.name)
        }


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO kb_field_metadata (entity_id,field_key,confirmation) VALUES ('entity','full_name','invalid')",
        "INSERT INTO kb_revision_fields (revision_id,field_key,privacy,confirmation) VALUES ('revision','other','public','invalid')",
        "INSERT INTO kb_revisions (id,entity_id,action,responsible,created_at,privacy,confirmation) VALUES ('r2','entity','change','test','now','public','invalid')",
    ],
)
def test_invalid_confirmation_is_rejected_by_database(tmp_path, statement):
    engine, _ = setup_db(tmp_path)
    add_entity_and_revision(engine)
    with engine.connect() as connection:
        with pytest.raises(IntegrityError):
            connection.exec_driver_sql(statement)
        connection.rollback()
