# Finding template

Filled per finding at the emit step. Substitute the bracketed placeholders with values produced by the pipeline. Emit the rendered block with no surrounding fences (the example below is fenced for readability of this template document only).

```text
[{index}] {dimension} · {severity} · {file}:{line}
    {why_this_matters}
    Suggest: {suggest}
```

## Field rules

- `{index}` — 1-based; stable within a single run.
- `{dimension}` — one of `missing-telemetry`, `poor-practices`, `structure-for-telemetry`.
- `{severity}` — one of `high`, `med`, `low`. Severity is decided by the rubric file that produced the finding.
- `{file}:{line}` — the most informative line for the finding (start of the operation, not start of the file).
- `{why_this_matters}` — 1–2 lines naming the concrete consequence of leaving the gap. "A failure in any one is currently indistinguishable from the others in production logs" is acceptable; "improves observability" is not.
- `{suggest}` — the *shape* of the fix, not a code patch. Names a span, metric, log event, or structural change. If the codebase already imports OTel / slog / zap / structlog, the suggestion uses that vocabulary; otherwise it stays neutral ("a span", "a structured log").

## Footer template

After all findings are emitted, render this footer block once:

```text
---
scanned: {n_scanned} files
skipped: {n_skipped} ({skip_reasons_grouped})
fp-dropped: {n_fp_dropped}
shown: {n_shown} of {n_total} findings{overflow_note}
```

- `{skip_reasons_grouped}` — reason-keyed counts, comma-separated, e.g. `generated: 8, no-io: 6, test-fixture: 4, pure-data: 1, vendored: 2`. Reasons come from the fixed set in `references/precheck.md`.
- `{overflow_note}` — when `n_shown < n_total`, append a single leading space, then an en-dash, then a space, then the literal text `narrow the target with a path or glob`. Otherwise empty.
