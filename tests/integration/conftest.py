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


@pytest.fixture(scope="session")
def isolated_redis():
    from redis_harness import DockerRedis

    with DockerRedis() as server:
        yield server


@pytest.fixture
def redis_broker(isolated_redis):
    from uuid import uuid4

    from resume_core.broker import make_broker

    broker = make_broker(isolated_redis.url, "rb-test-" + uuid4().hex)
    yield broker
    broker.client.close()
