"""FND-01/04/05/06: durable intentions and concurrency before delivery."""

from concurrent.futures import ThreadPoolExecutor
from uuid import UUID, uuid4

import pytest
from resume_core.database import diagnostic_runs
from resume_core.repository import ActiveDiagnosticConflict
from sqlalchemy import func, select, update


def test_empty_latest(repository):
    repo, _clock = repository
    assert repo.latest() is None


def test_create_persists_full_pending_record_before_return(repository):
    repo, clock = repository
    key, request = uuid4(), uuid4()
    outcome = repo.create(key, request)
    assert outcome.created is True
    execution = outcome.execution
    assert isinstance(execution.id, UUID)
    assert execution.request_id == request
    assert execution.idempotency_key == key
    assert execution.status == "pending"
    assert execution.attempt_count == 0
    assert execution.created_at == execution.updated_at == clock.now
    assert execution.result is execution.error is execution.delivery_warning is None
    assert repo.latest() == execution
    with repo.engine.connect() as connection:
        assert (
            connection.execute(select(func.count()).select_from(diagnostic_runs)).scalar_one() == 1
        )


def test_same_key_preserves_request_id_and_timestamp(repository):
    repo, clock = repository
    key = uuid4()
    initial = repo.create(key, uuid4()).execution
    clock.advance(2)
    replay = repo.create(key, uuid4())
    assert replay.created is False
    assert replay.execution == initial


def test_distinct_active_intention_conflicts_without_insertion(repository):
    repo, _clock = repository
    initial = repo.create(uuid4(), uuid4()).execution
    with pytest.raises(ActiveDiagnosticConflict):
        repo.create(uuid4(), uuid4())
    assert repo.latest() == initial


def test_terminal_key_replayed_while_another_run_active(repository):
    repo, clock = repository
    key = uuid4()
    initial = repo.create(key, uuid4()).execution
    with repo.engine.begin() as connection:
        connection.execute(
            update(diagnostic_runs)
            .where(diagnostic_runs.c.id == str(initial.id))
            .values(
                status="succeeded",
                result={"message": "diagnostic_completed", "fixtureVersion": "m0-v1"},
            )
        )
    terminal = repo.latest()
    clock.advance(1)
    second = repo.create(uuid4(), uuid4()).execution
    assert second.id != initial.id
    assert repo.create(key, uuid4()).execution == terminal
    assert repo.latest() == second


def test_concurrent_same_key_returns_one_id(repository):
    repo, _clock = repository
    key = uuid4()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: repo.create(key, uuid4()), range(4)))
    assert len({value.execution.id for value in results}) == 1
    assert sum(value.created for value in results) == 1


def test_concurrent_distinct_keys_only_one_creates(repository):
    repo, _clock = repository

    def create(_):
        try:
            return repo.create(uuid4(), uuid4())
        except ActiveDiagnosticConflict:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(create, range(4)))
    assert sum(value is not None for value in results) == 1


def test_latest_order_is_deterministic_when_timestamps_tie(repository):
    repo, _clock = repository
    first = repo.create(uuid4(), uuid4()).execution
    with repo.engine.begin() as connection:
        connection.execute(
            update(diagnostic_runs).values(
                status="succeeded",
                result={"message": "diagnostic_completed", "fixtureVersion": "m0-v1"},
            )
        )
    second = repo.create(uuid4(), uuid4()).execution
    assert repo.latest().id == max(first.id, second.id, key=str)
