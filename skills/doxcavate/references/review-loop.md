# Review loop

Orchestrates factcheck and persona reviews. See
[factcheck](./factcheck.md) and [persona-review](./persona-review.md)
for the per-pass details. This file owns the loop and termination
rules.

## Default flow

```text
draft
  → factcheck
  → persona review (≤7 ranked items)
  → authoring agent applies all items
  → focused factcheck (only the regions the persona pass changed)
  → done
```

- **Default: single round.** One factcheck, one persona pass, one
  focused factcheck on the applied changes. No automatic re-run of
  persona.
- **Done** = focused factcheck clean, no outstanding contradictions.
  Unverifiable claims aren't contradictions; they ship with the
  `> note: not independently verified` callout.
- **Doc updates** (refresh of an existing doc): factcheck scopes to
  changed claims; persona runs only if the change is reader-visible
  (sectioning, anchors, voice). Internal-only edits skip persona by
  default.

## Opt-in deviations

Two deviations are supported, signaled either via prompt hint or
`.doxcavate.yml`:

- **Thorough mode** — runs to fixed-point with a hard cap of 3 full
  rounds. Stops when the persona pass returns zero items, the
  factcheck pass shows zero contradictions, or the cap fires. Use
  when stakes warrant it (a cornerstone runbook, a learning path many
  newcomers will touch).
- **Skip persona** — runs factcheck only. Use for bulk-migration or
  format-only edits. Never available for newly drafted docs.

```yaml
# .doxcavate.yml
review:
  thorough: false        # default; true = run-to-fixed-point, cap 3 rounds
  persona: required      # default; "optional" = honor "skip persona" prompt hints
```

Prompt hints recognized by the skill: "rigorously" / "thorough review"
→ thorough mode; "skip persona" / "mechanical" / "format-only" → skip
persona (only when `review.persona: optional`).

## Why explicit halt

Silent truncation of a broken draft trains future readers to distrust
the doc — they hit one wrong claim and stop trusting the rest. The
factcheck and persona escape hatches
(`E_TOO_MANY_CONTRADICTIONS`, `E_PERSONA_OVERFLOW`) cost more upfront
but produce docs that stay trustworthy. They are the design choice
that makes the ≤7-item brevity cap honest.

## Action checklist (after a draft is produced)

1. Run [factcheck](./factcheck.md). If thresholds tripped → halt with
   `E_TOO_MANY_CONTRADICTIONS`.
2. Run [persona-review](./persona-review.md). If reviewer reports
   `E_PERSONA_OVERFLOW` → halt.
3. Apply all returned items, preferring `patch` over textual
   instruction.
4. Run focused factcheck on changed regions only.
5. If thorough mode (config or prompt hint), repeat 1–4 until
   factcheck shows zero contradictions and persona returns zero
   items, or until 3 rounds elapsed.
6. Done.
