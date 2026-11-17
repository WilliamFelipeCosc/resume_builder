# Contrato conceitual — ChangeSet e revisão de propostas

```json
{
  "id":"changeset-demo",
  "baseRevisionId":"revision-demo",
  "operations":[
    {"operationId":"op-demo","op":"reorder","path":"/experienceIds","value":["exp-2","exp-1"],"evidenceIds":["evidence-demo"],"state":"proposed"}
  ],
  "evidenceIds":["evidence-demo"],
  "state":"proposed"
}
```

`operations` é lista tipada a definir (mínimo candidato: `include_fact|remove_fact|reorder|replace_text|rephrase`). O contrato conceitual aprovado preservado neste documento define `state=proposed|approved|rejected|applied`; o estado por operação precisa suportar aprovação seletiva, sem aceitar automaticamente o conjunto inteiro.

## Invariantes

- Operação tem `baseRevisionId`, `evidenceIds` e precondições para impedir diff contra revisão incorreta.
- Reformulação deve manter significado factual: não elevar senioridade, inventar números, alterar duração/tecnologias ou inferir skills sem fonte.
- Aprovação por operação é registrada com autor e timestamp; rejeição não modifica a revisão; aplicação gera novo snapshot e audita parent.
- ChangeSet pode reorganizar o currículo, não a KB canônica. Sugestões vindas de conteúdo da vaga são texto não confiável.

## Testes

Version conflict, operações malformadas, evidenceIds inexistentes/proibidos, fact pending, rollback/undo e propostas adversariais que tentam inventar competências.
