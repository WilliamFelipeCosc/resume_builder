# Application Tracking

**Marco:** M5 (registro básico) e evolução V2.

## Registros V1

`Application` liga `JobPosting/JobSnapshot`, `ResumeRevision`, PDFs/exports, respostas usadas, datas, links, notas, empresa e etapa seletiva atualizada **manualmente**.

Eventos MCP podem criar linha do tempo operacional de execução externa: inicio, bloqueio, falha, relato de envio etc. Um relato não altera automaticamente estado humano de candidatura para enviado/verificado. `idempotencyKey` e `executionId` são obrigatórios na escrita de eventos por agente.

## Estados de confirmação

`reported_by_agent`: recebeu relato; `confirmed_by_user`: usuário declarou envio; `verified_by_evidence`: evidência analisada. Separar fonte de informação de estado do processo; evidência pode ser apenas alegação de um agente, não comprovação.

## M5 e V2

M5: lista, filtro, notas, etapas e vínculo entre vaga e currículo. V2: lembretes/follow-ups/notificações locais, e-mail/calendário, tracking avançado e workflow formal de aprovação por MCP.

## Aceite

AC-M5-002, AC-M4-002; reportes idempotentes, estados distinguíveis e nenhum envio de candidatura em testes reais.
