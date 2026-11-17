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
- **Phase / Task**: execução autorizada em 2026-11-16 às 20:17 (-03), retomada em 2026-11-17; fases 1–3 concluídas, T1–T21 (21/64); estado canônico in_progress.
- **Completed**: CI/dependências/UI básica, fronteiras e integridade, armazenamento/PDF limitado, fonte manual privada e consultas/download autorizados. Contrato manual aprovado em 2026-11-17 às 08:56 (-03). Commits até `68fcbd0`.
- **Gates**: último BUILD completo T17: 509 Python (2 avisos de depreciação existentes), 19 Vitest, 4 Playwright e typecheck/build/contrato/lint PASS. Evidência em `.specs/features/m1-career-kb/execution.md`.
- **In-progress**: nenhum; T21 concluída.
- **Next step**: executar T22–T23 e encerrar fase 4 com BUILD; sem push.
- **Blockers**: nenhuma decisão de T18 pendente; aceite privado continua humano após piloto independente; CI remoto não autorizado.
- **Branch**: feature/m1-career-kb, base d2a609d.

Operação: docs/engineering/m0-local-operation.md; just setup, just build, just redis-up (manual), just migrate, just api, just worker e just open. XDG_RUNTIME_DIR privado obrigatório; dados profissionais/providers/MCP/CI não utilizados. Testes: PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check, Docker e Chromium necessários. Evidências detalhadas e limites em .specs/features/m0-foundation/validation.md.
