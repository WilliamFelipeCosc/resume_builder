"""SQL metadata projections used by policy; no private values are selected."""

from sqlalchemy import or_, select
from sqlalchemy.orm import aliased

from resume_core.career_kb.models import (
    Entity,
    FieldMetadata,
    Link,
    Provenance,
    Revision,
    RevisionField,
    RevisionProvenance,
    SourceDocument,
)
from resume_core.career_kb.policy import FieldPolicy, LinkPolicy, SourcePolicy


class SqlMetadataReader:
    def __init__(self, session):
        self.session = session

    def entity_privacy(self, entity_id):
        return self.session.scalar(select(Entity.privacy).where(Entity.id == entity_id))

    def revision_privacy(self, entity_id, revision_id):
        return self.session.scalar(
            select(Revision.privacy).where(
                Revision.entity_id == entity_id, Revision.id == revision_id
            )
        )

    def fields(self, entity_id, revision_id):
        if revision_id is None:
            statement = select(FieldMetadata.field_key, FieldMetadata.privacy).where(
                FieldMetadata.entity_id == entity_id
            )
        else:
            statement = select(RevisionField.field_key, RevisionField.privacy).where(
                RevisionField.revision_id == revision_id
            )
        return tuple(FieldPolicy(*row) for row in self.session.execute(statement))

    def sources(self, entity_id, revision_id):
        table = Provenance if revision_id is None else RevisionProvenance
        identity = (
            table.entity_id == entity_id
            if revision_id is None
            else table.revision_id == revision_id
        )
        statement = (
            select(
                table.id,
                table.source_document_id,
                SourceDocument.privacy,
                table.privacy,
                table.field_key,
            )
            .join(SourceDocument, SourceDocument.id == table.source_document_id)
            .where(identity)
        )
        return tuple(SourcePolicy(*row) for row in self.session.execute(statement))

    def links(self, entity_id):
        left = aliased(Entity)
        right = aliased(Entity)
        statement = (
            select(Link.id, Link.privacy, left.privacy, right.privacy, Link.field_key)
            .join(left, left.id == Link.from_entity_id)
            .join(right, right.id == Link.to_entity_id)
            .where(
                or_(Link.from_entity_id == entity_id, Link.to_entity_id == entity_id),
                Link.archived_at.is_(None),
            )
        )
        return tuple(LinkPolicy(*row) for row in self.session.execute(statement))
