# M0.5 MCP feasibility Specification

**Status:** APPROVED — contexto e especificação aprovados pelo proprietário em
2026-11-12; desenho e tarefas aprovados; execução aguardando autorização explícita
do proprietário, sem implementação.
**Marco:** M0.5; REQ-MCP-001 e recortes de REQ-SEC-001/002,
REQ-OPS-001 e REQ-QA-001; AC-M05-001/002.
**Contexto:** [decisões da entrevista](context.md).

## Problem Statement

M0 validou a infraestrutura local, mas não a interoperabilidade MCP com agentes
CLI reais. Precisamos comprovar consultas autorizadas e relatos persistidos em
Hermes e Codex, além de um preenchimento fictício conduzido externamente, antes
de depender dessa integração no produto completo.

## Goals

- Validar as duas ferramentas via `stdio` em Hermes e Codex reais.
- Demonstrar quatro campos fictícios preenchidos por uma CLI e conferidos pelo
  proprietário, sem clicar em enviar.
- Preservar relatos idempotentes após reinício e documentar resultados reproduzíveis.
- Usar FastMCP independente, preservando integração com FastAPI no M4.

## Out of Scope

| Capacidade | Motivo |
| --- | --- |
| MCP HTTP montado no FastAPI | M4; M0.5 valida `stdio` |
| MCP V1 completo, resources/prompts adicionais e sugestões de IA | Não necessários para AC-M05-001/002 |
| Hermes como provider de inferência da aplicação | Viabilidade distinta de Hermes como cliente MCP |
| KB real, currículo privado e candidaturas reais | Experimento exclusivamente sintético |
| Controle de navegador na aplicação | ADR-004; browser pertence ao agente CLI externo |
| Envio, inclusive envio simulado do formulário | Proprietário escolheu parar com campos preenchidos |
| Confirmação de submissão ou aprovação remota via MCP | Relato não confirma envio; workflow formal é V2 |
| CI, Tauri, embeddings e mudanças de escopo M1–M3 | Roadmap vigente; checks locais neste spike |
| Compatibilidade universal ou preenchimento em ambas as CLIs | Só uma CLI demonstra navegador; ambas validam MCP |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Framework | Pacote independente `fastmcp` | Escolha explícita do proprietário | Sim |
| Integração FastAPI | Serviços compartilháveis agora; MCP HTTP no M4 | Preservar evolução sem antecipar transporte | Sim |
| Clientes | Hermes e Codex chamam ambas as tools | Alvos do kickoff e entrevista | Sim |
| Demonstração browser | Uma CLI, escolhida pelas capacidades verificadas | Critério suficiente para AC-M05-002 | Sim |
| Formulário | Nome, e-mail fictício, cargo e resposta profissional pré-aprovada | Escolha explícita do proprietário | Sim |
| Conferência | Proprietário compara os quatro campos com a fixture durante a execução | Evidência distinta do autorrelato | Sim |
| Persistência | Relatos sobrevivem ao reinício até limpeza manual | Escolha explícita do proprietário | Sim |
| Investigação de incompatibilidades | Até 60 minutos por cliente antes de reavaliar | Limitar o spike e apresentar diagnóstico | Sim |
| Escopo de autorização | Contexto e escrita limitados à candidatura concedida localmente | Contratos MCP existentes exigem escopo e capacidade | Herdado; mecanismo no desenho |
| Schemas, versões e armazenamento | Propor no desenho antes da implementação | Não presumir schema de banco nem pacote compatível | Delimitação técnica; sem schema definido |
| Instalações e configuração de CLIs | Planejar comandos e alterações exatas após inventário | Planejamento não afirma dependências instaladas nem compatibilidade | Delimitação operacional |

**Open questions:** none sobre comportamento de produto nesta proposta; escolhas
técnicas acima estão explicitamente reservadas ao desenho, com revisão antes de
implementar. Esta especificação não congela os rascunhos de DTOs como schemas finais.

## User Stories

### P1: Consultar contexto fictício por duas CLIs

**User Story:** Como proprietário, quero consultar os mesmos dados fictícios por
Hermes e Codex para verificar a conexão MCP em clientes reais.

**Acceptance Criteria**:
1. WHEN Hermes ou Codex executar `tools/list` na sessão autorizada THEN o servidor SHALL anunciar exatamente `get_application_context` e `report_application_progress` com schemas de entrada válidos para o protocolo. (SPIKE-01)
2. WHEN cada uma das duas CLIs chamar `get_application_context` para a candidatura sintética autorizada THEN o serviço SHALL devolver os quatro valores esperados da fixture versionada. (SPIKE-02)
3. IF uma chamada solicitar uma candidatura fora da concessão local THEN o serviço SHALL rejeitá-la com `NOT_AUTHORIZED` sem revelar seu conteúdo. (SPIKE-03)
4. The servidor SHALL limitar seu acesso a fixtures e armazenamento sintéticos dedicados ao spike. (SPIKE-04)
5. The processo MCP SHALL reservar `stdout` ao protocolo e emitir logs operacionais sanitizados em `stderr`. (SPIKE-05)

**Independent Test:** Executar descoberta e consulta em sessões reais de ambas as
CLIs, comparar retorno com fixture e executar negativos de escopo e vazamento.
Teste do SDK ou mock não substitui a evidência dos clientes reais.

### P1: Relatar progresso sem criar confirmação de envio

**User Story:** Como proprietário, quero receber relatos persistidos para verificar
que o canal bidirecional funciona, preservando a distinção entre relato e confirmação.

**Acceptance Criteria**:
1. WHEN cada CLI enviar um progresso válido e autorizado por `report_application_progress` THEN o serviço SHALL devolver um recibo somente após persistir o evento como relato do agente externo. (SPIKE-06)
2. WHEN o servidor reiniciar após devolver um recibo THEN o armazenamento SHALL preservar o mesmo evento e recibo até limpeza manual. (SPIKE-07)
3. WHEN a mesma execução repetir um relato com a mesma `idempotencyKey` e o mesmo conteúdo validado THEN o serviço SHALL devolver o recibo original sem criar outro evento. (SPIKE-08)
4. IF a mesma chave de idempotência for reutilizada na mesma execução com conteúdo diferente THEN o serviço SHALL devolver `CONFLICT` sem alterar o evento original. (SPIKE-09)
5. IF uma execução não tiver capacidade de escrita para a candidatura solicitada THEN o serviço SHALL rejeitar o relato com `NOT_AUTHORIZED` sem persistir o evento. (SPIKE-10)
6. The serviço SHALL preservar os relatos como `reported_by_agent`, sem criar confirmação humana ou verificação de submissão a partir da chamada MCP. (SPIKE-11)

**Independent Test:** Enviar relato por ambas as CLIs, verificar persistência,
reiniciar, repetir a chamada e conferir recibo e quantidade de eventos. Testar
conflito e escrita negada. Consulta de evidências pode usar comando local específico
ou teste, sem adicionar ferramenta MCP de leitura genérica do banco.

### P1: Demonstrar o formulário e registrar a compatibilidade

**User Story:** Como proprietário, quero observar um agente externo preencher um
formulário local com contexto MCP e conferir os campos antes de concluir o spike.

**Acceptance Criteria**:
1. WHEN a CLI selecionada receber a tarefa de demonstração THEN o agente externo SHALL obter os quatro valores pelo MCP e preencher os campos correspondentes usando suas próprias ferramentas de navegador. (SPIKE-12)
2. WHEN os quatro campos estiverem preenchidos THEN a demonstração SHALL parar antes de acionar envio do formulário. (SPIKE-13)
3. WHEN o proprietário conferir o formulário THEN o registro da demonstração SHALL indicar o resultado da comparação de cada um dos quatro campos com a fixture esperada. (SPIKE-14)
4. WHEN a CLI concluir o preenchimento THEN o agente externo SHALL registrar o progresso pelo MCP, mantendo o relato separado da conferência humana. (SPIKE-15)
5. The relatório de validação SHALL identificar versões efetivas de Python, FastMCP, SDK MCP e CLIs, comandos, configuração sanitizada, resultados de descoberta e chamadas, cliente do navegador e limitações. (SPIKE-16)
6. IF a investigação de incompatibilidade atingir 60 minutos em um cliente THEN o responsável pelo spike SHALL apresentar diagnóstico e alternativas ao proprietário antes de continuar investigando esse cliente. (SPIKE-17)
7. The implementação MCP SHALL chamar Application Services com autorização, independentes do transporte, preservando sua reutilização por FastAPI no M4. (SPIKE-18)

**Independent Test:** Rodar o cenário com uma CLI real e o proprietário presente,
registrar as quatro comparações e o recibo do progresso. Combinar essa evidência com
as chamadas reais da outra CLI para avaliar os dois ACs do marco.

## Edge Cases

- IF argumentos não corresponderem ao schema publicado THEN a fronteira SHALL rejeitar a chamada sem executar a operação de domínio. (SPIKE-19)
- IF a persistência falhar antes do commit THEN o serviço SHALL não devolver recibo de sucesso. (SPIKE-20)
- WHEN relatos idênticos com a mesma chave chegarem concorrentemente na mesma execução THEN o armazenamento SHALL preservar um único evento e um único recibo. (SPIKE-21)

Erros de protocolo respeitarão MCP; erros de domínio seguirão o envelope tipado
proposto no desenho. Nomes, formatos, limites em bytes e persistência serão
explicitados nesse documento antes da implementação. Nenhuma ferramenta admite
shell, SQL genérico, caminhos arbitrários ou confirmação de submissão.

## Implicit-requirement dimensions

| Dimensão | Cobertura ou limite |
| --- | --- |
| Validação e limites | SPIKE-01/19; modelos e limites numéricos propostos no desenho |
| Falhas e falhas parciais | SPIKE-20; sem recibo de sucesso antes de persistir |
| Idempotência e retries | SPIKE-08/09/21; nova chamada segura sem retry automático obrigatório |
| Autorização e rate limits | SPIKE-03/04/10; capacidades e limites do subprocesso no desenho; HTTP fora de escopo |
| Concorrência e ordem | SPIKE-21; armazenar relatos, sem prometer ordenação causal do agente |
| Ciclo de vida | SPIKE-07; retenção até limpeza manual, isolada dos dados reais |
| Observabilidade | SPIKE-05/16; separar evidência de execução de logs operacionais |
| Dependências externas | SPIKE-17; testes live reais separados de mocks; provider do app N/A por não ser usado |
| Integridade de estado | SPIKE-11; progresso não promove candidatura a enviada ou verificada |

## Requirement Traceability

T1 concluída parcialmente para SPIKE-04, SPIKE-16 e SPIKE-18; os requisitos
permanecem pendentes até os respectivos testes e evidências de integração.
T2 cobre parcialmente os contratos de SPIKE-01, SPIKE-02, SPIKE-06, SPIKE-11 e
SPIKE-19; os requisitos permanecem pendentes de execução pelos serviços e clientes.
T3 cobre a fixture de SPIKE-02, SPIKE-04, SPIKE-12 e SPIKE-14; os requisitos
continuam pendentes de validação ponta a ponta e conferência do proprietário.

| Requirement ID | Story / comportamento | Fonte e aceite | Phase | Status |
| --- | --- | --- | --- | --- |
| SPIKE-01 | Catálogo mínimo | REQ-MCP-001; AC-M05-001 | Tasks: T2, T11, T17, T18, T20 | Pending |
| SPIKE-02 | Contexto nas duas CLIs | REQ-MCP-001; AC-M05-001 | Tasks: T2, T3, T8, T11, T17, T18, T20 | Pending |
| SPIKE-03 | Escopo de leitura | REQ-SEC-001/002; AC-M05-001 | Tasks: T4, T8, T11, T20 | Pending |
| SPIKE-04 | Dados sintéticos isolados | REQ-SEC-001; ambos ACs | Tasks: T1, T3, T4, T5, T6, T8, T10, T12, T13, T14, T15, T16, T19, T20 | Pending |
| SPIKE-05 | Protocolo e logs | REQ-OPS-001; AC-M05-001 | Tasks: T10, T11, T12, T17, T18, T20 | Pending |
| SPIKE-06 | Relato nas duas CLIs | REQ-MCP-001; AC-M05-001 | Tasks: T2, T7, T9, T11, T17, T18, T20 | Pending |
| SPIKE-07 | Sobreviver ao reinício | Entrevista; AC-M05-001 | Tasks: T5, T6, T7, T12, T20 | Pending |
| SPIKE-08 | Replay idempotente | Contratos events/mcp-tools; AC-M05-001 | Tasks: T5, T7, T9, T12, T17, T18, T20 | Pending |
| SPIKE-09 | Conflito de conteúdo | Contrato events; AC-M05-001 | Tasks: T5, T7, T9, T20 | Pending |
| SPIKE-10 | Escrita autorizada | REQ-SEC-002; AC-M05-001 | Tasks: T4, T9, T11, T20 | Pending |
| SPIKE-11 | Relato sem confirmação | REQ-MCP-001; integrity hard gate | Tasks: T2, T5, T6, T9, T11, T17, T18, T19, T20 | Pending |
| SPIKE-12 | Formulário por agente externo | ADR-004; AC-M05-002 | Tasks: T3, T13, T14, T16, T19, T20 | Pending |
| SPIKE-13 | Parar sem enviar | Entrevista; AC-M05-002 | Tasks: T13, T14, T16, T19, T20 | Pending |
| SPIKE-14 | Conferência dos quatro campos | Entrevista; AC-M05-002 | Tasks: T3, T13, T16, T19, T20 | Pending |
| SPIKE-15 | Progresso após preenchimento | REQ-MCP-001; ambos ACs | Tasks: T9, T19, T20 | Pending |
| SPIKE-16 | Evidências reproduzíveis | REQ-QA-001; ambos ACs | Tasks: T1, T10, T12, T15, T16, T17, T18, T19, T20 | Pending |
| SPIKE-17 | Reavaliar incompatibilidade | Entrevista; gestão de escopo | Tasks: T16, T17, T18, T20 | Pending |
| SPIKE-18 | Serviços reutilizáveis | Arquitetura aprovada; entrevista | Tasks: T1, T4, T8, T9, T11, T12, T15, T20 | Pending |
| SPIKE-19 | Rejeitar entrada inválida | REQ-SEC-002; AC-M05-001 | Tasks: T2, T4, T8, T11, T12, T20 | Pending |
| SPIKE-20 | Falha ao persistir | REQ-MCP-001; AC-M05-001 | Tasks: T7, T9, T11, T20 | Pending |
| SPIKE-21 | Replay concorrente | Contrato events; integrity hard gate | Tasks: T5, T7, T20 | Pending |

**Coverage:** 21 requisitos mapeados a T1–T20 em [tasks.md](tasks.md), com
matriz de cobertura e gates para revisão. Nenhum requisito está implementado ou
verificado; tarefas aprovadas, execução ainda não autorizada.

## Success Criteria

- [ ] Hermes e Codex reais listam e chamam as duas ferramentas: AC-M05-001.
- [ ] Uma CLI real preenche os quatro campos e relata progresso, com conferência
  visual do proprietário e sem envio: AC-M05-002.
- [ ] Testes de contrato, autorização, isolamento, logs, persistência e idempotência
  passam; checks existentes de M0 continuam passando.
- [ ] Evidências live identificam versões e limitações; mocks não são classificados
  como validação de compatibilidade real.
- [ ] Verifier independente avalia os requisitos e as evidências ao fim da execução.

## Sequência planejada

Revisar contexto e especificação → desenhar contratos, autorização local,
persistência e versão FastMCP → decompor em tarefas verificáveis → implementar
e testar localmente → executar as duas CLIs e demonstração visual → verificar
independentemente e registrar o resultado.

Falha em Hermes ou Codex mantém o aceite correspondente pendente. Alternativas
serão propostas ao proprietário sem substituição silenciosa. Configurar ferramentas
externas de navegador não autoriza introduzir controle de navegador na aplicação.

## Documentation Impact

Na consolidação do desenho, sincronizar a escolha FastMCP com `PROJECT_SOURCE.md`,
`docs/modules/mcp-server.md`, contratos relevantes e uma nota de decisão adicional,
preservando as responsabilidades dos ADRs 004/005. A proposta presente registra a
escolha já autorizada sem declarar a stack instalada ou compatível.
