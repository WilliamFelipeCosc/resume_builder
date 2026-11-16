# Verificação independente: PASS com limitações

**Data:** 2026-11-16. Verificador distinto do autor. Escopo: alterações locais ainda não commitadas em `docs/process/`, `docs/roadmap/milestones.md`, `tools/check_milestone_drift.py`, `tests/unit/test_milestone_drift.py` e notas Obsidian M0–M7 e índice. Esta verificação não cobre as alterações preexistentes em `PROJECT_SOURCE.md`, contratos ou ADR-016. A comparação cobre um snapshot, não acesso automático ao vault nem detecção de texto narrativo divergente.

## Evidência por requisito

| Requisito | Resultado | Evidência independente |
| --- | --- | --- |
| HAR-01 | PASS | `docs/process/milestone-status.json:5` a `:13` contém os nove marcos com estado, critérios, evidência e exceções; `tests/unit/test_milestone_drift.py:12` exige o conjunto de IDs e `:24–25` exige critérios e arquivo de evidência. `:22–23` exige SPIKE-17 enquanto a exceção estiver ativa. |
| HAR-02 | PASS | `tests/unit/test_milestone_drift.py:43` exige retorno 0 e `:44` exige mensagem de ausência de divergência para snapshot coincidente. |
| HAR-03 | PASS | `tests/unit/test_milestone_drift.py:57` exige retorno 1; `:58` e `:59` exigem valores divergente e ausente identificados em registro de fixture. |
| HAR-04 | PASS | `tests/unit/test_milestone_drift.py:64` exige retorno 2 para arquivo ausente e `:67–68` exigem retorno 2 e mensagem para JSON inválido. O checker é offline; indisponibilidade do vault é detectada durante a coleta, não pelo checker. |
| HAR-05 | PASS | `tests/unit/test_milestone_drift.py:45` compara bytes do snapshot; `tools/check_milestone_drift.py:15–16` apenas lê arquivos e `:42–47` imprime resultados. Nenhum cliente Obsidian é chamado. |
| HAR-06 | PASS | `docs/process/slice-reconciliation.md:7–37` contém 31 IDs e seus ACs, incluindo avisos M1/M2 e stack M7. Comparei os IDs com as headings das oito notas pelo Obsidian MCP. Mapeamento futuro é planejamento, não prova de implementação. |
| HAR-07 | PASS | Li índice e nota M0 pelo Obsidian MCP: ambos registram M0.5 aceito com exceção; a nota M0 aponta para validação e exceção SPIKE-17, sem alegar tempo comprovado. |
| HAR-08 | PASS | Li notas M1/M2 pelo Obsidian MCP: M1 identifica staging privado, revisão e AC-M1-002/003; M2 identifica visual padrão e ATS, AC-M2-001/002/003. |
| HAR-09 | PASS | `docs/process/milestone-effort-template.md:5–15` inclui intervalos ativos, espera, intervenções, gates, achados, retrabalho e custos com `unknown`. |
| HAR-10 | PASS | `docs/process/milestone-status-workflow.md:17` mantém verificação independente, testes e gates de segurança. A execução do piloto M1 não foi autorizada nem avaliada. |

## Comandos e sensor

- `.venv/bin/pytest tests/unit/test_milestone_drift.py -q`: **4 passed**.
- `.venv/bin/ruff format --check tools/check_milestone_drift.py tests/unit/test_milestone_drift.py`: **2 files already formatted**. A primeira execução, anterior à correção do autor, falhou para ambos os arquivos; a execução posterior passou.
- `git diff --check`: PASS para as alterações rastreadas existentes no momento da execução.
- `python3 tools/check_milestone_drift.py /tmp/resume-builder-obsidian-status.json`: 0, sem divergência nos metadados coletados; li separadamente os nove arquivos do vault e conferi os objetos de status.
- Sensor em diretório temporário: substituir a comparação de divergência por condição falsa causou falha do teste correspondente; substituir a saída 2 de entrada inválida por 0 causou falha do teste correspondente. **2/2 mutações detectadas**. O sensor não alterou o código real e demonstra apenas esses dois comportamentos.

## Limitações

O snapshot foi produzido pela coleta manual via MCP; não é prova contínua de sincronia e o comando não confere corpos de notas. A ressalva sobre valores de estado fixados foi corrigida: `tests/unit/test_milestone_drift.py:49–56` fornece registro de fixture ao teste de divergência, sem exigir os valores históricos do registro real. Não executei `just check` completo, nem testes M1; nenhuma alegação de conclusão do produto decorre deste parecer. As alterações estavam sem commit quando verificadas.
