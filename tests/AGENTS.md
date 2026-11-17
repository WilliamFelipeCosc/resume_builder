# Testes Python

Escopo: `tests/**`. Comandos partem da raiz. Para testes de interface em `apps/web/tests/`, consulte `apps/web/AGENTS.md`.

- Use dados e perfis fictícios; não ler currículos/seeds reais, keyring ou contas pessoais. Nenhum teste envia candidaturas reais.
- Use armazenamento temporário e recursos isolados; testes não migram banco de uso pessoal nem dependem de serviços globais. Consulte os harnesses existentes antes de criar novos.
- Testes de autorização devem provar negação de acesso e ausência de vazamento, inclusive por IDs/escopos cruzados, logs, erros, cache e arquivos quando aplicável.
- Derive casos de REQs/ACs e falhas observáveis: replay/conflito, transação incompleta, revisão concorrente e dados não confiáveis. Evite testes que só repetem detalhes da implementação.
- Mocks de provider/cliente servem ao CI determinístico; execução live exige autorização e relato separado, com versões, comandos e limitações.
- Suites espelham responsabilidades: `unit`, `integration` e `smoke`; casos MCP ficam nos subdiretórios `mcp_spike`. Ao alterar backend, leia também o guia da área correspondente.
- Gate Python: `just check-python`; MCP: `just check-mcp-spike`; estilo: `just lint`. Durante desenvolvimento, execute o subconjunto relevante com `uv run --all-packages --locked pytest <caminho>` e os gates exigidos antes de fechar a tarefa.
- Registre resultados realmente obtidos. Check interrompido/indisponível é inconclusivo, e resultado histórico não comprova a árvore atual.
