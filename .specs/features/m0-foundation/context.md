# M0 — Contexto de kickoff

**Gathered:** 2026-11-11
**Status:** Decisões funcionais, contrato e abordagem de recuperação aprovados; desenho técnico aprovado em 2026-11-11. Execução autorizada em lotes sequenciais; T1–T6 verificadas, fluxo integrado pendente.
**Spec:** [spec.md](spec.md).
**Autoridade:** PROJECT_SOURCE.md e docs/specification-sync-2026-11-11.md.

## Feature Boundary

Foundation executável mínima para o caminho M0 → M0.5 → M1 → M2 → M3. React/Vite, FastAPI, SQLite/SQLAlchemy 2/Alembic, Dramatiq/Redis, contratos Pydantic/OpenAPI e cliente TS gerado, policy, structlog e testes mínimos. Gates herdados: AC-M0-001/002. Não antecipar domínio de currículo, Tauri, embeddings, dashboards ou MCP completo.

## Implementation Decisions

### Objetivo e forma de trabalho

- M3 utilizável rapidamente, com prioridade para construção e exportação do currículo.
- Disponibilidade semanal ilimitada por enquanto; nenhuma data de entrega informada.
- Entrevista guiada: até duas decisões por rodada. Nenhuma nova autorização de agentes ou providers.
- Base documental nova adotada; repo reconciliado com o pacote de 11/11 e a nota de refresh do Obsidian.

### Demonstração de M0

- Botão “Executar diagnóstico de teste”, com dados sintéticos fixos.
- Fluxo Web → API → persistência SQLite → Worker Dramatiq/Redis → resultado persistido → estado/resultado visíveis na Web.
- Nenhum dado profissional ou texto livre necessário nesta demonstração.
- Falhas controladas de Redis e reinício do Worker, com estado visível, retomada segura e sem efeito duplicado.
- Uma execução ativa por vez, botão desabilitado enquanto pendente/em processamento e recuperação do último estado/resultado ao reabrir a Web. Sem histórico navegável em M0; registros anteriores podem permanecer no banco para testes.
- Proposta inicial de contrato aprovada: `id`, `requestId`, `idempotencyKey`, `status` (`pending|queued|running|succeeded|failed`), `attemptCount`, `createdAt`, `updatedAt`, `result` e `error` sanitizado. Tipos, limites e transições serão detalhados na spec; não constitui DDL definitivo.

### Reactive Resume

- Relatório existente preservado como referência opcional posterior.
- Remover AC-M0-003 dos critérios de encerramento de M0 por decisão do proprietário nesta entrevista.

### Acesso e validação

- Web deve abrir já autorizada por um mecanismo local vinculado à sessão Linux, sem pedir credenciais a cada abertura. A API exige autorização; loopback não substitui autenticação.
- Mecanismo concreto ainda sujeito a validação técnica. Se exigir infraestrutura excessiva, propor alternativa ao proprietário antes de implementar; não adotar bypass ou fallback silencioso.
- Checks reproduzíveis apenas locais em M0. GitHub Actions fica para marco posterior; não criar workflow de CI nesta entrega.
- Marco de introdução do CI definido: M1, antes do domínio profissional.
- M0.5 usará Hermes e Codex como alvos. Nenhuma execução ou compatibilidade foi validada; o spike continua separado de M0.
- Abertura autorizada via comando local que abre a Web; URL direta sem sessão válida permanece bloqueada. Não confiar em qualquer request de localhost.
- Diagnósticos sintéticos persistidos em diretório local próprio, isolados por ambiente; bancos de teste temporários. Respeitar XDG para dados da aplicação.
- Logs JSON no terminal, sem arquivo por padrão; limpeza manual explícita. Não antecipar retenção automática, backups ou painel de logs de M7.
- Sessão autorizada válida enquanto a API estiver em execução; reiniciar a API invalida a sessão, e o comando local abre uma nova sem pedir senha. Não guardar credencial permanente no navegador.
- Diagnóstico com prazo total de 120 segundos, até três tentativas do Worker e até 30 segundos por tentativa. Após esgotar prazo/tentativas, falha visível; novo clique intencional cria outra execução, reentregas técnicas não duplicam efeito.

### Ambiente observado (não é matriz de compatibilidade validada)

- Nobara Linux 44 KDE; Python 3.14.8, uv 0.12.7, Node 24.18.0, pnpm 11.28.9, just 1.57.0, Docker 29.8.2, Compose 5.6.0 e SQLite do Python 3.51.2.
- Em 2026-11-11, o proprietário instalou pnpm; disponibilidade confirmada no PATH com `pnpm --version` → `11.28.9`. Dependências do projeto ainda não foram instaladas.
- Versões observadas não são versões selecionadas para o projeto. Compatibilidade e lockfiles serão verificados no momento de implementação; Redis/daemon Docker ainda não foram validados.

## Detalhamento proposto para revisão

- A [spec](spec.md) propõe tipos dos campos, resultado fixo, rotas e códigos de erro, limite de payload e atualização da Web. Essas propostas técnicas não foram aprovadas automaticamente pelas respostas anteriores.
- Design deverá comprovar a viabilidade do mecanismo de abertura local sem credencial recorrente; detalhar bootstrap/cookie/CSRF, portas, mecanismo de posse/reconciliação e dependências/versões, preservando as decisões funcionais.
- Não há necessidade de matriz multiplataforma em M0; o ambiente observado é o ponto inicial, sem alegação de suporte validado.
- Ordem das tarefas e testes será apresentada após revisão da spec e do desenho, mantendo gate separado de M0.5 e M3 prioritário.

## Aprovações de 2026-11-11 — revisão da spec

- Proprietário aprovou UUIDs/UTC, resultado fixo `m0-v1`, rotas de health/diagnóstico, códigos HTTP, limite de 1 KiB e polling/reconciliação de 1 s.
- Aprovado `deliveryWarning` opcional com código estável e mensagem sanitizada para indisponibilidade transitória do Redis; removido na recuperação da entrega. `error` continua exclusivo de falha terminal.
- Aprovado usar o registro do diagnóstico como intenção durável, reconciliador na API e posse temporária por tentativa; sem outbox separada em M0.
- A garantia é efeito persistido único; não é entrega única de mensagens.
- Estas decisões substituem o caráter proposto dos respectivos itens acima. DDL, bootstrap e desenho detalhado aprovados pelo proprietário em 2026-11-11; prova técnica continua obrigatória. O limite de 30 s é de validade da tentativa, sem garantia de interrupção física de código bloqueado. Testes de aplicação NOT_RUN.

## Deferred Ideas

- Análise adicional do Reactive Resume, opcional após M0.
- Currículo e dados profissionais começam em M1/M2, conforme roadmap aprovado.
