# Triage heuristics

Phase 1 (triage) is one model pass that produces the structured report consumed by Phase 2 and rendered at the top of user-facing output. Triage is cheap (no per-line review) and always runs first.

## Checks

### CL size scoring

Compute three numbers from the diff:

- `loc_added`: lines added (post-image).
- `loc_removed`: lines removed (pre-image).
- `files_touched`: count of distinct files changed.

Verdict ladder, in order — first match wins:

| Verdict | Threshold |
| --- | --- |
| small | `loc_added + loc_removed` ≤ 100 AND `files_touched` ≤ 5 |
| medium | `loc_added + loc_removed` ≤ 400 AND `files_touched` ≤ 15 |
| large | otherwise |

A `small-cl` finding is filed only when verdict is `medium` or `large`. Severity scales with deviation:

- medium → `optional` severity
- large → `required` severity

Suggestion field cites split strategy from Google `developer/small-cls.html`: stacking, by-files, horizontal, vertical.

### Scope-mix detection

Scan the file map for two patterns:

- **Refactor + feature**: file renames or move-without-modify in the same CL as added or changed callsites elsewhere.
- **Mixed concerns**: changes in two or more orthogonal subsystems (e.g., `pkg/auth/*` AND `pkg/billing/*`).

If detected, file a `small-cl` finding (scope-mix is a small-cls concern per Google) with `severity = optional`, and a `suggestion` that points at "vertical split" from `developer/small-cls.html`.

### CL description quality

Skipped when target is a local diff with no PR. When target is a PR, evaluate PR title + body against Google `developer/cl-descriptions.html`:

| Defect | Evidence | Severity |
| --- | --- | --- |
| First line is not imperative | Title starts with gerund ("Adding…", "Fixing…") or noun ("Improvements to…") | nit |
| First line is an anti-pattern | Matches one of: `Fix bug`, `Fix build`, `Add patch`, `Moving code from A to B`, `Phase 1`, `Add convenience functions`, `kill weird URLs` | required |
| Body missing | PR body is empty or single line | optional |
| Body explains "what" without "why" | No clause that gives the reasoning, motivation, or trade-off | optional |
| Body contains relevant context | Bug numbers, benchmark results, design doc links | (praise candidate) |

### Specialty triggers

Advisory only. Never `required`. Severity is always `fyi`. Detect by path or keyword in the diff:

| Trigger | Patterns |
| --- | --- |
| auth / crypto | paths matching `(auth\|oauth\|crypt\|jwt\|session\|secret)` (case-insensitive) |
| concurrency | added or changed `sync.`, `mutex`, `channel`, `goroutine`, `async`, `await`, `atomic.`, `Lock(`, `Unlock(` |
| public API | changes to exported symbols (capitalized identifiers in Go, exported in package.json/index, etc.) |
| perf-critical | path matches `(hot\|bench\|perf\|cache)` or file annotated `// PERF` |

A specialty finding's `suggestion` names the kind of reviewer to add ("consider a security reviewer for these auth changes").

## Triage emit format

Triage writes one [triage-report-template.md](../assets/triage-report-template.md)-shaped block PLUS one finding-record per non-green verdict (size > small, scope = mixed, description weak, any specialty). The findings get IDs `T-1`, `T-2`, … to distinguish from Phase-2 IDs (`F-1`, `F-2`, …).

## Hard rules

- Triage never re-derives size or scope-mix in Phase 2. Phase 2 reads the triage report.
- Triage never grades any of the ten Google principles other than `small-cl` and `description`. Those are Phase 2's job.
- When triage emits a `large` size finding at `required` severity, Phase 2 still runs. The CL is reviewed; the small-cl finding leads the output.
