"""FND-08..12: controlled clocks recover only within the approved budget."""

from uuid import uuid4

import pytest


def active(repo):
    return repo.create(uuid4(), uuid4()).execution


def test_expired_lease_recovers_same_execution(repository):
    repo, clock = repository
    original = active(repo)
    old = repo.claim(original.id)
    clock.advance(30)
    assert repo.reconcile() == 1
    recovered = repo.get(original.id)
    assert recovered.id == original.id
    assert recovered.request_id == original.request_id
    assert recovered.created_at == original.created_at
    assert recovered.status == "pending"
    assert recovered.attempt_count == 1
    assert recovered.error is None
    new = repo.claim(original.id)
    assert new.execution.attempt_count == 2
    assert repo.complete(original.id, old.token) is False
    assert repo.complete(original.id, new.token) is True


def test_failed_attempt_retries_same_id_without_final_error(repository):
    repo, _clock = repository
    original = active(repo)
    lease = repo.claim(original.id)
    assert repo.fail_attempt(original.id, lease.token) is True
    pending = repo.get(original.id)
    assert pending.status == "pending"
    assert pending.id == original.id
    assert pending.attempt_count == 1
    assert pending.error is pending.result is None
    assert repo.fail_attempt(original.id, lease.token) is False


def test_third_failure_is_terminal_and_cannot_claim(repository):
    repo, _clock = repository
    original = active(repo)
    for _ in range(3):
        lease = repo.claim(original.id)
        assert repo.fail_attempt(original.id, lease.token) is True
    failed = repo.get(original.id)
    assert failed.status == "failed"
    assert failed.attempt_count == 3
    assert failed.error.model_dump() == {
        "code": "attempts_exhausted",
        "message": "Diagnostic attempts exhausted.",
    }
    assert failed.result is failed.delivery_warning is None
    assert repo.claim(original.id) is None
    assert repo.reconcile() == 0
    assert repo.get(original.id) == failed


def test_third_abandoned_attempt_is_terminal(repository):
    repo, clock = repository
    original = active(repo)
    for _ in range(3):
        repo.claim(original.id)
        clock.advance(30)
        assert repo.reconcile() == 1
    failed = repo.get(original.id)
    assert failed.status == "failed"
    assert failed.attempt_count == 3
    assert failed.error.code == "attempts_exhausted"


@pytest.mark.parametrize("elapsed", [120, 120.000001, 1000])
def test_total_deadline_fails_pending_without_attempt(repository, elapsed):
    repo, clock = repository
    original = active(repo)
    clock.advance(elapsed)
    assert repo.claim(original.id) is None
    assert repo.reconcile() == 1
    failed = repo.get(original.id)
    assert failed.status == "failed"
    assert failed.attempt_count == 0
    assert failed.error.model_dump() == {
        "code": "deadline_exceeded",
        "message": "Diagnostic deadline exceeded.",
    }
    assert failed.result is failed.delivery_warning is None


def test_before_deadline_and_lease_does_not_mutate_polling(repository):
    repo, clock = repository
    original = active(repo)
    lease = repo.claim(original.id)
    clock.advance(29.999999)
    assert repo.reconcile() == 0
    assert repo.get(original.id) == lease.execution


def test_pending_just_before_deadline_still_claims(repository):
    repo, clock = repository
    original = active(repo)
    clock.advance(119.999999)
    assert repo.reconcile() == 0
    lease = repo.claim(original.id)
    assert lease is not None
    assert (lease.expires_at - clock.now).total_seconds() == 0.000001


def test_expired_failure_cannot_write_and_deadline_has_precedence(repository):
    repo, clock = repository
    original = active(repo)
    clock.advance(110)
    lease = repo.claim(original.id)
    clock.advance(10)
    assert repo.fail_attempt(original.id, lease.token) is False
    assert repo.reconcile() == 1
    failed = repo.get(original.id)
    assert failed.error.code == "deadline_exceeded"
    assert repo.complete(original.id, lease.token) is False
    assert repo.reconcile() == 0
    assert repo.get(original.id) == failed


def test_success_remains_immutable_after_deadline(repository):
    repo, clock = repository
    original = active(repo)
    lease = repo.claim(original.id)
    repo.complete(original.id, lease.token)
    succeeded = repo.get(original.id)
    clock.advance(1000)
    assert repo.reconcile() == 0
    assert repo.get(original.id) == succeeded
