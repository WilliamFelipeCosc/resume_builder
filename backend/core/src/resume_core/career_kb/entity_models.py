"""Typed current-content tables mapped to ORM classes."""

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Table

from resume_core.career_kb.models import Base

# (column, storage type, required); structured values remain closed DTO values.
SCHEMA = {
    "profile": [
        ("full_name", "name", True),
        ("professional_headline", "name", False),
        ("email", "name", False),
        ("phone_original", "name", False),
        ("objective_original", "text", False),
        ("city_of_residence", "name", False),
        ("country_of_residence", "name", False),
        ("linkedin_url", "name", False),
        ("github_url", "name", False),
    ],
    "experience": [
        ("company_name_original", "name", True),
        ("job_title_original", "name", True),
        ("start_date_original", "name", False),
        ("end_date_original", "name", False),
        ("start_period", "json", False),
        ("end_period", "json", False),
        ("end_date_is_current_as_of_source", "bool", False),
        ("location", "name", False),
    ],
    "statement": [
        ("text_original", "text", True),
        ("text_current", "text", False),
        ("statement_type", "name", False),
    ],
    "project": [
        ("title", "name", True),
        ("title_is_generated_label", "bool", False),
        ("description_original", "text", False),
        ("description_current", "text", False),
        ("time_to_develop_original", "name", False),
    ],
    "achievement": [
        ("text_original", "text", True),
        ("text_current", "text", False),
        ("metric_type", "name", False),
        ("metric_value", "text", False),
        ("metric_unit", "name", False),
        ("metric_meaning", "text", False),
    ],
    "skill": [
        ("name", "name", True),
        ("original_labels", "json", True),
        ("category", "name", False),
        ("explicitly_listed_in_skills_section", "bool", False),
    ],
    "education": [
        ("institution", "name", True),
        ("program_original", "name", True),
        ("start_date_original", "name", False),
        ("end_date_original", "name", False),
        ("start_period", "json", False),
        ("end_period", "json", False),
        ("ongoing_as_of_source_document", "bool", False),
        ("currently_ongoing", "bool", False),
        ("location", "name", False),
        ("description_original", "text", False),
        ("description_current", "text", False),
    ],
    "language": [("language", "name", True), ("proficiency_original", "name", True)],
    "evidence": [
        ("description", "text", True),
        ("evidence_kind", "name", True),
        ("source_document_id", "source", True),
        ("page", "int", False),
        ("excerpt", "text", False),
    ],
}


def column(name, kind, required):
    types = {
        "name": String(256),
        "text": String(8000),
        "json": JSON,
        "bool": Boolean,
        "int": Integer,
        "source": String,
    }
    args = [ForeignKey("source_documents.id")] if kind == "source" else []
    return Column(name, types[kind], *args, nullable=not required)


ENTITY_MODELS = {}
TABLE_NAMES = {"education": "kb_education", "evidence": "kb_evidence"}
for kind, fields in SCHEMA.items():
    table = Table(
        TABLE_NAMES.get(kind, f"kb_{kind}s"),
        Base.metadata,
        Column("entity_id", String, ForeignKey("kb_entities.id"), primary_key=True),
        *(column(*field) for field in fields),
    )
    model = type(f"{kind.title()}Row", (), {})
    Base.registry.map_imperatively(model, table)
    ENTITY_MODELS[kind] = model
