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
