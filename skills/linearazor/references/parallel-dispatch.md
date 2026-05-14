# Parallel dispatch (more-than-6-projects branch)

Loaded at the "decide single-pass vs parallel" step in Phase 2. Defines
when to dispatch parallel sub-agents and how to compose their outputs.

## Branching rule

- `factSheet.projects.length ≤ render.parallel_project_threshold`
  (default 6): single-pass. One model call reads the full fact sheet
  and produces the full lane stack plus the exec summary plus the
  mood line.
- Above the threshold: parallel sub-agents — one per project — draft
  each project's findings, grouped by signal lane. The main agent
  re-pivots into lanes, composes the exec summary, the lookahead
  block (if present), the mood line, and the footer.

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

The sub-agent produces a structured findings set for its project:
per-lane lists of bullet items (`shipped`, `questions`, `changes`,
`stalls`, `quality`, `retrospective`). It does **not** render the
final lane stack, the exec summary, the lookahead block, the mood
line, or the footer — those are composed by the main agent over all
sub-agent outputs. The sub-agent's output is data; the main agent's
job is presentation.

## Hard separation

Sub-agents never query Linear MCP. Hard rule 10 binds: if a sub-agent
wants a fact not in its slice of the fact sheet, that is a Phase-1
gap. The fix is upstream, not a side-channel query.

**Audit:** sub-agent prompts in this file contain no instructions to
call `mcp__linear__*` tools.

## Composition

The main agent reads all per-project findings sets and:

1. Filters the project set by the project cap
   ([signal-modes.md](./signal-modes.md) "Bounds").
2. Re-pivots into lanes: for each lane in fixed order
   (`shipped → questions → changes → stalls → quality → retrospective`),
   gather every project's contribution to that lane, drop the lane if
   empty, and render projects in the global order from
   [signal-modes.md](./signal-modes.md) "Lane ordering and item
   ordering."
3. Composes the exec summary from primary-horizon signal counts only.
4. Composes the lookahead block from
   `factSheet.projects[*].lookaheadIssues` and `lookaheadMilestones`
   per the lookahead rules in [signals.md](./signals.md).
5. Composes the mood line per [mood-line.md](./mood-line.md).
6. Appends the disclaimer footer from
   [`../assets/footer.md`](../assets/footer.md) (full-ritual / share
   only).

## Project ordering inside lanes

The global project order, applied identically in every lane:

1. Linear `status.type` — `started` first, then `backlog`, then
   `completed`.
2. Within each tier, alphabetical by project name (case-insensitive).

Projects with zero items in a given lane are omitted from that lane.
