"""FND-06/19/22: real temporary SQLite migration and invariant enforcement."""

from uuid import uuid4

import pytest
from alembic import command
from resume_core.database import diagnostic_runs, make_engine, migration_config
from sqlalchemy import insert, inspect, select
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def engine(tmp_path):
    engine = make_engine(tmp_path / "diagnostics.sqlite3")
    command.upgrade(migration_config(engine), "head")
    yield engine
    engine.dispose()


def row(**changes):
    return (
        dict(
            id=str(uuid4()),
            request_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            status="pending",
            attempt_count=0,
            created_at=1_000_000,
            updated_at=1_000_000,
            result=None,
            error=None,
            delivery_warning=None,
            lease_token=None,
            lease_expires_at=None,
            next_delivery_at=1_000_000,
        )
        | changes
    )


def test_upgrade_downgrade_upgrade_preserves_unrelated_table(tmp_path):
    engine = make_engine(tmp_path / "migration.sqlite3")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE unrelated (value TEXT)")
    cfg = migration_config(engine)
    command.upgrade(cfg, "head")
    with engine.begin() as connection:
        connection.execute(insert(diagnostic_runs).values(row()))
        assert connection.execute(select(diagnostic_runs.c.status)).scalar_one() == "pending"
    command.downgrade(cfg, "base")
    assert inspect(engine).get_table_names() == ["alembic_version", "unrelated"]
    command.upgrade(cfg, "head")
    assert "diagnostic_runs" in inspect(engine).get_table_names()
    engine.dispose()


def test_key_unique_even_for_terminal_runs(engine):
    key = str(uuid4())
    with engine.begin() as connection:
        connection.execute(
            insert(diagnostic_runs).values(
                row(
                    idempotency_key=key,
                    status="succeeded",
                    result={"message": "diagnostic_completed", "fixtureVersion": "m0-v1"},
                )
            )
        )
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(insert(diagnostic_runs).values(row(idempotency_key=key)))


def test_only_one_active_run(engine):
    with engine.begin() as connection:
        connection.execute(insert(diagnostic_runs).values(row()))
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(insert(diagnostic_runs).values(row(status="queued")))


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "unknown"},
        {"attempt_count": -1},
        {"attempt_count": 4},
        {"status": "succeeded"},
        {"status": "failed"},
        {"result": {"message": "diagnostic_completed", "fixtureVersion": "m0-v1"}},
        {"status": "succeeded", "result": {"message": "invented", "fixtureVersion": "m0-v1"}},
        {"status": "failed", "error": {"code": "secret", "message": "raw exception"}},
        {"status": "running"},
    ],
)
def test_reject_inconsistent_states(engine, changes):
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(insert(diagnostic_runs).values(row(**changes)))


def test_engine_uses_wal_and_bounded_wait(engine):
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA journal_mode").scalar_one() == "wal"
        assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == 250


@pytest.mark.parametrize(
    "changes",
    [
        {"status": "succeeded", "result": {}},
        {"status": "failed", "error": {}},
        {"delivery_warning": {}},
        {"delivery_warning": {"code": "queue_unavailable", "message": "raw secret"}},
    ],
)
def test_missing_or_unsanitized_payload_fields_are_rejected(engine, changes):
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(insert(diagnostic_runs).values(row(**changes)))
