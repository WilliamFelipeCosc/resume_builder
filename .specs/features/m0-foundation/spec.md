# M0 — Foundation mínima

**Status:** contrato e abordagem de recuperação aprovados em 2026-11-11; desenho e execução aprovados em 2026-11-11; T1–T8 concluídas; workspaces, bootstrap isolado, paths e contratos verificados, fluxo integrado pendente.
**Gathered:** 2026-11-11.
**Context:** [context.md](context.md).
**Fontes:** [PROJECT_SOURCE.md](../../../PROJECT_SOURCE.md), [roadmap](../../../docs/roadmap/milestones.md), [ACs](../../../docs/roadmap/acceptance-criteria.md).

## Problem Statement

O repositório contém especificações e referências, mas ainda não demonstra comunicação Web/API/Worker, persistência, autorização ou recuperação. M0 precisa provar essa base com uma operação sintética, sem antecipar os módulos de currículo, para acelerar construção e exportação do currículo em M1/M2/M3.

## Goals

- Demonstrar diagnóstico fixo completo: Web → FastAPI → SQLite → Dramatiq/Redis → resultado persistido → Web.
- Demonstrar acesso local autorizado e logs sanitizados desde o início.
- Demonstrar migração Alembic, contrato OpenAPI e cliente TypeScript gerado.
- Demonstrar recuperação após Redis indisponível e reinício do Worker, sem duplicar efeito.
- Disponibilizar comandos e checks locais reproduzíveis; nenhum teste de aplicação foi executado ainda.

## Out of Scope

| Item | Destino / motivo |
|---|---|
| Perfil profissional, currículo, PDF pessoal e seeds reais | M1/M2; M0 usa apenas fixtures sintéticas |
| Exportar currículo e templates de produção | M2; estilos/gerador importados continuam referências |
| Vagas, IA e providers live | M3; não há tarefa que precise deles em M0 |
| MCP e execução de CLIs/agentes | Spike M0.5 separado, com Hermes e Codex; não iniciar por este escopo |
| GitHub Actions | M1; checks somente locais em M0 |
| Histórico navegável e tarefas concorrentes na UI | Última execução e uma execução ativa bastam para M0 |
| Análise adicional de Reactive Resume | Atividade opcional posterior; AC-M0-003 não é gate |
| Tauri/RPM, embeddings, backup, rotação de logs, OTel/Sentry completo | Marcos posteriores conforme roadmap |
| Controle de navegador de candidaturas, shell/SQL genéricos MCP | Proibidos pelos invariantes aprovados |
| Instalação automática de ferramentas/sistema, push/deploy | Não fazem parte deste planejamento |

## Assumptions & Open Questions

Os contratos abaixo foram aprovados pelo proprietário em 2026-11-11. DDL e mecanismo de autenticação do Design também aprovados em 2026-11-11; sem implementação.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|---|---|---|---|
| Objetivo | M3 rapidamente, sobretudo construção/exportação do currículo | Prioridade do proprietário; sem limite semanal definido por enquanto | Sim |
| Demonstração | Diagnóstico com dados fixos e uma execução ativa por ambiente | Provar infraestrutura sem antecipar negócio | Sim |
| Sessão | Comando local abre Web autorizada; validade até a API encerrar/reiniciar | Sem digitação recorrente ou credencial permanente no navegador | Sim; mecanismo técnico pendente de validação no Design |
| Recuperação | Prazo total 120 s, até 3 tentativas, até 30 s por tentativa | Recuperação controlada e falha com limite conhecido | Sim |
| UI e dados | Último estado restaurado, sem histórico navegável; banco isolado por ambiente, testes temporários e limpeza manual | Persistência verificável sem painel operacional | Sim |
| Logs | JSON no terminal, sem arquivo por padrão | Diagnóstico mínimo sem antecipar retenção/backup | Sim |
| Contrato de execução | Campos e estados da seção Contrato proposto | Base aprovada na entrevista | Campos/estados sim; tipos e semântica abaixo propostos para revisão |
| Resultado do diagnóstico | Objeto fixo `message=diagnostic_completed`, `fixtureVersion=m0-v1` | Resultado esperado conhecido, independente de dados profissionais | Sim; aprovado em 2026-11-11 |
| Requests | UUIDs opacos, timestamps UTC RFC 3339, corpo JSON até 1 KiB, rejeição de campos extras | Contrato limitado e testável | Sim; aprovado em 2026-11-11 |
| Erros HTTP | 401 sem sessão, 403 origem/host rejeitado, 409 execução ativa distinta, 413 corpo excessivo, 422 contrato inválido | Diferenciar falhas sem expor conteúdo privado | Sim; aprovado em 2026-11-11 |
| Atualização da tela | Polling com intervalo proposto de 1 s, retomado ao reabrir a página | Suficiente para M0 sem SSE ou WebSockets | Sim; aprovado em 2026-11-11 |
| Observação do prazo | Com a API ativa, reconciliar vencimentos a cada 1 s; ao reiniciar, reconciliar antes de retornar o estado | Processos desligados não podem escrever estado; nenhum trabalho vencido pode retomar ou concluir com sucesso | Sim; aprovado em 2026-11-11 |
| Ambiente inicial | Nobara Linux 44 observado; pnpm 11.28.9 instalado pelo proprietário e verificado com `pnpm --version`; versões do projeto ainda serão selecionadas/verificadas | Ferramenta disponível não comprova compatibilidade das dependências nem define pin de versão | Ambiente observado; seleção técnica no Design |
| CI e MCP | CI em M1; Hermes/Codex em M0.5 separado | Decisões do proprietário | Sim |

**Open questions:** none — decisões funcionais e contrato de diagnóstico aprovados; bootstrap e schema físico aprovados no Design, com prova técnica obrigatória do bootstrap. A viabilidade do mecanismo de abertura autorizada deve ser comprovada antes de implementar o fluxo; se exigir alternativa, voltar ao proprietário.

## Contrato aprovado

Este é um contrato de aplicação para diagnóstico sintético, não o schema da Career KB nem DDL definitivo.

| Campo | Tipo e semântica propostos |
|---|---|
| id | UUID de execução, gerado pelo servidor, imutável |
| requestId | ID de correlação da criação; preservado entre API, fila e Worker |
| idempotencyKey | UUID da intenção de executar; único no ambiente; retry de transporte reutiliza a chave |
| status | `pending`, `queued`, `running`, `succeeded`, `failed` |
| attemptCount | Inteiro de 0 a 3; conta inícios efetivos de processamento, não consultas ou mensagens duplicadas |
| createdAt | Timestamp UTC da intenção persistida; início do prazo total de 120 s |
| updatedAt | Timestamp UTC da última transição persistida |
| result | Nulo até sucesso; objeto fixo com `message` e `fixtureVersion` descritos acima |
| deliveryWarning | Opcional/nulo; código estável e mensagem sanitizada de indisponibilidade transitória da entrega; removido quando a entrega for reconhecida ou a execução se tornar terminal |
| error | Nulo sem falha terminal; objeto com código estável e mensagem sanitizada, sem stack/payload/token |

Estados propostos: `pending` significa intenção persistida ainda sem entrega reconhecida ao broker; `queued` significa entrega reconhecida aguardando Worker; `running` significa tentativa com posse válida; `succeeded` e `failed` são terminais. Reentrega segura pode levar `running` a `pending/queued` após perda de posse, dentro do mesmo ID, orçamento de tentativas e prazo. Mensagem atrasada não regride estado terminal. Abordagem aprovada: o próprio registro é a intenção durável, com reconciliador na API e posse temporária por tentativa, sem tabela outbox separada. Mensagens podem ser reentregues; o resultado persistido não pode ser duplicado. Detalhes de posse/reconciliação serão propostos no Design.

Rotas aprovadas: `GET /api/health`, `POST /api/diagnostics` e `GET /api/diagnostics/latest`. O POST recebe apenas `idempotencyKey`; fixture e resultado não são escolhidos pelo cliente. Health expõe somente liveness mínimo; dados do diagnóstico exigem sessão válida. Acesso direto à Web sem sessão pode mostrar instrução de abertura local, sem expor diagnósticos.

Uma nova intenção após estado terminal cria outro ID e outra chave. Repetir a chave anterior retorna a mesma execução, sem criar outro resultado. Uma intenção distinta enquanto houver execução ativa recebe 409. Nenhuma decisão de endpoint ou campo desta seção foi implementada.

## User Stories

### P1: Executar e consultar o diagnóstico

**User Story:** Como proprietário, quero executar um diagnóstico pela Web e ver o resultado persistido para comprovar a base antes de construir o currículo.

**Acceptance Criteria**:
1. WHEN o usuário autorizado clicar em executar THEN the system SHALL persistir uma execução com `status=pending` antes de tentar publicar trabalho no Redis. [FND-01]
2. WHEN o Worker concluir a fixture fixa THEN the system SHALL persistir uma única conclusão `succeeded` com o resultado definido no contrato. [FND-02]
3. WHILE existir execução `pending`, `queued` ou `running` the system SHALL desabilitar o botão de nova execução na Web. [FND-03]
4. WHEN a Web autorizada for reaberta THEN the system SHALL mostrar o último estado e resultado persistidos no ambiente. [FND-04]
5. IF uma chave de idempotência já registrada for reenviada THEN the system SHALL retornar a mesma execução sem outro efeito de processamento. [FND-05]
6. IF uma nova intenção distinta chegar enquanto outra execução estiver ativa THEN the system SHALL rejeitá-la com 409 sem criar outra execução. [FND-06]

**Independent Test:** Iniciar stack local isolada, abrir Web pelo comando local, executar fixture, conferir resultado no SQLite e na tela, reabrir e consultar o mesmo ID. Reenviar a chave e tentar intenção concorrente por cliente de teste autorizado.

### P1: Controlar falhas e retomar sem duplicar

**User Story:** Como proprietário, quero ver falhas de infraestrutura e retomar trabalho pendente sem precisar descobrir inconsistências no banco.

**Acceptance Criteria**:
1. IF o Redis estiver indisponível ao criar o diagnóstico THEN the system SHALL preservar a intenção `pending` e indicar espera/falha de entrega sanitizada na Web. [FND-07]
2. WHEN o Redis voltar antes do prazo e com orçamento disponível THEN the system SHALL retomar a entrega da mesma execução sem criar outra intenção. [FND-08]
3. IF o Worker for interrompido durante processamento THEN the system SHALL recuperar a mesma execução após reinício dentro do prazo/orçamento, sem duplicar o resultado. [FND-09]
4. The system SHALL limitar a validade de cada tentativa efetiva do Worker a 30 segundos, rejeitando efeitos após esse limite; encerramento físico de código bloqueado não é garantido. [FND-10]
5. IF a terceira tentativa falhar ou a execução atingir 120 segundos desde `createdAt` antes de uma conclusão válida THEN the system SHALL persistir `failed` e mostrar erro sanitizado, sem nova tentativa automática. [FND-11]
6. WHILE uma execução estiver terminal the system SHALL impedir que reentregas atrasadas alterem sua conclusão. [FND-12]

**Independent Test:** Redis real isolado indisponível/recuperado e Worker interrompido/reiniciado; verificar mesmo ID e uma conclusão. Testes de tempo com relógio controlado devem cobrir os limites sem aguardar dois minutos em cada caso. Com a API ativa, vencimento deve ser persistido no ciclo seguinte de reconciliação, proposto em até 1 s; após reinício, reconciliar antes de retornar o estado. Nenhuma tentativa começa ou conclui com sucesso depois do prazo, independentemente do ciclo de observação.

### P1: Abrir com autorização local e bloquear acesso indevido

**User Story:** Como proprietário, quero abrir o app pelo comando local sem digitar credenciais e impedir consultas sem sessão válida.

**Acceptance Criteria**:
1. WHEN o comando local de abertura for executado THEN the system SHALL abrir a Web com uma sessão autorizada sem pedir credencial ao usuário. [FND-13]
2. IF uma leitura/escrita de diagnóstico não tiver sessão válida THEN the system SHALL responder 401 antes de acessar dados de diagnóstico ou enfileirar trabalho. [FND-14]
3. WHEN a API reiniciar THEN the system SHALL rejeitar a sessão anterior até nova abertura autorizada pelo comando local. [FND-15]
4. The system SHALL manter a API vinculada a loopback e rejeitar Host/Origin fora da configuração local autorizada. [FND-16]
5. IF requisição exceder 1 KiB ou violar o contrato proposto THEN the system SHALL rejeitá-la com 413 ou 422 respectivamente, sem criar execução. [FND-17]
6. The system SHALL emitir logs JSON com IDs de correlação sem incluir credenciais, cookies, corpo bruto, documentos ou mensagens de exceção não sanitizadas. [FND-18]

**Independent Test:** Abertura local e testes de sessão ausente/inválida/expirada, Host/Origin, corpo excessivo e campos extras; inserir sentinelas sintéticas e verificar ausência nos logs/erros. Mecanismo de bootstrap, cookie/CSRF, CORS e portas exatas precisam de proposta e prova técnica antes da implementação; não há bypass de desenvolvimento.

### P1: Reproduzir persistência, contratos e checks locais

**User Story:** Como desenvolvedor, quero montar e verificar a foundation com instruções reproduzíveis e dados isolados para que M1/M2 possam usar a mesma base.

**Acceptance Criteria**:
1. WHEN a migração Alembic inicial for aplicada em um SQLite temporário vazio THEN the system SHALL criar o schema necessário ao diagnóstico e permitir a execução de teste. [FND-19]
2. WHEN o contrato OpenAPI for exportado e o cliente TS for gerado THEN the system SHALL passar o check de tipos do frontend sem manter DTOs manuais duplicados. [FND-20]
3. WHEN os checks locais documentados forem executados THEN the system SHALL demonstrar Web/FastAPI/Worker iniciados, migração, fixture real SQLite/Redis/Worker, negativos de autorização e logs sanitizados. [FND-21]
4. The system SHALL isolar dados por ambiente e usar bancos temporários nos testes sem ler ou alterar currículo/seeds privados. [FND-22]
5. The system SHALL manter a inicialização do Redis sob comando manual do operador e não instalar dependências do sistema automaticamente. [FND-23]

**Independent Test:** Seguir instruções a partir de diretórios vazios de dados/cache de teste e ferramentas previamente disponíveis, registrar versões/comandos/resultados. Pytest para backend/integração, Vitest para comportamento da Web e demonstração real da Web consumindo a API; mocks não substituem prova do Worker/Redis real. Rollback da migração inicial só em banco temporário, conforme desenho posterior.

## Implicit-requirement dimensions

| Dimensão | Tratamento no escopo de M0 |
|---|---|
| Validação e limites | Corpo fixo/tipado, limite aprovado de 1 KiB, sessão e origem/host, FND-17 |
| Falha e falha parcial | Intenção antes da fila, prazo/tentativas e erro sanitizado, FND-07…11 |
| Idempotência, retry, duplicata | Mesma chave/ID e efeito único, FND-05/08/09/12 |
| Autorização e limites de chamadas | Sessão, origem/host, uma execução ativa por ambiente, FND-06/13…17; nenhum endpoint de dados de produto |
| Concorrência e ordem | Exclusão de execução ativa e transições terminais protegidas, FND-06/12 |
| Ciclo de vida | Último resultado persistido, isolamento e limpeza manual; sem retenção automática em M0 |
| Observabilidade | structlog JSON no terminal e requestId, FND-18; auditoria de negócio completo em marcos posteriores |
| Dependências externas | Redis/Worker/SQLite testados; providers e MCP N/A porque não são usados pelo diagnóstico |
| Integridade de transições | Estados e orçamento documentados; transições e relógio sob testes de recuperação |
| Privacidade | Somente fixture sintética; sem currículo privado, providers, telemetria ou export de conteúdo pessoal |

## Requirement Traceability

| Requirement ID | Critério / cobertura | Fonte REQ / AC | Phase | Status |
|---|---|---|---|---|
| FND-01 | Intenção persistida antes da fila | AC-M0-001 | Tasks: T8, T11, T15, T17 | Partial: T8 |
| FND-02 | Conclusão persistida | AC-M0-001 | Tasks: T6, T9, T18 | Partial: T6 |
| FND-03 | Botão e execução ativa | AC-M0-001; entrevista | Tasks: T20 | Pending |
| FND-04 | Reabertura | AC-M0-001; entrevista | Tasks: T8, T11, T16, T20 | Partial: T8 |
| FND-05 | Idempotência | AC-M0-001; entrevista | Tasks: T8, T11, T15 | Partial: T8 |
| FND-06 | Concorrência | AC-M0-001; entrevista | Tasks: T7, T8, T11, T15 | Partial: T7/T8 |
| FND-07 | Redis indisponível | AC-M0-001; entrevista | Tasks: T17, T20, T21 | Pending |
| FND-08 | Retomada da entrega | AC-M0-001; entrevista | Tasks: T10, T17, T21 | Pending |
| FND-09 | Worker interrompido | AC-M0-001; entrevista | Tasks: T9, T10, T18, T21 | Pending |
| FND-10 | Timeout da tentativa | AC-M0-001; entrevista | Tasks: T9, T10, T18, T21 | Pending |
| FND-11 | Falha terminal | AC-M0-001; entrevista | Tasks: T10, T16, T17, T18, T21 | Pending |
| FND-12 | Proteção terminal | AC-M0-001; entrevista | Tasks: T9, T10, T17, T18, T21 | Pending |
| FND-13 | Abertura autorizada | REQ-SEC-002; AC-M0-002 | Tasks: T4, T13, T14, T20 | Partial: T4 |
| FND-14 | Bloqueio sem sessão | REQ-SEC-001/002; AC-M0-002 | Tasks: T11, T14, T15, T16 | Pending |
| FND-15 | Reinício de sessão | REQ-SEC-002; entrevista | Tasks: T4, T13, T14, T20 | Partial: T4 |
| FND-16 | Loopback e Host/Origin | REQ-SEC-002; AC-M0-002 | Tasks: T4, T13, T14, T15, T16 | Partial: T4 |
| FND-17 | Limites de contrato | REQ-SEC-002; AC-M0-001/002 | Tasks: T6, T14, T15 | Partial: T6 |
| FND-18 | Logs sanitizados | REQ-OPS-001; AC-M0-002 | Tasks: T4, T12, T14, T15, T16, T18 | Pending |
| FND-19 | Migração | AC-M0-001 | Tasks: T7, T22 | Partial: T7 |
| FND-20 | OpenAPI e cliente TS | AC-M0-001 | Tasks: T1, T3, T6, T19, T22 | Partial: T1/T3/T6 |
| FND-21 | Checks locais | REQ-QA-001; AC-M0-001/002 | Tasks: T1, T2, T3, T21, T22 | Partial: T1/T2/T3 |
| FND-22 | Isolamento | REQ-SEC-001/002; entrevista | Tasks: T2, T5, T7, T21, T22 | Partial: T2/T5/T7 |
| FND-23 | Operação manual | REQ-LIN-001; ADR-002/012 | Tasks: T1, T5, T22 | Pending |

**Coverage:** 23 requisitos mapeados às 22 tarefas; T1–T6 implementadas e verificadas localmente. Desenho e execução aprovados; AC-M0-001/002 integrados pendentes.

## Success Criteria

- Um diagnóstico real completo demonstrado na Web com SQLite/Redis/Worker reais e dados sintéticos.
- Negativos de autorização/logs e falhas/recuperação executados com evidência local.
- Manifestos, contratos gerados, migração e instruções reproduzíveis verificados.
- AC-M0-001/002 demonstrados; M0.5 não tratado como parte concluída de M0.
- Nenhuma instalação, execução live, compatibilidade MCP ou conclusão de M0 alegada a partir desta documentação.
