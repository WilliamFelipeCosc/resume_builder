# Riscos e mitigação

| ID | Risco | Impacto | Resposta e marco |
|---|---|---|---|
| R-001 | Incompatibilidade do MCP com diferentes CLIs | Alto | Spike M0.5 com dois clientes e matrix M4 |
| R-002 | Contexto confidencial exposto via tool/resource/search | Crítico | ContextPolicy antes de recuperação, testes negativos desde M0 |
| R-003 | IA inventar competências ou resultados | Crítico | Proveniência, ChangeSets, review, evals adversariais no M3 |
| R-004 | Agente externo envia sem autorização | Alto | Limites explicitados; não oferecer submit MCP; operador usa controles do agente; sem alegar enforcement fora MCP |
| R-005 | URL bloqueada / página dinâmica | Médio | Fallback manual/screenshot; não integrar browser no app |
| R-006 | Screenshot parcialmente ilegível | Médio | Confidence/uncertainties e revisão dos requisitos |
| R-007 | Retries duplicam reports ou inconsistência de BullMQ | Alto | IdempotencyKey, invariantes e reconciliadores em SQLite |
| R-008 | Backup inconsistente DB/arquivos | Alto | Snapshot SQLite + file manifest + restore test |
| R-009 | Custos/tokens de providers | Médio | Provider manual e quotas; sem fallback pago automático |
| R-010 | Escopo excessivo atrasa M3 | Alto | Vertical Slices, separar Core e Complete, limitar extras |
| R-011 | Vetor/embedding falha em extensão SQLite | Médio | Adapter substituível, benchmark e fallback FTS |
| R-012 | Tauri/RPM/Node runtime incompatível com distros | Médio | Spike de packaging e matrix Linux em M7 |
| R-013 | Sentry coleta PII involuntariamente | Alto | Opt-in, redaction antes de envio e testes |

Todos os riscos devem possuir owner e status quando o repositório começar. `R-001` e `R-005` são alvos prioritários de validação técnica.
