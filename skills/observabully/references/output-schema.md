# Output schema

Load this reference at pipeline step 4.5 (rank and emit). It controls
finding render format and footer accounting. Read it at step 4.5 — not before.

## Finding shape

Each finding is a structured Markdown block. The structure is fixed so a
follow-up turn ("now fix #3") can address findings by index. Render each
finding through [assets/finding-template.md](../assets/finding-template.md).

Example finding block:

```text
[3] missing-telemetry · high · pkg/ingest/handler.go:84
    Operation `IngestBatch` runs three external calls (Kafka publish,
    S3 put, Postgres write) without a span or structured log at the
    boundary. A failure in any one is currently indistinguishable
    from the others in production logs.
    Suggest: wrap the operation in a span named `ingest.batch` with
    attributes batch_size, source. Emit one structured log at start
    and one at end with a stable event name.
```

### Field rules

- **index** — 1-based; stable within a single run.
- **dimension** — one of `missing-telemetry`, `poor-practices`,
  `structure-for-telemetry`.
- **severity** — `high` | `med` | `low`. Severity is decided by the rubric
  file that produced the finding.
- **`file:line`** — line numbers point to the most informative line for the
  finding (start of the operation, not start of the file).
- **why this matters** — 1–2 lines, concrete consequence. "A failure in any
  one is currently indistinguishable from the others in production logs" is
  acceptable; "improves observability" is not.
- **suggest** — the *shape* of the fix, not a code patch. Names a span,
  metric, log event, or structural change. If the codebase already uses
  OTel / slog / zap / structlog, the suggestion uses that vocabulary;
  otherwise it stays neutral.

## Ranking

Sort surviving findings by the following three-tier key, in order:

1. **Dimension severity.** `missing-telemetry` at request boundaries outranks
   `structure-for-telemetry`, which outranks `poor-practices`. Severity per
   finding is `high` / `med` / `low` per the rubric file.
2. **Blast radius.** Findings on a public/exported boundary outrank findings
   inside an internal helper.
3. **File path** (lexical, for stability).

## Footer

After all findings are emitted, render the footer block once:

```text
---
scanned: 47 files
skipped: 19 (generated: 8, no-io: 6, test-fixture: 4, pure-data: 1)
fp-dropped: 12
shown: 20 of 23 findings — narrow the target with a path or glob
```

Footer fields and their sources:

- `scanned` — count from step 4.1.
- `skipped` — count from step 4.2 rejection log; reasons grouped per the
  fixed set in [references/precheck.md](./precheck.md).
- `fp-dropped` — count from step 4.4.
- `shown` and overflow note — counts from this step (4.5).

## Bounded output

Cap output at `--max` findings (default 20). When the total surviving finding
count exceeds `--max`, render only the top `--max` findings and append the
overflow note in the footer's `shown` line.

The overflow note must read: `— narrow the target with a path or glob`.
Never truncate silently — always surface the overflow count.

**Wrong:** emit 20 findings with `shown: 20 of 23 findings` and no overflow
note, leaving the user unaware that 3 findings were suppressed.

**Correct:** emit 20 findings with
`shown: 20 of 23 findings — narrow the target with a path or glob`.

**Audit:** if the candidate finding count exceeds `--max`, the emitted output
must contain the string `narrow the target`.

## Skip accounting

Every excluded file must be counted in the footer's `skipped` field under one
of the fixed reason words from [references/precheck.md](./precheck.md). No
file is silently excluded.

**Wrong:** exclude 5 generated files and 3 test-fixture files, then emit
`skipped: 5 (generated: 5)` — the 3 test-fixture files are unaccounted for.

**Correct:** emit `skipped: 8 (generated: 5, test-fixture: 3)` — every
excluded file appears in the tally.

**Audit:** `scanned + skipped` in the footer must equal the resolved file
count from pipeline step 4.1.

## Action checklist

At pipeline step 4.5:

1. Sort surviving findings per the ranking rules above.
2. Assign 1-based indices.
3. Render each finding through [assets/finding-template.md](../assets/finding-template.md).
4. Render the footer block, populating skip-reason counts from the precheck
   step's rejection log and `fp-dropped` from the FP-review step's drop count.
5. If the total exceeds `--max`, render only the top `--max` and append the
   overflow note.
