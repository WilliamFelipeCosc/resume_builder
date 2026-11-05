# Observabilidade e auditoria

**REQ-OPS-001 — DECIDED.** Instrumentação progressiva: Pino + SQLite audit no início; OpenTelemetry e Jaeger opcional até V1; Sentry opt-in e sanitizado.

## Logs

JSON `event`, `service`, `requestId`, `traceId`, `applicationId?`, `jobId?`, `clientId?`, `durationMs`, `status`; sem textos de currículo, perguntas sensíveis, respostas, cookies ou tokens. Logs de MCP `stdio` em stderr, nunca stdout.

## Tracing

Rastreamento `API -> BullMQ -> Worker -> provider`, `CLI -> MCP -> service -> DB/AI`; correlação quando tecnicamente suportada; spans de Pino/OTel/Sentry sem instrumentação duplicada. Exemplos de spans: parse_job, context_retrieval, suggestion_generation, render_pdf, mcp_tool_call, report_persist.

## Métricas

Usage informado vs estimado; latência por provider/modelo/tarefa; erros de extração e suporte factual; aceite/rejeição de ChangeSets; tempos de filas; invocações MCP por tool/cliente, latência, relatos de bloqueio e resultados. Métricas não devem inferir a quantidade real de campos preenchidos se o cliente externo não reportou isso.

## Auditoria de domínio

Tabela append-only por API para fatos alterados/aprovados, changesets, exportações, consentimentos e relatos de agente. IDs e timestamps; retenção e exportação conforme política de privacidade. Audit log protegido operacionalmente, não imutável contra um administrador local com acesso ao banco.

## Sentry

Cloud opt-in com `beforeSend`/filtros de PII e secrets no cliente; performance/errors somente se permitido. Self-hosted não é dependência da V1. Controle de retenção local/externo e opção desativar em Settings.
