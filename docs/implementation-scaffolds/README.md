# Exemplos de configuração futuros — NÃO IMPLEMENTADOS

`PROJECT_SOURCE.md` menciona `pyproject.toml`, `uv.lock`, `justfile` e pnpm workspaces como elementos **de implementação M0**, mas o aplicativo não existe nesta entrega. Para não forjar arquivos de runtime nem lockfiles, fornecemos **exemplos** `.example` das configurações e registramos explicitamente que `uv.lock` e `pnpm-lock.yaml` precisam ser gerados por gerenciadores de pacotes quando dependências e versões reais forem selecionadas.

**Não** copiar exemplos como app rodando; adaptar aos packages reais e executar `uv lock`/`pnpm install` somente no momento de M0, após escolhas de versões e avaliação de segurança. `justfile` real deve evitar instalar dependências automaticamente.
