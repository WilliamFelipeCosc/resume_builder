"""SPIKE-04/07/11: isolated, reversible migration of the synthetic store."""

import pytest
from alembic import command
from resume_core.mcp_spike.database import make_engine
from resume_mcp_server.migration import is_current, migration_config
from sqlalchemy import inspect


@pytest.fixture
def engine(tmp_path):
    engine = make_engine(tmp_path / "mcp-spike.sqlite3")
    yield engine
    engine.dispose()


def test_unmigrated_store_is_not_current(engine):
    assert is_current(engine) is False
    assert "mcp_spike_reports" not in inspect(engine).get_table_names()


def test_upgrade_creates_report_table_and_marks_current(engine):
    command.upgrade(migration_config(engine), "head")
    assert is_current(engine) is True
    assert "mcp_spike_reports" in inspect(engine).get_table_names()
    columns = inspect(engine).get_columns("mcp_spike_reports")
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
    assert all(not column["nullable"] for column in columns)
    inspector = inspect(engine)
    assert inspector.get_pk_constraint("mcp_spike_reports")["constrained_columns"] == ["receipt_id"]
    unique = inspector.get_unique_constraints("mcp_spike_reports")
    assert [item["column_names"] for item in unique] == [
        ["client_id", "application_id", "execution_id", "idempotency_key"]
    ]
    checks = {item["sqltext"] for item in inspector.get_check_constraints("mcp_spike_reports")}
    assert checks == {
        "event IN ('started', 'form_filled', 'blocked')",
        "confirmation_state = 'reported_by_agent'",
    }


def test_upgrade_downgrade_upgrade_preserves_unrelated_data(engine):
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE unrelated (value TEXT NOT NULL)")
        connection.exec_driver_sql("INSERT INTO unrelated VALUES ('preserve')")
    cfg = migration_config(engine)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    assert is_current(engine) is False
    assert "mcp_spike_reports" not in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT value FROM unrelated").scalar_one() == "preserve"
    command.upgrade(cfg, "head")
    assert is_current(engine) is True
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT value FROM unrelated").scalar_one() == "preserve"


def test_unknown_revision_is_not_current(engine):
    command.upgrade(migration_config(engine), "head")
    with engine.begin() as connection:
        connection.exec_driver_sql("UPDATE alembic_version SET version_num='old-schema'")
    assert is_current(engine) is False


def test_does_not_touch_m0_history(engine, tmp_path):
    other = tmp_path / "diagnostics.sqlite3"
    other.write_bytes(b"m0-sentinel")
    command.upgrade(migration_config(engine), "head")
    assert other.read_bytes() == b"m0-sentinel"
