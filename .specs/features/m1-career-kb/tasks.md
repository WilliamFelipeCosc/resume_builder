# M1 — Career KB Core Tasks

## Execution Protocol

Executar com a skill `tlc-spec-driven`, seguindo Critical Rules e o fluxo Execute.
Ler a referência de implementação integralmente antes de começar.
Um deliverable atômico por tarefa; testes da mudança e registro de progresso
fazem parte do mesmo commit. Verifier independente final e sensor são obrigatórios.

**Design:** [design.md](design.md), aprovado pelo proprietário em 2026-11-16.
**Spec:** [spec.md](spec.md). **Status:** Approved em 2026-11-16 às 20:09 (-03); 6/64 concluídas.
**Início:** autorizado explicitamente pelo proprietário em 2026-11-16 às 20:17 (-03); execução iniciada na T1.
**Escopo:** M1; REQ-KB-001/002/004, REQ-SEC-001, AC-M1-001/002/003.
**Não executado:** nenhuma instalação, alteração funcional ou teste de runtime nesta preparação.

## Test Coverage Matrix

Gerada de AGENTS.md, docs/roadmap/acceptance-criteria.md, justfile,
pyproject.toml, manifests/configs web e spec/design aprovados.
Amostras de estilo: test_diagnostic_service, test_diagnostic_contracts,
test_diagnostic_http_create, test_diagnostic_repository,
test_diagnostic_migration, test_workspace, diagnostic.test.tsx e
diagnostic-app.spec.ts. São oito arquivos existentes, não resultados de execução.
Não há threshold percentual obrigatório; cada resultado relevante da spec e
cada edge case exige evidência. Contratos/constraints têm testes de significado,
não testes que apenas repitam declarações de configuração.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Domínio/policy | unit + integration | Todos os ramos dos ACs relevantes; autorização antes de qualquer acesso, estados e limites | tests/unit/test_m1_*.py; tests/integration/test_m1_*.py | PY |
| Persistência/migration/arquivos | unit + integration | Nove tipos, FK, original/snapshot, concorrência, integridade e falhas transacionais; SQL/filesystem reais | tests/integration/test_m1_*.py | PY |
| Serviço/HTTP | unit + integration | Rotas concretas: happy + edge + error; pré-auth antes de corpo/parser; JSON e multipart; redaction | tests/unit/test_m1_*.py; tests/integration/test_m1_*.py | HTTP |
| Contratos | unit + integration | Round trip e negativos dos nove tipos, SDK sem DTO manual, geração determinística | tests/unit/test_m1_*.py; apps/web/tests/client-contract.ts | PY ou WEB conforme runtime; HTTP ao publicar endpoint |
| UI/estado | unit + e2e | Interações/erros por componente, dados privados/session/cache e fluxo real com teclado | apps/web/tests/m1-*.test.tsx; apps/web/tests/m1-*.spec.ts | FRONT na T6; BROWSER com backend M1 |
| Processo limitado | unit + integration | PDF sintético, criptografia/erro/timeout/memória, ambiente e saída mínima | tests/integration/test_m1_*.py | PY |
| Configuração/dependências | verification | Checks existentes/build e experimento sintético; sem novo teste espelhando manifest | manifests/configs e evidência em execution.md | BUILD ou WEB conforme a tarefa |
| Documentação/evidência | verification | Consistência, links e comandos reais; nenhum resultado inventado | .specs/features/m1-career-kb/; docs/engineering/ | DOC; baseline/aceite usam BUILD |
| Verificação | verification + integration | Re-derivar ACs/sensor independente e evidência de processo; testes por operação já existem | test_m1_process_recovery.py; pilot-validation.md; validation.md | BUILD e sensor focal |
| Aceite humano privado | manual + verification | Revisão local humana real, hashes preservados e evidência minimizada | private-review.md sem conteúdo privado | MANUAL |

## Gate Check Commands

Gerados dos comandos existentes. PY acrescenta seleção `-k m1` ao runner atual;
os arquivos/nomes novos devem corresponder à seleção. Não criar scripts fictícios.
Zero testes coletados é falha. O nome dos arquivos de teste em cada tarefa é
um alvo proposto, não arquivo já existente.

| Gate Level | When to Use | Command |
| --- | --- | --- |
| PY | Resultado Python focal | `uv run --all-packages --locked pytest tests/unit tests/integration tests/smoke -q --basetemp=/tmp/rb-m1-tests -k m1`, seguido de `just lint` |
| WEB | Resultado TS/contrato focal | `pnpm --filter web test`, `pnpm --filter web typecheck`, `pnpm --filter web build`, `just check-contract`, `just lint` |
| HTTP | Endpoint/DTO publicado | `just generate`; PY; `just check-contract`; `pnpm --filter web typecheck`; `just lint` |
| FRONT | Compatibilidade de UI inicial, sem backend M1 | WEB; `just check-browser`, incluindo fixture sintética independente |
| BROWSER | Componente/fluxo real com backend M1 disponível | PY + WEB; `just check-browser` |
| BUILD | Baseline, fim de fase e fechamento | `just check` com PATH/Docker/Chromium preparados explicitamente conforme operação existente |
| DOC | Alteração só documental | `python3 /home/williamf/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/m1-career-kb/spec.md --strict`; `python3 /home/williamf/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/m1-career-kb/tasks.md --strict`; conferir links locais; `git diff --check` |
| MANUAL | Somente depois do piloto independente | Exigir T61 PASS_SYNTHETIC; exercer UI local com proprietário, conferir hashes/resultados agregados, sem executar CI sobre fontes pessoais |

`just generate` e mudanças no OpenAPI/SDK são coartefatos obrigatórios de cada
incremento HTTP, não diferidos para outra tarefa. Endpoint sem wiring testável
absorve o wiring mínimo na própria tarefa. Testes de UI usam os runners atuais;
não introduzir biblioteca de teste adicional por conveniência.
T4 configura descoberta; T6 comprova a coleta real da primeira fixture nova
de UI, sem depender de Python M1. T1/T5 usam BUILD; PY focal só começa com
os testes Python adicionados em T7. A baseline T1 não usa seleção focal vazia.

**Contagens esperadas:** cada tarefa lista o mínimo de cenários semânticos
planejados, derivado dos itens de aceite separados por ponto e vírgula.
Parametrizações podem produzir mais casos. As contagens coletadas/passadas
reais e a baseline são medidas em execução; ainda são unknown.
Nunca trocar contagem real por estimativa, apagar casos para atingir contagem,
ou usar esses mínimos como substituto da cobertura exigida na matriz.

## Execution Plan

Fases e tarefas executam sequencialmente; cada fase termina com BUILD.
Dependência imediata da tarefa anterior significa que todos os pré-requisitos
anteriores já passaram. Não há paralelismo intra-fase.
O número de tarefas não é número de slices: os checkpoints verticais estão
listados abaixo; as tarefas são unidades de commit/revisão.

### Phase 1: Reprodutibilidade, CI e compatibilidade

Tarefas T1 a T6; 6 entregas atômicas.

### Phase 2: Fronteiras, integridade e política

Tarefas T7 a T13; 7 entregas atômicas.

### Phase 3: Fontes privadas utilizáveis

Tarefas T14 a T17; 4 entregas atômicas.

### Phase 4: Primeiro domínio tipado pela API

Tarefas T18 a T23; 6 entregas atômicas.

### Phase 5: Primeiro cadastro completo na UI

Tarefas T24 a T28; 5 entregas atômicas.

### Phase 6: Formulários das demais entidades core

Tarefas T29 a T36; 8 entregas atômicas.

### Phase 7: Relações, revisão e confirmação

Tarefas T37 a T45; 9 entregas atômicas.

### Phase 8: Importação privada para staging

Tarefas T46 a T53; 8 entregas atômicas.

### Phase 9: Decisões atômicas, undo e recuperação

Tarefas T54 a T60; 7 entregas atômicas.

### Phase 10: Piloto independente, carga privada e fechamento

Tarefas T61 a T64; 4 entregas atômicas.

Checkpoints: T28 primeiro cadastro UI→API→SQLite; T36 entidades core;
T45 CRUD/relações/revisão; T53 staging inspecionável; T60 lote/undo/recuperação;
T61 verificação independente sintética; T62 carga privada humana.

## Task Breakdown

**Where** aponta a âncora do único deliverable da tarefa, não uma lista de
todos os arquivos do commit. **Supporting** declara explicitamente os
coartefatos necessários: testes, exports/wiring mínimo, ORM↔migration,
locks e SDK gerado. Não é autorização para implementar outras operações.
Tarefas de operação HTTP abrangem aquela operação e seu serviço testável;
não deixam regras sem teste para um incremento posterior.
Em arquivos com vários tipos de schema, o deliverable é o schema fechado
aprovado; não inclui CRUD, telas ou importadores adicionais.

**Tools** usa os conjuntos definidos no final deste documento, aprovados
pelo proprietário em 2026-11-16 às 20:09 (-03). Não requerem nova confirmação;
a execução foi liberada explicitamente às 20:17 (-03).

Pré-flight de execução: conferir branch/status e criar branch local de trabalho
sem descartar alterações. Stage explícito inclui somente artefatos aprovados e
a mudança da tarefa; nenhum dado privado ou alteração alheia. Preservar a
baseline para o sensor independente.

### Phase 1: Reprodutibilidade, CI e compatibilidade

#### T1: Registrar baseline e esforço da execução

**Status**: Complete
**What**: Registrar início real, comandos, contagens coletadas, espera separada e estado git; incorporar o plano aprovado em commit documental antes de código.
**Where**: `.specs/features/m1-career-kb/execution.md`
**Supporting**: artefatos de planejamento aprovados, registro de esforço e resultados reais dos comandos; não inclui mudança funcional ou dados privados.
**Depends on**: None
**Reuses**: Spec/design/contexto aprovados, modelo de esforço e workflow de estados.
**Requirement**: MONE-38
**Tools**: DOC
**Done when**:
- [x] Intervalos ativos e espera separados; suíte atual com contagens reais; falhas de worker registradas sem inventar causa.
- [x] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `docs(m1): record execution baseline`

#### T2: Preparar GitHub Actions antes do domínio

**Status**: Complete
**What**: Preparar runner Linux com pins/locks, Docker e Chromium para executar os gates existentes; resultados locais e remotos separados.
**Where**: `.github/workflows/check.yml`
**Supporting**: lockfile(s), configuração mínima e evidência de compatibilidade da dependência/runner.
**Depends on**: T1
**Reuses**: Pins, locks, justfile e seletores/harness atuais.
**Requirement**: MONE-01, MONE-02, MONE-33
**Tools**: PY
**Done when**:
- [x] Instalação reproduzível; comandos locais executáveis; CI remoto marcado NOT_RUN até push autorizado.
- [x] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `ci: add reproducible project checks`

#### T3: Fixar dependências de frontend

**Status**: Complete
**What**: Resolver versões exatas de Query, Router, RHF e Tailwind/integração Vite compatíveis com pins; incluir lock e evidência sintética do spike.
**Where**: `apps/web/package.json`
**Supporting**: lockfile(s), configuração mínima e evidência de compatibilidade da dependência/runner.
**Depends on**: T2
**Reuses**: Pins, locks, justfile e seletores/harness atuais.
**Requirement**: MONE-03, MONE-33
**Tools**: PY
**Done when**:
- [x] Typecheck e build atuais preservados; versões/peers/lock diff registrados, sem latest em manifests.
- [x] Gate WEB passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 2 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: WEB
**Commit**: `build(web): pin m1 frontend dependencies`

#### T4: Incluir os novos testes nos seletores e harness

**Status**: Complete
**What**: Adaptar seletores Vitest/Playwright e composição do harness para incluir testes M1, preservando os diagnósticos existentes e dados temporários.
**Where**: `apps/web/playwright.app.config.ts`
**Supporting**: lockfile(s), configuração mínima e evidência de compatibilidade da dependência/runner.
**Depends on**: T3
**Reuses**: Pins, locks, justfile e seletores/harness atuais.
**Requirement**: MONE-01, MONE-33, MONE-35
**Tools**: PY
**Done when**:
- [x] Descoberta preserva testes M0 e inclui padrões M1; T6 deve demonstrar coleta real do primeiro teste novo; não mascarar timeout com retry.
- [x] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `test(web): include m1 suites in existing gates`

#### T5: Fixar dependências de upload e metadados

**Status**: Complete
**What**: Declarar multipart diretamente na API e pypdf no pacote do leitor de fontes; resolver lock e importar em ambiente limpo sem ler dados privados.
**Where**: `backend/api/pyproject.toml`
**Supporting**: lockfile(s), configuração mínima e evidência de compatibilidade da dependência/runner.
**Depends on**: T4
**Reuses**: Pins, locks, justfile e seletores/harness atuais.
**Requirement**: MONE-14, MONE-15, MONE-30, MONE-33
**Tools**: PY
**Done when**:
- [x] Importação sem efeitos colaterais; parsing de PDF sintético; lock completo e pins mantidos.
- [x] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `build(api): pin source metadata dependencies`

#### T6: Configurar Tailwind e componentes shadcn necessários

**Status**: Complete
**What**: Configurar Tailwind com tokens padrão e primitivas aprovadas; gerar somente componentes usados; validar formulário e diálogo por teclado em fixture sintética.
**Where**: `apps/web/vite.config.ts`
**Supporting**: componentes/configuração gerados, teste Vitest e fixture temporária independente de compatibilidade, servida pelo teste externo no browser. A fixture não depende dos providers ou formulários de produto de T25 em diante e não adiciona rota de teste ao backend.
**Depends on**: T5
**Reuses**: React/Vite, pins e padrão de testes web existentes; componentes gerados nesta tarefa e fixture independente dos providers futuros.
**Requirement**: MONE-03, MONE-33
**Tools**: WEB
**Done when**:
- [x] Tokens padrão; foco retorna ao acionador; Escape e teclado operam diálogo; build com pins.
- [x] Gate FRONT passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t6.test.tsx e apps/web/tests/m1-t6.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: FRONT
**Commit**: `feat(web): establish accessible ui primitives`

### Phase 2: Fronteiras, integridade e política

#### T7: Estender erros HTTP tipados sem eco de input

**Status**: Complete
**What**: Manter envelope error, requestId e fieldErrors seguros para 404/409/413/415/422/429/503; preservar comportamento M0.
**Where**: `backend/api/src/resume_api/errors.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T6
**Reuses**: Envelope de erros e Boundary M0, modelos Pydantic, export offline e TestClient existentes; sem depender da Unit of Work futura.
**Requirement**: MONE-12, MONE-15, MONE-23, MONE-26, MONE-29, MONE-34
**Tools**: PY
**Done when**:
- [x] Erros de campo e de revisão tipados; input sentinela e detalhes internos ausentes; enum/schema exportável offline.
- [x] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t7.py e/ou tests/integration/test_m1_t7.py; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(api): expose safe m1 error contracts`

#### T8: Aplicar política de entrada e escopos por rota

**Status**: Complete
**What**: Autorizar sessão/capability antes de ler bytes; aplicar budgets JSON/multipart, concorrência de preparo e rate limits conforme design.
**Where**: `backend/api/src/resume_api/app.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T7
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-07, MONE-14, MONE-15, MONE-34
**Tools**: PY
**Done when**:
- [x] Sessão ausente e capability negada leem zero bytes/parser; chunked acima do limite falha; 1KiB M0 preservado; 429 explícito.
- [x] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t8.py e/ou tests/integration/test_m1_t8.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(api): authorize bounded m1 requests`

#### T9: Estender allowlists de logs M1

**Status**: Complete
**What**: Permitir eventos/códigos e identificadores estáticos de rota necessários, sem query, nome de arquivo, trecho ou payload privado.
**Where**: `backend/core/src/resume_core/logging_policy.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T8
**Reuses**: Allowlist e testes de logging existentes; captura de sentinelas sintéticas, sem dependência do domínio ou da Unit of Work futura.
**Requirement**: MONE-34
**Tools**: PY
**Done when**:
- [x] Sentinelas de contato, trecho, filename e exceção ausentes em logs da aplicação e dependências.
- [x] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t9.py e/ou tests/integration/test_m1_t9.py; mínimo de 1 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(core): redact career operation logs`

#### T10: Habilitar integridade referencial SQLite

**Status**: Complete
**What**: Habilitar foreign_keys em cada conexão inclusive migration, preservando WAL e busy_timeout atuais.
**Where**: `backend/core/src/resume_core/database.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T9
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-05, MONE-31, MONE-32
**Tools**: PY
**Done when**:
- [x] FK inválida rejeitada por SQL direto; nova conexão também enforce; M0 upgrade/downgrade preservado.
- [x] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t10.py e/ou tests/integration/test_m1_t10.py; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(data): enforce sqlite foreign keys`

#### T11: Criar Unit of Work explícita

**Status**: Complete
**What**: Compartilhar conexão entre repositórios, usar escrita IMMEDIATE e rollback total, com erro seguro de lock e sessões restritas ao trabalho.
**Where**: `backend/core/src/resume_core/persistence/unit_of_work.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T10
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-12, MONE-23, MONE-24, MONE-31, MONE-32
**Tools**: PY
**Done when**:
- [x] Dois escritores serializados ou falha segura; exceção faz rollback; sessão/conexão não escapa após close.
- [x] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t11.py e/ou tests/integration/test_m1_t11.py; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(data): add explicit career unit of work`

#### T12: Migrar identidade, fontes e histórico comum

**Status**: Pending
**What**: Criar envelope KB, fontes, metadados de campo, revisões/fields/proveniência, links, auditoria e recibos básicos com constraints e imutabilidade.
**Where**: `backend/migrations/versions/0002_kb_foundation.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T11
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-04, MONE-05, MONE-08, MONE-13, MONE-27, MONE-30, MONE-32
**Tools**: PY
**Done when**:
- [ ] Upgrade/downgrade/upgrade em banco fictício; preservar M0 e tabela alheia; UPDATE/DELETE histórico negados; FKs válidas.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t12.py e/ou tests/integration/test_m1_t12.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(data): migrate career history foundation`

#### T13: Implementar política e projeções autorizadas

**Status**: Pending
**What**: Resolver capability e classificação por entidade/campo/link/fonte antes dos valores; construir especificação de projeção sem ORM lazy.
**Where**: `backend/core/src/resume_core/career_kb/policy.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T12
**Reuses**: Principal/spies pré-leitura e Unit of Work já disponíveis; metadados/histórico da T12 para testar policy sem depender dos modelos tipados da T19.
**Requirement**: MONE-06, MONE-07, MONE-13, MONE-34
**Tools**: PY
**Done when**:
- [ ] Spy não lê repositório sem capability; public/professional/confidential/secret; campo e fonte mais restritivos; oculto e ausente indistinguíveis.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t13.py e/ou tests/integration/test_m1_t13.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(kb): authorize field and history projections`

### Phase 3: Fontes privadas utilizáveis

#### T14: Implementar armazenamento imutável de fontes

**Status**: Pending
**What**: Instalar bytes por hash em XDG privado com temporário/fsync/rename seguro e manifesto; nunca usar filename recebido como path.
**Where**: `backend/core/src/resume_core/sources/storage.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T13
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-14, MONE-30, MONE-31, MONE-32
**Tools**: PY
**Done when**:
- [ ] Hash igual reutiliza; hash/arquivo divergente bloqueia; traversal/symlink negados; original preservado; crash antes/depois do rename.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t14.py e/ou tests/integration/test_m1_t14.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(sources): store immutable private documents`

#### T15: Implementar leitor limitado de metadados PDF

**Status**: Pending
**What**: Ler somente estrutura/páginas com pypdf estrito em subprocesso limitado; saída mínima e erros sanitizados, sem extração textual.
**Where**: `backend/core/src/resume_core/sources/pdf_metadata.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T14
**Reuses**: Paths privados, subprocessos de teste e política de logs existentes.
**Requirement**: MONE-14, MONE-15, MONE-30, MONE-34
**Tools**: PY
**Done when**:
- [ ] PDF válido, inválido, criptografado, >50 páginas, timeout e memória; warning sentinela não sai; sem chamada de extract_text.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t15.py e/ou tests/integration/test_m1_t15.py; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(sources): inspect bounded pdf metadata`

#### T16: Criar fonte manual privada

**Status**: Pending
**What**: Entregar POST de anotação humana privada com serviço/recibo associado, sem confirmar qualificações; registrar router e SDK no mesmo incremento.
**Where**: `backend/api/src/resume_api/routers/source_notes.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T15
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-03, MONE-06, MONE-22, MONE-27, MONE-30
**Tools**: PY
**Done when**:
- [ ] Fonte manual unverified não é prova externa; repetição idempotente; negativa sem escrita; fonte recuperável pelo proprietário.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t16.py e/ou tests/integration/test_m1_t16.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(sources): record private manual provenance`

#### T17: Consultar e baixar fontes autorizadas

**Status**: Pending
**What**: Entregar componente de leitura de metadados/download attachment, com checagem de escopo e integridade antes de abrir conteúdo.
**Where**: `backend/api/src/resume_api/routers/sources.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T16
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-07, MONE-30, MONE-34
**Tools**: PY
**Done when**:
- [ ] Fonte oculta=404; arquivo adulterado/ausente bloqueia; no-store/attachment; liberar fato não libera PDF; nenhum StaticFiles privado.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t17.py e/ou tests/integration/test_m1_t17.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(sources): serve authorized source attachments`

### Phase 4: Primeiro domínio tipado pela API

#### T18: Formalizar DTOs tipados das entidades KB

**Status**: Pending
**What**: Codificar os nove tipos e comandos aprovados, períodos parciais, null/redigido, metadados e listas; extra forbid e aliases camelCase.
**Where**: `backend/core/src/resume_core/career_kb/contracts.py`
**Supporting**: exports/consumidor gerado e testes positivos/negativos de contrato.
**Depends on**: T17
**Reuses**: Pydantic/OpenAPI/cliente gerado e testes de contrato existentes.
**Requirement**: MONE-03, MONE-09, MONE-10, MONE-12, MONE-17
**Tools**: PY
**Done when**:
- [ ] Round trip dos nove tipos; nullable histórico; confirmação por campo Profile; extras/coerções inválidos; texto/data limites.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t18.py e/ou tests/integration/test_m1_t18.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(kb): define typed career contracts`

#### T19: Mapear e migrar conteúdo tipado das nove entidades

**Status**: Pending
**What**: Criar tabelas tipadas e registry ORM correspondente, com exatamente um tipo por identidade, Profile/filhos e restrições aprovadas.
**Where**: `backend/migrations/versions/0003_kb_entities.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T18
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-03, MONE-04, MONE-05, MONE-08, MONE-32
**Tools**: PY
**Done when**:
- [ ] Nove tipos persistem; kind incorreto/filho sem Profile/registro órfão rejeitados; upgrade/downgrade preserva histórico e M0.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t19.py e/ou tests/integration/test_m1_t19.py; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(data): migrate typed career entities`

#### T20: Implementar repositório de estado e snapshots

**Status**: Pending
**What**: Persistir conteúdo/snapshot/auditoria/recibo na UoW e produzir projeções explícitas; UPDATE condicional por revisão-base e rowcount.
**Where**: `backend/core/src/resume_core/career_kb/repository.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T19
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-03, MONE-07, MONE-09, MONE-12, MONE-13, MONE-24, MONE-25, MONE-26, MONE-27
**Tools**: PY
**Done when**:
- [ ] Atomicidade em falha; snapshot privado filtrado antes dos valores; duas conexões mesma base apenas uma grava; replay/conflito.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t20.py e/ou tests/integration/test_m1_t20.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(kb): persist versioned career records`

#### T21: Implementar criação autorizada de fatos

**Status**: Pending
**What**: Criar os nove tipos unverified com fonte, metadados e revisão inicial, sem promover valores de outros campos ou fatos.
**Where**: `backend/core/src/resume_core/career_kb/create.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T20
**Reuses**: Principal e spies pré-leitura existentes; DTOs/UoW/projeções já disponíveis.
**Requirement**: MONE-03, MONE-06, MONE-10, MONE-22, MONE-25, MONE-26, MONE-27
**Tools**: PY
**Done when**:
- [ ] Nove tipos; fonte obrigatória autorizada; confirmação inicial unverified; chave igual/diferente; spy nega antes da leitura.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t21.py e/ou tests/integration/test_m1_t21.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(kb): create grounded unverified facts`

#### T22: Implementar consultas paginadas da KB

**Status**: Pending
**What**: Listar e detalhar com filtros/offset/limite/ordenação estável e autorização SQL antes dos valores, respeitando orçamento de resposta.
**Where**: `backend/core/src/resume_core/career_kb/queries.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T21
**Reuses**: Principal e spies pré-leitura existentes; DTOs/UoW/projeções já disponíveis.
**Requirement**: MONE-03, MONE-06, MONE-07, MONE-08, MONE-13
**Tools**: PY
**Done when**:
- [ ] 25 default/100 máximo/offset 10000; total só visíveis; nulo distinto de redigido; fonte/contato ocultos; erro sem truncar.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t22.py e/ou tests/integration/test_m1_t22.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(kb): query authorized career records`

#### T23: Expor criação e consulta por rotas concretas

**Status**: Pending
**What**: Registrar fábrica de router tipado para criar/listar/detalhar cada tipo, principal confiável e composição sem efeitos no export offline.
**Where**: `backend/api/src/resume_api/routers/career.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T22
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-03, MONE-06, MONE-07, MONE-12, MONE-22, MONE-34
**Tools**: PY
**Done when**:
- [ ] Nove rotas tipadas e operationIds únicos; principal do body negado; auth/Origin/Host; schema exportado sem abrir DB/arquivo.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t23.py e/ou tests/integration/test_m1_t23.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(api): expose typed career resources`

### Phase 5: Primeiro cadastro completo na UI

#### T24: Integrar consumo TS dos contratos KB

**Status**: Pending
**What**: Consumir requests/resultados/erros gerados em TS e configurar wrapper fetch para rejeitar erros no Query; sem DTO manual.
**Where**: `apps/web/src/shared/api/client.ts`
**Supporting**: consumidor compilável em apps/web/tests/client-contract.ts, exports e testes positivos/negativos; SDK gerado já existe desde a publicação dos endpoints.
**Depends on**: T23
**Reuses**: Pydantic/OpenAPI/cliente gerado e testes de contrato existentes.
**Requirement**: MONE-03, MONE-12, MONE-25, MONE-26, MONE-34
**Tools**: PY
**Done when**:
- [ ] Campos camelCase; erro tipo 409/422 reconhecido; alias inválido não compila; cancelamento propagado; duas gerações iguais.
- [ ] Gate WEB passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — apps/web/tests/m1-t24.test.tsx para comportamento do transporte e apps/web/tests/client-contract.ts para consumo compilável dos tipos; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: WEB
**Commit**: `feat(web): consume generated career contracts`

#### T25: Compor providers e cache por sessão

**Status**: Pending
**What**: Instalar QueryClient e integração de sessão, cache só em memória, defaults aprovados, limpeza/cancelamento em 401 e sem retries automáticos.
**Where**: `apps/web/src/app/providers.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T24
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-06, MONE-07, MONE-12, MONE-33, MONE-34
**Tools**: WEB
**Done when**:
- [ ] Nenhuma chamada privada antes bootstrap; 401 limpa cache/mutations/rascunhos; StrictMode não duplica ticket; refetch não substitui dirty.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t25.test.tsx e apps/web/tests/m1-t25.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): isolate career state by session`

#### T26: Configurar navegação SPA e deep links

**Status**: Pending
**What**: Entregar Data Mode, layout e URLs aprovadas, limpeza de bootstrap e fallback backend limitado à whitelist UI; preservar acesso ao diagnóstico.
**Where**: `apps/web/src/app/router.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T25
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-06, MONE-07, MONE-34
**Tools**: WEB
**Done when**:
- [ ] Refresh em detalhe funciona; /api/inexistente continua JSON404; rota arbitrária não recebe index; ticket removido; M0 em /diagnostics.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t26.test.tsx e apps/web/tests/m1-t26.spec.ts; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): route career features as a spa`

#### T27: Entregar formulário Profile

**Status**: Pending
**What**: Cadastrar Profile com RHF, proveniência por campo, fontes manuais e leitura de erros do SDK; salvar não confirma campos.
**Where**: `apps/web/src/features/career-kb/components/ProfileEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T26
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-09, MONE-10, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Nome/campos desconhecidos preservados; fonte por campo; 422 no campo; sem confirmação conjunta acidental; teclado acessível.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t27.test.tsx e apps/web/tests/m1-t27.spec.ts; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): create profile with field provenance`

#### T28: Entregar lista e detalhe da KB

**Status**: Pending
**What**: Listar/abrir registros via Query com paginação/privacidade/IDs/fontes, sem depender de editor avançado; primeiro checkpoint UI→API→SQLite.
**Where**: `apps/web/src/features/career-kb/pages/CareerRecordsPage.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T27
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-06, MONE-07, MONE-08, MONE-13
**Tools**: WEB
**Done when**:
- [ ] Cadastro Profile aparece com ID/fonte; filtros/offset corretos; arquivados distinguíveis; campos restritos sem valores; processo reiniciado mantém dados.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t28.test.tsx e apps/web/tests/m1-t28.spec.ts; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): browse grounded career records`

### Phase 6: Formulários das demais entidades core

#### T29: Entregar formulário Experience

**Status**: Pending
**What**: Cadastrar experiência com período original/parcial, fonte e privacidade, preservando atualidade histórica e lacunas.
**Where**: `apps/web/src/features/career-kb/components/ExperienceEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T28
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Datas sobrepostas preservadas com aviso; data desconhecida null; Atualmente não vira hoje; round trip com ID/fonte.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t29.test.tsx e apps/web/tests/m1-t29.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): record historical experience`

#### T30: Entregar formulário Project

**Status**: Pending
**What**: Cadastrar projeto com título editorial explícito, texto original e tempo textual sem acrescentar métricas.
**Where**: `apps/web/src/features/career-kb/components/ProjectEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T29
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Título gerado identificado; narrativa/tempo preservados; ausência de métrica explícita; cadastro autorizado com proveniência.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t30.test.tsx e apps/web/tests/m1-t30.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): record sourced projects`

#### T31: Entregar formulário Statement

**Status**: Pending
**What**: Cadastrar declaração individual com original/current e tipo aprovado, sem usar interpretação como confirmação.
**Where**: `apps/web/src/features/career-kb/components/StatementEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T30
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-09, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Responsabilidade/resultado/editorial distintos; original preservado; salvar mantém unverified; fonte recuperável.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t31.test.tsx e apps/web/tests/m1-t31.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): capture individual career statements`

#### T32: Entregar formulário Achievement

**Status**: Pending
**What**: Cadastrar realização com métrica opcional explicitamente fornecida; preservar narrativa sem fabricar valores.
**Where**: `apps/web/src/features/career-kb/components/AchievementEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T31
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Métrica ausente null; métrica fornecida round trip; validação de tipo; nenhuma extração automática de número da narrativa.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t32.test.tsx e apps/web/tests/m1-t32.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): capture supported achievements`

#### T33: Entregar formulário Skill

**Status**: Pending
**What**: Cadastrar skill com rótulos originais e distinção entre listagem explícita e menção, usando contrato gerado.
**Where**: `apps/web/src/features/career-kb/components/SkillEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T32
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Listada e mencionada diferenciadas; não confirma competência; rótulos preservados; registros homônimos mantêm identidades distintas, sem merge automático.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t33.test.tsx e apps/web/tests/m1-t33.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): distinguish listed and mentioned skills`

#### T34: Entregar formulário Education

**Status**: Pending
**What**: Cadastrar formação com datas parciais e separação ongoingAsOfSource/currentlyOngoing, incluindo desconhecido.
**Where**: `apps/web/src/features/career-kb/components/EducationEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T33
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Ongoing histórico não implica atual; currentlyOngoing null preservado; intervalos originais; programa/fonte round trip.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t34.test.tsx e apps/web/tests/m1-t34.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): preserve historical education status`

#### T35: Entregar formulário Language

**Status**: Pending
**What**: Cadastrar idioma com proficiência declarada original, sem converter escala ou certificar capacidade.
**Where**: `apps/web/src/features/career-kb/components/LanguageEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T34
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-17, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Texto de proficiência preservado; sem CEFR inferido; unverified inicial; erros do servidor por campo.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t35.test.tsx e apps/web/tests/m1-t35.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): preserve declared language proficiency`

#### T36: Entregar formulário Evidence

**Status**: Pending
**What**: Cadastrar evidência documental/anotação manual com fonte autorizada, página/trecho; ausência de prova continua explícita.
**Where**: `apps/web/src/features/career-kb/components/EvidenceEditor.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T35
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-06, MONE-07, MONE-14, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Fonte não autorizada oculta; página inválida bloqueada; referência não vira prova independente; original não alterado.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t36.test.tsx e apps/web/tests/m1-t36.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): attach explicit career evidence`

### Phase 7: Relações, revisão e confirmação

#### T37: Criar vínculos autorizados e versionados

**Status**: Pending
**What**: Entregar operação de criação de vínculo com serviço/ORM/UoW, tipos/Profiles/endpoints/revisões verificados e auditoria.
**Where**: `backend/api/src/resume_api/routers/career_links.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T36
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-04, MONE-05, MONE-06, MONE-07, MONE-12, MONE-25, MONE-26, MONE-27
**Tools**: PY
**Done when**:
- [ ] FK/tipo/Profile inválidos rejeitados; ambos endpoints autorizados; revisão obsoleta409; replay não duplica vínculo.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t37.py e/ou tests/integration/test_m1_t37.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): link authorized career entities`

#### T38: Desativar associação preservando história

**Status**: Pending
**What**: Entregar archive de vínculo por nova revisão, sem cascade de fatos/fontes ou perda de revisões anteriores.
**Where**: `backend/api/src/resume_api/routers/career_link_archive.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T37
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-04, MONE-05, MONE-08, MONE-12, MONE-27, MONE-32
**Tools**: PY
**Done when**:
- [ ] Desativação preserva endpoints e história; link base obsoleta409; negativo sem alteração; restart mantém desativação.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t38.py e/ou tests/integration/test_m1_t38.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): archive career associations safely`

#### T39: Entregar associação e consulta de vínculos na UI

**Status**: Pending
**What**: Selecionar vínculos de Skill/Evidence/Statement/Project/Achievement e consultar dados relacionados sem copiar conteúdo canônico.
**Where**: `apps/web/src/features/career-kb/components/EntityLinks.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T38
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-04, MONE-05, MONE-06, MONE-07, MONE-08
**Tools**: WEB
**Done when**:
- [ ] Criar/abrir/desativar vínculo; destino restrito sem conteúdo; evidência ausente explícita; histórico preservado após arquivo.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t39.test.tsx e apps/web/tests/m1-t39.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): manage career relationships`

#### T40: Propor alteração de conteúdo com diff

**Status**: Pending
**What**: Entregar proposta manual com revisão-base, diff autorizado e recibo, sem aplicar ou apagar fonte original.
**Where**: `backend/api/src/resume_api/routers/career_proposals.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T39
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-07, MONE-09, MONE-11, MONE-12, MONE-13, MONE-21, MONE-27
**Tools**: PY
**Done when**:
- [ ] Proposta não altera canônico; diff não revela contato/fonte; base obsoleta409; idempotência; original conservado.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t40.py e/ou tests/integration/test_m1_t40.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): propose reviewable fact changes`

#### T41: Aprovar ou rejeitar proposta explicitamente

**Status**: Pending
**What**: Entregar decisão auditada que aplica revisão unverified da unidade alterada ou rejeita sem mudar estado anterior.
**Where**: `backend/api/src/resume_api/routers/career_decisions.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T40
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-09, MONE-11, MONE-12, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27
**Tools**: PY
**Done when**:
- [ ] Approve/reject; Profile só campo alterado perde confirmação; demais entidades invalidam unidade; corrida duas abas; rollback total.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t41.py e/ou tests/integration/test_m1_t41.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): apply explicit fact review decisions`

#### T42: Confirmar unidades de veracidade

**Status**: Pending
**What**: Entregar confirmação explícita por campo Profile ou entidade restante, vinculada a revisão-base e responsável.
**Where**: `backend/api/src/resume_api/routers/career_confirmations.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T41
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-09, MONE-10, MONE-12, MONE-22, MONE-27
**Tools**: PY
**Done when**:
- [ ] Confirmar nome não confirma contato; campo desconhecido não confirmado; base velha409; confirmação não vem de aceite de import.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t42.py e/ou tests/integration/test_m1_t42.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): confirm reviewed fact units`

#### T43: Arquivar fato sem destruir referências

**Status**: Pending
**What**: Entregar arquivamento auditado com revisão-base; preservar links, snapshots e fontes para leitura autorizada.
**Where**: `backend/api/src/resume_api/routers/career_archive.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T42
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-05, MONE-06, MONE-07, MONE-08, MONE-12, MONE-27, MONE-32
**Tools**: PY
**Done when**:
- [ ] Registro vinculado arquivado sem cascade; história acessível por escopo; consulta padrão e archived explícitos; replay seguro.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t43.py e/ou tests/integration/test_m1_t43.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): archive facts without losing provenance`

#### T44: Consultar revisões e diferenças autorizadas

**Status**: Pending
**What**: Entregar componente de histórico paginado e snapshot/diff por entidade, selecionando campos/trechos só após policy.
**Where**: `backend/api/src/resume_api/routers/career_history.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T43
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-07, MONE-09, MONE-10, MONE-13, MONE-27, MONE-34
**Tools**: PY
**Done when**:
- [ ] Revisão de outra entidade404; snapshot histórico confidencial não carregado indevidamente; diff filtrado; limite resposta sem truncar.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t44.py e/ou tests/integration/test_m1_t44.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(kb): expose authorized fact history`

#### T45: Entregar tela de revisão de fatos

**Status**: Pending
**What**: Comparar revisões, propor/aprovar/rejeitar/confirmar unidade, arquivar e resolver409 mantendo rascunho; concluir CRUD core na UI.
**Where**: `apps/web/src/features/fact-review/pages/FactReviewPage.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T44
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-03, MONE-08, MONE-09, MONE-10, MONE-11, MONE-12, MONE-13, MONE-21, MONE-22, MONE-27
**Tools**: WEB
**Done when**:
- [ ] Editar dois tabs; manter rascunho; rejeitar preserva anterior; confirmação separada; histórico/arquivo; testes parametrizados nos nove tipos.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t45.test.tsx e apps/web/tests/m1-t45.spec.ts; mínimo de 6 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): review facts with explicit confirmation`

### Phase 8: Importação privada para staging

#### T46: Validar schema preparatório do seed

**Status**: Pending
**What**: Definir DTO legado v0.1 estrito e bounds, sem promovê-lo a schema SQL; fixture inteiramente fictícia com todos os tipos.
**Where**: `backend/core/src/resume_core/imports/seed_contracts.py`
**Supporting**: exports/consumidor gerado e testes positivos/negativos de contrato.
**Depends on**: T45
**Reuses**: Pydantic/OpenAPI/cliente gerado e testes de contrato existentes.
**Requirement**: MONE-14, MONE-15, MONE-16, MONE-17, MONE-33
**Tools**: PY
**Done when**:
- [ ] Schema desconhecido, extra, JSON duplicado, NaN, profundidade/contagem/bytes acima do limite; fixture positiva completa.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t46.py e/ou tests/integration/test_m1_t46.py; mínimo de 2 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(imports): validate legacy career seed`

#### T47: Normalizar candidatos e ambiguidades

**Status**: Pending
**What**: Adapter puro transforma seed validado em candidatos privados com mapeamento de IDs/fonte/página, metadados e matching sugerido.
**Where**: `backend/core/src/resume_core/imports/seed_v01.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T46
**Reuses**: Principal e spies pré-leitura existentes; DTOs/UoW/projeções já disponíveis.
**Requirement**: MONE-14, MONE-15, MONE-16, MONE-17, MONE-18, MONE-19, MONE-20
**Tools**: PY
**Done when**:
- [ ] Todos os tipos e links; Profile por campo; listagem/menção; título editorial; datas históricas; legacyId de fontes diferentes não mescla.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t47.py e/ou tests/integration/test_m1_t47.py; mínimo de 6 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(imports): stage grounded seed candidates`

#### T48: Migrar staging e commits de revisão

**Status**: Pending
**What**: Criar batches/candidatos/decisões/commits/itens e identidade dedup, com ORM e constraints de estados e referências.
**Where**: `backend/migrations/versions/0004_kb_imports.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T47
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-16, MONE-18, MONE-19, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27, MONE-28, MONE-29, MONE-32
**Tools**: PY
**Done when**:
- [ ] Transição inválida negada; dedup único; versões-base/links persistidos; downgrade sintético não destrói M0/KB anterior.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t48.py e/ou tests/integration/test_m1_t48.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(data): migrate private import review state`

#### T49: Preparar importação direta e idempotente

**Status**: Pending
**What**: Autorizar, validar arquivos/seed/metadados, instalar fontes duráveis e persistir batch/candidatos/recibo sem fatos canônicos.
**Where**: `backend/core/src/resume_core/imports/prepare.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T48
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-06, MONE-14, MONE-15, MONE-16, MONE-17, MONE-18, MONE-19, MONE-20, MONE-25, MONE-26, MONE-30, MONE-31, MONE-32
**Tools**: PY
**Done when**:
- [ ] Repetição/JSON reformatado reutiliza; seed alterado mesma fonte propõe; falha de arquivo/DB sem batch quebrado; arquivo original preservado.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t49.py e/ou tests/integration/test_m1_t49.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(imports): prepare private review batches`

#### T50: Expor upload PDF e seed limitado

**Status**: Pending
**What**: Entregar POST multipart síncrono com principal/limites prévios e serviços aprovados; gerar cliente upload tipado no mesmo incremento.
**Where**: `backend/api/src/resume_api/routers/import_upload.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T49
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-14, MONE-15, MONE-16, MONE-18, MONE-30, MONE-34
**Tools**: PY
**Done when**:
- [ ] Exatamente dois arquivos; auth antes de parsing/tempfile; hash/página/tipo/limites; filename traversal; chamadas paralelas429; SDK multipart real.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t50.py e/ou tests/integration/test_m1_t50.py; mínimo de 6 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(api): accept bounded career seed uploads`

#### T51: Consultar batch e candidatos privados

**Status**: Pending
**What**: Entregar consultas paginadas, ambiguidades/matches e metadados do batch sem misturar staging com consultas canônicas.
**Where**: `backend/api/src/resume_api/routers/import_candidates.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T50
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-07, MONE-16, MONE-17, MONE-20, MONE-21, MONE-34
**Tools**: PY
**Done when**:
- [ ] Principal sem confidential não acessa; paginação/total corretos; pendentes não aparecem em career; desconhecido distinto de redigido.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t51.py e/ou tests/integration/test_m1_t51.py; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(api): query private import candidates`

#### T52: Entregar seleção e preparo de arquivos na UI

**Status**: Pending
**What**: Selecionar PDF/seed, enviar pelo SDK e abrir batch; mostrar falhas e replay sem persistir arquivos/dados em browser storage.
**Where**: `apps/web/src/features/imports/pages/ImportUploadPage.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T51
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-14, MONE-15, MONE-16, MONE-18, MONE-30, MONE-33, MONE-34
**Tools**: WEB
**Done when**:
- [ ] Upload sintético funciona; erro hash/limite legível; 401 limpa estado; repetição retorna mesmo batch; nenhum path absoluto enviado.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t52.test.tsx e apps/web/tests/m1-t52.spec.ts; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): prepare private career imports`

#### T53: Entregar staging com fontes e correspondências

**Status**: Pending
**What**: Exibir candidatos pending_review, fonte/diff/ambiguidade e sugestões create/update/link/ignore sem autoaplicação.
**Where**: `apps/web/src/features/imports/pages/ImportBatchPage.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T52
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-07, MONE-16, MONE-17, MONE-20, MONE-21, MONE-22
**Tools**: WEB
**Done when**:
- [ ] Itens não confirmados; fontes restritas não vazam; comparação preserva texto; usuário escolhe correspondência; canonical não muda ao abrir.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t53.test.tsx e apps/web/tests/m1-t53.spec.ts; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): inspect staged career candidates`

### Phase 9: Decisões atômicas, undo e recuperação

#### T54: Previsualizar decisões sem aplicar

**Status**: Pending
**What**: Entregar preview da seleção com revisões-base e dependências, action/disposition distintos; não incluir ou aprovar pais implicitamente.
**Where**: `backend/api/src/resume_api/routers/import_preview.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T53
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-07, MONE-12, MONE-20, MONE-21, MONE-22, MONE-23
**Tools**: PY
**Done when**:
- [ ] Create/update/link/ignore e reject distintos; missing parent bloqueia; stale base409; zero escrita canônica no preview; diff autorizado.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t54.py e/ou tests/integration/test_m1_t54.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(imports): preview explicit review decisions`

#### T55: Aplicar decisões em lote atomicamente

**Status**: Pending
**What**: Entregar aplicação individual/lote na mesma UoW com snapshots, links, auditoria e recibo pós-commit, sem confirmar conteúdo aceito.
**Where**: `backend/api/src/resume_api/routers/import_commits.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T54
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-06, MONE-09, MONE-12, MONE-22, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27, MONE-31, MONE-32
**Tools**: PY
**Done when**:
- [ ] Lote válido; um inválido ou revisão velha bloqueia todos; replay original; chave divergente409; perda resposta; confirmação não herdada.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t55.py e/ou tests/integration/test_m1_t55.py; mínimo de 6 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(imports): commit review decisions atomically`

#### T56: Reverter seleção com dependências e revisões-base

**Status**: Pending
**What**: Entregar undo por novas revisões; criação vira arquivo, alteração restaura anterior e qualquer mudança/dependência bloqueia seleção.
**Where**: `backend/api/src/resume_api/routers/import_undo.py`
**Supporting**: serviço/repositório focal, registro do router, DTO/exports necessários, OpenAPI/SDK regenerados e testes da operação.
**Depends on**: T55
**Reuses**: Boundary, Principal, DTOs, Unit of Work, SDK gerado e TestClient já existentes ou entregues antes.
**Requirement**: MONE-05, MONE-06, MONE-08, MONE-12, MONE-25, MONE-26, MONE-27, MONE-28, MONE-29, MONE-30, MONE-31, MONE-32
**Tools**: PY
**Done when**:
- [ ] Undo create/update/link; edição/confirmação/link posterior bloqueiam; lote tudoou nada; hash PDF/seed intactos; replay; rollback.
- [ ] Gate HTTP passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t56.py e/ou tests/integration/test_m1_t56.py; mínimo de 6 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: HTTP
**Commit**: `feat(imports): undo reviewed changes safely`

#### T57: Aplicar revisão individual e em lote na UI

**Status**: Pending
**What**: Selecionar decisões, ver preview/bloqueios e aplicar com intenção idempotente estável; aceitar não confirma fatos.
**Where**: `apps/web/src/features/imports/components/ReviewDecisions.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T56
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-12, MONE-20, MONE-21, MONE-22, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27
**Tools**: WEB
**Done when**:
- [ ] Individual e lote; seleção com conflito permanece; resultado incerto reutiliza chave/comando; alterar intenção cria nova chave; confirma separado.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t57.test.tsx e apps/web/tests/m1-t57.spec.ts; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): apply explicit import review decisions`

#### T58: Entregar revisão e bloqueios do undo na UI

**Status**: Pending
**What**: Selecionar commit/itens, comparar efeitos e solicitar undo; mostrar bloqueios e conservar alterações posteriores.
**Where**: `apps/web/src/features/imports/components/UndoReview.tsx`
**Supporting**: hooks/SDK/layout estritamente necessários, testes Vitest e E2E na mesma tarefa.
**Depends on**: T57
**Reuses**: Providers/SDK/UI kit introduzidos anteriormente e padrão de testes web existente.
**Requirement**: MONE-08, MONE-12, MONE-13, MONE-27, MONE-28, MONE-29, MONE-30
**Tools**: WEB
**Done when**:
- [ ] Undo limpo; edição/link posterior bloqueia seleção inteira; rascunho/dados preservados; fonte continua disponível e sem mudança.
- [ ] Gate BROWSER passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + e2e — apps/web/tests/m1-t58.test.tsx e apps/web/tests/m1-t58.spec.ts; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BROWSER
**Commit**: `feat(web): review safe import reversals`

#### T59: Recuperar manifesto e órfãos com autorização local

**Status**: Pending
**What**: Entregar operação local autorizada que confere referências/manifesta e reporta órfãos privados sem varrer conteúdo antes de autorização ou apagar referenciados.
**Where**: `backend/core/src/resume_core/sources/recovery.py`
**Supporting**: mapping ORM/migration correspondente, fixtures sintéticas e testes de integridade/rollback.
**Depends on**: T58
**Reuses**: Engine/Alembic/paths e isolamento tmp_path existentes; Unit of Work entregue antes quando aplicável.
**Requirement**: MONE-06, MONE-07, MONE-30, MONE-31, MONE-32, MONE-34
**Tools**: PY
**Done when**:
- [ ] Crash entre rename/commit; arquivo faltante/adulterado; dry-run aponta órfãos; sem leitura pré-auth; referenced nunca removido.
- [ ] Gate PY passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: unit + integration — tests/unit/test_m1_t59.py e/ou tests/integration/test_m1_t59.py; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: PY
**Commit**: `feat(sources): reconcile private source manifests`

#### T60: Demonstrar recuperação e fluxo sintético completo

**Status**: Pending
**What**: Ensaio de processo real que combina upload/revisão/lote/undo, perda de resposta, restart e falhas em fronteiras de commit já testadas por operação.
**Where**: `tests/integration/test_m1_process_recovery.py`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T59
**Reuses**: Gates existentes e testes de cada operação já entregues; spec como oráculo.
**Requirement**: MONE-03, MONE-07, MONE-12, MONE-16, MONE-22, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27, MONE-28, MONE-29, MONE-30, MONE-31, MONE-32, MONE-33, MONE-34, MONE-35
**Tools**: VERIFY
**Done when**:
- [ ] HTTP/SQLite reais após restart; nenhum efeito duplicado/estado parcial; relatório separa processo real de mocks; browser completo já verde.
- [ ] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification + integration — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 4 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `test(m1): demonstrate durable synthetic review flow`

### Phase 10: Piloto independente, carga privada e fechamento

#### T61: Verificar piloto sintético independentemente

**Status**: Pending
**What**: Verifier fresco verifica spec por evidência, executa gates e injeta >=5 falhas de comportamento em scratch; PASS_SYNTHETIC antecede qualquer carga real.
**Where**: `.specs/features/m1-career-kb/pilot-validation.md`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T60
**Reuses**: Gates existentes e testes de cada operação já entregues; spec como oráculo.
**Requirement**: MONE-01, MONE-02, MONE-03, MONE-04, MONE-05, MONE-06, MONE-07, MONE-08, MONE-09, MONE-10, MONE-11, MONE-12, MONE-13, MONE-14, MONE-15, MONE-16, MONE-17, MONE-18, MONE-19, MONE-20, MONE-21, MONE-22, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27, MONE-28, MONE-29, MONE-30, MONE-31, MONE-32, MONE-33, MONE-34, MONE-35, MONE-38
**Tools**: VERIFY
**Done when**:
- [ ] Sensor cobre pré-auth, snapshot privado, auto-confirmação, lote parcial, replay e undo; árvore real igual ao baseline; sem PASS final ainda.
- [ ] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification + integration — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 3 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `test(m1): record independent synthetic pilot verification`

#### T62: Exercitar carga privada e revisão humana local

**Status**: Pending
**What**: Após PASS_SYNTHETIC, proprietário seleciona fontes reais; exercitar staging/revisão/undo sem autoaprovar fatos e registrar somente resultado agregado e IDs opacos.
**Where**: `.specs/features/m1-career-kb/private-review.md`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T61
**Reuses**: Piloto fictício independente, UI de staging/undo e fontes privadas já localizadas.
**Requirement**: MONE-14, MONE-16, MONE-17, MONE-18, MONE-19, MONE-20, MONE-21, MONE-22, MONE-23, MONE-27, MONE-28, MONE-29, MONE-30, MONE-36, MONE-37, MONE-38
**Tools**: MANUAL
**Done when**:
- [ ] PDF/seed copiados só em XDG privado; originais intactos; ambiguidades/pending explícitos; sem valores reais em Git/log/CI; humano registra resultado.
- [ ] Gate MANUAL passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: manual + verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: MANUAL
**Commit**: `test(m1): record private import acceptance evidence`

#### T63: Sincronizar operação, contratos e projeção Obsidian

**Status**: Pending
**What**: Documentar comportamento efetivo, comandos existentes, limites/dependências, falhas, dados privados e pendências; reconciliar narrativas/estado sem mudar requisitos.
**Where**: `docs/engineering/m1-career-kb-operation.md`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T62
**Reuses**: Spec/design/contexto aprovados, modelo de esforço e workflow de estados.
**Requirement**: MONE-01, MONE-02, MONE-03, MONE-14, MONE-27, MONE-30, MONE-33, MONE-34, MONE-37, MONE-38
**Tools**: DOC
**Done when**:
- [ ] Links válidos; versões reais; instruções reproduzíveis; snapshot Obsidian fresco se autorizado; não marcar accepted por tarefas apenas.
- [ ] Gate DOC passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: DOC
**Commit**: `docs(m1): document career review operations`

#### T64: Preparar pacote final de aceite e retrospectiva

**Status**: Pending
**What**: Consolidar commits, gates reais, evidência privada minimizada, esforço e pendências; executar checks finais e preparar revisão independente final/humana sem alegar aceite antecipado.
**Where**: `.specs/features/m1-career-kb/acceptance.md`
**Supporting**: testes/evidências e wiring mínimo estritamente necessários ao deliverable.
**Depends on**: T63
**Reuses**: Gates existentes e testes de cada operação já entregues; spec como oráculo.
**Requirement**: MONE-01, MONE-02, MONE-03, MONE-04, MONE-05, MONE-06, MONE-07, MONE-08, MONE-09, MONE-10, MONE-11, MONE-12, MONE-13, MONE-14, MONE-15, MONE-16, MONE-17, MONE-18, MONE-19, MONE-20, MONE-21, MONE-22, MONE-23, MONE-24, MONE-25, MONE-26, MONE-27, MONE-28, MONE-29, MONE-30, MONE-31, MONE-32, MONE-33, MONE-34, MONE-35, MONE-36, MONE-37, MONE-38
**Tools**: VERIFY
**Done when**:
- [ ] 38 critérios mapeados por evidência; CI local/remoto distintos; unknown onde não medido; Verifier final automático após último commit; aceite humano separado.
- [ ] Gate BUILD passa, evidência real registrada; `tasks.md` e rastreabilidade atualizados no mesmo commit.
**Tests**: verification + integration — nenhum arquivo de testes novo obrigatório; verificação descrita na matriz; mínimo de 5 cenários semânticos descritos acima, contagem real registrada na execução.
**Gate**: BUILD
**Commit**: `docs(m1): prepare evidence based acceptance packet`

## Phase Execution Map

A cadeia abaixo é o mapa verificável de dependências. As fases já delimitam
as unidades semânticas; cada seta corresponde ao Depends on da tarefa-alvo.

```text
T1 -> T2
T2 -> T3
T3 -> T4
T4 -> T5
T5 -> T6
T6 -> T7
T7 -> T8
T8 -> T9
T9 -> T10
T10 -> T11
T11 -> T12
T12 -> T13
T13 -> T14
T14 -> T15
T15 -> T16
T16 -> T17
T17 -> T18
T18 -> T19
T19 -> T20
T20 -> T21
T21 -> T22
T22 -> T23
T23 -> T24
T24 -> T25
T25 -> T26
T26 -> T27
T27 -> T28
T28 -> T29
T29 -> T30
T30 -> T31
T31 -> T32
T32 -> T33
T33 -> T34
T34 -> T35
T35 -> T36
T36 -> T37
T37 -> T38
T38 -> T39
T39 -> T40
T40 -> T41
T41 -> T42
T42 -> T43
T43 -> T44
T44 -> T45
T45 -> T46
T46 -> T47
T47 -> T48
T48 -> T49
T49 -> T50
T50 -> T51
T51 -> T52
T52 -> T53
T53 -> T54
T54 -> T55
T55 -> T56
T56 -> T57
T57 -> T58
T58 -> T59
T59 -> T60
T60 -> T61
T61 -> T62
T62 -> T63
T63 -> T64
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | Um deliverable: registrar baseline e esforço da execução | OK; coartefatos limitados ao Supporting |
| T2 | Um deliverable: preparar github actions antes do domínio | OK; coartefatos limitados ao Supporting |
| T3 | Um deliverable: fixar dependências de frontend | OK; coartefatos limitados ao Supporting |
| T4 | Um deliverable: incluir os novos testes nos seletores e harness | OK; coartefatos limitados ao Supporting |
| T5 | Um deliverable: fixar dependências de upload e metadados | OK; coartefatos limitados ao Supporting |
| T6 | Um deliverable: configurar tailwind e componentes shadcn necessários | OK; coartefatos limitados ao Supporting |
| T7 | Um deliverable: estender erros http tipados sem eco de input | OK; coartefatos limitados ao Supporting |
| T8 | Um deliverable: aplicar política de entrada e escopos por rota | OK; coartefatos limitados ao Supporting |
| T9 | Um deliverable: estender allowlists de logs m1 | OK; coartefatos limitados ao Supporting |
| T10 | Um deliverable: habilitar integridade referencial sqlite | OK; coartefatos limitados ao Supporting |
| T11 | Um deliverable: criar unit of work explícita | OK; coartefatos limitados ao Supporting |
| T12 | Um deliverable: migrar identidade, fontes e histórico comum | OK; coartefatos limitados ao Supporting |
| T13 | Um deliverable: implementar política e projeções autorizadas | OK; coartefatos limitados ao Supporting |
| T14 | Um deliverable: implementar armazenamento imutável de fontes | OK; coartefatos limitados ao Supporting |
| T15 | Um deliverable: implementar leitor limitado de metadados pdf | OK; coartefatos limitados ao Supporting |
| T16 | Um deliverable: criar fonte manual privada | OK; coartefatos limitados ao Supporting |
| T17 | Um deliverable: consultar e baixar fontes autorizadas | OK; coartefatos limitados ao Supporting |
| T18 | Um deliverable: formalizar dtos tipados das entidades kb | OK; coartefatos limitados ao Supporting |
| T19 | Um deliverable: mapear e migrar conteúdo tipado das nove entidades | OK; coartefatos limitados ao Supporting |
| T20 | Um deliverable: implementar repositório de estado e snapshots | OK; coartefatos limitados ao Supporting |
| T21 | Um deliverable: implementar criação autorizada de fatos | OK; coartefatos limitados ao Supporting |
| T22 | Um deliverable: implementar consultas paginadas da kb | OK; coartefatos limitados ao Supporting |
| T23 | Um deliverable: expor criação e consulta por rotas concretas | OK; coartefatos limitados ao Supporting |
| T24 | Um deliverable: integrar consumo ts dos contratos kb | OK; coartefatos limitados ao Supporting |
| T25 | Um deliverable: compor providers e cache por sessão | OK; coartefatos limitados ao Supporting |
| T26 | Um deliverable: configurar navegação spa e deep links | OK; coartefatos limitados ao Supporting |
| T27 | Um deliverable: entregar formulário profile | OK; coartefatos limitados ao Supporting |
| T28 | Um deliverable: entregar lista e detalhe da kb | OK; coartefatos limitados ao Supporting |
| T29 | Um deliverable: entregar formulário experience | OK; coartefatos limitados ao Supporting |
| T30 | Um deliverable: entregar formulário project | OK; coartefatos limitados ao Supporting |
| T31 | Um deliverable: entregar formulário statement | OK; coartefatos limitados ao Supporting |
| T32 | Um deliverable: entregar formulário achievement | OK; coartefatos limitados ao Supporting |
| T33 | Um deliverable: entregar formulário skill | OK; coartefatos limitados ao Supporting |
| T34 | Um deliverable: entregar formulário education | OK; coartefatos limitados ao Supporting |
| T35 | Um deliverable: entregar formulário language | OK; coartefatos limitados ao Supporting |
| T36 | Um deliverable: entregar formulário evidence | OK; coartefatos limitados ao Supporting |
| T37 | Um deliverable: criar vínculos autorizados e versionados | OK; coartefatos limitados ao Supporting |
| T38 | Um deliverable: desativar associação preservando história | OK; coartefatos limitados ao Supporting |
| T39 | Um deliverable: entregar associação e consulta de vínculos na ui | OK; coartefatos limitados ao Supporting |
| T40 | Um deliverable: propor alteração de conteúdo com diff | OK; coartefatos limitados ao Supporting |
| T41 | Um deliverable: aprovar ou rejeitar proposta explicitamente | OK; coartefatos limitados ao Supporting |
| T42 | Um deliverable: confirmar unidades de veracidade | OK; coartefatos limitados ao Supporting |
| T43 | Um deliverable: arquivar fato sem destruir referências | OK; coartefatos limitados ao Supporting |
| T44 | Um deliverable: consultar revisões e diferenças autorizadas | OK; coartefatos limitados ao Supporting |
| T45 | Um deliverable: entregar tela de revisão de fatos | OK; coartefatos limitados ao Supporting |
| T46 | Um deliverable: validar schema preparatório do seed | OK; coartefatos limitados ao Supporting |
| T47 | Um deliverable: normalizar candidatos e ambiguidades | OK; coartefatos limitados ao Supporting |
| T48 | Um deliverable: migrar staging e commits de revisão | OK; coartefatos limitados ao Supporting |
| T49 | Um deliverable: preparar importação direta e idempotente | OK; coartefatos limitados ao Supporting |
| T50 | Um deliverable: expor upload pdf e seed limitado | OK; coartefatos limitados ao Supporting |
| T51 | Um deliverable: consultar batch e candidatos privados | OK; coartefatos limitados ao Supporting |
| T52 | Um deliverable: entregar seleção e preparo de arquivos na ui | OK; coartefatos limitados ao Supporting |
| T53 | Um deliverable: entregar staging com fontes e correspondências | OK; coartefatos limitados ao Supporting |
| T54 | Um deliverable: previsualizar decisões sem aplicar | OK; coartefatos limitados ao Supporting |
| T55 | Um deliverable: aplicar decisões em lote atomicamente | OK; coartefatos limitados ao Supporting |
| T56 | Um deliverable: reverter seleção com dependências e revisões-base | OK; coartefatos limitados ao Supporting |
| T57 | Um deliverable: aplicar revisão individual e em lote na ui | OK; coartefatos limitados ao Supporting |
| T58 | Um deliverable: entregar revisão e bloqueios do undo na ui | OK; coartefatos limitados ao Supporting |
| T59 | Um deliverable: recuperar manifesto e órfãos com autorização local | OK; coartefatos limitados ao Supporting |
| T60 | Um deliverable: demonstrar recuperação e fluxo sintético completo | OK; coartefatos limitados ao Supporting |
| T61 | Um deliverable: verificar piloto sintético independentemente | OK; coartefatos limitados ao Supporting |
| T62 | Um deliverable: exercitar carga privada e revisão humana local | OK; coartefatos limitados ao Supporting |
| T63 | Um deliverable: sincronizar operação, contratos e projeção obsidian | OK; coartefatos limitados ao Supporting |
| T64 | Um deliverable: preparar pacote final de aceite e retrospectiva | OK; coartefatos limitados ao Supporting |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Sem predecessor | OK |
| T2 | T1 | T1 -> T2 | OK |
| T3 | T2 | T2 -> T3 | OK |
| T4 | T3 | T3 -> T4 | OK |
| T5 | T4 | T4 -> T5 | OK |
| T6 | T5 | T5 -> T6 | OK |
| T7 | T6 | T6 -> T7 | OK |
| T8 | T7 | T7 -> T8 | OK |
| T9 | T8 | T8 -> T9 | OK |
| T10 | T9 | T9 -> T10 | OK |
| T11 | T10 | T10 -> T11 | OK |
| T12 | T11 | T11 -> T12 | OK |
| T13 | T12 | T12 -> T13 | OK |
| T14 | T13 | T13 -> T14 | OK |
| T15 | T14 | T14 -> T15 | OK |
| T16 | T15 | T15 -> T16 | OK |
| T17 | T16 | T16 -> T17 | OK |
| T18 | T17 | T17 -> T18 | OK |
| T19 | T18 | T18 -> T19 | OK |
| T20 | T19 | T19 -> T20 | OK |
| T21 | T20 | T20 -> T21 | OK |
| T22 | T21 | T21 -> T22 | OK |
| T23 | T22 | T22 -> T23 | OK |
| T24 | T23 | T23 -> T24 | OK |
| T25 | T24 | T24 -> T25 | OK |
| T26 | T25 | T25 -> T26 | OK |
| T27 | T26 | T26 -> T27 | OK |
| T28 | T27 | T27 -> T28 | OK |
| T29 | T28 | T28 -> T29 | OK |
| T30 | T29 | T29 -> T30 | OK |
| T31 | T30 | T30 -> T31 | OK |
| T32 | T31 | T31 -> T32 | OK |
| T33 | T32 | T32 -> T33 | OK |
| T34 | T33 | T33 -> T34 | OK |
| T35 | T34 | T34 -> T35 | OK |
| T36 | T35 | T35 -> T36 | OK |
| T37 | T36 | T36 -> T37 | OK |
| T38 | T37 | T37 -> T38 | OK |
| T39 | T38 | T38 -> T39 | OK |
| T40 | T39 | T39 -> T40 | OK |
| T41 | T40 | T40 -> T41 | OK |
| T42 | T41 | T41 -> T42 | OK |
| T43 | T42 | T42 -> T43 | OK |
| T44 | T43 | T43 -> T44 | OK |
| T45 | T44 | T44 -> T45 | OK |
| T46 | T45 | T45 -> T46 | OK |
| T47 | T46 | T46 -> T47 | OK |
| T48 | T47 | T47 -> T48 | OK |
| T49 | T48 | T48 -> T49 | OK |
| T50 | T49 | T49 -> T50 | OK |
| T51 | T50 | T50 -> T51 | OK |
| T52 | T51 | T51 -> T52 | OK |
| T53 | T52 | T52 -> T53 | OK |
| T54 | T53 | T53 -> T54 | OK |
| T55 | T54 | T54 -> T55 | OK |
| T56 | T55 | T55 -> T56 | OK |
| T57 | T56 | T56 -> T57 | OK |
| T58 | T57 | T57 -> T58 | OK |
| T59 | T58 | T58 -> T59 | OK |
| T60 | T59 | T59 -> T60 | OK |
| T61 | T60 | T60 -> T61 | OK |
| T62 | T61 | T61 -> T62 | OK |
| T63 | T62 | T62 -> T63 | OK |
| T64 | T63 | T63 -> T64 | OK |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Documentação/evidência | verification | verification | OK |
| T2 | Configuração/dependências | verification | verification | OK |
| T3 | Configuração/dependências | verification | verification | OK |
| T4 | Configuração/dependências | verification | verification | OK |
| T5 | Configuração/dependências | verification | verification | OK |
| T6 | UI/estado | unit + e2e | unit + e2e | OK |
| T7 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T8 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T9 | Domínio/policy | unit + integration | unit + integration | OK |
| T10 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T11 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T12 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T13 | Domínio/policy | unit + integration | unit + integration | OK |
| T14 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T15 | Processo limitado | unit + integration | unit + integration | OK |
| T16 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T17 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T18 | Contratos | unit + integration | unit + integration | OK |
| T19 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T20 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T21 | Domínio/policy | unit + integration | unit + integration | OK |
| T22 | Domínio/policy | unit + integration | unit + integration | OK |
| T23 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T24 | Contratos | unit + integration | unit + integration | OK |
| T25 | UI/estado | unit + e2e | unit + e2e | OK |
| T26 | UI/estado | unit + e2e | unit + e2e | OK |
| T27 | UI/estado | unit + e2e | unit + e2e | OK |
| T28 | UI/estado | unit + e2e | unit + e2e | OK |
| T29 | UI/estado | unit + e2e | unit + e2e | OK |
| T30 | UI/estado | unit + e2e | unit + e2e | OK |
| T31 | UI/estado | unit + e2e | unit + e2e | OK |
| T32 | UI/estado | unit + e2e | unit + e2e | OK |
| T33 | UI/estado | unit + e2e | unit + e2e | OK |
| T34 | UI/estado | unit + e2e | unit + e2e | OK |
| T35 | UI/estado | unit + e2e | unit + e2e | OK |
| T36 | UI/estado | unit + e2e | unit + e2e | OK |
| T37 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T38 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T39 | UI/estado | unit + e2e | unit + e2e | OK |
| T40 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T41 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T42 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T43 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T44 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T45 | UI/estado | unit + e2e | unit + e2e | OK |
| T46 | Contratos | unit + integration | unit + integration | OK |
| T47 | Domínio/policy | unit + integration | unit + integration | OK |
| T48 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T49 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T50 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T51 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T52 | UI/estado | unit + e2e | unit + e2e | OK |
| T53 | UI/estado | unit + e2e | unit + e2e | OK |
| T54 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T55 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T56 | Serviço/HTTP | unit + integration | unit + integration | OK |
| T57 | UI/estado | unit + e2e | unit + e2e | OK |
| T58 | UI/estado | unit + e2e | unit + e2e | OK |
| T59 | Persistência/arquivos | unit + integration | unit + integration | OK |
| T60 | Verificação | verification + integration | verification + integration | OK |
| T61 | Verificação | verification + integration | verification + integration | OK |
| T62 | Aceite humano privado | manual + verification | manual + verification | OK |
| T63 | Documentação/evidência | verification | verification | OK |
| T64 | Verificação | verification + integration | verification + integration | OK |

## Requirement-to-Task Matrix

| Requirement | Tasks |
| --- | --- |
| MONE-01 | T2, T4, T61, T63, T64 |
| MONE-02 | T2, T61, T63, T64 |
| MONE-03 | T3, T6, T16, T18, T19, T20, T21, T22, T23, T24, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T39, T45, T60, T61, T63, T64 |
| MONE-04 | T12, T19, T37, T38, T39, T61, T64 |
| MONE-05 | T10, T12, T19, T37, T38, T39, T43, T56, T61, T64 |
| MONE-06 | T8, T13, T16, T17, T21, T22, T23, T25, T26, T28, T36, T37, T39, T40, T42, T43, T44, T49, T50, T51, T54, T55, T56, T59, T61, T64 |
| MONE-07 | T8, T13, T17, T20, T22, T23, T25, T26, T28, T36, T37, T39, T40, T43, T44, T51, T53, T54, T59, T60, T61, T64 |
| MONE-08 | T12, T19, T22, T28, T38, T39, T43, T45, T56, T58, T61, T64 |
| MONE-09 | T18, T20, T27, T31, T40, T41, T42, T44, T45, T55, T61, T64 |
| MONE-10 | T18, T21, T27, T42, T44, T45, T61, T64 |
| MONE-11 | T40, T41, T45, T61, T64 |
| MONE-12 | T7, T11, T18, T20, T23, T24, T25, T37, T38, T40, T41, T42, T43, T45, T54, T55, T56, T57, T58, T60, T61, T64 |
| MONE-13 | T12, T13, T20, T22, T28, T40, T44, T45, T58, T61, T64 |
| MONE-14 | T5, T8, T14, T15, T36, T46, T47, T49, T50, T52, T61, T62, T63, T64 |
| MONE-15 | T5, T7, T8, T15, T46, T47, T49, T50, T52, T61, T64 |
| MONE-16 | T46, T47, T48, T49, T50, T51, T52, T53, T60, T61, T62, T64 |
| MONE-17 | T18, T27, T29, T30, T31, T32, T33, T34, T35, T46, T47, T49, T51, T53, T61, T62, T64 |
| MONE-18 | T47, T48, T49, T50, T52, T61, T62, T64 |
| MONE-19 | T47, T48, T49, T61, T62, T64 |
| MONE-20 | T47, T49, T51, T53, T54, T57, T61, T62, T64 |
| MONE-21 | T40, T45, T51, T53, T54, T57, T61, T62, T64 |
| MONE-22 | T16, T21, T23, T27, T29, T30, T31, T32, T33, T34, T35, T36, T42, T45, T53, T54, T55, T57, T60, T61, T62, T64 |
| MONE-23 | T7, T11, T41, T48, T54, T55, T57, T60, T61, T62, T64 |
| MONE-24 | T11, T20, T41, T48, T55, T57, T60, T61, T64 |
| MONE-25 | T20, T21, T24, T37, T41, T48, T49, T55, T56, T57, T60, T61, T64 |
| MONE-26 | T7, T20, T21, T24, T37, T41, T48, T49, T55, T56, T57, T60, T61, T64 |
| MONE-27 | T12, T16, T20, T21, T37, T38, T40, T41, T42, T43, T44, T45, T48, T55, T56, T57, T58, T60, T61, T62, T63, T64 |
| MONE-28 | T48, T56, T58, T60, T61, T62, T64 |
| MONE-29 | T7, T48, T56, T58, T60, T61, T62, T64 |
| MONE-30 | T5, T12, T14, T15, T16, T17, T49, T50, T52, T56, T58, T59, T60, T61, T62, T63, T64 |
| MONE-31 | T10, T11, T14, T49, T55, T56, T59, T60, T61, T64 |
| MONE-32 | T10, T11, T12, T14, T19, T38, T43, T48, T49, T55, T56, T59, T60, T61, T64 |
| MONE-33 | T2, T3, T4, T5, T6, T25, T46, T52, T60, T61, T63, T64 |
| MONE-34 | T7, T8, T9, T13, T15, T17, T23, T24, T25, T26, T44, T50, T51, T52, T59, T60, T61, T63, T64 |
| MONE-35 | T4, T60, T61, T64 |
| MONE-36 | T62, T64 |
| MONE-37 | T62, T63, T64 |
| MONE-38 | T1, T61, T62, T63, T64 |

## Tools and Execution Choice

| Conjunto | Ferramentas aprovadas |
| --- | --- |
| PY | Serena para navegação simbólica quando útil; terminal/apply_patch, uv/Pytest/Ruff/Alembic; Context7 e docs oficiais para APIs; Git local |
| WEB | Serena quando útil; terminal, pnpm/Vitest/typecheck/build e Playwright Test externo; Context7/docs oficiais; SDK gerado; Git local |
| DOC | Terminal e validadores da skill; Obsidian somente leitura para snapshot fresco e análise de drift; sincronização de escrita no vault só se autorizada |
| VERIFY | Verifier fresco com spec/diff/testes e sensor em scratch; terminal/gates; não corrige implementação |
| MANUAL | Proprietário e UI local; fontes pessoais só em XDG; terminal para hashes agregados; sem ferramentas remotas para conteúdo privado |

Skill principal: tlc-spec-driven em todas as tarefas; skill pdf aplicável
ao spike/leitor de metadados (T5/T15), sem alterar a fonte nem extrair conteúdo.
Conjuntos por tarefa aprovados; overrides futuros devem ser registrados, sem
reabrir a confirmação já obtida. O início foi autorizado às 20:17 (-03).

Se surgir índice CodeGraph no projeto, respeitar o AGENTS e consultá-lo antes
de explorar código; não criar índice por conta própria.
Não há skill de QA Ybera aplicável a este repositório. Browser de testes é
Playwright Test externo; o backend não ganha browser de candidaturas.
Context7 recebe consultas técnicas genéricas, sem dados do currículo.

Este plano tem 64 tarefas em 10 fases. O proprietário escolheu workers
sequenciais por lotes em 2026-11-16 às 20:09 (-03):
- oito lotes de workers para P1 (6), P2 (7), P3+P4 (10), P5 (5),
  P6 (8), P7 (9), P8 (8) e P9 (7), sem concorrência;
- agente principal conduz P10 (4 tarefas), coordena revisão privada humana,
  aciona os Verifiers frescos e prepara o fechamento.

Workers não criam outros agentes. Verificação independente continua
obrigatória. A forma de execução e as ferramentas estão aprovadas; nenhum
agente foi criado. Não começar ou despachar o primeiro lote antes de o
proprietário liberar explicitamente o início.

## Completion and Authorization Boundaries

O escopo aprovado para a futura execução inclui implementação e commits
locais; não inclui push, publicação ou modificação de dados reais fora do
fluxo humano previsto. O início foi liberado explicitamente em 2026-11-16 às 20:17 (-03).
Antes de Execute, ler implement.md integralmente e rodar validate_tasks.
Iniciar registro de esforço na T1, antes de instalações/experimentos.
Se for necessário corrigir baseline/dependência para prosseguir, registrar
a causa e tarefa atômica adicional sem retirar ACs ou esconder falhas.

T61 é gate independente do piloto: PASS_SYNTHETIC, não PASS final do M1.
T62 não autoaprova fatos privados: o humano pode manter pendências explícitas;
sem sua revisão, registrar bloqueio e não fingir que o aceite aconteceu.
Depois de T64 e seu commit, executar automaticamente Verifier final fresco,
sensor e validate_state; somente o relatório final usa validation.md/PASS.
Correções exigem novos gates e re-verificação (limite de três iterações da skill).
O estado accepted depende do aceite humano final; tarefas concluídas não bastam.
Ativar CI remoto e escrever projeção Obsidian dependem das autorizações
respectivas; resultados ausentes permanecem NOT_RUN, sem inventar evidência.
