# Contratos conceituais — JobPosting, JobSnapshot, JobRequirement e Matching

```json
{
  "jobSnapshotId":"snapshot-demo",
  "jobPostingId":"posting-demo",
  "sourceType":"text",
  "sourceUrl":null,
  "capturedAt":"2026-11-11T12:00:00-03:00",
  "originalText":"Requisito demonstrativo: experiência com React",
  "uncertainties":[]
}
```

`sourceType`: `url|text|image` como input de M3; snapshot bruto e metadados imutáveis. Salvar imagem original privada quando usada; URL bloqueada ou OCR/vision insuficiente resulta em fallback, nunca inventar descrição.

```json
{
  "id":"req-demo",
  "jobSnapshotId":"snapshot-demo",
  "category":"required",
  "text":"Experiência com React",
  "sourceExcerpt":"experiência com React",
  "confidenceNote":"extraído de texto explícito"
}
```

Categorias funcionais: obrigatório, desejável, eliminatório, senioridade, local/remoto, remuneração declarada, contrato, stack. Matching deve trazer `requirementId`, `evidenceIds`, lacunas e raciocínio verificável. **Não** gerar ATS score universal e não confundir keyword overlap com qualificação.
