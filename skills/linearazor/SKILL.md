---
name: linearazor
description: Reads a scoped Linear workspace via Linear MCP and produces per-project briefs framed as questions a thoughtful teammate would ask, with four signals (questions, scope/date changes, stalls, clarity gaps), a shipped lead-in, a tiered lookahead, a mood line, and a hand-drawn ASCII animation cast. Invoke when the user says "linearazor", "linearazor for [group]", "linearazor digest", "linearazor brief", "linearazor share", "linearazor for [member]", "linearazor on [project]", "linearazor reconfigure", "weekly Linear brief", or "what shipped in Linear this week". Read-only.
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

- Uses an explicit phrase: `linearazor`, `linearazor for [group]`,
  `linearazor digest`, `linearazor brief`, `linearazor share`,
  `linearazor reconfigure`.
- Adds a filter: `linearazor for [member]`, `linearazor on [project]`.
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
| `linearazor for [group]` | full ritual, named scope |
| `linearazor for [member]` | full ritual, member-filtered |
| `linearazor on [project]` | full ritual, project-filtered |
| `linearazor digest` | digest |
| `linearazor brief` | brief |
| `linearazor share` | share (PNG export) |
| `linearazor reconfigure` | setup flow |
| `linearazor since [date]` | full ritual, anchor override |
| `linearazor lookahead off` | (modifier) suppress lookahead |
| `linearazor lookahead 2` | (modifier) look two tiers ahead |

Filters compose as set intersection.

## Pipeline

When invoked (any non-setup mode), do:

1. **Resolve scope.** Read `~/.config/linearazor/[group].toml`.
   If absent and the session is interactive, route to the setup flow
   ([setup-flow.md](./references/setup-flow.md)). If absent and the
   session is non-interactive, exit with `no scope configured; ask
   the user to run "linearazor reconfigure"` and stop.
2. **Resolve horizon and lookahead.** See
   [horizon-and-scope.md](./references/horizon-and-scope.md).
3. **Phase 1 ingest.** Query Linear MCP per
   [ingest-and-factsheet.md](./references/ingest-and-factsheet.md).
   Emit the fact sheet (template at
   [assets/factsheet-template.json](./assets/factsheet-template.json)).
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

These are non-negotiable. Each is tagged [Signal] or [Presentation]
so the layers can be revised independently.

1. **[Signal] Read-only.** Phase 1 issues only Linear MCP read queries.
   Never edit files in the user's working directory, never edit
   Linear, never execute shell commands against the user's repos.
   Audit: in any run, no Linear MCP write tool, no Edit or Write to
   anything outside ~/.config/linearazor/, no Bash outside read-only
   commands.

2. **[Signal] Never invoke unscoped.** If no config exists and the
   session is non-interactive, exit with the one-line "no scope
   configured" message. In an interactive session, drop into the
   setup flow. Never dump the workspace.

3. **[Signal] Never name the person.** Findings name behaviors and
   identifiers, never authors. Forbidden patterns by example in
   [tone.md](./references/tone.md): "Bob hasn't…", "Carol is
   behind…", "@handle". Replace with subject-on-issue prose.
   Audit: emitted prose grepped for the configured member display
   names returns nothing outside the setup-health footer.

4. **[Signal] Signals, not verdicts.** No red/yellow/green markers,
   no CRITICAL / AT RISK / BEHIND SCHEDULE, no severity prefixes.
   Audit: grep for CRITICAL|AT RISK|BEHIND|FAILING over the output
   returns nothing.

5. **[Signal] Questions are questions.** Every line in the questions
   block ends with `?`. Same rule for lookahead-unclarities rendered
   as questions. Audit: non-comment lines in the questions block
   match `\?\s*$`.

6. **[Presentation] No emoji except the optional razor glyph in the
   header.** Color carries the emotional work. Audit: strip ANSI,
   strip the run header — remaining bytes contain no characters in
   the Emoji property range.

7. **[Signal] Acknowledge missing context once.** Full-ritual runs
   end with one line: the literal disclaimer from
   [assets/footer.md](./assets/footer.md). Suppressed in `brief`
   mode. Audit: full-ritual output contains the literal string.

8. **[Signal] Celebrate first.** Each per-project block leads with
   shipped. If nothing shipped, the block opens with
   `No completions in window` — never with stalls.

9. **[Signal] No scoring, no streaks, no leaderboards.** The mood
   line counts animals as flavor; the brief never tallies them across
   runs as metrics. Audit: no persisted counter of animals, shipped,
   or stalls exists.

10. **[Signal] Never re-query Linear from Phase 2.** If Phase 2 needs
    a fact, it is missing from the fact sheet — a Phase-1 gap to fix
    in code. Audit: Phase-2 prompts in `references/` contain no
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
| Phase 1 ingest | [ingest-and-factsheet.md](./references/ingest-and-factsheet.md), [assets/factsheet-template.json](./assets/factsheet-template.json) |
| Decide dispatch | [parallel-dispatch.md](./references/parallel-dispatch.md) |
| Phase 2 — signal composition | [signal-modes.md](./references/signal-modes.md), [signals.md](./references/signals.md), [tone.md](./references/tone.md), [assets/footer.md](./assets/footer.md) |
| Phase 2 — presentation | [presentation.md](./references/presentation.md), [palettes.md](./references/palettes.md), [mood-line.md](./references/mood-line.md), [assets/animation.md](./assets/animation.md) |

All references are one level deep from `SKILL.md`.
