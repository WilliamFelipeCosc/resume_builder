"""Explicit migration configuration for the synthetic MCP database."""

from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Engine

REVISION = "0001_spike_reports"


def migration_config(engine: Engine) -> Config:
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[2] / "migrations")
    )
    config.attributes["engine"] = engine
    return config


def is_current(engine: Engine) -> bool:
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision() == REVISION
