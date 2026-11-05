# Arquitetura de software

## Estilo e fronteiras (DECIDED)

Monólito modular em NestJS, React/Vite no browser, Worker Node separado com BullMQ/Redis, SQLite/Drizzle e filesystem local. Tauri reutiliza a mesma interface React; MCP Server independente como entrada externa para Application Services. Sem orquestração de navegador no backend.

```text
Web/Tauri --> API/Services --> DB/Filesystem
                        \--> Redis/BullMQ --> Worker --> AI/Document adapters
CLI agents --> MCP stdio/HTTP --> Authorized Application Services --> DB/AI/KB
CLI agents --> browser controlled independently of Resume Builder
```

## Fronteiras internas

- **Domain:** entidades, invariantes, políticas; não importa SDK de LLM/browser.
- **Application Services:** orquestram casos de uso, UoW/transações, permissões, auditoria.
- **Adapters:** SQLite, Redis, filesystem, Hermes, OpenAI, formatadores, extractors, MCP transports.
- **API:** REST + SSE para eventos relevantes; validação, autenticação local e observabilidade.
- **MCP:** mapeia Tools/Resources/Prompts para Application Services com escopo; não implementa lógica de negócio duplicada.
- **Worker:** ingestão, geração de documentos, matching/IA e tarefas; retries condicionados a idempotência e status.

## Pacotes iniciais propostos (PROPOSED)

```text
apps/web/ apps/api/ apps/worker/ apps/mcp-server/ apps/desktop/
packages/domain/ packages/contracts/ packages/database/
packages/ai/ packages/career-kb/ packages/resumes/
packages/job-intelligence/ packages/application-context/
packages/application-answers/ packages/mcp-contracts/
packages/documents/ packages/ui/ packages/config/
infra/compose.yaml tests/fixtures/ tests/ai-evals/
```

Não criar pacotes vazios sem consumidores reais. O objetivo é reduzir acoplamento, não maximizar quantidade de packages. Dependências: `domain` sem imports de infra; adapters dependem de portas; UI chama API; MCP chama cases de aplicação.

## Concorrência e confiabilidade

API/Worker compartilham SQLite no mesmo host (WAL, busy timeout e transações curtas). Redis executa filas, **não** substitui o banco como estado canônico. Persistir `WorkItem`/eventos de domínio para reconciliar tarefas após reboot/restore. Retries só em ações seguras ou idempotentes. Uma candidatura externa nunca é automaticamente reenviada pelo aplicativo.

## Decisões de integração

Hermes pode representar duas integrações separadas: (1) provider para tarefas de IA **internas**; (2) **agente CLI externo** cliente MCP. Não confundir capacidades, autenticação, custos ou permissões. A API OpenAI é alternativa **manual**, não fallback silencioso.

Consulte [ADR-004](adr/0004-mcp-external-execution.md) e [MCP](../modules/mcp-server.md).
