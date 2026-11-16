# Estado dos marcos e verificação de divergências

`milestone-status.json` é a fonte canônica de estado dos marcos. A especificação, os critérios e os relatórios de validação continuam sendo a fonte dos requisitos e evidências. Obsidian é uma projeção; sua edição não altera automaticamente o estado canônico. Não marque um marco como aceito apenas porque tarefas foram concluídas ou testes passaram.

Estados: `planned` (não executado), `in_progress`, `implemented` (implementação concluída, sem aceite), `verified` (verificação independente concluída, aceite humano pendente quando exigido), `accepted` e `accepted_with_exception`. Bloqueios e exceções devem constar no registro e apontar para evidência/decisão. Atualize data, critérios, evidências e exceções junto com qualquer mudança de estado. Não presuma que um estado posterior se aplica a outro marco.

## Conferir o Obsidian

1. Via Obsidian MCP, leia `milestone_statuses` do frontmatter do índice `10 Projects/Personal/Resume Builder/Vertical Slices/Vertical Slices.md` e de cada nota `M0.md` até `M7.md` na mesma pasta. M0 contém os dois estados M0 e M0.5. Se qualquer leitura falhar, registre **não conferido**; não gere um snapshot parcial como prova de sincronia.
2. Em arquivo temporário local, crie JSON UTF-8 com `captured_at` (UTC), `index` contendo exatamente o objeto do índice e `milestones` contendo a união dos objetos das oito notas. Confira visualmente IDs duplicados e a origem de cada objeto antes de consolidar. Exemplo: `{"captured_at":"2026-11-16T18:36:54Z","index":{"M0":"accepted"},"milestones":{"M0":"accepted"}}`; o exemplo é parcial e deve gerar divergência.
3. Na raiz do repositório, execute `python3 tools/check_milestone_drift.py /tmp/resume-builder-obsidian-status.json` com o caminho real do snapshot. Saída 0 significa que os estados **no snapshot fornecido** coincidem; 1 informa diferenças ou marcos ausentes/extras; 2 significa que a comparação não foi realizada por entrada ausente/inválida. O comando não acessa Obsidian nem escreve arquivos. Registre a hora da coleta: um snapshot antigo não comprova o estado atual do vault.
4. Revise divergências contra os relatórios e decisões atuais. Corrija o registro canônico se ele estiver errado; depois, atualize as notas afetadas pelo MCP com controle de versão. Recolete todos os metadados e rode novamente o check. A ferramenta confere frontmatter, não o texto dos corpos; confira manualmente afirmações narrativas e gates.

Não é um gate de CI: a disponibilidade do vault não é pressuposta no ambiente de build. Não armazene dados privados nos snapshots. O mapa `slice-reconciliation.md` cobre os IDs e aponta divergências legadas de escopo.

## Medição e piloto

Use `milestone-effort-template.md` a partir da próxima execução autorizada. M1 é o primeiro piloto; registre tempos ativos e espera separadamente, inclusive falhas, reexecuções, achados do verificador e retrabalho. Não calcule tempo ou custo histórico sem fonte. Ao fechar M1, compare a utilidade e o custo do processo antes de propor ajustes para M2. A verificação independente, os testes, os limites de privacidade e os demais gates aprovados continuam vigentes.
