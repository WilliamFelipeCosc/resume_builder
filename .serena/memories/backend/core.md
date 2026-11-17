# Backend
- backend/core contém domínio, serviços, autorização e persistência; adapters api, worker e mcp_server são separados. Leia backend/AGENTS.md e guias descendentes.
- MCP chama serviços autorizados, sem acesso indiscriminado a SQLite; modelos de fronteira Pydantic e persistência SQLAlchemy/Alembic.
