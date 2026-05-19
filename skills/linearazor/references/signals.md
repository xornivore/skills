# Signal detection rules

Loaded at the Phase-2 signal-composition step and by parallel sub-agents
(when dispatched). Defines how each of the six signal lanes is computed
from the fact sheet emitted by Phase 1.

## Lane order

The brief renders as a stack of top-level lanes in this fixed order:

1. shipped
2. questions
3. changes
4. stalls
5. quality
6. retrospective (only when the primary horizon crosses a cycle end
   or any in-scope milestone target date falls in the primary window)

Empty lanes are omitted entirely. When every lane is empty across
every in-scope project, the lane stack is replaced by the empty-brief
mascot (see [signal-modes.md](./signal-modes.md) "Empty-brief case").

`lookahead` stays its own top-level block after the lane stack —
never bundled into a lane. Hard rule 11 binds.

Inside each lane, items are grouped by project. Projects appear in
the same global order in every lane: by Linear `status.type`
(`started` first, then `backlog`, then `completed`), then alphabetical
within each tier. A project with zero items in a given lane is
omitted from that lane.

Each lane carries exactly one ASCII creature at the top of the lane.
Hard rule 8 (celebrate first) binds: when `shipped` has content it
leads the brief; when `shipped` is empty it is omitted and the next
non-empty lane leads — never opening with `stalls` while `shipped`
has content.

## 1. Shipped (lead-in)

Union of:

- Issues whose status changed to a Done-category state with
  `completedAt` inside the primary horizon window.
- Merged PRs linked to in-scope issues, with merge date inside the
  primary horizon window.

Rendered as bullet items grouped under each project's sub-header
(`• ENG-481  <title>`). Facts only — no verdicts.

When a project's `shipped` for the cycle spans a single milestone,
annotate the project sub-header inline:
`<Project name>   (milestone: "<milestone>")`. When items under a
project span multiple milestones, omit the annotation — the Linear
hyperlink on each ID carries the milestone in its destination.

When zero issues shipped across every project, the `shipped` lane is
omitted entirely (the lane is empty, no literal placeholder).

## 2. Questions

Phrased as questions. Hard rule 5 binds: every line ends with `?`.
Detection patterns:

- `daysInStatus("In Progress") > thresholds.agingWipDays`
  AND `lastCommentDaysAgo > thresholds.agingWipDays`:
  "What's the next concrete step on <ID>, and is anything blocking it?"
- Status `Blocked` AND `blockedBy == []`:
  "Is <ID> still actually blocked? Nothing is recorded as blocking it."
- Status `Blocked` AND every issue in `blockedBy` is in a Done state:
  "Is <ID> still actually blocked? Its blocker closed <date>."
- A milestone in `milestones[].datesMovedInWindow` has two or more
  date moves:
  "Is the appetite for <milestone> still well-framed?"
- The primary horizon crosses a cycle end AND there are 2+ issues
  with status `In Progress` across all in-scope projects:
  "Three issues are still started with N days left — which land, which
  slide? (ID1, ID2, …)". This is a cross-project question; render it
  under the project sub-header `(cross-project)` inside the questions
  lane, not promoted to a separate top-level block.

## 3. Changes

Information, not failure (Shape Up). From `projects[].scopeChangesInWindow`
and `projects[].milestones[].datesMovedInWindow`:

- Milestone target-date moves — render
  `Milestone "<name>" moved from <old> -> <new>`.
- Issues added to or removed from a milestone — render
  `<ID> added to scope this week` / `<ID> removed from scope this week`.
- Scope label changes on in-scope issues — render
  `<ID> labels changed: <old set> -> <new set>`.
- Projects entering or leaving an active state — render
  `Project state moved <old> -> <new>`.

Each line states the *what* and the *when*; no verdicts.

## 4. Stalls

Defaults from `thresholds`, never learned. Each stall lists facts —
never the person (hard rule 3).

### Issue-level stalls

| Stall | Detection | Render |
| --- | --- | --- |
| Reverted | `openIssues[].revertedAt != null` AND `revertedAt` falls in the primary horizon | `<ID>  rolled back from Done <date>` |
| Blocked-without-blocker | Status `Blocked` AND `blockedBy == []` | `<ID>  marked Blocked, no blocker linked` |
| Awaiting-merge | Status name matches the review pattern below AND any `linkedPRs[*].openedAt` is older than `prReviewDays` ago | `<ID>  PR open N days, no merge` |
| Review-aging | `daysInStatus > prReviewDays` AND status name matches the review pattern | `<ID>  In Review N days  (default threshold: M)` |
| PR-linked but stuck | `daysInStatus("In Progress") > noPrDays` AND `linkedPRs != []` AND status name does NOT match the review pattern | `<ID>  In Progress N days with PR open — flip status?` |
| Silent | No status change AND `lastCommentDaysAgo > silentDays` | `<ID>  silent N days` |
| No-PR | `daysInStatus("In Progress") > noPrDays` AND `linkedPRs == []` | `<ID>  In Progress N days, no PR linked` |
| Aging-WIP | `daysInStatus("In Progress") > agingWipDays` | `<ID>  In Progress N days  (default threshold: M)` |

**Review pattern.** Status name matches the case-insensitive regex
`\b(in[ -]?)?review\b|code[ -]?review`. Calibrate against the user's
workspace status set at implementation time — different workspaces use
different review-stage names (`In Review`, `Code Review`, `PR Review`).
The regex above is the floor.

**Awaiting-merge fallback.** When `linkedPRs[*].prOpenedAtApproximate`
is `true` for a given PR, fall back to `daysInStatus` against the
review-stage status — approximate but bounded. The audit treats
fallback firings the same as direct firings; the fact-sheet field
captures the degraded-mode source for transparency.

A single issue may match multiple patterns; emit the most-specific one
per precedence — top-down, first match wins:

1. Reverted
2. Blocked-without-blocker
3. Awaiting-merge
4. Review-aging
5. PR-linked but stuck
6. Silent
7. No-PR
8. Aging-WIP

Never emit more than one stall finding per issue.

### Project-level scope-hygiene stall

Fires once per in-scope project whose `projects[].inScopeIssueCount`
is below `thresholds.scopeMinIssues`. Renders under the project's
sub-header in the stalls lane — independent of any issue-level stalls
in the same project (both can coexist).

The bullet body's wording is keyed off the cycle's `elapsed_pct =
(today - cycle.startsAt) / cycle.length`:

| Position | `elapsed_pct` | Bullet body |
| --- | --- | --- |
| early | ≤ 33% | `no work tracked yet — cycle just started (day N of M)` |
| mid | 33% < x ≤ 66% | `no work tracked — N days in, M days remaining` |
| late | > 66% | `no work tracked — cycle ends in N days` |

When `0 < inScopeIssueCount < scopeMinIssues` (only possible when the
threshold is raised above 1), substitute `1 issue tracked` (or
`K issues tracked` for K > 1) for `no work tracked` and otherwise
reuse the variant.

Project muteness reads as silence, not as aging — the scope-hygiene
stall maps to the `stalls_silent` palette role and the turtle creature.
This affects the stalls-lane creature-precedence choice when multiple
sub-flavors fire — see [presentation.md](./presentation.md) "Stalls
lane creature precedence."

**Audit:** for every project where `inScopeIssueCount < scopeMinIssues`,
exactly one bullet renders under its sub-header in the stalls lane,
matching the variant string for the project's `elapsed_pct` bucket.

## 5. Quality

Acceptance-criteria and clarity gaps on in-scope issues:

- `bodyHasAcceptanceCriteria == false` AND the issue has subtasks OR
  `daysInStatus > thresholds.agingWipDays`: emit
  `<ID>  No acceptance criteria`.
- Title matches the vague-title regex set (`^fix bug$`, `^phase \d+$`,
  `^update$`, `^cleanup$`, `^WIP`, case-insensitive): emit
  `<ID>  Vague title: "<title>"`.
- `bodyIsEmpty == true` (issue body empty): emit
  `<ID>  No body`.

Calibrate the vague-title regex set against real titles at
implementation time (spec section 13). The set above is the floor.

## 6. Retrospective (horizon-triggered)

Triggered when the primary horizon crosses a cycle end OR any in-scope
milestone target date falls in the primary window.

Forward-looking only: "What would we want to know earlier next time?"
— never "what went wrong." No blame framing, no per-person commentary.
Patterns:

- A milestone slipped: "What signaled <milestone> was at risk that we
  could have caught earlier?"
- A cycle ended with N issues still In Progress: "What about <issue>
  surprised us — and how would we recognize the same shape next time?"
- Multiple scope changes in the same cycle: "What changed about our
  understanding of <project> that drove these scope changes? Was it
  the work or the framing?"

## 7. Lookahead

Two signals only. Never carries stalls, shipped, or retrospective
(hard rule 11). Source: `projects[].lookaheadIssues[]` and
`projects[].lookaheadMilestones[]`.

### Unclarities (lookahead)

Per `lookaheadIssues[]`:

- `bodyHasAcceptanceCriteria == false` AND `milestone != null`:
  `<ID>  No acceptance criteria  (<milestone>)`.
- `bodyIsEmpty == true`: `<ID>  No body, attached to <milestone>`.
- Title matches the vague-title regex set: `<ID>  Vague title: "<title>"`.
- `assigneeIdentifier == null` AND `milestone != null` AND
  `daysToTarget <= 21`:
  "What does done look like for <ID>?"

The first three render as statements; the fourth renders as a question
(hard rule 5 — every question line ends with `?`).

### Appetite-shape risk

Per `lookaheadMilestones[]`:

- `startedIssueCount == 0` AND
  `daysToTarget <= render.lookahead_appetite_warn_days`:
  `"<milestone>" — 0 started, <N>d to target`.
- `scopeChangedSinceTargetSet == true` AND target date did not move:
  `"<milestone>" — scope grew, target unchanged. Appetite unclear?`.
- Target date moved AND scope did not change:
  `"<milestone>" — target moved, scope unchanged. Appetite unclear?`.

## Disclaimer footer

Renders verbatim from `assets/footer.md` in full-ritual terminal mode.
Suppressed in `brief`, `digest`, and `share`. Hard rule 7 binds.
