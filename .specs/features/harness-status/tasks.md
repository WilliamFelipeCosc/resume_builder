# Harness status tasks

## Execution Protocol

Use the tlc-spec-driven Execute flow and independent verification. M1 execution is out of scope.

## Test Coverage Matrix

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Status comparison CLI | unit | matching, differing, missing, invalid and read-only snapshots | `tests/unit/test_milestone_drift.py` | `.venv/bin/pytest tests/unit/test_milestone_drift.py -q` |
| Documentation and Obsidian projection | none | manual evidence review against current requirements | `docs/process/`, Obsidian | inspect notes and criteria |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | checker | `.venv/bin/pytest tests/unit/test_milestone_drift.py -q` |
| Build | final | `.venv/bin/ruff check tools/check_milestone_drift.py tests/unit/test_milestone_drift.py` and `.venv/bin/ruff format --check tools/check_milestone_drift.py tests/unit/test_milestone_drift.py` and `git diff --check` |

## Execution Plan

### Phase 1: Status and comparison

T1 → T2

### Phase 2: Reconciliation and measurement

T3 → T4

## Task Breakdown

### T1: Record milestone status

**What**: Record canonical milestone states with criteria and evidence.
**Where**: `docs/process/milestone-status.json`
**Depends on**: None
**Requirement**: HAR-01
**Done when**:
- [x] All nine milestone states and evidence are represented.
**Tests**: none; inspect record and evidence.
**Gate**: Build.

### T2: Compare a read-only vault snapshot

**What**: Compare snapshot metadata and index against the canonical record.
**Where**: `tools/check_milestone_drift.py`
**Depends on**: T1
**Requirement**: HAR-02, HAR-03, HAR-04, HAR-05
**Done when**:
- [x] Matching, differing, missing and invalid snapshots produce specified results without writes.
**Tests**: unit, `tests/unit/test_milestone_drift.py`.
**Gate**: Quick.

### T3: Reconcile slice planning

**What**: Map slices to current criteria and reconcile Obsidian metadata and notes.
**Where**: `docs/process/slice-reconciliation.md`
**Depends on**: T2
**Requirement**: HAR-06, HAR-07, HAR-08
**Done when**:
- [x] All 31 IDs map to current criteria and stale M0.5, M1 and M2 descriptions are corrected.
**Tests**: none; inspect actual Obsidian and criteria.
**Gate**: Build.

### T4: Document measurement and handoff

**What**: Document status synchronization and measurement without changing gates.
**Where**: `docs/process/milestone-status-workflow.md`
**Depends on**: T3
**Requirement**: HAR-09, HAR-10
**Done when**:
- [ ] Workflow and measurement template cover required fields and preserve gates.
**Tests**: none; inspect documentation.
**Gate**: Build.

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | None | Match |
| T2 | T1 | T1 | Match |
| T3 | T2 | T2 | Match |
| T4 | T3 | T3 | Match |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | documentation | none | none | OK |
| T2 | CLI | unit | unit | OK |
| T3 | documentation | none | none | OK |
| T4 | documentation | none | none | OK |
