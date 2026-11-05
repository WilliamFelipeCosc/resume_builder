# ADR-011 — Pino, OpenTelemetry e Sentry opt-in

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Problemas de extração, tokens, filas e reportes MCP exigem logs e diagnósticos, sem expor CVs.

## Decisão

Pino JSON + auditoria SQLite; OTel tracing/métricas com Jaeger opcional; Sentry SDK opt-in e sanitizado.

## Consequências

Instrumentação deve evitar spans duplicados e PII em telemetria; self-hosted Sentry não é exigido.

## Alternativas consideradas

Logs simples somente ou stack Grafana completa obrigatória foram descartados.

## Verificação

Traces correlacionados, reportes auditáveis, Sentry desabilitado por padrão e teste de redaction.
