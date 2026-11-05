# Application Answer Engine

**REQ-ANS-001 — DECIDED.** Serviço reutilizável pela API/Resume Studio/MCP; não depende da escolha do executor CLI.

## Tipos de pergunta

- Factual: fatos estáveis e verificados, ex. anos de atuação **somente se calculáveis a partir de datas confirmadas**.
- Técnica: conhecimento/experiência atestados por evidência.
- Comportamental: relatos sobre projetos e realizações com fonte.
- Preferência: remuneração pretendida, modalidade, disponibilidade — configurados pelo usuário, não inferidos.
- Elegibilidade/sensível: autorização de trabalho, localização, identidade, questões pessoais — pedir confirmação explícita; não automatizar supostos valores.

## Reuso

Normalizar intenção da pergunta; buscar respostas previamente aprovadas e vínculo com vaga/empresa. Reuso automático apenas quando contexto semântico e fatos forem compatíveis. Não reciclar motivação específica de empresa em outra candidatura sem revisão.

## Geração

1. Consultar fatos autorizados e respostas aprovadas.
2. Se informação insuficiente, retornar `missingInformation`/`requiresReview`.
3. Se provider selecionado estiver disponível, gerar rascunho tipado com `evidenceIds` e estado `suggested`.
4. Validar schema, políticas de privacidade e apoio das afirmações; revisão seletiva para lacunas, ambiguidade, preferências e categorias sensíveis.
5. Não gravar novas respostas como `approved` ou fatos canônicos sem a ação adequada.

MCP V1 pode expor `suggest_answer` **opcional** e `get_approved_answers` para o agente externo, que pode usar modelo próprio. V1 não fornece uma ferramenta de aprovação remota formal; esta integração é V2.
