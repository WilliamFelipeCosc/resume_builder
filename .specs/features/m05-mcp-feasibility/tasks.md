# M0.5 — Tarefas de implementação

**Status:** Em execução — tarefas, matriz de testes e gates aprovados pelo proprietário
em 2026-11-12. T1–T3 concluídas; T4–T20 pendentes.
**Design:** [design.md](design.md), aprovado em 2026-11-12. **Spec:** [spec.md](spec.md).
**Escopo:** REQ-MCP-001, recortes SEC/OPS/QA; AC-M05-001/002; 21 requisitos SPIKE.

## Execution Protocol

Usar a skill `tlc-spec-driven` e seu fluxo Execute/Critical Rules. Se indisponível,
parar e informar. Uma tarefa por vez, testes pertinentes na mesma tarefa, gate verde
e atualização de tasks/spec antes do commit atômico Conventional Commits. Testes
assertam resultados da especificação; não espelham a implementação. Sem push/deploy.

`Where` identifica um único componente primário. Testes, imports e wiring mínimos
necessários para tornar esse componente verificável entram no mesmo commit; não
há autorização para agrupar componentes independentes. Todos os checks abaixo são
planejados: nenhum resultado de runtime M0.5 é alegado nesta fase.

Depois de T20, Verifier independente obrigatório (autor diferente), sem pergunta
adicional: checar cada requisito, evidências live e sensor em cópia isolada; escrever
validation.md com PASS/FAIL e file:line. Nunca simular aprovação visual do proprietário.
Ausência de cliente/conferência mantém o gate pendente. Até 60 minutos de investigação
ativa por cliente antes de apresentar diagnóstico e reavaliar.

## Test Coverage Matrix

Proveniência: AGENTS.md, docs/engineering/testing.md, docs/engineering/development.md,
docs/roadmap/acceptance-criteria.md, pyproject.toml, justfile e spec/design aprovados.
Amostras: test_diagnostic_contracts, test_diagnostic_service, test_diagnostic_repository,
test_diagnostic_migration, test_session_channel e test_workspace. Nomes abaixo para
as suites do spike são novos alvos planejados, criados com cada componente.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Workspace | smoke | Imports reais sem efeitos, pins/lock e pacote | tests/smoke/test_mcp_spike_workspace.py | Smoke focal |
| Contratos | unit | Campos/aliases/tipos/limites e todos os negativos do desenho | tests/unit/mcp_spike/test_contracts.py | Quick focal |
| Fixture | unit | Contexto fictício válido e formulário estático coerente, sem valores pré-preenchidos | tests/unit/mcp_spike/test_*fixture.py | Quick focal |
| Política/perfis | unit + integration | Negação antes de I/O de domínio, escopo, UID/permissões, symlinks e remoção | tests/unit/mcp_spike/test_policy.py; tests/integration/mcp_spike/test_profiles.py | Full focal |
| Persistência | integration | SQLite real: constraints, commit/replay/conflito, locks, restart e dois processos | tests/integration/mcp_spike/test_database.py; test_repository.py | Full focal |
| Migração | integration | Upgrade/downgrade e preservação de tabelas não relacionadas | tests/integration/mcp_spike/test_migration.py | Full focal |
| Serviço | unit | Cada REQ aplicável e falhas, sem acesso não autorizado a fixture/repositório | tests/unit/mcp_spike/test_*service.py | Quick focal |
| Logging | unit + integration | Sem echo de segredos/inputs rejeitados; stdout somente protocolo e stderr sanitizado | tests/unit/mcp_spike/test_logging.py; tests/integration/mcp_spike/test_dependency_logging.py | Full focal |
| Adapter MCP | integration | Subprocesso stdio/SDK: negotiation, schemas, duas tools, resultados e todos os negativos | tests/integration/mcp_spike/test_stdio_adapter.py | Full focal |
| Operação | integration ou smoke | Init/serve/reports com isolamento, migração explícita, comandos e encerramento | tests/integration/mcp_spike/test_operations.py; tests/smoke/test_mcp_spike_commands.py | Full focal ou Smoke focal conforme tarefa |
| Servidor fake | integration | Somente assets fixos em loopback; Host, traversal e POST negados | tests/integration/mcp_spike/test_form_server.py | Full focal |
| Documentação | documental | Links/comandos/fontes correspondem ao código e não contêm dados privados | docs/engineering/m05-mcp-operation.md | Documental |
| Live CLI | live | Hermes e Codex reais: list/get/report/replay; versões e recibos | .specs/features/m05-mcp-feasibility/live/ | Live CLI |
| Live formulário | live + UAT | Quatro comparações humanas, ausência de envio, recibo externo | .specs/features/m05-mcp-feasibility/live/form-demo.md | Live formulário |
| Evidência integrada | integration + smoke + live evidence | Todos os gates e REQs, sem substituir live por mocks | .specs/features/m05-mcp-feasibility/execution.md | Build integrado |

## Gate Check Commands

Comandos derivados dos runners existentes; novos alvos/receitas só serão usados
após serem criados pela tarefa indicada. Seleção focal lista os arquivos exatos em
cada tarefa, sem esconder falhas preexistentes. Não criar nova dependência de teste
sem justificar; preferir asyncio.run/harness subprocesso com stack já disponível.

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick focal | Unitários do componente | uv run --all-packages --locked pytest ARQUIVOS_DA_TAREFA -q --basetemp=/tmp/rb-m05-tests |
| Full focal | Integração e unitários do componente | Mesmo runner com todos os arquivos da tarefa; SQLite/processos reais isolados |
| Smoke focal | Workspace/comandos | Mesmo runner com testes/smoke indicados; em T1, uv sync --all-packages --locked e imports reais |
| Lint | Cada tarefa que altera código | uv run --all-packages --locked ruff check backend tests tools; uv run --all-packages --locked ruff format --check backend tests tools; git diff --check |
| Fim de fase | Todos os componentes entregues | just check-python; just lint; a partir de T15, just check-mcp-spike |
| Build integrado | T20 e Verifier | PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check; just check-mcp-spike; uv sync --all-packages --locked; pnpm install --frozen-lockfile |
| Documental | T16 e alterações documentais | Links locais, whitespace, comandos --help/dry-run implementados e comparação dos fragmentos com schemas; sem afirmar runtime por inspeção |
| Live CLI | T17/T18, manual/controlado | Comandos de cliente efetivos definidos e verificados em T16; tools/list + get_application_context + report_application_progress + replay, com recibos reais |
| Live formulário | T19 com proprietário | just mcp-spike-form e cliente externo escolhido; quatro comparações visuais + recibo form_filled + parada sem envio |

As contagens por tarefa são mínimos de cenários planejados, não resultados nem
substitutos da matriz. Registrar quantidade real, casos e comando após executar;
nenhuma remoção/skip de teste silencioso. Checks determinísticos não invocam providers.
Execuções live usam configuração explícita existente; sem troca automática de modelo
ou fallback para API paga. Nenhum comando novo deste plano é alegado como existente.

## Execution Plan

Execução sequencial. Cada tarefa depende da anterior para manter um único fluxo
revisável; dependências transitivas estão cobertas. Quatro fases de 5, 4, 6 e 5
tarefas; na modalidade delegada, quatro lotes sequenciais sem dividir fases.
Não iniciar workers sem escolha explícita do proprietário. Verifier final é sempre
independente, inclusive quando o agente principal executar todas as tarefas.

```
T1 -> T2 -> T3 -> T4 -> T5 -> T6 -> T7 -> T8 -> T9 -> T10 -> T11 -> T12 -> T13 -> T14 -> T15 -> T16 -> T17 -> T18 -> T19 -> T20
```

## Task Breakdown

### Phase 1: Contratos e preparação

### T1: Workspace FastMCP reproduzível

**What**: Adicionar o membro uv e seu pacote importável com FastMCP 4.1.8, preservando pins existentes e sem iniciar servidor por import.
**Where**: `backend/mcp_server/pyproject.toml`
**Depends on**: None
**Reuses**: uv workspace e evidência research/.
**Requirement**: SPIKE-04, SPIKE-16, SPIKE-18
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [x] Importar core/adapter em diretório vazio não cria arquivos nem escreve stdout; versão instalada e lock concordam; registrar SDK efetivo.
- [x] Cobertura da camada Workspace satisfeita, com pelo menos 3 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [x] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: smoke — tests/smoke/test_mcp_spike_workspace.py
**Gate**: Smoke focal: uv run --all-packages --locked pytest tests/smoke/test_mcp_spike_workspace.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): bootstrap pinned FastMCP workspace`

**Evidência T1**: `uv sync --all-packages --locked` passou; smoke focal 3 passed;
ruff check e ruff format --check passaram; `git diff --check` passou. Os 31 pins
de registry anteriores foram preservados. FastMCP 4.1.8 e MCP 2.3.0 instalados.
Os testes em `tests/smoke/test_mcp_spike_workspace.py` conferem saída vazia e
diretório vazio (linhas 16–18) e as duas versões (linhas 22 e 26). Cada assert
corresponde ao critério de importação sem efeitos ou versão fixada de T1; os
testes seguem `docs/engineering/testing.md`. Adequação: critérios T1 cobertos,
sem casos fora do escopo. Os requisitos e ACs completos continuam pendentes.

### T2: Contratos Pydantic do spike

**What**: Implementar DTOs e envelopes m05.v1 com aliases, eventos e limites aprovados.
**Where**: `backend/core/src/resume_core/mcp_spike/contracts.py`
**Depends on**: T1
**Reuses**: Pydantic 2 e padrão de contratos do core.
**Requirement**: SPIKE-01, SPIKE-02, SPIKE-06, SPIKE-11, SPIKE-19
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [x] Entradas planas e saídas aprovadas fazem roundtrip; extras/coerções/IDs inválidos são rejeitados; fronteiras 128/129, 2000/2001, 4096/4097 e 16384/16385 e Unicode têm resultados explícitos.
- [x] Cobertura da camada Contratos satisfeita, com pelo menos 18 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [x] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit — tests/unit/mcp_spike/test_contracts.py
**Gate**: Quick focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_contracts.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): define strict spike wire contracts`

**Evidência T2**: teste focal 28 passed; ruff check, format --check e git diff
--check passaram. `test_contracts.py`: linhas 14–43 verificam aliases, IDs,
tipos, eventos e extras; linhas 46–66 conferem limites de caracteres e bytes,
inclusive UTF-8; linhas 69 em diante verificam roundtrip de contexto/recibo,
UUIDs, ausência de confirmação e envelope excedente. Esses testes correspondem
aos critérios de T2; a validação em transporte e autorização permanece pendente.

### T3: Contexto sintético versionado

**What**: Criar a única fixture de candidatura fictícia com quatro valores, resposta fixa pré-aprovada no cenário e referências sintéticas explícitas.
**Where**: `data/synthetic/mcp-spike/context.json`
**Depends on**: T2
**Reuses**: Contrato T2 e exemplos sintéticos docs/contracts.
**Requirement**: SPIKE-02, SPIKE-04, SPIKE-12, SPIKE-14
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [x] Fixture valida no DTO, cabe nos limites e contém app-demo; approvedAnswer corresponde à approvedAnswers; referências não apontam a private, KB real ou arquivos pessoais.
- [x] Cobertura da camada Fixture satisfeita, com pelo menos 4 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [x] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit — tests/unit/mcp_spike/test_fixture.py
**Gate**: Quick focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_fixture.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): add fictional application context fixture`

**Evidência T3**: 4 testes focais passaram; ruff check, format --check e
git diff --check passaram. `test_fixture.py` linhas 9–12 validam o DTO e tamanho;
linhas 15–18 conferem candidatura/resposta; linhas 21–24 as referências sintéticas;
linhas 27–30 conferem restrições explícitas. A demonstração real permanece pendente.

### T4: Perfis locais e política de capacidades

**What**: Carregar o perfil local restrito e construir o principal usado para autorizar operações e candidatura.
**Where**: `backend/core/src/resume_core/mcp_spike/policy.py`
**Depends on**: T3
**Reuses**: Principal/require e EnvironmentPaths existentes, sem reusar sessão Web.
**Requirement**: SPIKE-03, SPIKE-04, SPIKE-10, SPIKE-18, SPIKE-19
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Perfis Hermes/Codex têm o schema aprovado; faltas/extras/wildcards/permissões/UID/symlinks inválidos falham fechado; clientId de tool não amplia acesso e nenhum segredo é necessário.
- [ ] Cobertura da camada Política/perfis satisfeita, com pelo menos 12 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit + integration — tests/unit/mcp_spike/test_policy.py tests/integration/mcp_spike/test_profiles.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_policy.py tests/integration/mcp_spike/test_profiles.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): enforce local profile capabilities`

### T5: Metadados e engine SQLite isolados

**What**: Definir tabela e engine exclusivos do ambiente mcp-spike com PK, UNIQUE, CHECKs e timestamp UTC aprovados.
**Where**: `backend/core/src/resume_core/mcp_spike/database.py`
**Depends on**: T4
**Reuses**: SQLAlchemy 2, WAL e timeout do engine atual; create_all somente na fixture de teste de metadados.
**Requirement**: SPIKE-04, SPIKE-07, SPIKE-08, SPIKE-09, SPIKE-11, SPIKE-21
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Oito colunas obrigatórias, tipos e constraints conferem com o desenho; testes usam SQLite temporário e não alteram banco M0; nenhum I/O ocorre por import.
- [ ] Cobertura da camada Persistência satisfeita, com pelo menos 7 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration — tests/integration/mcp_spike/test_database.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/integration/mcp_spike/test_database.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): define isolated report storage`

### Phase 2: Persistência e serviços

### T6: Migração Alembic do armazenamento sintético

**What**: Criar histórico Alembic próprio e reversível para a tabela aprovada.
**Where**: `backend/mcp_server/migrations/versions/0001_spike_reports.py`
**Depends on**: T5
**Reuses**: Alembic e padrão de engine explícito, com env/config mínimos próprios.
**Requirement**: SPIKE-04, SPIKE-07, SPIKE-11
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Upgrade/downgrade/upgrade passam em banco temporário; tabela não relacionada é preservada; histórico M0 não é alterado e schema antigo é detectável.
- [ ] Cobertura da camada Migração satisfeita, com pelo menos 4 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration — tests/integration/mcp_spike/test_migration.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/integration/mcp_spike/test_migration.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): migrate synthetic report database`

### T7: Repositório transacional idempotente

**What**: Persistir o relato com unicidade e devolver recibo somente após commit, resolvendo replay e conflito.
**Where**: `backend/core/src/resume_core/mcp_spike/repository.py`
**Depends on**: T6
**Reuses**: Metadados/migração T5–T6 e transações SQLAlchemy.
**Requirement**: SPIKE-06, SPIKE-07, SPIKE-08, SPIKE-09, SPIKE-20, SPIKE-21
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Replay preserva recibo/registro/timestamp; conteúdo diferente não altera original; falha de commit/lock não retorna sucesso; reinício e dois processos concorrentes produzem um único evento por chave.
- [ ] Cobertura da camada Persistência satisfeita, com pelo menos 10 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration — tests/integration/mcp_spike/test_repository.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/integration/mcp_spike/test_repository.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): persist idempotent progress receipts`

### T8: Serviço autorizado de consulta

**What**: Implementar get_application_context como Application Service sem dependência de transporte.
**Where**: `backend/core/src/resume_core/mcp_spike/service.py`
**Depends on**: T7
**Reuses**: DTOs, fixture e política; spies observam ausência de recuperação antes de autorização.
**Requirement**: SPIKE-02, SPIKE-03, SPIKE-04, SPIKE-18, SPIKE-19
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Contexto autorizado coincide com a fixture; principal ausente/sem capacidade/candidatura fora de escopo não recupera dados; fixture concedida ausente falha sem inventar contexto.
- [ ] Cobertura da camada Serviço satisfeita, com pelo menos 8 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit — tests/unit/mcp_spike/test_context_service.py
**Gate**: Quick focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_context_service.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): authorize synthetic context retrieval`

### T9: Serviço autorizado de relato

**What**: Implementar report_application_progress usando identidade local, política e repositório transacional.
**Where**: `backend/core/src/resume_core/mcp_spike/service.py`
**Depends on**: T8
**Reuses**: Serviço T8, repositório T7 e política T4.
**Requirement**: SPIKE-06, SPIKE-08, SPIKE-09, SPIKE-10, SPIKE-11, SPIKE-15, SPIKE-18, SPIKE-20
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Relato permitido produz receiptId e reported_by_agent; principal sem escrita não acessa repositório; nenhum argumento permite confirmação ou outro cliente; erros/replay conservam semântica aprovada.
- [ ] Cobertura da camada Serviço satisfeita, com pelo menos 8 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit — tests/unit/mcp_spike/test_progress_service.py
**Gate**: Quick focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_progress_service.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): authorize progress reporting`

### Phase 3: Servidor MCP e cenário local

### T10: Logging MCP sanitizado

**What**: Adicionar categorias estritamente necessárias do spike mantendo a política de allowlist e saída stderr.
**Where**: `backend/core/src/resume_core/logging_policy.py`
**Depends on**: T9
**Reuses**: configure_logging/sanitize_event atuais; logs não substituem auditoria persistida.
**Requirement**: SPIKE-04, SPIKE-05, SPIKE-16
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Sentinelas em valores/exceções não aparecem nos streams; eventos úteis permanecem identificáveis; dependências não contaminam stdout e regressão da política M0 passa.
- [ ] Cobertura da camada Logging satisfeita, com pelo menos 6 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit + integration — tests/unit/mcp_spike/test_logging.py tests/integration/mcp_spike/test_dependency_logging.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_logging.py tests/integration/mcp_spike/test_dependency_logging.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): sanitize protocol process logging`

### T11: Adapter FastMCP com duas ferramentas

**What**: Registrar exatamente as duas tools com assinaturas planas e traduzir serviços/erros em resultados MCP seguros.
**Where**: `backend/mcp_server/src/resume_mcp_server/server.py`
**Depends on**: T10
**Reuses**: FastMCP pinado, contratos e serviços; harness de subprocesso injeta composição temporária sem depender da CLI ainda não criada.
**Requirement**: SPIKE-01, SPIKE-02, SPIKE-03, SPIKE-05, SPIKE-06, SPIKE-10, SPIKE-11, SPIKE-18, SPIKE-19, SPIKE-20
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Cliente SDK negocia subprocesso stdio e confere tools/list, schemas e saídas; extras/coerções/tamanhos falham sem efeito; erros usam isError e códigos seguros sem echo; nenhuma tool genérica é exposta.
- [ ] Cobertura da camada Adapter MCP satisfeita, com pelo menos 12 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration — tests/integration/mcp_spike/test_stdio_adapter.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/integration/mcp_spike/test_stdio_adapter.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): expose scoped stdio tools`

### T12: CLI de composição e ciclo de vida

**What**: Implementar comandos locais específicos de init, serve e inspeção de relatos, com perfis/paths privados e migração explícita.
**Where**: `backend/mcp_server/src/resume_mcp_server/__main__.py`
**Depends on**: T11
**Reuses**: Composição do adapter, migration própria e EnvironmentPaths; fechar engine no fim do processo.
**Requirement**: SPIKE-04, SPIKE-05, SPIKE-07, SPIKE-08, SPIKE-16, SPIKE-18, SPIKE-19
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Init prepara apenas ambiente sintético; serve exige perfil e schema válido sem migrar silenciosamente; restart preserva recibos; perfil removido bloqueia novas sessões; inspeção filtra perfil e não aceita SQL/path arbitrário.
- [ ] Cobertura da camada Operação satisfeita, com pelo menos 10 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration — tests/integration/mcp_spike/test_operations.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/integration/mcp_spike/test_operations.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): add scoped local lifecycle commands`

### T13: Formulário HTML fictício

**What**: Criar formulário estático de quatro campos rotulados sem pré-preencher valores nem executar submissão.
**Where**: `data/synthetic/mcp-spike/form.html`
**Depends on**: T12
**Reuses**: Sem biblioteca UI nova; fixture serve ao navegador do agente externo.
**Requirement**: SPIKE-04, SPIKE-12, SPIKE-13, SPIKE-14
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Campos/rótulos correspondem aos quatro valores aprovados; não há valores de resposta no HTML nem script/browser runner; controle de envio é inerte e a página identifica claramente o experimento.
- [ ] Cobertura da camada Fixture satisfeita, com pelo menos 4 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: unit — tests/unit/mcp_spike/test_form_fixture.py
**Gate**: Quick focal: uv run --all-packages --locked pytest tests/unit/mcp_spike/test_form_fixture.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): add local fictional application form`

### T14: Servidor local restrito do formulário

**What**: Servir somente os assets fixos do formulário em loopback, validando Host e rejeitando submissões e caminhos arbitrários.
**Where**: `backend/mcp_server/src/resume_mcp_server/form_server.py`
**Depends on**: T13
**Reuses**: Biblioteca padrão Python e testes HTTPX existentes; não muda API M0.
**Requirement**: SPIKE-04, SPIKE-12, SPIKE-13
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] GET esperado funciona; Host inválido, traversal, arquivos fora da whitelist e POST não são aceitos; sem listagem de diretórios, browser integrado ou endpoint MCP HTTP.
- [ ] Cobertura da camada Servidor fake satisfeita, com pelo menos 8 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration — tests/integration/mcp_spike/test_form_server.py
**Gate**: Full focal: uv run --all-packages --locked pytest tests/integration/mcp_spike/test_form_server.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `feat(mcp): serve the restricted demo form`

### T15: Comandos just reproduzíveis do spike

**What**: Disponibilizar wrappers init/serve/form/reports/check específicos, mantendo o ciclo Redis e os checks atuais.
**Where**: `justfile`
**Depends on**: T14
**Reuses**: Receitas uv --all-packages --locked e lint existentes; comandos ainda não existem no momento deste plano.
**Requirement**: SPIKE-04, SPIKE-16, SPIKE-18
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] just --list e invocações de ajuda/dry-run apontam para comandos implementados; nenhuma instalação ocorre em serve; check-mcp-spike roda apenas suites determinísticas, nunca CLIs/providers live.
- [ ] Cobertura da camada Operação satisfeita, com pelo menos 4 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: smoke — tests/smoke/test_mcp_spike_commands.py
**Gate**: Smoke focal: uv run --all-packages --locked pytest tests/smoke/test_mcp_spike_commands.py -q --basetemp=/tmp/rb-m05-tests; Lint
**Commit**: `chore(mcp): wire reproducible local commands`

### Phase 4: Operação e validação real

### T16: Runbook de operação e compatibilidade

**What**: Documentar invocações, perfis e fragmentos sanitizados para Hermes/Codex com versões efetivas, ambiente mínimo e procedimento live.
**Where**: `docs/engineering/m05-mcp-operation.md`
**Depends on**: T15
**Reuses**: Runbook M0, ADR-016 e desenho; OpenAI Docs para configurar Codex e documentação oficial Hermes.
**Requirement**: SPIKE-04, SPIKE-12, SPIKE-13, SPIKE-14, SPIKE-16, SPIKE-17
**Tools**: Terminal/patch/git; Serena; Context7; fontes oficiais; skills tlc-spec-driven e OpenAI Docs para Codex. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Comandos já existem e são verificáveis; tempo de investigação e diagnóstico estão definidos; fonte oficial orienta clientes; detalhes/credenciais pessoais não são copiados e edição global não é presumida.
- [ ] Cobertura da camada Documentação satisfeita, com pelo menos 3 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: documental — Links locais, comandos --help e comparação dos fragmentos com o contrato implementado
**Gate**: Documental
**Commit**: `docs(mcp): document local compatibility procedure`

### T17: Compatibilidade real Hermes

**What**: Executar descoberta, consulta, relato e replay em Hermes real, registrando versões e evidências sanitizadas.
**Where**: `.specs/features/m05-mcp-feasibility/live/hermes.md`
**Depends on**: T16
**Reuses**: Runbook T16, perfis e MCP implementados; launcher Hermes com bloqueio de lock ainda precisa de execução em ambiente permitido.
**Requirement**: SPIKE-01, SPIKE-02, SPIKE-05, SPIKE-06, SPIKE-08, SPIKE-11, SPIKE-16, SPIKE-17
**Tools**: Terminal/git e cliente CLI externo com suas próprias ferramentas; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Quatro verificações passam em cliente real, com fixture/versionamento e recibos; se houver falha, manter tarefa pendente e apresentar diagnóstico após até 60 min, sem reparar instalação ou trocar provider silenciosamente.
- [ ] Cobertura da camada Live CLI satisfeita, com pelo menos 4 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: live — Sessão Hermes real; checklist discovery/context/progress/replay e recibos persistidos
**Gate**: Live CLI
**Commit**: `test(mcp): record Hermes compatibility evidence`

### T18: Compatibilidade real Codex

**What**: Executar descoberta, consulta, relato e replay em Codex real, registrando versões e evidências sanitizadas.
**Where**: `.specs/features/m05-mcp-feasibility/live/codex.md`
**Depends on**: T17
**Reuses**: Runbook T16, serviços e perfil Codex; skill OpenAI Docs para configuração suportada.
**Requirement**: SPIKE-01, SPIKE-02, SPIKE-05, SPIKE-06, SPIKE-08, SPIKE-11, SPIKE-16, SPIKE-17
**Tools**: Terminal/patch/git; Serena; Context7; fontes oficiais; skills tlc-spec-driven e OpenAI Docs para Codex. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Quatro verificações passam no cliente real e o resultado não é inferido do teste SDK; registrar versão executada (inventário inicial 0.167.1), limites e diagnóstico se necessário; sem mudar provider silenciosamente.
- [ ] Cobertura da camada Live CLI satisfeita, com pelo menos 4 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: live — Sessão Codex real; checklist discovery/context/progress/replay e recibos persistidos
**Gate**: Live CLI
**Commit**: `test(mcp): record Codex compatibility evidence`

### T19: Demonstração externa com conferência do proprietário

**What**: Demonstrar uma CLI real obtendo valores por MCP, preenchendo o formulário e relatando progresso, sem enviar.
**Where**: `.specs/features/m05-mcp-feasibility/live/form-demo.md`
**Depends on**: T18
**Reuses**: Formulário T13–T14, MCP e evidências das duas CLIs; não entregar valores diretamente no prompt externo.
**Requirement**: SPIKE-04, SPIKE-11, SPIKE-12, SPIKE-13, SPIKE-14, SPIKE-15, SPIKE-16
**Tools**: Terminal/git e cliente CLI externo com suas próprias ferramentas; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] Cliente escolhido por capacidade real de browser usa suas próprias ferramentas; proprietário confirma cada campo; recibo de progresso é separado da conferência; sem presença/conferência não há PASS de AC-M05-002.
- [ ] Cobertura da camada Live formulário satisfeita, com pelo menos 6 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: live + UAT — Quatro comparações visuais pelo proprietário, recibo form_filled e registro de parada sem envio
**Gate**: Live formulário
**Commit**: `test(mcp): record external form demonstration`

### T20: Evidência integrada e entrega ao Verifier

**What**: Registrar checks integrados, versões e resultado de cada requisito/AC para revisão independente após o último commit de tarefa.
**Where**: `.specs/features/m05-mcp-feasibility/execution.md`
**Depends on**: T19
**Reuses**: Gates existentes, novas suites e registros de execução; Verifier executa depois deste commit.
**Requirement**: SPIKE-01, SPIKE-02, SPIKE-03, SPIKE-04, SPIKE-05, SPIKE-06, SPIKE-07, SPIKE-08, SPIKE-09, SPIKE-10, SPIKE-11, SPIKE-12, SPIKE-13, SPIKE-14, SPIKE-15, SPIKE-16, SPIKE-17, SPIKE-18, SPIKE-19, SPIKE-20, SPIKE-21
**Tools**: Terminal/patch/git; Serena para navegação; Context7 e fontes oficiais quando depender de API; skill tlc-spec-driven. Proposta de ferramentas ainda sujeita à escolha do proprietário.
**Done when**:

- [ ] just check e check-mcp-spike passam, lock/workspace reproduzíveis e evidências dos 21 requisitos são referenciadas; contagens reais e limitações explícitas; nenhuma compatibilidade fictícia apresentada como live.
- [ ] Cobertura da camada Evidência integrada satisfeita, com pelo menos 21 cenários/checks pertinentes planejados; contagem e evidência reais registradas, sem exclusões silenciosas.
- [ ] Gate indicado passa; task/spec atualizados no mesmo commit atômico, sem alegar conclusão de AC ainda pendente.

**Tests**: integration + smoke + live evidence — Suites existentes e do spike, lock/Compose quando aplicável, registros live T17–T19
**Gate**: Build integrado
**Commit**: `test(mcp): record integrated milestone evidence`

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | Um componente: workspace fastmcp reproduzível; testes e wiring necessários no mesmo commit | OK |
| T2 | Um componente: contratos pydantic do spike; testes e wiring necessários no mesmo commit | OK |
| T3 | Um componente: contexto sintético versionado; testes e wiring necessários no mesmo commit | OK |
| T4 | Um componente: perfis locais e política de capacidades; testes e wiring necessários no mesmo commit | OK |
| T5 | Um componente: metadados e engine sqlite isolados; testes e wiring necessários no mesmo commit | OK |
| T6 | Um componente: migração alembic do armazenamento sintético; testes e wiring necessários no mesmo commit | OK |
| T7 | Um componente: repositório transacional idempotente; testes e wiring necessários no mesmo commit | OK |
| T8 | Um componente: serviço autorizado de consulta; testes e wiring necessários no mesmo commit | OK |
| T9 | Um componente: serviço autorizado de relato; testes e wiring necessários no mesmo commit | OK |
| T10 | Um componente: logging mcp sanitizado; testes e wiring necessários no mesmo commit | OK |
| T11 | Um componente: adapter fastmcp com duas ferramentas; testes e wiring necessários no mesmo commit | OK |
| T12 | Um componente: cli de composição e ciclo de vida; testes e wiring necessários no mesmo commit | OK |
| T13 | Um componente: formulário html fictício; testes e wiring necessários no mesmo commit | OK |
| T14 | Um componente: servidor local restrito do formulário; testes e wiring necessários no mesmo commit | OK |
| T15 | Um componente: comandos just reproduzíveis do spike; testes e wiring necessários no mesmo commit | OK |
| T16 | Um componente: runbook de operação e compatibilidade; testes e wiring necessários no mesmo commit | OK |
| T17 | Um componente: compatibilidade real hermes; testes e wiring necessários no mesmo commit | OK |
| T18 | Um componente: compatibilidade real codex; testes e wiring necessários no mesmo commit | OK |
| T19 | Um componente: demonstração externa com conferência do proprietário; testes e wiring necessários no mesmo commit | OK |
| T20 | Um componente: evidência integrada e entrega ao verifier; testes e wiring necessários no mesmo commit | OK |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Início | Match |
| T2 | T1 | T1 -> T2 | Match |
| T3 | T2 | T2 -> T3 | Match |
| T4 | T3 | T3 -> T4 | Match |
| T5 | T4 | T4 -> T5 | Match |
| T6 | T5 | T5 -> T6 | Match |
| T7 | T6 | T6 -> T7 | Match |
| T8 | T7 | T7 -> T8 | Match |
| T9 | T8 | T8 -> T9 | Match |
| T10 | T9 | T9 -> T10 | Match |
| T11 | T10 | T10 -> T11 | Match |
| T12 | T11 | T11 -> T12 | Match |
| T13 | T12 | T12 -> T13 | Match |
| T14 | T13 | T13 -> T14 | Match |
| T15 | T14 | T14 -> T15 | Match |
| T16 | T15 | T15 -> T16 | Match |
| T17 | T16 | T16 -> T17 | Match |
| T18 | T17 | T17 -> T18 | Match |
| T19 | T18 | T18 -> T19 | Match |
| T20 | T19 | T19 -> T20 | Match |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Workspace | smoke | smoke na própria tarefa | OK |
| T2 | Contratos | unit | unit na própria tarefa | OK |
| T3 | Fixture | unit | unit na própria tarefa | OK |
| T4 | Política/perfis | unit + integration | unit + integration na própria tarefa | OK |
| T5 | Persistência | integration | integration na própria tarefa | OK |
| T6 | Migração | integration | integration na própria tarefa | OK |
| T7 | Persistência | integration | integration na própria tarefa | OK |
| T8 | Serviço | unit | unit na própria tarefa | OK |
| T9 | Serviço | unit | unit na própria tarefa | OK |
| T10 | Logging | unit + integration | unit + integration na própria tarefa | OK |
| T11 | Adapter MCP | integration | integration na própria tarefa | OK |
| T12 | Operação | integration | integration na própria tarefa | OK |
| T13 | Fixture | unit | unit na própria tarefa | OK |
| T14 | Servidor fake | integration | integration na própria tarefa | OK |
| T15 | Operação | smoke | smoke na própria tarefa | OK |
| T16 | Documentação | documental | documental na própria tarefa | OK |
| T17 | Live CLI | live | live na própria tarefa | OK |
| T18 | Live CLI | live | live na própria tarefa | OK |
| T19 | Live formulário | live + UAT | live + UAT na própria tarefa | OK |
| T20 | Evidência integrada | integration + smoke + live evidence | integration + smoke + live evidence na própria tarefa | OK |

## Requirement Traceability

| Requirement ID | Tasks | Verification |
| --- | --- | --- |
| SPIKE-01 | T2, T11, T17, T18, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-02 | T2, T3, T8, T11, T17, T18, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-03 | T4, T8, T11, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-04 | T1, T3, T4, T5, T6, T8, T10, T12, T13, T14, T15, T16, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-05 | T10, T11, T12, T17, T18, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-06 | T2, T7, T9, T11, T17, T18, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-07 | T5, T6, T7, T12, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-08 | T5, T7, T9, T12, T17, T18, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-09 | T5, T7, T9, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-10 | T4, T9, T11, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-11 | T2, T5, T6, T9, T11, T17, T18, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-12 | T3, T13, T14, T16, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-13 | T13, T14, T16, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-14 | T3, T13, T16, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-15 | T9, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-16 | T1, T10, T12, T15, T16, T17, T18, T19, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-17 | T16, T17, T18, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-18 | T1, T4, T8, T9, T11, T12, T15, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-19 | T2, T4, T8, T11, T12, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-20 | T7, T9, T11, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |
| SPIKE-21 | T5, T7, T20 | Resultado esperado definido no spec/design; evidência ainda pendente |

## Closing Verification

Após o commit de T20, despachar Verifier fresco automaticamente, sem pedir permissão
adicional. Ele rederiva cobertura dos 21 requisitos e ambos os ACs, testa gates e
injeta falhas em cópia isolada, sem git stash. Priorizar remoção de autorização,
replay duplicado, recibo antes do commit, promoção a confirmação e stdout contaminado.
Registrar mutações detectadas/sobreviventes, baseline/diff e evidência file:line em
validation.md; preservar working tree real. Falhas viram tarefas corretivas e nova
verificação, no máximo três ciclos antes de escalar. Rodar validate_state.py antes
de declarar conclusão; registrar lições apenas quando fundamentadas por falhas reais.

## Review and Tools

Aprovação de tarefas não é conclusão do marco. Confirmar o plano e sua matriz;
depois escolher ferramentas e modalidade de execução, uma decisão por vez. Proposta
por tarefa está no campo Tools; inventário relevante: terminal/patch/git, Serena,
Context7, consulta oficial Web e CLIs externas; skills tlc-spec-driven e OpenAI Docs
para Codex. Não usar skill de browser Ybera nem Sites para este formulário de teste.

Alterações de configurações externas serão preparadas com diff/fragmentos exatos e
aplicarão as permissões do ambiente, sem revelar credenciais. Não reparar Hermes,
instalar ferramentas de sistema ou editar configurações globais por suposição.
Push/deploy não fazem parte da autorização local. Sem browser integrado, shell/SQL
MCP genérico, candidatura real ou MCP HTTP no M0.5.

