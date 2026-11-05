# Modelo de domínio — esquema conceitual

## Career Knowledge Base

- `Experience(id, organization, role, dateRange, scope, status, privacy, revision)`
- `Project(id, name, summary, links, status, privacy, revision)`
- `Achievement(id, statement, impactMetrics?, verificationStatus, privacy, revision)`
- `Skill(id, name, category, proficiencyEvidence?, verificationStatus)`
- `Evidence(id, sourceDocumentId?, reference, excerpt?, provenance, privacy, verificationStatus)`
- `SourceDocument(id, type, sha256, importMetadata, originalAssetId?, version)`
- Relações explícitas: `experience_project`, `experience_achievement`, `achievement_evidence`, `project_skill`, `skill_evidence` etc. Evitar serializar relações como strings soltas.
- `IngestionBatch`, `StagedProposal(create/update/link/ignore)`, `FactConflict`, `FactRevision`.

## Currículos

- `Resume(id, baseProfileId, templateId)`
- `ResumeRevision(id, resumeId, parentRevisionId?, jobSnapshotId?, structuredDocument, version, createdAt)`
- `ResumeChangeSet(id, baseRevisionId, operations[], evidenceRefs[], state, author)`
- `ResumeExport(id, revisionId, format, type[ats|visual], sha256, fileId, validationReportId)`
- `Template(id, stylesheet, componentSchema, constraints)`.

## Vagas e candidaturas

- `JobPosting(id, canonicalUrl?, sourcePlatform?, dedupKey?)`
- `JobSnapshot(id, postingId, sourceAssetId?, rawText?, parsedFields, extractionUncertainties, capturedAt, hash)`
- `JobRequirement(id, snapshotId, text, kind[required|preferred|disqualifier], evidenceMatchIds)`
- `Application(id, postingId, snapshotId, resumeRevisionId?, recruitmentStatus, createdAt)`
- `ApplicationEvent(id, applicationId, executionId?, eventType, reportingSource, confirmationState, createdAt, payloadSanitized)`
- `ApprovedAnswer(id, questionIntent, content, evidenceRefs, approvalRevision)`
- `AnswerSuggestion(id, applicationId, question, proposedAnswer, provenance, reviewState)`.

## Estado da automação (MCP externo)

- **Não** salvar controle de aba, cookies, DOM e sessão Chrome em `Application`.
- `ExternalExecution(id, applicationId, clientId, startedAt, lastReportedAt, reportedState)` e eventos anexos.
- `reported_submitted` não equivale a `confirmed_by_user` ou `verified_by_evidence`.
- Relatos com `idempotencyKey`, sequence number opcional e timestamps; rejeitar incoerência/duplicação.

## Dados pessoais e segurança

Privacidade por entidade e atributo: `public`, `professional_shareable`, `confidential`, `sensitive_secret`. Armazenar políticas separadamente de conteúdo. Política avaliada **antes da consulta, indexação ou divulgação**. Logs contêm IDs e metadados mínimos, não texto confidencial.

## Estado

Nomes e schemas acima são `PROPOSED`; relações e conceitos de domínio são `DECIDED`. Gerar schemas Drizzle e migrações em Vertical Slices a partir desses invariantes; evitar congelar colunas prematuramente.
