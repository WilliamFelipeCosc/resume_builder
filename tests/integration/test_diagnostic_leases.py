"""FND-02/09/10/12: leases fence duplicates and late workers."""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from resume_core.database import diagnostic_runs
from sqlalchemy import update


def create(repo):
    return repo.create(uuid4(), uuid4()).execution


def test_claim_changes_state_and_counts_only_effective_attempt(repository):
    repo, clock = repository
    execution = create(repo)
    lease = repo.claim(execution.id)
    assert lease.execution.status == "running"
    assert lease.execution.attempt_count == 1
    assert (lease.expires_at - clock.now).total_seconds() == 30
    assert repo.claim(execution.id) is None
    assert repo.get(execution.id).attempt_count == 1


def test_concurrent_claim_has_only_one_owner(repository):
    repo, _clock = repository
    execution = create(repo)
    with ThreadPoolExecutor(max_workers=4) as pool:
        leases = list(pool.map(lambda _: repo.claim(execution.id), range(4)))
    assert sum(value is not None for value in leases) == 1
    assert repo.get(execution.id).attempt_count == 1


def test_complete_persists_exact_fixture_and_clears_lease(repository):
    repo, clock = repository
    execution = create(repo)
    lease = repo.claim(execution.id)
    clock.advance(1)
    assert repo.complete(execution.id, lease.token) is True
    result = repo.get(execution.id)
    assert result.status == "succeeded"
    assert result.result.model_dump() == {
        "message": "diagnostic_completed",
        "fixtureVersion": "m0-v1",
    }
    assert result.error is result.delivery_warning is None
    assert result.updated_at == clock.now
    assert result.created_at == execution.created_at
    assert result.request_id == execution.request_id
    assert result.attempt_count == 1


@pytest.mark.parametrize("elapsed", [30, 30.000001, 120])
def test_completion_at_or_after_attempt_limit_is_rejected(repository, elapsed):
    repo, clock = repository
    execution = create(repo)
    lease = repo.claim(execution.id)
    clock.advance(elapsed)
    assert repo.complete(execution.id, lease.token) is False
    assert repo.get(execution.id).result is None


def test_just_before_lease_limit_completes(repository):
    repo, clock = repository
    execution = create(repo)
    lease = repo.claim(execution.id)
    clock.advance(29.999999)
    assert repo.complete(execution.id, lease.token) is True


def test_wrong_token_and_unknown_execution_cannot_complete(repository):
    repo, _clock = repository
    execution = create(repo)
    repo.claim(execution.id)
    assert repo.complete(execution.id, uuid4()) is False
    assert repo.complete(uuid4(), uuid4()) is False
    assert repo.get(execution.id).status == "running"


def test_lease_capped_by_total_deadline_and_claim_refused_at_deadline(repository):
    repo, clock = repository
    execution = create(repo)
    clock.advance(110)
    lease = repo.claim(execution.id)
    assert (lease.expires_at - clock.now).total_seconds() == 10
    clock.advance(10)
    assert repo.complete(execution.id, lease.token) is False
    assert repo.claim(execution.id) is None


def test_terminal_delivery_and_completion_are_immutable(repository):
    repo, _clock = repository
    execution = create(repo)
    lease = repo.claim(execution.id)
    assert repo.complete(execution.id, lease.token)
    terminal = repo.get(execution.id)
    assert repo.claim(execution.id) is None
    assert repo.complete(execution.id, lease.token) is False
    assert repo.get(execution.id) == terminal


def test_old_worker_token_rejected_after_new_lease(repository):
    repo, clock = repository
    execution = create(repo)
    old = repo.claim(execution.id)
    clock.advance(30)
    # T10 owns recovery; emulate its persisted transition for this fencing test.
    with repo.engine.begin() as connection:
        connection.execute(
            update(diagnostic_runs).values(
                status="pending", lease_token=None, lease_expires_at=None
            )
        )
    new = repo.claim(execution.id)
    assert new.token != old.token
    assert repo.complete(execution.id, old.token) is False
    assert repo.complete(execution.id, new.token) is True
    assert repo.get(execution.id).attempt_count == 2


def test_no_claim_when_attempt_budget_exhausted(repository):
    repo, _clock = repository
    execution = create(repo)
    with repo.engine.begin() as connection:
        connection.execute(update(diagnostic_runs).values(attempt_count=3))
    assert repo.claim(execution.id) is None
    assert repo.get(execution.id).attempt_count == 3
