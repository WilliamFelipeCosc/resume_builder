# Roadmap V1 — Vertical Slices aceleradas até M3

**DECIDED:** Priorizar ao máximo a conclusão de **M3**. Itens adiados dos primeiros marcos retornam em M6/M7 e são obrigatórios para V1 completa. Preferir redução de escopo secundário, **não** de segurança crítica ou validade das informações.

## M0 — Foundation mínima

**Objetivo:** ambiente executável, dados e processamento mínimos. Entregas: pnpm/Turborepo; React/Vite; NestJS; Worker BullMQ; SQLite/Drizzle + migrations; Redis Compose; contratos base; policy mínima; logs e testes. Não implementar dashboards avançados, todos os módulos, RabbitMQ ou Tauri.

**Saída verificável:** API health, web responde, migration rodou, Worker processa job de teste, política impede uma requisição não autorizada.

## M0.5 — MCP feasibility spike

**Objetivo:** eliminar cedo o maior risco técnico. Entregas: MCP `stdio` mínimo, `get_application_context` fake, `report_application_progress` fake/persistido, dados sintéticos, testes com Hermes e outra CLI. Formulário simulado preenchido pelo **agente externo**.

**Saída:** registro reproduzível de versão de clientes, tool calls e relatório; nenhum browser integrado; eventuais limitações documentadas. Se fracassar em cliente específico, documentar e testar alternativa sem redesenhar a aplicação inteira.

## M1 — Career KB Core

**Objetivo:** verdade profissional mínima para M3. CRUD Experience/Project/Achievement/Skill/Evidence, vínculos, revisão de fatos e privacy. Captura manual primeiro; importação sofisticada não bloqueia M3.

**Saída:** perfil fictício e perfil fornecido pelo usuário podem ser cadastrados, editados e consultados com fontes/IDs.

## M2 — Resume Builder Core

**Objetivo:** criar documento utilizável com o menor editor possível. Documento estruturado, formulário, template ATS, preview, snapshot/revisão, PDF extraível e linkage à KB.

**Saída:** PDF válido gerado de dados confirmados; fluxo sem drag/drop e chat completo.

## **M3 — Job Intelligence + Tailoring (PRIORIDADE PRINCIPAL)**

**Objetivo:** primeiro fluxo de valor end-to-end.

1. Importar vaga por URL quando acessível; oferecer fallback manual e screenshot com provider vision se disponível.
2. Preservar snapshot/descrição e extrair requisitos com incertezas explícitas.
3. Fazer matching explicável por requisito com evidência autorizada; SQL/FTS inicial é suficiente.
4. Gerar ChangeSet de currículo adaptado com IA (ou fixture mock no CI); validar fundamentação e permitir aprovar/rejeitar.
5. Persistir revisão do currículo e exportar PDF validado, vinculado a JobSnapshot.

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

Backups automáticos locais/restore; segurança e auditoria finais; Pino/OTel/Jaeger e Sentry opt-in; testes AI Evals, MCP HTTP/stdIO, agentes reais, recuperação; Tauri/RPM, documentação e `doctor`; release e baseline.

**Saída:** V1 completa somente após aprovação da suíte de critérios de aceitação; testes e privacidade não começam apenas no M7.

## Gestão de escopo

Não antecipar: descoberta de vagas, tracking automatizado, approval workflow MCP, RAG avançado, RabbitMQ obrigatório, browser integrado. Todo desvio ao caminho crítico M3 exige justificativa de risco/valor e atualização de ADR/roadmap.
