# ADR-001 — Aplicação local-first Linux

**Status:** Accepted | **Escopo:** V1, salvo indicações explícitas de V2

## Contexto

O produto usa arquivos profissionais, perfis privados e integrações com ferramentas de desenvolvimento locais.

## Decisão

Executar API, banco, arquivos, Web e opcionalmente desktop no Linux; acesso local pelo loopback. Providers de IA remotos só após configuração e política de compartilhamento.

## Consequências

Offline para a maioria das operações de dados; inferência pode exigir rede; distribuição e permissões de diretório precisam ser testadas.

## Alternativas consideradas

SaaS cloud e solução totalmente hospedada foram descartadas para a V1.

## Verificação

Verificar que o app inicia sem acesso externo para dados locais e falha claramente quando provider remoto não estiver disponível.
