**Status:** draft
**Author:** xornivore
**Date:** 2026-05-14
**Skill folder:** `skills/linearazor/`
**Branch:** `feat/linearazor-lane-grouped`
**Supersedes (in part):** [`2026-05-13-linearazor-design.md`](./2026-05-13-linearazor-design.md) — the per-project block structure described there.

# linearazor — lane-grouped layout design

## 1. Summary

The current `linearazor` brief renders one block per project, with up to six signal lanes inside each block, each lane led by its own ASCII animal. In practice the animals stack — a six-project brief carries dozens of small animal blocks, and the lane structure is repeated six times. The animals dominate the page and the lane comparisons that matter ("what shipped this cycle? what stalled?") are hard to see at a glance.

This spec inverts the structure: lanes become top-level, projects become sub-sections inside each lane, and each lane carries exactly one animal. The brief reads as "here is everything shipped, here is everything stalled" instead of "here is project A, here is project B, …, with shipped and stalls inside each."

The Phase-1 ingest, fact-sheet schema, and signal-detection rules are unchanged. This is a presentation-layer change with two follow-on edits to the signal layer: the wording of hard rule 8 ("celebrate first") and a one-line correction to the animation-cast frequency rule.

## 2. Motivation

Reading the existing rendered brief for a single cycle of seven members across six projects:

- The page is roughly 60% animals by line count.
- The reader has to scan project-by-project to find all the stalls, instead of seeing one stalls lane.
- The "celebrate first" rule fires per project — six small "Shipped:" headers, each with one or two bullets — which dilutes the actual cross-project celebration.
- The cross-cutting cycle-end question lives outside the per-project loop and feels orphaned.

Lane-first grouping fixes all four. The page shortens, the comparisons that matter (lane-by-lane) become visible, and the cross-cutting questions land naturally inside the Questions lane.

## 3. Out of scope

- Phase-1 ingest steps, Linear MCP usage, the fact-sheet schema. Unchanged.
- Signal detection rules (which findings fire, what their thresholds are). Unchanged.
- Mood-line voice, tone rules, palette colors, ANSI rendering contract. Unchanged in substance — a few examples that incidentally show per-project framing migrate to lane framing.
- The animation cast (which animal represents which lane). Unchanged.
- The `lookahead` block. Already a top-level section, stays that way.

## 4. Lane structure

### 4.1 Lane order

Lanes render in fixed order. Empty lanes are omitted entirely. The `lookahead` block stays its own top-level section after the lane stack (unchanged):

```text
shipped
questions
changes
stalls
quality
retrospective    (only when the horizon-cross trigger fires)
─────────────
lookahead        (own top-level block, after the lane stack)
```

`retrospective` fires under the same trigger as today (primary horizon crosses a cycle end or any in-scope milestone target date falls in the primary window). When it fires, it sits after `quality`.

### 4.2 Inside a lane

Each lane is a single ASCII animal followed by the lane title and a list of projects. Inside each project, items are bullets:

```text

<animal art>

<Lane title>

  <Project name>
    •  ID  title
    •  ID  title

  <Project name>
    •  ID  title

```

One animal per lane in the entire brief. No per-project animals.

### 4.3 Project order inside a lane

The same project sequence appears in every lane the project participates in. Order:

1. Linear project `status.type` — `started` first, then `backlog`, then `completed`.
2. Inside each tier, alphabetical by project name (case-insensitive).

Projects with zero items in a given lane are omitted from that lane. A project can appear in some lanes and not others.

### 4.4 Milestone sub-grouping

Today, the `shipped` lane sometimes carries a milestone annotation (e.g., `milestone: "May runtime cut"`) that groups several issues. With lane-first ordering, the milestone annotation moves onto the project sub-header line:

```text
  Build-infra sustaining   (milestone: "May runtime cut")
    •  ENG-101   …
    •  ENG-102   …
    •  ENG-103   …
```

If items under a project span multiple milestones, omit the annotation entirely (don't break into milestone-keyed sub-sub-sections — that reintroduces nesting). The Linear hyperlink on each ID carries the milestone in its destination anyway.

### 4.5 Cycle-end question

The "two-plus issues still In Progress crossing cycle end" question, the milestone-appetite question, and any other cross-cutting question fire **inside** the Questions lane as ordinary items. They are not promoted to a separate top block. Project sub-header for cross-cutting questions is `(cross-project)`.

## 5. Padding rule

One blank line above, one blank line below every ASCII art block. Every art. Every appearance. No exceptions, no extra second-blank-line for "breathing room," no zero-line tight-coupling between the art and the lane title beneath it.

This applies to:

- Animal art at the top of a lane.
- The setup mascot (duck) in `setup-flow.md`.
- The empty-brief mascot (puzzled face) when every lane is empty.
- The optional razor glyph in the run header.

Audit: any ASCII art block in the rendered output that isn't bracketed by exactly one blank line on each side is a violation.

## 6. Hard-rule changes

Two hard rules in `SKILL.md` and the animation cast rule in `animation.md` change.

### 6.1 Rule 8 (`[Signal] Celebrate first`)

Today:

> Each per-project block leads with shipped. If nothing shipped, the block opens with `No completions in window` — never with stalls.

New:

> Lanes render in the fixed order in [section 4.1](#41-lane-order). When the Shipped lane has any content, it leads the brief. When the Shipped lane is empty, it is omitted entirely — the brief opens with the next non-empty lane, never with `stalls` while `shipped` has content.

The `No completions in window` literal goes away — it existed only because the per-project loop forced every project to render a Shipped section. With lane-first ordering, an empty Shipped lane is just an absent lane.

Audit: parse the rendered output for lane titles in order. If `Shipped` and `Stalls` both appear, `Shipped` must precede `Stalls`. If `Stalls` is the first lane, no `Shipped` lane may exist in the output.

### 6.2 Animation cast: one animal per lane per brief

Today (`animation.md` "Cast" intro):

> One animal per signal category per per-project section, never one per item.

New:

> One animal per signal category per brief, never one per project and never one per item.

This is a one-line change; the cast itself is unchanged. Hard rule 12 (layer separation) still binds — this is a presentation-layer change.

### 6.3 Spider sub-flavor (scope drift)

Today the spider replaces the penguin in the Changes lane heading when the **per-project** scope-change count exceeds two. With lane-first ordering there is only one Changes lane, so:

> Total scope changes across all in-scope projects in the primary horizon ≥ 3 ⇒ spider replaces penguin in the Changes lane heading.

## 7. Mode interaction

The four documented modes behave like this:

| Mode | Lane structure | Project sub-headers inside a lane | Lookahead |
| --- | --- | --- | --- |
| full ritual | yes | yes | own top-level block (unchanged) |
| `digest` | yes | yes | collapsed to one-liner per project (unchanged) |
| `brief` | yes | **flat** — no project sub-headers, items render as `ID  title  · project`<br>(slack-paste shape; cheaper vertically) | suppressed (unchanged) |
| `share` | yes | yes | own top-level block (unchanged) |

For `brief` mode, items inside a lane render as a flat bullet list with the project as a trailing dot-separated tag. This matches how someone would paste the brief into a slack message and skim it — no nested project headers to parse.

## 8. Files affected

- `skills/linearazor/SKILL.md` — rewrite hard rule 8; add a one-line pointer to this spec under the existing "Reference index."
- `skills/linearazor/references/signals.md` — rewrite "Per-project block order" into "Lane order"; reword each signal-lane rule to drop per-project framing where present; move the cycle-end question into the Questions lane explicitly.
- `skills/linearazor/references/signal-modes.md` — update the mode tables to reflect the per-mode shapes in [section 7](#7-mode-interaction).
- `skills/linearazor/references/presentation.md` — add the universal padding rule from [section 5](#5-padding-rule); remove any per-project layout hints; update the rendered example.
- `skills/linearazor/references/tone.md` — minor: a handful of examples that show per-project framing migrate to lane framing.
- `skills/linearazor/assets/animation.md` — change the one-line frequency rule per [section 6.2](#62-animation-cast-one-animal-per-lane-per-brief); update the spider sub-flavor rule per [section 6.3](#63-spider-sub-flavor-scope-drift).
- `skills/linearazor/tests/fixtures/*.mcp.yaml` — fixtures themselves are Phase-1 data and don't change. If a fixture's snapshotted Phase-2 output is checked in alongside it, that snapshot is regenerated.
- `docs/superpowers/specs/2026-05-13-linearazor-design.md` — add a one-line "superseded in part by [this spec]" pointer at the top of section 4 (the layout section).

## 9. Worked example

A synthetic cycle for the fictional `infra` group, 2 members, 6 in-scope
projects, current cycle 14. Same data, both shapes.

### 9.1 Today's shape (per-project)

```text
A patient cat lingers — two days remain in the cycle and three issues are still moving.

# linearazor · infra · 2 members · cycle 14
*Cycle window: 21d total · 2 days remaining*

### Cycle-end question
<cat art>
- Three issues are still started with two days left — which land, which slide? (ENG-487, ENG-470, ENG-446)

### Runtime backpressure
<bee art>
**Shipped:**
  • ENG-481  finalize scope for runtime backpressure
<cow art>
**Stalls:**
  • ENG-487  In Progress 8 days  (default threshold: 7)
<cat art>
**Questions:**
  • What's the next concrete step on ENG-487, and is anything blocking it?

### Scheduler refactor
<bee art>
**Shipped:**
  • ENG-492  rough draft of post-migration roadmap
<cat art>
**Questions:**
  • ENG-446 is in the cycle but unstarted — realistic to land?

### Build-infra sustaining
<bee art>
**Shipped** (milestone "May runtime cut"):
  • ENG-101, ENG-102, ENG-103

### Policy engine · early access
**Shipped:** No completions in window.

### Policy engine · GA
<bee art>
**Shipped** (milestone "Configurable policies"):
  • ENG-505  rename cooldown policy

### Interrupts rotation
<bee art>
**Shipped:**
  • ENG-440  Interrupts rotation - week 7

The skill only sees Linear data; PTO, dependencies, conscious deprioritization may explain things.
```

Eight animal art blocks. Six project headers. Three "Shipped:" headers despite Shipped being one global lane in spirit.

### 9.2 New shape (lane-first)

```text
A patient cat lingers — two days remain in the cycle and three issues are still moving.

# linearazor · infra · 2 members · cycle 14
*Cycle window: 21d total · 2 days remaining*

<bee art>

Shipped

  Runtime backpressure
    •  ENG-481  finalize scope for runtime backpressure

  Scheduler refactor
    •  ENG-492  rough draft of post-migration roadmap

  Build-infra sustaining   (milestone: "May runtime cut")
    •  ENG-101   build-infra: human-intervention issue creation
    •  ENG-102   build-infra: workflow-failure issue creation
    •  ENG-103   build-infra: various failure-mode issue creation

  Policy engine · GA   (milestone: "Configurable policies")
    •  ENG-505  rename cooldown policy

  Interrupts rotation
    •  ENG-440  Interrupts rotation - week 7


<cat art>

Questions

  (cross-project)
    •  Three issues are still started with two days left — which land, which slide? (ENG-487, ENG-470, ENG-446)

  Runtime backpressure
    •  What's the next concrete step on ENG-487, and is anything blocking it?

  Scheduler refactor
    •  ENG-446 is in the cycle but unstarted — realistic to land?


<cow art>

Stalls

  Runtime backpressure
    •  ENG-487  In Progress 8 days  (default threshold: 7)


The skill only sees Linear data; PTO, dependencies, conscious deprioritization may explain things.
```

Three animal art blocks. Three lane headings. The cross-project question lives where it belongs. The reader sees "everything shipped" and "everything stalled" without scanning six projects.

## 10. Validation

After the implementation lands, the rendered output must satisfy:

1. **Lane order audit.** Lane titles appear in `shipped, questions, changes, stalls, quality, retrospective` order. If a lane is absent, its slot is simply skipped. The `lookahead` block, when present, sits after the entire lane stack.
2. **Animal count audit.** Each animal in the cast appears at most once in the lane stack of a single brief. The empty-brief mascot, when rendered, replaces the whole stack (no per-lane animals appear alongside it).
3. **Padding audit.** Every ASCII art block in the rendered output is bracketed by exactly one blank line above and one blank line below.
4. **Project order audit.** Inside any given lane with multiple projects, project sub-headers appear in `started → backlog → completed` order, alphabetized within each tier. The same projects appear in the same relative order across every lane in which they participate.
5. **Celebrate-first audit.** When `Shipped` has content, it precedes any other lane in the rendered output.

## 11. Open questions

None — the design above is the resolved form of the brainstorming session on 2026-05-14. Outstanding work is implementation, tracked separately via the writing-plans skill.
