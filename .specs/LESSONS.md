# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Test authorization before the first retrieval in the actual process lifecycle, not only in an injected service.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `mcp` · harmful: 0
- features: m05-mcp-feasibility
- evidence: backend/mcp_server/src/resume_mcp_server/__main__.py:98 (mcp)
- last seen: 2026-11-13T02:46:10Z

### L-002 - Test invalid wire aliases through the transport and assert the specified safe error code.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `mcp` · harmful: 0
- features: m05-mcp-feasibility
- evidence: backend/mcp_server/src/resume_mcp_server/server.py:70 (mcp)
- last seen: 2026-11-13T02:46:22Z

### L-003 - Verify subprocess environment isolation with synthetic sentinels for every supported client.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `mcp` · harmful: 0
- features: m05-mcp-feasibility
- evidence: .specs/features/m05-mcp-feasibility/design.md:248 (mcp)
- last seen: 2026-11-13T02:46:26Z

### L-004 - Exercise malformed transport frames in a subprocess and document actual parser limits.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `mcp` · harmful: 0
- features: m05-mcp-feasibility
- evidence: .specs/features/m05-mcp-feasibility/design.md:220 (mcp)
- last seen: 2026-11-13T02:46:31Z

### L-005 - Assert the full published input schema for every exposed tool.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `mcp` · harmful: 0
- features: m05-mcp-feasibility
- evidence: tests/integration/mcp_spike/test_stdio_adapter.py:72 (mcp)
- last seen: 2026-11-13T02:46:35Z

### L-006 - Record active investigation start and end times for each external client compatibility issue.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `mcp` · harmful: 0
- features: m05-mcp-feasibility
- evidence: .specs/features/m05-mcp-feasibility/live/hermes.md:43 (mcp)
- last seen: 2026-11-13T02:46:39Z

### L-007 - Record and investigate intermittent worker startup timeouts observed in integrated checks.
- signal: `gate_fail` · recurrence: 1 feature(s) · scope: `integration` · harmful: 0
- features: m05-mcp-feasibility
- evidence: tests/integration/test_real_recovery.py:182 (integration)
- last seen: 2026-11-13T02:46:45Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
