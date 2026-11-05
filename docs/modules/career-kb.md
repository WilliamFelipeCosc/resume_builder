# Career Knowledge Base

**REQ-KB-001..004 — DECIDED.** O objetivo é um perfil profissional factual, consultável e rastreável, independente de documentos de currículo.

## Entidades

Experiences (cargos/períodos/responsabilidades); Projects (artefatos, contexto, papel); Achievements (resultados e impactos, métricas quando comprovadas); Skills (competência e evidência de uso); Evidence (trechos, links, documentação e proveniência); SourceDocuments e relações. Evidência pode estar ausente, mas fatos sem comprovação devem ter status explícito.

## Fluxo MVP→V1

**M1 core:** CRUD, links, fontes fornecidas manualmente, privacy e `confirmed/unverified`, atualizações com histórico simples.

**V1 expandida (M6):** importar PDF, DOCX, MD, TXT, JSON, diretórios selecionados, vault Obsidian local, GitHub (repos/docs) e exportação do LinkedIn fornecida pelo usuário. Não fazer scraping não autorizado. Adapter extrai texto; IA propõe fatos e links; dedup/merge e conflito são revisados na Staging Area antes de qualquer commit canônico.

## Regras

- `Extraction confidence` não representa veracidade factual; usar fontes, estados e revisão humana.
- Não substituir fatos confirmados sem aprovação explícita; preservar versão anterior e log.
- Data de experiência não pode ser inferida silenciosamente a partir de texto ambíguo; sinalizar falta.
- Ingestão sensível recebe classificação `private`/`confidential` por padrão até revisão; autorização para sharing não é implícita.
- Documentos originais armazenados em filesystem com hash; relações apontam para versões estáveis.
- Alterações em fatos invalidam/atualizam projeções de documentos e índices, sem reescrever currículos já exportados.

## Acceptance examples

- Importação repetida propõe `link/update/ignore` e não duplica fatos confirmados.
- Conflitos de datas bloqueiam commit sem revisão; associação de Achievement ao Project preserva evidência.
- MCP não lê fonte confidencial sem política que autorize aquela candidatura e task.
