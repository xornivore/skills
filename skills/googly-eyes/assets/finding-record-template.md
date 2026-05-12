# Finding record template

Filled per finding at the emit step. Every finding — triage or Phase-2 — conforms to this shape. The fields are listed in source-of-truth order; the local renderer presents them in display order (severity label, location, why, suggestion, hunk).

```yaml
- id:          stable id, e.g. F-001; assigned by main agent after merge/dedupe
  principle:   one of: design | complexity | tests | functionality | naming |
                comments | documentation | every-line | style | consistency |
                small-cl | description | specialty
  severity:    one of: required | optional | nit | fyi | praise
  location:
    file:      repo-relative path
    line:      single line number, or range "L1-L2" for structural findings
  observation: factual: what in the code triggered this. No evaluation here.
  why:         reasoning: cites the Google principle by name. May cite one
                Pragmatic Programmer principle by name when it cleanly applies.
                Begins with "Because" or "This".
  suggestion:  preferred direction, or empty when the author should decide.
                Render verb form depends on severity (see severity-labels.md).
  pp:          optional. Pragmatic Programmer principle slug, e.g.
                orthogonality, dry, broken-windows. Omit when no clean
                mapping. See pragmatic-citations.md.
```

Hard rules:

- A finding without `principle` is a bug — reject it before emit.
- A finding without `why` is a bug — reject it before emit.
- `pp` is optional and may be omitted. Never invent a PP citation to fill the field.
- `observation` must be factual. Evaluative language ("badly written", "ugly") goes nowhere; the evaluation belongs in `why` and is grounded in the principle.
