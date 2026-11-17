"""Add typed current content and enforce kind/profile associations."""

import sqlalchemy as sa
from alembic import op

revision = "0003_kb_entities"
down_revision = "0002_kb_foundation"
branch_labels = None
depends_on = None

# Frozen migration schema; subsequent model changes require another migration.
SCHEMA = {
    "profile": [
        ("full_name", "name", 1),
        ("professional_headline", "name", 0),
        ("email", "name", 0),
        ("phone_original", "name", 0),
        ("objective_original", "text", 0),
        ("city_of_residence", "name", 0),
        ("country_of_residence", "name", 0),
        ("linkedin_url", "name", 0),
        ("github_url", "name", 0),
    ],
    "experience": [
        ("company_name_original", "name", 1),
        ("job_title_original", "name", 1),
        ("start_date_original", "name", 0),
        ("end_date_original", "name", 0),
        ("start_period", "json", 0),
        ("end_period", "json", 0),
        ("end_date_is_current_as_of_source", "bool", 0),
        ("location", "name", 0),
    ],
    "statement": [
        ("text_original", "text", 1),
        ("text_current", "text", 0),
        ("statement_type", "name", 0),
    ],
    "project": [
        ("title", "name", 1),
        ("title_is_generated_label", "bool", 0),
        ("description_original", "text", 0),
        ("description_current", "text", 0),
        ("time_to_develop_original", "name", 0),
    ],
    "achievement": [
        ("text_original", "text", 1),
        ("text_current", "text", 0),
        ("metric_type", "name", 0),
        ("metric_value", "text", 0),
        ("metric_unit", "name", 0),
        ("metric_meaning", "text", 0),
    ],
    "skill": [
        ("name", "name", 1),
        ("original_labels", "json", 1),
        ("category", "name", 0),
        ("explicitly_listed_in_skills_section", "bool", 0),
    ],
    "education": [
        ("institution", "name", 1),
        ("program_original", "name", 1),
        ("start_date_original", "name", 0),
        ("end_date_original", "name", 0),
        ("start_period", "json", 0),
        ("end_period", "json", 0),
        ("ongoing_as_of_source_document", "bool", 0),
        ("currently_ongoing", "bool", 0),
        ("location", "name", 0),
        ("description_original", "text", 0),
        ("description_current", "text", 0),
    ],
    "language": [("language", "name", 1), ("proficiency_original", "name", 1)],
    "evidence": [
        ("description", "text", 1),
        ("evidence_kind", "name", 1),
        ("source_document_id", "source", 1),
        ("page", "int", 0),
        ("excerpt", "text", 0),
    ],
}
TABLE_NAMES = {"education": "kb_education", "evidence": "kb_evidence"}


def upgrade():
    types = {
        "name": sa.String(256),
        "text": sa.String(8000),
        "json": sa.JSON,
        "bool": sa.Boolean,
        "int": sa.Integer,
        "source": sa.String,
    }
    for kind, fields in SCHEMA.items():
        table = TABLE_NAMES.get(kind, f"kb_{kind}s")
        columns = [
            sa.Column("entity_id", sa.String, sa.ForeignKey("kb_entities.id"), primary_key=True)
        ]
        for name, field_type, required in fields:
            args = [sa.ForeignKey("source_documents.id")] if field_type == "source" else []
            columns.append(sa.Column(name, types[field_type], *args, nullable=not required))
            if field_type in {"name", "text"}:
                limit = 256 if field_type == "name" else 8000
                columns.append(
                    sa.CheckConstraint(
                        f"{name} IS NULL OR length({name}) BETWEEN 1 AND {limit}",
                        name=f"ck_{kind}_{name}_length",
                    )
                )
            elif field_type == "bool":
                columns.append(
                    sa.CheckConstraint(
                        f"{name} IS NULL OR {name} IN (0,1)", name=f"ck_{kind}_{name}_boolean"
                    )
                )
        if kind == "statement":
            columns.append(
                sa.CheckConstraint(
                    "statement_type IS NULL OR statement_type IN ('responsibility','activity','result','editorial','unspecified')",
                    name="ck_statement_type",
                )
            )
        if kind == "evidence":
            columns.extend(
                [
                    sa.CheckConstraint(
                        "evidence_kind IN ('documentary','manual_note')", name="ck_evidence_kind"
                    ),
                    sa.CheckConstraint("page IS NULL OR page >= 1", name="ck_evidence_page"),
                ]
            )
        op.create_table(table, *columns)
        op.execute(f"""CREATE TRIGGER {table}_kind_insert BEFORE INSERT ON {table}
            WHEN NOT EXISTS (SELECT 1 FROM kb_entities WHERE id=NEW.entity_id AND kind='{kind}')
            BEGIN SELECT RAISE(ABORT, 'invalid entity kind'); END""")
        op.execute(f"""CREATE TRIGGER {table}_kind_update BEFORE UPDATE OF entity_id ON {table}
            WHEN NOT EXISTS (SELECT 1 FROM kb_entities WHERE id=NEW.entity_id AND kind='{kind}')
            BEGIN SELECT RAISE(ABORT, 'invalid entity kind'); END""")
    op.execute("""CREATE TRIGGER kb_entity_profile_insert BEFORE INSERT ON kb_entities
        WHEN (NEW.kind='profile' AND NEW.profile_id IS NOT NULL)
          OR (NEW.kind<>'profile' AND NOT EXISTS
              (SELECT 1 FROM kb_entities WHERE id=NEW.profile_id AND kind='profile'))
        BEGIN SELECT RAISE(ABORT, 'invalid profile association'); END""")
    op.execute("""CREATE TRIGGER kb_entity_profile_update BEFORE UPDATE OF kind, profile_id ON kb_entities
        WHEN NEW.kind<>OLD.kind OR (NEW.kind='profile' AND NEW.profile_id IS NOT NULL)
          OR (NEW.kind<>'profile' AND NOT EXISTS
              (SELECT 1 FROM kb_entities WHERE id=NEW.profile_id AND kind='profile'))
        BEGIN SELECT RAISE(ABORT, 'invalid profile association'); END""")


def downgrade():
    op.execute("DROP TRIGGER kb_entity_profile_update")
    op.execute("DROP TRIGGER kb_entity_profile_insert")
    for kind in reversed(SCHEMA):
        table = TABLE_NAMES.get(kind, f"kb_{kind}s")
        op.execute(f"DROP TRIGGER {table}_kind_update")
        op.execute(f"DROP TRIGGER {table}_kind_insert")
        op.drop_table(table)
