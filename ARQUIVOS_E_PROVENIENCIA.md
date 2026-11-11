# Auditoria de arquivos e proveniência do pacote

**Autoridade da especificação:** cópia exata do `PROJECT_SOURCE.md` aprovado em 2026-11-11.

## Arquivos existentes aproveitados e migrados

| Origem acessível | Destino | Alteração |
|---|---|---|
| Biblioteca anterior `AGENTS.md` | `AGENTS.md` | Preservadas regras, atualizada stack Python e regras de seed/template |
| Biblioteca anterior `milestones.md` | `docs/roadmap/milestones.md` | NestJS→FastAPI, BullMQ→Dramatiq, Drizzle→SQLAlchemy, M1/M2/M3 ampliados |
| Biblioteca anterior `acceptance-criteria.md` | `docs/roadmap/acceptance-criteria.md` | Mantidos AC originais, adicionados ACs de importação e PDF; ferramentas de teste migradas |
| Biblioteca anterior `mcp-tools.md` | `docs/contracts/mcp-tools.md` | Preservado catálogo/semântica, contextualizado SDK Python |
| Arquivos preparados a partir de `Curriculo.pdf` | `assets/` e `private/` | CSS e spec preservados, notas revisadas para FastAPI |

## Documentos redigidos a partir de `PROJECT_SOURCE.md`

`README.md`, `docs/README.md`, `docs/architecture/*`, `docs/architecture/adr/ADR-001...015.md`, `docs/modules/*`, `docs/contracts/*` (exceto MCP previamente acessível), `docs/decisions/open-decisions.md`, `docs/references.md`, `assets/resume-templates/ats-linear-v1/*`. Esses docs são **elaborações alinhadas à especificação**, não recuperação literal de versões anteriores não disponíveis e não significam código implementado.

## Arquivos futuros não forjados

`uv.lock`, `pnpm-lock.yaml`, `pyproject.toml`/`justfile` de produção, repositório do aplicativo, código de backend e cliente OpenAPI gerado: **não existem neste pacote**. Exemplos de configuração em `docs/implementation-scaffolds/` e explicação de por que não se criou lockfile falso. Os contratos estão documentados como drafts, não implementados.

## Privacidade

O ZIP completo contém dados pessoais em `private/` porque a solicitação foi enviar todos os materiais de referência. **Excluir `private/` antes de publicar/compartilhar/repositório**. Nenhum arquivo de fonte (.ttf/.otf/.woff) é distribuído.
