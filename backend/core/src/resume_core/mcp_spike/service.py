"""Transport-independent application services for synthetic MCP operations."""

from collections.abc import Callable

from resume_core.mcp_spike.contracts import (
    ApplicationContext,
    ContextQuery,
    ProgressReport,
    Receipt,
)
from resume_core.mcp_spike.policy import Profile, require
from resume_core.mcp_spike.repository import Repository


class ContextNotFound(Exception):
    """The authorized synthetic application has no matching context."""


class ContextService:
    def __init__(self, load_context: Callable[[str], ApplicationContext | None]):
        self._load_context = load_context

    def get(self, principal: Profile | None, query: ContextQuery) -> ApplicationContext:
        require(principal, "application_context:read", query.application_id)
        context = self._load_context(query.application_id)
        if context is None or context.application_id != query.application_id:
            raise ContextNotFound
        return context


class ProgressService:
    def __init__(self, repository: Repository):
        self._repository = repository

    def report(self, principal: Profile | None, request: ProgressReport) -> Receipt:
        require(principal, "application_progress:write", request.application_id)
        assert principal is not None
        return self._repository.record(principal.client_id, request)
