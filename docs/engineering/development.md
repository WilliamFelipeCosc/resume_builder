# Desenvolvimento e convenções

## Monorepo

Usar pnpm + Turborepo (DECIDED); scripts propostos (a criar em M0): `pnpm dev`, `pnpm test`, `pnpm test:e2e`, `pnpm lint`, `pnpm typecheck`, `pnpm infra:up`, `pnpm build`, `pnpm db:migrate`.

## Vertical Slice

Cada incremento entrega uma rota/serviço, UI mínima, persistência e teste de aceitação para um caso de uso. Não construir infraestrutura especulativa do M7 antes de atingir M3. Invariantes mínimos de privacidade/teste entram no M0 e evoluem a cada marco.

## Convenções de versão

Schemas de API/MCP/Dados importados versionados; migrations idempotentes/revisadas; ChangeSets exigem `baseRevisionId`; eventos exigem `idempotencyKey`; adapters de providers e fontes com contratos tipados. APIs externas são dados não confiáveis; validar em runtime.

## Documentação

Mudanças arquiteturais requerem ADR; requisitos mudam apenas com decisão explícita; fonte modular e `PROJECT_SOURCE.md` devem ser sincronizadas. Não presumir que CLAUDE.md ou AGENTS.md são autocarregados em todo harness — configurar clientes individualmente.

## Integração contínua

Testes determinísticos em PR/CI, sem cobrança automática de API nem acesso a contas de recrutamento. AI live eval controlado, com base sintética/consentida e orçamento fixado. Checklist de produção por marco; telemetria cloud opt-in.
