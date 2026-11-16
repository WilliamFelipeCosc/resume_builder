# Verificação independente M0.5

## Validation: PASS — aceite com exceção histórica documentada

**Data:** 2026-11-16. **Escopo:** `249e384..93739b6`, incluindo a evidência
Hermes complementar e a decisão do proprietário. Verificador independente
distinto dos autores. As duas falhas de comportamento e as lacunas técnicas do
parecer anterior foram corrigidas. O proprietário aceitou expressamente a
exceção de evidência histórica em `historical-exception.md:3`. O tempo ativo
total da investigação não foi medido: SPIKE-17 permanece historicamente não
comprovado, e a exceção não altera nem dispensa o limite em investigações futuras.

### Resultado das correções

| Item anterior | Evidência reavaliada | Resultado |
| --- | --- | --- |
| Recuperação antes de autorização | `tests/integration/mcp_spike/test_mcp_spike_operations.py:171` e `:174` exigem `fixture.read_text.assert_not_called()` na inicialização e na consulta negada. | PASS |
| Alias Python no wire | `tests/integration/mcp_spike/test_stdio_adapter.py:228` testa ambas as tools; `:235` exige `SCHEMA_INVALID` e `:239` exige banco vazio. | PASS |
| Schema do relato | `tests/integration/mcp_spike/test_stdio_adapter.py:74` e `:80` verificam os quatro campos e seus requisitos no catálogo real. | PASS |
| Frame malformado | `tests/integration/mcp_spike/test_mcp_spike_operations.py:182` envia JSON inválido e inicialização seguinte; `:202–206` exigem ausência de sentinela e resposta válida. `:209–232` observam frames válidos de 4.097 e 65.536 caracteres adicionais; isso não prova um teto máximo do transporte. | PASS |
| Ambiente restrito | `tests/integration/mcp_spike/test_mcp_spike_operations.py:235` mede os perfis e `:258–267` exige os sete nomes permitidos e ausência da sentinela. `live/codex.md:46` registra o teste real Codex. `live/hermes.md:92` registra servidor Hermes recém-nomeado, descoberta e chamadas; a continuidade do PID no instante exato não foi medida e a ausência de outra inicialização é evidência indireta. | PASS, com limite de medição documentado |
| Investigação com limite de 60 min | `live/hermes.md:82` e `live/codex.md:68` registram que o tempo ativo total não foi reconstruído; `historical-exception.md:3` registra a decisão explícita do proprietário. | NÃO COMPROVADO: SPIKE-17; lacuna aceita para este marco |

As evidências anteriormente aceitas para os demais requisitos permanecem na
tabela histórica abaixo. A demonstração de AC-M05-002 inclui a comparação dos
quatro valores e a ausência de envio confirmadas pelo proprietário em
`live/form-demo.md:24`. As duas CLIs consultaram e relataram progresso; o
relato permanece distinto de confirmação de envio. O marco é aceito com a
exceção histórica expressamente documentada, sem afirmar SPIKE-17 comprovado.

### Gates e sensor desta revalidação

- `just check`, com PATH e Chromium de teste especificados no plano: PASS,
  431 testes Python, 17 Vitest, 3 Chromium, typecheck, build, contratos
  OpenAPI/SDK e lint; dois avisos de depreciação do SDK.
- `just check-mcp-spike`: PASS, 177 testes, os mesmos dois avisos.
- `validate_tasks.py`: 0 erros e 0 avisos.
- Sensor em cópia isolada de `git archive HEAD`: cinco mutações detectadas
  em cinco tentativas. Remover as autorizações de leitura e escrita foi
  detectado por `tests/unit/mcp_spike/test_context_service.py:29` e
  `tests/unit/mcp_spike/test_progress_service.py:43`. Retornar recibo novo no
  replay, aceitar evento divergente e não fazer commit foram detectados por
  `tests/integration/mcp_spike/test_repository.py:73`, `:82` e `:63`,
  respectivamente. As mutações foram revertidas na cópia temporária; o
  código da árvore real não foi alterado pelo sensor. A evidência Hermes foi
  produzida em paralelo por outro agente, de modo que o status geral não foi
  comparado byte a byte como prova de isolamento.
- O primeiro gate independente anterior oscilou em um timeout do teste M0 de
  recuperação; teste isolado e gates completos subsequentes passaram. A causa
  dessa oscilação não foi identificada.

**Próximo passo:** registrar o parecer e atualizar a rastreabilidade do marco,
preservando a exceção histórica e o limite para investigações futuras.

---

## Parecer histórico anterior às correções

## Resultado histórico anterior: FAIL

**Escopo:** `249e384..8f092bf`; verificador independente, distinto dos autores.
O preenchimento e a compatibilidade reais foram demonstrados; as lacunas abaixo
impedem aceitar integralmente o desenho de segurança e o contrato de erros.

## Resultados e lacunas priorizadas

1. **Autorização antes de recuperação (alta):** o processo lê a fixture em
   `backend/mcp_server/src/resume_mcp_server/__main__.py:98` logo após carregar o
   perfil, mesmo que este não tenha capacidade de leitura. O teste de serviço
   `tests/unit/mcp_spike/test_context_service.py:29` apenas verifica o loader
   injetado após inicialização e não detecta essa leitura. Probe independente
   `/tmp/rb-verifier-probes/test_eager_fixture.py`: perfil sem capacidades,
   `fixture.read_text.assert_not_called()` falhou, com uma chamada observada.
   Não se observou divulgação de conteúdo nem acesso a dados reais; a divergência
   é o acesso antecipado à fixture sintética. **Correção:** recuperar e validar
   a fixture através do loader somente após `require`, com teste de inicialização
   e requisição negada que verifica ausência de leitura.
2. **Erro para schema inválido (alta):** chamada MCP stdio
   `get_application_context({"application_id":"app-demo"})`, ausente do schema
   publicado, retornou `INTERNAL_ERROR`, não `SCHEMA_INVALID`. Probe
   `/tmp/rb-verifier-probes/test_alias.py:199` falhou ao comparar o código.
   `backend/core/src/resume_core/mcp_spike/contracts.py:26` aceita nomes Python;
   o framework rejeita o argumento posteriormente e
   `backend/mcp_server/src/resume_mcp_server/server.py:70` o mascara como erro
   interno. **Correção:** validar estritamente os nomes de wire e testar ambos
   os métodos pelo transporte, sem executar efeitos de domínio.
3. **Ambiente do subprocesso (alta, evidência ausente):** o desenho exige apenas
   variáveis operacionais e teste real dos mecanismos de cada cliente
   `.specs/features/m05-mcp-feasibility/design.md:248`. O guia em
   `docs/engineering/m05-mcp-operation.md:47` delega a conferência ao operador,
   sem registrar resultado; `live/hermes.md` e `live/codex.md` não provam
   ausência de uma variável sentinela no subprocesso. Não se afirma vazamento
   real. **Correção:** configuração ou launcher com ambiente explicitamente
   limitado e prova em cada CLI real, com sentinela fictícia sem valor secreto.
4. **Frames malformados (média, evidência ausente):** o desenho em
   `.specs/features/m05-mcp-feasibility/design.md:220` exige testar o transporte
   com frames malformados e confirmar os limites efetivos do SDK. Busca nos
   testes MCP por `malform`, `frame`, `framing` e `json-rpc` não encontrou teste
   dessa fronteira. **Correção:** adicionar teste de subprocesso com frames
   malformados, verificar comportamento e sanitização dos streams, documentar
   o limite observado sem prometer limite pré-parse inexistente.

## Requisitos e evidências

| ID | Resultado | Evidência inspecionada e resultado esperado |
| --- | --- | --- |
| SPIKE-01 | Parcial | `tests/integration/mcp_spike/test_stdio_adapter.py:67` compara os dois nomes; `:72` compara os campos da consulta; `live/hermes.md:19` relata listagem real e `live/codex.md:18` chamadas reais. Não há asserção explícita dos campos obrigatórios do schema de relato. |
| SPIKE-02 | PASS | `tests/integration/mcp_spike/test_stdio_adapter.py:79` compara `data` à fixture; `live/hermes.md:27` e `live/codex.md:21` documentam comparação nas duas CLIs. |
| SPIKE-03 | Parcial | `tests/integration/mcp_spike/test_stdio_adapter.py:115` exige `NOT_AUTHORIZED`; leitura antecipada viola a ordenação aprovada, conforme lacuna 1. |
| SPIKE-04 | Parcial | `tests/integration/mcp_spike/test_database.py:35` exige tabela dedicada; `tests/integration/mcp_spike/test_mcp_spike_operations.py:103` rejeita symlinks. Ambiente das CLIs sem segredos não comprovado, lacuna 3. |
| SPIKE-05 | Parcial | `tests/integration/mcp_spike/test_dependency_logging.py:24` verifica stdout e `:26` ausência de sentinela em stderr; não há teste do frame malformado exigido pelo desenho, lacuna 4. |
| SPIKE-06 | PASS | `tests/integration/mcp_spike/test_repository.py:66` compara recibo à linha persistida; `live/hermes.md:31` e `live/codex.md:24` documentam relatos reais. |
| SPIKE-07 | PASS | `tests/integration/mcp_spike/test_repository.py:133` compara recibos e linha entre processos e `:134` exige apenas uma linha. |
| SPIKE-08 | PASS | `tests/integration/mcp_spike/test_repository.py:78` exige mesmo recibo e `:79` mesmo registro; há replay em cada evidência live. |
| SPIKE-09 | PASS | `tests/integration/mcp_spike/test_repository.py:85` exige exceção de conflito e `:88` preserva o original; adapter verifica `CONFLICT` em `test_stdio_adapter.py:131`. |
| SPIKE-10 | PASS | `tests/unit/mcp_spike/test_progress_service.py:43` exige rejeição e `:47` confirma ausência de acesso ao repositório; escopo alternativo em `:77`. |
| SPIKE-11 | PASS | `tests/integration/mcp_spike/test_repository.py:69` exige `reported_by_agent`; `tests/unit/mcp_spike/test_contracts.py:119` rejeita confirmação. |
| SPIKE-12 | PASS | `live/form-demo.md:8` registra prompt sem valores, consulta MCP e browser externo; `:11` registra preenchimento. |
| SPIKE-13 | PASS | `live/form-demo.md:29` registra confirmação humana de ausência de envio; `tests/integration/mcp_spike/test_form_server.py:59` exige HTTP 405 para POST. |
| SPIKE-14 | PASS | `live/form-demo.md:29` registra as quatro comparações humanas separadamente. |
| SPIKE-15 | PASS | `live/form-demo.md:19` identifica recibo persistido `form_filled`, separado da conferência em `:24`. |
| SPIKE-16 | Parcial | Versões, comandos e resultados em `live/hermes.md:6`, `live/codex.md:6` e `live/form-demo.md:6`; não há evidência do ambiente efetivo em cada cliente, lacuna 3. |
| SPIKE-17 | Parcial | Limite documentado em `docs/engineering/m05-mcp-operation.md`; evidências relatam diagnóstico, mas não apresentam tempos de investigação ativa suficientes para verificar a aplicação do limiar. Não se afirma que o limiar foi ultrapassado. |
| SPIKE-18 | PASS | `backend/mcp_server/src/resume_mcp_server/server.py:80` recebe serviços; `tests/unit/mcp_spike/test_context_service.py:20` e `test_progress_service.py:29` testam serviços sem transporte. |
| SPIKE-19 | FAIL | `test_stdio_adapter.py:98` verifica exemplos inválidos; probe de alias em lacuna 2 apresenta código divergente do desenho. |
| SPIKE-20 | PASS | `tests/integration/mcp_spike/test_repository.py:150` injeta falha antes de commit e `:162` exige nenhuma linha; `test_stdio_adapter.py:193` exige erro temporário. |
| SPIKE-21 | PASS | `tests/integration/mcp_spike/test_repository.py:166` usa processos concorrentes, `:178` exige linha única e `:180` recibo idêntico. |

As citações `live/...` nesta tabela referem-se a `.specs/features/m05-mcp-feasibility/live/`.
Os registros live são resumos sanitizados; não foram reexecutadas CLIs nem a
conferência humana na verificação independente.

## Gates

- `just check` com PATH e `PLAYWRIGHT_BROWSERS_PATH` do plano: primeira execução
  falhou em `tests/integration/test_real_recovery.py:182` por timeout aguardando
  worker; 421 passaram. Teste isolado passou (1/1); repetição completa passou:
  422 Python, 17 Vitest, 3 Chromium, typecheck, build, OpenAPI/SDK e lint.
  Falha transitória registrada; não foi provada uma causa.
- `just check-mcp-spike`: 168 passaram; dois avisos de aliases obsoletos no SDK.
- O plano original registra 254 testes Python em M0; após feature, 422.
- Probes independentes: alias inválido e leitura antecipada falharam conforme
  lacunas 1–2. Nenhum skip foi usado para ocultar falhas.
- T1–T20 registradas em commits `89d84e5..8f092bf`; tarefas físicas concluídas,
  mas os critérios e a validação global não estão aprovados.

## Sensor de discriminação

Sete mutações em cópia obtida com `git archive`, usando testes contra fontes em
`/tmp/rb-m05-verifier-scratch`; nenhuma alteração no código real. `git status
--porcelain` antes e depois coincidiu byte a byte. Mutações restauradas na cópia.

| Mutação | Teste que detectou | Resultado |
| --- | --- | --- |
| Remover autorização de leitura | `tests/unit/mcp_spike/test_context_service.py:29` | detectada, 4 falhas |
| Remover autorização de escrita | `tests/unit/mcp_spike/test_progress_service.py:43` | detectada, 4 falhas |
| Retornar recibo novo em replay | `tests/integration/mcp_spike/test_repository.py:73` | detectada |
| Não rejeitar evento divergente | `tests/integration/mcp_spike/test_repository.py:82` | detectada |
| Substituir transação com commit por conexão sem commit | `tests/integration/mcp_spike/test_repository.py:63` | detectada |
| Aceitar confirmação `confirmed` | `tests/unit/mcp_spike/test_contracts.py:119` | detectada |
| Retornar mensagem original no sanitizador | `tests/unit/mcp_spike/test_logging.py:15` | detectada |

**Sensor:** 7/7 detectadas. Uma primeira execução da suíte de repositório na
cópia também encontrou `PermissionError` do sandbox nos testes multiprocesso;
essas falhas ambientais não foram contadas como detecções. As três mutações de
repositório foram repetidas com testes focais, cujas asserções falharam pelo
comportamento mutado.

## Critérios do marco

AC-M05-001: **parcial**, pois as duas CLIs reais demonstraram ferramentas e
replay, mas lacunas 1–4 impedem aceite integral da segurança e do contrato.
AC-M05-002: **evidência funcional observada**; o proprietário confirmou os quatro
campos e a parada sem envio em `live/form-demo.md:29`. A conclusão global M0.5
permanece bloqueada pelas lacunas acima e pela verificação subsequente das correções.

**Próximo passo:** corrigir os itens priorizados, reexecutar os gates e solicitar
nova verificação independente. Não há aprovação implícita para push ou publicação.
