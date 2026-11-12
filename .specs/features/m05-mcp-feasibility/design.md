# M0.5 MCP feasibility Design

**Spec:** [spec.md](spec.md), aprovada pelo proprietário em 2026-11-12.
**Contexto:** [context.md](context.md).
**Status:** Approved — desenho consolidado aprovado pelo proprietário em
2026-11-12; decomposição de tarefas em preparação, sem implementação iniciada.

## Architecture Overview

FastMCP independente, somente `stdio` no M0.5. O cliente CLI inicia o processo
MCP; o navegador pertence ao agente externo. HTTP MCP e montagem no FastAPI são
M4. Ambas as opções abaixo preservam serviços de aplicação autorizados, persistência
de relatos sintéticos, duas ferramentas e os mesmos critérios de aceite.

### Abordagens para revisão

| Abordagem | Fluxo | Benefícios | Custos e limitações |
| --- | --- | --- | --- |
| A — serviços Python chamados diretamente, recomendada | CLI → FastMCP stdio → Application Services → repositório sintético | Segue a separação atual de core e adapters; MCP não exige API, Redis ou Worker em execução; FastAPI pode usar os mesmos serviços no M4 | Composição e concessão de capacidades próprias do processo MCP; isolamento e concorrência entre processos precisam de testes |
| B — FastAPI como mediador interno | CLI → FastMCP stdio → endpoints REST locais autorizados → Application Services → repositório sintético | API concentra execução dos serviços e persistência; MCP funciona como cliente do backend | Requer API ativa, endpoints REST sintéticos, autenticação específica e tratamento de indisponibilidade HTTP; não reutilizar cookies/permissões do diagnóstico como concessão MCP |

Em B, a conexão cliente–MCP continua em `stdio`; o HTTP seria exclusivamente um
salto interno REST. B não antecipa o transporte MCP HTTP, mas acrescenta dependências
operacionais e rotas ao spike. A não permite SQL genérico ao cliente: somente o
repositório interno acessa armazenamento mediante serviços autorizados.

O proprietário escolheu A em 2026-11-12. B permanece como alternativa considerada,
não como implementação planejada. Serviços de aplicação permanecem independentes
de FastMCP/FastAPI; o repositório é uma dependência interna desses serviços. Schemas
serão propostos para revisão, sem presumir campos de banco.

## Code Reuse Analysis

| Código existente | Uso possível / restrição |
| --- | --- |
| `backend/core/src/resume_core/service.py` | Reaproveitar separação de Principal, capacidades e Application Service; o serviço existente é específico de diagnóstico |
| `backend/core/src/resume_core/database.py` | Padrão SQLAlchemy, WAL e engine explícito; metadados e migração existentes são do M0, não são schema de candidatura |
| `backend/core/src/resume_core/paths.py` | Diretórios XDG por ambiente, permissões privadas e testes temporários; dedicar ambiente sintético ao spike |
| `backend/core/src/resume_core/logging_policy.py` | Logging sanitizado com saída padrão em stderr; novas categorias exigem extensão explícita da allowlist |
| `backend/api/src/resume_api/app.py` | Adapter HTTP futuro; sessão atual concede apenas capacidades de diagnóstico |
| `backend/migrations/env.py` | Padrão de migrations explícitas; estratégia de migração do armazenamento sintético ainda será proposta |

## Research & Evidence

Consulta em 2026-11-12; documentação não substitui teste de versão instalada:

- [FastMCP: execução e transportes](https://gofastmcp.com/docs/deployment/running-server):
  `stdio` usa subprocesso gerenciado pelo cliente. A mesma biblioteca oferece HTTP,
  sem obrigar sua ativação no M0.5.
- [FastMCP: integração FastAPI](https://gofastmcp.com/docs/integrations/fastapi):
  montagem ASGI é documentada; o lifecycle deve ser integrado. Esse código pertence
  ao M4. Evitar conversão automática de toda a API para ferramentas.
- Context7 `/prefecthq/fastmcp`: confirmou execução `stdio` e API de montagem;
  documentação pode refletir `main`, portanto ainda falta selecionar e resolver
  dependências de uma versão estável antes de declarar compatibilidade.
- Monorepo exige Python `>=3.14,<3.15`; dependências atuais de FastAPI/Pydantic e
  demais pins devem entrar na verificação de resolução. Nenhum pacote foi instalado
  ou lockfile alterado durante este planejamento.
- `codex --version`: `codex-cli 0.167.1`, exit 0; warning de impossibilidade de
  criar aliases de PATH no ambiente restrito. Não demonstra compatibilidade MCP.
- `hermes --version`: launcher informou bloqueio de escrita de `.install.lock`
  sob a instalação em `~/.hermes/installs/`; não retornou versão. Não foi executado
  `hermes pm repair`. Versão e execução ainda precisam de verificação permitida.
- Não há `.codegraph/` no checkout; navegação por arquivos conhecidos e ripgrep.
- Não há lições confirmadas no repositório.

## Risks & Concerns

| Concern | Localização | Impacto | Mitigação |
| --- | --- | --- | --- |
| Identidade/permissões HTTP específicas do M0 | `backend/api/src/resume_api/app.py:143` | Reutilização indevida concede diagnóstico ou depende de cookie Web | Concessão MCP própria, escopada e definida no desenho; nunca confiar no clientId enviado como identidade autenticada |
| Metadados existentes só representam diagnóstico | `backend/core/src/resume_core/database.py:23` | Confundir evento sintético com dados reais ou alterar schema sem revisão | Propor armazenamento e migration dedicados antes de implementar |
| Categorias de logging fechadas | `backend/core/src/resume_core/logging_policy.py:13` | Eventos MCP podem perder identificação ou vazar dados se contornarem política | Projetar categorias e testar redaction e stdout, incluindo logs de dependências |
| Compatibilidade de dependências não resolvida | `backend/core/pyproject.toml:4` | Uma versão FastMCP pode conflitar com os pins Python do monorepo | Resolver em cópia temporária durante desenho sem alterar lockfiles reais; só afirmar compatibilidade após evidência |
| Launcher Hermes grava fora do workspace até para consultar versão | comando `hermes --version` | Sandbox bloqueia inventário e eventualmente execução live | Consultar metadados locais ou executar passo autorizado no ambiente adequado; sem reparo ou mudança global presumida |
| Relato do agente não comprova formulário nem envio | `spec.md`, SPIKE-11/14 | Aceite falso baseado apenas em autorrelato | Comparação visual pelo proprietário, registrada separadamente; sem clique de envio |

## Local Authorization

O proprietário aprovou perfis de execução reutilizáveis até remoção manual em
2026-11-12: um para Hermes e outro para Codex, selecionados na inicialização local,
com acesso somente à candidatura fictícia e às duas operações. Isso identifica o
perfil configurado, não autentica criptograficamente o executável da CLI; o usuário
Linux e suas configurações são a fronteira de confiança. Nenhum argumento de tool
pode ampliar permissões ou substituir a identidade configurada. Não haverá
aprovação interativa MCP por chamada nem novo fluxo remoto de aprovação.

O mecanismo exato de armazenamento/carregamento dos perfis será descrito no desenho
antes de implementar; remoção do perfil deverá impedir novas inicializações. Não
há alegação de revogação instantânea de processos já iniciados: encerrar suas sessões
locais faz parte da remoção operacional.

## Next Design Decision

Desenho consolidado aprovado em 2026-11-12. Próximo passo: revisar as tarefas,
gates e ferramentas antes da execução. Nomes de arquivos, tipos físicos, formato
dos perfis e detalhes do envelope abaixo foram aprovados como desenho futuro;
não são schemas existentes nem funcionalidades já implementadas.

## Context Contract

Estrutura aprovada pelo proprietário em 2026-11-12:

- Entrada: `applicationId`, sem caminho de arquivo, SQL ou identidade do cliente.
- Saída: quatro valores em `data.formValues` com os nomes `fullName`, `email`,
  `targetRole` e `approvedAnswer`.
- Preservar metadados, referências e restrições do contexto e envelope previstos
  nos contratos de referência. A especificação executável e seus limites ainda
  serão detalhados; o contrato não cria campos presumidos de banco ou da Career KB.
- Dados vêm de uma fixture sintética versionada. A resposta pré-aprovada é
  conteúdo fixo dessa fixture, sem geração de resposta por IA no app.

## Progress Events

O proprietário escolheu em 2026-11-12 somente as etapas gerais: execução iniciada,
formulário preenchido e execução bloqueada. Valores JSON aprovados no contrato
de relato: `started`, `form_filled`, `blocked`. Sem evento
por campo, submissão ou promoção de estado confirmado. Os eventos são relatos;
não impõem uma máquina de estados da candidatura real neste spike.

## Progress Contract

Contrato aprovado em 2026-11-12:

- Entrada: `applicationId`, `executionId`, `idempotencyKey`, `event`.
- `event`: `started`, `form_filled` ou `blocked`; sem texto livre ou valores dos
  campos do formulário no relato mínimo.
- Retorno em `data`: `receiptId` e `confirmationState=reported_by_agent`.
- A identidade é obtida do perfil local e não de um `clientId` enviado pela tool.
- Repetição com a mesma chave e conteúdo na mesma execução devolve o recibo
  original; mudança de conteúdo devolve `CONFLICT` sem alterar o registro.

## Synthetic Report Persistence

Schema aprovado pelo proprietário em 2026-11-12, sem execução de migration:

- SQLite dedicado ao spike, isolado do banco M0 e de dados profissionais.
- Tabela `mcp_spike_reports`: `receipt_id` (PK), `client_id`, `application_id`,
  `execution_id`, `idempotency_key`, `event`, `confirmation_state`, `created_at`.
- Todos os campos são obrigatórios. `created_at` é horário UTC gerado pelo servidor.
- Restrição UNIQUE em (`client_id`, `application_id`, `execution_id`,
  `idempotency_key`). Identidade vem do perfil; a comparação de `event` distingue
  replay de conflito dentro dessa combinação.
- Uma transação registra evento e unicidade; resposta somente após commit.
  Em concorrência, a restrição do banco decide o vencedor; o outro processo lê o
  registro persistido e retorna o mesmo recibo ou `CONFLICT`.
- O replay devolve o recibo original; `requestId` do envelope pode ser novo, pois
  identifica a chamada, não o evento persistido.
- Planejar migration Alembic própria e reversível, sem upgrade do banco M0.
  SQLAlchemy 2 e padrões de engine/WAL do core serão reaproveitados.
- Relatos permanecem até limpeza manual; não há TTL automático nem Redis/Worker
  no caminho síncrono das duas ferramentas.

## Components

Proposta de organização, sujeita à revisão final do desenho:

| Componente | Local proposto | Interface / responsabilidade |
| --- | --- | --- |
| Contratos | `backend/core/src/resume_core/mcp_spike/contracts.py` | DTOs Pydantic estritos; aliases JSON aprovados; sem importar FastMCP/FastAPI |
| Autorização | `backend/core/src/resume_core/mcp_spike/policy.py` | Principal local com cliente, candidaturas e capacidades; checar antes de recuperar ou gravar |
| Serviços | `backend/core/src/resume_core/mcp_spike/service.py` | `get_application_context(principal, query)` e `report_application_progress(principal, report)`; resultados/erros de domínio |
| Repositório | `backend/core/src/resume_core/mcp_spike/repository.py` | Inserção transacional, replay, conflito e leitura local de recibos |
| Metadados sintéticos | `backend/core/src/resume_core/mcp_spike/database.py` | Tabela aprovada e engine dedicada; sem alterar `diagnostic_runs` |
| Adapter FastMCP | `backend/mcp_server/src/resume_mcp_server/server.py` | Registrar exatamente as duas tools, converter DTOs e sanitizar erros; chamar serviços, sem SQL direto |
| Composição/CLI local | `backend/mcp_server/src/resume_mcp_server/__main__.py` | Inicialização, perfis, migrations explícitas, inspeção específica de relatos e servidor stdio |
| Migração do spike | `backend/mcp_server/migrations/` | Histórico Alembic separado, upgrade/downgrade exclusivamente no banco sintético |
| Fixture e formulário | `data/synthetic/mcp-spike/` | Contexto versionado e HTML estático com quatro campos |

`backend/mcp_server` entra no uv workspace com dependências explícitas de
`resume-core` e `fastmcp==4.1.8`. A API e o Worker não passam a depender do adapter
FastMCP. O core não passa a depender da biblioteca FastMCP.

## DTOs and Wire Contract

Os dois argumentos de consulta/relato seguem o formato plano aprovado; não haverá
wrapper adicional `request` exigido do cliente. Funções do adapter podem usar nomes
camelCase para preservar o contrato publicado; domínio Python usa snake_case com
aliases Pydantic. Modelos rejeitam extras e coerção indevida de tipos.

### Envelope proposto

| Campo | Tipo / significado |
| --- | --- |
| `schemaVersion` | Literal `m05.v1` |
| `data` | Contexto ou recibo tipado |
| `provenance` | Lista de referências sintéticas `{sourceId, version}`; no relato, lista vazia |
| `truncated` | Literal `false`; spike falha explicitamente em vez de cortar silenciosamente |
| `policy` | `{clientId, applicationId, capabilities}` efetivos e filtrados pelo servidor |
| `requestId` | UUID textual gerado pelo servidor para a chamada |

Metadados do contexto em `data`: `applicationId`, `jobSnapshotId`,
`resumeRevisionId`, `approvedAnswers` (lista de textos fixos da fixture),
`evidenceRefs` (referências sintéticas), `restrictions` e `formValues` aprovado.
Os identificadores de snapshot/revisão são stubs explícitos da fixture, sem
afirmação de existência na KB ou no Resume Studio. A resposta profissional em
`formValues.approvedAnswer` corresponde ao texto da fixture em `approvedAnswers`.
As restrições indicam dados fictícios e proibição de envio no experimento.
Decisão do proprietário: `evidenceRefs` é lista de IDs sintéticos sujeitos ao
padrão de identificadores aprovado; `restrictions` é lista de textos no spike.

O recibo em `data` contém somente `receiptId` e
`confirmationState=reported_by_agent`. `requestId` muda por chamada; `receiptId`
permanece igual no replay. `clientId`, source ou estado de confirmação não são
argumentos controlados pela tool. Não há inferência de submissão nem promoção de
fato canônico.

### Limites aprovados e aplicação técnica

- Identificadores: 1–128 caracteres, regex ASCII `^[A-Za-z0-9._:-]{1,128}$`.
- Entrada: máximo de 4.096 bytes; saída: máximo de 16.384 bytes, inclusive envelope
  de aplicação, excluindo o wrapper JSON-RPC/MCP.
- Medida canônica: JSON compacto, UTF-8, `ensure_ascii=False`, sem espaços de
  separação. O limite mede conteúdo validado, não os espaços extras do frame original.
- Quatro valores textuais: até 2.000 caracteres Unicode cada, com limite total de
  bytes prevalecendo. Identificadores e valores não são normalizados silenciosamente.
- As entradas de consulta/relato não contêm texto livre, paths ou credenciais.
- Validação do schema e do tamanho antecede efeitos de domínio. Saída da fixture
  é validada no preparo; resposta excedente falha com código seguro, sem truncamento.
- O limite dos argumentos não é alegado como limite de frame pré-parse do SDK.
  Testar o comportamento do transporte em frames malformados e confirmar seus
  limites efetivos na versão pinada, sem prometer isolamento de processo hostil.

## Profile Configuration Proposal

Arquivos locais propostos: `profiles/hermes.json` e `profiles/codex.json` sob o
diretório XDG de configuração do ambiente `mcp-spike`. Campos propostos:

```json
{
  "clientId": "hermes",
  "applicationIds": ["app-demo"],
  "capabilities": ["application_context:read", "application_progress:write"]
}
```

O outro arquivo usa `clientId=codex`. Esses nomes são uma proposta de schema de
configuração, não dados inferidos de um arquivo existente. Pydantic rejeita
capacidades desconhecidas, extras, candidaturas fora da fixture e wildcards.

Comando proposto: `python -m resume_mcp_server serve --profile hermes` ou `codex`.
Seleção de perfil é local; argumentos MCP não podem selecionar perfil, arquivo
de banco, fixture ou ampliar capacidades. A configuração da CLI especificará o
executável absoluto do ambiente já instalado, sem baixar dependências ao iniciar.

Diretórios privados `0700`, arquivos `0600`, proprietário UID local, sem symlinks
nos caminhos validados; falhar fechado para perfil ausente, inválido ou permissivo.
Perfis não contêm tokens de providers. O subprocesso recebe somente variáveis de
ambiente operacionais necessárias e o contexto sintético, sem repassar segredos
desnecessários; mecanismos de ambiente de cada CLI precisam de teste real.
Mesmo UID é a fronteira de confiança, não uma sandbox de filesystem contra o
próprio proprietário. Perfis removidos impedem nova inicialização; processos em
execução devem ser encerrados para revogar o acesso já carregado.

## Physical Storage Proposal

Arquivo proposto `mcp-spike.sqlite3` no diretório XDG de dados `mcp-spike`.
Campos aprovados serão representados como `TEXT NOT NULL`; `created_at` será
ISO 8601 UTC com sufixo `Z`, gerado no servidor. `receipt_id` é UUID textual.
CHECKs limitam `event` aos três valores e `confirmation_state` a `reported_by_agent`.
PK e UNIQUE seguem o schema aprovado. Não guardar valores do formulário ou payload
arbitrário nessa tabela.

Usar SQLAlchemy 2, transações curtas, WAL e timeout de lock de 250 ms já adotado
no core. Em `IntegrityError` da combinação única: rollback, leitura do registro
existente e comparação de evento. Lock ocupado ou indisponibilidade retorna erro
temporário; não fabricar recibo nem fazer retry automático ilimitado. Cliente pode
repetir com a mesma chave após falha ou perda de resposta.

Inicialização/migração é comando local explícito. `serve` exige schema atualizado e
não roda upgrade silencioso. Testar upgrade e downgrade em bancos temporários, além
de persistência/replay entre dois processos distintos. Fixture é somente leitura;
relatos e profiles pertencem ao ambiente sintético. Remoção é manual, com sessões
encerradas e caminhos fixos; nunca aceitar path arbitrário de limpeza pela tool.

## Error Handling Strategy

| Cenário | Resposta proposta | Efeitos |
| --- | --- | --- |
| Sem capacidade ou fora da candidatura concedida | `NOT_AUTHORIZED` | Nenhuma recuperação de conteúdo nem escrita |
| Candidatura concedida sem fixture correspondente | `CONTEXT_NOT_FOUND` | Nenhum contexto inventado |
| Tipo, extra, identificador ou tamanho inválido | `SCHEMA_INVALID` | Nenhum efeito de domínio |
| Chave existente com evento diferente | `CONFLICT` | Registro original intacto |
| SQLite indisponível, ocupado ou falha antes do commit | `TEMPORARILY_UNAVAILABLE` | Sem recibo de sucesso; retry com mesma chave |
| Saída acima do limite | `CONTEXT_TRUNCATED` | Sem resposta parcial apresentada como completa |
| Exceção inesperada | `INTERNAL_ERROR` | Mensagem fixa, sem valores, stack, path ou segredo |

Erros de tool usam MCP `isError=true` com conteúdo textual JSON do envelope seguro
`{schemaVersion, error:{code,message}, requestId}`. Erros de framing/negociação
permanecem erros de protocolo MCP; não prometer requestId de domínio quando a
chamada ainda não chegou ao adapter. O adapter/middleware deve sanitizar também
erros de validação do framework; testes com sentinelas verificam ausência de echo
de valores e argumentos rejeitados nos dois streams.

## Dependency Decision and Evidence

Candidato pinado: **FastMCP 4.1.8**, com resolução **MCP 2.3.0 / mcp-types 2.3.0**.
Publicado em 2026-11-10 segundo [PyPI](https://pypi.org/project/fastmcp/4.1.8/).
Em 2026-11-12, `uv pip compile --no-build` para Python 3.14/Linux x86_64 resolveu
78 distribuições mantendo todos os 31 pins de registry do lock existente.

Evidências versionáveis, sem dados pessoais:

- [Entrada da resolução](research/dependency-input.txt).
- [Resultado pinado](research/dependency-resolution.txt).
- [Comando, hash do lock e limites da evidência](research/dependency-evidence.json).

Consulta inicial ao PyPI falhou por DNS no sandbox; execução com permissão de rede
restrita ao comando de resolução passou. Somente `/tmp` recebeu cache/resultado;
nenhuma instalação ou edição do lock real. A integração deve gerar o lock real
durante a implementação e rodar testes na versão pinada. Resolução não prova
compatibilidade runtime nem suporte real dos dois clientes.

FastMCP documenta `strict_input_validation=True`, rejeição de argumentos extras e
mascaramento de exceções; confirmar APIs na versão pinada com teste de contrato.
Referências: [tools](https://gofastmcp.com/docs/servers/tools),
[settings](https://gofastmcp.com/docs/more/settings). Nenhuma funcionalidade de
`main` é tratada como comprovada por esse levantamento.

## Fake Form and Local Operation

HTML estático de teste, quatro campos com rótulos visíveis, sem script ou integração
de navegador. Um servidor local dedicado serve apenas os assets fixos do cenário
em loopback, com validação de Host; não expõe diretórios arbitrários. Pode ter um
controle de envio inerte para tornar o limite da tarefa visível; não terá backend
de submissão. Não introduz endpoint MCP HTTP nem depende de autenticação da API M0.

O agente externo recebe URL e instrução de consultar o MCP; os quatro valores
esperados ficam na fixture, não são fornecidos diretamente no prompt da tarefa.
O operador escolhe cliente com ferramentas de navegador verificadas. O agente
preenche, para antes de enviar e relata `form_filled`; se não conseguir prosseguir,
relata `blocked`. Proprietário confere os quatro valores ao vivo; a conferência é
registrada separadamente em evidência local. Não afirmar envio, aprovação de fatos
ou integração com agentes antes dessa execução real.

Comandos locais propostos no justfile: `mcp-spike-init`, `mcp-spike-serve <profile>`,
`mcp-spike-form`, `mcp-spike-reports <profile>` e `check-mcp-spike`. São comandos
específicos de operação, não ferramentas MCP nem shell genérico exposto ao cliente.
Detalhar invocações na documentação operacional da implementação. Instalação de
dependências e edição das configurações de Hermes/Codex exigem preparação concreta;
nada disso foi executado nesta fase.

Investigações de incompatibilidade: registrar início/fim e interromper após até
60 minutos de investigação ativa por cliente para apresentar diagnóstico. Tempo
aguardando o proprietário não é investigação ativa. Alternativa de cliente ou
continuação além desse limite exige reavaliação com o proprietário; gate pendente
não vira PASS. Não há fallback automático para provider pago.

## Test Coverage Matrix

Todos os testes abaixo são planejados, não executados nesta fase.

| Requisitos | Verificação de resultado |
| --- | --- |
| SPIKE-01 | Subprocesso stdio negocia e lista exatamente duas tools, nomes/schema/argumentos planos; repetir em cada CLI real |
| SPIKE-02 | Retorno igual à fixture, inclusive metadados e quatro valores; evidência de chamada real Hermes e Codex |
| SPIKE-03/10 | Principal sem capacidade e candidatura não concedida: NOT_AUTHORIZED, sem recuperação ou escrita |
| SPIKE-04 | Ambiente temporário e mcp-spike não leem banco M0/private; perfis/caminhos inválidos e symlinks rejeitados |
| SPIKE-05 | stdout contém apenas frames MCP; stderr sanitizado; testar startup, exceções e dependências com sentinelas |
| SPIKE-06 | Ambas as CLIs registram progresso; recibo corresponde a evento persistido |
| SPIKE-07 | Encerrar servidor após recibo, iniciar outro processo e repetir: mesmo evento e recibo |
| SPIKE-08/09 | Mesma chave/evento: um recibo; evento divergente: CONFLICT e original preservado |
| SPIKE-11 | Nenhum evento cria estado confirmado ou submissão verificada; enums/DB impedem valores indevidos |
| SPIKE-12/13 | CLI real usa seu browser, consulta MCP e preenche quatro campos, parando antes de envio |
| SPIKE-14 | Checklist do proprietário com quatro comparações individuais; ausência mantém AC pendente |
| SPIKE-15 | Recibo form_filled é relato separado da conferência humana |
| SPIKE-16 | Relatório com versões efetivas, configurações sanitizadas, comandos, resultados e limitações; sem alegar live a partir de mocks |
| SPIKE-17 | Evidência operacional de tempo/diagnóstico quando houver incompatibilidade; não precisa provocar uma hora de falha em teste |
| SPIKE-18 | Serviços testáveis sem FastMCP/FastAPI; adapter chama serviços e não repositório diretamente |
| SPIKE-19 | Extras, tipos, IDs vazios/129 chars, ASCII indevido, entrada 4.096/4.097 bytes, saída 16.384/16.385 e Unicode multibyte |
| SPIKE-20 | Falha de commit e lock ocupado não devolvem sucesso; nova tentativa pode persistir com segurança |
| SPIKE-21 | Dois processos com mesma chave/evento convergem para um registro/recibo; divergência concorrente preserva vencedor |

Fronteiras textuais 2.000/2.001 caracteres testadas junto ao teto total de bytes.
Testes Pytest usam fixtures fictícias e diretórios temporários; não usam configs
pessoais nem providers live por padrão. SQLite/Alembic reais para persistência.
Vitest/Chromium existentes permanecem nos checks de regressão M0. Não criar executor
de browser no backend para substituir a demonstração pelo agente externo.

Após implementação: `just check`, check específico MCP, verificação de locks,
testes reais Hermes/Codex e demonstração com proprietário. Verifier independente
deriva cobertura dos 21 requisitos e executa sensor em cópia isolada; mutações
prioritárias: autorização removida, replay duplicando, recibo antes do commit,
confirmação indevida e log de conteúdo em stdout. Não enfraquecer testes para PASS.

## Remaining Risks and Mitigations

- Adicionar 47 distribuições à resolução aumenta a superfície de dependências:
  fixar lock, não habilitar extras opcionais e revisar o diff do lock na implementação.
- Erros do framework podem expor argumentos mesmo com logs locais filtrados:
  testar máscara de validação e garantir mensagens fixas antes de aceitar o gate.
- CLI com acesso ao browser não está demonstrada: inventário e execução reais
  escolhem qual cliente fará o formulário; a outra continua obrigada a testar MCP.
- Perfis locais não são isolamento contra processos do mesmo UID: documentar
  a fronteira e não extrapolar a dados profissionais; auth HTTP pertence ao M4.

## Documentation Impact and Review Boundary

Após aprovação do desenho em 2026-11-12, `PROJECT_SOURCE.md`, módulo/contratos MCP
e decisões abertas foram sincronizados; ADR-016 registra a escolha FastMCP
independente autorizada pelo proprietário. ADR-004/005 preservam suas responsabilidades.
Não afirmar versão validada em clientes a partir da resolução. O desenho não
implementa nem testa MCP HTTP.

Próximo artefato após aprovação: tarefas atômicas, gates e dependências. Não há
tarefas executadas, migrations, instalação FastMCP ou edição global de clientes
neste planejamento. AC-M05-001/002 continuam pendentes de execução real.
