# Modelo de dados — proposta conceitual para SQLite/SQLAlchemy 2

**Status:** proposta de entidades e relacionamentos, não DDL definitivo. Referências: [Career KB](../modules/career-kb.md), [contratos](../contracts/README.md) e spec/design aprovados da feature; schemas persistidos efetivos ficam nas migrations.

## Fatos profissionais

- `Profile` (1 perfil local inicial): contatos, resumo, preferências profissionais aprovadas; campos sensíveis têm classificação por campo.
- `Experience`: empresa, título original, período, local; pode se relacionar a N `Statement` e N `Skill`.
- `Statement`: unidade atômica de afirmação/responsabilidade/resultado com texto original e versão normalizada, `sourceId`, trecho, página e flag editorial.
- `Project`: pessoal ou ligado a N `Experience`, com links e evidências.
- `Achievement`: resultado associado a projeto/experiência/formação; métricas só se presentes na fonte ou confirmadas.
- `Skill`: termo canônico, grafias/aliases originais, relação de ocorrência e qualidade da evidência; menção ≠ domínio comprovado.
- `Education`, `Language`: declaração histórica, origem e status de confirmação.
- `Evidence`: URI/arquivo/trecho/hash, versão, admissibilidade e escopo autorizado.
- `SourceDocument`: origem, hash, mime, versão, caminho local em XDG, privacidade; nunca tratar como instrução confiável.

Cada fato possui `id`, proveniência, status de confirmação e privacy (`public`, `professional`, `confidential`, `secret`). `pending_review` é um **estado de staging**, não confirmação. Exemplos em `docs/contracts/career-kb.md`.

## Importação e revisão

- `ImportBatch` → `ImportCandidate` (`pending_review`, `approved`, `rejected`, `applied`) + decisão `create|update|link|ignore`.
- `FactRevision` ou registros versionados imutáveis com autor, momento, diff, fonte anterior e nova.
- `AuditEvent`: ações humanas/agents/automáticas, requestId, referência a entidade/versão; eventos de IA não elevam fatos sem confirmação.
- Documento fonte imutável, dedupe por hash e chave idempotente de lote; eventos de undo como compensação auditável.

## Currículo e vagas

- `ResumeDocument`: conteúdo semântico e seleções por IDs, layoutId e preferências de estilo separados.
- `ResumeRevision`: snapshot imutável, parentRevisionId e opcional jobSnapshotId.
- `ChangeSet`: operações tipadas + evidências + decisão parcial/total + estado.
- `JobPosting` 1:N `JobSnapshot` com texto/url/imagem original; N `JobRequirement` com categorias/inferências/certeza.
- `Application`: JobSnapshot, ResumeRevision, status manual, datas, respostas aprovadas, eventos MCP.
- `ApplicationReport`: executionId/idempotencyKey/status relatado, source=`external_agent`, confirmationState separado.
- `Answer`: conteúdo, tipo de pergunta, evidências, aprovação, escopo de reuso.

## Busca e concorrência

FTS5/BM25 em texto permitido por política; preferir consultar registro relacional autoritativo antes de usar ranking. Filtros de privacidade na consulta e na saída. Embeddings híbridos ficam para concluir V1 (M6), sem misturar dimensões/modelos.

Constraints a definir em migrations: FKs ativas, unicidade para idempotency keys em escopo adequado, índices por fonte e status, `CHECK` para enums críticos, migração com backup e validação de restore. Não colocar blobs grandes de PDF diretamente em FTS.
