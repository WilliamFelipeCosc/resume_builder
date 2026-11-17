"""Authorized source metadata and integrity-checked content."""

from dataclasses import dataclass

from sqlalchemy import select

from resume_core.career_kb.models import SourceDocument
from resume_core.service import Clearance, require


@dataclass(frozen=True)
class SourceMetadata:
    id: str
    kind: str
    sha256: str
    title: str | None
    media_type: str | None
    page_count: int | None
    privacy: str
    storage_ref: str | None


class SourceQueries:
    def __init__(self, engine, storage):
        self.engine, self.storage = engine, storage

    def metadata(self, principal, source_id: str) -> SourceMetadata | None:
        require(principal, "source:read")
        levels = [level.name.lower() for level in Clearance if level <= principal.clearance]
        with self.engine.connect() as connection:
            row = connection.execute(
                select(
                    SourceDocument.id,
                    SourceDocument.kind,
                    SourceDocument.sha256,
                    SourceDocument.private_name,
                    SourceDocument.media_type,
                    SourceDocument.page_count,
                    SourceDocument.privacy,
                    SourceDocument.storage_ref,
                ).where(SourceDocument.id == source_id, SourceDocument.privacy.in_(levels))
            ).one_or_none()
        return SourceMetadata(*row) if row is not None else None

    def content(self, principal, source_id: str) -> tuple[SourceMetadata, bytes] | None:
        metadata = self.metadata(principal, source_id)
        if metadata is None:
            return None
        if metadata.storage_ref is None or metadata.storage_ref != metadata.sha256:
            from resume_core.sources.storage import SourceIntegrityError

            raise SourceIntegrityError("source unavailable")
        return metadata, self.storage.read(metadata.storage_ref)
