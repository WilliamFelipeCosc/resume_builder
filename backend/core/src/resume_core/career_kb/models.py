"""Typed persistence envelope; career content tables are added separately."""

from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


PRIVACY = "privacy IN ('public','professional','confidential','secret')"
KINDS = "kind IN ('profile','experience','statement','project','achievement','skill','education','language','evidence')"


class Entity(Base):
    __tablename__ = "kb_entities"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    profile_id: Mapped[str | None] = mapped_column(ForeignKey("kb_entities.id"))
    head_revision_id: Mapped[str | None] = mapped_column(String)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    archived_at: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        CheckConstraint(KINDS, name="ck_kb_entities_kind"),
        CheckConstraint(PRIVACY, name="ck_kb_entities_privacy"),
        ForeignKeyConstraint(
            ["head_revision_id", "id"],
            ["kb_revisions.id", "kb_revisions.entity_id"],
            name="fk_entity_head",
            deferrable=True,
            initially="DEFERRED",
        ),
    )


class SourceDocument(Base):
    __tablename__ = "source_documents"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False)
    private_name: Mapped[str | None] = mapped_column(String)
    media_type: Mapped[str | None] = mapped_column(String)
    page_count: Mapped[int | None]
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    storage_ref: Mapped[str | None] = mapped_column(String)
    __table_args__ = (
        CheckConstraint("kind IN ('file','manual_note')", name="ck_source_kind"),
        CheckConstraint(PRIVACY, name="ck_source_privacy"),
        CheckConstraint("page_count IS NULL OR page_count > 0", name="ck_source_pages"),
    )


class Revision(Base):
    __tablename__ = "kb_revisions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), nullable=False)
    parent_revision_id: Mapped[str | None] = mapped_column(String)
    action: Mapped[str] = mapped_column(String, nullable=False)
    responsible: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    confirmation: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint("id", "entity_id", name="uq_revision_entity"),
        ForeignKeyConstraint(
            ["parent_revision_id", "entity_id"],
            ["kb_revisions.id", "kb_revisions.entity_id"],
            name="fk_revision_parent",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint(PRIVACY, name="ck_revision_privacy"),
        CheckConstraint(
            "confirmation IN ('confirmed','unverified')", name="ck_revision_confirmation"
        ),
    )


class FieldMetadata(Base):
    __tablename__ = "kb_field_metadata"
    entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), primary_key=True)
    field_key: Mapped[str] = mapped_column(String, primary_key=True)
    privacy: Mapped[str | None] = mapped_column(String)
    confirmation: Mapped[str | None] = mapped_column(String)
    __table_args__ = (
        CheckConstraint("privacy IS NULL OR " + PRIVACY, name="ck_field_privacy"),
        CheckConstraint(
            "confirmation IS NULL OR confirmation IN ('confirmed','unverified')",
            name="ck_field_confirmation",
        ),
    )


class RevisionField(Base):
    __tablename__ = "kb_revision_fields"
    revision_id: Mapped[str] = mapped_column(ForeignKey("kb_revisions.id"), primary_key=True)
    field_key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[Any] = mapped_column(JSON(none_as_null=True), nullable=True)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    confirmation: Mapped[str | None] = mapped_column(String)
    __table_args__ = (
        CheckConstraint(PRIVACY, name="ck_revision_field_privacy"),
        CheckConstraint(
            "confirmation IS NULL OR confirmation IN ('confirmed','unverified')",
            name="ck_revision_field_confirmation",
        ),
    )


class Provenance(Base):
    __tablename__ = "kb_provenance"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), nullable=False)
    source_document_id: Mapped[str] = mapped_column(
        ForeignKey("source_documents.id"), nullable=False
    )
    source_sha256: Mapped[str] = mapped_column(String, nullable=False)
    field_key: Mapped[str | None] = mapped_column(String)
    page: Mapped[int | None]
    excerpt: Mapped[str | None] = mapped_column(String)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        CheckConstraint(PRIVACY, name="ck_provenance_privacy"),
        CheckConstraint("page IS NULL OR page > 0", name="ck_provenance_page"),
    )


class RevisionProvenance(Base):
    __tablename__ = "kb_revision_provenance"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    revision_id: Mapped[str] = mapped_column(ForeignKey("kb_revisions.id"), nullable=False)
    source_document_id: Mapped[str] = mapped_column(
        ForeignKey("source_documents.id"), nullable=False
    )
    source_sha256: Mapped[str] = mapped_column(String, nullable=False)
    field_key: Mapped[str | None] = mapped_column(String)
    page: Mapped[int | None]
    excerpt: Mapped[str | None] = mapped_column(String)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        CheckConstraint(PRIVACY, name="ck_revision_provenance_privacy"),
        CheckConstraint("page IS NULL OR page > 0", name="ck_revision_provenance_page"),
    )


class Link(Base):
    __tablename__ = "kb_links"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    from_entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), nullable=False)
    to_entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), nullable=False)
    field_key: Mapped[str | None] = mapped_column(String)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    revision_id: Mapped[str] = mapped_column(String, nullable=False)
    archived_at: Mapped[str | None] = mapped_column(String)
    __table_args__ = (
        ForeignKeyConstraint(
            ["revision_id", "id"],
            ["kb_link_revisions.id", "kb_link_revisions.link_id"],
            name="fk_link_head",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint(PRIVACY, name="ck_link_privacy"),
        CheckConstraint("from_entity_id != to_entity_id", name="ck_link_distinct"),
        Index(
            "uq_active_link",
            "kind",
            "from_entity_id",
            "to_entity_id",
            text("coalesce(field_key, '')"),
            unique=True,
            sqlite_where=text("archived_at IS NULL"),
        ),
    )


class LinkRevision(Base):
    __tablename__ = "kb_link_revisions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    link_id: Mapped[str] = mapped_column(ForeignKey("kb_links.id"), nullable=False)
    parent_revision_id: Mapped[str | None] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    from_entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), nullable=False)
    to_entity_id: Mapped[str] = mapped_column(ForeignKey("kb_entities.id"), nullable=False)
    field_key: Mapped[str | None] = mapped_column(String)
    archived_at: Mapped[str | None] = mapped_column(String)
    responsible: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint("id", "link_id", name="uq_link_revision_link"),
        ForeignKeyConstraint(
            ["parent_revision_id", "link_id"],
            ["kb_link_revisions.id", "kb_link_revisions.link_id"],
            name="fk_link_revision_parent",
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint(PRIVACY, name="ck_link_revision_privacy"),
    )


class LinkRevisionProvenance(Base):
    __tablename__ = "kb_link_revision_provenance"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    link_revision_id: Mapped[str] = mapped_column(
        ForeignKey("kb_link_revisions.id"), nullable=False
    )
    source_document_id: Mapped[str] = mapped_column(
        ForeignKey("source_documents.id"), nullable=False
    )
    source_sha256: Mapped[str] = mapped_column(String, nullable=False)
    page: Mapped[int | None]
    excerpt: Mapped[str | None] = mapped_column(String)
    privacy: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (
        CheckConstraint(PRIVACY, name="ck_link_revision_provenance_privacy"),
        CheckConstraint("page IS NULL OR page > 0", name="ck_link_revision_provenance_page"),
    )


class AuditEvent(Base):
    __tablename__ = "kb_audit_events"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    responsible: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    request_id: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[str | None] = mapped_column(ForeignKey("kb_entities.id"))
    revision_id: Mapped[str | None] = mapped_column(ForeignKey("kb_revisions.id"))
    source_document_id: Mapped[str | None] = mapped_column(ForeignKey("source_documents.id"))


class MutationReceipt(Base):
    __tablename__ = "mutation_receipts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    principal: Mapped[str] = mapped_column(String, nullable=False)
    operation: Mapped[str] = mapped_column(String, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False)
    command_hash: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[Any] = mapped_column(JSON, nullable=False)
    __table_args__ = (
        UniqueConstraint("principal", "operation", "idempotency_key", name="uq_receipt_scope"),
    )
