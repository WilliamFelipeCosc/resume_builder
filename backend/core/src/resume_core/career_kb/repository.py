"""Transactional career writes and SQL-filtered historical fields."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, insert, literal, select, type_coerce, update

from resume_core.career_kb.entity_models import ENTITY_MODELS
from resume_core.career_kb.models import (
    AuditEvent,
    Entity,
    FieldMetadata,
    MutationReceipt,
    Provenance,
    Revision,
    RevisionField,
    RevisionProvenance,
)


class RevisionConflict(Exception):
    pass


class ReceiptConflict(Exception):
    pass


class CareerRepository:
    """Uses the caller's UoW; authorization and commit belong to the service."""

    def __init__(self, session):
        self.session = session

    def receipt(self, principal, operation, key, command_hash):
        row = self.session.execute(
            select(MutationReceipt.command_hash, MutationReceipt.result).where(
                MutationReceipt.principal == principal,
                MutationReceipt.operation == operation,
                MutationReceipt.idempotency_key == str(key),
            )
        ).one_or_none()
        if row is None:
            return None
        if row.command_hash != command_hash:
            raise ReceiptConflict
        return row.result

    def write(
        self,
        *,
        kind,
        content,
        entity_id,
        revision_id,
        profile_id,
        base_revision_id,
        privacy,
        field_privacy,
        source_id,
        source_sha256,
        principal,
        request_id,
        operation,
        key,
        command_hash,
        provenance_field=None,
        provenance_page=None,
        provenance_excerpt=None,
    ):
        now = datetime.now(UTC).isoformat()
        values = content.model_dump(mode="json", by_alias=False)
        table = ENTITY_MODELS[kind].__table__
        if base_revision_id is None:
            self.session.add(
                Entity(
                    id=entity_id,
                    kind=kind,
                    profile_id=profile_id,
                    head_revision_id=revision_id,
                    privacy=privacy,
                    created_at=now,
                    updated_at=now,
                )
            )
            self.session.flush()
            self.session.execute(insert(table).values(entity_id=entity_id, **values))
        else:
            result = self.session.execute(
                update(Entity)
                .where(
                    Entity.id == entity_id,
                    Entity.kind == kind,
                    Entity.head_revision_id == base_revision_id,
                )
                .values(head_revision_id=revision_id, updated_at=now, privacy=privacy)
            )
            if result.rowcount != 1:
                raise RevisionConflict
            result = self.session.execute(
                update(table).where(table.c.entity_id == entity_id).values(**values)
            )
            if result.rowcount != 1:
                raise RevisionConflict
        self.session.add(
            Revision(
                id=revision_id,
                entity_id=entity_id,
                parent_revision_id=base_revision_id,
                action="create" if base_revision_id is None else "update",
                responsible=principal,
                created_at=now,
                privacy=privacy,
                confirmation="unverified",
            )
        )
        self.session.flush()
        for name, value in values.items():
            level = field_privacy.get(name, privacy)
            confirmation = None
            if kind == "profile":
                confirmation = "unverified"
                if base_revision_id is not None:
                    previous = self.session.scalar(
                        select(RevisionField.confirmation).where(
                            RevisionField.revision_id == base_revision_id,
                            RevisionField.field_key == name,
                            RevisionField.value.is_(None)
                            if value is None
                            else RevisionField.value == type_coerce(value, JSON()),
                        )
                    )
                    if previous == "confirmed":
                        confirmation = previous
            self.session.add(
                RevisionField(
                    revision_id=revision_id,
                    field_key=name,
                    value=value,
                    privacy=level,
                    confirmation=confirmation,
                )
            )
            if base_revision_id is None:
                self.session.add(
                    FieldMetadata(
                        entity_id=entity_id,
                        field_key=name,
                        privacy=level,
                        confirmation=confirmation,
                    )
                )
            else:
                self.session.execute(
                    update(FieldMetadata)
                    .where(FieldMetadata.entity_id == entity_id, FieldMetadata.field_key == name)
                    .values(privacy=level, confirmation=confirmation)
                )
        provenance = dict(
            source_document_id=source_id,
            source_sha256=source_sha256,
            field_key=provenance_field,
            page=provenance_page,
            excerpt=provenance_excerpt,
            privacy=privacy,
        )
        self.session.add(Provenance(id=str(uuid4()), entity_id=entity_id, **provenance))
        self.session.flush()
        # Copy provenance inside SQL: private excerpts never enter application memory.
        source_rows = self.session.scalars(
            select(Provenance.id).where(Provenance.entity_id == entity_id)
        ).all()
        for provenance_id in source_rows:
            self.session.execute(
                insert(RevisionProvenance).from_select(
                    [
                        "id",
                        "revision_id",
                        "source_document_id",
                        "source_sha256",
                        "field_key",
                        "page",
                        "excerpt",
                        "privacy",
                    ],
                    select(
                        literal(str(uuid4())),
                        literal(revision_id),
                        Provenance.source_document_id,
                        Provenance.source_sha256,
                        Provenance.field_key,
                        Provenance.page,
                        Provenance.excerpt,
                        Provenance.privacy,
                    ).where(Provenance.id == provenance_id),
                )
            )
        self.session.add(
            AuditEvent(
                id=str(uuid4()),
                responsible=principal,
                action=operation,
                created_at=now,
                request_id=request_id,
                entity_id=entity_id,
                revision_id=revision_id,
                source_document_id=source_id,
            )
        )
        result = {"id": entity_id, "revisionId": revision_id}
        self.session.add(
            MutationReceipt(
                id=str(uuid4()),
                principal=principal,
                operation=operation,
                idempotency_key=str(key),
                command_hash=command_hash,
                result=result,
            )
        )
        self.session.flush()
        return result

    def snapshot(self, revision_id, permitted_fields):
        if not permitted_fields:
            return {}
        rows = self.session.execute(
            select(RevisionField.field_key, RevisionField.value).where(
                RevisionField.revision_id == revision_id,
                RevisionField.field_key.in_(permitted_fields),
            )
        )
        return dict(rows.all())
