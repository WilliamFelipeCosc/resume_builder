# Job Intelligence

**Marco de prioridade:** M3. **Fonte:** `PROJECT_SOURCE.md` §4.3.

## Entradas obrigatórias

- URL prioritária, com erro observável e fallback quando página for bloqueada ou renderizada dinamicamente; não executar navegador integrado.
- Texto manual colado pelo usuário.
- Screenshot/imagem com provider vision somente quando disponível e autorizado; imagem imperfeita gera lacunas, não suposições.

Persistir `JobPosting` com origem, URL e `JobSnapshot` imutável de texto/imagem, horário e metadados; não substituir snapshot anterior ao reimportar. Conteúdo externo é não confiável e não pode atuar como system prompt.

## Requisitos e matching

Extrair obrigatórios, desejáveis, eliminatórios, senioridade, localização/remoto, remuneração quando declarada, contrato e stack. Cada requisito tem fonte/trecho, categoria e incerteza. Matching por evidências da KB autorizadas (SQL/FTS5/BM25 em M3), com status `supported`, `partial`, `unknown`, `gap` e justificativa rastreável. Esses status são rótulos de UX candidatos, não score universal nem comprovação automática.

## Tailoring

Enviar para `Resume Studio` apenas shortlist de fatos autorizados e requisitos; criar ChangeSet fundamentado, nunca modificar a KB. Dados do staging não confirmados requerem revisão visível, não promoção silenciosa. Vincular JobSnapshot↔ResumeRevision↔PDF; eventual Application pode ser criado/associado no tracking.

## Aceite

AC-M3-001…006: três entradas, erros/fallback, snapshots, requisito→evidências, ChangeSet aprovado, PDF testado e isolamento de dados.
