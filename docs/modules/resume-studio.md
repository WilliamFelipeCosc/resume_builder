# Resume Studio

**REQ-RES-001..005 — DECIDED.** Currículo é documento estruturado, nunca HTML editado livremente como fonte de verdade.

## Separação

`ResumeDocument` contém seções e referências a Career KB; `Template` define layout; `Presentation` define tokens de estilo, densidade, fontes, seções visíveis e paginação. A renderização React deriva do modelo e não o inverso.

## Entrega M2 mínima

Selecionar informações aprovadas da KB; template ATS de uma coluna; editor por formulário com preview; gerar um PDF e verificar que o texto é extraível, ordenado e referenciado pela revisão exata. Vincular revisão a JobSnapshot quando houver. Não aguardar drag/drop para liberar M3.

## M3

IA propõe alteração textual/estrutural baseada em requisitos e fatos, sem inventar habilidades. Mostrar diff, fontes, impacto de paginação, aprovar/rejeitar, persistir nova `ResumeRevision`, exportar PDF após revisão. O fluxo end-to-end define conclusão de M3.

## V1 completa (M6)

Inline edit controlado, drag-and-drop de seções/experiências/bullets, propriedades visuais, zoom, preview de páginas, templates ATS e visual, CSS override delimitado, undo/redo, ChangeSets parciais, rollback; exportar PDF ATS/visual, DOCX e HTML. Sem executar JS arbitrário de templates na V1.

## IA contextual

Ações inline (reescrever, reduzir, destacar, adaptar à vaga) → chat sobre seleção, revisão e job → sugestões por evento (importação de vaga, gaps, paginação). Toda mutação é `ChangeSet` tipado + diff; o histórico de conversa vincula prompts a propostas sem alterar automaticamente fatos da KB.

## Validações

- Textos em PDF/DOCX extraíveis e ordem coerente com modelo.
- Paginação e quebra de seções inspecionadas; overflow sinalizado.
- Reportar adequação ATS por checks rastreáveis, sem nota universal.
- Export vinculado exatamente a `resumeRevisionId` e `jobSnapshotId` quando aplicável.
- Modificações visuais não mudam a semântica dos dados canônicos.

**Nota:** Playwright é permitido para renderizar/validar documentos e E2E UI, mas proibido no app como executor de preenchimento de vagas.
