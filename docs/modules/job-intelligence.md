# Job Intelligence

**REQ-JOB-001..003 — DECIDED.** Fonte prioritária: URL; fallback texto e screenshot/imagem. Descoberta automática de anúncios é V2.

## Ingestão

- Entrada URL: recuperar conteúdo por meios normais quando acessível, sem exigir controle/browser integrado. Se autenticação/JS/bloqueio impedir extração confiável, oferecer texto ou screenshot em vez de prometer acesso irrestrito.
- Entrada texto: preservar a descrição original.
- Entrada screenshot: provider com visão quando disponível e autorizado; sinalizar baixa legibilidade, conteúdo parcial e ausência de valores.
- `JobPosting` relaciona publicações; `JobSnapshot` congela conteúdo, origem, hash, data, parser/modelo e incertezas.
- Dedupe por URL/IDs e conteúdo com revisão; não assumir que vagas similares de plataformas distintas são idênticas.

## Parsing

Extrair cargo, organização, localização/remote, senioridade, tipo de vínculo, remuneração se expressa, requisitos obrigatórios, desejáveis e eliminatórios, tarefas e tech stack. Não inferir dados não publicados como fatos.

## Matching

Para cada requisito: status `supported`, `partially_supported`, `missing_evidence`, `not_applicable`, `unresolved`; IDs de evidências e explicação; flag de requisitos eliminatórios. Separar grau de relevância da verdade factual; indicar dados desconhecidos sem preencher suposições.

## Critério M3

Import URL/texto/imagem → parser e snapshot → matching explicável → IA sugere currículo adaptado (ChangeSet) → humano revisa → export PDF ligado à vaga. Perfis fictícios e vagas de teste devem cobrir importações com sucesso e fallbacks.
