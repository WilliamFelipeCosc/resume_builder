# Arquitetura — Visão geral

**Status:** DECIDED conforme ADR-001…016; detalhes de implementação sujeitos a contrato e teste. Prioridade: primeira experiência utilizável em M3.

```text
[React/Vite/TypeScript] -- REST/OpenAPI --> [FastAPI / Services] -- SQLAlchemy --> [SQLite WAL]
           |                                    |                    |
  [Tauri Desktop na V1]                        |                    +--> [XDG Files]
                                                +--> [Redis] --> [Dramatiq Python Worker]
                                                +--> [Hermes / OpenAI explicit AI adapters]
                                                +--> [SQL + FTS5/BM25 Retrieval]
             [MCP Python stdio/HTTP] -- authorized services --^
                        ^
           [External Hermes/Codex/Claude/Kimi] --> [Browser externo e sites de vagas]
```

## Componentes

- **Web:** React, TypeScript, Vite. Formulários, Staging Area, preview, diff/approval, tracking. Cliente TS gerado de OpenAPI.
- **API:** FastAPI/Pydantic. Autorização por operação e serviço, validação em runtime, Application Services não acoplados aos adaptadores HTTP.
- **Core Python:** domain services sem FastAPI/transport; políticas de privacidade e proveniência em fronteiras de persistência, retrieval, IA e MCP.
- **Persistência:** SQLite local, WAL, SQLAlchemy 2, migrações Alembic serializadas, arquivos em XDG e backups consistentes.
- **Worker:** Dramatiq + Redis, jobs identificados e idempotentes; retries controlados e limites de recurso; resultados importantes sempre persistidos em SQLite (Redis não é fonte canônica).
- **MCP:** processo Python via `stdio` no M0.5 e Streamable HTTP antes do término da V1; chama serviços autenticados, sem SQL/shell genéricos e sem controle de navegador. Testes com dois clientes.
- **Renderer:** `ResumeDocument` estruturado + tokens de template; Playwright Python/Chromium **somente** para exportar PDF do HTML local; DOCX/HTML em M6.
- **IA:** providers explicitamente selecionados, Hermes padrão quando disponível, OpenAI manual, sem fallback automático pago. Prompt injection de vagas/documentos é tratado como entrada não confiável.

## Composição de pacotes (implementação incremental)

```text
apps/web/                       # React/Vite
apps/desktop/                   # Tauri no M7
backend/api/                   # FastAPI routers/adapters
backend/core/                  # domain + application services
backend/worker/                # Dramatiq
backend/mcp_server/            # stdio/HTTP MCP
backend/migrations/            # Alembic
packages/api-client/           # TS gerado de OpenAPI
assets/resume-templates/       # spec/CSS/templates
private/                       # dados pessoais locais (não versionados)
docs/                          # contratos, módulos, ADRs
PROJECT_OVERVIEW.md, AGENTS.md
pyproject.toml, uv.lock, pnpm-workspace.yaml, justfile # manifests e comandos do monorepo
```

O monorepo e seus comandos já existem; a árvore também inclui componentes planejados, como `apps/desktop/`. Consulte [estado dos marcos](../process/milestone-status.json) e `.specs/` para distinguir implementação e planejamento. Fontes documentais e precedência: [índice](../README.md).

## Fluxos críticos

1. Importação: source privado → parser → normalização → Staging Area `pending_review` → revisão → `CareerFact` confirmado/auditoria.
2. Currículo: facts permitidos → `ResumeDocument` → `ResumeRevision` → HTML renderizado → PDF validado.
3. Vaga: URL/texto/imagem → `JobSnapshot` → `JobRequirement[]` → matching explicável → `ChangeSet` → aprovação → PDF associado.
4. MCP: cliente externo autorizado → `ApplicationContextService` → evidências minimizadas → relato idempotente não confirmado de envio.

## Limites de transação

Commit SQLite com audit trail para revisão de fatos, revisões de currículo, ChangeSets e reports; manter vínculos/hash a arquivos sob disciplina de escrita atômica e recuperação. Locks/transactions para migrations e escritor único; não assumir que WAL permite vários escritores simultâneos. Jobs reexecutados não podem duplicar revisões ou sobrescrever aprovações.

## Observabilidade e segurança

`structlog` JSON, OTel/Jaeger opcionais, Sentry opt-in sanitizado, auditoria de domínio separada de log. Rede loopback e autenticação adequada; `Origin`/`Host`, CSRF aplicável, limitação de payload/rate limit e DNS rebinding. Segredos no keyring. Dados externos e prompts são não confiáveis.

## DoD do MVP

Ver `../roadmap/acceptance-criteria.md` — o M3 precisa de importação por URL/texto/screenshot com fallbacks, matching fundamentado, revisão, seleção visual/ATS, PDF versionado e privacidade testada. MCP completo e embeddings não são pré-requisitos de M3.
