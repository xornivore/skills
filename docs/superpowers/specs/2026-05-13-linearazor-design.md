# linearazor — design spec

**Status:** draft
**Author:** Ivan Ilichev
**Date:** 2026-05-13
**Skill folder (planned):** `skills/linearazor/`
**Branch:** `feat/linearazor`

## 1. Summary

`linearazor` reads a scoped slice of a Linear workspace and produces a
per-project brief built around four signals — open questions, scope and
date changes, stalls, and clarity gaps — preceded by a shipped lead-in
per project and a cross-cutting exec summary at the top. The output is
read-only, written for a human running it as a weekly ritual.

The skill borrows specific practices from Kanban flow metrics, Shape Up
(hill-chart mentality, appetite-vs-estimate, scope-changes-as-information),
Definition of Done, and blameless postmortem culture. It deliberately
skips sprint, velocity, and story-point framing. Linear is the system of
record; if a fact matters and is not in Linear, the brief surfaces it as
a question rather than tracking it in a side-car file.

The skill is invoked conversationally by Claude Code via natural-language
phrasing (`linearazor`, `linearazor digest for containers-blue`,
`linearazor for Bob Wu`). It presents modes, not CLI flags — the
`SKILL.md` body teaches the model to parse phrasing into modes.

## 2. Differentiation

Linear has dashboards. What it does not have is judgment scoped to a
specific working group, framed as questions a thoughtful teammate would
ask, and held to a blameless tone.

| Axis | Linear dashboards | `linearazor` |
| --- | --- | --- |
| Frame | Metrics surfaces | Questions a teammate would ask |
| Tone | Neutral metrics | Signals, not verdicts; never names the person |
| Scope | Team or workspace | A working group: team plus optional label scope, plus a roster |
| Output | Charts, tables | Per-project prose brief, mood line, ASCII animation cast, color-coded signal lanes |
| Cadence | Always-on | Weekly ritual, with digest and brief shapes for daily and slack-paste |
| Stateful | Yes (Linear's database) | No — every run is a fresh observation of Linear |

The skill composes with `googly-eyes`, `observablip`, and `doxcavate` —
it never overlaps. `googly-eyes` reviews code; `observablip` reviews
telemetry; `doxcavate` reviews documentation; `linearazor` reviews the
project board.

## 3. Inputs and modes

### 3.1 Modes

The skill recognizes modes from user phrasing. `SKILL.md` carries the
routing table; the model parses the message into a mode plus optional
scope arguments.

| Phrasing | Mode | Notes |
| --- | --- | --- |
| `linearazor` | full ritual | Uses the default saved scope, default horizon |
| `linearazor for containers-blue` | full ritual | Explicit saved scope by group name |
| `linearazor for Bob Wu` | full ritual, member-filtered | Narrows the issue set to one member |
| `linearazor on <project>` | full ritual, project-filtered | Narrows to a single Linear project |
| `linearazor digest` | digest | Slim daily-cadence shape |
| `linearazor brief` | brief | Mood line plus counts only — slack-paste shape |
| `linearazor reconfigure` | setup | Re-enters the interactive scope flow |
| `linearazor since 2026-05-01` | full ritual, anchor override | Overrides the horizon anchor for shipped and changes |
| `linearazor share` | full ritual, rendered as PNG | Renders the brief as a carbon-style PNG for slack-paste — see [8.6 Share as image](#86-share-as-image-png-for-slack-paste) |

Filter composition: `linearazor for Bob Wu on containers-blue` intersects
the two slices. No special-case prose; filters compose as set
intersection.

### 3.2 Horizon

The horizon frames what counts as in-scope and what counts as recent.

| Horizon | Window |
| --- | --- |
| `cycle` (default) | Current Linear cycle's start to end |
| `week` | Monday of current week to Friday |
| `2w` / `4w` | Today minus N weeks to today |
| `milestone` | Today to the next project milestone target date in scope |
| `since <date>` | The given date to today (overrides horizon anchor) |

When the user's phrasing is ambiguous and no default is set, the skill
prompts once interactively. In non-interactive sessions it falls back
to `cycle`.

### 3.3 Lookahead (tiered auto-horizon)

The primary horizon is the main frame, but pure current-horizon framing
is kanban myopia — divergence from the plan is only visible after it
lands in the active cycle. The skill compensates by **always** ingesting
one tier beyond the primary horizon and rendering a narrower "Looking
ahead" section with two forward-looking signals only (see
[6.7 Lookahead](#67-lookahead-shape-up-forward-looking)).

| Primary horizon | Lookahead window |
| --- | --- |
| `cycle` | The next cycle after the active one |
| `week` / `2w` / `4w` | Today's primary window-end plus the same window length |
| `milestone` | The milestone after the next-in-scope one |
| `since <date>` | Lookahead suppressed (anchor mode is explicitly backward-facing) |

User overrides:

- `linearazor lookahead off` — suppress the lookahead block for a
  single invocation.
- `linearazor lookahead 2` — look two tiers ahead instead of one.

Mode interaction:

- `full ritual` — own section between the per-project blocks and the
  disclaimer footer.
- `digest` — collapsed to a one-liner per project.
- `brief` — suppressed (slack-paste is current-cycle only).

### 3.4 Scope (in-scope issue set)

An issue is in scope when **all** apply:

- It belongs to the configured team.
- It carries at least one of the configured labels (if labels are set).
- It satisfies the composite horizon filter — at least one of:
  - Assigned to a cycle whose window intersects the horizon.
  - Attached to a milestone whose target date falls in the horizon.
  - Has a `dueDate` in the horizon window.
  - Was In Progress at any point in the horizon window
    (catches issues not bound to a cycle, milestone, or due date).

The lookahead set (section [3.3](#33-lookahead-tiered-auto-horizon)) is
computed with the same filter applied to the lookahead window, not the
primary horizon. Lookahead issues are tracked separately in the fact
sheet — they never bleed into the primary signal lanes.

### 3.5 First-run / no-scope behavior

When no config exists and the session is interactive, the skill enters
a conversational setup flow:

1. Detect the workspace shape. List Linear teams. If exactly one team
   exists or the team has many members, assume the workspace is
   tag-partitioned and continue. Otherwise offer a pick list of teams.
2. Ask for a working-group name (free text, becomes the config key).
3. Ask for member names (free text). Match against Linear users by
   display name and email with fuzzy matching. High-confidence matches
   are listed for a single end-of-step confirmation; low-confidence
   matches are confirmed one-by-one. No silent inclusion.
4. Ask for project label scope (optional). Suggest labels seen on
   recent active projects as a pick list; allow free text. Multiple
   labels allowed.
5. Ask for default horizon. Default `cycle`.
6. Offer to persist. Write to `~/.config/linearazor/<group>.toml`.
   Confirm the path so it is discoverable.

When no config exists and the session is **non-interactive** (no TTY or
invoked under a harness loop), the skill exits with the one-line
message: `no scope configured; ask the user to run "linearazor
reconfigure"`. The skill never dumps the workspace.

## 4. Architecture: two-phase ingest then analyze

### 4.1 Phase 1 — Ingest (deterministic, no model judgment)

Steps in order, all read-only via Linear MCP:

1. Resolve scope. Load `<group>.toml`. Resolve member display names to
   Linear user identifiers and label names to label identifiers via
   Linear MCP. Resolution is fresh every run — no cache. Unresolved
   names are surfaced as a setup-health footer in the brief, never as
   stalls.
2. Resolve horizon — and lookahead. Compute the primary date window
   from the mode arguments or the configured default. Compute the
   lookahead window per section
   [3.3](#33-lookahead-tiered-auto-horizon) unless suppressed.
3. Query in-scope issues for the **primary** horizon. Composite filter
   from section [3.4](#34-scope-in-scope-issue-set).
4. For each in-scope issue, fetch the minimum needed: status, status
   history, assignee, last comment timestamp, linked PR URLs, blocker
   / blocking relations, project, milestone, due date, label set,
   title, body.
5. Query project state changes within the primary horizon (milestone
   date moves, label adds/removes, project state transitions)
   directly from Linear's history.
6. Compute shipped (issues completed in the primary horizon plus PRs
   merged in the primary horizon linked to in-scope issues).
7. Query the **lookahead** issue set with the same composite filter
   against the lookahead window. Fetch a narrower projection per
   issue: title, body, assignee, milestone, labels, status (to
   exclude already-In-Progress / Done from lookahead noise),
   acceptance-criteria presence flag.
8. Emit a compact **fact sheet** (machine-readable structure) with
   `projects[].lookaheadIssues[]` and `projects[].lookaheadMilestones[]`
   blocks separate from the primary signal blocks — this is the only
   artifact Phase 2 reads.

Phase 1 is stateless. It does not read or write any file outside
`~/.config/linearazor/`. The fact-sheet schema is illustrative below;
the implementation plan must first probe Linear MCP and pin the schema
to what the MCP actually returns.

```jsonc
{
  "schemaVersion": 1,
  "group": "containers-blue",
  "horizon": { "kind": "cycle", "from": "2026-05-06", "to": "2026-05-16" },
  "thresholds": { "agingWipDays": 7, "silentDays": 7, "noPrDays": 3 },
  "members": [
    { "displayName": "Bob Wu",   "identifier": "bob.wu@example.com" },
    { "displayName": "Carol Ko", "identifier": "carol.ko@example.com" }
  ],
  "unresolved": [],
  "projects": [
    {
      "name": "containers-blue / runtime",
      "state": "started",
      "milestones": [
        { "name": "May runtime cut", "targetDate": "2026-05-21",
          "datesMovedInWindow": [ "2026-05-14 -> 2026-05-21" ] }
      ],
      "shipped": [
        { "id": "ENG-481", "title": "Backplane handshake hardening",
          "completedAt": "2026-05-09T14:02:11Z", "linkedPRs": ["..."] }
      ],
      "openIssues": [
        { "id": "ENG-423", "title": "...", "status": "In Progress",
          "assigneeIdentifier": "carol.ko@example.com",
          "daysInStatus": 11, "lastCommentDaysAgo": 6,
          "linkedPRs": [], "blockedBy": [], "milestone": null,
          "labels": ["eng:containers-blue"],
          "bodyHasAcceptanceCriteria": false }
      ],
      "scopeChangesInWindow": [
        { "id": "ENG-470", "change": "added-to-milestone",
          "at": "2026-05-12T09:14:02Z" }
      ],
      "lookaheadMilestones": [
        { "name": "June runtime cut", "targetDate": "2026-06-18",
          "startedIssueCount": 0, "daysToTarget": 35,
          "scopeChangedSinceTargetSet": false }
      ],
      "lookaheadIssues": [
        { "id": "ENG-502", "title": "Decide on config schema v2",
          "assigneeIdentifier": null, "status": "Backlog",
          "milestone": "June runtime cut",
          "bodyHasAcceptanceCriteria": false, "bodyIsEmpty": true }
      ]
    }
  ]
}
```

### 4.2 Phase 2 — Analyze (model-driven, fact-sheet input only)

Branching rule:

- **≤ 6 in-scope projects** — single-pass. One model call reads the
  fact sheet and produces all per-project briefs plus exec summary
  plus mood line.
- **> 6 projects** — parallel sub-agents (one per project) each draft
  a per-project brief from their slice of the fact sheet. The main
  agent then composes the exec summary and mood line over the drafts.
  The threshold is configurable in `[render]` but defaults to 6.

Hard separation: Phase 2 never queries Linear. If Phase 2 wants a fact
not in the fact sheet, that is a Phase-1 gap and is fixed by extending
Phase 1, not by adding a query in Phase 2.

## 5. Configuration

Single XDG config file per scope: `~/.config/linearazor/<group>.toml`.
No state directory. Linear holds the state.

```toml
# version = 1
group   = "containers-blue"
team    = "Containers"            # Linear team display name
members = ["Bob Wu", "Carol Ko"]  # display names; resolved fresh every run
labels  = ["eng:containers-blue"] # optional; OR'd together; omit for all team work
default_horizon = "cycle"         # cycle | week | 2w | 4w | milestone

# Sane defaults ship in SKILL.md; override only if the team's rhythm
# differs.
[thresholds]
aging_wip_days = 7   # In Progress longer than this -> aging
silent_days    = 7   # No status change AND no comment in this window
no_pr_days     = 3   # In Progress this long with no linked PR

# Optional render preferences. See section 8.1 for palette options.
[render]
palette                       = "catppuccin-mocha"
parallel_project_threshold    = 6
lookahead_unclarities         = true
lookahead_appetite            = true
lookahead_appetite_warn_days  = 14

[render.palette_overrides]
# shipped = "rosewater"
```

Config rules:

- Schema-versioned at the document level via `# version = N` comment on
  line one. The skill refuses to run on an unknown version and tells
  the user how to migrate.
- The skill only writes to this file from the `reconfigure` flow, and
  only after the user confirms.
- ID resolution is **never** persisted. Re-resolving every run is fast
  and keeps the file hand-editable without staleness traps.

## 6. Signal model

Every per-project block leads with **shipped**, then the four signals
in fixed order: questions, changes, stalls, quality. A retrospective
section is appended when the primary horizon crosses a cycle end or
milestone. A lookahead section is appended after the per-project
blocks (full-ritual mode) when the lookahead window has any
forward-looking signal to surface.

### 6.1 Shipped (lead-in)

Union of:

- Issues whose status changed to a Done-category state with
  `completedAt` inside the horizon window.
- Merged PRs linked to in-scope issues, with merge date inside the
  horizon window.

Rendered as a one-line ticker per project. Never a verdict — only
facts.

### 6.2 Questions

Phrased as questions, never accusations. Patterns:

- In Progress past `aging_wip_days` with no recent comment →
  "What's the next concrete step on `ENG-423`, and is anything
  blocking it?"
- Status `Blocked` with no `blockedBy` relation set, OR with a
  `blockedBy` relation whose target has closed → "Is `ENG-440` still
  actually blocked?"
- Milestone date moved twice within the horizon → "Is the appetite
  for `<milestone>` still well-framed?"
- Cycle ends within the horizon and multiple issues are still In
  Progress → "Which of these are realistic to land this cycle?"

Every line in the questions block ends with `?`. Hard rule
([9.5](#9-hard-rules)).

### 6.3 Changes

Surfaced as information, not failure (Shape Up framing). All queried
directly from Linear history within the horizon:

- Milestone target-date moves.
- Issues added to or removed from a milestone.
- Scope label changes on in-scope issues.
- Projects entering or leaving an active state.

Each change states the *what* and the *when*. No verdicts.

### 6.4 Stalls

Computed against defaults from `[thresholds]`, never against learned
baselines. Each stall lists the fact, never the person.

| Stall | Detection |
| --- | --- |
| Aging WIP | `daysInStatus("In Progress") > thresholds.aging_wip_days` |
| No PR linked | `daysInStatus("In Progress") > thresholds.no_pr_days` AND `linkedPRs == []` |
| Silent | No status change AND no comment in `thresholds.silent_days` |
| Blocked-without-blocker | Status is `Blocked` AND `blockedBy == []` |

The skill defends thresholds as defaults, not laws. The brief footer
notes which thresholds are in effect.

### 6.5 Quality

Acceptance criteria and clarity gaps on in-scope issues:

- Body has no acceptance-criteria section AND the issue has subtasks
  or is otherwise non-trivial.
- Title matches a vague-title regex set (`fix bug`, `phase 1`,
  `update`, `cleanup`, `WIP`).
- Open issues with no description body at all.

### 6.6 Retrospective (horizon-triggered)

When the horizon crosses a cycle end or any in-scope milestone target
date, append a forward-looking retrospective section: "What would we
want to know earlier next time?" — never "what went wrong." No blame
framing, no per-person commentary.

### 6.7 Lookahead (Shape Up forward-looking)

The lookahead section uses the lookahead window (section
[3.3](#33-lookahead-tiered-auto-horizon)). It carries only two
signals — chosen to surface plan divergence before it lands in the
active cycle without generating noise about distant work that is
legitimately not-yet-scoped.

**Unclarities (lookahead).** Issues scoped to the lookahead window
that are missing the basics — `bodyHasAcceptanceCriteria == false`
AND issue is non-trivial, OR `bodyIsEmpty == true`, OR title matches
the vague-title regex set (section 6.5), OR `assignee == null` with a
fixed target date. Rendered as questions when a question is the right
shape ("What does done look like for `ENG-502`?"), as a statement
otherwise ("ENG-502 has no body, attached to June runtime cut").

**Appetite-shape risk.** A milestone-level signal, not an issue-level
one. Triggered by either:

- `lookaheadMilestones[].startedIssueCount == 0` AND
  `daysToTarget <=` (configurable, default 14): the milestone has no
  work in flight and is close enough that absence is information.
- Scope grew without the target moving, or the target moved without
  scope shrinking (`scopeChangedSinceTargetSet && !targetMoved`,
  or vice versa). This is the Shape Up "appetite wasn't framed" tell
  — scope and target should move together.

**Out of scope for lookahead.**

- **No stalls.** Issues that have not started cannot be stalled. The
  stall signals (aging WIP, no PR, silent, blocked-without-blocker)
  apply only to issues in the primary horizon.
- **No shipped.** Forward-looking by definition.
- **No retrospective.** Retrospectives belong to the primary horizon.

Configurable suppression:

- `linearazor lookahead off` — skip the lookahead section entirely
  for one invocation.
- `[render].lookahead_unclarities = false` / `..appetite = false` in
  config — turn off individual lookahead signals persistently.

## 7. Signal layer (what gets said)

The signal layer is the information surface — modes, signal ordering,
bounds, the disclaimer footer. It is what would survive a fresh
revision of the presentation layer (section
[8](#8-presentation-layer-how-it-looks)).

This layer and the presentation layer are intentionally kept separate
in the spec, in the file layout, and in `SKILL.md` references — the
signal layer can be revised without disturbing the animation cast or
the palette, and the presentation layer can be tweaked without
touching what is said.

### 7.1 Modes and shapes

| Mode | Mood line | Exec summary | Per-project briefs | Lookahead | Animation | Footer |
| --- | --- | --- | --- | --- | --- | --- |
| `brief` | yes | no | no — counts only | suppressed | no | no |
| `digest` | optional | one-line counts | shipped + new stalls + new changes only | one-liner per project | no | thresholds line |
| full ritual | yes | yes | shipped → questions → changes → stalls → quality | own section after per-project blocks | yes | thresholds + disclaimer |

### 7.2 Ordering and bounds

Within a per-project block, signal lanes appear in the fixed order
(shipped, questions, changes, stalls, quality, retrospective). Within
a lane, issues are ordered by recency of the relevant event
(`daysInStatus` descending for stalls; `completedAt` descending for
shipped). Project sections cap at 12 per run; overflow appends a
single line `N more projects in scope; narrow with "linearazor on
<project>"`.

The lookahead section (when present) follows the per-project blocks
and precedes the disclaimer footer. Lookahead findings carry no
ordering within their lane beyond `daysToTarget` ascending (closest
target date first).

### 7.3 Exec summary

A single line at the top of the full-ritual output, after the mood
line. Lists the per-signal counts across the primary horizon (no
lookahead counts, by design — the exec summary is about active work):

```text
Across 4 projects: 7 shipped · 3 stalls · 5 questions · 2 changes
```

Suppressed in `brief` and `digest` modes (brief is itself a counts
shape; digest leads with shipped per project).

### 7.4 Disclaimer footer

Every full-ritual run ends with one fixed line: the skill only sees
Linear data; PTO, dependencies, conscious deprioritization may
explain things. Stored as a literal string in `assets/footer.md`.
Suppressed in `brief` and `digest`.

## 8. Presentation layer (how it looks)

The presentation layer is the visual and affective polish — palette,
the animation cast, the mood line, color contract, Unicode flourishes,
TTY behavior. It is revisable in isolation: changing a hex code or
swapping an animal does not touch any signal-layer rule.

### 8.1 Palette and color

Default palette: `catppuccin-mocha` (truecolor). Bundled named
palettes in `references/palettes.md`: `catppuccin-mocha`,
`catppuccin-latte`, `solarized-dark`, `tokyo-night`, `monochrome`
(one accent plus dim).

Selection resolution at render time:

1. Environment: `LINEARAZOR_PALETTE=<name>` wins (terminal-specific
   override).
2. Config `[render].palette` name.
3. Per-role overrides in `[render.palette_overrides]` (any signal
   role can be remapped to a different role name or a hex literal).
4. Built-in defaults for the selected palette.
5. `NO_COLOR=1` is absolute — bypasses all of the above.

Signal-role names are palette-independent. Every shipped palette
assigns the same roles to its accents — only the hues change:

| Role | Mocha default |
| --- | --- |
| `shipped` | Teal / Green |
| `questions` | Lavender |
| `changes_scope` | Peach |
| `changes_date` | Mauve |
| `stalls_aging` | Peach |
| `stalls_no_pr` | Peach |
| `stalls_silent` | Sapphire |
| `stalls_blocked` | Overlay |
| `quality` | Sky |
| `retrospective` | Mauve |
| `lookahead` | Sky |
| `metadata` | Overlay0 / Subtext |

### 8.2 Animation (the cast)

Hand-drawn ASCII animals, 4–6 lines tall, 12–20 columns wide. One per
signal category per per-project section — not one per item. All face
right (toward the list below). Mood through pose.

Core cast — six animals shipped in `assets/animation.md`:

| Animal | Lane | Default palette role |
| --- | --- | --- |
| Bee | Shipped, momentum | `shipped` (Teal/Green) |
| Lemur (upside-down) | Questions | `questions` (Lavender) |
| Cow (in field) | Stalls — aging WIP | `stalls_aging` (Peach) |
| Snail | Stalls — no PR | `stalls_no_pr` (Peach) |
| Turtle | Stalls — silent | `stalls_silent` (Sapphire) |
| Beaver | Praise, active building | `shipped` (Teal) |

Extended cast — used sparingly: Fox (scope change), Chameleon (date
move), Mole (blocked), Heron (quality / watching, lookahead
unclarities), Owl (retrospective), Crab (sideways movement).

The cast is purely affective; replacing an animal, changing its pose,
or adding a new one is a presentation-layer change. The signal it
labels is unaffected.

### 8.3 Mood line

One sentence at the top, in the tool's voice. Examples shipped in
`references/mood-line.md` for the model to imitate. Animals serve as
a unit of measure when they appear in the line.

Constraints (presentation-layer rules, not signals): no scoring, no
streaks, no leaderboards. The mood line counts animals as flavor; the
brief never tallies them across runs as metrics. Suppressable with
`no-mood`.

### 8.4 Unicode flourishes

One Unicode flourish max per section — never decorative, always
load-bearing:

- `◇` — leads a stall or lookahead-unclarity line (the diamond reads
  as "noticed thing").
- `→` — leads a question line (the arrow reads as "where does this
  point").
- `─` `├` `└` `│` — section dividers and the run header frame.

ASCII fallback (when not a TTY or `NO_COLOR=1`): `◇` → `*`, `→` → `>`.

### 8.5 TTY and NO_COLOR

Detection: `[ -t 1 ] && [ -z "$NO_COLOR" ]`. Piped or non-TTY output
falls back to plain ASCII with the same content. ANSI escapes are
composed inline — no renderer dependency.

### 8.6 Share as image (PNG for slack-paste)

The `brief` mode is the lean text shape for slack-paste, but
monospace ANSI in a Slack code block loses the color contract — and
the animation cast becomes block-noise without truecolor backing. The
`share` mode produces a carbon-style PNG (or SVG) of the rendered
brief, preserving palette and animation, sized for Slack and similar
chat surfaces.

Implementation: shell out to
[`charmbracelet/freeze`](https://github.com/charmbracelet/freeze) —
it consumes ANSI input directly (no re-themeing pass), runs locally
without a headless browser, and ships PNG and SVG output. The skill
generates the brief into a temp file and pipes it through `freeze`
with a Catppuccin-aligned config.

Behavior:

- `linearazor share` — renders the full ritual brief to a PNG at
  `${TMPDIR:-/tmp}/linearazor-<group>-<date>.png` and prints the
  path. User drags into Slack.
- `linearazor share digest` / `linearazor share brief` — renders
  the digest or brief mode instead. Brief mode is the most
  slack-appropriate default.
- `linearazor share --svg` — emits SVG instead (sharper, scales
  better, but Slack does not always preview SVGs inline).

Opt-in dependency:

- The skill checks for `freeze` in `$PATH` at invocation time.
- If absent, it prints a one-line install hint
  (`brew install charmbracelet/tap/freeze` or `go install
  github.com/charmbracelet/freeze@latest`) and falls back to writing
  a plain markdown file at the same path. **Never** silently
  installs a binary; **never** errors out — the fallback always
  produces a shareable artifact.

Presentation-layer rule: the PNG must visually match the terminal
render byte-for-byte at the signal layer (same prose, same lines,
same flourishes). Only the *medium* changes. **Audit:** the
plain-text dump from `freeze --output text` over a `share` invocation
must be byte-identical to the same brief rendered to a TTY-fallback
file via redirection.

Out of scope for v1: posting to Slack directly via a webhook. The
share artifact is a file the user pastes; auto-posting opens a write
surface (slack token, channel selection) that belongs in a later
revision.

### 8.7 Layout sketch (combined signal + presentation)

Illustrative — actual prose and animal art are produced at render
time from the templates in `assets/` and the model's prose.

```text
─────────────────────────────────────────────────────────────────────────
 linearazor — containers-blue · cycle ending Fri May 16
─────────────────────────────────────────────────────────────────────────

   Three cows in the field this week, one bee, and a lemur with a
   good question.

 Across 4 projects: 7 shipped · 3 stalls · 5 questions · 2 changes

─────────────────────────────────────────────────────────────────────────
 containers-blue / runtime
─────────────────────────────────────────────────────────────────────────
   <bee animal in Teal>
 Shipped:
   • ENG-481  Backplane handshake hardening
   • ENG-487  Drop debug logger in prod build

   <lemur animal in Lavender>
 →  What's the next concrete step on ENG-423, and is anything
    blocking it?
 →  Is ENG-440 still actually blocked? Its blocker closed Tuesday.

   <cow animal in Peach>
 ◇  ENG-423  In Progress 11 days  (default threshold: 7)
 ◇  ENG-446  In Progress 9 days, no PR linked

   <fox animal in Mauve>
    Milestone "May runtime cut" moved from May 14 → May 21
    ENG-470 added to scope this week

─────────────────────────────────────────────────────────────────────────
 Looking ahead — next cycle
─────────────────────────────────────────────────────────────────────────
   <heron animal in Sky>
 ◇  ENG-502  No body, no acceptance criteria  (June runtime cut)
 →  What does done look like for ENG-505?

   <chameleon animal in Mauve>
    "June runtime cut" — 0 started, 35d to target

─────────────────────────────────────────────────────────────────────────
 Thresholds: aging 7d, silent 7d, no-PR 3d.
 The skill only sees Linear data; PTO, dependencies, conscious
 deprioritization may explain things.
```

## 9. Hard rules

Imperative directives in `SKILL.md` per `skills/CLAUDE.md` voice rules
("must" / "never", not "should"). Each rule is tagged `[Signal]` or
`[Presentation]` so the two layers can be revised independently.

1. **[Signal] Read-only.** Phase 1 issues only Linear MCP read
   queries. The skill never edits files in the user's working
   directory, never edits Linear, never executes shell commands
   against the user's repos. **Audit:** in any run, no Linear MCP
   write tool, no `Edit` or `Write` to anything outside
   `~/.config/linearazor/`, no `Bash` outside read-only commands.
2. **[Signal] Never invoke unscoped.** If no config exists and the
   session is non-interactive, exit with the one-line "no scope
   configured" message. In an interactive session, drop into the
   setup flow. Never dump the workspace. **Audit:** every run path
   through `SKILL.md` reads `~/.config/linearazor/<group>.toml`,
   runs the setup flow, or exits — no fourth branch.
3. **[Signal] Never name the person.** Findings name behaviors and
   identifiers, never authors. Forbidden patterns by example in
   `references/tone.md`: `Bob hasn't…`, `Carol is behind…`,
   `@bob.wu`. Replace with subject-on-issue prose. **Audit:** emitted
   prose grepped for the configured member display names returns
   nothing outside the setup-health footer.
4. **[Signal] Signals, not verdicts.** No red/yellow/green markers,
   no `CRITICAL` / `AT RISK` / `BEHIND SCHEDULE`, no severity
   prefixes. **Audit:** grep for `CRITICAL|AT RISK|BEHIND|❌|⚠️` over
   the output returns nothing.
5. **[Signal] Questions are questions.** Every line in the questions
   block ends with `?`. Same rule for lookahead-unclarities rendered
   as questions. **Audit:** non-comment lines in the questions block
   match `\?\s*$`.
6. **[Presentation] No emoji except the optional razor glyph in the
   header.** Color carries the emotional work. **Audit:** strip
   ANSI, strip the run header — the remaining bytes contain no
   characters in the Emoji property range.
7. **[Signal] Acknowledge missing context once.** Full-ritual runs
   end with one line: the skill only sees Linear data; PTO,
   dependencies, conscious deprioritization may explain things.
   Suppressed in `brief` mode. **Audit:** full-ritual output
   contains the literal disclaimer string from `assets/footer.md`.
8. **[Signal] Celebrate first.** Each per-project block leads with
   shipped. If nothing shipped, the block opens with "No completions
   in window" — never with stalls.
9. **[Signal] No scoring, no streaks, no leaderboards.** The mood
   line counts animals as flavor; the brief never tallies them
   across runs as metrics. **Audit:** no persisted counter of
   animals, shipped, or stalls exists — there is no state file in
   which to persist them.
10. **[Signal] Never re-query Linear from Phase 2.** If Phase 2 needs
    a fact, it is missing from the fact sheet — a Phase-1 gap to fix
    in code. **Audit:** Phase-2 prompts in `references/` contain no
    instructions to call Linear MCP.
11. **[Signal] Lookahead never carries stall, shipped, or
    retrospective signals.** Issues in the lookahead window are
    surfaced only as unclarities or appetite-shape risks (section
    [6.7](#67-lookahead-shape-up-forward-looking)). **Audit:** the
    rendered "Looking ahead" section contains no shipped lines, no
    `daysInStatus` references, and no retrospective language.
12. **[Presentation] Layer separation.** Presentation-layer changes
    (swapping an animal, changing a hex code, renaming a palette)
    must not alter any signal-layer rule or rendering bound.
    **Audit:** a diff that touches only files under section
    [10's](#10-file-layout) "Presentation layer" group must leave
    `references/signals.md`, `references/signal-modes.md`, and
    `references/tone.md` untouched.

## 10. File layout

References and assets are grouped by layer so a presentation-layer
revision can be reviewed as a single concern.

```text
skills/linearazor/
├── SKILL.md                          # entry point; routing + hard rules + reference index
├── README.md                         # human-facing; install command + link to SKILL.md
├── references/
│   │   # — Signal layer —
│   ├── setup-flow.md                 # interactive scope detection, member fuzzy match, persist
│   ├── horizon-and-scope.md          # composite horizon, lookahead window, scope filter
│   ├── ingest-and-factsheet.md       # Phase 1: MCP queries, fact-sheet schema (illustrative until probe)
│   ├── signals.md                    # questions / changes / stalls / quality / lookahead detection rules
│   ├── signal-modes.md               # full ritual / digest / brief shapes; what signals each carries
│   ├── tone.md                       # signals-not-verdicts; questions phrasing; forbidden patterns
│   ├── parallel-dispatch.md          # the more-than-6-projects escape: sub-agent prompts
│   │   # — Presentation layer —
│   ├── presentation.md               # how the signal layer is dressed: palette routing, animation placement, flourishes
│   ├── palettes.md                   # bundled palettes, role names, hex tables, NO_COLOR
│   └── mood-line.md                  # voice exemplars and constraints
├── assets/
│   │   # — Signal layer —
│   ├── config-template.toml          # scaffold written by reconfigure
│   ├── factsheet-template.json       # Phase 1 to Phase 2 handoff skeleton
│   ├── footer.md                     # the "skill only sees Linear data" disclaimer string
│   │   # — Presentation layer —
│   └── animation.md                  # ASCII animals (the cast), colored in their role
└── tests/
    └── fixtures/                     # mock Linear MCP responses for manual smoke runs
```

Loading order (stage 2 to stage 3):

| Step in SKILL.md | References pulled |
| --- | --- |
| Detect mode plus parse phrasing | none |
| First-run setup branch | `setup-flow.md`, `assets/config-template.toml` |
| Resolve scope plus horizon plus lookahead | `horizon-and-scope.md` |
| Phase 1 ingest | `ingest-and-factsheet.md`, `assets/factsheet-template.json` |
| Decide single-pass vs parallel | `parallel-dispatch.md` |
| Sub-agent dispatch (parallel branch) | each sub-agent loads `signals.md` plus `tone.md` |
| Phase 2 — signal composition | `signal-modes.md`, `signals.md`, `tone.md`, `assets/footer.md` |
| Phase 2 — presentation | `presentation.md`, `palettes.md`, `mood-line.md`, `assets/animation.md` |

All file references are exactly one level deep from `SKILL.md`.
`SKILL.md` target length is at most 250 lines, well under the 500-line
cap in `skills/CLAUDE.md`.

## 11. Out of scope (v1)

- **Write-back to Linear.** No project updates, no comments, no issue
  edits. v1.1 may add an opt-in, never silent surface.
- **Per-individual judgments.** Hard rule 3 in section
  [9](#9-hard-rules). The skill produces team-level prose; "how is Bob
  doing" is not a question it answers.
- **Velocity, sprint, story points, burndown.** Different framework.
  Cycle time and PR-link as raw observation yes; aggregated velocity
  metrics no.
- **Scoring and gamification.** Hard rule 9 in section
  [9](#9-hard-rules). No streaks, no leaderboards, no points.
- **Non-Linear data sources.** No Jira, no GitHub-only mode, no Slack
  scraping. Linear MCP is the spine.
- **Cross-team aggregation.** One scope per invocation. Composite
  workspace shape is handled at scope-config time, not by merging
  groups at run time.
- **Scheduling.** Skills are invoked by Claude Code; cron, `loop`, and
  `ScheduleWakeup` are harness concerns. The skill only commits to
  behaving correctly under non-interactive invocation.
- **First-class GitHub integration.** PR-link inspection uses whatever
  Linear already exposes. No `gh` calls.

## 12. Validation and testing

Validation gate, same as the rest of the repo:

```bash
pnpm lint                                          # markdownlint + lint-staged
npx skills-ref validate ./skills/linearazor        # agentskills.io reference validator
```

Both must exit 0 before the PR is mergeable.

Testing strategy, three layers:

1. **Smoke tests (manual, in-repo).** Run `linearazor` against curated
   mock Linear MCP responses in `tests/fixtures/`:
   - Healthy workspace: most issues moving, several shipped, no
     stalls.
   - Aging workspace: several stalls across categories.
   - Cycle-end retrospective: horizon crosses a cycle end.
   - Over-6-projects: triggers parallel dispatch.
2. **Tone audits.** A small script greps the rendered output against
   the audit cues from section [9](#9-hard-rules) (member names not
   present outside footer, no `CRITICAL` / `AT RISK`, every question
   line ends with `?`, no emoji outside header). Audit runs split by
   layer: signal-layer audits gate merge; presentation-layer audits
   (emoji check, ASCII fallback for flourishes) gate the
   presentation-layer reference set independently.
3. **Skill validator.** `npx skills-ref validate` covers spec
   mechanics (frontmatter, layout, install command, no `<>` in
   frontmatter).

No automated end-to-end test against a real Linear workspace —
too brittle, too much surface. Fixture-based smoke tests plus the
tone audit are the practical bar.

## 13. Open at implementation time

These are known unknowns that the implementation plan (next step
after this spec) must address before any code:

- **Probe Linear MCP shapes.** First implementation task: query the
  real Linear MCP from a worktree and pin the fact-sheet schema to
  what the MCP actually returns. The schema in section 4.1 is
  illustrative. Examples in this spec use email-shaped identifiers
  for clarity, but the actual identifier format is whatever Linear
  MCP emits.
- **Acceptance-criteria detection heuristic.** Section 6.5 calls for
  detecting a missing acceptance-criteria section in the issue body.
  The detection regex set will be derived from sampled real bodies
  in the user's workspace, not invented up front.
- **Vague-title regex set.** Section 6.5 lists examples; the full set
  is calibrated against real titles at implementation time.
- **`reconfigure` flow's pick-list source.** Section 3.4 step 4
  suggests labels seen on recent active projects. The exact query
  ("recent" = which window) is finalized once the Linear MCP shape
  is known.

These are intentionally deferred — the spec settles the architecture,
tone, and rules; the plan settles the data shapes.
