# Resume Studio

**Marcos:** M2 core, M3 tailoring, M6 editor completo; ADR-015.

## Fonte semântica

`ResumeDocument` identifica o perfil, fatos/Statements selecionados, ordem de seções, layout/template e estilo. Conteúdo, layout e CSS são separados; nenhuma edição de currículo altera silenciosamente `CareerFact` na KB. Uma adaptação gera `ChangeSet` → revisão humana → `ResumeRevision` imutável (com parentRevisionId e opcional jobSnapshotId).

## Templates aprovados

1. **Padrão:** `resume-reference-slate-sidebar-v1`, reproduz composição do `Curriculo.pdf` (595,92 × 924 pt, sidebar à direita `#99A2B3`, linha do tempo, títulos caixa alta, corpo Roboto e nome serifado com fallback legal). Referências em `assets/resume-templates/resume-reference-slate-sidebar-v1/`.
2. **Alternativo:** `ats-linear-v1`, leitura em uma coluna, sem tabelas/ícones essenciais para significado. Não prometer compatibilidade ATS universal.

Ambos usam a **mesma** fonte semântica; a ordem de leitura deve ser validada em PDF extraído, inclusive quando o layout visual tem duas colunas. Ao crescer conteúdo, paginação sem cortes/overlap; não reduzir fonte indefinidamente.

## M2 mínimo utilizável

Formulário para seleção/ordem de Profile, Experience, Statement, Skill, Education, Language, com preview React e exportação Playwright **Python**/Chromium, validando PDF, tamanho, texto extraível e revisões básicas. `private/imports/resume_document_seed.json` é exemplo inicial **pendente de revisão**, não fato confirmado. MVP não exige drag-and-drop nem chat completo.

## M3 adapting to vacancy

- Selecionar template e `JobSnapshot`; recuperar apenas fatos confirmados ou autorizados explicitamente.
- IA sugere operações tipadas em `ChangeSet` (ex.: `reorder`, `replace_text`, `include_fact`, `remove_fact`), com `evidenceIds` por alteração. Nada de métricas inventadas.
- UI mostra texto anterior/novo, justificativa, fonte e lacunas. Aprovar ou rejeitar por operação; aplicar só a operações aprovadas e gerar nova `ResumeRevision`.
- Exportar PDF e vincular a `JobSnapshot` e relatório de validação. Reedições não mudam revisão já exportada.

## M6 — recursos restantes da V1

Editor híbrido de painéis/inline, drag-and-drop de seções/bullets, preview/zoom/paginação, CSS override controlado, undo/redo/rollback, templates adicionais (decisão aberta), DOCX via lib Python validada e HTML estático, chat contextual e sugestões em eventos.

## Ferramenta de referência vs implementação definitiva

`generate_resume.py` foi preparado para reproduzir **um documento específico** lendo `career_kb_seed.json`; não conhece todas as revisões, templates ou paginação dinâmica. Serve apenas para comparar o estilo, sem passar por serviços ou autorização. Na implementação definitiva, o serviço de rendering consome `ResumeDocument` e tokens do template, não a base privada crua.

## Qualidade

AC-M2-001/002/003 e AC-M3-004/005; regressão visual da referência, screenshots sem PII no CI, extração de texto, ordem de leitura, PDF com múltiplas páginas e proteção contra overflow. Se a saída não couber, paginar e registrar warnings.
