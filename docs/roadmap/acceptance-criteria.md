# Critérios de aceite e Quality Gates

**DECIDED:** V1 conclui com aceitação funcional e Quality Gates mensuráveis. Thresholds quantitativos de IA serão calibrados por datasets; não inventar metas científicas sem baseline. Metas de privacidade e ações proibidas são hard gates.

## Aceite por marco

| ID | Marco | Critério verificável |
|---|---|---|
| AC-M0-001 | M0 | Web/API/Worker iniciam, migration SQLite e job BullMQ passam em teste |
| AC-M0-002 | M0 | Proteção mínima bloqueia consulta não autorizada e logs não incluem secrets |
| AC-M05-001 | M0.5 | `stdio` lista/usa tools em Hermes e outra CLI com dados sintéticos, evidências de execução |
| AC-M05-002 | M0.5 | Cliente externo preenche formulário fake sem browser integrado no app |
| AC-M1-001 | M1 | CRUD/vínculos KB preservam provenance, privacy e fact revisions |
| AC-M2-001 | M2 | Currículo gerado com template ATS, texto extraível, revisão e PDF |
| AC-M3-001 | M3 | URL acessível, texto manual e imagem legível são importados e geram JobSnapshot |
| AC-M3-002 | M3 | URL bloqueada e screenshot incompleto são tratados com fallback e lacunas explícitas |
| AC-M3-003 | M3 | Parser extrai requisitos em fixture versionada; matching cita evidências existentes |
| AC-M3-004 | M3 | IA propõe ChangeSet fundamentado, usuário pode aceitar/rejeitar e comparar diff |
| AC-M3-005 | M3 | PDF exportado liga JobSnapshot, ResumeRevision e validation report corretos |
| AC-M3-006 | M3 | Informação privada não aparece em contexto não autorizado; afirmação inventada conhecida é barrada |
| AC-M4-001 | M4 | Contratos MCP funcionam em stdio e HTTP com schemas e errors estáveis |
| AC-M4-002 | M4 | Reports são idempotentes, identidade/capability verificadas, result `reported` não `confirmed` |
| AC-M5-001 | M5 | Resposta nova usa evidências e marca unknown/sensitive, não altera fatos silenciosamente |
| AC-M5-002 | M5 | Status seletivo continua manual; relato externo não afirma envio verificado |
| AC-M6-001 | M6 | Editor inline + drag/drop, chat/sugestões, templates e DOCX/HTML funcionais |
| AC-M6-002 | M6 | Importação KB com staging/revisão e híbrido SQL+FTS+embeddings avaliados |
| AC-M7-001 | M7 | Backup local restaurado após verificação e migrations, incluindo arquivos e vínculos |
| AC-M7-002 | M7 | Suite de segurança (MCP, privacidade, token leakage, CSRF/origin/host) passa sem regressão |
| AC-M7-003 | M7 | Dados sintéticos em pelo menos duas CLIs passam casos de leitura+reportes |
| AC-M7-004 | M7 | Observabilidade, Sentry opt-in, retenção/redaction e auditoria demonstrados |
| AC-M7-005 | M7 | Web local e Tauri/RPM executam em Linux suportado, `doctor` diagnostica dependências |

## Quality Gates globais

1. **Security hard gate:** sem vulnerabilidade conhecida nos cenários testados que exponha confidencial/secret ou conceda capability não autorizada; sem creds em log/test artefact; reviews de segurança antes de ativar HTTP/telemetria.
2. **Truthfulness hard gate:** afirmações sem apoio nas fixtures adversariais devem ser rejeitadas/sinalizadas; fato canônico não pode ser modificado por IA sem aprovação.
3. **MCP integrity hard gate:** agente externo não altera estado confirmado por simples relato; idempotência e validação de contrato.
4. **Functional gates:** testes unit/integration/E2E críticos verdes, import/preview/export/restauração nos fluxos documentados.
5. **AI quality gates:** metas de F1/precision/recall/schema validity/tokens/latência decididas após benchmark, versionadas por dataset e provider; regressão acima de tolerância documentada bloqueia release.
6. **Evidence gates:** resultados de testes reais e simulados identificados separadamente, com versões, comandos, registros e limitações.

A V1 não exige cobertura percentual de código arbitrária; medir cobertura como indicador, priorizando fluxo/riscos. Nenhum teste envia candidatura real automaticamente.
