"""Short SQLite transactions; the diagnostic record is the durable intention."""

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import Engine, func, insert, select, update

from resume_core.contracts import DiagnosticError, DiagnosticExecution, DiagnosticResult
from resume_core.database import diagnostic_runs as runs

EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
ACTIVE = ("pending", "queued", "running")
TOTAL_US = 120_000_000
LEASE_US = 30_000_000


def to_micros(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("clock must be timezone-aware")
    delta = value.astimezone(UTC) - EPOCH
    return (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds


def execution_from_row(row) -> DiagnosticExecution:
    data = {name: row[name] for name in DiagnosticExecution.model_fields}
    for name in ("created_at", "updated_at"):
        data[name] = EPOCH + timedelta(microseconds=data[name])
    return DiagnosticExecution.model_validate(data)


class ActiveDiagnosticConflict(Exception):
    """A distinct intention cannot replace an active run."""


@dataclass(frozen=True)
class CreateOutcome:
    execution: DiagnosticExecution
    created: bool


@dataclass(frozen=True)
class Lease:
    execution: DiagnosticExecution
    token: UUID
    expires_at: datetime


class DiagnosticRepository:
    def __init__(self, engine: Engine, clock: Callable[[], datetime] | None = None):
        self.engine = engine
        self.clock = clock or (lambda: datetime.now(UTC))

    @contextmanager
    def _write(self):
        with self.engine.connect() as connection:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            try:
                yield connection, to_micros(self.clock())
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    def create(self, key: UUID, request_id: UUID) -> CreateOutcome:
        with self._write() as (connection, now):
            existing = (
                connection.execute(select(runs).where(runs.c.idempotency_key == str(key)))
                .mappings()
                .first()
            )
            if existing is not None:
                return CreateOutcome(execution_from_row(existing), False)
            if connection.execute(select(runs.c.id).where(runs.c.status.in_(ACTIVE))).first():
                raise ActiveDiagnosticConflict("A diagnostic is already active.")
            row = (
                connection.execute(
                    insert(runs)
                    .values(
                        id=str(uuid4()),
                        request_id=str(request_id),
                        idempotency_key=str(key),
                        status="pending",
                        attempt_count=0,
                        created_at=now,
                        updated_at=now,
                        next_delivery_at=now,
                    )
                    .returning(runs)
                )
                .mappings()
                .one()
            )
            outcome = CreateOutcome(execution_from_row(row), True)
        return outcome

    def latest(self) -> DiagnosticExecution | None:
        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    select(runs).order_by(runs.c.created_at.desc(), runs.c.id.desc()).limit(1)
                )
                .mappings()
                .first()
            )
            return execution_from_row(row) if row is not None else None

    def get(self, execution_id: UUID) -> DiagnosticExecution | None:
        with self.engine.connect() as connection:
            row = (
                connection.execute(select(runs).where(runs.c.id == str(execution_id)))
                .mappings()
                .first()
            )
            return execution_from_row(row) if row is not None else None

    def claim(self, execution_id: UUID) -> Lease | None:
        token = uuid4()
        with self._write() as (connection, now):
            row = (
                connection.execute(
                    update(runs)
                    .where(
                        runs.c.id == str(execution_id),
                        runs.c.status.in_(("pending", "queued")),
                        runs.c.attempt_count < 3,
                        runs.c.created_at > now - TOTAL_US,
                    )
                    .values(
                        status="running",
                        attempt_count=runs.c.attempt_count + 1,
                        lease_token=str(token),
                        lease_expires_at=func.min(now + LEASE_US, runs.c.created_at + TOTAL_US),
                        updated_at=now,
                        delivery_warning=None,
                    )
                    .returning(runs)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return Lease(
                execution_from_row(row),
                token,
                EPOCH + timedelta(microseconds=row["lease_expires_at"]),
            )

    def complete(self, execution_id: UUID, token: UUID) -> bool:
        with self._write() as (connection, now):
            row = connection.execute(
                update(runs)
                .where(
                    runs.c.id == str(execution_id),
                    runs.c.status == "running",
                    runs.c.lease_token == str(token),
                    runs.c.lease_expires_at > now,
                    runs.c.created_at > now - TOTAL_US,
                )
                .values(
                    status="succeeded",
                    updated_at=now,
                    result=DiagnosticResult().model_dump(),
                    error=None,
                    delivery_warning=None,
                    lease_token=None,
                    lease_expires_at=None,
                )
                .returning(runs.c.id)
            ).first()
            return row is not None

    @staticmethod
    def _failure_values(now: int, code=None):
        return dict(
            status="failed" if code else "pending",
            updated_at=now,
            lease_token=None,
            lease_expires_at=None,
            result=None,
            delivery_warning=None,
            error=DiagnosticError.for_code(code).model_dump() if code else None,
            next_delivery_at=now,
        )

    def fail_attempt(self, execution_id: UUID, token: UUID) -> bool:
        with self._write() as (connection, now):
            row = (
                connection.execute(
                    select(runs).where(
                        runs.c.id == str(execution_id),
                        runs.c.status == "running",
                        runs.c.lease_token == str(token),
                        runs.c.lease_expires_at > now,
                        runs.c.created_at > now - TOTAL_US,
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                return False
            code = "attempts_exhausted" if row["attempt_count"] >= 3 else None
            connection.execute(
                update(runs).where(runs.c.id == row["id"]).values(**self._failure_values(now, code))
            )
            return True

    def reconcile(self) -> int:
        changed = 0
        with self._write() as (connection, now):
            rows = (
                connection.execute(select(runs).where(runs.c.status.in_(ACTIVE))).mappings().all()
            )
            for row in rows:
                if row["created_at"] + TOTAL_US <= now:
                    code = "deadline_exceeded"
                elif row["status"] == "running" and row["lease_expires_at"] <= now:
                    code = "attempts_exhausted" if row["attempt_count"] >= 3 else None
                elif row["status"] != "running" and row["attempt_count"] >= 3:
                    code = "attempts_exhausted"
                else:
                    continue
                connection.execute(
                    update(runs)
                    .where(runs.c.id == row["id"])
                    .values(**self._failure_values(now, code))
                )
                changed += 1
        return changed
