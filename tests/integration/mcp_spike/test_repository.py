"""SPIKE-06/07/08/09/20/21: real durable idempotent receipts."""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from pathlib import Path

import pytest
from alembic import command
from resume_core.mcp_spike.contracts import ProgressReport
from resume_core.mcp_spike.database import make_engine, reports
from resume_core.mcp_spike.repository import Conflict, Repository, TemporarilyUnavailable
from resume_mcp_server.migration import migration_config
from sqlalchemy import select
from sqlalchemy.exc import OperationalError


@pytest.fixture
def engine(tmp_path):
    engine = make_engine(tmp_path / "mcp-spike.sqlite3")
    command.upgrade(migration_config(engine), "head")
    yield engine
    engine.dispose()


def report(event="started", **changes):
    return ProgressReport.model_validate(
        {
            "applicationId": "app-demo",
            "executionId": "run-1",
            "idempotencyKey": "key-1",
            "event": event,
        }
        | changes
    )


def rows(engine):
    with engine.connect() as connection:
        return connection.execute(select(reports)).mappings().all()


def run_process(path, event, barrier):
    engine = make_engine(path)
    barrier.wait(timeout=10)
    try:
        try:
            return ("receipt", Repository(engine).record("hermes", report(event)).receipt_id)
        except Conflict:
            return ("conflict", None)
    finally:
        engine.dispose()


def record_in_process(path):
    engine = make_engine(path)
    try:
        return Repository(engine).record("hermes", report()).receipt_id
    finally:
        engine.dispose()


def test_success_is_committed_and_returns_only_reported_state(engine):
    result = Repository(engine).record("hermes", report())
    stored = rows(engine)
    assert len(stored) == 1
    assert stored[0]["receipt_id"] == result.receipt_id
    assert stored[0]["event"] == "started"
    assert stored[0]["confirmation_state"] == result.confirmation_state == "reported_by_agent"
    assert stored[0]["created_at"].endswith("Z")


def test_replay_preserves_complete_record_and_receipt(engine):
    repo = Repository(engine)
    first = repo.record("hermes", report())
    original = dict(rows(engine)[0])
    second = repo.record("hermes", report())
    assert second == first
    assert list(map(dict, rows(engine))) == [original]


def test_changed_event_conflicts_and_preserves_original(engine):
    repo = Repository(engine)
    repo.record("hermes", report())
    original = dict(rows(engine)[0])
    with pytest.raises(Conflict):
        repo.record("hermes", report("blocked"))
    assert list(map(dict, rows(engine))) == [original]


@pytest.mark.parametrize(
    "change",
    [
        {"executionId": "run-2"},
        {"idempotencyKey": "key-2"},
    ],
)
def test_distinct_execution_or_key_creates_distinct_receipt(engine, change):
    repo = Repository(engine)
    first = repo.record("hermes", report())
    second = repo.record("hermes", report(**change))
    assert first.receipt_id != second.receipt_id
    assert len(rows(engine)) == 2


def test_distinct_client_has_distinct_receipt(engine):
    repo = Repository(engine)
    first = repo.record("hermes", report())
    second = repo.record("codex", report())
    assert first.receipt_id != second.receipt_id
    assert len(rows(engine)) == 2


def test_restart_returns_same_receipt(engine):
    first = Repository(engine).record("hermes", report())
    database_path = engine.url.database
    engine.dispose()
    restarted = make_engine(Path(database_path))
    try:
        assert Repository(restarted).record("hermes", report()) == first
        assert len(rows(restarted)) == 1
    finally:
        restarted.dispose()


def test_receipt_survives_two_separate_processes(engine):
    path = Path(engine.url.database)
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=1, mp_context=ctx) as first:
        receipt = first.submit(record_in_process, path).result(timeout=20)
    with ProcessPoolExecutor(max_workers=1, mp_context=ctx) as second:
        replay = second.submit(record_in_process, path).result(timeout=20)
    assert receipt == replay == rows(engine)[0]["receipt_id"]
    assert len(rows(engine)) == 1


def test_locked_database_returns_no_receipt_and_retry_can_commit(engine):
    with engine.connect() as connection:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        try:
            with pytest.raises(TemporarilyUnavailable):
                Repository(engine).record("hermes", report())
        finally:
            connection.rollback()
    assert len(rows(engine)) == 0
    assert Repository(engine).record("hermes", report()).confirmation_state == "reported_by_agent"
    assert len(rows(engine)) == 1


def test_commit_failure_does_not_return_receipt_or_leave_row(engine, monkeypatch):
    original_begin = engine.begin

    @contextmanager
    def failed_commit():
        with original_begin() as connection:
            yield connection
            raise OperationalError("commit", {}, RuntimeError("failure"))

    monkeypatch.setattr(engine, "begin", failed_commit)
    with pytest.raises(TemporarilyUnavailable):
        Repository(engine).record("hermes", report())
    assert rows(engine) == []


@pytest.mark.parametrize("second_event", ["started", "blocked"])
def test_concurrent_processes_share_one_event_and_correct_outcome(engine, second_event):
    ctx = multiprocessing.get_context("spawn")
    with ctx.Manager() as manager:
        barrier = manager.Barrier(2)
        with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
            path = Path(engine.url.database)
            jobs = [
                pool.submit(run_process, path, event, barrier)
                for event in ("started", second_event)
            ]
            results = [job.result(timeout=20) for job in jobs]
    stored = rows(engine)
    assert len(stored) == 1
    if second_event == "started":
        assert results == [("receipt", stored[0]["receipt_id"])] * 2
    else:
        assert sorted(result[0] for result in results) == ["conflict", "receipt"]
        assert (
            next(value for kind, value in results if kind == "receipt") == stored[0]["receipt_id"]
        )
        assert stored[0]["event"] in {"started", "blocked"}
