# linearazor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `linearazor` Claude Code skill — a project-board reviewer that reads a scoped Linear workspace via Linear MCP and produces per-project briefs with four signals (questions, changes, stalls, quality), a shipped lead-in, a tiered lookahead, and a mood line, rendered in a Catppuccin palette with a hand-drawn ASCII animation cast.

**Architecture:** Skill packaged as Markdown content (no runtime code). `SKILL.md` is the lean entry point: mode routing, hard rules, reference index. References split by layer — **signal layer** (setup-flow, horizon-and-scope, ingest-and-factsheet, signals, signal-modes, tone, parallel-dispatch) and **presentation layer** (presentation, palettes, mood-line, plus `assets/animation.md`). `assets/` holds the signal-layer templates (config, fact-sheet, footer) and the presentation-layer animation cast. Two-phase pipeline (Phase 1 deterministic ingest → Phase 2 model-driven analyze) plus an optional `share` mode that shells out to `charmbracelet/freeze` for PNG export.

**Tech Stack:** Markdown only. Validation by `pnpm lint` (`markdownlint-cli2`) and `npx skills-ref validate`. The skill is content for Claude Code — bash snippets inside `SKILL.md` are executed by the agent at runtime against Linear MCP and the user's shell.

**Spec source:** `docs/superpowers/specs/2026-05-13-linearazor-design.md`. When a step says "transcribe spec section N.M," the spec prose is the source of truth — adapt to skill-instruction voice ("when invoked, do X" rather than "linearazor does X") per `skills/CLAUDE.md` section 3.1.

**Authoring rules:** Follow `skills/CLAUDE.md` (skill-authoring conventions, derived from the agentskills.io specification). Read it before starting Task 1. Doc voice and cross-reference rules in `docs/CLAUDE.md` apply to this plan file and to the per-skill `README.md`.

---

## Working environment

- Branch: `feat/linearazor` (already created from `main` at `f3974cd`).
- Worktree: `.worktrees/feat/linearazor/`.
- All commands run from the worktree root.
- Run `pnpm install` once at the start of Task 1 if `node_modules/` is missing.

## Target file structure

```text
skills/linearazor/
├── SKILL.md
├── README.md
├── references/
│   ├── setup-flow.md                 # signal layer
│   ├── horizon-and-scope.md          # signal layer
│   ├── ingest-and-factsheet.md       # signal layer
│   ├── signals.md                    # signal layer
│   ├── signal-modes.md               # signal layer
│   ├── tone.md                       # signal layer
│   ├── parallel-dispatch.md          # signal layer
│   ├── presentation.md               # presentation layer
│   ├── palettes.md                   # presentation layer
│   └── mood-line.md                  # presentation layer
├── assets/
│   ├── config-template.toml          # signal layer
│   ├── factsheet-template.yaml       # signal layer
│   ├── footer.md                     # signal layer
│   └── animation.md                  # presentation layer
└── tests/
    └── fixtures/
        ├── healthy.mcp.yaml
        ├── aging.mcp.yaml
        ├── cycle-end-retro.mcp.yaml
        └── many-projects.mcp.yaml
```

Plus one modification:

- `README.md` (top-level) — add `linearazor` row to the Skills table.

## Voice rules (apply to all skill files)

- **`SKILL.md` body:** imperative — "when invoked, do X", "must", "never". Per `skills/CLAUDE.md` section 3.1. Strip `should` / `may` / `might` / `could` / `ideally`.
- **References:** declarative — describe rules and tables. References inform the action; `SKILL.md` issues the orders.
- Each standalone rule paired with a correct example and a wrong example, per `skills/CLAUDE.md` section 3.2.
- Mechanical rules carry an audit cue (per `skills/CLAUDE.md` section 3.3) — for linearazor, the audit cues from spec section 9 hard rules go verbatim into `SKILL.md`.
- No `§`. Cross-references use plain Markdown anchor links or plain prose, per `docs/CLAUDE.md`.
- No angle brackets in any frontmatter value, per `skills/CLAUDE.md` section 2.

## Layer hygiene (the diff audit)

Hard rule 12 from the spec is mechanically auditable: a change touching only presentation-layer files must leave signal-layer files untouched. Group commits by layer where possible — a Task that writes a signal-layer reference commits only signal-layer files; a Task that writes a presentation-layer reference commits only presentation-layer files.

---

## Phase 1 — Scaffold and asset templates

### Task 1: Scaffold directory tree and asset templates

**Files:**

- Create: `skills/linearazor/` (plus `references/`, `assets/`, `tests/fixtures/` subdirs)
- Create: `skills/linearazor/assets/config-template.toml`
- Create: `skills/linearazor/assets/factsheet-template.yaml`
- Create: `skills/linearazor/assets/footer.md`

**Source spec sections:** 5 (Configuration), 4.1 (Phase 1 fact sheet), 8.4 ([Signal layer] disclaimer footer).

- [ ] **Step 1: Ensure node_modules is present in the worktree**

```bash
[ -d node_modules ] || pnpm install
```

Expected: either no output (already present) or pnpm completes; husky reinstalls hooks.

- [ ] **Step 2: Create the directory tree**

```bash
mkdir -p skills/linearazor/references skills/linearazor/assets skills/linearazor/tests/fixtures
```

- [ ] **Step 3: Verify directories exist and are empty**

```bash
find skills/linearazor -type d
```

Expected:

```text
skills/linearazor
skills/linearazor/references
skills/linearazor/assets
skills/linearazor/tests
skills/linearazor/tests/fixtures
```

- [ ] **Step 4: Write `assets/config-template.toml`**

The scaffold written by the `reconfigure` flow. Write the file with this exact content:

````toml
# version = 1
# linearazor scope: <group-name>
#
# This file is hand-editable. The skill rewrites it only from the
# `reconfigure` flow, and only after confirmation.

group   = "<group-name>"
team    = "<linear-team-display-name>"
members = []
labels  = []
default_horizon = "cycle"        # cycle | week | 2w | 4w | milestone

[thresholds]
aging_wip_days = 7               # In Progress longer than this -> aging
silent_days    = 7               # No status change AND no comment in this window
no_pr_days     = 3               # In Progress this long with no linked PR

[render]
palette                       = "catppuccin-mocha"
parallel_project_threshold    = 6
lookahead_unclarities         = true
lookahead_appetite            = true
lookahead_appetite_warn_days  = 14

[render.palette_overrides]
# shipped = "rosewater"
````

Note: the `<group-name>` / `<linear-team-display-name>` placeholders in the template body are documented as literal placeholders the `reconfigure` flow substitutes. They are not in any YAML frontmatter (this is a TOML asset, not a `SKILL.md`), so the no-angle-brackets rule does not apply.

- [ ] **Step 5: Write `assets/factsheet-template.yaml`**

The Phase-1 → Phase-2 handoff skeleton. yaml format: quote-light strings, inline comments allowed, human-reviewable. Marked illustrative until the Linear MCP probe (spec section 13).

````yaml
# linearazor fact-sheet template
#
# Phase-1 to Phase-2 handoff. Illustrative shape; pin to the actual
# Linear MCP wire format at implementation time (spec section 13).
#
# Placeholder values in angle brackets ("<group-name>", "<ISSUE-ID>",
# "YYYY-MM-DD") document the substitution points. Phase 1 replaces
# them before Phase 2 reads the document. Keep them quoted so yaml
# parses them as strings rather than attempting date / number coercion.

schemaVersion: 1
group: "<group-name>"

horizon:
  kind: cycle              # cycle | week | 2w | 4w | milestone | since
  from: "YYYY-MM-DD"
  to: "YYYY-MM-DD"

lookahead:
  kind: cycle
  from: "YYYY-MM-DD"
  to: "YYYY-MM-DD"
  suppressed: false        # true when the user passed "lookahead off"
                           # or the primary horizon is "since <date>"

thresholds:
  agingWipDays: 7
  silentDays: 7
  noPrDays: 3

members:
  - displayName: "<name>"
    identifier: "<linear-user-id>"

unresolved: []             # member names that failed to resolve against
                           # Linear users; surfaced in the setup-health
                           # footer, never as stalls

projects:
  - name: "<project-name>"
    state: started         # started | paused | completed | canceled
    milestones:
      - name: "<milestone-name>"
        targetDate: "YYYY-MM-DD"
        datesMovedInWindow: []
    shipped:
      - id: "<ISSUE-ID>"
        title: "<title>"
        completedAt: "ISO-8601"
        linkedPRs: []
    openIssues:
      - id: "<ISSUE-ID>"
        title: "<title>"
        status: "<status>"
        assigneeIdentifier: "<linear-user-id>"
        daysInStatus: 0
        lastCommentDaysAgo: 0
        linkedPRs: []
        blockedBy: []
        milestone: null
        labels: []
        bodyHasAcceptanceCriteria: false
    scopeChangesInWindow:
      - id: "<ISSUE-ID>"
        change: "<change-kind>"   # added-to-milestone | removed-from-milestone | labels-changed | project-state-moved
        at: "ISO-8601"
    lookaheadMilestones:
      - name: "<milestone-name>"
        targetDate: "YYYY-MM-DD"
        startedIssueCount: 0
        daysToTarget: 0
        scopeChangedSinceTargetSet: false
    lookaheadIssues:
      - id: "<ISSUE-ID>"
        title: "<title>"
        assigneeIdentifier: null
        status: "<status>"
        milestone: null
        bodyHasAcceptanceCriteria: false
        bodyIsEmpty: true
````

- [ ] **Step 6: Write `assets/footer.md`**

The literal disclaimer string for the full-ritual run footer. Hard rule 7 binds: this file's text is rendered verbatim.

````markdown
# Footer disclaimer

Rendered verbatim at the end of every full-ritual run. Suppressed in
`brief` and `digest` modes. Loaded at the Phase-2 signal-composition
step.

```text
The skill only sees Linear data; PTO, dependencies, conscious
deprioritization may explain things.
```

Hard rule (spec section 9, rule 7): this string is rendered verbatim
from this file. Edits to wording require updating audit fixtures
that assert byte-equality.
````

- [ ] **Step 7: Validate templates lint clean**

```bash
pnpm lint
```

Expected: exits 0.

- [ ] **Step 8: Commit**

```bash
git add skills/linearazor/assets/
git commit -m "feat(linearazor): scaffold skill dir and signal-layer asset templates"
```

---

## Phase 2 — Signal-layer references

Each reference is a focused, stage-3 document loaded at one specific step in the `SKILL.md` pipeline. Keep each file under 200 lines. Declarative voice (descriptions of rules + tables), not imperatives.

### Task 2: Write `references/signals.md`

**Files:**

- Create: `skills/linearazor/references/signals.md`

**Source spec sections:** 6.1–6.7 (signal model: shipped, questions, changes, stalls, quality, retrospective, lookahead).

- [ ] **Step 1: Write the file**

Transcribe the six signal definitions from spec section 6 into a declarative reference. Structure:

````markdown
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
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/signals.md
git commit -m "feat(linearazor): signal detection rules reference"
```

---

### Task 3: Write `references/signal-modes.md`

**Files:**

- Create: `skills/linearazor/references/signal-modes.md`

**Source spec sections:** 7.1 (modes and shapes), 7.2 (ordering and bounds), 7.3 (exec summary), 7.4 (disclaimer footer), 3.1 (mode phrasing).

- [ ] **Step 1: Write the file**

````markdown
# Signal-layer render modes

What the signal layer renders for each mode. The presentation layer
([presentation.md](./presentation.md)) handles palette, animation, and
flourishes. This reference covers structure only: which signal blocks
appear, in what order, with what bounds.

## Modes

| Mode | Mood line | Exec summary | Per-project briefs | Lookahead | Footer |
| --- | --- | --- | --- | --- | --- |
| `brief` | yes | no | no — counts only | suppressed | no |
| `digest` | optional (off with `no-mood`) | one-line counts | shipped + new stalls + new changes | one-liner per project | thresholds line |
| full ritual | yes | yes | shipped → questions → changes → stalls → quality | own section after per-project blocks | thresholds + disclaimer |
| `share` | full ritual content | full ritual | full ritual | full ritual | full ritual |

The `share` mode renders the full ritual brief and then exports it via
`charmbracelet/freeze` — see [presentation.md](./presentation.md) section
"Share as image."

## Phrasing-to-mode routing

`SKILL.md` parses the user message into a mode. The phrasing table:

| User phrasing | Mode | Notes |
| --- | --- | --- |
| `linearazor` | full ritual | default scope, default horizon |
| `linearazor for <group>` | full ritual | saved scope by group name |
| `linearazor for <member>` | full ritual, member-filtered | narrow to one member |
| `linearazor on <project>` | full ritual, project-filtered | narrow to one project |
| `linearazor digest` | digest | slim daily shape |
| `linearazor brief` | brief | mood line + counts only |
| `linearazor share` | share | render + freeze PNG |
| `linearazor reconfigure` | setup | interactive scope flow |
| `linearazor since <date>` | full ritual, anchor override | overrides horizon anchor |
| `linearazor lookahead off` | (modifier) | suppresses lookahead for this run |
| `linearazor lookahead 2` | (modifier) | look two tiers ahead |

Filter composition: `linearazor for <member> on <project>` intersects
the two slices. Filters compose as set intersection — no special-case
prose.

## Block ordering within a per-project brief

Signal lanes appear in this fixed order:

1. shipped
2. questions
3. changes
4. stalls
5. quality
6. retrospective (when triggered)

Within a lane, order issues by recency of the relevant event:

- `shipped`: `completedAt` descending.
- `stalls`: `daysInStatus` descending.
- `questions`, `changes`, `quality`: source-order in the fact sheet.

## Lookahead placement

The lookahead block follows the per-project blocks and precedes the
disclaimer footer. Within the block, `lookaheadIssues` precede
`lookaheadMilestones`. Order by `daysToTarget` ascending (closest
target first).

## Bounds

- Per-project sections cap at 12. Overflow appends one line:
  `N more projects in scope; narrow with "linearazor on <project>"`.
- No per-signal cap within a project block — projects with many stalls
  surface them all. The 12-project cap is the only bound.
- Lookahead unclarities cap at 8 per project. Overflow appends
  `N more lookahead unclarities — consider triaging the next milestone`.

## Exec summary

A single line at the top of the full-ritual output, after the mood
line. Lists per-signal counts across the primary horizon only — no
lookahead counts.

Format:

```text
Across <N> projects: <S> shipped · <T> stalls · <Q> questions · <C> changes
```

Suppressed in `brief` and `digest` modes (brief is counts; digest leads
with per-project shipped).

## Disclaimer footer

Renders the literal string from [`assets/footer.md`](../assets/footer.md)
once per run. Full-ritual and `share` modes only. Suppressed in `brief`
and `digest`. Hard rule 7 binds.

## Mode-by-mode rendering details

### brief

Single output block, no per-project subdivisions. Shape:

```text
<mood line>
Across <N> projects: <S> shipped · <T> stalls · <Q> questions · <C> changes
```

Slack-paste shape. No animation cast. No flourishes.

### digest

```text
<mood line>           # suppressed with `no-mood`
<exec summary line>

<project name>: <S> shipped · <T> new stalls · <C> new changes
  • <new-stall-1>
  • <new-stall-2>
[...]

Lookahead: <project-name> "<milestone>" — 0 started, <N>d to target
[...]

Thresholds: aging <N>d, silent <N>d, no-PR <N>d.
```

"new" stalls / "new" changes in digest mode = items not present in the
previous digest output. Since linearazor is stateless, "new" is
detected by comparing the current fact sheet's signal IDs against a
list of IDs maintained in Linear itself (via project-update tracking
referenced from comments). When that mechanism isn't available, treat
every emitted item as new and document the limitation.

### full ritual

Full structure per spec section 7 (signal layer) and 8.7 (combined
sketch).

### share

Same content as full ritual. The signal layer treats `share` and full
ritual identically; the presentation layer's `share` step pipes the
output to `freeze`.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/signal-modes.md
git commit -m "feat(linearazor): signal-layer render modes reference"
```

---

### Task 4: Write `references/tone.md`

**Files:**

- Create: `skills/linearazor/references/tone.md`

**Source spec sections:** 9 (hard rules 3, 4, 5, 8, 9), 6.2 (question patterns), 7.1 (modes).

- [ ] **Step 1: Write the file**

````markdown
# Tone rules

The blameless, signals-not-verdicts voice. Loaded by Phase-2 signal
composition and by every parallel sub-agent. Phrasing rules apply
across all signal lanes.

## Subject-on-issue, never subject-on-person

Hard rule 3 binds: findings name behaviors and identifiers, never
authors.

| Wrong | Right |
| --- | --- |
| "Bob hasn't moved ENG-423 since Monday." | "ENG-423 has been In Progress 11 days." |
| "Carol is behind on the runtime milestone." | "Two issues attached to the runtime milestone are aging." |
| "@bob.wu owns this stall." | "ENG-446 has no PR linked." |
| "The team is slipping." | "Three milestones moved this cycle." |

Forbidden tokens in any emitted prose outside the setup-health footer:

- Any configured member display name.
- Any `@`-prefixed handle.
- Pronouns referring to a person — `they`, `their`, `she`, `he`,
  `his`, `her`, `them`. (Pronouns referring to issues / projects /
  milestones are fine: "ENG-423 has been In Progress 11 days; its
  blocker closed Tuesday.")

**Audit:** grep the rendered prose for the configured member display
names. Any match outside the literal setup-health footer is a
violation. The setup-health footer is the only place member names
appear (and only when name resolution failed).

## Signals, not verdicts

Hard rule 4 binds: no red/yellow/green markers, no severity prefixes,
no judgment vocabulary.

Forbidden tokens:

- Severity vocabulary: `CRITICAL`, `AT RISK`, `BEHIND SCHEDULE`,
  `FAILING`, `BLOCKED` (as a prefix label — the actual `Blocked`
  status from Linear is fine in factual context).
- Decoration: red/yellow/green dots, traffic lights, severity badges.
- Emoji other than the optional razor glyph in the run header
  (hard rule 6).

| Wrong | Right |
| --- | --- |
| "⚠️ ENG-423 AT RISK — 11 days in progress." | "ENG-423  In Progress 11 days  (default threshold: 7)" |
| "Milestone "May runtime cut" is BEHIND SCHEDULE." | `Milestone "May runtime cut" moved from May 14 -> May 21` |
| "🔴 Stall." | `<cow animal in Peach>` (presentation layer) plus the factual stall line. |

**Audit:** grep over the output for `CRITICAL|AT RISK|BEHIND|FAILING|❌|⚠️|🔴|🟡|🟢`. Any match is a violation.

## Questions are questions

Hard rule 5 binds: every line in the questions block ends with `?`.
Same rule for lookahead unclarities rendered as questions (when the
signal source is "no acceptance criteria" with a question framing).

| Wrong | Right |
| --- | --- |
| "ENG-423 needs an update." | "What's the next concrete step on ENG-423, and is anything blocking it?" |
| "Check on the runtime milestone." | "Is the appetite for the runtime milestone still well-framed?" |

**Audit:** lines in the questions block must match `\?\s*$`.

## Celebrate first

Hard rule 8 binds: each per-project block opens with shipped or the
literal `No completions in window` — never with stalls.

| Wrong | Right |
| --- | --- |
| Block opens with `Stalls:` ahead of `Shipped:`. | Block opens with `Shipped:` (or `No completions in window`), then questions, changes, stalls, quality. |

## No scoring, no streaks, no leaderboards

Hard rule 9 binds: the mood line counts animals as flavor; the brief
never tallies them across runs as metrics. There is no state file in
which to persist counters — the rule is structurally enforced.

| Wrong | Right |
| --- | --- |
| "3rd consecutive week with zero stalls — great streak!" | "Three projects shipped this week and one is waiting on a question." |
| "Bob's velocity is up 20% over last cycle." | (No per-person framing. No cross-run comparison.) |

## Acknowledge missing context once

Hard rule 7 binds: full-ritual runs end with the literal disclaimer
string from [`../assets/footer.md`](../assets/footer.md). One line,
unmodified.

## Lookahead voice

Lookahead findings adopt the same tone rules. Unclarities lean toward
question phrasing when the signal source is "no clear definition of
done" — because asking a question is itself the action.

| Wrong | Right |
| --- | --- |
| "ENG-505 is underspecified." | "What does done look like for ENG-505?" |
| "Milestone slipping risk." | `"June runtime cut" — 0 started, 35d to target` |

## Retrospective voice

Retrospective lines are forward-looking only — "what would we want to
know earlier next time?" Never "what went wrong."

| Wrong | Right |
| --- | --- |
| "We missed the May runtime cut because Carol was overloaded." | "What signaled the May runtime cut was at risk that we could have caught earlier?" |
| "Should have caught the scope creep on ENG-470." | "What changed about our understanding of the runtime project that drove the scope changes this cycle? Was it the work or the framing?" |
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/tone.md
git commit -m "feat(linearazor): tone reference (signals-not-verdicts, never-name-the-person)"
```

---

### Task 5: Write `references/horizon-and-scope.md`

**Files:**

- Create: `skills/linearazor/references/horizon-and-scope.md`

**Source spec sections:** 3.2 (horizon), 3.3 (lookahead), 3.4 (scope), 3.5 (first-run / no-scope).

- [ ] **Step 1: Write the file**

````markdown
# Horizon, lookahead, and scope

Loaded at the "resolve scope plus horizon plus lookahead" step in the
`SKILL.md` pipeline. Defines how the primary horizon window, the
lookahead window, and the in-scope issue set are computed.

## Primary horizon

| Horizon | Window |
| --- | --- |
| `cycle` (default) | Current Linear cycle's start to end |
| `week` | Monday of current week to Friday |
| `2w` / `4w` | Today minus N weeks to today |
| `milestone` | Today to the next project milestone target date in scope |
| `since <date>` | The given date to today (overrides horizon anchor) |

If the user's phrasing is ambiguous and `default_horizon` is not set in
config, prompt once interactively. In non-interactive sessions, fall
back to `cycle` without prompting.

## Lookahead window (auto-tiered)

The lookahead window is always computed unless the user passes
`lookahead off` or the primary horizon is `since <date>` (which is
explicitly backward-facing).

| Primary horizon | Lookahead window |
| --- | --- |
| `cycle` | The next Linear cycle after the active one |
| `week` / `2w` / `4w` | Today's primary window-end plus the same window length |
| `milestone` | The milestone after the next-in-scope one |
| `since <date>` | Suppressed |

`lookahead 2` looks two tiers ahead instead of one — concatenate the
two windows for the lookahead set.

## In-scope set (primary horizon)

An issue is in scope when all apply:

- Belongs to the configured Linear team.
- Carries at least one of the configured labels (when `labels` is
  non-empty in config).
- Satisfies the composite horizon filter — at least one of:
  - Assigned to a cycle whose window intersects the primary horizon.
  - Attached to a milestone whose target date falls in the primary
    horizon.
  - Has a `dueDate` in the primary horizon window.
  - Was In Progress at any point in the primary horizon window
    (catches issues not bound to a cycle, milestone, or due date).

## Lookahead set

The lookahead set uses the same composite filter against the lookahead
window. Lookahead issues are tracked in `lookaheadIssues[]` separate
from `openIssues[]` — never bleed into the primary signal lanes (hard
rule 11).

## Filters that compose with horizon

The `for <member>` and `on <project>` modes narrow the in-scope set
after the horizon filter applies:

- `for <member>`: keep only issues where assignee OR creator matches
  the configured member identifier.
- `on <project>`: keep only issues whose `project.name` matches the
  given pattern (case-insensitive, substring).

Filters compose as set intersection. `linearazor for Bob Wu on
infra` narrows to issues both assigned to Bob and in the infra
project.

## First-run / no-scope behavior

When no config exists at `~/.config/linearazor/<group>.toml`:

- **Interactive session** (TTY present): enter the setup flow
  ([`setup-flow.md`](./setup-flow.md)).
- **Non-interactive session** (no TTY, harness loop): exit with the
  one-line message
  `no scope configured; ask the user to run "linearazor reconfigure"`.
  Hard rule 2 binds: never dump the workspace.

When the user passes an explicit `--scope <group>` and that group is
not configured, treat it the same as no-scope: setup or exit.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/horizon-and-scope.md
git commit -m "feat(linearazor): horizon, lookahead, and scope rules reference"
```

---

### Task 6: Write `references/setup-flow.md`

**Files:**

- Create: `skills/linearazor/references/setup-flow.md`

**Source spec sections:** 3.5 (first-run / no-scope), 5 (Configuration), section 13 (open at implementation time — label pick-list source).

- [ ] **Step 1: Write the file**

````markdown
# Interactive setup flow

Loaded when no config exists at `~/.config/linearazor/<group>.toml` and
the session is interactive (TTY present). Reconfigure mode
(`linearazor reconfigure`) loads this same flow.

The flow is conversational — one question at a time, with skip
allowed for optional steps. Never proceeds with an unscoped run; if
the user refuses to scope, exit with a one-line explanation.

## Step 1: Detect workspace shape

Query Linear MCP for the list of teams. Two cases:

- **Multiple teams (≥ 2), each with a manageable member count
  (≤ 25):** present a pick list of teams. Continue with the chosen
  team. Skip to Step 3.
- **Exactly one team, OR a single team with many members (> 25):**
  the workspace is tag-partitioned. Continue with the only team (or
  ask the user to confirm the partition assumption) and ask for a
  working-group name in Step 2.

## Step 2: Ask for a working-group name

Free text. Becomes the config key (e.g. `infra`, `containers-blue`).
Validation: lowercase ASCII letters, digits, hyphens. 1–32 chars.
This is independent of Linear's team concept — it is the name of the
config file (`~/.config/linearazor/<group>.toml`).

## Step 3: Ask for member names

Free text. Comma- or newline-separated. Match each name against Linear
users by display name and email with fuzzy matching:

- **High-confidence match** (score ≥ 0.9, exact-or-near-exact on
  display name or email-local-part): include without per-line
  prompting. Show the full list at the end for a single confirmation.
- **Low-confidence match** (0.6 ≤ score < 0.9): show the best one to
  three candidates and ask "Which one (or none)?"
- **No match** (score < 0.6): list the name as unmatched. Offer:
  retry with a different name, skip, or accept the unmatched name
  (which will surface as a setup-health note in every brief).

No silent inclusion. Above-threshold matches are confirmed in a
single summary at the end of this step. Unresolved names are saved to
config exactly as entered.

## Step 4: Ask for project label scope (optional)

Query Linear MCP for labels on projects whose state is `started` or
whose latest milestone target date is within the next 60 days.
Present these as a pick list (suggestion). Allow free text. Multiple
labels allowed.

Skip allowed — when no labels are set, the in-scope filter does not
apply the label clause.

## Step 5: Ask for default horizon

Default `cycle`. Pick list: `cycle`, `week`, `2w`, `4w`, `milestone`.

## Step 6: Offer to persist

Show the rendered config (full TOML). Ask "Save to
`~/.config/linearazor/<group>.toml`?" Two paths:

- **Yes:** create the directory if needed
  (`mkdir -p ~/.config/linearazor`), write the file, confirm path.
- **No:** exit with a one-line note explaining how to manually save
  later (print the rendered TOML to stdout for copy-paste).

## Setup-health note

The first run after setup includes a setup-health line in the footer
listing unresolved names. Example:

```text
Setup health: 2 of 3 members resolved. Unresolved: "Bob 2".
```

This is the only place outside the disclaimer footer where member
names appear in the output.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/setup-flow.md
git commit -m "feat(linearazor): interactive setup flow reference"
```

---

### Task 7: Write `references/ingest-and-factsheet.md`

**Files:**

- Create: `skills/linearazor/references/ingest-and-factsheet.md`

**Source spec sections:** 4.1 (Phase 1 ingest), 13 (open at implementation time — Linear MCP probe).

- [ ] **Step 1: Write the file**

````markdown
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
2. **Resolve horizon and lookahead windows.** See
   [horizon-and-scope.md](./horizon-and-scope.md).
3. **Query in-scope issues** for the primary horizon. Composite filter
   from [horizon-and-scope.md](./horizon-and-scope.md) "In-scope set".
4. **Fetch per-issue details** (one MCP call per page; batch as
   permitted): status, status history, assignee, last comment
   timestamp, linked PR URLs, blocker / blocking relations, project,
   milestone, due date, label set, title, body.
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
10. **Emit fact sheet** as a single JSON-shaped structure conforming
    to [`../assets/factsheet-template.yaml`](../assets/factsheet-template.yaml).

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
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/ingest-and-factsheet.md
git commit -m "feat(linearazor): Phase 1 ingest and fact-sheet reference"
```

---

### Task 8: Write `references/parallel-dispatch.md`

**Files:**

- Create: `skills/linearazor/references/parallel-dispatch.md`

**Source spec sections:** 4.2 (Phase 2), 9 (hard rule 10).

- [ ] **Step 1: Write the file**

````markdown
# Parallel dispatch (more-than-6-projects branch)

Loaded at the "decide single-pass vs parallel" step in Phase 2. Defines
when to dispatch parallel sub-agents and how to compose their outputs.

## Branching rule

- `factSheet.projects.length ≤ render.parallel_project_threshold`
  (default 6): single-pass. One model call reads the full fact sheet
  and produces all per-project briefs plus the exec summary plus the
  mood line.
- Above the threshold: parallel sub-agents — one per project — draft
  the per-project briefs. The main agent then composes the exec
  summary, the lookahead block (if present), the mood line, and the
  footer.

The threshold is configurable in `[render]` (`parallel_project_threshold`).
Default 6.

## Sub-agent prompt skeleton

Each sub-agent receives:

- Its project's slice of the fact sheet
  (`factSheet.projects[i]` plus the envelope fields).
- The signal-detection rules ([signals.md](./signals.md)).
- The tone rules ([tone.md](./tone.md)).
- The animation cast for its lanes
  ([../assets/animation.md](../assets/animation.md)).

The sub-agent produces a single per-project block following the
ordering in [signal-modes.md](./signal-modes.md). It does **not**
produce the exec summary, the lookahead block, the mood line, or the
footer — those are composed by the main agent over all sub-agent
outputs.

## Hard separation

Sub-agents never query Linear MCP. Hard rule 10 binds: if a sub-agent
wants a fact not in its slice of the fact sheet, that is a Phase-1
gap. The fix is upstream, not a side-channel query.

**Audit:** sub-agent prompts in this file contain no instructions to
call `mcp__linear__*` tools.

## Composition

The main agent reads all per-project drafts and:

1. Filters per-project blocks by the project-section cap
   ([signal-modes.md](./signal-modes.md) "Bounds").
2. Composes the exec summary from primary-horizon signal counts only.
3. Composes the lookahead block from
   `factSheet.projects[*].lookaheadIssues` and `lookaheadMilestones`
   per the lookahead rules in [signals.md](./signals.md).
4. Composes the mood line per [mood-line.md](./mood-line.md).
5. Appends the disclaimer footer from
   [`../assets/footer.md`](../assets/footer.md) (full-ritual / share
   only).

## Cross-project ordering

Project sections appear in this order:

- Projects with shipped activity first (more shipped → earlier).
- Then projects with stalls (more stalls → earlier).
- Then projects with no signals (rare; only when in-scope by
  membership).

Tiebreaker: project name alphabetical.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/parallel-dispatch.md
git commit -m "feat(linearazor): parallel-dispatch reference (>6 projects branch)"
```

---

## Phase 3 — Presentation-layer references and animation cast

The presentation layer is revisable in isolation. Commits in this phase
must not touch signal-layer files (hard rule 12).

### Task 9: Write `references/palettes.md`

**Files:**

- Create: `skills/linearazor/references/palettes.md`

**Source spec sections:** 8.1 (palette and color).

- [ ] **Step 1: Write the file**

````markdown
# Palettes

Loaded at the Phase-2 presentation step. Bundled named palettes plus
the role mapping that survives across palettes.

## Resolution order

At render time, the palette is chosen in this order — first hit wins:

1. `LINEARAZOR_PALETTE=<name>` env var.
2. Config `[render].palette` name.
3. Per-role overrides in `[render.palette_overrides]` (any role can
   be remapped to a different role name or a hex literal).
4. Built-in defaults for the selected palette.

`NO_COLOR=1` is absolute — bypasses all of the above and renders plain
ASCII. See [presentation.md](./presentation.md) "TTY and NO_COLOR."

## Roles

Role names are palette-independent. Every shipped palette assigns the
same roles to its accents — only the hues change.

| Role | What it colors |
| --- | --- |
| `shipped` | Shipped lead-in, momentum, bee animal |
| `questions` | Questions lane, cat animal, `→` flourish |
| `changes_scope` | Scope-change lines, penguin animal |
| `changes_date` | Date-move lines, snake animal |
| `stalls_aging` | Aging-WIP stall lines, cow animal |
| `stalls_no_pr` | No-PR-linked stall lines, snail animal |
| `stalls_silent` | Silent stall lines, turtle animal |
| `stalls_blocked` | Blocked-without-blocker stall lines, fish animal |
| `quality` | Quality lines, bat animal |
| `retrospective` | Retrospective block, dog animal |
| `lookahead` | Lookahead block headings and milestone lines |
| `metadata` | Dim context — file paths, timestamps, footer text |

## Bundled palettes

### catppuccin-mocha (default)

Truecolor. Source: <https://github.com/catppuccin/catppuccin>.

| Role | Hex |
| --- | --- |
| `shipped` | `#a6e3a1` (green) |
| `questions` | `#b4befe` (lavender) |
| `changes_scope` | `#fab387` (peach) |
| `changes_date` | `#cba6f7` (mauve) |
| `stalls_aging` | `#fab387` (peach) |
| `stalls_no_pr` | `#fab387` (peach) |
| `stalls_silent` | `#74c7ec` (sapphire) |
| `stalls_blocked` | `#9399b2` (overlay2) |
| `quality` | `#89dceb` (sky) |
| `retrospective` | `#cba6f7` (mauve) |
| `lookahead` | `#89dceb` (sky) |
| `metadata` | `#7f849c` (overlay1) |

### catppuccin-latte

Light-terminal mirror.

| Role | Hex |
| --- | --- |
| `shipped` | `#40a02b` (green) |
| `questions` | `#7287fd` (lavender) |
| `changes_scope` | `#fe640b` (peach) |
| `changes_date` | `#8839ef` (mauve) |
| `stalls_aging` | `#fe640b` (peach) |
| `stalls_no_pr` | `#fe640b` (peach) |
| `stalls_silent` | `#209fb5` (sapphire) |
| `stalls_blocked` | `#8c8fa1` (overlay2) |
| `quality` | `#04a5e5` (sky) |
| `retrospective` | `#8839ef` (mauve) |
| `lookahead` | `#04a5e5` (sky) |
| `metadata` | `#9ca0b0` (overlay1) |

### solarized-dark

Source: <https://ethanschoonover.com/solarized/>.

| Role | Hex |
| --- | --- |
| `shipped` | `#859900` (green) |
| `questions` | `#268bd2` (blue) |
| `changes_scope` | `#cb4b16` (orange) |
| `changes_date` | `#6c71c4` (violet) |
| `stalls_aging` | `#cb4b16` (orange) |
| `stalls_no_pr` | `#cb4b16` (orange) |
| `stalls_silent` | `#2aa198` (cyan) |
| `stalls_blocked` | `#586e75` (base01) |
| `quality` | `#2aa198` (cyan) |
| `retrospective` | `#6c71c4` (violet) |
| `lookahead` | `#2aa198` (cyan) |
| `metadata` | `#586e75` (base01) |

### tokyo-night

Source: <https://github.com/folke/tokyonight.nvim>.

| Role | Hex |
| --- | --- |
| `shipped` | `#9ece6a` (green) |
| `questions` | `#bb9af7` (purple) |
| `changes_scope` | `#ff9e64` (orange) |
| `changes_date` | `#7aa2f7` (blue) |
| `stalls_aging` | `#ff9e64` (orange) |
| `stalls_no_pr` | `#ff9e64` (orange) |
| `stalls_silent` | `#7dcfff` (cyan) |
| `stalls_blocked` | `#565f89` (comment) |
| `quality` | `#7dcfff` (cyan) |
| `retrospective` | `#bb9af7` (purple) |
| `lookahead` | `#7dcfff` (cyan) |
| `metadata` | `#565f89` (comment) |

### monochrome

One accent plus dim. For terminals with limited color support or for
users who want minimal color.

| Role | Hex |
| --- | --- |
| All non-metadata roles | `#ffffff` (bold) |
| `metadata` | `#777777` (dim) |

Layer accent via bold or underline rather than hue.

## Hex literal overrides

Any role in `[render.palette_overrides]` accepts:

- A role name from the selected palette (`shipped = "rosewater"` →
  use rosewater for the shipped role).
- A hex literal (`shipped = "#f9e2af"`).

Validation: hex literals must match `^#[0-9a-fA-F]{6}$`. Anything else
is rejected with a one-line config error.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/palettes.md
git commit -m "feat(linearazor): palette reference (5 named palettes, role mapping)"
```

---

### Task 10: Write `references/presentation.md`

**Files:**

- Create: `skills/linearazor/references/presentation.md`

**Source spec sections:** 8.1 (palette routing), 8.4 (flourishes), 8.5 (TTY and NO_COLOR), 8.6 (share as image).

- [ ] **Step 1: Write the file**

````markdown
# Presentation layer

Loaded at the Phase-2 presentation step, after the signal layer has
composed the brief. Defines palette routing, animation placement,
Unicode flourishes, the TTY/NO_COLOR contract, and the `share` mode's
PNG export.

## Palette routing

Resolve the active palette per [palettes.md](./palettes.md). For each
emitted line, identify its signal role (from the signal-layer output)
and wrap the role's anchor text in the palette's ANSI escape for that
role.

What gets colored:

- **Project names** (in per-project headers).
- **Numbers** (`11 days`, `8d to target`).
- **Verbs** that carry the signal (`shipped`, `moved`, `silent`).
- **Identifiers** (`ENG-423`) — bold default Text role, not a colored
  accent.

What stays plain:

- Prose. Sentences are not colored.
- Punctuation, divider characters, spaces.

Rule of thumb: a single line carries one or two colored tokens. More
than three colored tokens on a line is a presentation-layer bug.

## Animation placement

The animation cast lives in [`../assets/animation.md`](../assets/animation.md).
One animal per signal category per per-project section — not one per
item.

For each signal lane that has at least one finding in the current
per-project block, render the animal once at the top of that lane,
left-aligned with two-space indent, before the finding lines. All
animals face right toward the finding list below.

If a signal lane is empty, no animal renders for that lane.

## Unicode flourishes

One Unicode flourish max per line — never decorative, always
load-bearing:

| Glyph | Role | Meaning | ASCII fallback |
| --- | --- | --- | --- |
| `◇` | Lead stall / lookahead-unclarity line | "Noticed thing" | `*` |
| `→` | Lead question line | "Where does this point" | `>` |
| `─` `├` `└` `│` | Section dividers, run header frame | Visual scaffolding | `-` `+` `+` `|` |
| `•` | Shipped-list bullet | "Item" | `*` |

ASCII fallback is used when `[ -t 1 ]` is false (not a TTY) OR
`$NO_COLOR` is set.

## TTY and NO_COLOR

Detection at render entry:

```bash
if [ -t 1 ] && [ -z "$NO_COLOR" ]; then
  USE_ANSI=1
else
  USE_ANSI=0
fi
```

When `USE_ANSI=0`:

- ANSI escapes are not emitted (plain ASCII output).
- Unicode flourishes degrade to ASCII per the table above.
- Animation cast still renders (ASCII is the medium of the cast
  anyway).
- Mood line, exec summary, all signals — content identical.

The principle: piped output is byte-identical to TTY output minus
ANSI escapes and Unicode flourishes. Audit by piping a `share` PNG
render's text version against a `>file` redirect of the TTY render
with ANSI stripped — they must match.

## Share as image

The `share` mode renders the full ritual brief, then exports it as a
carbon-style PNG (or SVG) via
[`charmbracelet/freeze`](https://github.com/charmbracelet/freeze).

### Detection and fallback

At the start of `share` mode, check `freeze` is on `$PATH`:

```bash
command -v freeze >/dev/null 2>&1
```

- **Present:** proceed with the freeze pipeline.
- **Absent:** print the one-line install hint and write a markdown
  fallback (the full ritual brief as plain markdown) to the same
  output path, with the file extension `.md` instead of `.png`. Never
  silently install. Never error out — the user always gets a
  shareable artifact.

Install hint:

```text
freeze not found. Install with:
  brew install charmbracelet/tap/freeze
  # or
  go install github.com/charmbracelet/freeze@latest
Falling back to markdown export at <path>.md
```

### Freeze invocation

The pipeline (illustrative — pin flags at implementation time):

```bash
RENDER_OUT="${TMPDIR:-/tmp}/linearazor-<group>-<date>.png"
linearazor_render | freeze \
  --language ansi \
  --output "$RENDER_OUT" \
  --background "$PRIMARY_BG" \
  --font.family "JetBrains Mono" \
  --font.size 13 \
  --padding 24
echo "$RENDER_OUT"
```

`$PRIMARY_BG` is the background hex from the active palette. For
`catppuccin-mocha`, `#1e1e2e` (base). For palettes without an
explicit background hex, default to black (`#000000`).

### SVG variant

`linearazor share --svg` substitutes `--output` to `.svg`. SVG is
sharper and scales but does not always preview inline in Slack.

### Audit

The plain-text dump from `freeze --output text` (when supported) over
a `share` invocation must be byte-identical to the same brief rendered
to a TTY-fallback file via redirection.

## Layer-separation contract

Changes in this file (or any file under "Presentation layer" in
[the file layout](../../docs/superpowers/specs/2026-05-13-linearazor-design.md#10-file-layout))
must not require edits to any signal-layer reference, asset, or audit
fixture. Hard rule 12 binds.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/presentation.md
git commit -m "feat(linearazor): presentation-layer reference (palette routing, share-as-image)"
```

---

### Task 11: Write `references/mood-line.md`

**Files:**

- Create: `skills/linearazor/references/mood-line.md`

**Source spec sections:** 8.3 (mood line), 9 (hard rule 9 — no scoring).

- [ ] **Step 1: Write the file**

````markdown
# Mood line

Loaded at the Phase-2 presentation step. The mood line is one
sentence at the top of the full-ritual output, in the tool's voice.
Animals serve as a unit of measure when they appear in the line.

## Voice

Specific, observational, light. Names what is in the brief without
verdicts.

Exemplars (the model should imitate this register):

```text
Three cows in the field this week, one bee, and a cat with a good question.
```

```text
Two bees this cycle — the field is quiet, but the snail on ENG-446
is worth a look.
```

```text
A dog this morning — looking back at the May runtime cut so the June
one doesn't end the same way.
```

```text
A snake and three penguins — the runtime project is changing shape
faster than it's moving.
```

```text
A bat and two questions — the next cycle has acceptance criteria
to nail down.
```

## Constraints (presentation-layer rules, not signals)

Hard rule 9 binds. No scoring, no streaks, no leaderboards. Forbidden
patterns:

| Wrong | Right |
| --- | --- |
| "Best week yet — 8 bees!" | "Three bees and a cow this week." |
| "Stall count up 30% from last cycle." | "Three cows in the field — worth a chat about ENG-423 and ENG-446." |
| "Bob: 4 bees · Carol: 3 bees" | (No per-person framing in the mood line.) |
| "🐝🐝🐝🐝" | (No emoji. Color and prose carry the cast.) |

The brief never tallies animals across runs as metrics. There is no
state file in which to persist counters — the rule is structurally
enforced.

## Suppression

`linearazor` invocations with `no-mood` suppress the mood line:

| Mode | Default | With `no-mood` |
| --- | --- | --- |
| `brief` | mood line present | suppressed |
| `digest` | mood line present | suppressed |
| full ritual | mood line present | suppressed |
| `share` | mood line present | suppressed |

## Composition input

The mood line is generated last in the Phase-2 pipeline, after all
per-project blocks and the lookahead block are composed. The model
sees the full draft brief and selects animal references that actually
appear in the rendered output — never invents a unit not present.

**Audit:** every animal name appearing in the mood line must appear
in at least one per-project block or the lookahead block of the same
run.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/references/mood-line.md
git commit -m "feat(linearazor): mood line reference (voice exemplars, constraints)"
```

---

### Task 12: Write `assets/animation.md` — the cast

**Files:**

- Create: `skills/linearazor/assets/animation.md`

**Source spec sections:** 8.2 (animation cast).

This is the cast file. Eleven lane-mapped animals (bee, cat, cow,
snail, turtle, fish, penguin, snake, bat, dog, spider) plus two
special-case mascots (duck for setup/welcome, puzzled face for the
empty-brief case). Sourced from established ASCII art rather than
freehand; the original spec's "all face right, 4–6 lines, 12–20
columns" rule is relaxed to accept the canonical art as-is.

- [ ] **Step 1: Write the file**

````markdown
# Animation cast

Eleven ASCII animals, one per signal lane. Sourced from established
ASCII art rather than freehand.

One animal per signal category per per-project section, never one per
item. Color via the palette role in the heading — see
[../references/palettes.md](../references/palettes.md).

The cast deliberately mixes facing directions and sizes. The earlier
"all face right, 4-6 lines, 12-20 columns" rule was an aspiration;
the canonical art doesn't all conform, and the canonical art is the
point.

## Cast

### Bee — `shipped`

Active, momentum, just shipped. Motion lines trail right.

```text
              _   _
             ( | / )
           \\ \|/,'_
           (")(_)()))=-
              <\\
```

### Cat — `questions`

Sitting, curious, alert.

```text
 /\_/\
( o.o )
 > ^ <
```

### Cow — `stalls_aging`

Standing in a field of grass — head down, plodding.

```text
\|/          (__)
     `\------(oo)
       ||    (__)
       ||w--||     \|/
   \|/
```

### Snail — `stalls_no_pr`

Slow, antennae up, leaves no trail.

```text
    .----.   @   @
   / .-"-.`.  \v/
   | | '\ \ \_/ )
 ,-\ `-.' /.'  /
'---`----'----'
```

### Turtle — `stalls_silent`

Withdrawn, shell-textured, head still extended but quiet.

```text
                    __
         .,-;-;-,. /'_\
       _/_/_/_|_\_\) /
     '-<_><_><_><_>=/\
       `/_/====/_/-'\_\
        ""     ""    ""
```

### Fish — `stalls_blocked`

Small fish trailed by a larger one — surrounded, not moving forward.

```text
               O  o
          _\_   o
>('>   \\/  o\ .
       //\___=
          ''
```

### Penguin — `changes_scope`

Stands sentinel, eye spotting the change.

```text
         __
      -=(o '.
         '.-.\
         /|  \\
         '|  ||
          _\_):,_
```

### Snake — `changes_date`

Sinuous, shape-shifting, the milestone date moving.

```text
             ____
            / . .\
            \  ---<
             \  /
   __________/ /
-=:___________/
```

### Bat — `quality`

Wings out, alert, watching for what's missing.

```text
        _   ,_,   _
       / `'=) (='` \
      /.-.-.\ /.-.-.\
      `      "      `
```

### Dog — `retrospective`

Looking back, loyal, the run that just ended.

```text
  __      _
o'')}____//
 `_/      )
 (_(_/-(_/
```

### Spider — `scope drift`

Eight-legged, sideways and multidirectional, the scope creeping out.

```text
 ||  ||
 \\()//
//(__)\\
||    ||
```

## Setup mascot

The duck appears only in the setup flow ([`../references/setup-flow.md`](../references/setup-flow.md))
and in the first ritual run after a fresh `reconfigure`. It is not
tied to a signal lane and never appears in normal brief output.

```text
    __
___( o)>
\ <_. )
 `---'
```

## Empty-brief mascot

The puzzled face appears only when the ritual runs but every signal
lane comes up empty across every in-scope project — nothing shipped,
no questions, no changes, no stalls, no quality findings. Replaces
the mood line in that case; the per-project blocks are suppressed
since they would all be `No completions in window`.

```text
       .--.
      / o o \
     |   ^   |
      \ --- /
```

## Lane → animal table

| Role | Animal |
| --- | --- |
| `shipped` | Bee |
| `questions` | Cat |
| `stalls_aging` | Cow |
| `stalls_no_pr` | Snail |
| `stalls_silent` | Turtle |
| `stalls_blocked` | Fish |
| `changes_scope` | Penguin |
| `changes_date` | Snake |
| `quality` | Bat |
| `retrospective` | Dog |
| `scope drift` | Spider |

## Replacement

The cast is purely affective. Replacing an animal, changing its pose,
or adding a new one is a presentation-layer change — no signal-layer
file needs updating. Hard rule 12 binds.

## Audit

- Each lane has exactly one animal in the cast.
- One animal per signal category per per-project section (never one
  per item).
- No emoji anywhere in this file.

## Provenance (TODO)

Known artists to credit when the attribution pass happens: Joan G.
Stark (`jgs`) — turtle, bat; Shanaka Dias (`snd`) — penguin; Hayley
Wakenshaw (`hjw`) — duck; Stef00 — bee. The cat, cow, snail, fish,
snake, dog, spider, and puzzled-face pieces come from uncredited
canonical forms in the ASCII commons.
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/assets/animation.md
git commit -m "feat(linearazor): animation cast (12 ASCII animals)"
```

---

## Phase 4 — Entry point and human-facing surfaces

### Task 13: Write `SKILL.md`

**Files:**

- Create: `skills/linearazor/SKILL.md`

**Source spec sections:** all (the entry point indexes everything).

The `SKILL.md` is the lean entry point — target ≤ 250 lines (well
under the 500-line cap). Imperative voice. Reference index pulls each
reference at the step that needs it.

- [ ] **Step 1: Write the file**

````markdown
---
name: linearazor
description: Reads a scoped Linear workspace via Linear MCP and produces per-project briefs framed as questions a thoughtful teammate would ask, with four signals (questions, scope/date changes, stalls, clarity gaps), a shipped lead-in, a tiered lookahead, a mood line, and a hand-drawn ASCII animation cast. Invoke when the user says "linearazor", "linearazor for <group>", "linearazor digest", "linearazor brief", "linearazor share", "linearazor for <member>", "linearazor on <project>", "linearazor reconfigure", "weekly Linear brief", or "what shipped in Linear this week". Read-only.
license: MIT
compatibility: Requires Linear MCP installed and authenticated. Optional: charmbracelet/freeze for share-as-image mode.
---

# linearazor

Reads a scoped Linear workspace via Linear MCP and produces a per-project
brief built around four signals — open questions, scope and date
changes, stalls, and clarity gaps — preceded by a shipped lead-in per
project and a cross-cutting exec summary at the top. Read-only; never
edits files or Linear.

## Install

```bash
npx skills add xornivore/skills@linearazor --agent claude-code -y
```

Requires Linear MCP. Install command:

```bash
claude mcp add linear --transport sse https://mcp.linear.app/sse
```

Optional for `share` mode: `brew install charmbracelet/tap/freeze`.

## When to use

Invoke when the user:

- Uses an explicit phrase: `linearazor`, `linearazor for <group>`,
  `linearazor digest`, `linearazor brief`, `linearazor share`,
  `linearazor reconfigure`.
- Adds a filter: `linearazor for <member>`, `linearazor on <project>`.
- Asks for a periodic project-board review: "weekly Linear brief",
  "what shipped in Linear this week", "what's stalled this cycle",
  "team retrospective for the runtime cut".

Do not invoke for:

- Writing to Linear (creating issues, updating status, posting
  comments). linearazor is read-only.
- Per-individual judgments. linearazor produces team-level prose.
- Velocity, sprint, or story-point reporting.

## Mode routing

When invoked, parse the user message into a mode plus optional filters
per [signal-modes.md](./references/signal-modes.md). The mode table:

| User phrasing | Mode |
| --- | --- |
| `linearazor` | full ritual, default scope |
| `linearazor for <group>` | full ritual, named scope |
| `linearazor for <member>` | full ritual, member-filtered |
| `linearazor on <project>` | full ritual, project-filtered |
| `linearazor digest` | digest |
| `linearazor brief` | brief |
| `linearazor share` | share (PNG export) |
| `linearazor reconfigure` | setup flow |
| `linearazor since <date>` | full ritual, anchor override |
| `linearazor lookahead off` | (modifier) suppress lookahead |
| `linearazor lookahead 2` | (modifier) look two tiers ahead |

Filters compose as set intersection.

## Pipeline

When invoked (any non-setup mode), do:

1. **Resolve scope.** Read `~/.config/linearazor/<group>.toml`.
   If absent and the session is interactive, route to the setup flow
   ([setup-flow.md](./references/setup-flow.md)). If absent and the
   session is non-interactive, exit with `no scope configured; ask
   the user to run "linearazor reconfigure"` and stop.
2. **Resolve horizon and lookahead.** See
   [horizon-and-scope.md](./references/horizon-and-scope.md).
3. **Phase 1 ingest.** Query Linear MCP per
   [ingest-and-factsheet.md](./references/ingest-and-factsheet.md).
   Emit the fact sheet (template at
   [assets/factsheet-template.yaml](./assets/factsheet-template.yaml)).
4. **Decide dispatch.** If `factSheet.projects.length` is at most the
   configured threshold (default 6), single-pass. Else parallel
   sub-agents per [parallel-dispatch.md](./references/parallel-dispatch.md).
5. **Phase 2 signal composition.** Compose per-project blocks per
   [signals.md](./references/signals.md) and
   [signal-modes.md](./references/signal-modes.md). Apply
   [tone.md](./references/tone.md) to every emitted line.
6. **Phase 2 presentation.** Apply palette and animation per
   [presentation.md](./references/presentation.md),
   [palettes.md](./references/palettes.md),
   [mood-line.md](./references/mood-line.md), and
   [assets/animation.md](./assets/animation.md).
7. **Footer.** Append the literal disclaimer from
   [assets/footer.md](./assets/footer.md) (full-ritual and share
   modes only).
8. **Share-mode export.** If mode is `share`, pipe the rendered
   output to `freeze` per
   [presentation.md](./references/presentation.md) "Share as image."

Never re-query Linear MCP from Phase 2 (hard rule 10).

## Hard rules

These are non-negotiable. Each is tagged `[Signal]` or `[Presentation]`
so the layers can be revised independently.

1. **[Signal] Read-only.** Phase 1 issues only Linear MCP read queries.
   Never edit files in the user's working directory, never edit
   Linear, never execute shell commands against the user's repos.
   **Audit:** in any run, no Linear MCP write tool, no `Edit` or
   `Write` to anything outside `~/.config/linearazor/`, no `Bash`
   outside read-only commands.

2. **[Signal] Never invoke unscoped.** If no config exists and the
   session is non-interactive, exit with the one-line "no scope
   configured" message. In an interactive session, drop into the
   setup flow. Never dump the workspace.

3. **[Signal] Never name the person.** Findings name behaviors and
   identifiers, never authors. Forbidden patterns by example in
   [tone.md](./references/tone.md): `Bob hasn't…`, `Carol is
   behind…`, `@handle`. Replace with subject-on-issue prose.
   **Audit:** emitted prose grepped for the configured member display
   names returns nothing outside the setup-health footer.

4. **[Signal] Signals, not verdicts.** No red/yellow/green markers,
   no `CRITICAL` / `AT RISK` / `BEHIND SCHEDULE`, no severity
   prefixes. **Audit:** grep for `CRITICAL|AT RISK|BEHIND|FAILING`
   over the output returns nothing.

5. **[Signal] Questions are questions.** Every line in the questions
   block ends with `?`. Same rule for lookahead-unclarities rendered
   as questions. **Audit:** non-comment lines in the questions block
   match `\?\s*$`.

6. **[Presentation] No emoji except the optional razor glyph in the
   header.** Color carries the emotional work. **Audit:** strip
   ANSI, strip the run header — remaining bytes contain no characters
   in the Emoji property range.

7. **[Signal] Acknowledge missing context once.** Full-ritual runs
   end with one line: the literal disclaimer from
   [assets/footer.md](./assets/footer.md). Suppressed in `brief`
   mode. **Audit:** full-ritual output contains the literal string.

8. **[Signal] Celebrate first.** Each per-project block leads with
   shipped. If nothing shipped, the block opens with
   `No completions in window` — never with stalls.

9. **[Signal] No scoring, no streaks, no leaderboards.** The mood
   line counts animals as flavor; the brief never tallies them across
   runs as metrics. **Audit:** no persisted counter of animals,
   shipped, or stalls exists.

10. **[Signal] Never re-query Linear from Phase 2.** If Phase 2 needs
    a fact, it is missing from the fact sheet — a Phase-1 gap to fix
    in code. **Audit:** Phase-2 prompts in `references/` contain no
    instructions to call Linear MCP.

11. **[Signal] Lookahead never carries stall, shipped, or
    retrospective signals.** Issues in the lookahead window are
    surfaced only as unclarities or appetite-shape risks.

12. **[Presentation] Layer separation.** Presentation-layer changes
    (animation, palette, hex code, mood-line wording) must not alter
    any signal-layer rule or rendering bound.

## Reference index

| Pipeline step | Files pulled |
| --- | --- |
| Setup flow (interactive) | [setup-flow.md](./references/setup-flow.md), [assets/config-template.toml](./assets/config-template.toml) |
| Resolve scope + horizon + lookahead | [horizon-and-scope.md](./references/horizon-and-scope.md) |
| Phase 1 ingest | [ingest-and-factsheet.md](./references/ingest-and-factsheet.md), [assets/factsheet-template.yaml](./assets/factsheet-template.yaml) |
| Decide dispatch | [parallel-dispatch.md](./references/parallel-dispatch.md) |
| Phase 2 — signal composition | [signal-modes.md](./references/signal-modes.md), [signals.md](./references/signals.md), [tone.md](./references/tone.md), [assets/footer.md](./assets/footer.md) |
| Phase 2 — presentation | [presentation.md](./references/presentation.md), [palettes.md](./references/palettes.md), [mood-line.md](./references/mood-line.md), [assets/animation.md](./assets/animation.md) |

All references are one level deep from `SKILL.md`.
````

- [ ] **Step 2: Verify frontmatter has no angle brackets**

```bash
awk '/^---$/{c++; if(c==2) exit} c==1' skills/linearazor/SKILL.md | grep -nE '[<>]' || echo "OK no angle brackets in frontmatter"
```

Expected: `OK no angle brackets in frontmatter`.

- [ ] **Step 3: Verify file is under 250 lines**

```bash
wc -l skills/linearazor/SKILL.md
```

Expected: ≤ 250.

- [ ] **Step 4: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/SKILL.md
git commit -m "feat(linearazor): SKILL.md entry point"
```

---

### Task 14: Write per-skill `README.md`

**Files:**

- Create: `skills/linearazor/README.md`

**Source spec sections:** 1 (Summary), 2 (Differentiation).

- [ ] **Step 1: Write the file**

````markdown
# linearazor

> Read-only project-board reviewer for Linear, framed as questions a
> thoughtful teammate would ask. Signals, not verdicts.

## Install

```bash
npx skills add xornivore/skills@linearazor --agent claude-code -y
```

Requires Linear MCP:

```bash
claude mcp add linear --transport sse https://mcp.linear.app/sse
```

Optional for `share` mode (carbon-style PNG export):

```bash
brew install charmbracelet/tap/freeze
# or
go install github.com/charmbracelet/freeze@latest
```

## What it does

linearazor reads a scoped slice of your Linear workspace and produces a
per-project brief with four signals — open questions, scope and date
changes, stalls, and clarity gaps — preceded by a shipped lead-in per
project and a cross-cutting exec summary at the top. A tiered lookahead
section surfaces unclarities and appetite-shape risks in the next
cycle / milestone, so you see plan divergence before it lands in the
active cycle.

Output is rendered in a Catppuccin Mocha palette with a hand-drawn
ASCII animation cast. Modes: `brief` (mood line + counts for
slack-paste), `digest` (daily-cadence slim shape), full ritual (weekly
read), and `share` (carbon-style PNG export for sharing).

Read-only by design. Linear is the source of truth — if something
matters and isn't in Linear, the brief surfaces it as a question
rather than tracking it in a side-car file.

## Use

```text
linearazor
linearazor for infra
linearazor digest
linearazor brief
linearazor share
linearazor for "Bob Wu"
linearazor on infra
linearazor since 2026-05-01
linearazor lookahead off
linearazor reconfigure
```

First-run setup is conversational — name the working group, list
members, optionally narrow by label, pick a default horizon. The
config lives at `~/.config/linearazor/<group>.toml` and is hand-editable.

## Skill internals

See [`SKILL.md`](./SKILL.md) for the routing and pipeline. The skill
is split into a **Signal layer** (what gets said) and a **Presentation
layer** (how it looks) — see the design spec at
[`../../docs/superpowers/specs/2026-05-13-linearazor-design.md`](../../docs/superpowers/specs/2026-05-13-linearazor-design.md)
for the full architecture.

## License

MIT — see [`../../LICENSE`](../../LICENSE).
````

- [ ] **Step 2: Verify lint and commit**

```bash
pnpm lint
git add skills/linearazor/README.md
git commit -m "feat(linearazor): per-skill README"
```

---

### Task 15: Update top-level `README.md`

**Files:**

- Modify: `README.md` (top-level)

**Source:** repo convention — every skill appears in the top-level skills table (per the top-level `CLAUDE.md` section 4).

- [ ] **Step 1: Verify current state of the Skills table**

```bash
sed -n '/^## Skills/,/^## /p' README.md
```

- [ ] **Step 2: Add the `linearazor` row**

Add a row to the Skills table immediately after the `googly-eyes` row:

```markdown
| [linearazor](./skills/linearazor/SKILL.md) | Read-only project-board reviewer for Linear MCP. Per-project briefs framed as questions, with four signals (questions, changes, stalls, quality), shipped lead-in, tiered lookahead, mood line, Catppuccin palette, ASCII animation cast. Modes: brief, digest, full ritual, share (PNG). |
```

Use the `Edit` tool to insert the row in the existing markdown table.

- [ ] **Step 3: Verify lint and commit**

```bash
pnpm lint
git add README.md
git commit -m "docs: add linearazor to top-level skills table"
```

---

### Task 16: Write test fixtures

**Files:**

- Create: `skills/linearazor/tests/fixtures/healthy.mcp.yaml`
- Create: `skills/linearazor/tests/fixtures/aging.mcp.yaml`
- Create: `skills/linearazor/tests/fixtures/cycle-end-retro.mcp.yaml`
- Create: `skills/linearazor/tests/fixtures/many-projects.mcp.yaml`

Mock Linear MCP responses for manual smoke runs. Until the Linear MCP
shape is pinned at implementation time, the fixtures use the
illustrative schema from
[`../assets/factsheet-template.yaml`](../assets/factsheet-template.yaml) —
keep them lean. Revisit and adjust after the probe in
[ingest-and-factsheet.md](./references/ingest-and-factsheet.md).

- [ ] **Step 1: Write `healthy.mcp.yaml`**

A healthy workspace — most issues moving, several shipped, no stalls.

````yaml
# Healthy workspace fixture — most issues moving, several shipped, no stalls.

factSheet:
  schemaVersion: 1
  group: infra
  horizon:
    kind: cycle
    from: "2026-05-06"
    to: "2026-05-16"
  lookahead:
    kind: cycle
    from: "2026-05-17"
    to: "2026-05-30"
    suppressed: false
  thresholds:
    agingWipDays: 7
    silentDays: 7
    noPrDays: 3
  members:
    - displayName: Bob Wu
      identifier: bob.wu@example.com
    - displayName: Carol Ko
      identifier: carol.ko@example.com
  unresolved: []
  projects:
    - name: infra / runtime
      state: started
      milestones:
        - name: May runtime cut
          targetDate: "2026-05-16"
          datesMovedInWindow: []
      shipped:
        - id: ENG-481
          title: Backplane handshake hardening
          completedAt: "2026-05-09T14:02:11Z"
          linkedPRs:
            - https://github.com/example/runtime/pull/812
        - id: ENG-487
          title: Drop debug logger in prod build
          completedAt: "2026-05-11T09:30:00Z"
          linkedPRs:
            - https://github.com/example/runtime/pull/819
      openIssues:
        - id: ENG-492
          title: Bootstrap token rotation
          status: In Progress
          assigneeIdentifier: bob.wu@example.com
          daysInStatus: 2
          lastCommentDaysAgo: 1
          linkedPRs:
            - https://github.com/example/runtime/pull/825
          blockedBy: []
          milestone: May runtime cut
          labels:
            - eng:infra
          bodyHasAcceptanceCriteria: true
      scopeChangesInWindow: []
      lookaheadMilestones:
        - name: June runtime cut
          targetDate: "2026-06-18"
          startedIssueCount: 3
          daysToTarget: 35
          scopeChangedSinceTargetSet: false
      lookaheadIssues: []
````

- [ ] **Step 2: Write `aging.mcp.yaml`**

Several stalls across categories — one project with aging WIP, one
silent issue, one no-PR-linked, one blocked-without-blocker.

````yaml
# Aging workspace fixture — multiple stalls across categories.

factSheet:
  schemaVersion: 1
  group: infra
  horizon:
    kind: cycle
    from: "2026-05-06"
    to: "2026-05-16"
  lookahead:
    kind: cycle
    from: "2026-05-17"
    to: "2026-05-30"
    suppressed: false
  thresholds:
    agingWipDays: 7
    silentDays: 7
    noPrDays: 3
  members:
    - displayName: Bob Wu
      identifier: bob.wu@example.com
    - displayName: Carol Ko
      identifier: carol.ko@example.com
  unresolved: []
  projects:
    - name: infra / runtime
      state: started
      milestones:
        - name: May runtime cut
          targetDate: "2026-05-21"
          datesMovedInWindow:
            - "2026-05-14 -> 2026-05-21"
      shipped: []
      openIssues:
        - id: ENG-423
          title: Refactor scheduler
          status: In Progress
          assigneeIdentifier: carol.ko@example.com
          daysInStatus: 11             # exceeds agingWipDays (7) -> aging WIP
          lastCommentDaysAgo: 6
          linkedPRs: []
          blockedBy: []
          milestone: null
          labels:
            - eng:infra
          bodyHasAcceptanceCriteria: false
        - id: ENG-446
          title: Audit retry policy
          status: In Progress
          assigneeIdentifier: bob.wu@example.com
          daysInStatus: 9              # exceeds noPrDays (3), linkedPRs empty -> no-PR stall
          lastCommentDaysAgo: 2
          linkedPRs: []
          blockedBy: []
          milestone: null
          labels:
            - eng:infra
          bodyHasAcceptanceCriteria: true
        - id: ENG-440
          title: Vendor handshake
          status: Blocked
          assigneeIdentifier: carol.ko@example.com
          daysInStatus: 5
          lastCommentDaysAgo: 4
          linkedPRs: []
          blockedBy: []               # Blocked status without blockedBy -> blocked-without-blocker stall
          milestone: null
          labels:
            - eng:infra
          bodyHasAcceptanceCriteria: true
      scopeChangesInWindow:
        - id: ENG-470
          change: added-to-milestone
          at: "2026-05-12T09:14:02Z"
      lookaheadMilestones:
        - name: June runtime cut
          targetDate: "2026-06-18"
          startedIssueCount: 0        # 0 started, daysToTarget 35 (>14) -> not appetite-risk yet
          daysToTarget: 35
          scopeChangedSinceTargetSet: false
      lookaheadIssues:
        - id: ENG-502
          title: Decide on config schema v2
          assigneeIdentifier: null
          status: Backlog
          milestone: June runtime cut
          bodyHasAcceptanceCriteria: false
          bodyIsEmpty: true            # empty body + attached to milestone -> unclarity
````

- [ ] **Step 3: Write `cycle-end-retro.mcp.yaml`**

Horizon crosses a cycle end (active cycle ends today). Triggers
retrospective section.

````yaml
# Cycle-end fixture — horizon crosses a cycle end; triggers retrospective.

factSheet:
  schemaVersion: 1
  group: infra
  horizon:
    kind: cycle
    from: "2026-04-29"
    to: "2026-05-09"
    endsToday: true
  lookahead:
    kind: cycle
    from: "2026-05-10"
    to: "2026-05-23"
    suppressed: false
  thresholds:
    agingWipDays: 7
    silentDays: 7
    noPrDays: 3
  members:
    - displayName: Bob Wu
      identifier: bob.wu@example.com
  unresolved: []
  projects:
    - name: infra / runtime
      state: started
      milestones:
        - name: May runtime cut
          targetDate: "2026-05-21"
          datesMovedInWindow:
            - "2026-05-14 -> 2026-05-21"
            - "2026-05-07 -> 2026-05-14"
      shipped:
        - id: ENG-481
          title: Backplane handshake
          completedAt: "2026-05-09T11:00:00Z"
          linkedPRs:
            - https://github.com/example/runtime/pull/812
      openIssues:
        - id: ENG-423
          title: Refactor scheduler
          status: In Progress
          assigneeIdentifier: bob.wu@example.com
          daysInStatus: 8
          lastCommentDaysAgo: 2
          linkedPRs:
            - https://github.com/example/runtime/pull/820
          blockedBy: []
          milestone: May runtime cut
          labels:
            - eng:infra
          bodyHasAcceptanceCriteria: true
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
````

- [ ] **Step 4: Write `many-projects.mcp.yaml`**

More than 6 projects in scope — triggers parallel dispatch. 7 project
entries with minimal content. Two of the shipped entries set
`assigneeIdentifier` to exercise the `for <member>` filter in the
same fixture.

````yaml
# Many-projects fixture — 7 projects, triggers parallel-dispatch branch
# (default threshold is 6). Each project has minimal content.

factSheet:
  schemaVersion: 1
  group: infra
  horizon:
    kind: cycle
    from: "2026-05-06"
    to: "2026-05-16"
  lookahead:
    kind: cycle
    from: "2026-05-17"
    to: "2026-05-30"
    suppressed: false
  thresholds:
    agingWipDays: 7
    silentDays: 7
    noPrDays: 3
  members:
    - displayName: Bob Wu
      identifier: bob.wu@example.com
  unresolved: []
  projects:
    - name: infra / svc-1
      state: started
      milestones: []
      shipped:
        - id: ENG-101
          title: svc-1 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          assigneeIdentifier: bob.wu@example.com   # exercises the `for <member>` filter
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
    - name: infra / svc-2
      state: started
      milestones: []
      shipped:
        - id: ENG-102
          title: svc-2 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          assigneeIdentifier: bob.wu@example.com   # exercises the `for <member>` filter
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
    - name: infra / svc-3
      state: started
      milestones: []
      shipped:
        - id: ENG-103
          title: svc-3 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
    - name: infra / svc-4
      state: started
      milestones: []
      shipped:
        - id: ENG-104
          title: svc-4 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
    - name: infra / svc-5
      state: started
      milestones: []
      shipped:
        - id: ENG-105
          title: svc-5 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
    - name: infra / svc-6
      state: started
      milestones: []
      shipped:
        - id: ENG-106
          title: svc-6 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
    - name: infra / svc-7
      state: started
      milestones: []
      shipped:
        - id: ENG-107
          title: svc-7 work shipped
          completedAt: "2026-05-09T10:00:00Z"
          linkedPRs: []
      openIssues: []
      scopeChangesInWindow: []
      lookaheadMilestones: []
      lookaheadIssues: []
````

- [ ] **Step 5: Verify yaml is valid**

```bash
for f in skills/linearazor/tests/fixtures/*.mcp.yaml; do
  yq eval '. | length' "$f" >/dev/null 2>&1 && echo "VALID: $f" || echo "INVALID: $f"
done
```

Expected: 4 `VALID` lines, no `INVALID`. Install `yq` with
`brew install yq` if not present.

- [ ] **Step 6: Lint and commit**

```bash
pnpm lint
git add skills/linearazor/tests/fixtures/
git commit -m "test(linearazor): mock Linear MCP fixtures for smoke runs"
```

---

## Phase 5 — Validation

### Task 17: Final validation

**Files:**

- (No new files; runs the validators.)

- [ ] **Step 1: Lint everything**

```bash
pnpm lint
```

Expected: exits 0.

- [ ] **Step 2: Run `skills-ref validate`**

```bash
npx skills-ref validate ./skills/linearazor
```

Expected: exits 0. Validates frontmatter shape, folder/name match, no
angle brackets in frontmatter, file-reference depth, install command
presence.

- [ ] **Step 3: Audit hard rules mechanically**

```bash
# Audit cue: frontmatter has no angle brackets
awk '/^---$/{c++; if(c==2) exit} c==1' skills/linearazor/SKILL.md | grep -nE '[<>]' && echo "FAIL: angle brackets in frontmatter" || echo "PASS: no angle brackets in frontmatter"

# Audit cue: install command present in SKILL.md and README.md
grep -q "npx skills add xornivore/skills@linearazor" skills/linearazor/SKILL.md && echo "PASS: install in SKILL.md" || echo "FAIL: install missing in SKILL.md"
grep -q "npx skills add xornivore/skills@linearazor" skills/linearazor/README.md && echo "PASS: install in README.md" || echo "FAIL: install missing in README.md"

# Audit cue: top-level README has linearazor row
grep -q "skills/linearazor/SKILL.md" README.md && echo "PASS: top-level README links to skill" || echo "FAIL: top-level README missing skill row"

# Audit cue: Phase-2 references contain no Linear MCP call instructions
grep -nE 'mcp__linear__|Linear MCP query|query Linear MCP' skills/linearazor/references/signals.md skills/linearazor/references/signal-modes.md skills/linearazor/references/parallel-dispatch.md skills/linearazor/references/presentation.md skills/linearazor/references/palettes.md skills/linearazor/references/mood-line.md skills/linearazor/references/tone.md && echo "FAIL: Phase-2 reference references Linear MCP" || echo "PASS: no Phase-2 Linear MCP references"

# Audit cue: file refs at most one level deep from SKILL.md
grep -oE '\]\(\./[^)]+\)' skills/linearazor/SKILL.md | grep -E '/.*/' && echo "FAIL: file ref deeper than one level" || echo "PASS: file refs one level deep"

# Audit cue: no emoji in references or assets (except optional razor glyph nowhere required)
grep -rnE '[\x{1F300}-\x{1FAFF}]|[\x{2600}-\x{27BF}]' skills/linearazor/ --include='*.md' --exclude=animation.md 2>/dev/null | grep -v '^skills/linearazor/SKILL.md:1:' && echo "FAIL: emoji in skill files" || echo "PASS: no emoji"
```

Expected: every line ends in `PASS`.

- [ ] **Step 4: Confirm SKILL.md length**

```bash
wc -l skills/linearazor/SKILL.md
```

Expected: ≤ 250.

- [ ] **Step 5: Confirm all references are under 250 lines**

```bash
wc -l skills/linearazor/references/*.md
```

Expected: each file ≤ 250 lines.

- [ ] **Step 6: Open PR**

```bash
git push -u origin feat/linearazor
gh pr create --title "feat(linearazor): implement skill per spec" --body "$(cat <<'EOF'
## Summary

- Implements `linearazor` per the merged design spec at
  `docs/superpowers/specs/2026-05-13-linearazor-design.md` (PR #12).
- Two-phase pipeline: deterministic Phase 1 ingest from Linear MCP into
  a fact sheet, then model-driven Phase 2 analyze. Parallel sub-agents
  only when more than 6 in-scope projects.
- Four signal lanes plus shipped lead-in, tiered lookahead, mood line.
- Catppuccin Mocha default palette with bundled alternatives.
  Hand-drawn ASCII animation cast (12 animals).
- `share` mode shells out to `charmbracelet/freeze` for PNG export
  (opt-in dependency with markdown fallback).
- Signal layer and presentation layer separated in references and
  audit-able by file diff (hard rule 12).

## Test plan

- [x] `pnpm lint` clean
- [x] `npx skills-ref validate ./skills/linearazor` exits 0
- [x] Hard-rule audit script (Task 17 Step 3) passes
- [ ] Manual smoke runs against `tests/fixtures/healthy.mcp.yaml`,
  `aging.mcp.yaml`, `cycle-end-retro.mcp.yaml`,
  `many-projects.mcp.yaml`
- [ ] Live run against the author's Linear workspace, with Linear MCP
  installed, to probe the real MCP shape and adjust
  `references/ingest-and-factsheet.md` per spec section 13 "Open at
  implementation time"
EOF
)"
```

---

## Self-review checklist

Run after Task 17 commits, before opening the PR:

- [ ] Every spec section maps to a task or is explicitly out of v1
      scope (spec section 11).
- [ ] No placeholders or `TODO` strings in skill files. Placeholders
      in `.toml` and `.yaml` templates marked with angle-bracket
      conventions in body text (not in frontmatter) are allowed.
- [ ] Method, file, and reference names referenced in later tasks
      match what was created in earlier tasks. Grep for orphan
      references:
      ```bash
      grep -oE '\[[^]]+\]\([^)]+\)' skills/linearazor/SKILL.md skills/linearazor/references/*.md | \
        awk -F'[][)(]' '{print $4}' | sort -u | while read p; do
          [ -e "skills/linearazor/$p" ] || [ -e "skills/linearazor/references/$p" ] || \
            [ -e "skills/linearazor/assets/$p" ] || echo "MISSING: $p"
        done
      ```
- [ ] Signal-layer and presentation-layer references are committed in
      separate commits where possible (hard rule 12).
- [ ] SKILL.md frontmatter has no angle brackets.
- [ ] Install command appears in SKILL.md and per-skill README.

If any item fails, fix inline and re-run the validation step.
