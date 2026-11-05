# ADR-007 — Fatos auditáveis e privacidade por padrão

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

Arquivos, dados profissionais e evidências podem conter conteúdo confidencial; IA pode produzir texto persuasivo não fundamentado.

## Decisão

Entidades com proveniência e status de confirmação; staging e aprovação para alterar fatos; importados privados por padrão; filtro de autorização antes de recuperar/enviar contexto.

## Consequências

Mais implementação de policy e revisão, porém reduz alucinação factual e vazamento.

## Alternativas consideradas

Atualização automática da KB por inferência foi rejeitada.

## Verificação

Testes negativos de acesso e conflitos; nenhuma mudança de fato confirmed sem aprovação.
