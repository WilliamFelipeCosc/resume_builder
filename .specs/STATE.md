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
- **Phase / Task**: snapshot 2026-11-17 às 10:35 (-03); fases 1–4 e T1–T23 concluídas (23/64), M1 in_progress. Handoff detalhado atualizado: `.specs/features/m1-career-kb/handoff.md`.
- **Completed**: CI/dependências/UI básica, fronteiras/persistência/fontes, nove tipos KB com criação/consulta/proveniência e 27 rotas HTTP concretas; OpenAPI/SDK gerados, erros tipados e revisão dos CHECKs. Decisões manuais T16/T18/T22 aprovadas; não repetir entrevistas dessas escolhas.
- **Gates**: principal repetiu a validação da árvore final após o pedido de commit/push: geração PASS, focal 141 passed/435 deselected, BUILD integral exit 0 com 576 Python (2 avisos existentes), 19 Vitest, 4 Playwright, typecheck/build/contrato/lint PASS. Lacuna do último BUILD do worker resolvida; evidência em execution.md.
- **In-progress**: commit/push solicitado às 10:32 (-03); nenhum incremento T24 iniciado. T23 foi fechada com status/rastreabilidade e evidências no mesmo commit.
- **Next step**: conferir git e retomar próximo lote Terra T24–T28 (cliente TS, sessão/cache, Router, ProfileEditor e lista/detalhe), em sequência. Não refazer T1–T23. Preservar dados fictícios e preferência GPT Terra.
- **Blockers**: sem decisão de negócio pendente; worker anterior atingiu quota, verificar capacidade ao retomar delegação. Piloto independente, revisão privada e aceite final ainda futuros. Push autorizado neste pedido; resultado do CI remoto não verificado.
- **Uncommitted files**: nenhum após o commit de fechamento T23; conferir git antes de retomar.
- **Branch**: feature/m1-career-kb, base d2a609d; conferir git antes de retomar. Ambiente atual full access/approval never: não enviar sandbox_permissions; isso não autoriza operações remotas ou dados reais.

Operação e comandos: handoff.md e docs/engineering/m0-local-operation.md; PATH Node 24 e PLAYWRIGHT_BROWSERS_PATH explícitos. Dados fictícios; não carregar fontes pessoais antes do piloto independente e revisão humana.
