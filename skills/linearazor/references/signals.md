# Signal detection rules

Loaded at the Phase-2 signal-composition step and by parallel sub-agents
(when dispatched). Defines how each of the six signal lanes is computed
from the fact sheet emitted by Phase 1.

## Per-project block order

Every per-project block leads with `shipped`, then `questions`,
`changes`, `stalls`, `quality`. A `retrospective` block appears when
the primary horizon crosses a cycle end or milestone target date. The
`lookahead` section is its own top-level block after the per-project
blocks (full-ritual mode) — never bundled into a per-project block.

## 1. Shipped (lead-in)

Union of:

- Issues whose status changed to a Done-category state with
  `completedAt` inside the primary horizon window.
- Merged PRs linked to in-scope issues, with merge date inside the
  primary horizon window.

Rendered as a one-line ticker per project (`• ENG-481  <title>`).
Facts only — no verdicts.

When zero shipped, render literal `No completions in window`. Hard
rule 8 (celebrate first): the block opens with shipped or with the
literal "No completions in window" — never with stalls.

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
  with status `In Progress`:
  "Which of these are realistic to land this cycle?"

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

| Stall | Detection | Render |
| --- | --- | --- |
| Aging WIP | `daysInStatus("In Progress") > agingWipDays` | `<ID>  In Progress N days  (default threshold: M)` |
| No PR linked | `daysInStatus("In Progress") > noPrDays` AND `linkedPRs == []` | `<ID>  In Progress N days, no PR linked` |
| Silent | No status change AND `lastCommentDaysAgo > silentDays` | `<ID>  silent N days` |
| Blocked-without-blocker | Status `Blocked` AND `blockedBy == []` | `<ID>  marked Blocked, no blocker linked` |

A single issue may match multiple stall patterns; emit the most
specific one (Blocked-without-blocker beats Silent beats No-PR beats
Aging-WIP). Never emit more than one stall finding per issue.

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

Renders verbatim from `assets/footer.md`. Always present in full-ritual
mode (hard rule 7).
