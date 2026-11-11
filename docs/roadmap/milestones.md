# Roadmap V1 — Vertical Slices aceleradas até M3

**DECIDED:** Priorizar ao máximo a conclusão de **M3**. Itens adiados dos primeiros marcos retornam em M6/M7 e são obrigatórios para V1 completa. Preferir redução de escopo secundário, **não** de segurança crítica ou validade das informações.

## M0 — Foundation mínima

**Objetivo:** ambiente executável, dados e processamento mínimos. Entregas: pnpm (web) + uv (Python) + justfile; React/Vite; FastAPI; worker Python Dramatiq/Redis; SQLite/SQLAlchemy 2 + Alembic; contratos Pydantic/OpenAPI; policy mínima, structlog e Pytest/Vitest. Não implementar dashboards avançados, todos os módulos, RabbitMQ ou Tauri.

**Saída verificável:** API health, web responde, migração Alembic aplicou corretamente, Worker Dramatiq processa job de teste, política impede uma requisição não autorizada.

**Detalhamento do kickoff (2026-11-11):** proprietário escolheu diagnóstico sintético completo, recuperação controlada e checks somente locais. [Contexto da entrevista](../../.specs/features/m0-foundation/context.md) e [spec proposta](../../.specs/features/m0-foundation/spec.md) registram o comportamento; implementação ainda não iniciada. Análise adicional de Reactive Resume é opcional posterior, fora do gate M0.

## M0.5 — MCP feasibility spike

**Objetivo:** eliminar cedo o maior risco técnico. Entregas: MCP Python `stdio` mínimo, `get_application_context` fake, `report_application_progress` fake/persistido, dados sintéticos, testes com Hermes e outra CLI. Formulário simulado preenchido pelo **agente externo**.

**Saída:** registro reproduzível de versão de clientes, tool calls e relatório; nenhum browser integrado; eventuais limitações documentadas. Se fracassar em cliente específico, documentar e testar alternativa sem redesenhar a aplicação inteira.

**Alvos escolhidos no kickoff:** Hermes e Codex; compatibilidade ainda não validada. O spike tem execução/gate separado de M0.

## M1 — Career KB Core

**Objetivo:** verdade profissional mínima para M3. CRUD Profile/Experience/Statement/Project/Achievement/Skill/Education/Language/Evidence, vínculos, revisões, proveniência e privacy. Importação inicial do currículo PDF via `career_kb_seed.json` em Staging Area `pending_review`, com revisão manual e nenhuma confirmação automática; importação sofisticada não bloqueia M3.

**Saída:** perfil fictício pode ser cadastrado/testado; dados extraídos do currículo são exibidos como pendentes de revisão e, após aprovação, podem ser consultados com fontes/IDs.

**Decisão de kickoff:** introduzir GitHub Actions em M1, antes do domínio profissional; os checks de M0 são locais e reproduzíveis.

## M2 — Resume Builder Core

**Objetivo:** criar documento utilizável com o menor editor possível. Documento estruturado, formulário, `resume-reference-slate-sidebar-v1` como padrão visual e `ats-linear-v1` alternativo, preview, snapshot/revisão, PDF extraível e linkage à KB.

**Saída:** PDF válido gerado a partir de fatos revisados, ambos os templates selecionáveis, regressão visual e paginação básica validadas; fluxo sem drag/drop e chat completo.

## **M3 — Job Intelligence + Tailoring (PRIORIDADE PRINCIPAL)**

**Objetivo:** primeiro fluxo de valor end-to-end.

1. Importar vaga por URL quando acessível; oferecer fallback manual e screenshot com provider vision se disponível.
2. Preservar snapshot/descrição e extrair requisitos com incertezas explícitas.
3. Fazer matching explicável por requisito com evidência autorizada; SQL/FTS inicial é suficiente.
4. Gerar ChangeSet de currículo adaptado com IA (ou fixture mock no CI); validar fundamentação e permitir aprovar/rejeitar.
5. Persistir revisão do currículo, exportar PDF validado no template selecionado, vinculado a JobSnapshot; nenhum fato pendente vira qualificação confirmada.

**Saída:** usuário conclui fluxo completo com uma vaga de teste e dados válidos sem backend de browser, sem MCP completo e sem embeddings. A especificação exige **todos os três modos de entrada** no M3; fontes inacessíveis falham com fallback claro.

**Qualidade mínima:** privacidade aplicada, diffs com aprovação, export testado, falhas claras, sem afirmações não apoiadas nas fixtures adversariais; ver `AC-M3-*`.

## M4 — MCP V1 completo

**Objetivo:** agentes externos acessam os dados reais do app. `stdio` + HTTP, ferramentas de contexto, evidências, currículos, respostas aprovadas disponíveis, prompts/resources, reportes bidirecionais, auth/ACL/limits, testes de contrato e compatibilidade CLI. `suggest_answer` inicialmente pode chamar serviço IA mínimo; geração sofisticada no M5.

**Saída:** Hermes e outro cliente consultam contexto real **autorizado** e relatam progresso em formulário fictício. Sem fluxo de aprovação MCP.

## M5 — Application Answers & Tracking

**Objetivo:** respostas fundamentadas e histórico. Answer KB, classificação de perguntas, geração com evidência, revisão seletiva, reuso aprovado, tracking manual, eventos reportados com confirmação distinta e idempotência.

**Saída:** preparar dados para formulário, agente externo reporta execução, histórico registra estado relatado sem falsamente marcar envio confirmado.

## M6 — Completar produto funcional V1

Expandir KB ingestion multi-formato/Obsidian/GitHub/export LinkedIn + Staging Area; completar Resume Studio inline/drag-drop/templates/ChangeSets/undo; chat contextual/sugestões por eventos; PDF visual + DOCX/HTML; embeddings e busca híbrida completa, quotas/tokens; refinar Answer Engine.

**Saída:** todas as features funcionais acordadas sem gaps de implementação intencionais.

## M7 — Quality Gates e distribuição

Backups automáticos locais/restore; segurança e auditoria finais; structlog/OTel/Jaeger e Sentry opt-in; testes AI Evals, MCP HTTP/stdIO, agentes reais, recuperação; Tauri/RPM, documentação e `doctor`; release e baseline.

**Saída:** V1 completa somente após aprovação da suíte de critérios de aceitação; testes e privacidade não começam apenas no M7.

## Gestão de escopo

Não antecipar: descoberta de vagas, tracking automatizado, approval workflow MCP, RAG avançado, RabbitMQ obrigatório, browser integrado. Todo desvio ao caminho crítico M3 exige justificativa de risco/valor e atualização de ADR/roadmap.

## Dependências explícitas de execução

- **M0 → M0.5:** dados sintéticos e API/service stub bastam; não depender da KB real.
- **M1 → M2:** fatos aprovados e `ResumeDocument` referencial, sem duplicar conteúdo canônico.
- **M2 → M3:** ChangeSet e revisão com snapshots imutáveis, renderer visual/ATS e extração de texto.
- **Privacidade:** conteúdo do currículo em `private/` é fornecido apenas para uso local autorizado, nunca como fixture de CI.
- **Sem mudança em M4–M7:** migração técnica muda ferramentas, não obrigações funcionais.
