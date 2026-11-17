"""Authorize metadata first and return a value-free projection specification."""

from dataclasses import dataclass
from typing import Protocol

from resume_core.service import Clearance, Principal, require


@dataclass(frozen=True)
class FieldPolicy:
    key: str
    privacy: str | None


@dataclass(frozen=True)
class SourcePolicy:
    reference_id: str
    source_id: str
    source_privacy: str
    reference_privacy: str
    field_key: str | None


@dataclass(frozen=True)
class LinkPolicy:
    id: str
    privacy: str
    from_privacy: str
    to_privacy: str
    field_key: str | None


class MetadataReader(Protocol):
    """Methods return metadata only; never field values, excerpts, or file names."""

    def entity_privacy(self, entity_id: str) -> str | None: ...
    def revision_privacy(self, entity_id: str, revision_id: str) -> str | None: ...
    def fields(self, entity_id: str, revision_id: str | None) -> tuple[FieldPolicy, ...]: ...
    def sources(self, entity_id: str, revision_id: str | None) -> tuple[SourcePolicy, ...]: ...
    def links(self, entity_id: str) -> tuple[LinkPolicy, ...]: ...


@dataclass(frozen=True)
class Projection:
    fields: frozenset[str]
    restricted_fields: frozenset[str]
    source_references: frozenset[tuple[str, str]]
    link_ids: frozenset[str]


def _visible(clearance: Clearance, *levels: str | None) -> bool:
    # Unknown classifications fail closed, even if a malformed row bypasses the DB constraints.
    try:
        return all(level is None or Clearance.parse(level) <= clearance for level in levels)
    except KeyError, AttributeError:
        return False


def authorize_projection(
    reader: MetadataReader,
    principal: Principal | None,
    entity_id: str,
    candidate_fields: frozenset[str],
    *,
    revision_id: str | None = None,
) -> Projection | None:
    """None deliberately covers both absent and invisible entities or revisions."""
    require(principal, "career:read")
    clearance = principal.clearance
    if not isinstance(clearance, Clearance):
        raise ValueError("Invalid clearance")
    entity_privacy = reader.entity_privacy(entity_id)
    if entity_privacy is None or not _visible(clearance, entity_privacy):
        return None
    revision_privacy = None
    if revision_id is not None:
        revision_privacy = reader.revision_privacy(entity_id, revision_id)
        if revision_privacy is None or not _visible(clearance, entity_privacy, revision_privacy):
            return None
    metadata = {field.key: field.privacy for field in reader.fields(entity_id, revision_id)}
    fields = frozenset(
        key
        for key in candidate_fields
        if _visible(clearance, entity_privacy, revision_privacy, metadata.get(key))
    )
    source_allowed = principal is not None and "source:read" in principal.capabilities
    sources = (
        frozenset(
            (source.reference_id, source.source_id)
            for source in reader.sources(entity_id, revision_id)
            if source_allowed
            and (source.field_key is None or source.field_key in fields)
            and _visible(
                clearance,
                entity_privacy,
                revision_privacy,
                source.source_privacy,
                source.reference_privacy,
            )
        )
        if source_allowed
        else frozenset()
    )
    links = (
        frozenset(
            link.id
            for link in reader.links(entity_id)
            if (link.field_key is None or link.field_key in fields)
            and _visible(
                clearance,
                entity_privacy,
                revision_privacy,
                link.privacy,
                link.from_privacy,
                link.to_privacy,
            )
        )
        if revision_id is None
        else frozenset()
    )
    return Projection(fields, candidate_fields - fields, sources, links)
