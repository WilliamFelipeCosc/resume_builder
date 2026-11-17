"""Private manual source creation."""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from resume_core.persistence.unit_of_work import DatabaseBusy
from resume_core.service import PermissionDenied
from resume_core.sources.manual_notes import IdempotencyConflict
from resume_core.sources.storage import SourceIntegrityError

from resume_api.errors import error_response

router = APIRouter()


class ManualNoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=8000, strict=True)
    title: str | None = Field(default=None, max_length=256, strict=True)
    idempotencyKey: UUID


class ManualNoteResponse(BaseModel):
    sourceId: UUID


@router.post(
    "/api/sources/manual-notes",
    response_model=ManualNoteResponse,
    status_code=201,
    responses={200: {"model": ManualNoteResponse}},
    operation_id="create_manual_note",
    openapi_extra={"security": [{"LocalSession": []}]},
)
async def create_manual_note(body: ManualNoteCreate, request: Request):
    try:
        source_id, created = await asyncio.to_thread(
            request.app.state.source_service.create,
            request.state.principal,
            text=body.text,
            title=body.title,
            key=body.idempotencyKey,
            request_id=request.state.request_id,
        )
    except PermissionDenied:
        return error_response(403, request.state.request_id, code="forbidden")
    except IdempotencyConflict:
        return error_response(409, request.state.request_id, code="idempotency_conflict")
    except DatabaseBusy:
        return error_response(503, request.state.request_id, code="database_busy")
    except SourceIntegrityError, OSError:
        return error_response(503, request.state.request_id)
    return JSONResponse({"sourceId": source_id}, status_code=201 if created else 200)
