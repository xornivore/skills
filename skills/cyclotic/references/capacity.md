# Capacity math

Pure arithmetic over the fact sheet. No queries.

## Load

For each roster member, sum `capacity.sizes[estimate.value].days` over their
issues in the target cycle.

An issue with **no `estimate` key** contributes `0` days and increments that
person's `unestimated` counter.

An issue with an `estimate` key whose `value` is `0` — Linear's `-` size —
contributes `0` days and does **not** increment `unestimated`. It is sized,
and the answer was zero.

An issue whose `estimate.value` has no entry in `capacity.sizes` contributes
`0` days, increments `unestimated`, and adds a blind spot naming the unmapped
point value. This happens when a team extends its scale after `init` ran.

## Available days

Start at the cycle's working-day count, taken from Linear's dates per
[ingest.md](./ingest.md).

For each on-call shift mapped to that person:

1. Count the shift's weekdays that fall inside the cycle window.
2. Cap that count at `capacity.oncall_cost_days`.
3. Subtract.

Floor the result at `0`.

A shift straddling a cycle boundary is charged only for the part inside the
cycle. A one-week rotation fully inside a ten-day cycle costs 5 days. The same
rotation split across two cycles costs each cycle only its own days.

## Verdict

In precedence order:

| Verdict | Condition |
| --- | --- |
| `EMPTY` | zero issues in the target cycle |
| `OVER` | load is greater than available |
| `full` | load equals available |
| `UNDER` | load is less than available |

`EMPTY` outranks `UNDER`. Having no work at all is a different problem from
having light work, and collapsing the two hides the person nobody planned for.

There is no tolerance band and no configurable threshold. Render the signed
delta next to the verdict so magnitude is visible without inventing a knob. A
row reading `-0.5 UNDER` is half a day short and needs no attention, while
`+11.0 OVER` is two weeks of work that will not fit.

## Unestimated suppresses the delta

When a person's `unestimated` count is above zero:

- Render their load with a trailing `+`, meaning "plus an unknown amount."
- Render no signed delta. The real delta is unknown, and a number computed
  over the sized issues alone is made up.
- Render the verdict as `UNDER?` with the count, never a bare `UNDER`.

Correct:

```text
 Chen           6.0d+    10.0d            UNDER?   3 unestimated
```

Wrong:

```text
 Chen           6.0d     10.0d      -4.0  UNDER
```

`OVER` is still reported plainly when load already exceeds available, because
unestimated work can only push it further over. A person at `14.5d` against
`10.0d` with two unestimated tickets renders `14.5d+ ... OVER` with the count
in notes, and no delta.

See [hard rule 4](../SKILL.md#4-unestimated-work-never-reads-as-spare-capacity).

## Rounding

Sum in the day units from config, then render to one decimal place. Do not
round intermediate sums — four `XS` tickets at 0.5 days are 2.0 days, not
4 × 1.

## What is never computed

- A person's completion percentage, in any mode.
- Any per-person figure spanning more than the target cycle.
- A ranking of roster members against each other.
- An estimate-accuracy or velocity number.

`review` totals completions at team level only, so no per-person figure exists
to rank. See [hard rule 5](../SKILL.md#5-judge-the-plan-never-the-person).
