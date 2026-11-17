# Planos e evidências

Escopo: `.specs/**`. Comandos partem da raiz.

- Leia `STATE.md` e a spec/design/tasks atuais da feature antes de retomar; reutilize decisões aprovadas e não refaça tarefas concluídas sem evidência de necessidade.
- Preserve IDs de requisitos, aceites e tarefas, relacionando alterações a evidências. Uma tarefa concluída não equivale ao aceite do marco; status de marco é canônico em `docs/process/milestone-status.json`.
- Especifique o que é proposto, aprovado, implementado ou verificado. Registre comandos/exit status, ambiente, dados fictícios, limitações e diferenças entre mocks e testes live.
- Handoffs históricos permanecem identificados por data; acrescente correções/supersessões explícitas. Permissões, branches, modelos e autorizações descritos em snapshots não substituem a sessão atual.
- Não inferir aprovação de fatos privados, compatibilidade CLI ou confirmação de envio a partir de testes/relatos insuficientes. Preserve os gates de revisão/verificação da feature.
- `STATE.md` orienta a retomada, enquanto `execution.md`/`validation.md` guardam evidências detalhadas; evite contagens transitórias nas instruções permanentes.
- Sincronize progresso/decisões pertinentes no Obsidian conforme `docs/process/milestone-status-workflow.md`; registre pendências se não puder conferir.
- Para alterações documentais, valide links, rastreabilidade, manifesto quando afetado e `git diff --check`; não invente resultados de execução.
