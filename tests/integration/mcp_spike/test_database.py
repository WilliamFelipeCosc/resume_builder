import os
import subprocess
import sys

import pytest
from resume_core.mcp_spike.database import make_engine, metadata, reports
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def engine(tmp_path):
    engine = make_engine(tmp_path / "mcp-spike.sqlite3")
    metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def record():
    return dict(
        receipt_id="r1",
        client_id="codex",
        application_id="app-demo",
        execution_id="run-1",
        idempotency_key="key-1",
        event="started",
        confirmation_state="reported_by_agent",
        created_at="2026-11-12T00:00:00Z",
    )


def test_exact_schema_isolated(engine):
    inspector = inspect(engine)
    assert inspector.get_table_names() == ["mcp_spike_reports"]
    columns = inspector.get_columns("mcp_spike_reports")
    assert {column["name"] for column in columns} == {
        "receipt_id",
        "client_id",
        "application_id",
        "execution_id",
        "idempotency_key",
        "event",
        "confirmation_state",
        "created_at",
    }
    assert all(str(column["type"]) == "TEXT" and not column["nullable"] for column in columns)
    assert inspector.get_pk_constraint("mcp_spike_reports")["constrained_columns"] == ["receipt_id"]


def test_wal_and_lock_timeout(engine):
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"
        assert connection.execute(text("PRAGMA busy_timeout")).scalar_one() == 250


def test_diagnostic_database_name_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        make_engine(tmp_path / "diagnostic.sqlite3")
    assert list(tmp_path.iterdir()) == []


def test_insert_synthetic_report(engine, record):
    with engine.begin() as connection:
        connection.execute(reports.insert().values(**record))
        assert dict(connection.execute(reports.select()).mappings().one()) == record


@pytest.mark.parametrize(
    "column",
    [
        "receipt_id",
        "client_id",
        "application_id",
        "execution_id",
        "idempotency_key",
        "event",
        "confirmation_state",
        "created_at",
    ],
)
def test_required_columns_reject_null(engine, record, column):
    record[column] = None
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(reports.insert().values(**record))


@pytest.mark.parametrize(
    "column,value", [("event", "submitted"), ("confirmation_state", "confirmed")]
)
def test_unapproved_states_rejected(engine, record, column, value):
    record[column] = value
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(reports.insert().values(**record))


def test_idempotency_constraint(engine, record):
    with engine.begin() as connection:
        connection.execute(reports.insert().values(**record))
    record["receipt_id"] = "r2"
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(reports.insert().values(**record))


def test_same_key_in_different_client_scope_is_allowed(engine, record):
    with engine.begin() as connection:
        connection.execute(reports.insert().values(**record))
        record.update(receipt_id="r2", client_id="hermes")
        connection.execute(reports.insert().values(**record))
        assert len(connection.execute(reports.select()).all()) == 2


def test_import_does_not_create_files_or_output(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", "import resume_core.mcp_spike.database"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""
    assert result.stderr == ""
    assert list(tmp_path.iterdir()) == []
