# Harness status and measurement specification

## Problem Statement

Milestone evidence and Obsidian planning notes drift. Effort and verification findings are not consistently measurable.

## Goals

- [ ] Maintain repository-owned milestone status and detect stale Obsidian projections.
- [ ] Provide a measurement template and reconcile the slice notes against approved criteria.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Execute M1 | Separate milestone authorization is required. |
| Automatic vault writes | The owner chose reviewed manual synchronization. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Status authority | Repository | One authoritative projection | yes |
| Vault synchronization | Read-only check and reviewed manual update | Avoid accidental writes | yes |
| Vault input | Explicit JSON snapshot from Obsidian MCP | No direct vault path or credentials required | no |

**Open questions:** none; the snapshot input is a documented implementation assumption.

## User Stories

### P1: Trustworthy milestone status

**User Story**: As an owner, I want status and evidence in the repository and drift reported so that I can trust planning notes.

**Why P1**: Status drift can hide missing acceptance criteria.

**Acceptance Criteria**:

1. The status record SHALL list M0, M0.5 and M1 through M7 with status, acceptance criteria, evidence and exceptions. (HAR-01)
2. WHEN a snapshot matches every milestone status THEN the checker SHALL exit 0 and report no drift. (HAR-02)
3. IF a snapshot has a missing or different milestone status THEN the checker SHALL exit 1 and identify the milestone and values. (HAR-03)
4. IF a snapshot is unavailable or malformed THEN the checker SHALL exit 2 and report that synchronization was not checked. (HAR-04)
5. The checker SHALL never write to Obsidian or change its input. (HAR-05)

**Independent Test**: Compare matching, conflicting, missing and malformed snapshots and confirm unchanged input bytes.

### P2: Reconciled planning and measurement

**User Story**: As an owner, I want current slice notes and a lightweight measurement procedure so future milestones can be reviewed consistently.

**Why P2**: Stale scope and missing effort data compromise planning.

**Acceptance Criteria**:

1. The reconciliation SHALL map all 31 slice IDs to current milestone acceptance criteria and flag stale scope. (HAR-06)
2. The M0.5 Obsidian notes SHALL state acceptance with the documented historical exception. (HAR-07)
3. The M1 and M2 Obsidian notes SHALL identify the current staging and both-template acceptance requirements. (HAR-08)
4. The measurement template SHALL record active intervals, blocked time, intervention, gate retries, verifier findings, rework and available costs with unknowns explicit. (HAR-09)
5. The procedure SHALL preserve independent verification and existing security gates. (HAR-10)

**Independent Test**: Inspect every slice against the source criteria and review the updated notes and template.

## Edge Cases

- IF the snapshot cannot be read THEN the checker SHALL report synchronization was not checked and exit 2. Obsidian availability itself is determined by the operator before creating a snapshot.
- IF a milestone is missing from the snapshot THEN the checker SHALL report drift and exit 1.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| HAR-01 | P1 | Execute | Implementing |
| HAR-02 | P1 | Execute | Implementing |
| HAR-03 | P1 | Execute | Implementing |
| HAR-04 | P1 | Execute | Implementing |
| HAR-05 | P1 | Execute | Implementing |
| HAR-06 | P2 | Execute | Implementing |
| HAR-07 | P2 | Execute | Implementing |
| HAR-08 | P2 | Execute | Implementing |
| HAR-09 | P2 | Execute | Pending |
| HAR-10 | P2 | Execute | Pending |

## Success Criteria

- [ ] Matching and negative drift scenarios produce the specified exit codes.
- [ ] Slice status and scope reconcile with current evidence without claiming M1 execution.
