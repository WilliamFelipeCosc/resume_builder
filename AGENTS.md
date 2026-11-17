# AGENTS.md — Instruções para agentes de programação

## Missão

Implementar um **Resume Builder local-first** que cria currículos fundamentados em evidências da Career Knowledge Base, analisa vagas e oferece um **servidor MCP** para agentes CLI externos preencherem candidaturas. Priorizar a primeira entrega utilizável **M3** sem retirar requisitos da V1 completa.

## Ordem de leitura

1. `PROJECT_OVERVIEW.md` para orientação; este resumo não substitui requisitos aprovados.
2. Antes de editar, leia os `AGENTS.md` locais aplicáveis, da raiz até cada diretório afetado; não presuma que o cliente carregou todos os descendentes automaticamente.
3. Consulte apenas os requisitos, módulos, contratos e ADRs relevantes à tarefa em `docs/product/requirements.md`, `docs/modules/`, `docs/contracts/` e `docs/architecture/adr/`.
4. Para implementação/retomada, leia `.specs/STATE.md` e os documentos atuais da feature em `.specs/features/`; reutilize decisões aprovadas. Para marcos/aceite, consulte `docs/roadmap/` e `docs/process/milestone-status.json`.
5. `docs/decisions/open-decisions.md` contém escolhas abertas, não autorização. A precedência documental e a distinção entre requisitos, estado e evidências estão em `docs/README.md` e ADR-013.

## Mapa e escopo das instruções

| Diretório | Responsabilidade |
|---|---|
| `backend/core/` | domínio, serviços, autorização e persistência compartilháveis |
| `backend/api/`, `backend/worker/`, `backend/mcp_server/` | adapters HTTP, jobs e MCP |
| `backend/migrations/` | migrações do banco da aplicação; o spike MCP tem migrações isoladas |
| `apps/web/` | aplicação React/Vite e seus testes de interface |
| `packages/api-client/` | OpenAPI e cliente TypeScript gerados |
| `tests/` | testes Python; não herda instruções de `backend/` |
| `docs/`, `.specs/` | especificações/decisões e planos/evidências de execução |

As instruções locais especializam convenções da área; preserve as invariantes globais. Mudanças que atravessam áreas exigem consultar cada guia e seus testes relacionados. Crie novos guias somente quando houver regras próprias, evitando duplicar esta raiz.

## Navegação e análise de código

Em tarefas que exijam entender ou alterar código, use **CodeGraph e os LSP do Serena** conforme o tipo de pergunta, sempre que estiverem disponíveis e aplicáveis:

- **CodeGraph primeiro** para descobrir símbolos, entender como uma funcionalidade funciona, rastrear chamadas e dependências ou avaliar o impacto de uma mudança. Em repositório indexado (`.codegraph/`), consulte-o antes de buscas textuais ou leitura de código para essas questões. Use `codegraph_explore` ou `codegraph explore`.
- **Serena/LSP** para navegação semântica em símbolos identificados: definição, implementações, referências, tipos, diagnósticos e operações de refatoração suportadas. Antes de usar o Serena em uma tarefa de código, leia suas instruções iniciais. Use os LSPs configurados para Python e TypeScript e limite a consulta aos arquivos ou símbolos pertinentes.
- **Combine os dois** ao avaliar referências e impacto de alterações, sobretudo entre pacotes e através de reexports. Resultados vazios ou pequenos do LSP não provam ausência de usos: confirme com CodeGraph e `rg` antes de renomear, remover ou concluir que não há consumidores. O índice também pode estar incompleto ou desatualizado; confira o código atual quando necessário.
- **`rg`** é apropriado para texto literal, mensagens, chaves e confirmação de ocorrências; use ferramentas estruturais quando o padrão exigir análise sintática. Não substitua testes ou revisão por resultados de navegação.
- Se uma ferramenta ou servidor estiver indisponível, não indexado ou falhar, registre a limitação e use as alternativas disponíveis; não crie índice, instale dependências ou altere permissões automaticamente. Consulte `docs/engineering/serena-local.md` para configuração e limitações observadas.

## Regras invariantes

- **Nunca** inventar experiência, certificação, remuneração, autorização de trabalho ou outras qualificações de uma pessoa. Textos gerados são propostas até revisão quando necessária.
- Não transformar outputs de IA em fatos canônicos da Career KB sem aprovação do usuário.
- Não expor dados confidenciais/secretos por padrão. Aplicar política antes da recuperação e antes de enviar contexto a providers ou MCP.
- **Não construir nem reintroduzir controle de navegador de candidaturas integrado** (Playwright/Hermes como executor no backend, CDP orquestrado pela aplicação ou capturas internas de Chrome). Esse navegador pertence ao agente CLI externo. São permitidos Playwright Test para testar a interface, Playwright Python/Chromium para renderizar/exportar PDF do HTML local (ADR-015) e validação controlada do agente externo em formulários fictícios; nenhum deles autoriza um executor de candidaturas na aplicação.
- Não criar ferramentas MCP genéricas de shell, SQL, filesystem indiscriminado, gestão de credenciais ou `submit_application`.
- No MCP V1, registrar relatos de progresso/resultados **sem inferir confirmação de submissão**; aprovação remota formal via MCP pertence à V2.
- Não exigir RabbitMQ, Grafana/Loki/Tempo, descoberta automatizada de vagas ou workflow MCP de aprovações na V1.
- Não criar fallback automático de Hermes para OpenAI API paga. A escolha de provider deve ser explícita.
- Não adicionar bibliotecas ou dependências por preferência pessoal quando existirem escolhas `OPEN` — faça um pequeno ADR/proposta com tradeoffs.

## Fluxo de trabalho por tarefa

1. Identifique REQs e ACs relacionados, escopo de marco e riscos de privacidade.
2. Faça a menor mudança funcional end-to-end (Vertical Slice), usando contratos e adapters.
3. Adicione testes unitários/integração/E2E e testes negativos de autorização conforme aplicável.
4. Rode checks definidos no projeto; se scripts ainda não existirem, **não finja que foram executados**.
5. Forneça evidências verificáveis: comandos, status, fixtures, arquivos alterados e limitações.
6. Atualize documentação e ADR quando a mudança afetar comportamento ou arquitetura.
7. Mantenha sempre a documentação do Obsidian sincronizada com mudanças de documentação, decisões e progresso no repositório, seguindo `docs/process/milestone-status-workflow.md` e preservando as fontes canônicas; se o vault estiver indisponível, registre a sincronização como pendente, sem declarar sincronia verificada.

## Verificação

Comandos executados da raiz, com dependências já instaladas. Os gates específicos da feature continuam obrigatórios; use verificações focais durante o trabalho e o gate integral exigido antes de concluir a integração.

| Mudança | Comandos |
|---|---|
| Python | `just check-python`, `just lint` |
| Web | `just check-web`, `just check-browser` |
| Contratos HTTP/SDK | `just generate`, `just check-contract` |
| Spike MCP | `just check-mcp-spike` |
| Gate integral | `just check` |
| Somente documentação | conferir links/caminhos, manifesto quando afetado e `git diff --check` |

Preserve `uv.lock` e `pnpm-lock.yaml`; use `uv sync --all-packages --locked` e `pnpm install --frozen-lockfile` quando a instalação estiver autorizada. Pré-requisitos operacionais: `docs/engineering/m0-local-operation.md`. Não instalar dependências de sistema automaticamente nem apresentar checks não executados como aprovados.

## Estilo arquitetural

- Monorepo com pnpm workspaces (frontend), uv workspaces (Python) e justfile; React/Vite; FastAPI; worker Dramatiq/Redis; SQLite/SQLAlchemy 2/Alembic. Tauri é entrega de V1 completa.
- Separar domínio, adapters, contratos e infraestrutura. MCP chama Application Services autorizados; não acessa SQLite indiscriminadamente.
- Schemas com validação em runtime, migrations reversíveis/planejadas, idempotency keys para relatos, logs estruturados e operações auditáveis.
- Separar conteúdo semântico do currículo de seus templates e estilo; edições de IA em ChangeSets com diff/aprovação.

## Regras de trabalho para FastAPI e documentos de referência

- Usar modelos Pydantic para fronteiras/DTOs; SQLAlchemy 2 para persistência e Alembic para migrações; gerar cliente TypeScript do OpenAPI e testar compatibilidade; não duplicar DTOs manualmente.
- Python: Pytest (API, domínio, worker, MCP) e structlog JSON. TypeScript: Vitest e Playwright Test. Logs do MCP `stdio` vão para `stderr`, nunca `stdout`.
- Reprodutibilidade: dependências versionadas e lockfiles reais; alterações precisam manter consistência entre os manifests e locks.
- M1: usar `Curriculo.pdf` e seeds em `private/imports/` como dados **privados pendentes de revisão**. Não commitar, divulgar, usar em CI ou confirmar automaticamente. O item `Statement` não é um fato verificado sem aprovação.
- M2: `resume-reference-slate-sidebar-v1` é o visual padrão, com `ats-linear-v1` alternativo. Não confundir o gerador de referência com o renderer definitivo do Resume Studio.
- M3: importar URL, texto ou screenshot, explicitar falhas e lacunas, correlacionar somente fatos autorizados e gerar ChangeSets aprováveis. Sem embeddings ou MCP completo como requisito de M3.
- Não modificar requisitos ou decisões aprovados na documentação modular sem aprovação; registrar divergências em documentação/ADR quando necessário.

## Segurança de testes

- Usar perfis e dados **fictícios** e formulários de teste; não enviar candidaturas reais em CI.
- Garantir que exemplos e fixtures não incluam credenciais ou dados privados reais.
- Testar redaction e permissões MCP; usuários e clientes podem ter níveis distintos de capacidade.

## Atualização de progresso

Ao concluir uma tarefa, informar: marco, REQ/AC cobertos, implementado, testes realmente executados, pendências e riscos. Não anunciar uma release ou integração com agentes externos como concluída antes da validação em seus clientes.

Mantenha contagens de tarefas/testes, branches e autorizações temporárias nos registros de execução. Descrições históricas de ambiente em handoffs não definem permissões atuais: consulte as políticas e ferramentas efetivas da sessão.
