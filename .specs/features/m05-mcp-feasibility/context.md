# M0.5 MCP feasibility — contexto

**Coletado:** 2026-11-11
**Status:** contexto e especificação aprovados pelo proprietário em 2026-11-12;
desenho e tarefas aprovados na mesma data; execução não iniciada por instrução
explícita do proprietário. Manter uma decisão por vez ao retomar.

## Limite da feature

Validar MCP Python via `stdio` com dados sintéticos em Hermes e Codex,
com `get_application_context` e `report_application_progress`.
Um agente CLI externo preenche um formulário fictício usando suas próprias
ferramentas de navegador. Cobertura: AC-M05-001/002.

## Decisões confirmadas pelo proprietário

- Ritmo da entrevista: detalhado, uma decisão por vez, com discussão dos impactos
  antes de avançar.
- Hermes e Codex devem descobrir e chamar as duas ferramentas MCP.
- Apenas uma das CLIs precisa demonstrar o preenchimento do formulário.
  A outra terá compatibilidade MCP validada, sem alegação de preenchimento validado.
- A CLI da demonstração será escolhida após verificar as capacidades disponíveis.
- Relatos de progresso persistem após encerrar/reiniciar o MCP, até limpeza manual.
- A demonstração termina com os campos preenchidos e conferidos e o progresso
  registrado pelo agente, sem clicar em enviar.
- O formulário terá nome, e-mail fictício, cargo pretendido e resposta profissional
  pré-aprovada fornecida pelo contexto MCP; todos os valores serão sintéticos.
- O proprietário conferirá visualmente os quatro campos durante a demonstração,
  comparando seus valores com a fixture sintética. Essa conferência do formulário
  é distinta do relato de progresso e não representa confirmação de submissão.
- Framework escolhido pelo proprietário: pacote independente `fastmcp`
  (`from fastmcp import FastMCP`), com possibilidade de integração com FastAPI.
  A versão será validada no desenho técnico; a documentação que hoje prevê uso
  direto do SDK Python oficial será sincronizada com essa escolha.
- M0.5 valida somente `stdio`. Preparar a arquitetura para integração FastMCP
  com FastAPI, implementando o transporte MCP HTTP no M4. Não antecipar esse
  endpoint nem sua validação HTTP neste spike.
- Investigar incompatibilidades por até 60 minutos por cliente antes de apresentar
  diagnóstico e alternativas ao proprietário. Isso não autoriza substituir clientes
  nem concluir o marco com um gate pendente.
- Abordagem A aprovada em 2026-11-12: FastMCP chama Application Services Python
  diretamente; não depende de endpoints REST nem da API em execução para MCP.
- Autorização aprovada em 2026-11-12: perfis locais reutilizáveis, um por cliente,
  até remoção manual, com acesso somente à candidatura fictícia e às operações
  de consulta de contexto e registro de progresso. Sem concessão temporária por
  rodada e sem possibilidade de ampliar permissões pelos argumentos das tools.
- Relatos aprovados em 2026-11-12: somente etapas gerais — execução iniciada,
  formulário preenchido e execução bloqueada. Sem acompanhamento por campo e sem
  evento de submissão. Nomes JSON propostos: `started`, `form_filled`, `blocked`.
- Consulta aprovada em 2026-11-12: entrada com `applicationId`; projeção dos valores
  em `data.formValues` com `fullName`, `email`, `targetRole`, `approvedAnswer`,
  preservando metadados, referências e restrições do contexto. Essa projeção não
  define schema da Career KB nem do banco.
- Relato aprovado em 2026-11-12: entrada `applicationId`, `executionId`,
  `idempotencyKey`, `event`; eventos `started`, `form_filled`, `blocked`.
  Retorno em `data` com `receiptId` e `confirmationState=reported_by_agent`.
  Replay idêntico devolve recibo original; conteúdo diferente na mesma chave e
  execução retorna `CONFLICT`. Identidade vem do perfil local, não de `clientId`
  informado na chamada.
- Persistência aprovada em 2026-11-12: SQLite exclusivo do spike, tabela
  `mcp_spike_reports`, com `receipt_id` (PK), `client_id`, `application_id`,
  `execution_id`, `idempotency_key`, `event`, `confirmation_state`, `created_at`
  (UTC do servidor). Unicidade por cliente + candidatura + execução + chave de
  idempotência. Sem criação de tabela ou migração nesta etapa de planejamento.
- Limites aprovados em 2026-11-12: identificadores ASCII de 1–128 caracteres,
  usando letras, números e `._:-`; JSON de argumentos até 4 KiB e JSON de resposta
  até 16 KiB, excluindo o envelope JSON-RPC; valores textuais do formulário até
  2.000 caracteres cada; argumentos extras rejeitados.

## Limites herdados dos documentos aprovados

- Somente dados fictícios; sem acesso à Career KB privada.
- Sem controle de navegador integrado à aplicação.
- Relato externo não confirma submissão.
- `stdio` primeiro; HTTP e MCP completo pertencem ao M4.
- Integração do Hermes como provider de inferência é uma questão separada.
- Preservar o caminho prioritário até M3.

## Detalhes reservados ao desenho técnico

- Versão estável compatível do FastMCP a validar no desenho.
- Mecanismo de concessão local das capacidades, respeitando escopo por candidatura
  já exigido nos contratos aprovados; identidade não pode vir de alegação do tool.
- Schemas executáveis, limites, persistência e estratégia de testes serão propostos
  no desenho, sem presumir schema de banco ou dependências já instaladas.

## Referências

- [Roadmap](../../../docs/roadmap/milestones.md)
- [Critérios de aceite](../../../docs/roadmap/acceptance-criteria.md)
- [Módulo MCP](../../../docs/modules/mcp-server.md)
- [Contratos propostos](../../../docs/contracts/mcp-tools.md)

## Ideias adiadas

Nenhuma capacidade adicional aprovada nesta entrevista.
