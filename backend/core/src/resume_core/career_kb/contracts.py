"""Concrete, validated career content and transport contracts."""

import calendar
import re
from datetime import date
from typing import Annotated, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import Field, StrictBool, StrictStr, create_model, model_validator

from resume_core.contracts import Contract

Name = Annotated[StrictStr, Field(min_length=1, max_length=256)]
Text = Annotated[StrictStr, Field(min_length=1, max_length=8000)]
Privacy = Literal["public", "professional", "confidential", "secret"]
Confirmation = Literal["unverified", "confirmed"]
LEVELS = ("public", "professional", "confidential", "secret")


class PartialDate(Contract):
    value: StrictStr
    precision: Literal["year", "month", "day"]

    @model_validator(mode="after")
    def valid_date(self):
        patterns = {"year": r"\d{4}", "month": r"\d{4}-\d{2}", "day": r"\d{4}-\d{2}-\d{2}"}
        if not re.fullmatch(patterns[self.precision], self.value):
            raise ValueError("invalid partial date")
        parts = [int(part) for part in self.value.split("-")]
        if parts[0] < 1:
            raise ValueError("invalid partial date")
        if len(parts) > 1 and not 1 <= parts[1] <= 12:
            raise ValueError("invalid partial date")
        if len(parts) == 3:
            if not 1 <= parts[2] <= calendar.monthrange(parts[0], parts[1])[1]:
                raise ValueError("invalid partial date")
            date(*parts)
        return self


class ProfileContent(Contract):
    full_name: Name
    professional_headline: Name | None = None
    email: Name | None = None
    phone_original: Name | None = None
    objective_original: Text | None = None
    city_of_residence: Name | None = None
    country_of_residence: Name | None = None
    linkedin_url: Name | None = None
    github_url: Name | None = None


class ExperienceContent(Contract):
    company_name_original: Name
    job_title_original: Name
    start_date_original: Name | None = None
    end_date_original: Name | None = None
    start_period: PartialDate | None = None
    end_period: PartialDate | None = None
    end_date_is_current_as_of_source: StrictBool | None = None
    location: Name | None = None


class StatementContent(Contract):
    text_original: Text
    text_current: Text | None = None
    statement_type: (
        Literal["responsibility", "activity", "result", "editorial", "unspecified"] | None
    ) = None


class ProjectContent(Contract):
    title: Name
    title_is_generated_label: StrictBool | None = None
    description_original: Text | None = None
    description_current: Text | None = None
    time_to_develop_original: Name | None = None


class AchievementContent(Contract):
    text_original: Text
    text_current: Text | None = None
    metric_type: Name | None = None
    metric_value: Text | None = None
    metric_unit: Name | None = None
    metric_meaning: Text | None = None


class SkillContent(Contract):
    name: Name
    original_labels: list[Name] = Field(default_factory=list)
    category: Name | None = None
    explicitly_listed_in_skills_section: StrictBool | None = None


class EducationContent(Contract):
    institution: Name
    program_original: Name
    start_date_original: Name | None = None
    end_date_original: Name | None = None
    start_period: PartialDate | None = None
    end_period: PartialDate | None = None
    ongoing_as_of_source_document: StrictBool | None = None
    currently_ongoing: StrictBool | None = None
    location: Name | None = None
    description_original: Text | None = None
    description_current: Text | None = None


class LanguageContent(Contract):
    language: Name
    proficiency_original: Name


class EvidenceContent(Contract):
    description: Text
    evidence_kind: Literal["documentary", "manual_note"]
    source_document_id: UUID
    page: Annotated[int, Field(strict=True, ge=1)] | None = None
    excerpt: Text | None = None


CONTENT_TYPES = {
    "profile": ProfileContent,
    "experience": ExperienceContent,
    "statement": StatementContent,
    "project": ProjectContent,
    "achievement": AchievementContent,
    "skill": SkillContent,
    "education": EducationContent,
    "language": LanguageContent,
    "evidence": EvidenceContent,
}

T = TypeVar("T", bound=Contract)


class CreateCommand(Contract, Generic[T]):
    content: T
    source_document_id: UUID
    profile_id: UUID | None
    idempotency_key: UUID
    privacy: Privacy = "confidential"
    field_privacy: dict[StrictStr, Privacy] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_scope(self):
        if (isinstance(self.content, ProfileContent)) != (self.profile_id is None):
            raise ValueError("invalid profile association")
        aliases = {field.alias for field in type(self.content).model_fields.values()}
        if not set(self.field_privacy).issubset(aliases):
            raise ValueError("invalid field classification")
        if any(
            LEVELS.index(level) < LEVELS.index(self.privacy)
            for level in self.field_privacy.values()
        ):
            raise ValueError("field classification cannot be less restrictive")
        return self


class ReadEnvelope(Contract, Generic[T]):
    id: UUID
    revision_id: UUID
    content: T
    restricted_fields: list[StrictStr] = Field(default_factory=list)
    privacy: Privacy
    confirmation: Confirmation

    @model_validator(mode="after")
    def valid_fields(self):
        aliases = {field.alias for field in type(self.content).model_fields.values()}
        if not set(self.restricted_fields).issubset(aliases) or any(
            getattr(self.content, name) is not None
            for name, field in type(self.content).model_fields.items()
            if field.alias in self.restricted_fields
        ):
            raise ValueError("invalid restricted field")
        return self


class ProfileReadEnvelope(Contract, Generic[T]):
    id: UUID
    revision_id: UUID
    content: T
    restricted_fields: list[StrictStr] = Field(default_factory=list)
    privacy: Privacy
    field_confirmations: dict[StrictStr, Confirmation]

    @model_validator(mode="after")
    def valid_fields(self):
        aliases = {field.alias for field in type(self.content).model_fields.values()}
        if not set(self.restricted_fields).issubset(aliases) or not set(
            self.field_confirmations
        ).issubset(aliases):
            raise ValueError("invalid field metadata")
        if set(self.restricted_fields) & set(self.field_confirmations):
            raise ValueError("restricted confirmation")
        if any(
            getattr(self.content, name) is not None
            for name, field in type(self.content).model_fields.items()
            if field.alias in self.restricted_fields
        ):
            raise ValueError("restricted value")
        return self


class Page(Contract, Generic[T]):
    items: list[T]
    offset: Annotated[int, Field(strict=True, ge=0, le=10000)]
    limit: Annotated[int, Field(strict=True, ge=1, le=100)]
    total: Annotated[int, Field(strict=True, ge=0)]


READ_CONTENT_TYPES = {
    kind: create_model(
        f"{kind.title()}ReadContent",
        __base__=Contract,
        **{
            name: (Annotated[field.annotation | None, *field.metadata], None)
            if field.metadata
            else (field.annotation | None, None)
            for name, field in model.model_fields.items()
        },
    )
    for kind, model in CONTENT_TYPES.items()
}
CREATE_TYPES = {kind: CreateCommand[model] for kind, model in CONTENT_TYPES.items()}
READ_TYPES = {
    kind: (ProfileReadEnvelope[model] if kind == "profile" else ReadEnvelope[model])
    for kind, model in READ_CONTENT_TYPES.items()
}
