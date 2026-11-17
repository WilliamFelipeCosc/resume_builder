# M1 — Registro de execução

## T1 — baseline

- Início de trabalho ativo: 2026-11-16 20:18:14 -03; autorização explícita do proprietário às 20:17 -03.
- Estado inicial: `main` em `d2a609d`, com `.specs/STATE.md` e `docs/decisions/open-decisions.md` modificados e planejamento M1 não rastreado; preservados. Branch local `feature/m1-career-kb` criada após aprovação de acesso a `.git`.
- Espera: criação da branch aguardou aprovação de sandbox; duração exata não instrumentada.
- Plano: executar BUILD integral existente, registrar contagens e falhas reais, sincronizar estado e rastreabilidade antes do commit documental.

- BUILD inicial no sandbox: falhou antes da coleta (0 testes) por cache uv somente leitura; repetido com permissão.
- BUILD escalado inicial: 435 Python passaram (2 avisos de depreciação), 17 Vitest passaram, typecheck/build/contrato passaram; Playwright 0/1 executado, falhou ao iniciar por headless shell ausente. Instalação autorizada do Chromium v1254 em `/tmp/resume-builder-playwright` terminou com exit 0; sistema não oficialmente suportado, fallback Ubuntu 24.04.
- BUILD repetido: PASS em 2026-11-16 20:24 -03: 435 Python (2 avisos), 17 Vitest, 1 probe e 2 testes de aplicação Playwright passaram; typecheck, build, contrato (duas gerações idênticas), Ruff e `git diff --check` passaram. Comando: `env PATH=/home/williamf/.local/share/pnpm/bin:/home/williamf/.nvm/versions/node/v24.18.0/bin:/home/williamf/.local/bin:/usr/local/bin:/usr/bin:/bin PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright just check`.
- Intervalo ativo e esperas até 20:24:54 -03: início instrumentado 20:18:14; duração líquida e limites individuais de espera não medidos, `unknown`. As esperas por aprovação, instalação e gates não são somadas como trabalho ativo; duração detalhada `unknown`.
- Intervenções: autorização de início às 20:17 e aprovações de sandbox; CI remoto NOT_RUN. Retrabalho: instalação de Chromium e repetição do gate, duração `unknown`. Tokens/custo `unknown`; verificador independente e aceite humano pendentes; nenhuma exceção aceita.
- MONE-38 parcialmente atendido pelo registro e baseline; medição continua até o encerramento. Próximo: T2.

## T2 — CI

- Início de trabalho observado: 2026-11-16 20:27:10 -03. Plano: workflow Linux com versões fixas, instalação pelos locks, Chromium e Docker; rodar BUILD local; CI remoto NOT_RUN até push autorizado.
- Documentação consultada via Context7: `astral-sh/setup-uv` para versões, Playwright para `install chromium --with-deps`, GitHub Actions para pins de actions. O ambiente remoto ainda não foi executado.
- BUILD local iniciado aproximadamente 20:27:47 e concluído antes de 20:31:17 -03 (fim exato não instrumentado): PASS, 435 Python (2 avisos), 17 Vitest e 3 Playwright, typecheck, build, contrato e Ruff. Mesmo comando BUILD da T1; Docker local funcional.
- Instalação local verificada às 20:31:17: `uv sync --all-packages --locked` exit 0 (85 resolvidos, 81 verificados); `pnpm install --frozen-lockfile` exit 0, 3 projetos; `docker info --format '{{.ServerVersion}}'` exit 0, 29.8.2. Aprovação de sandbox aguardada antes do comando; início exato da espera unknown, encerrada antes de 20:31:17.
- `setup-uv` documenta `python-version` como configuração de `UV_PYTHON`, não instalação em si; `uv sync` resolve interpretador. Node documenta Corepack nas versões anteriores a 25 e `corepack enable`. Chromium usa diretório padrão tanto na instalação quanto no gate do workflow. Tags exatas de checkout/setup-node verificadas em releases oficiais; runner remoto e instalação limpa remota NOT_RUN. T2 sustenta MONE-01/02/33 parcialmente, sem concluir aceite dos requisitos.

## T3 — dependências frontend

- Início observado: 20:32:22 -03. Plano: consultar documentação/peers públicos, instalar pins exatos, compor spike sintético descartável e executar WEB.
- Registro npm dentro do sandbox falhou com EAI_AGAIN; consulta escalada foi aprovada. Pins: `@tanstack/react-query` 5.107.1, `react-router` 7.18.5, `react-hook-form` 7.92.0, `tailwindcss` e `@tailwindcss/vite` 4.3.5. Peers declarados aceitam React 19 e Vite 8; sem peers novos obrigatórios identificados. Lock +283 linhas: query-core 5.107.1, Tailwind node/oxide 4.3.5 e variantes de plataforma, cookie/parser e demais transitivas, integralmente registrados no lock.
- Spike fictício em `/tmp/rb-m1-spike`: QueryClientProvider/useQuery, Router Data, RHF e Tailwind Vite; primeira compilação TS falhou por declaração CSS ausente, corrigida adicionando `vite/client` ao tsconfig temporário; build inicial passou. Repetição com Node 24.18.0: tsc exit 0 e Vite build exit 0, 67 módulos e CSS gerado. Não representa teste de integração do produto.
- WEB inicial passou sob Node 26 detectado posteriormente; repetido com PATH Node 24 explícito: 17 Vitest, typecheck, build, contrato determinístico e Ruff PASS. Solicitação de aprovação posterior a 20:34:21; execução observada às 20:35:18 e conclusão até 20:35:24 -03. Espera por aprovação separada do trabalho ativo; limites exatos desconhecidos. `pnpm list` adicional no sandbox falhou por SQLite do store somente leitura; não é gate, versões verificadas por lock e registro.
- MONE-03/33 parcialmente atendidos pela compatibilidade; não indicam aceite funcional. APIs consultadas via Context7 nas documentações oficiais genéricas, sem dados privados.

## T4 — descoberta de testes

- Início observado: 20:36:38 -03. Plano: incluir `m1-*.spec.ts` no mesmo harness real e descoberta `.test.ts`/`.test.tsx` no Vitest, preservar testes existentes, dados temporários e zero retries; verificar listagem com fixtures transitórias e executar BUILD.
- Playwright `--list`: 2 diagnósticos existentes e 1 probe M1 transitório (3 em 2 arquivos); Vitest `list`: testes existentes e probe `.test.ts`. Primeira listagem Vitest falhou por caminho de configuração duplicado; corrigida e repetida com exit 0. Probes removidos, T6 continua responsável por demonstrar coleta real persistente. Harness permanece com dados temporários e `retries: 0`.
- BUILD começou após 20:37:04 e terminou antes de 20:38:30 -03: PASS, 435 Python (2 avisos), 17 Vitest, 3 Playwright, typecheck, build, contrato e Ruff. Comando BUILD da T1. Intervalo de gate/espera separado do trabalho ativo; duração ativa líquida unknown.
- MONE-01/33/35 parcialmente atendidos pela descoberta; coleta real de teste M1 pendente de T6.

## T5 — upload e metadados

- Início observado: 20:39:09 -03. Plano: declarar multipart existente diretamente na API e pypdf no core, gerar lock, verificar ambiente limpo com PDF sintético e executar BUILD. A skill PDF e documentação oficial de FastAPI/pypdf foram consultadas; conteúdo privado não foi acessado.
- `uv lock`: 86 pacotes resolvidos, adicionou pypdf 6.21.4; multipart 0.0.33 já constava transitivamente. `UV_PROJECT_ENVIRONMENT=/tmp/rb-m1-clean-venv uv sync --all-packages --locked`: exit 0, CPython 3.14.8, 82 pacotes instalados; aviso de hardlink entre filesystems, fallback cópia. Aprovação foi aguardada após 20:40:07; início/fim exatos da espera unknown.
- Na instalação limpa, importações de `pypdf` e `python_multipart` e PDF sintético estrito em memória: 1 página, título fictício e não criptografado, PASS; nenhum arquivo pessoal lido. Isso não valida ainda o leitor limitado de produção T15.
- BUILD após 20:41:48 até antes de 20:43:13 -03: PASS, 435 Python (2 avisos), 17 Vitest, 3 Playwright, typecheck/build/contrato/Ruff. Gate e espera não são somados ao trabalho ativo; duração líquida unknown. MONE-14/15/30/33 parcialmente atendidos, sem completar os comportamentos de importação.

## T6 — primitivas de UI

- Início observado: 20:44:16 -03. Plano: Tailwind Vite com tokens padrão, adaptar apenas Button/Input/Dialog do padrão shadcn/Radix e verificá-los com formulário sintético, teclado e foco em servidor de fixture separado do produto; rodar FRONT e BUILD de fase.
- Consulta pública: `@radix-ui/react-dialog` 1.3.1 aceita React/React DOM 19 e tipos existentes; instalado com pin exato, adicionando transitivas ao lock. APIs e padrões consultados em documentação oficial via Context7.
- Button/Input/Dialog são adaptações mínimas de código aberto do padrão shadcn, não saída automática da CLI; Radix fornece o comportamento do diálogo. A fixture usa label nativo e fica em `tests/fixtures`, servida no processo Vite de teste; não é incluída no build de produção (busca por seus textos em `apps/web/dist` sem correspondências). Lock +419 linhas, incluindo transitivas Radix; pins/peers no lock.
- FRONT: iniciado após 20:48:29, testes começaram 20:49:21, concluído antes de 20:49:43 -03: PASS, 19 Vitest (2 novos), typecheck/build/contrato/lint, 4 Playwright (1 novo). Adequação: `apps/web/tests/m1-t6.test.tsx:9` verifica tipo não-submit/label, `:14` verifica atributos; `apps/web/tests/m1-t6.spec.ts:7` abre com teclado, `:12` foco no campo, `:15` e `:17` navegação e envio, `:19` e `:20` Escape/restauração, `:24` e `:25` fechamento por botão e restauração; todos PASS.
- BUILD da fase: iniciado após 20:49:43 e concluído antes de 20:51:11 -03, PASS: 435 Python (2 avisos), 19 Vitest, 4 Playwright, typecheck/build/contrato/Ruff. Após adicionar asserção de isolamento, repetição começou após 20:51:19: Python 435 e WEB passaram, browser falhou porque a asserção de 404 foi executada sem sessão e recebeu 401 antes da rota. Não houve alteração de autenticação. Corrigida precondição usando sessão autorizada existente: `apps/web/tests/diagnostic-app.spec.ts:47` confirma 404; `just check-browser` solicitado após 20:53:04 e concluído antes de 20:55:14, 4 testes PASS. O BUILD anterior cobre a implementação; repetição focal cobre a única mudança posterior de teste.
- Intervalos de gate e aprovações são espera, não somados ao trabalho ativo; limites exatos da espera e duração líquida unknown. MONE-03/33 parcialmente atendidos, sem aceite funcional. Fase 1 encerrada; T7 não iniciada. CI remoto continua NOT_RUN.

## T7 — contrato seguro de erros

- Início observado: 2026-11-16 21:34:03 -03. Arquivos: API, OpenAPI/SDK, testes sintéticos e rastreabilidade. Contrato: códigos estáticos, requestId correlacionado, paths estritamente listados a partir do design; nenhum valor rejeitado é retornado. Rotas posteriores continuam responsáveis por selecionar seus códigos específicos.
- Gate HTTP observado de 21:38:00 a 21:38:58 -03: `just generate` PASS; pytest M1 10 passed, 435 deselected; `just check-contract` PASS duas gerações idênticas; `pnpm --filter web typecheck` PASS; `just lint` falhou inicialmente por ordem de import, corrigido e PASS. O pnpm autônomo informa Node 26; `pnpm --filter web exec node --version` com PATH explícito confirmou v24.18.0 nos scripts. Aprovação de sandbox e gate são espera separada; duração líquida ativa unknown.
- Adequação: `tests/integration/test_m1_t7.py:11` valida sete status, códigos e mensagens explícitos; `:30` valida 422, paths permitidos, requestId e ausência de sentinela; `:44` valida 404 sem eco; `:59` valida conflito de revisão e filtragem de path. Após reforço somente das asserções, teste focal repetido até 21:39:47 -03: 10 passed. MONE-12/15/23/26/29/34 parcialmente atendidos; comportamentos de operações futuras permanecem pendentes.

## T8 — entrada autorizada e limitada

- Início observado: 2026-11-16 21:40:11 -03. Boundary resolve principal por composição confiável e capabilities por rota antes de ler bytes; budgets 1 KiB M0, 256 KiB JSON KB e 12 MiB multipart, rate limits por sessão/global e um preparo por processo. Limites individuais PDF/seed e budget de respostas pertencem aos endpoints futuros.
- Gate HTTP observado 21:41:38–21:42:51 -03: `just generate` PASS; pytest M1 15 passed, 435 deselected; contrato determinístico PASS; typecheck PASS com Node 24 nos scripts; lint PASS. Testes adicionais após gate: execução focal inicial falhou 7/8 devido a parâmetro ausente em fixture; corrigido e repetido 8 passed. Aprovação/gate separados do trabalho ativo; duração líquida unknown.
- Adequação: `tests/integration/test_m1_t8.py:69` prova zero bytes sem sessão/capability; `:77` testa chunked e orçamento M0; `:87` testa 120/min e 429; `:103` testa media e 12 MiB; `:116` testa decisão de revisão; `:122` verifica 5/sessão, 10/global e expiração; `:154` e `:194` verificam liberação e concorrência real. MONE-06/07/14/15/34 parcialmente atendidos; endpoints e parsing permanecem pendentes.

## T9 — logs operacionais

- Início observado: 2026-11-16 21:43:31 -03. Allowlist ampliada para eventos/códigos e identificadores estáticos M1; caminhos arbitrários, query e conteúdo continuam omitidos.
- Gate PY observado 21:43:53–21:44:05 -03: pytest M1 19 passed, 435 deselected; `just lint` PASS. Aprovação e gates separados do trabalho ativo; duração líquida unknown.
- `tests/integration/test_m1_t9.py:11` captura aplicação e dependência, valida preservação de evento/path/código permitidos e ausência de sentinelas de contato, trecho, filename, exceção e query. MONE-34 parcialmente atendido; integrações futuras precisam usar a allowlist.
