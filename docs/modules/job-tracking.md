# Application Tracking

## V1 — básico (DECIDED)

Vaga e snapshot associado; currículo e revisão usados; respostas aprovadas; status recrutamento manual (`saved`, `applied`, `screening`, `interview`, `offer`, `rejected`, `withdrawn` etc.); datas, anotações e links.

Agentes externos podem **relatar** progresso, campos pendentes, falha, ação desconhecida e envio. Guardar relatos em histórico, com origem explícita e prova opcional; status só confirmado por usuário ou evidência independente sob regra de verificação.

**Não** implementar notificações, follow-ups e atualização automática de etapas externas na V1. Worker pode registrar eventos operacionais internos; não é executor navegador.

## V2 — deferred

Lembretes, notificações locais, integrações e-mail/calendário quando autorizadas, alterações sugeridas a partir de comunicações e analytics mais elaborados. Workflow de aprovação entre app e agentes MCP é requisito distinto de tracking, também V2.
