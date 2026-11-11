# Referência de análise — Reactive Resume

**Status após decisão do proprietário em 2026-11-11:** referência preservada; aprofundamento opcional posterior, fora dos critérios de encerramento de M0. O antigo AC-M0-003 foi retirado do gate por essa decisão. Nenhuma nova análise do checkout de referência foi executada nesta sincronização.

## Objetivo e limites

Analisar Reactive Resume como referência técnica para M0, extraindo padrões aplicáveis ao Resume Builder sem adotar sua arquitetura ou seu código automaticamente. A análise é somente leitura; o repositório de referência não é dependência, submodule nem parte do build deste projeto.

## Proveniência do snapshot

- Repositório: https://github.com/reactive-resume/reactive-resume
- Checkout analisado: commit `1704ed190725d7fb393bb5b0bf7ddded8c366d95` (branch `main` no momento do clone)
- Clone raso de leitura: `/home/williamf/.hermes/cache/scratch/reactive-resume-reference` (fora deste repositório)
- Fontes examinadas: README e manifests raiz/pacotes; schema de currículo; lógica de propostas e mudanças estruturais; pacote PDF e MCP, com inspeção focada, não auditoria integral.

O checkout não foi executado nem testado. A análise não valida segurança, qualidade operacional ou completude de funcionalidades. Repetir a análise contra um commit atual antes de usar como base para decisões de implementação.

## Observações verificadas no snapshot

- É um monorepo TypeScript com pnpm/Turborepo. O README descreve React/Vite, Hono em Node/Cloudflare, PostgreSQL/Drizzle, REST/MCP, e PDF via Forme; difere deliberadamente da stack aprovada aqui (FastAPI/Python, SQLite/SQLAlchemy 2/Alembic, Dramatiq/Redis).
- O modelo de currículo é um documento estruturado validado por Zod, com conteúdo, seções, layout, tipografia e estilo semântico. Inclui seções padrão e customizadas e normalização/migração de datas (`packages/schema/src/resume/data.ts`).
- O código de propostas separa mudanças textuais e estruturais, mantém before/after, status, localização e referências de evidência; o aceite é explícito e a aplicação verifica se o conteúdo base ainda corresponde (`packages/resume/src/proposals.ts`, `structural-proposals.ts`). A detecção de claims não suportados é apresentada como checagem cautelosa, não como prova.
- O PDF tem pacote dedicado e testes de extração ATS/paginação; o README informa preview e renderização em worker. É uma referência útil para estratégias de validação de exportação, não razão para escolher a mesma biblioteca.
- O MCP fica em pacote próprio e expõe tools, resources e prompts (`packages/mcp/src/`). Isso serve como referência de organização e contratos; não demonstra compatibilidade com os clientes CLI exigidos neste projeto.
- O README lista importações, tracking de candidaturas e recursos de IA, mas a análise de superfície não verifica todas as implementações nem garantias de privacidade.

## Aplicabilidade ao Resume Builder

| Tema | Aproveitar como princípio | Não copiar sem decisão/validação |
|---|---|---|
| Modelo de currículo | Documento semântico estruturado, layouts/estilos separados e schema de runtime | Modelo de dados inteiro: nossa Career KB mantém fatos/evidências canônicos separados do ResumeDocument |
| Mudanças de IA | Propostas explícitas, diff, before/after, revisão e detecção de conteúdo obsoleto | Heurísticas de claims como garantia de verdade; nossas mudanças devem referenciar evidências aprovadas e nunca promover fatos sem aprovação |
| PDF/ATS | Testes de extração de texto, paginação e fixtures | Forme ou qualquer dependência sem spike/ADR e avaliação compatível com Linux/local-first |
| MCP | Pacote/contratos isolados e testes específicos | Superfície ou permissões do projeto; preservar Application Services autorizados e proibições MCP locais |
| Arquitetura | Fronteiras de pacotes e separação de responsabilidades como tópicos para comparação | Hono, PostgreSQL, Cloudflare, identidade pública/compartilhamento e operação multiusuário; não são requisitos aprovados |

## Atividade opcional posterior e critérios de revisão

- Manter este relatório versionado e identificar o commit do snapshot analisado.
- Registrar recomendações em termos dos requisitos/ADRs existentes; qualquer mudança de arquitetura precisa de proposta/ADR e aprovação, sem alteração silenciosa de decisões `DECIDED`.
- Revisar escopo M0/M1/M2/M3 e listar oportunidades, incompatibilidades e riscos pertinentes (schema/proveniência, ChangeSets, PDF/ATS, privacidade e MCP).
- Tratar o clone como referência descartável, fora do build, sem dependência de rede em CI e sem dados pessoais.
- Registrar limitações e fontes de código por caminho/commit. Não declarar equivalência, auditoria completa ou validação funcional.

Este relatório preserva a análise comparativa anterior de escopo limitado. Qualquer proposta futura derivada dela deve ser avaliada/decidida no contexto do slice correspondente antes da implementação. Não altera critérios de aceite funcionais de M0.
