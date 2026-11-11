# Contrato conceitual — Career KB e Staging Area

## `CareerFact` (mínimo DECIDED)

```json
{"id":"fact-demo","provenance":["source-demo#page=1"],"confirmation":"unverified","privacy":"professional"}
```

- `confirmation`: `confirmed|unverified`; status de Staging Area é separado (`pending_review`).
- `privacy`: `public|professional|confidential|secret`; políticas por campo podem ser mais restritivas que a entidade.
- `provenance`: referências a SourceDocument/versão/página/trecho; não somente uma URL opaca.
- `version`/`updatedAt` devem suportar revisão concorrente; estes campos ainda não são finais.

## Entidades e links

`Profile`, `Experience`, `Statement`, `Project`, `Achievement`, `Skill`, `Education`, `Language`, `Evidence`, `SourceDocument`. `Statement` preserva `textOriginal`, `sourceRef`, tipo e entidade de destino; skills de listas e menções mantêm origem distinta. Vínculos many-to-many conforme domínio e integridade referencial.

## Importação proposta

```json
{
  "importBatchId": "batch-demo",
  "sourceDocumentId": "source-demo",
  "status": "pending_review",
  "candidates": [
    {"candidateId":"cand-demo","entityType":"Experience","action":"create","reviewStatus":"pending_review","sourceRef":"source-demo#page=1"}
  ]
}
```

Decisões admitidas: `create`, `update`, `link`, `ignore`. Revisión/commit somente com autorização humana, diff auditável e chave idempotente. Conflitos com fatos confirmados geram candidato de revisão, nunca overwrite.

## Seed real privado

`private/imports/career_kb_seed.json` usa **schema preparatório `career-kb-import-v0.1`**, não o contrato persistido definitivo. É necessário construir adapter de migração/validação para o modelo SQLAlchemy. Os seus dados pessoais não devem ser embutidos em exemplos públicos.

## Regras de teste

Importação idempotente, alteração indevida de fato aprovado bloqueada, PII e `secret` não retornados por pesquisa sem escopo, detecção de ambiguidades e páginas originais recuperáveis.
