from uuid import uuid4

import pytest
from alembic import command
from pydantic import ValidationError
from resume_core.career_kb.contracts import CREATE_TYPES
from resume_core.career_kb.create import CareerCreateService
from resume_core.career_kb.queries import CareerQueries, ListQuery, ResponseTooLarge
from resume_core.database import make_engine, migration_config
from resume_core.service import Clearance, PermissionDenied, Principal
from sqlalchemy import event, text


@pytest.fixture
def setup(tmp_path):
    engine = make_engine(tmp_path / "query.sqlite")
    command.upgrade(migration_config(engine), "head")
    source = str(uuid4())
    with engine.begin() as c:
        c.execute(
            text(
                "INSERT INTO source_documents (id,kind,sha256,privacy) VALUES (:id,'manual_note','hash','confidential')"
            ),
            {"id": source},
        )
    owner = Principal(
        "owner", frozenset({"career:read", "career:write", "source:read"}), Clearance.SECRET
    )
    yield engine, CareerCreateService(engine), CareerQueries(engine), owner, source
    engine.dispose()


def create(service, owner, source, kind, content, profile=None, **options):
    command = CREATE_TYPES[kind].model_validate(
        {
            "content": content,
            "sourceDocumentId": source,
            "profileId": profile,
            "idempotencyKey": str(uuid4()),
            **options,
        }
    )
    return service.create(owner, kind, command, request_id="test")[0]["id"]


def test_m1_detail_filters_multiword_field_before_sql_and_distinguishes_null(setup):
    engine, service, queries, owner, source = setup
    entity_id = create(
        service,
        owner,
        source,
        "profile",
        {"fullName": "Synthetic", "phoneOriginal": "PRIVATE"},
        privacy="public",
        fieldPrivacy={"phoneOriginal": "secret"},
    )
    statements = []

    @event.listens_for(engine, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, many):
        statements.append(statement.lower())

    reader = Principal("reader", frozenset({"career:read"}), Clearance.PUBLIC)
    item = queries.detail(reader, "profile", entity_id)
    assert item.content.full_name == "Synthetic" and item.content.phone_original is None
    assert item.content.email is None and item.restricted_fields == ["phoneOriginal"]
    assert "phoneOriginal" not in item.field_confirmations
    values_sql = [sql for sql in statements if "from kb_profiles" in sql and "full_name" in sql]
    assert values_sql and all("phone_original" not in sql for sql in values_sql)
    assert queries.detail(reader, "profile", str(uuid4())) is None


def test_m1_evidence_source_fields_follow_current_source_privacy_and_capability(setup):
    engine, service, queries, owner, source = setup
    profile = create(service, owner, source, "profile", {"fullName": "Synthetic"})
    evidence = create(
        service,
        owner,
        source,
        "evidence",
        {
            "description": "Synthetic",
            "evidenceKind": "manual_note",
            "sourceDocumentId": source,
            "excerpt": "PRIVATE",
        },
        profile,
        privacy="public",
    )
    with engine.begin() as c:
        c.execute(text("UPDATE source_documents SET privacy='secret' WHERE id=:id"), {"id": source})
    reader = Principal("reader", frozenset({"career:read", "source:read"}), Clearance.CONFIDENTIAL)
    captured = []

    @event.listens_for(engine, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, many):
        captured.append(statement.lower())

    item = queries.detail(reader, "evidence", evidence)
    assert item.content.description == "Synthetic"
    assert (
        item.content.source_document_id is None
        and item.content.page is None
        and item.content.excerpt is None
    )
    assert set(item.restricted_fields) == {"sourceDocumentId", "page", "excerpt"}
    values_sql = [sql for sql in captured if "from kb_evidence" in sql and "description" in sql]
    assert values_sql and all(
        "source_document_id" not in sql and "excerpt" not in sql for sql in values_sql
    )
    no_source = Principal("reader", frozenset({"career:read"}), Clearance.SECRET)
    assert set(queries.detail(no_source, "evidence", evidence).restricted_fields) == {
        "sourceDocumentId",
        "page",
        "excerpt",
    }
    assert queries.detail(owner, "evidence", evidence).content.excerpt == "PRIVATE"


def test_m1_list_pagination_visible_total_order_and_incomplete_exclusion(setup):
    engine, service, queries, owner, source = setup
    for number in range(3):
        create(
            service, owner, source, "profile", {"fullName": f"Synthetic {number}"}, privacy="public"
        )
    create(service, owner, source, "profile", {"fullName": "SECRET"}, privacy="secret")
    with engine.begin() as c:
        c.exec_driver_sql(
            "INSERT INTO kb_entities (id,kind,privacy,created_at,updated_at) VALUES ('incomplete','profile','public','now','now')"
        )
    reader = Principal("reader", frozenset({"career:read"}), Clearance.PUBLIC)
    page = queries.list(reader, "profile", ListQuery(limit=2))
    next_page = queries.list(reader, "profile", ListQuery(limit=2, offset=2))
    assert page.total == next_page.total == 3
    assert (
        page.limit == 2 and page.offset == 0 and len(page.items) == 2 and len(next_page.items) == 1
    )
    assert {str(x.id) for x in page.items}.isdisjoint({str(x.id) for x in next_page.items})
    assert queries.detail(reader, "profile", "incomplete") is None
    assert ListQuery().limit == 25 and ListQuery(offset=10000, limit=100).limit == 100
    for invalid in ({"limit": 101}, {"offset": 10001}, {"sort": "arbitrary"}):
        with pytest.raises(ValidationError):
            ListQuery(**invalid)


def test_m1_list_filters_archive_and_confirmation_and_orders_stably(setup):
    engine, service, queries, owner, source = setup
    profile = create(service, owner, source, "profile", {"fullName": "Synthetic"})
    first = create(service, owner, source, "skill", {"name": "First"}, profile)
    second = create(service, owner, source, "skill", {"name": "Second"}, profile)
    with engine.begin() as c:
        c.execute(
            text("UPDATE kb_entities SET created_at='same' WHERE id IN (:a,:b)"),
            {"a": first, "b": second},
        )
        c.execute(text("UPDATE kb_entities SET archived_at='now' WHERE id=:id"), {"id": second})
    all_items = queries.list(owner, "skill", ListQuery())
    assert [str(item.id) for item in all_items.items] == sorted([first, second])
    assert [
        str(item.id) for item in queries.list(owner, "skill", ListQuery(sort="-createdAt")).items
    ] == sorted([first, second], reverse=True)
    assert [
        str(item.id) for item in queries.list(owner, "skill", ListQuery(archived=True)).items
    ] == [second]
    assert (
        queries.list(owner, "skill", ListQuery(archived=False, confirmation="unverified")).total
        == 1
    )
    assert queries.list(owner, "skill", ListQuery(confirmation="confirmed")).total == 0


def test_m1_profile_confirmation_filter_requires_visible_explicit_field(setup):
    engine, service, queries, owner, source = setup
    visible = create(
        service,
        owner,
        source,
        "profile",
        {"fullName": "Visible", "phoneOriginal": "123"},
        privacy="public",
    )
    hidden = create(
        service,
        owner,
        source,
        "profile",
        {"fullName": "Hidden", "phoneOriginal": "PRIVATE"},
        privacy="public",
        fieldPrivacy={"phoneOriginal": "secret"},
    )
    with engine.begin() as c:
        c.execute(
            text(
                "UPDATE kb_field_metadata SET confirmation='confirmed' WHERE field_key='phone_original' AND entity_id IN (:a,:b)"
            ),
            {"a": visible, "b": hidden},
        )
    statements = []

    @event.listens_for(engine, "before_cursor_execute")
    def capture(conn, cursor, statement, parameters, context, many):
        statements.append(statement.lower())

    reader = Principal("reader", frozenset({"career:read"}), Clearance.PUBLIC)
    query = ListQuery(confirmation="confirmed", confirmationField="phoneOriginal")
    page = queries.list(reader, "profile", query)
    assert page.total == 1 and [str(item.id) for item in page.items] == [visible]
    assert queries.list(owner, "profile", query).total == 2
    count_sql = [sql for sql in statements if "count(" in sql]
    assert count_sql and all("kb_field_metadata.privacy" in sql for sql in count_sql)
    with pytest.raises(ValueError):
        queries.list(reader, "profile", ListQuery(confirmation="confirmed"))
    with pytest.raises(ValueError):
        queries.list(reader, "skill", query)
    with pytest.raises(ValidationError):
        ListQuery(confirmationField="phoneOriginal")
    with pytest.raises(ValidationError):
        ListQuery(confirmation="confirmed", confirmationField="unknown")


def test_m1_response_budget_rejects_instead_of_truncation(setup):
    _, service, queries, owner, source = setup
    profile = create(service, owner, source, "profile", {"fullName": "Synthetic"})
    for number in range(34):
        create(
            service,
            owner,
            source,
            "achievement",
            {
                "textOriginal": "a" * 8000,
                "textCurrent": "b" * 8000,
                "metricValue": "c" * 8000,
                "metricMeaning": "d" * 8000,
            },
            profile,
        )
    with pytest.raises(ResponseTooLarge):
        queries.list(owner, "achievement", ListQuery(limit=100))
    page = queries.list(owner, "achievement", ListQuery(limit=1))
    assert len(page.items[0].content.text_original) == 8000 and page.total == 34


def test_m1_query_denies_before_database():
    class Forbidden:
        def __getattribute__(self, name):
            raise AssertionError("unauthorized access")

    queries = CareerQueries(Forbidden())
    principal = Principal("test", frozenset())
    with pytest.raises(PermissionDenied):
        queries.detail(principal, "profile", str(uuid4()))
    with pytest.raises(PermissionDenied):
        queries.list(principal, "profile", ListQuery())
