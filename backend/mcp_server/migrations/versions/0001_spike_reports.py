"""Create the isolated synthetic progress report store."""

import sqlalchemy as sa
from alembic import op

revision = "0001_spike_reports"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mcp_spike_reports",
        sa.Column("receipt_id", sa.Text, primary_key=True, nullable=False),
        sa.Column("client_id", sa.Text, nullable=False),
        sa.Column("application_id", sa.Text, nullable=False),
        sa.Column("execution_id", sa.Text, nullable=False),
        sa.Column("idempotency_key", sa.Text, nullable=False),
        sa.Column("event", sa.Text, nullable=False),
        sa.Column("confirmation_state", sa.Text, nullable=False),
        sa.Column("created_at", sa.Text, nullable=False),
        sa.UniqueConstraint("client_id", "application_id", "execution_id", "idempotency_key"),
        sa.CheckConstraint("event IN ('started', 'form_filled', 'blocked')"),
        sa.CheckConstraint("confirmation_state = 'reported_by_agent'"),
    )


def downgrade():
    op.drop_table("mcp_spike_reports")
