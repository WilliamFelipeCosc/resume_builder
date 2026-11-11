# Contratos do Resume Builder

**Status:** especificações **conceituais**, NÃO um OpenAPI ou Pydantic package já instalado. Implementar em Python com Pydantic 2 na API, SQLAlchemy 2 no DB e gerar cliente TS via OpenAPI; validar por Pytest/Vitest. Os nomes de exemplo são candidatos e não afirmam endpoints em execução.

| Contrato | Arquivo | Uso principal |
|---|---|---|
| Career KB e staging | [career-kb.md](career-kb.md) | fontes/fatos/revisão |
| ResumeDocument/Revision | [resume-document.md](resume-document.md) | currículo semântico e layout |
| ChangeSet | [change-set.md](change-set.md) | propostas e aprovação parcial |
| JobSnapshot/Requirement | [job-intelligence.md](job-intelligence.md) | vaga e matching |
| ApplicationContext/Report | [application-context.md](application-context.md) | contexto autorizado e relatórios |
| MCP V1 | [mcp-tools.md](mcp-tools.md) | Tools/Resources/Prompts/transportes |
| REST/OpenAPI | [rest-openapi.md](rest-openapi.md) | fronteira FastAPI/TS |
| Eventos/jobs | [events.md](events.md) | audit/retries/idempotência |
| Modelos exemplo | [examples/models.py](examples/models.py) | validação conceitual Pydantic |

Em JSON/TypeScript, usar `camelCase` consistente; em Python, `snake_case`, `alias_generator` para serialização. Nunca permitir que dados `pending_review` sejam devolvidos como fatos confirmados. IDs do projeto e exemplos fictícios aqui não correspondem a dados reais.
