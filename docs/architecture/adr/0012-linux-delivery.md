# ADR-012 — Web primeiro, Tauri V1, instalação manual

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

O projeto usa Linux e serviços externos; instalar/alterar Chrome, Docker ou Hermes silenciosamente seria indesejável.

## Decisão

Web local no início, Tauri desktop + RPM na V1 completa; Compose Redis manual, units systemd user opcionais e `resume-agent doctor` diagnóstico não destrutivo.

## Consequências

Menos automação no instalador, mais documentação; evitar dependências invisíveis e necessidade de root para uso comum.

## Alternativas consideradas

Tauri-first e setup totalmente gerenciado foram descartados.

## Verificação

V1 inicia em Web/Tauri; doctor detecta falhas e não executa instalações.
