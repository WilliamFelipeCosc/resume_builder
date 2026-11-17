"""Foreign key enforcement is enabled on every application and migration connection."""

import pytest
from alembic import command
from resume_core.database import make_engine, migration_config
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError


def test_each_connection_rejects_invalid_foreign_key_and_preserves_pragmas(tmp_path):
    engine = make_engine(tmp_path / "foreign.sqlite3")
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE parent (id INTEGER PRIMARY KEY)")
        connection.exec_driver_sql("CREATE TABLE child (parent_id INTEGER REFERENCES parent(id))")
    with engine.connect() as first, engine.connect() as second:
        for connection in (first, second):
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
            assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar_one() == 250
            assert connection.exec_driver_sql("PRAGMA journal_mode").scalar_one() == "wal"
            with pytest.raises(IntegrityError):
                connection.exec_driver_sql("INSERT INTO child VALUES (123)")
            connection.rollback()
    engine.dispose()


def test_migration_connection_enforces_foreign_keys_and_round_trips(tmp_path):
    engine = make_engine(tmp_path / "migration.sqlite3")
    observed = []

    @event.listens_for(engine, "before_cursor_execute")
    def observe(connection, cursor, statement, parameters, context, executemany):
        if "alembic_version" in statement.lower():
            observed.append(connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one())

    config = migration_config(engine)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    assert observed and all(value == 1 for value in observed)
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT count(*) FROM diagnostic_runs").scalar_one() == 0
    engine.dispose()
