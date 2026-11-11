# M0 — Tarefas de implementação

**Status:** Execução aprovada pelo proprietário em 2026-11-11; quatro lotes sequenciais de agentes (T1–T6, T7–T12, T13–T18, T19–T22).
**Design:** [design.md](design.md). **Spec:** [spec.md](spec.md).

## Execution Protocol

Usar `tlc-spec-driven` e seu fluxo Execute/Critical Rules. Uma tarefa por vez; testes na mesma tarefa, gate verde e atualização de tasks/spec antes do commit atômico Conventional Commits. Sem push/deploy. Se a skill não estiver disponível, parar e informar.

Prova de bootstrap em T4 bloqueia T13: falha exige revisão, sem fallback de autorização. Contagens abaixo são mínimos de casos planejados, não resultados nem quotas que substituam cobertura. Registrar contagem real e nenhum teste removido silenciosamente. T1–T6 concluídas com gates registrados; T7–T22 pendentes.

## Test Coverage Matrix

Proveniência: AGENTS.md, docs/engineering/testing.md, docs/engineering/development.md, docs/roadmap/acceptance-criteria.md e spec aprovada. Workspaces/manifests e testes de T2–T6 existem; fases seguintes pendentes. Tipos de teste já decididos nesses documentos; comandos abaixo são PROPOSTOS para criação, não comandos existentes ou executados.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
|---|---|---|---|---|
| Domínio/contratos/política/paths | Pytest unitário | Cada FND aplicável e limites/falhas listados | tests/unit/ | Quick Python |
| Repositório/migração | Pytest integração | SQLite real, constraints, concorrência, rollback e limites temporais | tests/integration/ | Full focal |
| HTTP/bootstrap | Pytest integração + prova navegador | Happy path e todos os negativos de autorização/input/logs | tests/integration/ | Full focal |
| Worker/Redis/resiliência | Pytest integração real | Offline/recovery/crash/redelivery, mesma execução e efeito único | tests/integration/ | Full integrado |
| Web | Vitest + Playwright Test externo | Botão, retry, polling, reabertura, bootstrap, avisos e terminal | apps/web/tests/ | Full Web |
| Cliente gerado | Contrato/typecheck | OpenAPI válido, regeneração sem diff e compilação consumidora | packages/api-client/ | Build integrado |
| Configuração/operação | Smoke | Imports/build, isolamento e comandos reproduzíveis | tests/smoke/ | Build por runtime |
| Documentação técnica | Verificação documental | Versões/fontes/comandos verificáveis; sem alegação de execução | docs/engineering/ | Build inicial |

## Gate Check Commands

Comandos Python/Web de T2–T6 executados conforme evidências; comandos do fluxo integrado permanecem futuros. Até existir runtime, gate inicial usa verificações documentais e os validadores da skill. Não executar suíte inexistente/vazia como evidência.

| Gate Level | When to Use | Command |
|---|---|---|
| Build inicial | T1 | Verificar ferramentas disponíveis, fontes e nota de compatibilidade; validate_spec.py e validate_tasks.py da skill + git diff --check |
| Quick Python | Unitários | Proposto: uv run pytest tests/unit -q; seleção focal indicada por tarefa |
| Build Python | Workspace Python | Proposto: uv sync --locked; uv run pytest tests/smoke -q; imports dos membros |
| Build Web | Workspace frontend | Proposto: pnpm install --frozen-lockfile; pnpm --filter web test; pnpm --filter web typecheck; pnpm --filter web build |
| Full focal | Integração do componente | Proposto: uv run pytest tests/unit tests/integration -q com seleção explícita do componente e dependências; broker real quando aplicável |
| Full Web | Tela/abertura | Proposto: Vitest, typecheck/build e Playwright Test externo via scripts do workspace web |
| Full integrado | Resiliência real | Proposto: uv run pytest tests/unit tests/integration tests/smoke -q com SQLite/Redis/Worker reais isolados |
| Build integrado | Fim de fase/runtime integrado | Full integrado + Full Web + regeneração OpenAPI/TS sem diff + lint/format a definir em T1 + git diff --check |

Gates de fase rodam apenas checks aplicáveis ao runtime já entregue; a fase final exige todos. Comandos exatos e versões serão preenchidos ao criá-los. Seleção focal deve citar casos e contagem, nunca esconder falhas preexistentes. Nenhuma instalação de ferramentas do sistema/CI/provider.

## Execution Plan

Fases sequenciais; tarefas sequenciais em cada fase. Setas representam dependências completas. As dependências de fase anteriores são transitivas.

```
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12 → T13 → T14 → T15 → T16 → T17 → T18 → T19 → T20 → T21 → T22
```

## Task Breakdown

### Phase 1: Preparação e prova técnica

### T1: Nota de compatibilidade e seleção técnica

**What**: Registrar versões e compatibilidade verificadas, gerador OpenAPI→TS escolhido com tradeoffs, dependências de teste/lint e comandos futuros; nenhuma instalação de sistema.
**Where**: `docs/engineering/m0-toolchain.md` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: None
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-20/21/23
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 3 casos/checks pertinentes; contagem real registrada.
- [x] Gate Build inicial passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: documental
**Gate**: Build inicial
**Commit**: `docs(m0): record toolchain decision`

**Evidence:** `docs/engineering/m0-toolchain.md`: três checks documentais, versões/metadados oficiais, gerador selecionado e validadores verdes; runtime ainda não executado.

### T2: Workspace Python reproduzível

**What**: Configurar membros uv, imports mínimos e lock; smoke verifica imports e testes isolados sem ler private.
**Where**: `backend/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T1
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-21/22
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 3 casos/checks pertinentes; contagem real registrada.
- [x] Gate Build Python passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: smoke
**Gate**: Build Python
**Commit**: `feat(m0): bootstrap python workspace`

**Evidence:** `uv sync --all-packages --locked` passou (33 pacotes); `.venv/bin/pytest tests/smoke -q`: 5 passed; Ruff check/format passaram. Execução direta da venv equivale ao runner uv sem acesso ao cache externo bloqueado. Nenhum teste removido/ignorado.

| Critério T2 / FND | Evidência (assertion) | Resultado / reverse mapping |
|---|---|---|
| Imports dos três membros sem efeitos, FND-21/22 | tests/smoke/test_workspace.py:20 `assert completed.returncode == 0`; :22 `assert list(tmp_path.iterdir()) == []` | 3 casos, mantidos: workspace e isolamento |
| Dependências compatíveis/importáveis, FND-21 | tests/smoke/test_workspace.py:27 `assert importlib.import_module(name).__name__ == name` | imports reais, mantido: build Python |
| Coleta isolada, FND-22 | tests/smoke/test_workspace.py:34 `assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]` | mantido: não coletar private |

Adequação: critérios T2 cobertos; sem assertions rasas ou casos fora do escopo; padrão docs/engineering/testing.md seguido. Não demonstra ainda AC-M0 completo.

### T3: Workspace frontend reproduzível

**What**: Configurar pnpm, React/Vite, cliente workspace inicialmente vazio e lock; build, typecheck e smoke Vitest passam sem DTO manual.
**Where**: `apps/web/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T2
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-20/21
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 3 casos/checks pertinentes; contagem real registrada.
- [x] Gate Build Web passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: smoke
**Gate**: Build Web
**Commit**: `feat(m0): bootstrap web workspace`

**Evidence:** `pnpm install --frozen-lockfile`; `pnpm --filter web test` (3 passed), `typecheck` e `build` passaram fora do sandbox, sem warnings de runtime. Sandbox usa Node embutido 26.12.1 do executável pnpm e bloqueia store; gate oficial usou ambiente autorizado Node24.18. Nenhum DTO manual.

| Critério / FND | Assertion / evidência | Reverse mapping |
|---|---|---|
| Web renderiza, FND-21 | apps/web/tests/smoke.test.tsx:7 `toContain('<h1>Resume Builder</h1>')` | manter: smoke T3 |
| Instrução sem sessão, FND-21 | apps/web/tests/smoke.test.tsx:10 `toContain('Abra pelo comando local para iniciar uma sessão autorizada.')` | manter: placeholder autorizado pelo desenho |
| Sem ações antecipadas, FND-20 | apps/web/tests/smoke.test.tsx:13 `not.toContain('<button')` | manter: workspace sem DTO/API manual |

Adequação: smoke mínimo 3 casos e checks de compilação/build cobertos; sem teste removido/ignorado. Contrato consumido somente após T19.

### T4: Prova isolada do bootstrap Linux

**What**: Comprovar UID, ticket expirado/repetido, cookie real, fragmento limpo e reinício com sentinelas ausentes; registrar navegador/versões. Falha bloqueia autenticação definitiva e exige revisão.
**Where**: `tools/bootstrap_probe/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T3
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-13/15/16/18
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 8 casos/checks pertinentes; contagem real registrada.
- [x] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração + navegador
**Gate**: Full focal
**Commit**: `feat(m0): prove local session bootstrap`

**Evidence:** `tools/bootstrap_probe/README.md`: prova PASS, 10 casos Python + 1 navegador Chromium158 headless, smoke5 preservados. Typecheck/Ruff verdes. Navegador desktop padrão não validado; launcher definitivo permanece T20.

| Critério / FND | Assertion / resultado definido | Reverse mapping |
|---|---|---|
| UID/path, FND-13/16 | tests/integration/test_bootstrap_probe.py:43 `assert probe.peer_uids == [os.getuid()]`; :44/45 modos 0700/0600; :50 recusa unauthorized | manter: UID real, esperado divergente |
| TTL e uso único, FND-13 | mesmo arquivo :59 `redeem(value) is None` aos 30s; :67 sucesso antes; :75 exatamente um resgate | manter: limites/concorrência |
| Cookie/replay, FND-13 | :82 status200; :83 atributos; :85 status401; :87 leitura200 | manter: sessão real HTTP |
| Restart, FND-15 | :95 cookie antigo401 | manter: sessão por instância |
| Host/Origin, FND-16 | :100/102 status403 | manter: fronteira loopback |
| Logs, FND-18 | :115…120 sentinela/ticket/cookie ausentes, campos exatos JSON | manter: conteúdo sanitizado |
| Path preexistente/symlink | :126/130 `pytest.raises(FileExistsError)` | manter: não sobrescrever canal |
| Navegador, FND-13/15/18 | apps/web/tests/bootstrap-probe.spec.ts:57 autorizado, :58 hash vazio, :59 cookie JS vazio, :62 atributos/expires=-1, :64 URL sem ticket, :65 replay401, :69/70 logs, :75 unauthorized após restart | manter: prova real exigida T4 |

Adequação: todos critérios da prova cobertos, sem testes removidos/ignorados; nenhuma alegação de autenticação definitiva ou desktop padrão. Segurança/lifecycle completos ficam T13–T16.

### T5: Paths e isolamento por ambiente

**What**: Resolver XDG/env validado e diretórios temporários em testes; rejeitar configuração insegura, impedir seleção acidental de ambiente de teste sobre dados locais.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T4
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-22/23
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 5 casos/checks pertinentes; contagem real registrada.
- [x] Gate Quick Python passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário
**Gate**: Quick Python
**Commit**: `feat(m0): isolate environment paths`

**Evidence:** `.venv/bin/pytest tests/unit/test_paths.py -q`: 19 passed; Ruff check/format e diff check verdes. Paths sem I/O de conteúdo, criação explícita, nenhum Redis/provider iniciado.

| Critério / FND | Assertion / resultado definido | Reverse mapping |
|---|---|---|
| XDG e namespace por ambiente, FND-22 | tests/unit/test_paths.py:15…19 paths exatos e diretório vazio; :24…27 defaults HOME | manter: resolução sem side effects |
| Nomes/paths inválidos, FND-22 | :34 `raises(ValueError, match="environment")`; :69 relative/absolute; :78 symlink | manter: configuração segura |
| Teste temporário explícito, FND-22 | :39 test_root obrigatório; :49…52 paths temporários ignoram XDG; :56 recusa root em dev; :61 recusa fora de temp | manter: proteção dados locais |
| Diretórios privados, FND-22/23 | :87 `st_mode & 0o777 == 0o700`; :93 recusa existente inseguro; :95 sem alterar permissões | manter: criação somente explícita |

Adequação: 19 casos necessários aos critérios de configuração/isolamento, nenhuma leitura de private nem dependência de sistema iniciada. Nenhum teste removido/ignorado.

### T6: Contrato Pydantic do diagnóstico

**What**: Definir requests/respostas aprovados, aliases, UUID/UTC, resultado fixo, estados e erros constantes; rejeitar campos extras, entradas inválidas e tipos indevidos.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T5
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-02/17/20
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 8 casos/checks pertinentes; contagem real registrada.
- [x] Gate Quick Python passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário
**Gate**: Quick Python
**Commit**: `feat(m0): define diagnostic contracts`

**Evidence:** `.venv/bin/pytest tests/unit -q`: 66 passed (47 contratos + 19 paths). Gate da fase: `.venv/bin/pytest tests/unit tests/integration tests/smoke -q` 81 passed; Vitest3, typecheck/build, uv locked e Ruff check/format verdes. Nenhum teste removido/ignorado.

| Critério / FND | Assertion / resultado definido | Reverse mapping |
|---|---|---|
| Request UUID/alias/extra, FND-17/20 | tests/unit/test_diagnostic_contracts.py:38 dump exato; :52 inválidos rejeitados; :65 UUIDs inválidos | manter: contrato aprovado |
| Campos resposta, FND-20 | :59/60 dump completo igual payload e chaves exatas | manter: todos os 11 campos/valores |
| Contador estrito 0…3, FND-02 | :71 inválidos; :77 válidos | manter: orçamento definido |
| Estados/resultados, FND-02 | :83 ativos sem final; :97 resultado exato m0-v1; :99/101 recusa sucesso inválido; :110 falha com code; :112/114 recusa falha inválida; :122 estado desconhecido; :183/190/201 combinações erro/warning inválidas | manter: integridade DTO |
| UTC, FND-20 | :128 instante UTC; :129 Z normalizado; :130/132 naïve/número recusados | manter: timestamps RFC3339 |
| Aviso separado, FND-17 | :138 objeto queue_unavailable exato; :142 error nulo | manter: warning transitório |
| Allowlist e extras, FND-17 | :156/161/163 rejeição payload/lease; :220 mensagens constantes por código; :224 incompatibilidade código/mensagem recusada | manter: sem texto arbitrário |
| Schema nullable/tipado, FND-20 | :168 execution:null; :173/174 aliases/additionalProperties; :176…178 limites/uuid | manter: fonte OpenAPI futura |

Adequação: critérios locais T6 cobertos por valores definidos, sem assertions rasas ou testes fora do contrato. Limite HTTP 1KiB é T14/T15; geração TS é T19. Não confundir contratos validados com fluxo integrado concluído.

### Phase 2: Persistência e serviços

### T7: Migração inicial do diagnóstico

**What**: Criar tabela, CHECKs e índices aprovados; upgrade/downgrade/upgrade em SQLite temporário; negar duplicação de chave/ativo e estados inconsistentes.
**Where**: `backend/migrations/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T6
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-06/19/22
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 6 casos/checks pertinentes; contagem real registrada.
- [x] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): migrate diagnostic persistence`

**Evidence:** `.venv/bin/pytest tests/unit tests/integration/test_diagnostic_migration.py -q`: 83 passed (66 unit +17 migration). Ruff check/format + diff check green. Integer Unix microseconds normalize UTC storage; WAL and 250 ms busy timeout. No schema operation on requests; explicit Alembic only.

| Criterion / FND | Assertion evidence / expected outcome | Reverse mapping |
|---|---|---|
| Migration roundtrip, FND-19/22 | tests/integration/test_diagnostic_migration.py:49 pending; :51 unrelated table retained; :53 table recreated | keep: approved migration |
| Key/active exclusion, FND-06 | tests/integration/test_diagnostic_migration.py:69/76 raises IntegrityError | keep: uniqueness |
| Consistency and safe payloads | tests/integration/test_diagnostic_migration.py:95 and final parametrized test raises IntegrityError for invalid states/payloads | keep: approved CHECKs |
| WAL / bounded wait | tests/integration/test_diagnostic_migration.py:101/102 wal and250 | keep: ADR-003 concurrency |

Adequacy: all local T7 criteria covered with real SQLite; no removed/skipped tests. Concurrency at service boundary is T8; integrated migration acceptance is T22.

### T8: Repositório de criação e leitura

**What**: Persistir pending, ler última execução com ordenação determinística, reutilizar chave inclusive terminal, resolver concorrência por transação/índice; não publicar na transação.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T7
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-01/04/05/06
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 7 casos/checks pertinentes; contagem real registrada.
- [x] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): persist diagnostic intentions`

**Evidence:** `.venv/bin/pytest tests/unit tests/integration/test_diagnostic_migration.py tests/integration/test_diagnostic_repository.py -q`: 91 passed (8 new repository cases). Ruff check/format green. BEGIN IMMEDIATE serializes create; commit precedes return and no broker dependency exists.

| Criterion / FND | Assertion evidence / expected outcome | Reverse mapping |
|---|---|---|
| Persist full pending, FND-01 | tests/integration/test_diagnostic_repository.py:28–40 values pending/0/UUID/UTC/null and durable row | keep: intention contract |
| latest/reopen, FND-04 | same file empty/latest/timestamp-tie tests: None, same DTO, deterministic max UUID | keep: latest query |
| same key incl terminal, FND-05 | same file replay/terminal tests: created=False and equal prior execution while another active | keep: idempotency |
| concurrent distinct/same keys, FND-06 | same file concurrent tests: one created and one ID; distinct keys one winner | keep: SQLite concurrency |

Adequacy: eight cases map to T8, no speculative tests. Full HTTP409 and queue ordering remain T15/T17. No tests removed/skipped.

### T9: Posse e conclusão condicionais

**What**: Claim atômico incrementa apenas tentativa efetiva; conclusão exige token/estado/prazo válidos; testes de duplicatas, limite exato e Worker antigo após nova posse.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T8
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-02/09/10/12
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [x] Entrega descrita em What funciona e atende os FNDs citados.
- [x] Testes da camada escritos junto da implementação, mínimo planejado de 9 casos/checks pertinentes; contagem real registrada.
- [x] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): guard worker leases`

**Evidence:** `.venv/bin/pytest tests/unit tests/integration/test_diagnostic_{migration,repository,leases}.py -q`: 103 passed, including12 lease cases. Atomic UPDATE RETURNING, clock read after write lock; no processing/Redis in transaction.

| Criterion / FND | Assertion evidence / expected outcome | Reverse mapping |
|---|---|---|
| claim/count, FND-09 | tests/integration/test_diagnostic_leases.py: claim test asserts running/1/30s; concurrent test one owner/1 | keep: actual attempts only |
| fixture result, FND-02 | same file complete test asserts succeeded, exact message/version, timestamps/correlation/count and null error/warning | keep: complete contract |
| time fences, FND-10 | same file elapsed30/30.000001/120 returns False,29.999999 True; lease capped at total120 | keep: exact deadline |
| stale/terminal, FND-12 | same file wrong token False; terminal equality; old token False after new claim | keep: no late effects |
| budget | same file exhausted budget claim None/count3 | keep: approved cap |

Adequacy:12 cases cover all T9 local outcomes; no assertions weakened/removed/skipped. Recovery itself remains T10.

### T10: Reconciliação de prazo e tentativas

**What**: Com relógio controlado recuperar lease abandonada e falha de tentativa; terceira falha e 120 s terminam; impedir retomada vencida e alteração terminal.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T9
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-08/09/10/11/12
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 9 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário + integração
**Gate**: Full focal
**Commit**: `feat(m0): reconcile diagnostic deadlines`

### T11: Serviço de diagnóstico autorizado

**What**: Exigir principal/capability antes de acessar repositório; criar/consultar usando contratos e reconciliar leitura; spies comprovam zero acesso sem autorização.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T10
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-01/04/05/06/14
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 6 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário + integração
**Gate**: Full focal
**Commit**: `feat(m0): authorize diagnostic service`

### T12: Política de logs estruturados

**What**: Configurar structlog JSON e allowlist de campos, correlação e códigos; excluir cookies/tickets/payload/stack crua inclusive de logs de terceiros e erro inesperado.
**Where**: `backend/core/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T11
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-18
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 6 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Quick Python passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário
**Gate**: Quick Python
**Commit**: `feat(m0): sanitize structured logs`

### Phase 3: Fronteiras autorizadas e fila

### T13: Sessão e canal Unix

**What**: Promover mecanismo comprovado: peer UID, permissões/owner/symlink, ticket atômico e TTL, memória por instância, lock e lifecycle; não remover socket vivo.
**Where**: `backend/api/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T12
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-13/15/16
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 9 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): implement local session channel`

### T14: Rota de resgate de sessão

**What**: Implementar bootstrap com JSON/Origin/limite/ticket, cookie e no-store; negativos não consultam diagnósticos e não vazam sentinelas; reinício invalida cookie.
**Where**: `backend/api/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T13
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-13/14/15/16/17/18
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 9 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): redeem bootstrap tickets`

### T15: Rota de criação de diagnóstico

**What**: Implementar POST 202/200/409 e middleware compartilhado de Host/Origin/sessão/limite; cobrir 401/403/413 chunked/422 sem eco de input e zero efeito indevido.
**Where**: `backend/api/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T14
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-01/05/06/14/16/17/18
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 10 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): create diagnostic endpoint`

### T16: Rota de última execução

**What**: Implementar GET com execution nullable, reconciliação antes de retornar, requestId de transporte separado e negativos antes da leitura.
**Where**: `backend/api/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T15
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-04/11/14/16/18
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 6 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): read latest diagnostic`

### T17: Entrega Redis e reconciliador da API

**What**: Publicar após commit, timeout curto sem bloquear event loop, warning sanitizado, reentrega limitada e tick/startup; não regredir claim que venceu corrida com confirmação.
**Where**: `backend/api/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T16
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-01/07/08/11/12
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 8 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração
**Gate**: Full focal
**Commit**: `feat(m0): reconcile redis delivery`

### T18: Actor do diagnóstico fixo

**What**: Processar fixture só após claim; usar posse na conclusão, sem retry automático concorrente; redelivery e falha após commit não duplicam resultado. Integrar Worker real.
**Where**: `backend/worker/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T17
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-02/09/10/11/12/18
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 8 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full focal passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário + integração
**Gate**: Full focal
**Commit**: `feat(m0): process fixed diagnostic`

### Phase 4: Contrato, Web e aceite real

### T19: Cliente gerado OpenAPI

**What**: Exportar schema offline, gerar tipos/chamadas com ferramenta selecionada; geração repetida sem diff, frontend compila; docs/schema HTTP protegidos, health mínimo público.
**Where**: `packages/api-client/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T18
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-20
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 4 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Build integrado passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: contrato + typecheck
**Gate**: Build integrado
**Commit**: `feat(m0): generate openapi client`

### T20: Tela do diagnóstico e abertura local

**What**: Implementar tela e bootstrap usando cliente gerado, chave estável no retry, botão/polling sem sobreposição, aviso/terminal/401; servir build mesma origem e launcher via URL padrão.
**Where**: `apps/web/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T19
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-03/04/07/13/15
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 10 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full Web passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: unitário + E2E
**Gate**: Full Web
**Commit**: `feat(m0): deliver diagnostic web flow`

### T21: Harness de resiliência real

**What**: Exercitar Redis offline/online, perda de fila confirmada, kill/restart Worker e expiração com mesma execução e efeito único; fault injection só no harness, nunca no endpoint público.
**Where**: `tests/integration/` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T20
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-07/08/09/10/11/12/21/22
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 6 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Full integrado passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: integração real
**Gate**: Full integrado
**Commit**: `feat(m0): verify recovery scenarios`

### T22: Operação reproduzível e aceite M0

**What**: Expor comandos reais, documentar operação/limpeza manual e Redis Compose manual, executar caminho completo Web→API→SQLite→Worker→Web com dados sintéticos; capturar evidências e limites sem declarar M0.5 concluído.
**Where**: `justfile` (um componente; testes e wiring indispensável no mesmo commit)
**Depends on**: T21
**Reuses**: desenho aprovado e componentes das tarefas anteriores; nenhum dado privado.
**Requirement**: FND-19/20/21/22/23
**Tools**: terminal/patch; Context7 para APIs novas; Serena para navegação quando houver código; skill tlc-spec-driven. Proposta sujeita à escolha do proprietário.
**Done when**:

- [ ] Entrega descrita em What funciona e atende os FNDs citados.
- [ ] Testes da camada escritos junto da implementação, mínimo planejado de 4 casos/checks pertinentes; contagem real registrada.
- [ ] Gate Build integrado passa com comandos e evidências registrados; tasks/spec atualizados no commit atômico.

**Tests**: smoke + E2E
**Gate**: Build integrado
**Commit**: `feat(m0): document reproducible local checks`

## Task Granularity Check

Cada tarefa entrega um componente/endpoint ou uma prova/nota operacional coesa. Testes e wiring mínimo pertencem à mesma entrega; não existem tarefas de teste que substituam os testes locais de tarefas anteriores. T21 acrescenta cenários sistêmicos reais. T22 verifica o procedimento completo.

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
|---|---|---|---|
| T1 | None | None | Match |
| T2 | T1 | T1 | Match |
| T3 | T2 | T2 | Match |
| T4 | T3 | T3 | Match |
| T5 | T4 | T4 | Match |
| T6 | T5 | T5 | Match |
| T7 | T6 | T6 | Match |
| T8 | T7 | T7 | Match |
| T9 | T8 | T8 | Match |
| T10 | T9 | T9 | Match |
| T11 | T10 | T10 | Match |
| T12 | T11 | T11 | Match |
| T13 | T12 | T12 | Match |
| T14 | T13 | T13 | Match |
| T15 | T14 | T14 | Match |
| T16 | T15 | T15 | Match |
| T17 | T16 | T16 | Match |
| T18 | T17 | T17 | Match |
| T19 | T18 | T18 | Match |
| T20 | T19 | T19 | Match |
| T21 | T20 | T20 | Match |
| T22 | T21 | T21 | Match |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires / Task Says | Status |
|---|---|---|---|
| T1 | documentação | documental | OK — na própria tarefa |
| T2 | configuração | smoke | OK — na própria tarefa |
| T3 | configuração | smoke | OK — na própria tarefa |
| T4 | bootstrap | integração + navegador | OK — na própria tarefa |
| T5 | configuração de runtime | unitário | OK — na própria tarefa |
| T6 | contrato | unitário | OK — na própria tarefa |
| T7 | persistência | integração | OK — na própria tarefa |
| T8 | persistência | integração | OK — na própria tarefa |
| T9 | persistência | integração | OK — na própria tarefa |
| T10 | domínio | unitário + integração | OK — na própria tarefa |
| T11 | domínio | unitário + integração | OK — na própria tarefa |
| T12 | observabilidade | unitário | OK — na própria tarefa |
| T13 | bootstrap | integração | OK — na própria tarefa |
| T14 | HTTP | integração | OK — na própria tarefa |
| T15 | HTTP | integração | OK — na própria tarefa |
| T16 | HTTP | integração | OK — na própria tarefa |
| T17 | fila | integração | OK — na própria tarefa |
| T18 | worker | unitário + integração | OK — na própria tarefa |
| T19 | contrato gerado | contrato + typecheck | OK — na própria tarefa |
| T20 | Web | unitário + E2E | OK — na própria tarefa |
| T21 | resiliência | integração real | OK — na própria tarefa |
| T22 | operação | smoke + E2E | OK — na própria tarefa |

## Aprovação e execução

Plano: 22 tarefas em quatro fases (6 + 6 + 6 + 4). Oferecer execução pelo agente principal ou por quatro workers sequenciais, um por fase, antes de iniciar; nenhum worker é iniciado sem aceite. Verifier independente obrigatório após última tarefa, incluindo sensor de discriminação em scratch e validation.md com evidência por AC. Verifier não é aprovação de release.

Aprovação das tarefas confirma matriz/gates propostos e autoriza implementação/commits locais. Ferramentas e opção de workers serão confirmadas antes da execução, conforme skill. Prova no navegador e downloads que exigirem permissões seguem a autorização do ambiente; não alegar execução antes dela. Não pedir autorização repetida para o que já foi aprovado.
