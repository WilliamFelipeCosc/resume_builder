# Desenvolvimento e convenções

## Monorepo

Usar pnpm Workspaces para React/TypeScript, uv workspaces para Python e justfile para comandos comuns (DECIDED). Comandos, versões, lockfiles e geração do cliente TypeScript foram implementados em M0. Consulte [operação e evidências locais](m0-local-operation.md), `just --list` e `just check`. Redis via Compose é iniciado manualmente. Referências: [operação local](../architecture/local-operations.md) e [contrato REST/OpenAPI](../contracts/rest-openapi.md).

Os manifests e lockfiles estão versionados. Consulte `docs/engineering/m0-toolchain.md`, `package.json`, `pyproject.toml` e o workflow CI para pins e pré-requisitos; a disponibilidade de ferramentas deve ser conferida no ambiente atual. Mudanças documentais não comprovam instalação ou testes de runtime.

## Vertical Slice

Cada incremento entrega uma rota/serviço, UI mínima, persistência e teste de aceitação para um caso de uso. Não construir infraestrutura especulativa do M7 antes de atingir M3. Invariantes mínimos de privacidade/teste entram no M0 e evoluem a cada marco.

## Convenções de versão

Schemas de API/MCP/Dados importados versionados; migrations idempotentes/revisadas; ChangeSets exigem `baseRevisionId`; eventos exigem `idempotencyKey`; adapters de providers e fontes com contratos tipados. APIs externas são dados não confiáveis; validar em runtime.

## Documentação

Mudanças arquiteturais requerem ADR; requisitos mudam apenas com decisão explícita; módulos, contratos, ADRs e notas pertinentes do Obsidian devem ser sincronizados conforme ADR-013 e `docs/process/milestone-status-workflow.md`. Não presumir que CLAUDE.md ou AGENTS.md são autocarregados em todo harness — configurar clientes individualmente.

## Integração contínua

M0 usou checks locais; GitHub Actions foi introduzido em M1, conforme a decisão de kickoff. O workflow em `.github/workflows/check.yml` executa `just check`; sua existência não comprova que uma execução remota específica passou. Consulte as evidências da feature e preserve os Quality Gates.

Testes determinísticos em PR/CI, sem cobrança automática de API nem acesso a contas de recrutamento. AI live eval controlado, com base sintética/consentida e orçamento fixado. Checklist de produção por marco; telemetria cloud opt-in.
