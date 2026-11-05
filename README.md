# Resume Builder — Especificação do projeto

> Pacote documental de planejamento. **Não é uma implementação funcional.**

## Por onde começar

1. **[PROJECT_SOURCE.md](PROJECT_SOURCE.md)** — documento autocontido para ChatGPT Project, com decisões aprovadas e contexto essencial.
2. **[docs/roadmap/milestones.md](docs/roadmap/milestones.md)** — roadmap em Vertical Slices, acelerado até o **M3**.
3. **[docs/roadmap/acceptance-criteria.md](docs/roadmap/acceptance-criteria.md)** — critérios de aceite e Quality Gates.
4. **[AGENTS.md](AGENTS.md)** — instruções independentes de harness para agentes de programação.
5. **[docs/architecture/overview.md](docs/architecture/overview.md)** e **[docs/contracts/mcp-tools.md](docs/contracts/mcp-tools.md)** — arquitetura e contratos.

## Convenções da documentação

- `DECIDED`: aprovado durante a entrevista; obrigatório no escopo da versão indicada.
- `PROPOSED`: detalhe sugerido, ainda sujeito a validação de implementação.
- `OPEN`: decisão não tomada ou viabilidade ainda não demonstrada.
- `DEFERRED`: explicitamente adiado para V2 ou etapa futura.
- `SPIKE`: experimento de viabilidade; não é garantia de compatibilidade.
- `REQ-...`: requisito rastreável; `AC-...`: critério de aceite; `ADR-...`: decisão arquitetural.

A documentação modular detalha os assuntos; `PROJECT_SOURCE.md` é um **snapshot editorial autocontido** para uso em ChatGPT Project. Ao alterar requisitos, atualize a fonte modular e sincronize o resumo principal na mesma mudança.

## O que não está incluído

Nenhum código executável de backend, frontend ou MCP foi implementado neste pacote. Exemplos de API e estruturas de diretório são contratos e propostas, não interfaces já disponíveis.

## Fontes técnicas

Links de referência e pontos de verificação de versões estão em [docs/references.md](docs/references.md).
