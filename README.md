# Resume Builder — pacote de documentação (2026-11-11)

**Estado:** documentação e artefatos de referência. **Nenhum software foi implementado ou migrado** por este pacote; `PROJECT_SOURCE.md` é a autoridade final das decisões aprovadas.

## Onde começar

1. [PROJECT_SOURCE.md](PROJECT_SOURCE.md) — escopo V1/V2, ADRs, roadmap consolidado.
2. [AGENTS.md](AGENTS.md) — regras para agentes de programação.
3. [docs/roadmap/milestones.md](docs/roadmap/milestones.md) e [acceptance-criteria.md](docs/roadmap/acceptance-criteria.md).
4. [docs/architecture/overview.md](docs/architecture/overview.md) e [ADRs](docs/architecture/adr/).
5. [docs/modules](docs/modules/) e [docs/contracts](docs/contracts/).
6. [docs/decisions/open-decisions.md](docs/decisions/open-decisions.md) e [docs/references.md](docs/references.md).

## Privacidade — leia antes de copiar o pacote

No pacote de origem, `private/` contém PDF original, JSONs com contato e amostras de currículo. Esse diretório não foi importado para este repositório. **Não envie esse diretório ao Git, CI, issues ou provedores externos por padrão**. O `.gitignore` incluído exclui `private/`. Se desejar compartilhar a documentação, distribua apenas os arquivos públicos após inspecionar metadados e nomes. O ZIP completo é destinado a uso pessoal.

`assets/resume-templates/` contém CSS e especificações de estilo, sem os dados do currículo. O arquivo `generate_resume.py` é uma **ferramenta de referência**, não o renderer de produção; sua execução depende de JSON privado. Os artefatos em `private/` são amostras de um documento específico e **não representam dados confirmados no banco**.

## Escopo da entrega

Documentação da stack aprovada (FastAPI + SQLAlchemy 2 + Alembic, Dramatiq/Redis, React/Vite, pnpm/uv/justfile), Career KB, templates, vagas, IA, Answer Engine, MCP, tracking, retrieval, segurança, distribuição, contratos e ADR-001…015.

## Estado deste repositório

Sincronizado com o pacote de 11/11 por decisão do proprietário. O kickoff de M0 está em entrevista; prioridade: chegar rapidamente à construção e exportação do currículo em M3. Veja [decisões e proveniência da sincronização](docs/specification-sync-2026-11-11.md) e [contexto de M0](.specs/features/m0-foundation/context.md). O manifesto público atual é verificável com `sha256sum --check MANIFEST.sha256`; o manifesto de origem de 04/11 está preservado em `docs/history/`.

Os arquivos de documentação modular não disponíveis no contexto anterior foram **redigidos a partir do PROJECT_SOURCE.md**, não recuperados de um repositório implementado. As assinaturas de contratos são conceituais e demandam versionamento e testes antes de implementação.
