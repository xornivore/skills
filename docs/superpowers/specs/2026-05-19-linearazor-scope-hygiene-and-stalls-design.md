**Status:** draft
**Author:** xornivore
**Date:** 2026-05-19
**Skill folder:** `skills/linearazor/`
**Branch:** `feat/linearazor-scope-hygiene-and-stalls`
**Extends:** [`2026-05-13-linearazor-design.md`](./2026-05-13-linearazor-design.md), [`2026-05-14-linearazor-lane-grouped-layout-design.md`](./2026-05-14-linearazor-lane-grouped-layout-design.md).

# linearazor — scope hygiene, estimates, and expanded stalls

## 1. Summary

Three additions to the signal layer:

1. **Scope-hygiene stall** — flag in-scope projects whose active cycle has no work tracked yet. Always-on, with framing that softens early in the cycle and hardens late.
2. **Story-point estimates** — surface Linear's `estimate` field as a per-bullet badge and an exec-summary aggregate.
3. **Four new stall patterns** — review-aging, PR-linked-but-stuck, awaiting-merge, reverted.

Phase-1 ingest gains one new per-issue field (`estimate`) and one new per-linked-PR field (`openedAt`). The lane stack, hard rules, mood-line voice, and animation cast are unchanged in shape — the cast adds no creatures; the stalls lane gains one precedence rule for which creature renders when multiple sub-flavors fire.

## 2. Motivation

Three gaps the current brief misses:

- **Empty cycles read as "everything's fine."** When a project has no in-scope issues, the brief simply doesn't render that project in any lane. A team forgetting to track work shows up as silence — indistinguishable from a team having nothing to do. The brief should notice the absence.
- **Weight is invisible.** A 5-point stall and a 1-point stall render identically. Readers infer rough effort from the title; the brief could surface Linear's existing estimate field cheaply.
- **The stall lane only catches one shape of "stuck."** "In Progress for too long" is a single shape. PRs sitting in review, PRs opened but issues still flagged In Progress, completed work being reverted — these are all stuck shapes the lane currently can't see.

## 3. Out of scope

- Cross-run trends (week-over-week velocity, point-burndown). Hard rule 9 still binds — the brief is a snapshot.
- Auto-fixing scope hygiene (creating issues, suggesting backlogs to pull from). The brief surfaces the gap; the team fills it.
- Story-point normalization across teams or workspaces. We render whatever Linear returns — `S`/`M`/`L` stays as such, numbers stay as numbers.
- New creatures in the animation cast. The eleven-creature cast is unchanged; new stall sub-flavors map onto existing creatures.

## 4. Scope-hygiene stall

### 4.1 Detection

Per in-scope project (one stall finding per project, not per issue):

```text
projectInScopeIssueCount(project) < thresholds.scopeMinIssues
```

Fires for every in-scope project that fails the count check, on every full-ritual run. No early-cycle suppression — the framing (see [4.2](#42-render-variants)) carries the softness.

`projectInScopeIssueCount` is the count of issues belonging to the project that pass the composite horizon filter (per [`horizon-and-scope.md`](../../../skills/linearazor/references/horizon-and-scope.md) "In-scope set").

`scopeMinIssues` is a new threshold. Default: `1`. Configurable in `[thresholds]`.

### 4.2 Render variants

Three variants keyed off `elapsed_pct = (today - cycle.startsAt) / cycle.length`. The project sub-header in the stalls lane already names the project, so the rendered bullet body starts directly with the state:

| Position | `elapsed_pct` | Bullet body |
| --- | --- | --- |
| early | ≤ 33% | `no work tracked yet — cycle just started (day N of M)` |
| mid | 33% < x ≤ 66% | `no work tracked — N days in, M days remaining` |
| late | > 66% | `no work tracked — cycle ends in N days` |

When `0 < count < scopeMinIssues` (only possible when the threshold is raised above 1), substitute `1 issue tracked` (or `K issues tracked` for K > 1) for `no work tracked` and otherwise reuse the variant.

### 4.3 Lane placement and creature

Renders under the affected project's sub-header inside the **stalls** lane. The brief still emits the project sub-header even though the project has no items in any other lane — scope hygiene is the reason the project shows up at all in this brief.

The scope-hygiene stall maps to the `stalls_silent` palette role and the turtle creature. Project muteness reads as silence, not as aging.

## 5. Story-point estimates

### 5.1 Ingest

Phase 1 adds one field per issue:

```yaml
estimate:
  value: <integer or null>     # Linear's numeric estimate
  name: <string or null>       # e.g. "S", "M", "L", "5", "8"
```

Linear MCP returns both `estimate.value` and `estimate.name` on `list_issues` and `get_issue` responses already — no extra MCP calls, just record the field.

`estimate` is `null` (both subfields null) when no estimate is set on the issue.

### 5.2 Per-bullet badge

When `estimate.name` is non-null, render `(<name>)` after the ID with one trailing space:

```text
    •  ENG-1522 (L)  In Progress 11 days  (default threshold: 7)
    •  ENG-1278 (S)  finalize scope for runtime backpressure
    •  ENG-1042       no estimate — no badge, no extra space
```

The badge inherits the lane's palette color via the parentheses; the glyph between them is plain text. This is consistent with the rule that identifiers stay plain-bold and only role-bound tokens carry color.

### 5.3 Exec-summary aggregation

The exec summary line in full-ritual mode gains a parenthesized aggregate per lane that has at least one estimate-bearing item:

```text
Across N projects: S shipped (12pt) · T stalls (8pt) · Q questions · C changes
```

Aggregation rule:

- Numeric `estimate.value` is summed across in-lane items.
- Items with non-null `name` but null `value` (T-shirt sizes with no point mapping) are excluded from the aggregate and don't contribute to the `(pt)` total.
- Lanes where every item lacks an estimate render without the `(pt)` suffix.

The unit literal is `pt` regardless of estimate scheme.

### 5.4 Hard rule 9 compatibility

"No scoring, no streaks, no leaderboards" forbids cross-run tallies of bees, shipped, or stalls as metrics. Per-run estimate aggregation is metadata on the current snapshot, not a cross-run comparison. No counter is persisted across runs. Safe.

## 6. Four new stall patterns

Added to the stall-detection table in [`signals.md`](../../../skills/linearazor/references/signals.md), in order of precedence (most-specific first):

| Stall | Detection | Render |
| --- | --- | --- |
| **Reverted** | Status history contains a transition `Done → started-or-unstarted` within the primary horizon window | `<ID>  rolled back from Done <date>` |
| **Blocked-without-blocker** | (existing) | (existing) |
| **Awaiting-merge** | Status name matches the review pattern AND any `linkedPRs[*].openedAt` is older than `pr_review_days` ago | `<ID>  PR open N days, no merge` |
| **Review-aging** | `daysInStatus > pr_review_days` AND status name matches the review pattern | `<ID>  In Review N days  (default threshold: 3)` |
| **PR-linked but stuck** | `daysInStatus("In Progress") > no_pr_days` AND `linkedPRs != []` AND status name does NOT match the review pattern | `<ID>  In Progress N days with PR open — flip status?` |
| **Silent** | (existing) | (existing) |
| **No-PR** | (existing) | (existing) |
| **Aging-WIP** | (existing) | (existing) |

### 6.1 Review pattern

Status name matches the case-insensitive regex:

```text
\b(in[ -]?)?review\b|code[ -]?review
```

Calibrate against the user's workspace status set at implementation time — different workspaces use different review-stage names ("In Review", "Code Review", "PR Review"). The regex above is the floor.

### 6.2 Stall precedence (updated full ordering)

A single issue matches at most one stall finding. Precedence (top-down, first match wins):

1. Reverted
2. Blocked-without-blocker
3. Awaiting-merge
4. Review-aging
5. PR-linked but stuck
6. Silent
7. No-PR
8. Aging-WIP

Plus, at the project level (independent of any issue-level stall), the scope-hygiene stall fires per [section 4](#4-scope-hygiene-stall). Project-level and issue-level stalls coexist within the same lane block for that project.

### 6.3 Phase-1 ingest changes

Per-issue `estimate` (per [section 5.1](#51-ingest)).

Per `linkedPRs[*]`, the existing URL is joined by `openedAt`:

```yaml
linkedPRs:
  - url: "https://github.com/org/repo/pull/123"
    openedAt: "2026-05-14T17:23:00Z"
```

Linear MCP exposes PR metadata on the issue's relations. If `openedAt` isn't reliably available, the Awaiting-merge detector falls back to using `daysInStatus` for the review-stage status — approximate but bounded. Mark the fallback in the fact sheet as `prOpenedAtApproximate: true` per linked PR so the audit can detect the degraded mode.

## 7. New config keys

`assets/config-template.toml` adds two keys under `[thresholds]`:

```toml
[thresholds]
aging_wip_days   = 7
silent_days      = 7
no_pr_days       = 3
pr_review_days   = 3      # NEW
scope_min_issues = 1      # NEW
```

Phase 1 translates these to camelCase (`prReviewDays`, `scopeMinIssues`) in the fact sheet, per the existing snake-to-camel rule.

## 8. Animation cast — stalls lane precedence

The stalls lane carries one creature in the brief. When multiple stall sub-flavors fire, the rendered creature is chosen by precedence — top-down, first non-empty wins:

| Precedence | Sub-flavor | Creature |
| --- | --- | --- |
| 1 | `stalls_blocked` (blocked-without-blocker) | Fish |
| 2 | `stalls_silent` (silent + scope-hygiene) | Turtle |
| 3 | `stalls_no_pr` (no-PR + PR-linked but stuck) | Snail |
| 4 | `stalls_aging` (aging-WIP + review-aging + awaiting-merge + reverted) | Cow |

The new stall sub-flavors map onto existing creatures — no new art, no new palette roles. Spider sub-flavor for `changes_scope` is unchanged.

## 9. Files affected

- `skills/linearazor/references/signals.md` — extend the stall table per [section 6](#6-four-new-stall-patterns); add a "Scope hygiene" subsection inside the stalls lane per [section 4](#4-scope-hygiene-stall).
- `skills/linearazor/references/ingest-and-factsheet.md` — add `estimate` per-issue and `openedAt` per linked PR per [section 5.1](#51-ingest) and [section 6.3](#63-phase-1-ingest-changes).
- `skills/linearazor/assets/factsheet-template.yaml` — same fields.
- `skills/linearazor/references/signal-modes.md` — exec-summary `(Npt)` suffix per [section 5.3](#53-exec-summary-aggregation).
- `skills/linearazor/references/presentation.md` — estimate-badge palette rule per [section 5.2](#52-per-bullet-badge); stalls-lane creature precedence per [section 8](#8-animation-cast--stalls-lane-precedence).
- `skills/linearazor/references/horizon-and-scope.md` — no changes; the in-scope set definition already supports the scope-hygiene detection.
- `skills/linearazor/assets/config-template.toml` — two new `[thresholds]` keys per [section 7](#7-new-config-keys).

## 10. Worked example

A synthetic full-ritual run for the fictional `infra` group, 4 in-scope projects, cycle day 14 of 21, demonstrating all three additions:

```text
A patient turtle watches infra v2 — no work tracked, the cycle is two
thirds gone.

# linearazor · infra · 4 members · cycle 14
*Cycle window: 21d total · 7 days remaining*
Across 4 projects: 2 shipped (8pt) · 4 stalls (16pt) · 3 questions · 0 changes


<bee art>

Shipped

  Runtime backpressure
    •  ENG-481 (M)  finalize scope for runtime backpressure

  Build-infra sustaining   (milestone: "May runtime cut")
    •  ENG-101 (L)  build-infra: human-intervention issue creation


<cat art>

Questions

  Scheduler refactor
    •  ENG-446 (S)  is in the cycle but unstarted — realistic for this cycle?


<turtle art>

Stalls

  Runtime backpressure
    •  ENG-487 (L)  In Review 5 days  (default threshold: 3)
    •  ENG-502 (M)  PR open 4 days, no merge

  Scheduler refactor
    •  ENG-470 (L)  In Progress 9 days with PR open — flip status?

  infra v2
    •  no work tracked — 14 days in, 7 days remaining


The skill only sees Linear data; PTO, dependencies, conscious deprioritization may explain things.
```

Five things to notice in the example:

- The exec summary aggregates points per lane where any item carries an estimate.
- Each bullet's ID is followed by `(<size>)` when an estimate exists.
- The stalls lane renders the turtle creature because `stalls_silent` (scope hygiene on `infra v2`) wins precedence over the aging variants present on other projects.
- The `infra v2` project appears in the stalls lane only — it has no items in any other lane; scope hygiene is the reason the project surfaces at all.
- Three new stall renderings fire in this single brief: review-aging on ENG-487, awaiting-merge on ENG-502, PR-linked-but-stuck on ENG-470. None overlap.

## 11. Validation

After implementation, the rendered output must satisfy:

1. **Scope-hygiene audit.** For every in-scope project with `projectInScopeIssueCount < scopeMinIssues`, exactly one stall finding renders under that project in the stalls lane, with the variant string matching the project's `elapsed_pct` bucket.
2. **Estimate badge audit.** Every bullet whose source issue has a non-null `estimate.name` carries a `(<name>)` token immediately after the ID. Bullets without an estimate carry no badge.
3. **Exec-summary aggregation audit.** For each lane where at least one item has a numeric `estimate.value`, the exec summary line contains `(Npt)` after the lane count where `N` is the sum of those values. Lanes with zero estimate-bearing numeric items render no `(pt)` suffix.
4. **Stall precedence audit.** No issue carries more than one stall finding in the lane stack. For every issue that matches multiple detection patterns, the rendered finding corresponds to the highest-precedence match in [section 6.2](#62-stall-precedence-updated-full-ordering).
5. **Creature precedence audit.** The stalls lane's creature corresponds to the highest-precedence non-empty sub-flavor in the brief per [section 8](#8-animation-cast--stalls-lane-precedence).

## 12. Open questions

None — the design above is the resolved form of the brainstorming session on 2026-05-19. The fallback path for missing `linkedPRs[].openedAt` is documented at [section 6.3](#63-phase-1-ingest-changes); implementation pins which mode applies after probing the real MCP response.
