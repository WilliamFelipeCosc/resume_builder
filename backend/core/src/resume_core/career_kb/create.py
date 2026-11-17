"""Authorize and create source-grounded, unverified career facts."""

import hashlib
import json
from uuid import uuid4

from sqlalchemy import select

from resume_core.career_kb.contracts import CONTENT_TYPES, LEVELS
from resume_core.career_kb.entity_models import ENTITY_MODELS
from resume_core.career_kb.models import (
    Entity,
    Provenance,
    Revision,
    RevisionProvenance,
    SourceDocument,
)
from resume_core.career_kb.repository import CareerRepository
from resume_core.persistence.unit_of_work import UnitOfWork
from resume_core.service import Clearance, PermissionDenied, require


class ReferenceNotFound(Exception):
    """Absent and inaccessible references are intentionally indistinguishable."""


class InvalidEvidence(Exception):
    """Evidence contradicts its authorized source metadata."""


class CareerCreateService:
    def __init__(self, engine):
        self.engine = engine

    def create(self, principal, kind, command, *, request_id):
        require(principal, "career:write")
        require(principal, "source:read")
        if kind not in CONTENT_TYPES or not isinstance(command.content, CONTENT_TYPES[kind]):
            raise ValueError("invalid career kind")
        if not isinstance(principal.clearance, Clearance):
            raise PermissionDenied("Operation is not permitted")
        if any(
            LEVELS.index(level) > principal.clearance
            for level in (command.privacy, *command.field_privacy.values())
        ):
            raise PermissionDenied("Operation is not permitted")
        levels = [level.name.lower() for level in Clearance if level <= principal.clearance]
        command_json = command.model_dump(mode="json", by_alias=True)
        command_hash = hashlib.sha256(
            json.dumps(
                command_json, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        operation = f"career.{kind}.create"
        with UnitOfWork(self.engine) as work:
            session = work.session
            source = session.execute(
                select(
                    SourceDocument.id,
                    SourceDocument.sha256,
                    SourceDocument.privacy,
                    SourceDocument.kind,
                    SourceDocument.page_count,
                ).where(
                    SourceDocument.id == str(command.source_document_id),
                    SourceDocument.privacy.in_(levels),
                )
            ).one_or_none()
            if source is None:
                raise ReferenceNotFound
            evidence_source = source
            if (
                kind == "evidence"
                and command.content.source_document_id != command.source_document_id
            ):
                evidence_source = session.execute(
                    select(
                        SourceDocument.id,
                        SourceDocument.sha256,
                        SourceDocument.privacy,
                        SourceDocument.kind,
                        SourceDocument.page_count,
                    ).where(
                        SourceDocument.id == str(command.content.source_document_id),
                        SourceDocument.privacy.in_(levels),
                    )
                ).one_or_none()
                if evidence_source is None:
                    raise ReferenceNotFound
            if kind == "evidence":
                expected = "manual_note" if evidence_source.kind == "manual_note" else "documentary"
                page = command.content.page
                if command.content.evidence_kind != expected or (
                    page is not None
                    and (evidence_source.page_count is None or page > evidence_source.page_count)
                ):
                    raise InvalidEvidence
            if command.profile_id is not None:
                profile = ENTITY_MODELS["profile"].__table__
                exists = session.scalar(
                    select(Entity.id)
                    .join(profile, profile.c.entity_id == Entity.id)
                    .where(
                        Entity.id == str(command.profile_id),
                        Entity.kind == "profile",
                        Entity.privacy.in_(levels),
                        Entity.head_revision_id.is_not(None),
                    )
                )
                if exists is None:
                    raise ReferenceNotFound
            repo = CareerRepository(session)
            replay = repo.receipt(
                principal.subject, operation, command.idempotency_key, command_hash
            )
            if replay is not None:
                table = ENTITY_MODELS[kind].__table__
                row = session.scalar(
                    select(Entity.id)
                    .join(table, table.c.entity_id == Entity.id)
                    .join(Revision, Revision.entity_id == Entity.id)
                    .where(
                        Entity.id == replay["id"],
                        Entity.kind == kind,
                        Entity.privacy.in_(levels),
                        Entity.head_revision_id.is_not(None),
                        Revision.id == replay["revisionId"],
                        Revision.privacy.in_(levels),
                    )
                )
                if row is None:
                    raise ReferenceNotFound
                return replay, False
            aliases = {
                field.alias: name for name, field in type(command.content).model_fields.items()
            }
            field_privacy = {aliases[key]: value for key, value in command.field_privacy.items()}
            if kind == "evidence":
                for field in ("source_document_id", "page", "excerpt"):
                    current = field_privacy.get(field, command.privacy)
                    field_privacy[field] = LEVELS[
                        max(LEVELS.index(current), LEVELS.index(evidence_source.privacy))
                    ]
            result = repo.write(
                kind=kind,
                content=command.content,
                entity_id=str(uuid4()),
                revision_id=str(uuid4()),
                profile_id=str(command.profile_id) if command.profile_id else None,
                base_revision_id=None,
                privacy=command.privacy,
                field_privacy=field_privacy,
                source_id=source.id,
                source_sha256=source.sha256,
                principal=principal.subject,
                request_id=request_id,
                operation=operation,
                key=command.idempotency_key,
                command_hash=command_hash,
            )
            if kind == "evidence":
                provenance = dict(
                    source_document_id=evidence_source.id,
                    source_sha256=evidence_source.sha256,
                    field_key="excerpt",
                    page=command.content.page,
                    excerpt=command.content.excerpt,
                    privacy=field_privacy["excerpt"],
                )
                session.add(Provenance(id=str(uuid4()), entity_id=result["id"], **provenance))
                session.add(
                    RevisionProvenance(
                        id=str(uuid4()), revision_id=result["revisionId"], **provenance
                    )
                )
        return result, True
