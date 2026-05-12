# Output format

This reference defines: finding-record schema, ranking algorithm, dedupe rules, bounded output, file-map block, top-of-output structure.

## Finding record schema

Source: [finding-record-template.md](../assets/finding-record-template.md). Every finding — triage or Phase-2 — conforms to that template.

## Ranking algorithm

Two-key sort, descending:

1. Severity: required > optional > nit > fyi > praise.
2. Principle priority (tiebreaker within severity):
   `design > complexity > tests > functionality > naming > comments > documentation > every-line > consistency > style`.
3. Final tiebreaker: file (alphabetical) then `location.line` ascending.

Triage findings (`small-cl`, `description`, `specialty`) do not enter the principle-ranked list — they render in the triage block at the top of output, in the order produced by [triage-heuristics.md](./triage-heuristics.md).

## Dedupe

After all findings are collected:

- Group by `(file, line ± 2, principle)`. On collision, keep the highest-severity record; concatenate non-redundant `why` clauses with `;` separator; preserve at most one `suggestion` (highest severity wins; on tie, longer suggestion wins).
- Structural findings ("this function is over-complex", "this type hierarchy is too deep") bundle at function scope. The bundled finding's `location.line` is a range starting at the function header line.

## Bounded output

Per-severity caps, applied after dedupe:

| Severity | Cap |
| --- | --- |
| required | 20 |
| optional | 15 |
| nit | 10 |
| fyi | 5 |
| praise | unbounded |

When a severity is capped, append at the bottom of that section in the rendered output:

`N more <severity> findings suppressed; consider splitting this CL for thorough review`

The suppression message reinforces small-cl when the CL is the cause.

## File map

Render the file map immediately after the triage block, before the findings. Format:

```text
<repo-relative file path>  <R>R · <O>O · <N>N · <F>F · <P>P  (+<added>/-<removed>)
```

One row per file. Columns aligned. Sort by total finding count descending, then by file path ascending.

## Top-of-output structure

```text
👀 googly-eyes review — <target ref> @ <short SHA>

<triage block from triage-report-template.md>

<file map>

## Required (N)
<finding records in display order>

## Optional (M)
<...>

## Nit / FYI / Praise
<...>

## Next step
<one of:
  - Post selected findings to PR #<N> — run: googly-eyes post
  - Split this CL before review — see Triage
  - Iterate on findings locally — re-run after edits>
```

## Audit cues

- The header line literally starts with `👀 googly-eyes review —` (audit: regex on rendered output).
- No `required` finding is emitted without a `suggestion` (audit: scan emitted YAML).
- No finding is emitted whose `principle` is outside the allowed set (audit: scan emitted YAML against the list in [google-principles.md](./google-principles.md) plus `small-cl`, `description`, `specialty`).
