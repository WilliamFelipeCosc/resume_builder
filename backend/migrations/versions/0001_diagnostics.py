"""Create the synthetic M0 diagnostic, isolated from professional data."""

import sqlalchemy as sa
from alembic import op

revision = "0001_diagnostics"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "diagnostic_runs",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("request_id", sa.String, nullable=False),
        sa.Column("idempotency_key", sa.String, nullable=False, unique=True),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("attempt_count", sa.Integer, nullable=False),
        sa.Column("created_at", sa.BigInteger, nullable=False),
        sa.Column("updated_at", sa.BigInteger, nullable=False),
        sa.Column("result", sa.JSON(none_as_null=True)),
        sa.Column("error", sa.JSON(none_as_null=True)),
        sa.Column("delivery_warning", sa.JSON(none_as_null=True)),
        sa.Column("lease_token", sa.String),
        sa.Column("lease_expires_at", sa.BigInteger),
        sa.Column("next_delivery_at", sa.BigInteger, nullable=False),
        sa.CheckConstraint(
            "status IN ('pending','queued','running','succeeded','failed')", name="status"
        ),
        sa.CheckConstraint(
            "typeof(attempt_count)='integer' AND attempt_count BETWEEN 0 AND 3", name="attempts"
        ),
        sa.CheckConstraint(
            "(status='succeeded' AND result IS NOT NULL AND error IS NULL AND delivery_warning IS NULL) OR "
            "(status='failed' AND error IS NOT NULL AND result IS NULL AND delivery_warning IS NULL) OR "
            "(status IN ('pending','queued','running') AND result IS NULL AND error IS NULL)",
            name="outcome",
        ),
        sa.CheckConstraint(
            "result IS NULL OR coalesce((json_valid(result) AND json_extract(result,'$.message')='diagnostic_completed' "
            "AND json_extract(result,'$.fixtureVersion')='m0-v1' "
            "AND json_remove(result,'$.message','$.fixtureVersion')='{}'), 0)",
            name="fixed_result",
        ),
        sa.CheckConstraint(
            "error IS NULL OR coalesce((json_valid(error) AND ("
            "(json_extract(error,'$.code')='deadline_exceeded' AND json_extract(error,'$.message')='Diagnostic deadline exceeded.') OR "
            "(json_extract(error,'$.code')='attempts_exhausted' AND json_extract(error,'$.message')='Diagnostic attempts exhausted.') OR "
            "(json_extract(error,'$.code')='internal_error' AND json_extract(error,'$.message')='Diagnostic could not be completed.')"
            ") AND json_remove(error,'$.code','$.message')='{}'), 0)",
            name="safe_error",
        ),
        sa.CheckConstraint(
            "delivery_warning IS NULL OR coalesce((json_valid(delivery_warning) "
            "AND json_extract(delivery_warning,'$.code')='queue_unavailable' "
            "AND json_extract(delivery_warning,'$.message')='Queue is temporarily unavailable.' "
            "AND json_remove(delivery_warning,'$.code','$.message')='{}'), 0)",
            name="safe_warning",
        ),
        sa.CheckConstraint(
            "(status='running' AND lease_token IS NOT NULL AND lease_expires_at IS NOT NULL) OR "
            "(status!='running' AND lease_token IS NULL AND lease_expires_at IS NULL)",
            name="lease",
        ),
    )
    op.create_index(
        "one_active_diagnostic",
        "diagnostic_runs",
        [sa.text("(1)")],
        unique=True,
        sqlite_where=sa.text("status IN ('pending','queued','running')"),
    )


def downgrade():
    op.drop_index("one_active_diagnostic", table_name="diagnostic_runs")
    op.drop_table("diagnostic_runs")
