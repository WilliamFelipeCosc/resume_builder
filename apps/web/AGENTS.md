# Aplicação Web

Escopo: `apps/web/**`. Comandos partem da raiz do repositório.

- Siga a organização por funcionalidades aprovada em AD-002 de `.specs/STATE.md` e no design M1; componentes genéricos ficam em `src/shared/`. Uma decisão aprovada não comprova que todas as telas já foram implementadas.
- Preserve React/Vite SPA, React Router Data Mode, TanStack Query, React Hook Form, Tailwind/tokens e componentes shadcn/ui conforme aprovação. Editor avançado/drag-and-drop continua uma escolha separada de M6.
- Consuma o SDK OpenAPI gerado em `packages/api-client/`; não duplique DTOs. Alteração necessária de contrato deve começar no Python e ser regenerada.
- Separe estado remoto (Query), rascunho de formulário e estado local de UI. Evite store global sem necessidade/decisão aprovada; conflitos de versão devem preservar o rascunho do usuário.
- Use labels, navegação por teclado, foco e diálogos acessíveis; estados de loading/erro/permissão não podem exibir conteúdo de outro contexto ou sessão.
- Ao trocar/encerrar sessão, impeça reuso de dados privados no cache; não registrar conteúdo pessoal no console ou artefatos de teste.
- Use fixtures fictícias em `apps/web/tests/`. Vitest cobre comportamento de componentes; Playwright Test cobre interface, acessibilidade e fluxos essenciais. Esses testes não autorizam navegador de candidaturas integrado.
- Execute `just check-web` e `just check-browser` quando a interface/fluxo for afetada; o segundo usa as duas configurações Playwright do projeto. Siga os gates específicos da feature e os pré-requisitos de `docs/engineering/m0-local-operation.md`.
