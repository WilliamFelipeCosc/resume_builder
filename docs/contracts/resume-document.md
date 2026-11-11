# Contrato conceitual — ResumeDocument e ResumeRevision

`ResumeDocument` é a única fonte **semântica** do conteúdo do currículo; renderizadores não interpretam diretamente arquivos pessoais ou HTML gerado por IA.

```json
{
  "schemaVersion":"resume-document-v1-draft",
  "id":"resume-demo",
  "profileId":"profile-demo",
  "templateId":"resume-reference-slate-sidebar-v1",
  "styleMode":"visual_reference",
  "sectionOrder":["experience","education","skills","languages"],
  "experienceIds":["experience-demo"],
  "factSelections":[{"factId":"fact-demo","statementIds":["statement-demo"]}],
  "jobSnapshotId":null
}
```

Este objeto ilustra *a intenção* e **não replica exatamente** `resume_document_seed.json` (schema preparatório v0.1). O adaptador deve preservar IDs e ordem originais, aplicando transformações versionadas explícitas.

```json
{"id":"revision-demo","resumeId":"resume-demo","jobSnapshotId":"job-demo","content":{"schemaVersion":"resume-document-v1-draft"},"parentRevisionId":"revision-base"}
```

Uma `ResumeRevision` é snapshot imutável: aplicar ChangeSet cria outra revisão; não alterar uma revisão já exportada. `ResumeDocument` e `ChangeSet` não alteram Career KB confirmada. `ResumeRevision` e PDF validado são ligados a JobSnapshot e às fontes autorizadas.

### Renders e validação

Template visual padrão e ATS alternativo consomem o mesmo documento semântico. Exportar via Playwright Python/Chromium com geração de HTML local; validar texto extraído, ordem de leitura, nomes/contatos conforme policy, transparência de overflow, quebras de página e regressão visual. DOCX/HTML implementados em M6.
