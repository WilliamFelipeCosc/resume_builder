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

## T10 — chaves estrangeiras SQLite

- Início observado: 2026-11-16 21:44:30 -03. Cada conexão da engine, inclusive Alembic, ativa foreign_keys preservando WAL e busy_timeout 250 ms.
- Gate PY observado 21:44:53–21:45:21 -03: pytest M1 21 passed, 435 deselected; lint falhou duas vezes por ordenação/espaço de imports, corrigido e PASS. Teste adicional `pytest tests/integration/test_diagnostic_migration.py -q`: 17 passed. Espera por gate/aprovação separada; duração ativa unknown.
- `tests/integration/test_m1_t10.py:10` testa SQL inválido em duas conexões e pragmas; `:28` observa FK durante upgrade/downgrade/upgrade e preserva a tabela M0. MONE-05/31/32 parcialmente atendidos.

## T11 — Unit of Work

- Início observado aproximadamente 2026-11-16 21:45:21 -03. Sessão vinculada à conexão única com BEGIN IMMEDIATE, propriedade de commit/rollback pela UoW, bloqueio mapeado a erro seguro e fechamento definitivo. Documentação SQLAlchemy consultada via Context7 sobre sessão vinculada a transação externa.
- Gate PY observado 21:46:43–21:47:29 -03: inicialmente 24 M1 passaram; após proteção de propriedade transacional, 25 passed, 435 deselected; lint inicialmente falhou por imports, corrigido e PASS. Espera por gate/aprovação separada; duração ativa unknown.
- `tests/integration/test_m1_t11.py:18` valida commit e referências fechadas; `:39` rollback de duas tabelas; `:51` conflito de escrita e recuperação; `:65` impede commit/rollback pela sessão. MONE-12/23/24/31/32 parcialmente atendidos.

## T12 — fundação de histórico

- Início observado 2026-11-16 21:48:01 -03. ORM tipado e migration independente criam identidade, fontes, metadados, revisões/campos/proveniência, vínculos e revisões, auditoria e recibos. FKs compostas/deferidas vinculam head e parent à própria entidade/vínculo; gatilhos protegem histórico e recibos. Entidades sem head são estado transitório; T19/T20 devem impedir sua exposição incompleta.
- Primeiro teste focal: 10 passaram e downgrade povoado falhou por ciclo de FK/DDL SQLite; corrigido por transação explícita e exclusão ordenada exclusivamente no downgrade. Segundo teste focal 11 PASS; compatibilidade adicional `pytest tests/integration/test_diagnostic_migration.py -q` 17 PASS. Gate PY observado 21:52:16–21:53:12 -03: inicialmente 37 PASS; após constraints de confirmação, 40 passed, 435 deselected e lint PASS. Alembic autogenerate advertiu ciclos e índice de expressão não refletido; migration fixa inclui índice explicitamente e testes o verificam. Esperas/gates separados; duração ativa unknown.
- `tests/integration/test_m1_t12.py:56` testa roundtrip povoado e preservação; `:86` imutabilidade; `:102` FK inválida e head cruzado; `:119` unicidade, histórico e ciclo de vínculo povoado; `:149` colunas ORM/migration; `:169` nega confirmação inválida. MONE-04/05/08/13/27/30/32 parcialmente atendidos; conteúdo tipado e serviços futuros pendentes.

## T13 — projeções autorizadas

- Início observado 2026-11-16 21:53:59 -03. Principal imutável possui clearance confiável (default public, owner local secret); policy verifica capability antes de qualquer leitura, consulta apenas metadados e retorna especificação de campos, referências de fonte e vínculos. Ocultos e ausentes resultam no mesmo `None`; fontes exigem capability própria. Consumidores futuros ainda devem aplicar a especificação na seleção dos valores, sem ORM lazy.
- Gate PY inicial 21:55:37–21:55:51 -03: 48 passed, 435 deselected e lint PASS. Após revisão da vinculação de clearance, gate repetido a partir de 21:56:59: 49 passed, 435 deselected e lint PASS. BUILD iniciado antes da correção foi interrompido deliberadamente após 190 testes, sem resultado; não é PASS.
- BUILD seguinte falhou com 482 passed e 2 falhas: expectativas antigas de versão Alembic e enum HTTP. Atualizadas para head 0002 e igualdade com registro completo, preservando os defaults e adicionando códigos M1 literais; focal 10 PASS e reforço posterior OpenAPI 5 PASS. BUILD repetido observado 21:58:57–22:00:28 -03: PASS, 484 Python (2 avisos de depreciação existentes), 19 Vitest, 4 Playwright, typecheck, build, contrato determinístico e lint. Avisos NO_COLOR/FORCE_COLOR no browser não impediram os testes. O reforço posterior apenas de asserções recebeu teste focal e não mudou runtime. Esperas/gates separados; duração líquida ativa unknown.
- `tests/integration/test_m1_t13.py:59` prova zero acesso sem capability; `:67` quatro classificações; `:77` restrições de campo/fonte/vínculo e capability de fonte; `:92` indistinguibilidade; `:109` SQL real sem valores, nomes ou trechos; `:153` impede elevar clearance por argumento. MONE-06/07/13/34 parcialmente atendidos; endpoints, serviços e verificações posteriores permanecem pendentes. CI remoto NOT_RUN.

## T14 — armazenamento privado

- Retomada observada em 2026-11-17 08:49:12 -03 após interrupção noturna, separada de esforço ativo; duração líquida e limites exatos da interrupção unknown. Premissas: diretório XDG privado existente é autoridade, nome recebido nunca é caminho; referência é SHA-256. Arquivos: storage, testes sintéticos e rastreabilidade. Sucesso: integridade, rejeição de caminhos inseguros e durabilidade antes de referenciar no banco.
- Instalação usa arquivo temporário privado, fsync e hard link atômico sem sobrescrita no mesmo diretório, seguido de fsync do diretório; essa primitiva oferece a propriedade de instalação sem substituição exigida para rename seguro. Manifesto retornado contém hash, referência e tamanho; persistência da referência usa `source_documents` existente em incrementos posteriores. Uma falha após instalação pode deixar órfão privado, nunca referência de banco parcial.
- Gate PY concluído antes de 08:50:44 -03: 54 passed, 435 deselected; Ruff e diff-check PASS. Teste focal anterior: 5 passed. Espera pelo gate separada; duração ativa líquida unknown. MONE-14/30/31/32 parcialmente atendidos; integração de importação permanece pendente.
- Adequação: `tests/integration/test_m1_t14.py:14` verifica reutilização, manifesto e original; `:26` adulteração/ausência; `:36` traversal e symlinks; `:56` falha antes da instalação sem objeto; `:71` falha após instalação deixa órfão íntegro. Cada cenário corresponde aos critérios T14; nenhuma asserção existente alterada ou teste omitido.

## T15 — metadados PDF

- Início observado 08:51:17 -03. Premissas: somente contagem de páginas; PDF privado sintético, subprocesso isolado e ambiente mínimo. Arquivos: leitor, testes e rastreabilidade. Sucesso: entrada válida e falhas estáticas sem extrair conteúdo ou divulgar warning.
- Parser estrito em subprocesso com limite de 512 MiB, timeout de 5 s, até 50 páginas e 10 MiB; stderr descartado e resposta mínima. Nenhuma chamada `extract_text` no leitor. Gate PY concluído antes de 08:52:24 -03: 62 passed, 435 deselected; lint PASS. Gate e interrupção noturna separados do trabalho ativo, duração líquida unknown.
- Adequação: `tests/integration/test_m1_t15.py:21` comprova duas páginas; `:33` rejeita inválido, criptografado, 51 páginas e tamanho, sem eco; `:40` timeout sanitizado; `:51` configura timeout, ambiente e stderr; `:65` confere limite aplicado e caminho de contagem sem extração. O limite de memória é verificado por spy no worker, não por exaustão real; a operação real foi testada em subprocesso para PDFs sintéticos. MONE-14/15/30/34 parcialmente atendidos; integração de importação pendente.

## T16 — fonte manual

- Retomada observada 09:00 -03 após aprovação do contrato às 08:56; espera por decisão separada do esforço ativo, duração líquida unknown. Premissas: texto e título conforme decisão registrada, confidential, arquivo instalado antes de referência DB; nenhum fato ou confirmação. Arquivos: serviço/rota, composição, contrato gerado, testes e rastreabilidade.
- DTO estrito, armazenamento UTF-8, fonte/auditoria/recibo na mesma UoW e replay sujeito à autorização atual; erro de chave divergente 409. Primeira execução focal encontrou ordem de flush de FK e falhou 2/4; corrigida com flush da fonte antes da auditoria e repetida 4/4. Gate HTTP concluído antes de 09:01:22 -03: geração PASS, 69 passed/435 deselected, contrato determinístico PASS, typecheck e lint PASS.
- Adequação: `tests/integration/test_m1_t16.py:43` verifica criação/replay/conflito, `:55` privacidade, bytes, recibo, auditoria e ausência de fatos; `:62` valida limites sem eco; `:77` nega antes do repositório; `:91` exige autorização atual no replay; `:108` testa negativa HTTP sem escrita; `:139` falha de armazenamento sem registro parcial. Os seis cenários mapeiam aos critérios T16, sem testes existentes removidos ou enfraquecidos. A recuperação HTTP da fonte cabe à T17. MONE-03/06/22/27/30 parcialmente atendidos.

## T17 — consulta de fontes

- Início observado 09:02:22 -03. Premissas: capability antes do acesso, classificação própria filtrada em SQL, hash verificado antes da resposta; nome de download fixo, sem path externo. Arquivos: serviço/rotas, composição, SDK, testes e rastreabilidade.
- Gate HTTP PASS: 74 passed/435 deselected, geração/contrato determinístico/typecheck/lint PASS. Primeiro BUILD passou 509 Python, 19 Vitest, typecheck/build/contrato e falhou no browser por Chromium temporário ausente. Instalação autorizada repetida; browser separado 4/4 PASS. Após reforço só de asserções, focal T17 5/5 PASS. BUILD completo repetido e concluído 09:08 -03: PASS, 509 Python (2 warnings existentes), 19 Vitest, 4 Playwright, typecheck/build/contrato/lint. Esperas separadas do esforço ativo; duração líquida unknown.
- Adequação: `tests/integration/test_m1_t17.py:58` confere payload completo, `:67` bytes, attachment e no-store; `:72` prova SQL com filtro de classificação e ausente/oculto; `:86` confirma 404 e separação de acesso ao fato; `:103` bloqueia adulteração/ausência; `:124` nega capability antes do repositório. Montagem StaticFiles existente serve apenas `/assets`, nenhuma fonte privada. MONE-06/07/30/34 parcialmente atendidos; CI remoto NOT_RUN.

## T18 — contratos tipados

- Início observado 09:14:13 -03 após aprovação de tipos/envelopes às 09:12/09:13; espera por decisão separada, duração ativa líquida unknown. Premissas: campos e limites aprovados, classificação confidential padrão, confirmação não fornecida na criação. Arquivos: contratos, testes e rastreabilidade.
- Nove conteúdos, comandos e leituras concretas, datas parciais, metadados e paginação validados por Pydantic; metricValue permanece texto. Gate PY concluído antes de 09:15:53 -03: 93 passed/435 deselected e lint PASS.
- Adequação: `tests/unit/test_m1_t18.py:25` valida roundtrip dos nove conteúdos; `:33` associa Profile e restringe classificação/campos; `:58` distingue unknown/restricted e confirmação por campo; `:76`/`:84` datas válidas/inválidas; `:89` extras, coerções e limites. 19 casos focais, todos derivados dos critérios; nenhum teste anterior alterado ou omitido. MONE-03/09/10/12/17 parcialmente atendidos; persistência e rotas pendentes.
- Revisão posterior da T18 identificou perda de constraints nos DTOs nullable e possibilidade de marcar valor não nulo como restrito. Corrigidas ambas; teste focal adicional rejeita valor restrito, booleano coercivo e nome longo. Gate PY: 94 passed/435 deselected; lint inicialmente falhou por arquivo não rastreado em andamento de T19 ainda sem formatação, formatado e lint repetido PASS. Nenhuma asserção anterior alterada.

## T19 — tabelas tipadas

- Início observado 09:16:37 -03. Premissas: identidade e conteúdo em tabelas separadas; FK/kind/Profile no SQLite, conteúdo/head completo garantido pela UoW e consulta das tarefas seguintes. SQLite não permite exigir FK reversa diferível no commit sem mudar o modelo; entidades transitórias/incompletas não podem ser expostas. Arquivos: mapping, migrations, testes e rastreabilidade.
- Migration 0003 cria nove tabelas e gatilhos de associação; downgrade preserva fundação e M0. Fixtures históricas T12 fixadas na revisão 0002, preservando suas asserções; smoke acompanha head 0003. Primeiro PY encontrou BEGIN duplicado no downgrade encadeado; corrigido BEGIN condicional na 0002. Gate repetido até 09:20:10 -03: 97 passed/435 deselected e lint PASS. Reforço posterior só de asserções focal: 3 passed.
- Adequação: `tests/integration/test_m1_t19.py:18` persiste os nove tipos e confere todos os campos fornecidos e mapping; `:72` rejeita kind incorreto, Profile ausente e conteúdo órfão; `:89` downgrade/upgrade povoado preserva revisão e M0. Testes 0002/0003 focais 18 PASS. MONE-03/04/05/08/32 parcialmente atendidos; rollback e não exposição de estado incompleto exigem verificação em T20–T22.

## T20 — repositório versionado

- Início observado 09:21:07 -03. Premissas: chamador autoriza campos/fontes antes de invocar repositório; UoW possui transação; snapshots são linhas por campo; datas/conteúdo são DTOs aprovados. Arquivos: repositório, testes e rastreabilidade.
- Escrita transacional com UPDATE por head e rowcount, snapshots, metadados, proveniência, auditoria e recibo; alterações de Profile preservam confirmação apenas de valores iguais comparados no SQL, sem recuperar valores anteriores. Proveniência de revisões é copiada no SQL, sem materializar excerpts. Revisão identificou e corrigiu classificação do head e preservação de fontes correntes/históricas. Primeiro teste focal encontrou conversão de resultado e comparação JSON; corrigidas. Gate PY final: 103 passed/435 deselected e lint PASS; duração ativa líquida unknown.
- Adequação: `tests/integration/test_m1_t20.py:57` injeta falha entre identidade e conteúdo e confere rollback; `:78` filtra snapshot antes do valor; `:95` duas engines rejeitam revisão obsoleta sem registros parciais; `:137` replay/conflito; `:148` confirmação independente; `:192` privacidade e proveniência por campo atual/histórica. Seis cenários necessários aos critérios; sem remover testes. MONE-03/07/09/12/13/24/25/26/27 parcialmente atendidos; autorização e exclusão de entidades incompletas nas consultas permanecem T21/T22.

### Revisão complementar de T14/T15

- Em 2026-11-17, entre a lacuna identificada em T16 e sua resolução humana às 08:56 (-03), o principal revisou armazenamento e limites. T14 preserva a propriedade de instalação atômica sem sobrescrita usando hard link; o manifesto tipado fornece hash/referência/tamanho, e os serviços persistem a referência e o hash no SourceDocument existente. Não se exige um segundo arquivo de manifesto.
- `tests/integration/test_m1_t15.py:96` executa o worker real em subprocesso com parser sintético: controle retorna uma página (`:120`); reserva virtual de 600 MiB sob RLIMIT_AS de 512 MiB resulta em `pdf_invalid` (`:123`); warnings e stderr injetados não chegam à saída do principal (`:125`, `:126`). O ensaio verifica o limite real de espaço de endereçamento, sem esgotar a memória física do host. O teste complementa o spy e os PDFs reais sintéticos já presentes; nenhum teste foi removido ou enfraquecido.
- Gate focal: `uv run --all-packages --locked pytest tests/integration/test_m1_t15.py -q`, 9 passed em 0,68 s. Gate PY complementar observado entre 08:56 e 08:57 (-03): 63 passed, 435 deselected; `just lint` PASS (102 arquivos). Intervalos de execução são espera, não tempo ativo reconstruído. Naquele momento, BUILD da fase 3 ainda aguardava T17; o resultado posterior está no registro T17. CI remoto NOT_RUN.

## Reconciliação após fase 3

Em 2026-11-17 às 09:11 (-03), a conferência de git e dos status individuais
confirmou T1–T17 concluídas (17/64), até `68fcbd0`. O resumo do tasks.md
ainda mostrava 6/64 e o handoff 15/64; ambos foram corrigidos pelos status
individuais e commits. BUILD de T17: 509 Python, 19 Vitest, 4 Playwright e
checks PASS. T18 aguarda decisão humana sobre tipos/envelopes em
`contracts-refinement.md`; a proposta ainda não é implementação aprovada.

## Decisão de tipos e envelopes T18

O proprietário aprovou metricValue como texto opcional preservado às 09:12
e os formatos de contracts-refinement.md às 09:13 (-03), em 2026-11-17.
Contexto, design, spec e handoff foram sincronizados com as escolhas.
A espera por esclarecimento é separada do esforço ativo, sem reconstruir
duração não instrumentada. T18 está liberada; runtime e seu gate ainda
não executados neste registro de decisão.
