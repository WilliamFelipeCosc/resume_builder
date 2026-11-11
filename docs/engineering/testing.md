# Estratégia de testes e AI Evals

**REQ-QA-001 — DECIDED:** cobertura completa implementada progressivamente ao longo da V1; Quality Gates obrigatórios na release.

## Pirâmide e suites

| Nível | Ferramenta sugerida | Conteúdo |
|---|---|---|
| Unit | Pytest (Python) / Vitest (frontend) | Domínio, políticas, ChangeSets, schemas, dedup, componentes |
| Integração | Pytest + SQLite/Redis isolados | SQLAlchemy 2/Alembic, Dramatiq, reindexação, auditoria, contratos OpenAPI e cliente TS gerado |
| UI E2E / export | Playwright Test e checks Python | Editor, revisão, preview, upload, PDF renderizado por Playwright Python/Chromium; extração, regressão visual e paginação dos templates visual/ATS |
| MCP Contract | Pytest + SDK Python client + fixtures | stdio/HTTP, tools/resources/prompts, autorização, versionamento |
| CLI Compatibility | Hermes + ao menos outro CLI | leitura + reporte com dados fictícios; logs de versão e limitações |
| AI evals | runner local + datasets versionados | extraction F1, evidence precision, unsupported claims, schema validity |
| Resiliência | fault injection controlado | Worker crash, Redis offline, retries, restore, replay report |

## Test doubles

`FakeAIProvider`, `FakeVisionProvider`, `FakeEmbeddingProvider`, `FakeMCPClient`, fixtures de páginas de vagas e formulários de teste. **Não** depender de APIs pagas para CI determinístico. Testes live manuais/controlados em branch de validação; isolar segredos e orçamento.

## Métricas

Extração: precisão/recall/F1 por requisito; matching: precision@k/recall@k e cobertura de lacunas; respostas: schema validity, factual support, unsupported claim rate, revisão humana; operações: latência, retries, entrega idempotente, vazamentos. Valor-alvo a calibrar por dataset e baseline; testes de privacidade e proibição de operações privilegiadas **não toleram regressões**.

## Critérios de confiança do M3

Ao menos três fixtures distintas de vaga (URL acessível, texto manual e screenshot legível) + caso de falha/baixa legibilidade; CV com evidências sustentadas; uma sugestão aprovada e outra rejeitada; PDF parsável com conteúdo vinculado à revisão; nenhum claim fabricado nos casos adversariais conhecidos; testes mínimos de permissões.

## Contratos MCP

Testar `stdio` logs fora de stdout; HTTP origin, host/auth e limites; capabilities; contexts autorizados/truncados; `idempotencyKey`; duplicação e reordenação de reportes; cliente não pode alterar status confirmed; compatibilidade comprovada em duas CLIs para concluir V1.

## Resultado de testes

Documentar o que foi efetivamente executado (comandos, ambiente, fixture versions, outputs, limitações). Não marcar testes live como aprovados com base em mocks. Os fixtures não contêm dados pessoais reais nem ações de envio a sites de emprego.
