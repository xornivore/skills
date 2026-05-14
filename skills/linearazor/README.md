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
