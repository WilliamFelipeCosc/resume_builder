from uuid import uuid4

import pytest
from resume_core.repository import ActiveDiagnosticConflict
from resume_core.service import DiagnosticService, Principal

OWNER = Principal("synthetic-linux-user", frozenset({"diagnostic:read", "diagnostic:write"}))


def test_authorized_service_create_and_latest_contract(repository):
    repo, _clock = repository
    service = DiagnosticService(repo)
    assert service.latest(OWNER).execution is None
    key, request = uuid4(), uuid4()
    outcome = service.create(key, OWNER, request_id=request)
    assert outcome.created is True
    assert outcome.execution.idempotency_key == key
    assert outcome.execution.request_id == request
    assert service.latest(OWNER).execution == outcome.execution


def test_read_reconciles_expired_before_returning(repository):
    repo, clock = repository
    service = DiagnosticService(repo)
    original = service.create(uuid4(), OWNER).execution
    clock.advance(120)
    latest = service.latest(OWNER).execution
    assert latest.id == original.id
    assert latest.status == "failed"
    assert latest.error.code == "deadline_exceeded"


def test_create_reconciles_expired_before_new_intention(repository):
    repo, clock = repository
    service = DiagnosticService(repo)
    first = service.create(uuid4(), OWNER).execution
    clock.advance(120)
    second = service.create(uuid4(), OWNER).execution
    assert second.id != first.id
    assert second.status == "pending"
    assert repo.get(first.id).status == "failed"


def test_service_idempotency_and_conflict_preserve_original(repository):
    repo, _clock = repository
    service = DiagnosticService(repo)
    key = uuid4()
    first = service.create(key, OWNER)
    replay = service.create(key, OWNER)
    assert replay.created is False
    assert replay.execution == first.execution
    with pytest.raises(ActiveDiagnosticConflict):
        service.create(uuid4(), OWNER)
    assert service.latest(OWNER).execution == first.execution
