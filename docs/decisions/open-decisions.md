# Decisões abertas e pontos para spikes

As decisões abaixo **não bloqueiam** a geração da especificação nem o início de M0/M0.5, salvo onde explicitado. Não apresentá-las como se já tivessem sido aprovadas.

| ID | Estado | Tema | Resolução proposta |
|---|---|---|---|
| OPEN-001 | OPEN | Nome/branding do aplicativo | Escolher quando necessário para empacotamento |
| OPEN-002 | OPEN | Biblioteca UI, drag-drop e edição inline | Spike M2/M6; avaliar acessibilidade e compatibilidade com modelo |
| OPEN-003 | OPEN | Modelo local de embeddings, runtime, extensão vetorial | Benchmark M6; adapter + reindexação |
| OPEN-004 | OPEN | Método exato de ranking híbrido e pesos | Eval corpus SQL/FTS baseline vs RRF/outros |
| OPEN-005 | OPEN | SDK MCP, versões e nuances de transporte por CLI | Verificar libs atuais e testar em M0.5/M4; fixar versões reais |
| OPEN-006 | OPEN | Implementação prática de autenticação/capabilities MCP stdio/HTTP | Spike com mínimo privilégio; security review M4 |
| OPEN-007 | OPEN | Hermes provider local: interface, capacidades vision, autenticação/planos | Spike real e documentação; alternativas manuais |
| OPEN-008 | OPEN | Providers e parsing de screenshots por vision | Seleção da UI, rejeição segura se indisponível |
| OPEN-009 | OPEN | Metas quantitativas AI eval e benchmarks | Definir após fixtures/datasets baselines |
| OPEN-010 | OPEN | Distribuição Tauri/RPM e bundling de runtimes | Spike M7, matrix de Linux suportado |
| OPEN-011 | OPEN | Política exata de retenção para logs/backup | Configurável com defaults conservadores e revisão UX |
| OPEN-012 | OPEN | Implementação detalhada de export DOCX/validação ATS | Escolha de lib e fixture durante M6 |

**Decisões já fechadas (não reabrir sem ADR):** browser externo exclusivo; MCP read+report V1; aprovação MCP formal V2; roadmap B com M3 acelerado; M3 = análise+tailoring+PDF; DB SQLite/Drizzle; filas Redis/BullMQ; segurança B; testes B; observabilidade B+Sentry; distribuição B; instalação A; documentação B; retrieval híbrido V1/RAG avançado V2.
