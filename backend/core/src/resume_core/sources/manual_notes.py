"""Create private human-declared provenance with transactional receipts."""

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select

from resume_core.career_kb.models import AuditEvent, MutationReceipt, SourceDocument
from resume_core.persistence.unit_of_work import UnitOfWork
from resume_core.service import Clearance, PermissionDenied, require


class IdempotencyConflict(Exception):
    pass


class ManualNoteService:
    def __init__(self, engine, storage):
        self.engine, self.storage = engine, storage

    def create(self, principal, *, text: str, title: str | None, key: UUID, request_id: str):
        require(principal, "career:write")
        if principal.clearance < Clearance.CONFIDENTIAL:
            raise PermissionDenied("Operation is not permitted")
        command_hash = hashlib.sha256(
            json.dumps([text, title], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        with UnitOfWork(self.engine) as uow:
            receipt = uow.session.scalar(
                select(MutationReceipt).where(
                    MutationReceipt.principal == principal.subject,
                    MutationReceipt.operation == "source.manual_note.create",
                    MutationReceipt.idempotency_key == str(key),
                )
            )
            if receipt is not None:
                if receipt.command_hash != command_hash:
                    raise IdempotencyConflict
                require(principal, "source:read")
                source_id = receipt.result["sourceId"]
                visible = uow.session.scalar(
                    select(SourceDocument.id).where(
                        SourceDocument.id == source_id,
                        SourceDocument.privacy.in_(
                            ["public", "professional", "confidential"]
                            + (["secret"] if principal.clearance >= Clearance.SECRET else [])
                        ),
                    )
                )
                if visible is None:
                    raise PermissionDenied("Operation is not permitted")
                return source_id, False
            manifest = self.storage.install(text.encode("utf-8"))
            source_id = str(uuid4())
            uow.session.add(
                SourceDocument(
                    id=source_id,
                    kind="manual_note",
                    sha256=manifest.sha256,
                    private_name=title,
                    media_type="text/plain; charset=utf-8",
                    privacy="confidential",
                    storage_ref=manifest.storage_ref,
                )
            )
            uow.session.flush()
            uow.session.add(
                AuditEvent(
                    id=str(uuid4()),
                    responsible=principal.subject,
                    action="source.manual_note.create",
                    created_at=datetime.now(UTC).isoformat(),
                    request_id=request_id,
                    source_document_id=source_id,
                )
            )
            uow.session.add(
                MutationReceipt(
                    id=str(uuid4()),
                    principal=principal.subject,
                    operation="source.manual_note.create",
                    idempotency_key=str(key),
                    command_hash=command_hash,
                    result={"sourceId": source_id},
                )
            )
        return source_id, True
