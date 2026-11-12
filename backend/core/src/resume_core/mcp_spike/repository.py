"""Transactional persistence for externally reported synthetic progress."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Engine, insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from resume_core.mcp_spike.contracts import ProgressReport, Receipt
from resume_core.mcp_spike.database import reports


class Conflict(Exception):
    """The idempotency key already identifies a different event."""


class TemporarilyUnavailable(Exception):
    """Persistence could not safely complete."""


class Repository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def record(self, client_id: str, report: ProgressReport) -> Receipt:
        key = (
            (reports.c.client_id == client_id)
            & (reports.c.application_id == report.application_id)
            & (reports.c.execution_id == report.execution_id)
            & (reports.c.idempotency_key == report.idempotency_key)
        )
        receipt_id = str(uuid4())
        try:
            try:
                with self.engine.begin() as connection:
                    connection.execute(
                        insert(reports).values(
                            receipt_id=receipt_id,
                            client_id=client_id,
                            application_id=report.application_id,
                            execution_id=report.execution_id,
                            idempotency_key=report.idempotency_key,
                            event=report.event,
                            confirmation_state="reported_by_agent",
                            created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                        )
                    )
            except IntegrityError:
                with self.engine.connect() as connection:
                    existing = (
                        connection.execute(select(reports).where(key)).mappings().one_or_none()
                    )
                if existing is None:
                    raise TemporarilyUnavailable from None
                if existing["event"] != report.event:
                    raise Conflict from None
                receipt_id = existing["receipt_id"]
        except SQLAlchemyError as exc:
            raise TemporarilyUnavailable from exc
        return Receipt(receipt_id=receipt_id, confirmation_state="reported_by_agent")
