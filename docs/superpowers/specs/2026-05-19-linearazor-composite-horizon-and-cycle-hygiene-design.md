**Status:** draft
**Author:** xornivore
**Date:** 2026-05-19
**Skill folder:** `skills/linearazor/`
**Branch:** `feat/linearazor-composite-horizon-and-cycle-hygiene`
**Extends:** [`2026-05-13-linearazor-design.md`](./2026-05-13-linearazor-design.md), [`2026-05-19-linearazor-scope-hygiene-and-stalls-design.md`](./2026-05-19-linearazor-scope-hygiene-and-stalls-design.md).

# linearazor — composite horizon filter, and cycle-hygiene as its own signal

## 1. Summary

Two related fixes to Phase 1 and to the scope-hygiene stall:

1. **Composite horizon filter is non-negotiable.** Phase 1 currently spells the in-scope set as a union of four conditions in `horizon-and-scope.md`, but the easiest MCP query — `list_issues --cycle <name>` — only matches the first condition (cycle assignment). The skill must make it obvious that this single-criterion query is *wrong*, and give the agent a concrete query plan that covers all four conditions.
2. **Scope hygiene splits into two signals.** "Project has zero in-scope issues" conflates two genuinely different shapes: (A) the team isn't doing the work at all, and (B) the team is shipping but isn't assigning issues to the cycle. The signal should distinguish them, because the conversation each one needs is different.

## 2. Motivation

This came out of a live invocation against the `containers` group on cycle FY27-6. The brief reported `Add -full tag to top 10 most popular Chainguard Images` as `no work tracked yet — cycle just started (day 3 of 21)`. The reality:

- One issue **In Review for 26 days** (CON-1263, infrastructure for the project).
- One issue **In Review since today** (CON-1580, S1 schema simplification).
- One issue filed today as a backlog refinement (CON-1581).
- One triaged today (CON-1589).
- A 10-issue milestone "Top 10 Images have 'full' tags" with per-image rollout tickets.

None of these are assigned to the FY27-6 cycle. Two are actively in flight. The brief framed this as silence; the truer reading is "the cycle field on this project isn't being populated, even though the team is shipping." The scope-hygiene observation the user originally asked for was exactly this — *cycle for a project should be populated at the beginning of a cycle, towards the end of the cycle flag it hard*. The current implementation collapses the case onto a "no work" message and the audit can't tell the difference.

The Phase-1 bug is upstream of the signal bug. Fix the query, then the signal layer has two different inputs to react to.

## 3. Out of scope

- Changing the lane stack, exec summary, mood-line voice, animation cast. No new creatures.
- Changing the set of in-scope projects (the labels filter is unchanged).
- New stall *patterns* on individual issues. The four added in
  [`2026-05-19-linearazor-scope-hygiene-and-stalls-design.md`](./2026-05-19-linearazor-scope-hygiene-and-stalls-design.md)
  cover the issue-level cases. This spec only refines the
  project-level scope-hygiene stall and the Phase-1 query plan that
  feeds it.

## 4. Composite horizon filter (Phase 1)

### 4.1 The filter, restated

An issue passes the composite horizon filter when **any** of these is true:

1. `cycleId` is a cycle whose window intersects the primary horizon.
2. Attached to a milestone whose target date falls in the primary horizon.
3. `dueDate` falls in the primary horizon window.
4. The issue was in a status of type `started` (`In Progress`, `In Review`, etc.) at any point in the primary horizon window.

Existing text in `horizon-and-scope.md` already lists these. This spec makes them load-bearing by:

- Naming each condition with an explicit label (C1 through C4) so audits can reference them.
- Adding a concrete Phase-1 query plan that demonstrably covers each.
- Calling out the most common wrong path (C1-only) by name.

### 4.2 Required query plan

Phase 1 must execute the union explicitly. The minimum set of MCP queries:

```text
Q1  list_issues --team <id> --cycle <name>             # covers C1
Q2  list_issues --team <id> --updatedAt -P<horizon>D   # candidates for C4; filter
Q3  list_milestones --project <each in-scope project>  # covers C2 by milestone date
Q4  list_issues --team <id> --updatedAt -P<horizon>D   # candidates for C3; filter by dueDate
```

In practice Q2 and Q4 share the same MCP call — they're both "issues touched in the last N days" filtered locally. Phase 1 then unions the result sets by issue ID before applying the project-label filter.

For C4 specifically: an issue passes when its `status.type == "started"` at any point during the horizon, even if it later transitions out of `started`. The check is against status *history*, not just current status. Linear MCP returns status history on the per-issue detail call; Phase 1 must use it.

### 4.3 Wrong-path callout

Add this directly into `ingest-and-factsheet.md` step 3.1, named and labeled so it can't be skimmed past:

> **Anti-pattern.** Running only `list_issues --cycle <name>` and treating the result as the in-scope set. That query only covers C1 — it misses any issue that was In Progress when the cycle started but has no `cycleId` set. Real cycles have carryover work that lives outside the cycle field; the brief that ignores it claims a project is silent when it's shipping.
>
> **Wrong:** `list_issues --team T --cycle FY27-6` → assume that's the universe.
>
> **Right:** call the queries in [the query plan](#42-required-query-plan), union by issue ID, deduplicate, then filter by project label.

### 4.4 Audit

For every rendered brief, a reviewer (or future smoke harness) must be able to:

- Compute the C4 set by listing all status-history transitions inside the horizon and assert every C4 candidate appears in the fact sheet's `openIssues[]` (or `shipped[]` when the transition was into a Done state).
- Spot-check: pick a known-aging issue in the workspace, confirm it appears in the brief even when its `cycleId` is null.

## 5. Scope-hygiene splits into two signals

### 5.1 New per-project fields

`projects[].inScopeIssueCount` (existing) — count of issues passing the full composite horizon filter.

`projects[].cycleAssignedIssueCount` (NEW) — count of issues with `cycleId` equal to the active cycle's ID. By construction this is always `≤ inScopeIssueCount` for cycle horizons.

`projects[].inScopeIssueIdsByPath` (NEW) — small map keyed by `c1` / `c2` / `c3` / `c4` listing the issue IDs that pass each condition. Lets the signal layer reach for specific IDs when explaining the cycle-hygiene case.

### 5.2 Two stall variants

The single "scope-hygiene" stall in
[`2026-05-19-linearazor-scope-hygiene-and-stalls-design.md`](./2026-05-19-linearazor-scope-hygiene-and-stalls-design.md)
splits in two. Both still render in the stalls lane, both still map
to `stalls_silent` (turtle), both still fire as one bullet per
project. Detection separates them:

| Variant | Detection | Bullet body (early framing — full table follows) |
| --- | --- | --- |
| **Empty project** | `inScopeIssueCount == 0` | `no work tracked yet — cycle just started (day N of M)` |
| **Cycle field unpopulated** | `inScopeIssueCount > 0` AND `cycleAssignedIssueCount == 0` | `<K> in-flight issues, none assigned to the cycle (<ID1>, <ID2>, …)` |

Empty-project framing keeps the existing early/mid/late table:

| Position | `elapsed_pct` | Empty-project body |
| --- | --- | --- |
| early | ≤ 33% | `no work tracked yet — cycle just started (day N of M)` |
| mid | 33% < x ≤ 66% | `no work tracked — N days in, M days remaining` |
| late | > 66% | `no work tracked — cycle ends in N days` |

Cycle-field-unpopulated framing softens early and hardens late the same way:

| Position | `elapsed_pct` | Cycle-unpopulated body |
| --- | --- | --- |
| early | ≤ 33% | `K in-flight issues, none assigned to the cycle yet — early days (<ID1>, <ID2>, …)` |
| mid | 33% < x ≤ 66% | `K in-flight issues, none assigned to the cycle — N days in (<ID1>, <ID2>, …)` |
| late | > 66% | `K in-flight issues, none assigned to the cycle — cycle ends in N days (<ID1>, <ID2>, …)` |

When `K` is large enough that listing IDs would dominate the line, cap at three IDs and append `… and K-3 more`.

### 5.3 Why two variants, not one

The conversation each variant invites is different:

- **Empty project**, late framing: "Is this project still appetite for the cycle? Should it be dropped?"
- **Cycle field unpopulated**, late framing: "The work is happening. Hook it into the cycle so the rest of the org can see it."

Collapsing them into "no work tracked" mis-frames the second case and erodes the brief's credibility — a reader who knows their own project is shipping will trust the brief less the next time it says something is stalled.

### 5.4 Precedence inside the stalls lane

Issue-level stalls and project-level scope-hygiene continue to coexist for the same project (the project sub-header carries both). The two new scope-hygiene variants are mutually exclusive per project — either the project has zero in-scope issues (empty) or it has some that aren't cycle-bound (unpopulated). Cannot both fire.

When a project has `inScopeIssueCount > 0 AND cycleAssignedIssueCount > 0 AND inScopeIssueCount > cycleAssignedIssueCount`, the scope-hygiene signal does NOT fire — the cycle field is in use, just not for everything. The carryover issues themselves will surface as issue-level stalls (Review-aging, PR-linked-but-stuck, etc.) on their own merits.

## 6. Files affected

- `skills/linearazor/references/horizon-and-scope.md` — label the four composite-filter conditions C1-C4, link them by name in audit prose.
- `skills/linearazor/references/ingest-and-factsheet.md` — add the explicit query plan from [section 4.2](#42-required-query-plan), the wrong-path callout from [section 4.3](#43-wrong-path-callout), and the new per-project fields from [section 5.1](#51-new-per-project-fields).
- `skills/linearazor/assets/factsheet-template.yaml` — `cycleAssignedIssueCount`, `inScopeIssueIdsByPath`.
- `skills/linearazor/references/signals.md` — split the scope-hygiene subsection into two variants per [section 5.2](#52-two-stall-variants); refine precedence note per [section 5.4](#54-precedence-inside-the-stalls-lane).

## 7. Worked example

Same containers FY27-6 cycle as the live invocation. The actual data is preserved as a synthetic equivalent — fictional names from the prior spec's worked-example vocabulary.

```text
A patient turtle watches Runtime backpressure — the cycle field hasn't
been populated, but the work is in flight.

# linearazor · infra · 7 members · cycle 14
*Cycle window: 21d total · day 3 of 21 · 18 days remaining*
Across 3 projects: 1 shipped (5pt) · 2 stalls (2pt) · 0 questions · 0 changes


<bee art>

Shipped

  Build-infra sustaining
    •  ENG-101 (L)  finalize scope for runtime backpressure


<turtle art>

Stalls

  Runtime backpressure
    •  4 in-flight issues, none assigned to the cycle yet — early days (ENG-263, ENG-580, ENG-581, … and 1 more)

  Policy gates · Early Access
    •  ENG-044 (S)  In Review 5 days  (default threshold: 3)


The skill only sees Linear data; PTO, dependencies, conscious deprioritization may explain things.
```

The key difference from the prior brief: `Runtime backpressure` no longer reads as "no work tracked" — it reads as "the work is here, but the cycle field isn't being used". A reader can act on that. Across-run audit: every named ID (`ENG-263` etc.) corresponds to an issue that passed at least one of C2-C4 but failed C1.

## 8. Validation

After implementation:

1. **C1-C4 union audit.** Phase-1 fact sheet contains every issue that passes any of C1-C4. Run a workspace where a known carryover issue exists with `cycleId == null` but was In Progress at cycle start — confirm it appears in the fact sheet.
2. **Empty-vs-unpopulated audit.** For each project in the brief, the variant chosen for the scope-hygiene line matches the rule in [section 5.2](#52-two-stall-variants):
   - `inScopeIssueCount == 0` → empty-project variant fires.
   - `inScopeIssueCount > 0 AND cycleAssignedIssueCount == 0` → unpopulated variant fires.
   - Otherwise no scope-hygiene line fires for that project.
3. **ID-list audit.** When the unpopulated variant fires, the listed IDs are exactly the in-scope IDs that fail C1 (no cycle), capped at three with `… and N more` appended when needed.
4. **No-regression audit.** A workspace where every project's cycle is populated and full produces no scope-hygiene findings at all.

## 9. Open questions

None.
