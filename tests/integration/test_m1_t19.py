import pytest
from alembic import command
from resume_core.career_kb.entity_models import ENTITY_MODELS
from resume_core.database import make_engine, migration_config
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def database(tmp_path):
    engine = make_engine(tmp_path / "migration.sqlite")
    config = migration_config(engine)
    command.upgrade(config, "head")
    yield engine, config
    engine.dispose()


def test_m1_nine_typed_entities_persist_and_match_mapping(database):
    engine, _ = database
    rows = [
        ("profile", "kb_profiles", "full_name", "synthetic"),
        (
            "experience",
            "kb_experiences",
            "company_name_original,job_title_original",
            "synthetic,engineer",
        ),
        ("statement", "kb_statements", "text_original", "synthetic"),
        ("project", "kb_projects", "title", "synthetic"),
        ("achievement", "kb_achievements", "text_original", "synthetic"),
        ("skill", "kb_skills", "name,original_labels", "synthetic,[]"),
        ("education", "kb_education", "institution,program_original", "synthetic,course"),
        ("language", "kb_languages", "language,proficiency_original", "synthetic,basic"),
        (
            "evidence",
            "kb_evidence",
            "description,evidence_kind,source_document_id",
            "synthetic,manual_note,source",
        ),
    ]
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES ('source','manual_note','hash','confidential')"
        )
        for kind, table, columns, values in rows:
            c.exec_driver_sql(
                "INSERT INTO kb_entities (id,kind,profile_id,privacy,created_at,updated_at) VALUES (?,?,?,'public','now','now')",
                (kind, kind, None if kind == "profile" else "profile"),
            )
            parts = values.split(",")
            placeholders = ",".join("?" for _ in parts)
            c.exec_driver_sql(
                f"INSERT INTO {table} (entity_id,{columns}) VALUES (?,{placeholders})",
                (kind, *parts),
            )
        for kind, table, columns, values in rows:
            actual = c.exec_driver_sql(
                f"SELECT {columns} FROM {table} WHERE entity_id=?", (kind,)
            ).one()
            assert tuple(actual) == tuple(values.split(","))
        assert c.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    inspector = inspect(engine)
    for model in ENTITY_MODELS.values():
        assert set(model.__table__.columns.keys()) == {
            col["name"] for col in inspector.get_columns(model.__table__.name)
        }


def test_m1_wrong_kind_missing_profile_and_orphan_content_rejected(database):
    engine, _ = database
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES ('p','profile','public','now','now')"
        )
        for sql in (
            "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES ('s','skill','public','now','now')",
            "INSERT INTO kb_entities (id,kind,profile_id,privacy,created_at,updated_at) VALUES ('s','skill','missing','public','now','now')",
            "INSERT INTO kb_skills (entity_id,name,original_labels) VALUES ('p','synthetic','[]')",
            "INSERT INTO kb_profiles (entity_id,full_name) VALUES ('missing','synthetic')",
        ):
            with pytest.raises(IntegrityError):
                c.exec_driver_sql(sql)
        assert c.exec_driver_sql("SELECT count(*) FROM kb_skills").scalar_one() == 0


def test_m1_populated_downgrade_preserves_foundation_and_m0(database):
    engine, config = database
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,head_revision_id,privacy,created_at,updated_at) VALUES ('p','profile','r','public','now','now')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_revisions (id,entity_id,action,responsible,created_at,privacy,confirmation) VALUES ('r','p','create','test','now','public','unverified')"
        )
        c.exec_driver_sql("INSERT INTO kb_profiles (entity_id,full_name) VALUES ('p','synthetic')")
    command.downgrade(config, "0002_kb_foundation")
    with engine.connect() as c:
        assert (
            c.exec_driver_sql("SELECT head_revision_id FROM kb_entities WHERE id='p'").scalar_one()
            == "r"
        )
        assert (
            c.exec_driver_sql("SELECT confirmation FROM kb_revisions WHERE id='r'").scalar_one()
            == "unverified"
        )
        assert c.exec_driver_sql("SELECT count(*) FROM diagnostic_runs").scalar_one() == 0
        assert c.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    command.upgrade(config, "head")
    with engine.connect() as c:
        assert (
            c.exec_driver_sql("SELECT head_revision_id FROM kb_entities WHERE id='p'").scalar_one()
            == "r"
        )


def test_m1_typed_content_database_constraints_reject_invalid_values(database):
    engine, _ = database
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES ('source','file','hash','public')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES ('p','profile','public','now','now')"
        )
        for entity, kind in (("s", "statement"), ("e", "evidence"), ("k", "skill")):
            c.exec_driver_sql(
                "INSERT INTO kb_entities (id,kind,profile_id,privacy,created_at,updated_at) VALUES (?,?,'p','public','now','now')",
                (entity, kind),
            )
        cases = [
            ("INSERT INTO kb_profiles (entity_id,full_name) VALUES ('p',?)", ("x" * 257,)),
            ("INSERT INTO kb_profiles (entity_id,full_name) VALUES ('p',?)", ("",)),
            (
                "INSERT INTO kb_statements (entity_id,text_original,statement_type) VALUES ('s',?,'invalid')",
                ("synthetic",),
            ),
            ("INSERT INTO kb_statements (entity_id,text_original) VALUES ('s',?)", ("x" * 8001,)),
            (
                "INSERT INTO kb_skills (entity_id,name,original_labels,explicitly_listed_in_skills_section) VALUES ('k','synthetic','[]',2)",
                (),
            ),
            (
                "INSERT INTO kb_evidence (entity_id,description,evidence_kind,source_document_id) VALUES ('e','synthetic','invalid','source')",
                (),
            ),
            (
                "INSERT INTO kb_evidence (entity_id,description,evidence_kind,source_document_id,page) VALUES ('e','synthetic','documentary','source',0)",
                (),
            ),
        ]
        for sql, params in cases:
            with pytest.raises(IntegrityError):
                c.exec_driver_sql(sql, params)
        assert c.exec_driver_sql("SELECT count(*) FROM kb_evidence").scalar_one() == 0
        assert c.exec_driver_sql("SELECT count(*) FROM kb_statements").scalar_one() == 0
    inspector = inspect(engine)
    for model in ENTITY_MODELS.values():
        expected = {
            constraint.name
            for constraint in model.__table__.constraints
            if constraint.name and constraint.name.startswith("ck_")
        }
        actual = {
            constraint["name"]
            for constraint in inspector.get_check_constraints(model.__table__.name)
        }
        assert actual == expected
