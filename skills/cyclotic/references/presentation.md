# Presentation

Plain text, rendered as markdown. No ANSI escapes, no emoji, no image export,
no palette. See [hard rule 7](../SKILL.md#7-plain-text-only).

No queries in this phase. Everything rendered here comes from the fact sheet.

## `prep` section order

1. **Header** — cycle name and number, mode, date range, working days.
2. **Capacity table** — one row per roster member: load, available, signed
   delta, verdict, notes.
3. **CARRYOVER FROM prior-cycle** — grouped never-started, in-progress,
   in-review. Headed `ALREADY IN FLIGHT` in `prep next`.
4. **NO ESTIMATE** — identifier, assignee, title.
5. **NEEDS SPLIT** — identifier, assignee, size, title.
6. **UNASSIGNED IN CYCLE** — identifier, size, title, with the day total in the
   heading.
7. **BACKLOG BEHIND THE CYCLE** — readiness table, one row per project, with a
   trailing list of the owned-but-unscheduled identifiers.
8. **UNLISTED IN ROSTER** — name, issue count, day total.
9. **Footer** — blind spots.

Every section that names an issue renders its title. Titles arrive in the same
query as the estimate, so they cost nothing, and an identifier alone cannot be
discussed without opening Linear — which defeats the point of a report someone
reads during planning.

### Header date range

Render the cycle's **calendar** range, from `first_day` to `last_day`. The
working-day count is stated beside it and does the other job.

Correct: `CYCLE 47  prep   Aug 3-16   10 working days`

Wrong: `CYCLE 47  prep   Aug 3-14   10 working days` — Aug 14 is the last
weekday, not the last day. It silently contradicts `last_day` in the fact sheet
and makes the cycle look shorter than Linear shows it.

Use `Mon D-D` inside one month and `Mon D-Mon D` across a boundary, as in
`Jul 20-Aug 2`.

Omit empty sections entirely. The capacity table is the exception: in `prep` it
renders even when every row is unremarkable, because a table of four `full`
rows is the answer to "is this cycle allocated."

## `review` section order

1. **Header.**
2. **Landed line** — `landed N of M issues, Xd of Yd`. Team level only. `M`
   comes from the cycle's `issueCountHistory`, not from counting current
   members — see [ingest.md](./ingest.md). Suffix `Y` with `+` when any issue
   in the cycle had no estimate, or when the reconciliation left an issue
   unattributed. The `+` means the same thing it means in the capacity table:
   plus an unknown amount.
3. **CARRYING INTO next-cycle** — same three-way grouping as carryover.
4. **NO ESTIMATE, SO UNCOUNTED** — issues excluded from the day totals.
5. **Footer.**

No capacity table, and no per-person completion figure anywhere.

## Filtered runs

`for someone` collapses to person-major:

1. That person's capacity row.
2. Their target-cycle issues grouped by project, with sizes.
3. Only the flags touching them.
4. The readiness rows for projects they lead or hold work in.

Suppress the team capacity table. A filtered run must not become a back-door
team comparison — see
[hard rule 5](../SKILL.md#5-judge-the-plan-never-the-person).

Correct, for `cyclotic prep for chen`: Chen's row, Chen's issues, the
`NO ESTIMATE` entries that are Chen's.

Wrong: the full four-row capacity table with Chen's row marked, which invites
exactly the comparison the rule exists to prevent.

## Verbose and drill-down runs

Verbose runs, the full ticket inventory, and `explain` requests have their own
layouts in [verbose.md](./verbose.md). Load that file only when the run asks for
one; a plain `prep` never needs it.

## Column alignment

Use a fixed-width block for the capacity table and the readiness table.
Alignment carries meaning there: a reader scans the delta column vertically to
find who is out of balance, and ragged columns defeat that.

Use ordinary prose lists everywhere else.

Right-align numeric columns. Render every day figure to one decimal place with
a `d` suffix, so `6d` renders as `6.0d`.

## Reference layout

```text
CYCLE 47  prep   Aug 3-16   10 working days

                load     avail     delta  verdict  notes
 Avery          9.0d     10.0d      -1.0  UNDER
 Blake          0.0d     10.0d            EMPTY
 Chen           6.0d+    10.0d            UNDER?   3 unestimated
 Dara          14.5d     10.0d      +4.5  OVER

CARRYOVER FROM 46 (2)
  never started (1)
    ENG-155  Avery   M    "retry budget for ingest"
  in progress (1)
    ENG-160  Avery   S    7d since started

NO ESTIMATE (3)
  ENG-201  Chen  "token refresh race"
  ENG-233  Chen  "audit the scope claims"
  ENG-240  Chen  "rotate the signing key"

NEEDS SPLIT (1)
  ENG-190  Dara  XXL  "rewrite ingest pipeline"

UNASSIGNED IN CYCLE (2, 3.0d)
  ENG-244  M  "cache the label lookup"
  ENG-249  S  "trim the debug output"

BACKLOG BEHIND THE CYCLE
                    ready   unsized   owned/unsched
 Gateway rework         3         9         2        no lead
 Ingest v2              4         0         0
 Auth migration         0         6         1
  owned/unsched: ENG-248 Avery · ENG-251 Blake · ENG-263 Chen

UNLISTED IN ROSTER (1, 3.5d)
  Priya Raman  3 issues  3.5d  — add to config?

rotations not checked (no schedules configured); available days may be
overstated. 3 issues excluded from day totals for having no estimate.
never-started carryover is inferred from creation date; an issue created
during cycle 46 and never started cannot be told apart from new work.
```

This layout is the `messy` fixture rendered, so the arithmetic in it can be
checked against `tests/fixtures/messy.mcp.yaml`.

## `review` reference layout

```text
CYCLE 46  review   Jul 20-Aug 2   10 working days

landed 7 of 14 issues, 15.0d of 24.5d+

CARRYING INTO 47 (5 issues, 10 pts)
  never started (2)
    ENG-111  Blake   M    "retry budget"
    ENG-252  Chen    --   "audit the scope claims"
  in progress (1)
    ENG-110  Chen    L    12d since started
  in review (1)
    ENG-112  Avery   S    6d since started

NO ESTIMATE, SO UNCOUNTED (1)
  ENG-252  Chen  "audit the scope claims"

1 issue left cycle 46 that could not be matched to a named ticket.
rotations not checked (incident.io MCP not installed); available days
may be overstated. 1 issue excluded from day totals for having no
estimate. never-started carryover is inferred from creation date; an
issue created during cycle 46 and never started cannot be told apart
from new work.
```

The heading says 5 issues while 4 are named, because the heading count is
authoritative and the fifth cannot be attributed. The footer carries the gap.
This layout is the `cycle-close` fixture rendered.

## Footer wording

One line per blind spot, and only when true. Fixed wording so it is greppable:

| Condition | Line |
| --- | --- |
| rotations checked | `rotations checked: NAMES.` |
| no rotation data | `rotations not checked (REASON); available days may be overstated.` |
| unestimated excluded | `N issues excluded from day totals for having no estimate.` |
| backlog truncated | `backlog query truncated at the page cap for PROJECTS.` |
| roster unresolved | `roster names not resolved to a Linear user: NAMES.` |
| carryover unattributed | `N issues left cycle NUMBER that could not be matched to a named ticket.` |
| carryover overshoot | `N classified issues exceed the NUMBER that left cycle NUMBER; some are not carryover.` |
| never-started inferred | `never-started carryover is inferred from creation date; an issue created during cycle NUMBER and never started cannot be told apart from new work.` |
| no prior cycle | `no prior cycle, so never-started carryover was not checked.` |
| unmapped size | `estimate value N has no entry in capacity.sizes; counted as unknown.` |

The never-started line renders whenever that bucket is evaluated, hit or miss.
An empty bucket is exactly the case a reader would otherwise take as proof that
nothing was left unstarted.

See [hard rule 6](../SKILL.md#6-state-blind-spots-once).
