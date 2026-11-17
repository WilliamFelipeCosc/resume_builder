from uuid import uuid4

import pytest
from alembic import command
from resume_core.career_kb.contracts import CREATE_TYPES
from resume_core.career_kb.create import CareerCreateService, InvalidEvidence, ReferenceNotFound
from resume_core.career_kb.repository import ReceiptConflict
from resume_core.database import make_engine, migration_config
from resume_core.service import Clearance, PermissionDenied, Principal
from sqlalchemy import text

SAMPLES = {
    "profile": {"fullName": "Synthetic Person"},
    "experience": {"companyNameOriginal": "Synthetic Co", "jobTitleOriginal": "Engineer"},
    "statement": {"textOriginal": "Synthetic statement"},
    "project": {"title": "Synthetic project"},
    "achievement": {"textOriginal": "Synthetic achievement"},
    "skill": {"name": "Synthetic skill"},
    "education": {"institution": "Synthetic school", "programOriginal": "Course"},
    "language": {"language": "Synthetic language", "proficiencyOriginal": "basic"},
    "evidence": {"description": "Synthetic note", "evidenceKind": "manual_note"},
}


@pytest.fixture
def setup(tmp_path):
    engine = make_engine(tmp_path / "create.sqlite")
    command.upgrade(migration_config(engine), "head")
    source = str(uuid4())
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES (:id,'manual_note','hash','confidential')"
            ),
            {"id": source},
        )
    principal = Principal("test", frozenset({"career:write", "source:read"}), Clearance.SECRET)
    yield engine, CareerCreateService(engine), principal, source
    engine.dispose()


def make_command(kind, source, profile=None, **changes):
    content = dict(SAMPLES[kind])
    if kind == "evidence":
        content["sourceDocumentId"] = source
    payload = {
        "content": content,
        "sourceDocumentId": source,
        "profileId": profile,
        "idempotencyKey": str(uuid4()),
    } | changes
    return CREATE_TYPES[kind].model_validate(payload)


@pytest.mark.parametrize("kind", SAMPLES)
def test_m1_create_all_types_are_unverified_with_source(setup, kind):
    engine, service, principal, source = setup
    profile, _ = service.create(
        principal, "profile", make_command("profile", source), request_id="test"
    )
    command = make_command(kind, source, None if kind == "profile" else profile["id"])
    result, created = service.create(principal, kind, command, request_id="test")
    assert created is True
    with engine.connect() as c:
        row = c.execute(
            text(
                "SELECT e.kind,e.privacy,r.confirmation FROM kb_entities e JOIN kb_revisions r ON r.id=e.head_revision_id WHERE e.id=:id"
            ),
            {"id": result["id"]},
        ).one()
        assert tuple(row) == (kind, "confidential", "unverified")
        assert (
            c.execute(
                text("SELECT source_document_id FROM kb_provenance WHERE entity_id=:id LIMIT 1"),
                {"id": result["id"]},
            ).scalar_one()
            == source
        )
        assert (
            c.execute(
                text(
                    "SELECT count(*) FROM kb_revision_fields WHERE revision_id=:id AND confirmation='confirmed'"
                ),
                {"id": result["revisionId"]},
            ).scalar_one()
            == 0
        )


def test_m1_create_replay_conflict_and_alias_privacy(setup):
    engine, service, principal, source = setup
    cmd = make_command(
        "profile",
        source,
        content={"fullName": "Synthetic", "phoneOriginal": "PRIVATE"},
        fieldPrivacy={"phoneOriginal": "secret"},
    )
    first, created = service.create(principal, "profile", cmd, request_id="test")
    assert created and service.create(principal, "profile", cmd, request_id="test") == (
        first,
        False,
    )
    changed = cmd.model_copy(
        update={"content": cmd.content.model_copy(update={"full_name": "Changed"})}
    )
    with pytest.raises(ReceiptConflict):
        service.create(principal, "profile", changed, request_id="test")
    with engine.connect() as c:
        assert (
            c.execute(
                text(
                    "SELECT privacy FROM kb_field_metadata WHERE entity_id=:id AND field_key='phone_original'"
                ),
                {"id": first["id"]},
            ).scalar_one()
            == "secret"
        )
        assert c.execute(text("SELECT count(*) FROM kb_entities")).scalar_one() == 1


def test_m1_create_denial_precedes_database():
    class Forbidden:
        def __getattribute__(self, name):
            raise AssertionError("unauthorized access")

    service = CareerCreateService(Forbidden())
    cmd = make_command("profile", str(uuid4()))
    for principal in (
        Principal("test", frozenset()),
        Principal("test", frozenset({"career:write"}), Clearance.SECRET),
    ):
        with pytest.raises(PermissionDenied):
            service.create(principal, "profile", cmd, request_id="test")


def test_m1_create_rejects_inaccessible_source_and_incomplete_profile(setup):
    engine, service, principal, source = setup
    with pytest.raises(ReferenceNotFound):
        service.create(
            principal, "profile", make_command("profile", str(uuid4())), request_id="test"
        )
    incomplete = str(uuid4())
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES (:id,'profile','public','now','now')"
            ),
            {"id": incomplete},
        )
    with pytest.raises(ReferenceNotFound):
        service.create(
            principal, "skill", make_command("skill", source, incomplete), request_id="test"
        )


def test_m1_archived_profile_preserves_its_identity_for_references(setup):
    engine, service, principal, source = setup
    profile, _ = service.create(
        principal, "profile", make_command("profile", source), request_id="test"
    )
    with engine.begin() as c:
        c.execute(
            text("UPDATE kb_entities SET archived_at='now' WHERE id=:id"), {"id": profile["id"]}
        )
    result, created = service.create(
        principal, "skill", make_command("skill", source, profile["id"]), request_id="test"
    )
    assert created
    with engine.connect() as c:
        assert (
            c.execute(
                text("SELECT profile_id FROM kb_entities WHERE id=:id"), {"id": result["id"]}
            ).scalar_one()
            == profile["id"]
        )


def test_m1_evidence_source_privacy_kind_and_page(setup):
    engine, service, principal, source = setup
    profile, _ = service.create(
        principal, "profile", make_command("profile", source), request_id="test"
    )
    cmd = make_command(
        "evidence",
        source,
        profile["id"],
        privacy="public",
        content={
            "description": "Synthetic",
            "evidenceKind": "manual_note",
            "sourceDocumentId": source,
            "excerpt": "PRIVATE",
        },
    )
    result, _ = service.create(principal, "evidence", cmd, request_id="test")
    with engine.connect() as c:
        rows = c.execute(
            text(
                "SELECT field_key,privacy FROM kb_field_metadata WHERE entity_id=:id AND field_key IN ('source_document_id','page','excerpt')"
            ),
            {"id": result["id"]},
        ).all()
        assert dict(rows) == {
            "source_document_id": "confidential",
            "page": "confidential",
            "excerpt": "confidential",
        }
        assert (
            c.execute(
                text(
                    "SELECT excerpt FROM kb_revision_provenance WHERE revision_id=:id AND field_key='excerpt'"
                ),
                {"id": result["revisionId"]},
            ).scalar_one()
            == "PRIVATE"
        )
    for change in ({"evidence_kind": "documentary"}, {"page": 1}):
        invalid = cmd.model_copy(
            update={"idempotency_key": uuid4(), "content": cmd.content.model_copy(update=change)}
        )
        with pytest.raises(InvalidEvidence):
            service.create(principal, "evidence", invalid, request_id="test")


def test_m1_evidence_checks_second_source_and_actual_page_count(setup):
    engine, service, principal, source = setup
    pdf_id = str(uuid4())
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO source_documents (id,kind,sha256,privacy,page_count) VALUES (:id,'file','pdfhash','secret',2)"
            ),
            {"id": pdf_id},
        )
    profile, _ = service.create(
        principal, "profile", make_command("profile", source), request_id="test"
    )
    payload = {
        "description": "Synthetic",
        "evidenceKind": "documentary",
        "sourceDocumentId": pdf_id,
        "page": 2,
        "excerpt": "synthetic excerpt",
    }
    cmd = make_command("evidence", source, profile["id"], content=payload)
    result, _ = service.create(principal, "evidence", cmd, request_id="test")
    with engine.connect() as c:
        row = c.execute(
            text(
                "SELECT source_document_id,page,excerpt,privacy FROM kb_revision_provenance WHERE revision_id=:id AND field_key='excerpt'"
            ),
            {"id": result["revisionId"]},
        ).one()
        assert tuple(row) == (pdf_id, 2, "synthetic excerpt", "secret")
    invalid = cmd.model_copy(
        update={"idempotency_key": uuid4(), "content": cmd.content.model_copy(update={"page": 3})}
    )
    with pytest.raises(InvalidEvidence):
        service.create(principal, "evidence", invalid, request_id="test")
    restricted = Principal("test", principal.capabilities, Clearance.CONFIDENTIAL)
    with pytest.raises(ReferenceNotFound):
        service.create(restricted, "evidence", cmd, request_id="test")
