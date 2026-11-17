"""Source metadata and attachment endpoints."""

import asyncio
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import Response
from pydantic import BaseModel
from resume_core.service import PermissionDenied
from resume_core.sources.storage import SourceIntegrityError

from resume_api.errors import error_response

router = APIRouter()


class SourceResponse(BaseModel):
    id: UUID
    kind: Literal["file", "manual_note"]
    sha256: str
    title: str | None
    mediaType: str | None
    pageCount: int | None
    privacy: Literal["public", "professional", "confidential", "secret"]


@router.get(
    "/api/sources/{source_id}",
    response_model=SourceResponse,
    operation_id="get_source",
    openapi_extra={"security": [{"LocalSession": []}]},
)
async def get_source(source_id: UUID, request: Request):
    try:
        item = await asyncio.to_thread(
            request.app.state.source_queries.metadata, request.state.principal, str(source_id)
        )
    except PermissionDenied:
        return error_response(403, request.state.request_id, code="forbidden")
    if item is None:
        return error_response(404, request.state.request_id)
    return SourceResponse(
        id=item.id,
        kind=item.kind,
        sha256=item.sha256,
        title=item.title,
        mediaType=item.media_type,
        pageCount=item.page_count,
        privacy=item.privacy,
    )


@router.get(
    "/api/sources/{source_id}/content",
    response_class=Response,
    responses={
        200: {
            "content": {
                "application/octet-stream": {"schema": {"type": "string", "format": "binary"}}
            }
        }
    },
    operation_id="download_source",
    openapi_extra={"security": [{"LocalSession": []}]},
)
async def download_source(source_id: UUID, request: Request):
    try:
        result = await asyncio.to_thread(
            request.app.state.source_queries.content, request.state.principal, str(source_id)
        )
    except PermissionDenied:
        return error_response(403, request.state.request_id, code="forbidden")
    except SourceIntegrityError, OSError:
        return error_response(503, request.state.request_id)
    if result is None:
        return error_response(404, request.state.request_id)
    item, content = result
    filename = "source.pdf" if item.media_type == "application/pdf" else "source.txt"
    return Response(
        content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
