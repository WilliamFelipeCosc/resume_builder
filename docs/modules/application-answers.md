# Application Answer Engine

**Marcos:** M4 disponibiliza consulta/sugestão inicial por MCP; M5 completa respostas e reuso.

## Tipos de perguntas

Factual, técnica, comportamental, preferência e elegibilidade/sensível. O modelo de Answer deve preservar pergunta, texto, idioma, intenção, versão, evidenceIds, status (`suggested`, `approved`, etc.), uso autorizado e referência a application/job.

## Fluxo

1. Receber pergunta no contexto de candidatura e classificar tipo.
2. Recuperar somente fontes e respostas aprovadas compatíveis com a finalidade.
3. Formular proposta com fatos sustentados e assinalar desconhecidos; preferência, elegibilidade e sensíveis exigem resposta/validação humana quando necessário.
4. Mostrar diff/aprovação seletiva; registrar versão aprovada e âmbito de reutilização.
5. MCP pode retornar `approved_answers` e `suggest_answer`, sem workflow formal interativo remoto na V1.

Nunca reutilizar cegamente motivação para uma empresa diferente, dados sensíveis ou salários/autorização de trabalho sem confirmação. Nunca converter sugestões em fatos canônicos. Provider pago exige escolha explícita.

## Aceite

AC-M5-001; CI com perguntas adversariais, desconhecidos e reuso por intenção testados; rastreabilidade e privacy gates obrigatórios.
