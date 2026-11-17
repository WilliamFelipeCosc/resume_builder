# Career Knowledge Base (KB)

**Marcos:** M1 Core, M6 importadores completos. **Fontes:** [requisitos](../product/requirements.md), ADR-003/007/014 e [spec M1 aprovada](../../.specs/features/m1-career-kb/spec.md).

## Domínio

`Profile`, `Experience`, `Statement`, `Project`, `Achievement`, `Skill`, `Education`, `Language`, `Evidence`, `SourceDocument`. Entidades com IDs, versões, proveniência e classificação de privacidade; relação de muitos-para-muitos onde útil (skill↔experiência/projeto, evidência↔fato). Não copiar descrições para objetos diferentes sem manter referência à fonte.

`Statement` representa cada bullet/declaração e pode ser responsabilidade, atuação, resultado ou texto editorial; versões editadas preservam original. `Skill` separa termo explicitamente listado, menção e competência confirmada. `Education.ongoingAsOfSourceDocument` não implica `currentlyOngoing=true`.

## Fluxo M1 obrigatório

1. Criar `SourceDocument` privado para `Curriculo.pdf`, hash e página/versão.
2. Validar arquivo `private/imports/career_kb_seed.json` como **importação sugerida**, nunca estado final do banco.
3. Normalizar entidades, identificar duplicações por hash e correspondências por IDs/nome/período; preservar texto original.
4. Exibir Staging Area: `pending_review`, decisão `create`, `update`, `link` ou `ignore`, fonte, diff, classificação e evidência.
5. Aplicar revisão individual/lote; registrar quem/como/quando confirmou; commit idempotente, trilha de auditoria e undo.
6. Expor consultas autorizadas para Resume Studio e Job Intelligence; ocultar contatos privados em contextos não autorizados.

Os JSONs extraídos registram 1 perfil, 4 experiências, 12 statements, 2 formações, 3 idiomas, 27 skills/termos (10 explicitamente listados), 1 projeto com rótulo editorial e 2 realizações. Contagens são do seed, não significam fatos confirmados.

## Ambiguidades que não podem ser corrigidas automaticamente

- Experiências com períodos simultâneos; preservar intervalo original.
- Universidade indicada como em andamento na data do PDF; atualidade requer revisão.
- Proficiência em idiomas deve permanecer como declarada até validação.
- `Microsoft Azure` na referência está em contexto de gestão de projetos, não como prova de cloud.
- Website de empresa em quatro dias é descrição textual sem outras métricas; não acrescentar números.
- Título do projeto derivado é **editorial**, não identificador oficial.

## Recursos V1 posteriores (M6)

Adapters para PDF/DOCX/MD/TXT/JSON; diretórios locais selecionados, Obsidian vault local, GitHub repositories/docs e dados exportados do LinkedIn pelo usuário, sem scraping não autorizado. Dedup/merge com Staging Area, import history, rollbacks e policy de origem.

## APIs funcionais (conceituais)

- `POST /api/imports` → lote privado e candidates;
- `GET /api/imports/{id}/candidates`, `POST /api/imports/{id}/decisions` → review/commit;
- `GET/POST/PATCH /api/career/{entity}` → CRUD com versões/escopos;
- `GET /api/evidence/{id}` → dados mínimos autorizados.

Paths não são contratos finais: formalização em `docs/contracts/` e OpenAPI após implementação.

## Testes / aceite

AC-M1-001/002/003; importação repetida não duplica dados; sem PII em CI; `pending_review` não se torna `confirmed` sem ação explícita; proveniência é recuperável no diff.
