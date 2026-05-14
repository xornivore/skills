# Signal-layer render modes

What the signal layer renders for each mode. The presentation layer
([presentation.md](./presentation.md)) handles palette, animation, and
flourishes. This reference covers structure only: which signal blocks
appear, in what order, with what bounds.

## Modes

| Mode | Mood line | Exec summary | Lane stack | Project sub-headers in lanes | Lookahead | Footer |
| --- | --- | --- | --- | --- | --- | --- |
| `brief` | yes | no | yes (lanes render) | no — flat items with trailing `· <project>` tag | suppressed | no |
| `digest` | optional (off with `no-mood`) | one-line counts | yes (lanes render) | yes | one-liner per project | thresholds line |
| full ritual | yes | yes | yes (lanes render) | yes | own section after the lane stack | thresholds + disclaimer |
| `share` | full ritual content | full ritual | full ritual | full ritual | full ritual | full ritual |

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

## Lane ordering and item ordering

Lanes render in this fixed order, with empty lanes omitted:

1. shipped
2. questions
3. changes
4. stalls
5. quality
6. retrospective (when triggered)

Inside each lane, items are grouped by project. Projects appear in a
**consistent global order** across every lane:

1. Linear `status.type` — `started` first, then `backlog`, then
   `completed`.
2. Within each tier, alphabetical by project name (case-insensitive).

Projects with zero items in a given lane are omitted from that lane.
A project can appear in some lanes and not others; when it does, its
position relative to other projects stays the same in each lane it
participates in.

Within a single project's items inside a lane, order by recency of
the relevant event:

- `shipped`: `completedAt` descending.
- `stalls`: `daysInStatus` descending.
- `questions`, `changes`, `quality`: source-order in the fact sheet.

## Lookahead placement

The lookahead block follows the lane stack and precedes the
disclaimer footer. Within the block, `lookaheadIssues` precede
`lookaheadMilestones`. Order by `daysToTarget` ascending (closest
target first).

## Bounds

- Project sub-headers cap at 12 across the brief (counted as the
  distinct project set appearing across all lanes). Overflow appends
  one line under the questions lane's `(cross-project)` sub-header:
  `N more projects in scope; narrow with "linearazor on <project>"`.
- No per-lane cap on items — lanes with many entries surface them all.
- Lookahead unclarities cap at 8 per project. Overflow appends
  `N more lookahead unclarities — consider triaging the next milestone`.

## Empty-brief case

When every signal lane is empty across every in-scope project —
nothing shipped, no questions, no changes, no stalls, no quality
findings — suppress the lane stack entirely and replace the mood
line with the empty-brief mascot from
[`../assets/animation.md`](../assets/animation.md) "Empty-brief
mascot", rendered in the `metadata` palette role. Keep the exec
summary line (it will read `Across N projects: 0 shipped · 0
stalls · 0 questions · 0 changes`) and the disclaimer footer.

This is an honest edge case — better than a forced upbeat mood line
when the horizon turned up nothing.

## Exec summary

A single line at the top of the full-ritual output, after the mood
line. Lists per-signal counts across the primary horizon only — no
lookahead counts.

Format:

```text
Across <N> projects: <S> shipped · <T> stalls · <Q> questions · <C> changes
```

Suppressed in `brief` and `digest` modes (brief is counts at the foot;
digest leads with its own exec-summary line, then the lane stack).

## Disclaimer footer

Renders the literal string from [`assets/footer.md`](../assets/footer.md)
once per run. Full-ritual and `share` modes only. Suppressed in `brief`
and `digest`. Hard rule 7 binds.

## Mode-by-mode rendering details

### brief

The lane stack renders, but each lane is a flat bullet list — no
project sub-headers. Items render with the project name as a trailing
dot-separated tag, suited for slack-paste:

```text
<mood line>

Shipped
  •  ENG-481  finalize scope for runtime backpressure  · Runtime backpressure
  •  ENG-492  rough draft of post-migration roadmap    · Scheduler refactor
  [...]

Stalls
  •  ENG-487  In Progress 8 days  (default threshold: 7)  · Runtime backpressure
```

No animation cast. No flourishes. Counts line at the foot when the
mood line is suppressed:

```text
Across <N> projects: <S> shipped · <T> stalls · <Q> questions · <C> changes
```

### digest

Lane stack renders with project sub-headers. Stalls and changes are
filtered to "new" items only (not present in the previous digest).
Lookahead collapses to one line per project.

```text
<mood line>           # suppressed with `no-mood`
<exec summary line>


<bee art>

Shipped
  <project name>
    •  <id>  <title>
  [...]


<cow art>

Stalls (new)
  <project name>
    •  <new-stall-1>
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
