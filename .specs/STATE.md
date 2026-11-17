# STATE

## Decisions

ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais
à feature. A escolha FastMCP aprovada no M0.5 está registrada em AD-001/ADR-016.

### AD-001
- **Decision**: Usar FastMCP independente como adapter MCP, chamando Application Services Python compartilháveis; stdio no M0.5 e integração HTTP com FastAPI no M4.
- **Reason**: Escolha explícita do proprietário e desenho consolidado aprovado; manter o spike independente da API e preservar evolução para HTTP.
- **Trade-off**: Dependências adicionais do framework e concessão local própria no processo stdio, em lugar de mediação REST interna.
- **Scope**: MCP e integração futura com FastAPI; ADR-016 complementa ADRs 004/005 sem alterar seus limites.
- **Date**: 2026-11-12
- **Status**: active

### AD-002
- **Decision**: Organizar o frontend por funcionalidades (Feature-based), com componentes genéricos compartilhados; usar Tailwind com tokens padrão, shadcn/ui, TanStack Query sobre SDK OpenAPI gerado, React Hook Form e React Router Data Mode como SPA no Vite.
- **Reason**: Escolhas explícitas do proprietário na entrevista M1 de 2026-11-16; definir convenções antes de implementar várias telas.
- **Trade-off**: Novas dependências e código de componentes sob manutenção do projeto; exigir spike de compatibilidade com os pins atuais e separação entre estado da API, rascunhos e UI.
- **Scope**: Frontend de aplicação a partir do M1; estado de UI local inicialmente, sem store global; não define estilos do renderer de currículo nem editor avançado M6.
- **Date**: 2026-11-16
- **Status**: active; decisões aprovadas, implementação NOT_RUN.

## Handoff

- **Feature**: m1-career-kb — execução do Career KB Core.
- **Phase / Task**: snapshot 2026-11-17 às 10:22 (-03); T1–T22 concluídas (22/64), T23 parcialmente implementada e sem commit; M1 in_progress. Handoff detalhado: `.specs/features/m1-career-kb/handoff.md`.
- **Completed**: fases 1–3; contratos/tabelas tipadas, repositório, criação e consultas autorizadas de T18–T22; correções de leitura/proveniência/CHECKs. Último commit de implementação `ac94851`. Decisões manuais T16/T18/T22 aprovadas e documentadas; sem nova entrevista para essas escolhas.
- **Gates**: último BUILD confirmado anterior aos CHECKs finais: 575 Python, 19 Vitest, 4 Playwright e checks PASS; pós-CHECKs, worker informou gate HTTP/PY 141 passed, 435 deselected e lint PASS. BUILD final após `ac94851` iniciado, resultado não confirmado devido à quota. Não declarar fase 4 verde sem repetir.
- **In-progress** (file:line): `backend/api/src/resume_api/routers/career.py:28` (27 rotas concretas); `tests/integration/test_m1_t23.py:72` e coartefatos de SDK/composição, não commitados.
- **Next step**: reconciliar diff de T23, repetir HTTP/BUILD na árvore final, registrar adequação/status/traceabilidade e commit local; só depois despachar Terra para T24–T28. Preservar preferência GPT Terra e lotes sequenciais.
- **Blockers**: worker Terra atingiu limite de uso; nenhum resultado final do último BUILD. Sem decisão de negócio pendente. Piloto independente, revisão privada humana e aceite final ainda futuros; CI remoto NOT_RUN e push não autorizado.
- **Uncommitted files**: T23 em `backend/api/src/resume_api/{__main__,app,errors}.py`, `backend/api/src/resume_api/routers/career.py`, `backend/core/src/resume_core/logging_policy.py`, `packages/api-client/openapi.json`, `packages/api-client/src/generated/{index,sdk.gen,types.gen}.ts`, `tests/integration/test_m1_t23.py`; lista exata e contexto em handoff.md. Documentos deste handoff são adicionais a essa captura.
- **Branch**: feature/m1-career-kb, base d2a609d; conferir git antes de retomar. Ambiente atual full access/approval never: não enviar sandbox_permissions; isso não autoriza operações remotas ou dados reais.

Operação e comandos: handoff.md e docs/engineering/m0-local-operation.md; PATH Node 24 e PLAYWRIGHT_BROWSERS_PATH explícitos. Dados fictícios; não carregar fontes pessoais antes do piloto independente e revisão humana.
