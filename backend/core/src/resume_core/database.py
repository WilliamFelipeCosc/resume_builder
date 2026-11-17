"""Explicit SQLite composition. Imports never create files or run migrations."""

from pathlib import Path

from alembic.config import Config
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    Engine,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
)

metadata = MetaData()
diagnostic_runs = Table(
    "diagnostic_runs",
    metadata,
    Column("id", String, primary_key=True),
    Column("request_id", String, nullable=False),
    Column("idempotency_key", String, nullable=False),
    Column("status", String, nullable=False),
    Column("attempt_count", Integer, nullable=False),
    Column("created_at", BigInteger, nullable=False),
    Column("updated_at", BigInteger, nullable=False),
    Column("result", JSON(none_as_null=True)),
    Column("error", JSON(none_as_null=True)),
    Column("delivery_warning", JSON(none_as_null=True)),
    Column("lease_token", String),
    Column("lease_expires_at", BigInteger),
    Column("next_delivery_at", BigInteger, nullable=False),
)


def make_engine(path: Path) -> Engine:
    if not path.is_absolute() or path.is_symlink():
        raise ValueError("database requires an absolute non-symlink path")
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"timeout": 0.25},
        hide_parameters=True,
    )

    @event.listens_for(engine, "connect")
    def configure(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=250")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def migration_config(engine: Engine) -> Config:
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[3] / "migrations")
    )
    config.attributes["engine"] = engine
    return config
