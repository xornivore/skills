# Presentation

Plain text, rendered as markdown. No ANSI escapes, no emoji, no image export,
no palette. See [hard rule 7](../SKILL.md#7-plain-text-only).

No queries in this phase. Everything rendered here comes from the fact sheet.

## `prep` section order

1. **Header** — cycle name and number, mode, date range, working days.
2. **Capacity table** — one row per roster member: load, available, signed
   delta, verdict, notes.
3. **CARRYOVER FROM prior-cycle** — grouped never-started, in-progress,
   in-review.
4. **NO ESTIMATE** — identifier and assignee.
5. **NEEDS SPLIT** — identifier, assignee, size, title.
6. **UNASSIGNED IN CYCLE** — identifier and size, with the day total in the
   heading.
7. **BACKLOG BEHIND THE CYCLE** — readiness table, one row per project, with a
   trailing list of the owned-but-unscheduled identifiers.
8. **UNLISTED IN ROSTER** — name and issue count.
9. **Footer** — blind spots.

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

## Column alignment

Use a fixed-width block for the capacity table and the readiness table.
Alignment carries meaning there: a reader scans the delta column vertically to
find who is out of balance, and ragged columns defeat that.

Use ordinary prose lists everywhere else.

Right-align numeric columns. Render every day figure to one decimal place with
a `d` suffix, so `6d` renders as `6.0d`.

## Reference layout

```text
CYCLE 47  prep   Aug 3-14   10 working days

                load     avail     delta  verdict  notes
 Avery          6.0d     10.0d      -4.0  UNDER
 Blake          4.0d      5.0d      -1.0  UNDER    oncall: Interrupts Aug 4-8
 Chen           6.0d+    10.0d            UNDER?   3 unestimated
 Dara          14.5d     10.0d      +4.5  OVER

CARRYOVER FROM 46 (6)
  never started (3)
    ENG-155  Blake   M    "retry budget for ingest"
  in progress (2)
    ENG-160  Avery   L    9d since started
  in review (1)
    ENG-171  Chen    S    4d since started

NO ESTIMATE (3)
  ENG-201 Chen · ENG-233 Chen · ENG-240 Chen

NEEDS SPLIT (1)
  ENG-190  Dara  XXL  "rewrite ingest pipeline"

UNASSIGNED IN CYCLE (2, 3.0d)
  ENG-244  M · ENG-249  S

BACKLOG BEHIND THE CYCLE
                    ready   unsized   owned/unsched
 Gateway rework         3         9         2        no lead
 Ingest v2              4         0         0
 Auth migration         0         6         1
  owned/unsched: ENG-248 Avery · ENG-251 Blake · ENG-263 Chen

UNLISTED IN ROSTER (1)
  Priya Raman  3 issues  — add to config?

rotations checked: Interrupts. 3 issues excluded from day totals for
having no estimate.
```

## `review` reference layout

```text
CYCLE 46  review   Jul 20-31   10 working days

landed 28 of 48 issues, 41.0d of 79.5d+

CARRYING INTO 47 (16 issues, 33 pts)
  never started (7)
    ENG-155  Blake   M    "retry budget for ingest"
  in progress (5)
    ENG-160  Avery   L    9d since started
  in review (1)
    ENG-171  Chen    S    4d since started

NO ESTIMATE, SO UNCOUNTED (4)
  ENG-201 Chen · ENG-233 Chen · ENG-240 Avery · ENG-252 Blake

3 issues left cycle 46 that could not be matched to a named ticket.
rotations not checked (incident.io MCP not installed); available days
may be overstated.
```

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
| unmapped size | `estimate value N has no entry in capacity.sizes; counted as unknown.` |

See [hard rule 6](../SKILL.md#6-state-blind-spots-once).
