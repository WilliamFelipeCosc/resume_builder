"""Authorization precedes value access for current and historical projections."""

import pytest
from alembic import command
from resume_api.app import local_owner
from resume_core.career_kb.metadata_reader import SqlMetadataReader
from resume_core.career_kb.policy import (
    FieldPolicy,
    LinkPolicy,
    SourcePolicy,
    authorize_projection,
)
from resume_core.database import make_engine, migration_config
from resume_core.service import Clearance, PermissionDenied, Principal
from sqlalchemy import event
from sqlalchemy.orm import Session


class Reader:
    def __init__(self, entity="public", revision="public"):
        self.entity = entity
        self.revision = revision
        self.calls = []

    def entity_privacy(self, entity_id):
        self.calls.append("entity")
        return self.entity

    def revision_privacy(self, entity_id, revision_id):
        self.calls.append("revision")
        return self.revision

    def fields(self, entity_id, revision_id):
        self.calls.append("fields")
        return (FieldPolicy("private", "secret"), FieldPolicy("public", None))

    def sources(self, entity_id, revision_id):
        self.calls.append("sources")
        return (
            SourcePolicy("r1", "s1", "confidential", "public", "public"),
            SourcePolicy("r2", "s1", "public", "secret", "public"),
        )

    def links(self, entity_id):
        self.calls.append("links")
        return (
            LinkPolicy("l1", "public", "public", "professional", None),
            LinkPolicy("l2", "secret", "public", "public", None),
        )


def principal(clearance):
    return Principal("test", frozenset({"career:read", "source:read"}), clearance)


FIELDS = frozenset({"public", "private"})


def test_no_capability_means_no_metadata_or_values_read():
    reader = Reader()
    with pytest.raises(PermissionDenied):
        authorize_projection(reader, Principal("restricted", frozenset()), "id", FIELDS)
    assert reader.calls == []


@pytest.mark.parametrize("entity", ["public", "professional", "confidential", "secret"])
def test_every_clearance_respects_entity_classification(entity):
    level = Clearance.parse(entity)
    assert authorize_projection(Reader(entity), principal(level), "id", FIELDS) is not None
    if level > Clearance.PUBLIC:
        assert (
            authorize_projection(Reader(entity), principal(Clearance(level - 1)), "id", FIELDS)
            is None
        )


def test_fields_sources_links_use_most_restrictive_metadata():
    reader = Reader()
    projection = authorize_projection(reader, principal(Clearance.CONFIDENTIAL), "id", FIELDS)
    assert projection.fields == {"public"}
    assert projection.restricted_fields == {"private"}
    assert projection.source_references == {("r1", "s1")}
    assert projection.link_ids == {"l1"}
    no_source = Reader()
    result = authorize_projection(
        no_source, Principal("test", frozenset({"career:read"}), Clearance.SECRET), "id", FIELDS
    )
    assert result.source_references == set()
    assert "sources" not in no_source.calls


def test_hidden_and_absent_entities_or_revisions_return_same_result():
    assert authorize_projection(Reader(None), principal(Clearance.PUBLIC), "id", FIELDS) is None
    assert authorize_projection(Reader("secret"), principal(Clearance.PUBLIC), "id", FIELDS) is None
    assert (
        authorize_projection(
            Reader(revision=None), principal(Clearance.PUBLIC), "id", FIELDS, revision_id="r"
        )
        is None
    )
    assert (
        authorize_projection(
            Reader(revision="secret"), principal(Clearance.PUBLIC), "id", FIELDS, revision_id="r"
        )
        is None
    )


def test_real_sql_metadata_projections_never_select_values_or_excerpts(tmp_path):
    engine = make_engine(tmp_path / "policy.sqlite3")
    command.upgrade(migration_config(engine), "head")
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,head_revision_id,privacy,created_at,updated_at) VALUES ('e','profile','r','public','now','now')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_revisions (id,entity_id,action,responsible,created_at,privacy,confirmation) VALUES ('r','e','create','test','now','public','unverified')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_field_metadata (entity_id,field_key,privacy) VALUES ('e','private','secret')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_revision_fields (revision_id,field_key,value,privacy) VALUES ('r','private','SECRET_VALUE','secret')"
        )
        c.exec_driver_sql(
            "INSERT INTO source_documents (id,kind,sha256,private_name,privacy) VALUES ('s','file','hash','SECRET_FILENAME','secret')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_provenance (id,entity_id,source_document_id,source_sha256,excerpt,privacy) VALUES ('p','e','s','hash','SECRET_EXCERPT','public')"
        )
        c.exec_driver_sql(
            "INSERT INTO kb_revision_provenance (id,revision_id,source_document_id,source_sha256,excerpt,privacy) VALUES ('hp','r','s','hash','SECRET_EXCERPT','public')"
        )
    statements = []

    @event.listens_for(engine, "before_cursor_execute")
    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement.lower())

    with Session(engine) as session:
        reader = SqlMetadataReader(session)
        current = authorize_projection(reader, principal(Clearance.PUBLIC), "e", FIELDS)
        history = authorize_projection(
            reader, principal(Clearance.PUBLIC), "e", FIELDS, revision_id="r"
        )
    assert current.fields == {"public"} and current.source_references == set()
    assert history.fields == {"public"} and history.source_references == set()
    sql = " ".join(statements)
    assert "revision_fields.value" not in sql
    assert "excerpt" not in sql and "private_name" not in sql


def test_clearance_is_principal_bound_and_cannot_be_supplied_separately():
    public_principal = Principal("test", frozenset({"career:read"}))
    assert public_principal.clearance is Clearance.PUBLIC
    assert local_owner().clearance is Clearance.SECRET
    assert authorize_projection(Reader("secret"), public_principal, "id", FIELDS) is None
    with pytest.raises(TypeError):
        authorize_projection(
            Reader("secret"), public_principal, "id", FIELDS, clearance=Clearance.SECRET
        )
