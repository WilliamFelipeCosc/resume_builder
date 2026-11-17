# Contratos do Resume Builder

**Status:** este diretório contém contratos conceituais e propostas identificadas, não a lista completa de endpoints implementados. A API já possui schemas executáveis Pydantic/OpenAPI e cliente TS gerado em `packages/api-client/`; consulte as specs/evidências da feature para o recorte entregue. Exemplos candidatos não comprovam implementação. Mudanças de contrato passam por Python, geração do SDK e testes de compatibilidade.

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
