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
