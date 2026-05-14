# Phase 1 — Ingest and fact sheet

Loaded at the Phase-1 ingest step. Defines the steps Phase 1 takes
against Linear MCP and the fact-sheet shape Phase 2 reads.

**Status:** the fact-sheet schema below is illustrative. Implementation
plan's first task is to probe the real Linear MCP and pin field names
and types to what the MCP actually returns. The shape is otherwise
stable.

## Steps (order matters)

1. **Resolve scope.** Load `~/.config/linearazor/<group>.toml`.
   Resolve member display names to Linear user identifiers; resolve
   label names to label identifiers. Use Linear MCP read tools.
   Resolution is fresh every run — no cache. Unresolved names go to
   `factSheet.unresolved` for the setup-health footer.

   **Threshold-name translation.** The TOML config uses
   `snake_case` keys (`aging_wip_days`, `silent_days`,
   `no_pr_days`) per TOML convention. Phase 1 translates these to
   the fact sheet's `camelCase` keys
   (`agingWipDays`, `silentDays`, `noPrDays`) per YAML / wire-format
   convention before emitting. Phase 2 always reads the camelCase
   form from the fact sheet — it never sees the TOML keys.
2. **Resolve horizon and lookahead windows.** See
   [horizon-and-scope.md](./horizon-and-scope.md).
3. **Query in-scope issues** for the primary horizon. Composite filter
   from [horizon-and-scope.md](./horizon-and-scope.md) "In-scope set".
4. **Fetch per-issue details** (one MCP call per page; batch as
   permitted): status, status history, assignee, last comment
   timestamp, linked PR URLs, blocker / blocking relations, project,
   milestone, due date, label set, title, body, canonical Linear
   URL. Linear MCP returns the URL alongside the issue (typically
   `https://linear.app/<workspace>/issue/<ID>/<slug>`); record it
   verbatim into the `url` field of every per-issue entry in the
   fact sheet (shipped, openIssues, scopeChangesInWindow,
   lookaheadIssues). Phase 2 renders identifiers as hyperlinks per
   the rendering-mode contract in
   [presentation.md](./presentation.md) — a missing URL falls back
   to a bare identifier, which is the failure mode to avoid.
5. **Compute derived fields** per issue (no MCP calls):
   - `daysInStatus`: now minus the timestamp of the latest status
     transition into the current status.
   - `lastCommentDaysAgo`: now minus last comment timestamp.
   - `bodyHasAcceptanceCriteria`: heuristic match against the
     acceptance-criteria regex set (see "Heuristics" below).
   - `bodyIsEmpty`: `body == null` OR `body.trim() == ""`.
6. **Query project state changes** within the primary horizon —
   milestone date moves, label adds/removes, project state
   transitions. Linear MCP exposes history; query directly.
7. **Compute shipped:** union of (issues completed in the primary
   horizon) plus (PRs merged in the primary horizon linked to in-scope
   issues). Linear tracks linked PRs natively.
8. **Query lookahead set** with the same composite filter against the
   lookahead window. Fetch the narrower projection per spec section
   4.1 step 7.
9. **Compute lookahead-milestone-level fields:**
   `startedIssueCount`, `daysToTarget`,
   `scopeChangedSinceTargetSet`.
10. **Emit fact sheet** as a single YAML document conforming
    to [`../assets/factsheet-template.yaml`](../assets/factsheet-template.yaml).
    YAML is the canonical handoff format — quote-light, comment-friendly,
    and human-reviewable. The fact sheet is documentation as much as it
    is a data structure; Phase 2 reads it as YAML.

## Heuristics (calibrated at implementation time)

### Acceptance-criteria detection

A body has acceptance criteria when any of these match:

- `^(?:#{1,4}\s*)?Acceptance Criteria` (heading-style).
- `^(?:#{1,4}\s*)?Definition of Done` (heading-style).
- A bullet list with two or more lines starting with `[ ]` or `[x]`
  (task-list style) under a heading containing "criteria", "done", or
  "outcome".

Calibrate against the user's workspace samples; the regex set above is
the floor.

### Vague-title set

```text
^(fix bug|phase \d+|update|cleanup|misc|WIP|todo)\b
```

Case-insensitive. Calibrate against the user's workspace at
implementation time.

## Fact-sheet schema

See [`../assets/factsheet-template.yaml`](../assets/factsheet-template.yaml)
for the skeleton. The schema-versioned envelope (`schemaVersion`,
`group`, `horizon`, `lookahead`, `thresholds`, `members`, `unresolved`,
`projects[]`) is stable; per-project field names are pinned at probe
time.

## Stateless contract

Phase 1 reads only from Linear MCP and `~/.config/linearazor/<group>.toml`.
It writes nothing — no cache, no state file, no snapshot. Hard rule 1
(read-only) and hard rule 10 (never re-query Linear from Phase 2)
both depend on this.

## Phase-2 handoff

The fact sheet is the only artifact Phase 2 reads. Pass it as inline
JSON to the analyze step (single-pass) or partition it per project
when dispatching parallel sub-agents (see
[parallel-dispatch.md](./parallel-dispatch.md)).
