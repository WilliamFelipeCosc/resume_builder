"""Run explicit migrations only against the supplied spike engine."""

from alembic import context

engine = context.config.attributes["engine"]
with engine.begin() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
