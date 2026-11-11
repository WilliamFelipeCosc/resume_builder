# uv.lock ainda não gerado

A versão consolidada do `PROJECT_SOURCE.md` prescreve um `uv.lock` para componentes Python. **Não foi gerado**, pois não há um projeto backend implementado nem dependências resolvidas. Um lockfile vazio/fictício daria falsa segurança reprodutível; gerar quando M0 definir `pyproject.toml` e executar `uv lock`. Também ainda não há `pnpm-lock.yaml` real.
