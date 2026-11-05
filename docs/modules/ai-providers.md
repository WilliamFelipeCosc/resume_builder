# Providers e UX de IA

## Decisões

Abstração multi-provider desde o início; Hermes default quando configurado, OpenAI API alternativa **manual**. Não realizar fallback automático que gere cobrança. Agente Hermes na CLI que executa navegador é **outro papel** e não uma dependência obrigatória da aplicação MCP-first.

## Contratos propostos

`AIProvider.generateStructured(task, schema, permittedContext)`; `VisionProvider.extractImage` quando disponível; `EmbeddingProvider.embed`; `AIResponse` com `provider`, `model`, `promptVersion`, `schemaVersion`, `usage` (se reportado), `output`, `uncertainty`. Tokens reportados e estimados devem ser rotulados separadamente. Acesso por assinatura OAuth/planos de terceiros e suporte a vision requer validação técnica/termos, não pressuposição.

## Interface V1

Ações inline primeiro; chat contextual depois; sugestões por eventos, sem monitoramento contínuo por tecla. Enviar apenas seleção, contexto da vaga e evidências permitidas. Sugestão IA vira ChangeSet e exige validação/revisão apropriada. Histórico de interação vinculado à alteração aplicada e provider quando disponível.

## Segurança e custos

Sem prompts/documentos sensíveis em telemetria; minimização, token budgeting e provider selecionado claramente exibido. Em caso de provider indisponível, mostrar erro e oferecer seleção manual de outro — nunca trocar silenciosamente para endpoint pago. Cache somente de conteúdo permitido, com invalidação por revisão.
