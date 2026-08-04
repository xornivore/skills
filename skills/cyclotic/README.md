# cyclotic

Reads a scoped slice of a Linear workspace and reports how well a cycle is
prepared. Read-only against Linear.

## Install

```bash
npx skills add xornivore/skills@cyclotic --agent claude-code -y
```

Requires Linear MCP:

```bash
claude mcp add linear --transport sse https://mcp.linear.app/sse
```

Optional: incident.io MCP, for deducting on-call rotation weeks from a
person's available days. Without it the report still runs and the footer says
rotations were not checked.

## What it answers

- **Is the team's capacity allocated?** Who is holding more days of work than
  the cycle has room for, and who is holding none at all.
- **Are the tickets in the cycle sized and assigned?** An unsized ticket cannot
  be weighed against anyone's capacity; an unassigned one belongs to nobody.
- **Are the projects behind the cycle groomed?** Whether there is a sized,
  unclaimed queue to pull from next, or a pile of raw tickets nobody triaged.
- **Was unfinished work from the last cycle accounted for?** What came across,
  and whether it was never started, stuck in progress, or waiting on review.
- **Does rotation time come out of the right person's capacity?** A week on an
  on-call schedule is a week not spent on cycle work.
- **Is anyone doing cycle work who is not on the roster?**

## Modes

| Command | What it asks |
| --- | --- |
| `cyclotic prep` | How well is the active cycle prepared, while there is still time to change it |
| `cyclotic prep next` | Same, for the next upcoming cycle |
| `cyclotic review` | How well was the cycle that just closed prepared, and what did it leave behind |
| `cyclotic prep for avery` | Either mode, narrowed to one person |
| `cyclotic init` | Interactive setup; `cyclotic configure` is an alias |

Bare `cyclotic` routes to `prep`.

## What it does not do

It never writes to Linear, and it never judges a person. There are no
completion percentages, no per-person trends across cycles, and no ranking of
people against each other. Load, sizing, and carryover describe the plan; a
capacity tool that describes people is a performance-review instrument.

PTO and per-person baseline capacity are also out. Available days come only
from cycle length and on-call rotation, because a hand-typed absence figure
goes stale immediately and a baseline percentage encodes a judgment about a
person in a config file.

Output is plain text. No palette, no theme, no image export.

## How it works

Two phases. Everything is read from Linear in one ingest pass and landed in a
fact sheet; rendering reads only the fact sheet and never queries again. Cycle
length and working days come from Linear's own cycle dates on every run, so an
unusually long or short cycle gets the right denominator with no config edit.

Details, hard rules, and the reference index are in
[`SKILL.md`](./SKILL.md).

## Configuration

Lives at `~/.config/cyclotic/GROUP.toml`, is hand-editable, and is the only
file this skill writes. See
[`assets/config-template.toml`](./assets/config-template.toml).

## Composes with

`googly-eyes` reviews code, `observablip` reviews telemetry, `doxcavate`
reviews documentation, `cyclotic` reviews the plan.
