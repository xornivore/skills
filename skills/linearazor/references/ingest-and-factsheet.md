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
   the configured `labels` against Linear's **project-label**
   namespace via `list_project_labels` (not `list_issue_labels`) —
   see [horizon-and-scope.md](./horizon-and-scope.md) "Label
   resolution" for why. Use Linear MCP read tools. Resolution is
   fresh every run — no cache. Unresolved member names and unresolved
   project-label names both go to `factSheet.unresolved` for the
   setup-health footer.

   **Threshold-name translation.** The TOML config uses
   `snake_case` keys (`aging_wip_days`, `silent_days`,
   `no_pr_days`, `pr_review_days`, `scope_min_issues`) per TOML
   convention. Phase 1 translates these to the fact sheet's
   `camelCase` keys (`agingWipDays`, `silentDays`, `noPrDays`,
   `prReviewDays`, `scopeMinIssues`) per YAML / wire-format
   convention before emitting. Phase 2 always reads the camelCase
   form from the fact sheet — it never sees the TOML keys.
2. **Resolve horizon and lookahead windows.** See
   [horizon-and-scope.md](./horizon-and-scope.md).
3. **Query in-scope issues** for the primary horizon. Order of
   operations:
   1. **Project narrowing.** When `labels` is non-empty, call
      `list_projects --label <id>` once per resolved project-label
      identifier and intersect the returned project-ID sets — the
      candidate set is every project carrying every configured label
      (AND semantics). When `labels` is empty, the candidate set is
      every project under the configured team. When the intersection
      is empty, surface a one-line setup-health note pointing at
      `~/.config/linearazor/<group>.toml`; do not fall back to a
      broader scope.
   2. **Issue narrowing.** Query in-scope issues constrained to the
      candidate projects + team + composite horizon filter from
      [horizon-and-scope.md](./horizon-and-scope.md) "In-scope set".
      Issue labels are not used for scoping (they are recorded in
      `openIssues[].labels` for downstream signals only).
4. **Fetch per-issue details** (one MCP call per page; batch as
   permitted): status, status history, assignee, last comment
   timestamp, linked PRs (URL + `openedAt`), blocker / blocking
   relations, project, milestone, due date, label set, title, body,
   `estimate` (both `value` and `name` when present; null otherwise),
   canonical Linear URL. Linear MCP returns the URL alongside the
   issue (typically `https://linear.app/<workspace>/issue/<ID>/<slug>`);
   record it verbatim into the `url` field of every per-issue entry in
   the fact sheet (shipped, openIssues, scopeChangesInWindow,
   lookaheadIssues). Phase 2 renders identifiers as hyperlinks per
   the rendering-mode contract in
   [presentation.md](./presentation.md) — a missing URL falls back
   to a bare identifier, which is the failure mode to avoid.

   **Linked-PR open date.** Each `linkedPRs[*]` entry carries both
   `url` and `openedAt` (ISO-8601 timestamp). When the MCP response
   doesn't expose `openedAt` for a given PR, set
   `linkedPRs[*].prOpenedAtApproximate = true` and approximate the
   value from the issue's most recent transition into a review-stage
   status. The Awaiting-merge stall detector
   ([signals.md](./signals.md) "Stalls") reads `openedAt` directly;
   when `prOpenedAtApproximate` is true, the same detector falls back
   to `daysInStatus` against the review-stage status.

   **Estimates.** Linear's `estimate` field comes back on `list_issues`
   and `get_issue` responses with `value` (numeric) and `name`
   (display string — `S` / `M` / `L` / `5` / etc.). Either may be null
   when the workspace's estimation scheme omits one of the two
   representations. Record both verbatim per issue.
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
