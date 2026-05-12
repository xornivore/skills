# Triage report template

Filled at the end of Phase 1 (triage). Substitute bracketed placeholders with values produced by the triage pass. Render the filled block at the top of the user-facing output, before the file map and findings.

```text
Triage
------
Target:       [PR #N | local diff vs <base>]
Commit:       [short SHA]
Files:        [F file(s)]
LOC:          +[added] / -[removed]

Size:         [small | medium | large]
              [N LOC, F files — small ≤ 100 LOC and ≤ 5 files;
               medium ≤ 400 LOC; large > 400 LOC or > 15 files]

Scope:        [single | mixed]
              [if mixed, name the mixed concerns, e.g. "refactor + feature"]

Description:  [strong | weak | n/a-for-local-diff]
              [one-line verdict — what is missing or what is good]

Specialty:    [none | listed]
              [comma-separated list of advisory triggers, e.g.
               "auth/crypto path, concurrency primitive"]
```

Hard rules:

- The triage block is rendered verbatim from this template — no reordering, no additional rows.
- `Size`, `Scope`, `Description`, `Specialty` each correspond to one Phase-1 finding when the verdict is anything other than green (small / single / strong / none). Those findings are filed by triage and not re-derived in Phase 2.
- When the target is a local diff with no open PR, `Description` is `n/a-for-local-diff`; the description-quality check is skipped.
