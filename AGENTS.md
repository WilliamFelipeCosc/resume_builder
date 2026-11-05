# AGENTS.md — Instruções para agentes de programação

## Missão

Implementar um **Resume Builder local-first** que cria currículos fundamentados em evidências da Career Knowledge Base, analisa vagas e oferece um **servidor MCP** para agentes CLI externos preencherem candidaturas. Priorizar a primeira entrega utilizável **M3** sem retirar requisitos da V1 completa.

## Ordem de leitura

1. `PROJECT_SOURCE.md` para contexto global.
2. `docs/roadmap/milestones.md` e `docs/roadmap/acceptance-criteria.md` para prioridade e DoD.
3. Módulo em `docs/modules/` e contratos em `docs/contracts/` relevantes à tarefa.
4. ADRs em `docs/architecture/adr/` para decisões que não devem ser reabertas sem autorização.
5. `docs/decisions/open-decisions.md` para decisões abertas (não tratá-las como definitivas).

## Regras invariantes

- **Nunca** inventar experiência, certificação, remuneração, autorização de trabalho ou outras qualificações de uma pessoa. Textos gerados são propostas até revisão quando necessária.
- Não transformar outputs de IA em fatos canônicos da Career KB sem aprovação do usuário.
- Não expor dados confidenciais/secretos por padrão. Aplicar política antes da recuperação e antes de enviar contexto a providers ou MCP.
- **Não construir nem reintroduzir controle de navegador integrado** (Playwright/Hermes no backend, CDP orquestrado pela aplicação, Chrome screenshots internos). O browser pertence ao agente CLI externo.
- Não criar ferramentas MCP genéricas de shell, SQL, filesystem indiscriminado, gestão de credenciais ou `submit_application`.
- No MCP V1, registrar relatos de progresso/resultados **sem inferir confirmação de submissão**; aprovação remota formal via MCP pertence à V2.
- Não exigir RabbitMQ, Grafana/Loki/Tempo, descoberta automatizada de vagas ou workflow MCP de aprovações na V1.
- Não criar fallback automático de Hermes para OpenAI API paga. A escolha de provider deve ser explícita.
- Não adicionar bibliotecas ou dependências por preferência pessoal quando existirem escolhas `OPEN` — faça um pequeno ADR/proposta com tradeoffs.

## Fluxo de trabalho por tarefa

1. Identifique REQs e ACs relacionados, escopo de marco e riscos de privacidade.
2. Faça a menor mudança funcional end-to-end (Vertical Slice), usando contratos e adapters.
3. Adicione testes unitários/integração/E2E e testes negativos de autorização conforme aplicável.
4. Rode checks definidos no projeto; se scripts ainda não existirem, **não finja que foram executados**.
5. Forneça evidências verificáveis: comandos, status, fixtures, arquivos alterados e limitações.
6. Atualize documentação e ADR quando a mudança afetar comportamento ou arquitetura.

## Estilo arquitetural

- Monorepo pnpm + Turborepo; React/Vite; NestJS API; Worker BullMQ; SQLite/Drizzle; Redis via Compose.
- Separar domínio, adapters, contratos e infraestrutura. MCP chama Application Services autorizados; não acessa SQLite indiscriminadamente.
- Schemas com validação em runtime, migrations reversíveis/planejadas, idempotency keys para relatos, logs estruturados e operações auditáveis.
- Separar conteúdo semântico do currículo de seus templates e estilo; edições de IA em ChangeSets com diff/aprovação.

## Segurança de testes

- Usar perfis e dados **fictícios** e formulários de teste; não enviar candidaturas reais em CI.
- Garantir que exemplos e fixtures não incluam credenciais ou dados privados reais.
- Testar redaction e permissões MCP; usuários e clientes podem ter níveis distintos de capacidade.

## Atualização de progresso

Ao concluir uma tarefa, informar: marco, REQ/AC cobertos, implementado, testes realmente executados, pendências e riscos. Não anunciar uma release ou integração com agentes externos como concluída antes da validação em seus clientes.
