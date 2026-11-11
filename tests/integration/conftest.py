from datetime import UTC, datetime, timedelta

import pytest
from alembic import command
from resume_core.database import make_engine, migration_config
from resume_core.repository import DiagnosticRepository


class Clock:
    def __init__(self):
        self.now = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += timedelta(seconds=seconds)


@pytest.fixture
def repository(tmp_path):
    engine = make_engine(tmp_path / "diagnostics.sqlite3")
    command.upgrade(migration_config(engine), "head")
    clock = Clock()
    yield DiagnosticRepository(engine, clock=clock), clock
    engine.dispose()
