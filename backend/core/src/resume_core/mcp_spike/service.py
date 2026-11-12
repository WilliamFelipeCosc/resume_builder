"""Transport-independent application services for synthetic MCP operations."""

from collections.abc import Callable

from resume_core.mcp_spike.contracts import ApplicationContext, ContextQuery
from resume_core.mcp_spike.policy import Profile, require


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
