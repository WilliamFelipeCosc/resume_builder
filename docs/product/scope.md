# Escopo por versão

## Primeiras entregas e M3 acelerado

M0/M0.5/M1/M2 são **mínimos funcionais**, não módulos encerrados. O primeiro fluxo end-to-end esperado em **M3** é: importação (URL, texto ou imagem) → parsing de requisitos → matching com Career KB → IA sugere currículo adaptado → humano revisa → PDF é exportado e vinculado ao snapshot da vaga.

## V1 completa — DECIDED

Career KB relacional com ingestion multi-fonte e Staging Area; Resume Studio completo (inline, drag-drop, ChangeSets, versões e múltiplos formatos); Job Intelligence (URL/texto/screenshot, matching); Answer Engine com respostas fundamentadas; MCP stdio/HTTP bidirecional **para reporte**, sem aprovação remota formal; Job Tracking manual básico; recuperação híbrida embeddings+FTS; testes e Quality Gates; Pino/OTel/Sentry opt-in; backup automático local; web + Tauri/RPM no Linux.

## V2 — DEFERRED

Busca/monitoramento automatizado de vagas; lembretes/notificações e integrações de tracking; approval workflow entre agentes e interface via MCP; pipeline RAG avançado e benchmarks de aprendizado; analytics adicionais e adapters exploratórios.

## Não objetivos

Navegação/browser automation executados pela aplicação; envio de candidatura pelo MCP; integração obrigatória com todo CLI ou site de recrutamento existente; bypass de CAPTCHA, coleta de dados por scraping não autorizado; promessa de infalibilidade da IA.
