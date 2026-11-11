"""Contracts draft, NOT executable backend API or persisted schema.

Pydantic 2 illustrative models corresponding to PROJECT_SOURCE.md §10.
Run basic import/check only after Pydantic is installed separately.
"""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

Privacy = Literal["public", "professional", "confidential", "secret"]
Confirmation = Literal["confirmed", "unverified"]

class CareerFact(ApiModel):
    id: str
    provenance: list[str] = Field(default_factory=list)
    confirmation: Confirmation = "unverified"
    privacy: Privacy = "confidential"

class ResumeRevision(ApiModel):
    id: str
    resume_id: str
    job_snapshot_id: str | None = None
    content: Any
    parent_revision_id: str | None = None

class ChangeSet(ApiModel):
    id: str
    base_revision_id: str
    operations: list[dict[str, Any]]
    evidence_ids: list[str] = Field(default_factory=list)
    state: Literal["proposed", "approved", "rejected", "applied"] = "proposed"

class ApplicationContext(ApiModel):
    application_id: str
    job_snapshot_id: str
    resume_revision_id: str
    approved_answers: list[Any] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)

class ApplicationReport(ApiModel):
    application_id: str
    execution_id: str
    idempotency_key: str
    status: Literal["in_progress", "blocked", "reported_submitted", "reported_failed", "unknown"]
    source: Literal["external_agent"] = "external_agent"

# Staging `pending_review` belongs to ImportCandidate, not CareerFact.confirmation.
# Real API error models, validation of evidenceIds, and persistence are not implemented.
