"""Short SQLite transactions; the diagnostic record is the durable intention."""

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import Engine, insert, select

from resume_core.contracts import DiagnosticExecution
from resume_core.database import diagnostic_runs as runs

EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
ACTIVE = ("pending", "queued", "running")


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
