"""Isolated SQLite metadata for synthetic reports; no I/O on import."""

from pathlib import Path

from sqlalchemy import CheckConstraint, Column, Engine, MetaData, Table, Text, UniqueConstraint

from resume_core.database import make_engine as _make_sqlite_engine

metadata = MetaData()
reports = Table(
    "mcp_spike_reports",
    metadata,
    Column("receipt_id", Text, primary_key=True, nullable=False),
    Column("client_id", Text, nullable=False),
    Column("application_id", Text, nullable=False),
    Column("execution_id", Text, nullable=False),
    Column("idempotency_key", Text, nullable=False),
    Column("event", Text, nullable=False),
    Column("confirmation_state", Text, nullable=False),
    Column("created_at", Text, nullable=False),
    UniqueConstraint("client_id", "application_id", "execution_id", "idempotency_key"),
    CheckConstraint("event IN ('started', 'form_filled', 'blocked')"),
    CheckConstraint("confirmation_state = 'reported_by_agent'"),
)


def make_engine(path: Path) -> Engine:
    if path.name != "mcp-spike.sqlite3":
        raise ValueError("spike database must use its dedicated filename")
    return _make_sqlite_engine(path)
