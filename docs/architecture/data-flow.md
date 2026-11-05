# Fluxos de dados

## A — Ingestão de Career KB

Fonte local / arquivo / integração aprovada → adapter normaliza e identifica origem → extrator propõe fatos, relações e duplicatas → **Staging Area** → revisão/aceitação do usuário → transação canônica + revisão + evento de auditoria → atualização do índice textual/vetorial autorizada.

## B — M3 acelerado (fluxo prioritário)

URL/texto/screenshot → snapshot original e hash → parser de vaga e requisitos → recuperação autorizada de evidências SQL/FTS → relatório de correspondência/lacunas → IA sugere ChangeSet de currículo → validação de schema e proveniência → revisão pelo usuário → nova ResumeRevision → renderização e validação de PDF → vínculo ao JobSnapshot.

## C — MCP externo

Agente CLI → MCP stdio/HTTP → validação identidade/scope/limites → ApplicationContextService consulta dados autorizados → resposta estruturada com provenance, metadados de truncamento → agente preenche formulário fora do app → agente opcionalmente reporta progresso/resultados → validação e histórico no SQLite → confirmação manual ou independente quando possível.

## D — Resposta por IA

Pergunta+aplicação → `AnswerEngine` verifica respostas aprovadas/KB → filtro de privacidade por task → escolha de provider explícita → output tipado com evidências → detecção de desconhecidos/afirmações não apoiadas → sugestão e revisão apropriada; sem atualizar facts confirmados.

## E — Backup

Suspender writers/reconciliar → snapshot consistente SQLite e inventário de arquivos → manifesto/hash/criptografia opcional → armazenar em destino local → testar restauração em área temporária → ativar de forma controlada. Segredos e Chrome profile não entram no backup padrão.
