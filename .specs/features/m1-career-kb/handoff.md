# Handoff — execução M1 Career KB

**Registrado:** 2026-11-17 às 10:22 (-03), America/Sao_Paulo.
**Período coberto:** início autorizado em 2026-11-16 às 20:17 (-03),
interrupção noturna e retomada em 2026-11-17 às 08:48 (-03), até o pedido
de registrar este handoff. Inclui os três workers e as revisões do principal.
**Branch:** `feature/m1-career-kb`.
**Base:** `d2a609d`, anteriormente em `main`.
**HEAD de implementação conferido:** `ac94851`.
**Estado canônico:** M1 `in_progress`; **22/64 tarefas concluídas**.
**Ponto de retomada:** T23 parcialmente implementada, sem commit;
T24–T64 não executadas. Não tratar M1 ou fase 4 como aceitos/concluídos.

## 1. Pedido, autorizações e modo de trabalho

O proprietário pediu ler a spec `m1-career-kb`, iniciar a execução e usar
GPT Terra nos subagentes/workers. O nome digitado `m1-carrer-kb` foi
reconciliado com a pasta existente. O comando de início substituiu a
retenção histórica de não iniciar que constava do planejamento aprovado.
As mensagens posteriores de Continue mantiveram essa autorização.

Foram aplicados AGENTS.md e a skill `tlc-spec-driven`: gates por tarefa,
testes derivados dos critérios, status/rastreabilidade antes do commit e
commits locais atômicos. Serena foi inicializada; não havia `.codegraph/`,
e nenhum índice foi criado. Context7/documentação oficial foram usados
para APIs técnicas. A skill PDF foi usada no trabalho de metadados PDF.

O plano já aprovado tem 64 tarefas, 10 fases, 38 critérios MONE e oito lotes
sequenciais de workers para P1–P9; o principal conduz P10. Não houve
paralelismo entre lotes nem subagentes criados pelos workers.

Workers desta execução, todos `gpt-6.1-terra`:

| Worker | Escopo e resultado |
| --- | --- |
| `/root/m1_batch1` | P1, T1–T6 concluídas |
| `/root/m1_batch2` | P2, T7–T13 concluídas |
| `/root/m1_batch3` | Despachado antes da interrupção noturna; não deixou implementação de T14 |
| `/root/m1_batch3_resume` | Retomou P3+P4; T14–T22 concluídas, T23 em andamento quando atingiu quota |

O principal revisou mudanças, registrou decisões, corrigiu resumos de
progresso e adicionou a prova real de limite de memória do subprocesso PDF.
Essas revisões não equivalem ao Verifier independente completo previsto no
piloto e no fechamento do marco.

Autorização vigente: implementação e commits **locais**. Não houve push,
execução remota do CI, deploy, escrita no Obsidian ou importação/revisão
dos dados pessoais nesta execução. Não repetir entrevistas de decisões já
aprovadas. Lacunas novas de negócio/schema exigem esclarecimento conforme
AGENTS.md; decisões específicas resolvidas abaixo já podem ser usadas.

## 2. Situação reconciliada no encerramento

- T1–T22 estão marcadas Complete e têm commits locais.
- T23 continua Pending em `tasks.md`: código, testes e artefatos gerados
  existem na árvore, mas seu gate final e fechamento não foram registrados.
- O worker terminou com erro de **limite de uso**, não com um veredito de
  falha funcional. A mensagem sugeriu tentar novamente às 1:48 PM, sem
  timezone explícito; não transformar isso em horário de retomada garantido.
- O BUILD posterior à última correção de constraints havia sido iniciado;
  não há confirmação final de exit 0 no retorno do worker. Seu resultado é
  **não confirmado**, mesmo que o processo tenha terminado em background.
- A inspeção de processos ao preparar este arquivo não encontrou processos
  identificados como pytest, harness web, gates Playwright ou `just check`
  ainda ativos. Isso não recupera o exit code do comando interrompido.
- Não há decisão humana de T16/T18/T22 pendente. O próximo impedimento é
  recuperar capacidade de execução e conferir/fechar T23.
- O pedido atual foi registrar o handoff; não foi iniciado outro lote.

### Arquivos pendentes de T23

O estado abaixo foi capturado antes de criar este handoff e atualizar o
resumo global. Preservar todos estes arquivos; são trabalho M1 identificado,
não alterações desconhecidas do usuário.

| Estado | Caminho |
| --- | --- |
| Modificado | `backend/api/src/resume_api/__main__.py` |
| Modificado | `backend/api/src/resume_api/app.py` |
| Modificado | `backend/api/src/resume_api/errors.py` |
| Modificado | `backend/core/src/resume_core/logging_policy.py` |
| Modificado | `packages/api-client/openapi.json` |
| Modificado | `packages/api-client/src/generated/index.ts` |
| Modificado | `packages/api-client/src/generated/sdk.gen.ts` |
| Modificado | `packages/api-client/src/generated/types.gen.ts` |
| Novo, não rastreado | `backend/api/src/resume_api/routers/career.py` |
| Novo, não rastreado | `tests/integration/test_m1_t23.py` |

O diff dos oito arquivos já rastreados tem 11.554 inserções e 363 remoções,
majoritariamente OpenAPI/SDK gerados; esse stat não inclui os dois arquivos
novos. Não separar nem descartar o SDK: ele é coartefato dos endpoints.
O handoff e a atualização de `.specs/STATE.md` são alterações documentais
adicionais criadas após essa captura; conferir `git status` na retomada.

## 3. Entregas concluídas e commits

### Fase 1 — reprodutibilidade, CI e compatibilidade

| Tarefa | Entrega | Commit |
| --- | --- | --- |
| T1 | Branch local, planejamento aprovado incorporado, baseline e esforço; M1 canônico passou a in_progress | `84778a2` |
| T2 | GitHub Actions Linux com pins/locks, Docker/Chromium e gates existentes; CI remoto NOT_RUN | `14424bd` |
| T3 | Query, Router, RHF e Tailwind pinados; spike sintético compilou sob Node 24 | `b6248e8` |
| T4 | Descoberta Vitest `.test.ts`/`.tsx` e Playwright `m1-*.spec.ts`; diagnósticos preservados e retries zero | `79c6f00` |
| T5 | multipart direto na API e pypdf no core, lock e instalação limpa com PDF sintético | `f8ba137` |
| T6 | Tailwind e primitivas mínimas Button/Input/Dialog; formulário e diálogo por teclado em fixture isolada | `018b1d0` |

T6 usa adaptações mínimas do padrão shadcn e Radix Dialog, não geração de
um kit inteiro pela CLI. A fixture é servida por Vite de testes separado,
não entra no build do produto e retorna 404 no backend com sessão válida.
Sem sessão, a proteção retorna 401 antes da rota; o teste foi corrigido
na precondição de autenticação, sem relaxar o 404 nem alterar a proteção.

Houve remoção de linha em branco excedente no planejamento em `41803b0`.
Uma mensagem de commit T5 foi corrigida localmente; o hash válido é
`f8ba137`. Referências anteriores a `8f97b1c` ficaram obsoletas.

### Fase 2 — fronteiras, integridade e política

| Tarefa | Entrega | Commit |
| --- | --- | --- |
| T7 | Erros HTTP tipados, códigos/mensagens estáticos, requestId e campos seguros sem eco; SDK atualizado | `6fb91bc` |
| T8 | Sessão/capability antes dos bytes; budgets por rota, rate limits e slot de preparo | `808f6a6` |
| T9 | Allowlists de logs M1 e sentinelas de conteúdo privado em aplicação/dependências | `8fb2ca6` |
| T10 | Foreign keys em toda conexão, inclusive migrações, mantendo WAL/timeout | `9c99195` |
| T11 | Unit of Work explícita BEGIN IMMEDIATE, rollback conjunto, erro seguro de lock e sessão fechada definitivamente | `5d3dd1a` |
| T12 | Fundação ORM/migration 0002: identidade, fontes, metadados, revisões, vínculos, proveniência, auditoria e recibos | `53ff526` |
| T13 | Capabilities/clearance e projeções autorizadas a partir de metadados, antes de valores | `458b5ab` |

Pontos relevantes:

- Principal imutável possui clearance; default PUBLIC preserva consumidores
  anteriores e o owner local tem SECRET. A policy não aceita um clearance
  separado para elevar acesso.
- M0 mantém 1 KiB; JSON KB/review tem 256 KiB; import total tem 12 MiB.
- KB: 120 req/min/sessão; preparo: 5/min/sessão e 10/min global; um preparo
  por processo, liberado em finally inclusive após exceção/desconexão.
- SQLite mantém busy_timeout 250 ms. Repositórios compartilham a UoW e não
  fazem commits independentes.
- FKs compostas/deferidas ligam head/parent à entidade ou vínculo correto;
  histórico, auditoria e recibos têm proteção de imutabilidade no banco.
- O downgrade povoado expôs ciclos FK/DDL, corrigidos e testados em banco
  temporário. Nenhum downgrade de dados reais foi executado.
- Dois testes antigos foram atualizados pela evolução aprovada: head
  Alembic e enum completo de erros. As demais asserções foram preservadas,
  e a cobertura dos códigos M1 foi reforçada com valores literais.

### Fase 3 — fontes privadas utilizáveis

| Tarefa | Entrega | Commit |
| --- | --- | --- |
| T14 | Objetos privados por SHA-256, instalação durável sem sobrescrita e manifesto tipado | `9ca4718` |
| T15 | Metadados PDF estritos em subprocesso limitado, sem extração textual e sem warnings crus | `6582805` |
| T16 | Fonte manual UTF-8 confidential, recibo/auditoria transacionais, replay e conflitos seguros | `4259792` |
| T17 | Metadados/download de fonte com classificação própria, integridade, attachment e no-store | `68fcbd0` |

T14 usa hard link atômico no mesmo diretório após fsync para instalar sem
sobrescrita; é a primitiva técnica usada para a propriedade de instalação
atômica prevista no design. O manifesto retorna hash/referência/tamanho;
os serviços persistem hash/referência em `source_documents`. Não há segundo
arquivo de manifesto. Falha após instalação pode deixar órfão privado,
sem publicar referência DB para bytes ainda não instalados. A recuperação
completa desses órfãos pertence às tarefas posteriores.

T15 limita PDF a 10 MiB/50 páginas, timeout a 5 s e espaço de endereçamento
a 512 MiB; filtra ambiente, usa `-I`, descarta stderr e devolve saída mínima.
O principal acrescentou em `e7b7603` um teste com o worker real: controle
de uma página passa, reserva virtual de 600 MiB é recusada e warnings de
logging/stderr não vazam. Essa prova complementa o spy inicial sem esgotar
memória física. Não é uma promessa de sandbox completo ou isolamento de rede.

T16 não cria CareerFacts nem confirma qualificações. A fonte é anotação
declarada pelo usuário; não se transforma em prova externa. T17 mantém
autorização da fonte independente da classificação de um fato derivado.

### Fase 4 — domínio tipado pela API, ainda aberta

| Tarefa | Entrega concluída | Commit |
| --- | --- | --- |
| T18 | Nove conteúdos/comandos/leituras Pydantic, períodos parciais, confirmação e privacidade | `088462d` |
| T19 | Nove tabelas de conteúdo e migration 0003 com associações de kind/Profile | `422ba33` |
| T20 | Estado/snapshots/auditoria/recibos na UoW; UPDATE condicional por revisão-base | `4d13ed2` |
| T21 | Criação autorizada dos nove tipos, sempre unverified, com fonte e replay reautorizados | `1a28e80` |
| T22 | Detalhe/lista paginada e filtrada no SQL, budget e proveniência autorizada | `504e3af` |

Correções/revisões complementares:

| Commit | Correção |
| --- | --- |
| `3676f7f` | DTOs nullable preservam constraints originais e rejeitam valor não nulo marcado como restrito |
| `4449922` | Leitura retorna proveniência tipada após autorização; não seleciona excerpt de referência restrita |
| `ac94851` | CHECKs SQLite de tamanho, booleanos, enums Statement/Evidence e página positiva; ORM/migration coerentes |

T19 garante no DB os invariantes expressáveis de FK/kind/Profile. A criação
da identidade precede conteúdo/revisão dentro da transação; a garantia de
conjunto completo antes da exposição é dos serviços/UoW/consultas. T20 testa
falha entre identidade e conteúdo com rollback, e T21/T22 rejeitam ou excluem
identidades incompletas. Não alegar que o DB sozinho impede todo estado
intermediário em uma transação.

T20 preserva confirmação de campos independentes do Profile e invalida a
unidade alterada, sem selecionar valores antigos só para compará-los. A
classificação do estado atual foi alinhada à revisão; novas origens são
registradas sem apagar as anteriores. Proveniência de snapshots é copiada
em SQL sem materializar excerpts no Python.

T21 valida ambas as fontes se Evidence aponta para documento diferente da
fonte do comando; origem manual/documental e página devem corresponder aos
metadados reais autorizados. Campos sourceDocumentId/page/excerpt recebem
proteção da fonte. Uma proibição não especificada de usar Profile arquivado
como referência foi retirada; identidade/histórico são preservados.

T22 usa BEGIN explícito para leitura consistente, seleção de colunas/linhas
autorizadas antes dos valores, ordenação createdAt/UUID, default 25, máximo
100 e offset até 10.000. Unknown/null é distinguido de restrictedFields.
Evidence considera também a classificação **atual** da fonte e a capability
source:read. A resposta acima de 1 MiB falha sem truncar o conteúdo.

## 4. T23 — trabalho a preservar e fechar

Implementação existente, ainda sem commit:

- Fábrica registra rotas **concretas singulares** para os nove kinds:
  `/api/career/profile`, `/experience`, `/statement`, `/project`,
  `/achievement`, `/skill`, `/education`, `/language` e `/evidence`, todas
  sob `/api/career`. Cada família tem POST, GET de lista e GET por UUID.
- São 27 operationIds distintos (`create_…`, `list_…`, `get_…`), com DTOs
  concretos, respostas e erros tipados.
- Composição confiável dos serviços na aplicação/CLI e export offline do
  OpenAPI sem abrir banco ou fonte.
- Parsing real de query string no adapter HTTP antes do domínio estrito,
  incluindo offset/limit/archived/confirmationField.
- `ResponseTooLarge` retorna 422 com código `response_too_large` e mensagem
  pedindo página/seleção menor; não usa mensagem de body inválido para GET.
- OpenAPI e SDK TypeScript regenerados; nenhum DTO TS manual.
- Testes cobrem os nove tipos por POST/list/detail, erro 409/422, sessão,
  Origin/Host, principal forjado no body, fonte oculta, head incompleto,
  redaction/proveniência, budget e export offline/operationIds únicos.

Âncoras para retomar:

- `backend/api/src/resume_api/routers/career.py:28`: fábrica e handlers.
- `tests/integration/test_m1_t23.py:72`: round trip dos nove tipos.
- `tests/integration/test_m1_t23.py:92`: query strings reais/filtro Profile.
- `tests/integration/test_m1_t23.py:118`: erros/autorização/origem.
- `tests/integration/test_m1_t23.py:171`: budget explícito.
- `tests/integration/test_m1_t23.py:199`: redaction e proveniência.
- `tests/integration/test_m1_t23.py:237`: schema offline e contratos concretos.

O worker informou gate HTTP com 140 testes M1 antes da última correção;
após CHECKs, informou repetição com **141 passed, 435 deselected** e lint
PASS. O BUILD anterior passou com **575 Python, 19 Vitest, 4 Playwright**,
mas **precedeu `ac94851`**. O BUILD final foi iniciado e ficou sem confirmação
quando o worker atingiu quota. Não substituir essa lacuna por soma de testes
ou por resultado da árvore anterior. Reexecutar o gate na árvore final.

Falta registrar T23 em `execution.md`, conferir adequação/traceabilidade,
marcar seus critérios e Status Complete, atualizar contagem/handoff e criar
o commit previsto `feat(api): expose typed career resources`, depois dos
gates reais. Só então iniciar T24.

## 5. Decisões humanas novas nesta sessão

As decisões completas estão em [context.md](context.md),
[design.md](design.md) e [contracts-refinement.md](contracts-refinement.md).

| Hora local, 2026-11-17 | Decisão aprovada |
| --- | --- |
| 08:56 | Fonte manual: text obrigatório 1–8.000, title opcional até 256, idempotencyKey UUID; texto UTF-8 imutável por hash, confidential inicial, sem confirmar qualificações |
| 09:12 | metricValue como texto opcional preservado, sem conversão numérica automática |
| 09:13 | originalLabels lista de textos; category/metricType/metricUnit textuais sem taxonomia; metricMeaning textual; PartialDate value/precision; envelopes tipados de criação/leitura/lista |
| 09:32 | Profile filtra confirmation por confirmationField explícito; demais tipos por entidade; privacidade aplicada também antes do total |

Criação aprovada: content concreto, sourceDocumentId UUID, profileId
(null só Profile), idempotencyKey UUID, privacy e fieldPrivacy com nomes
fechados do DTO; confidential padrão, campo só mais restritivo. Confirmação,
principal, clearance e caminhos não são escolhidos pelo cliente.

Leitura: IDs/revisão, conteúdo concreto nullable, restrictedFields e
confirmação na granularidade correta; Profile usa fieldConfirmations.
Listas: items/offset/limit/total. Proveniência usa os campos do modelo
aprovado e só aparece quando autorizada.

Commits documentais desta sessão, além dos commits de tarefas/correções:

| Commit | Registro |
| --- | --- |
| `965ad8b` | Contrato aprovado da fonte manual |
| `4c19e38` | Reconciliação do progresso após fase 3 |
| `6cc5f72` | Proposta concreta dos refinamentos de DTO |
| `f993023` | Aprovação dos refinamentos e sincronização dos documentos |
| `f805b74` | Filtro explícito de confirmação do Profile |

Os resumos antigos em tasks/STATE chegaram a mostrar 6/64 ou 15/64 apesar
dos status individuais corretos. Foram reconciliados com git; no encerramento
o header de tasks está correto em 22/64. O bloco global de handoff é atualizado
junto com este arquivo para explicitar T23 em andamento.

## 6. Evidências de testes e falhas intermediárias

Resultados abaixo são da execução registrada, não testes novos executados
apenas para elaborar o handoff. Logs/resumos e âncoras de asserção por tarefa
estão em [execution.md](execution.md).

| Checkpoint | Python | Vitest | Playwright | Resultado |
| --- | --- | --- | --- | --- |
| Baseline T1 | 435 | 17 | 3 | BUILD PASS após instalar Chromium |
| Fim P1/T6 | 435 | 19 | 4 | BUILD PASS; asserção posterior 404 recebeu browser focal PASS |
| Fim P2/T13 | 484 | 19 | 4 | BUILD PASS |
| Fim P3/T17 | 509 | 19 | 4 | BUILD integral repetido PASS após reinstalar Chromium |
| P4 antes dos CHECKs finais | 575 | 19 | 4 | Worker informou BUILD PASS; não representa a árvore pós-ac94851 |
| Pós-CHECKs, focal/HTTP | 141 M1 + 435 deselected | não repetido nesse gate | não repetido nesse gate | Gate focal/HTTP e lint informados PASS |
| BUILD final P4 | não confirmado | não confirmado | não confirmado | Reexecutar; não declarar PASS |

Os BUILDs verdes incluem typecheck, build, contrato determinístico e lint.
Dois avisos de depreciação Python já existentes permanecem. Warnings de cor
ou fallback Ubuntu do Playwright não foram tratados como falha de produto.

Falhas/limitações registradas e tratadas nesta sessão:

- Sandbox inicial bloqueou `.git`, cache uv e consultas de rede; ocorreram
  pedidos de permissão. Uma chamada de commit do worker ficou pendente por
  700 s e foi abortada; o principal concluiu T6. Chamadas foram separadas
  para permitir os prefixes já autorizados.
- O ambiente depois mudou para full access/approval never; não tentar
  contornar nem reutilizar parâmetros de escalação do ambiente antigo.
- Chromium temporário faltou na baseline e novamente após interrupção;
  foi instalado na versão compatível, e gates foram repetidos.
- Spike JS inicial usou Node 26; foi repetido sob Node 24.18.0. O pnpm
  standalone embute Node 26, mas `pnpm exec node --version` com PATH correto
  confirmou Node 24.18.0 para scripts do projeto.
- Houve falhas de fixture/config/imports/flush, testes obsoletos de head/enum
  e downgrade encadeado; causas e repetições estão no execution, sem esconder
  falhas com retries ou remover testes.
- Primeiro teste de 404 da fixture sem sessão recebeu 401; precondição
  corrigida, proteção preservada.
- BUILD de P2 foi interrompido para vincular clearance ao Principal; apenas
  a repetição completa foi declarada PASS.
- O último BUILD P4 ficou sem resultado final após limite de uso do worker.

A medição de esforço contém timestamps observados, gates/esperas e limitações.
Não há tempo ativo líquido, custo/tokens ou duração de todas as esperas
medidos com precisão. Não reconstruir esses números por suposição.

## 7. Cobertura parcial e o que ainda não foi entregue

Marco: **M1**, REQ-KB-001/002/004 e REQ-SEC-001; alvo
AC-M1-001/002/003, rastreado pelos 38 MONEs da spec.

- MONE-01/02: CI preparado antes do domínio, resultados locais separados
  de remoto. Runner remoto continua NOT_RUN.
- MONE-03–13: fundação/contratos/criação/consultas e partes de revisão/
  privacidade implementadas. CRUD completo, relações e UI de confirmação/
  histórico ainda dependem das próximas fases. AC-M1-001 não está encerrado.
- MONE-14/15/30/31/32: armazenamento/metadados/fontes e transações possuem
  cobertura parcial; associação/importador/staging e recuperação completa
  ainda pendem. Não declarar AC-M1-002 entregue.
- MONE-16–29: staging, decisões, lote e undo não foram concluídos;
  AC-M1-003 permanece aberto.
- MONE-33/34: fixtures fictícias e redaction foram exercitadas nos caminhos
  implementados; cobertura dos fluxos futuros continua necessária.
- MONE-35–38: piloto sintético completo, Verifiers/sensores, revisão privada,
  relatório final e aceite do M1 continuam pendentes.

Não foram implementados nesta sessão os formulários/telas finais da KB,
propostas/decisões/confirmar/arquivar/histórico de todas as entidades,
importação do seed para staging, aplicação de lotes ou undo. Primitivas UI
de T6 e serviços de criação não significam que esses fluxos estejam prontos.
Não foram executados piloto independente, sensor final, carga privada ou
aceite humano. M1 continua in_progress, sem promoção para accepted.

## 8. Próximos passos exatos

1. Ler este arquivo, STATE, spec/context/design/refinamento e definições da
   tarefa atual; reconciliar branch/status/commits antes de editar. Não
   refazer T1–T22 nem descartar o diff T23.
2. Recuperar execução com **GPT Terra** conforme preferência do proprietário.
   Conferir artefatos T23 e testes; não presumir sucesso do último BUILD.
3. Executar geração/gates HTTP e BUILD da árvore final. Resolver falhas com
   evidência, sem enfraquecer asserções. Registrar resultados/adequação.
4. Fechar status/rastreabilidade de T23 e commit local atômico. Atualizar
   contagem para 23/64 somente quando realmente concluída.
5. Despachar o próximo lote sequencial P5, T24–T28: cliente TS gerado com
   erros/cancelamento, cache/sessão, Router/deep links, ProfileEditor e
   lista/detalhe. Esse é o primeiro checkpoint completo UI→API→SQLite.
6. Seguir os lotes aprovados: P6 T29–T36; P7 T37–T45; P8 T46–T53;
   P9 T54–T60. Cada worker executa todas as tarefas do lote em ordem;
   não criar workers em paralelo nem delegação aninhada.
7. Principal conduz P10: T61 Verifier fresco do piloto sintético antes de
   dados pessoais; T62 revisão privada humana; T63 documentação/evidências;
   T64 fechamento, seguido de Verifier final fresco, sensor e validate_state.
   Somente registrar aceite após evidência real e aprovação humana.

Pontos técnicos a carregar para as próximas tarefas:

- Repositório de baixo nível recebe campos previamente autorizados; nunca
  usar snapshot completo/ORM lazy para só então redigir dados em Python.
- Na futura leitura histórica de Evidence, aplicar capability e classificação
  **atual** da fonte também a sourceDocumentId/page/excerpt. A leitura
  corrente de T22 já faz isso; não confiar só no nível gravado no snapshot.
- Garantir conversão camelCase↔chave canônica, inclusive phoneOriginal;
  não limitar testes de privacidade a email.
- Preservar proveniência e confirmação de unidades independentes; alteração
  não herda confirmação anterior. Aceitar importação não confirma veracidade.
- Não usar Profile arquivado como motivo implícito para proibir referências;
  não inventar regra nova de negócio sem decisão.
- Limites individuais PDF/seed, parser de importação, dedup/ambiguidades,
  recuperação de arquivos e semântica de lotes/undo ainda têm tarefas próprias.
- Fonte/arquivo é independente do fato: liberar conteúdo derivado não libera
  PDF, seed, filename ou excerpt restritos.
- O orçamento de resposta é 1 MiB; falhar explicitamente pedindo seleção
  menor, sem truncar ou sinalizar sucesso parcial.

## 9. Comandos e ambiente para retomada

Ambiente atual: Linux, filesystem/network sem sandbox e approval policy
never. **Não fornecer `sandbox_permissions`** nas chamadas de comando.
Isso não amplia o escopo autorizado para push, deploy ou dados reais.

Pins novos/relevantes: Node 24.18.0, pnpm 11.28.9, Python 3.14.x;
Query 5.107.1, Router 7.18.5, RHF 7.92.0, Tailwind/plugin 4.3.5,
Radix Dialog 1.3.1, pypdf 6.21.4 e multipart 0.0.33. Usar os manifests e
locks atuais; não instalar latest ou trocar dependências por preferência.

```sh
export PATH=/home/williamf/.local/share/pnpm/bin:/home/williamf/.nvm/versions/node/v24.18.0/bin:/home/williamf/.local/bin:/usr/local/bin:/usr/bin:/bin
export PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright

git branch --show-current
git status --short
git log -10 --oneline

just generate
uv run --all-packages --locked pytest tests/unit tests/integration tests/smoke -q --basetemp=/tmp/rb-m1-tests -k m1
just check-contract
pnpm --filter web typecheck
just lint
just check
```

Se Chromium estiver ausente, instalar a versão do Playwright pinado com o
mesmo PLAYWRIGHT_BROWSERS_PATH antes de repetir o gate de browser/full:

```sh
pnpm --filter web exec playwright install chromium
```

Validadores documentais usados:

```sh
python3 /home/williamf/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/m1-career-kb/spec.md --strict
python3 /home/williamf/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/m1-career-kb/tasks.md --strict
git diff --check
```

Zero testes coletados não é PASS. Gerar OpenAPI/SDK no mesmo incremento HTTP;
testes de transporte não substituem testes de estado real. Só commitar T23
quando seus gates forem conferidos; não incluir alterações alheias por git add
indiscriminado. Não usar stash/reset para esconder trabalho pendente.

## 10. Limites de privacidade e referências

Nesta execução foram usados exclusivamente dados fictícios. Nenhum valor
pessoal, trecho de currículo, credencial ou hash privado foi incorporado ao
repo/CI. Arquivos reais foram inspecionados na preparação anterior, não
importados/revisados nesta execução. Sua localização permanece em context.md;
não é necessário reproduzir ou abrir esse conteúdo para continuar T23/UI.

Permanecem invariantes: sem browser de candidaturas no backend, sem MCP
genérico de shell/SQL/filesystem, sem submit_application, sem promoção de
output IA para fato canônico e sem fallback automático para API paga.

Referências de trabalho:

- [spec.md](spec.md): critérios, escopo e rastreabilidade MONE.
- [design.md](design.md): dados, autorizações, limites e transações.
- [context.md](context.md): decisões humanas e limites de uso das fontes.
- [contracts-refinement.md](contracts-refinement.md): contratos adicionais aprovados.
- [tasks.md](tasks.md): ordem, gates e critérios das 64 tarefas.
- [execution.md](execution.md): evidência detalhada por tarefa e falhas intermediárias.
- [STATE](../../STATE.md): snapshot global de retomada.
- [Estado canônico dos marcos](../../../docs/process/milestone-status.json).

Ao retomar, atualizar este snapshot se git/gates mostrarem fatos mais novos.
Este documento registra evidência e pendências; não declara release, integração
externa completa, importação privada ou aceite do marco.

Verificação desta documentação: validate_spec/validate_tasks estritos sem
erros ou avisos, 12 links locais válidos, contagem 22/64 e T23 Pending
conferidas, log Decisions de STATE preservado e diff-check limpo. Nenhuma
suíte de runtime foi repetida apenas para produzir o handoff.
