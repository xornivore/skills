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
