"""Authorized SQL projections and bounded career pagination."""

from typing import Literal

from pydantic import Field, model_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from resume_core.career_kb.contracts import CONTENT_TYPES, READ_TYPES, Page
from resume_core.career_kb.entity_models import ENTITY_MODELS
from resume_core.career_kb.metadata_reader import SqlMetadataReader
from resume_core.career_kb.models import Entity, FieldMetadata, Revision, SourceDocument
from resume_core.career_kb.policy import authorize_projection
from resume_core.contracts import Contract
from resume_core.service import Clearance, require


class ResponseTooLarge(Exception):
    pass


class ListQuery(Contract):
    offset: int = Field(default=0, ge=0, le=10000, strict=True)
    limit: int = Field(default=25, ge=1, le=100, strict=True)
    sort: Literal["createdAt", "-createdAt"] = "createdAt"
    archived: bool | None = Field(default=None, strict=True)
    confirmation: Literal["confirmed", "unverified"] | None = None
    confirmation_field: (
        Literal[
            "fullName",
            "professionalHeadline",
            "email",
            "phoneOriginal",
            "objectiveOriginal",
            "cityOfResidence",
            "countryOfResidence",
            "linkedinUrl",
            "githubUrl",
        ]
        | None
    ) = None

    @model_validator(mode="after")
    def field_requires_confirmation(self):
        if self.confirmation_field is not None and self.confirmation is None:
            raise ValueError("confirmation field requires confirmation")
        return self


class CareerQueries:
    def __init__(self, engine):
        self.engine = engine

    @staticmethod
    def _levels(principal):
        return [level.name.lower() for level in Clearance if level <= principal.clearance]

    @staticmethod
    def _budget(result):
        if len(result.model_dump_json(by_alias=True).encode("utf-8")) > 1024 * 1024:
            raise ResponseTooLarge
        return result

    def _detail(self, session, principal, kind, entity_id):
        table = ENTITY_MODELS[kind].__table__
        levels = self._levels(principal)
        meta = session.execute(
            select(Entity.id, Entity.head_revision_id, Entity.privacy, Revision.confirmation)
            .join(table, table.c.entity_id == Entity.id)
            .join(Revision, Revision.id == Entity.head_revision_id)
            .where(
                Entity.id == entity_id,
                Entity.kind == kind,
                Entity.privacy.in_(levels),
                Revision.entity_id == Entity.id,
                Revision.privacy.in_(levels),
            )
        ).one_or_none()
        if meta is None:
            return None
        fields = CONTENT_TYPES[kind].model_fields
        projection = authorize_projection(
            SqlMetadataReader(session), principal, entity_id, frozenset(fields)
        )
        if projection is None:
            return None
        allowed = set(projection.fields)
        if kind == "evidence":
            source_fields = {"source_document_id", "page", "excerpt"}
            if "source:read" not in principal.capabilities:
                allowed -= source_fields
            else:
                source_privacy = session.scalar(
                    select(SourceDocument.privacy)
                    .join(table, table.c.source_document_id == SourceDocument.id)
                    .where(table.c.entity_id == entity_id)
                )
                if source_privacy not in levels:
                    allowed -= source_fields
        selected = [table.c[name] for name in fields if name in allowed]
        values = dict.fromkeys(fields)
        if selected:
            row = (
                session.execute(select(*selected).where(table.c.entity_id == entity_id))
                .mappings()
                .one()
            )
            values.update(row)
        aliases = {name: field.alias for name, field in fields.items()}
        payload = {
            "id": meta.id,
            "revisionId": meta.head_revision_id,
            "content": values,
            "privacy": meta.privacy,
            "restrictedFields": [aliases[name] for name in fields if name not in allowed],
        }
        if kind == "profile":
            states = (
                session.execute(
                    select(FieldMetadata.field_key, FieldMetadata.confirmation).where(
                        FieldMetadata.entity_id == entity_id,
                        FieldMetadata.field_key.in_(allowed),
                        FieldMetadata.confirmation.is_not(None),
                    )
                ).all()
                if allowed
                else []
            )
            payload["fieldConfirmations"] = {aliases[name]: state for name, state in states}
        else:
            payload["confirmation"] = meta.confirmation
        return READ_TYPES[kind].model_validate(payload)

    def detail(self, principal, kind, entity_id):
        require(principal, "career:read")
        if kind not in CONTENT_TYPES:
            raise ValueError("invalid career kind")
        with self.engine.connect() as connection:
            connection.exec_driver_sql("BEGIN")
            with Session(connection) as session:
                result = self._detail(session, principal, kind, str(entity_id))
                return self._budget(result) if result is not None else None

    def list(self, principal, kind, query: ListQuery):
        require(principal, "career:read")
        if kind not in CONTENT_TYPES:
            raise ValueError("invalid career kind")
        if (
            kind == "profile"
            and query.confirmation is not None
            and query.confirmation_field is None
        ):
            raise ValueError("profile confirmation filter requires a field")
        if kind != "profile" and query.confirmation_field is not None:
            raise ValueError("confirmation field only applies to profile")
        table = ENTITY_MODELS[kind].__table__
        levels = self._levels(principal)
        with self.engine.connect() as connection:
            connection.exec_driver_sql("BEGIN")
            with Session(connection) as session:
                base = (
                    select(Entity.id)
                    .join(table, table.c.entity_id == Entity.id)
                    .join(Revision, Revision.id == Entity.head_revision_id)
                    .where(
                        Entity.kind == kind,
                        Entity.privacy.in_(levels),
                        Revision.entity_id == Entity.id,
                        Revision.privacy.in_(levels),
                    )
                )
                if query.archived is not None:
                    base = base.where(
                        Entity.archived_at.is_not(None)
                        if query.archived
                        else Entity.archived_at.is_(None)
                    )
                if query.confirmation is not None:
                    if kind == "profile":
                        aliases = {
                            field.alias: name
                            for name, field in CONTENT_TYPES["profile"].model_fields.items()
                        }
                        field_key = aliases[query.confirmation_field]
                        base = base.join(FieldMetadata, FieldMetadata.entity_id == Entity.id).where(
                            FieldMetadata.field_key == field_key,
                            FieldMetadata.confirmation == query.confirmation,
                            or_(FieldMetadata.privacy.is_(None), FieldMetadata.privacy.in_(levels)),
                        )
                    else:
                        base = base.where(Revision.confirmation == query.confirmation)
                total = session.scalar(select(func.count()).select_from(base.subquery()))
                ordering = (
                    (Entity.created_at.desc(), Entity.id.desc())
                    if query.sort == "-createdAt"
                    else (Entity.created_at, Entity.id)
                )
                ids = session.scalars(
                    base.order_by(*ordering).offset(query.offset).limit(query.limit)
                ).all()
                items = [self._detail(session, principal, kind, entity_id) for entity_id in ids]
                page = Page[READ_TYPES[kind]](
                    items=items, offset=query.offset, limit=query.limit, total=total
                )
                return self._budget(page)
