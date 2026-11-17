# resume-reference-slate-sidebar-v1 — padrão visual

**Decisão:** ADR-015 / `docs/modules/resume-studio.md`. Reproduzir estilo visual de `Curriculo.pdf`: tamanho personalizado 595,92×924 pt, branco na principal, sidebar direita `#99A2B3`, linha do tempo, títulos em caixa alta, corpo Roboto e nome serifado com fallback. É aproximação visual, não cópia pixel-perfect.

## Arquivos

- `resume_template_spec.json`: geometria, cores e diretrizes extraídas do PDF.
- `resume_template.css`: regras da amostra histórica, **não suporta paginação dinâmica arbitrária**.
- `generate_resume.py`: renderer de referência (Python + Playwright Python/Chromium), recebe `career_kb_seed.json` privado e renderiza HTML/PDF. Não usa `ResumeDocument` de produção.

## Uso local de referência

```bash
python assets/resume-templates/resume-reference-slate-sidebar-v1/generate_resume.py \
  --json private/imports/career_kb_seed.json \
  --html /tmp/resume-reference.html \
  --pdf /tmp/resume-reference.pdf
```

Instalar Python/Playwright/Chromium de forma explícita se necessário; o script pode exigir ajustes de paths em ambiente distinto. Não commitar o HTML/PDF gerado: contém dados pessoais.

## Próxima implementação (M2/M3)

Integrar HTML de template à representação `ResumeDocument`, com paginação robusta, contraste/legibilidade, fallback de fontes licenciadas, importação de CSS tokens para preview React e export Playwright Python, além de regressão visual e text extraction. Não reduzir fontes ilimitadamente quando conteúdo crescer; paginação controlada é mandatória.
