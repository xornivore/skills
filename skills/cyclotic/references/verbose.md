# Verbose output and drill-down

Load this file only when the run asks for detail. A plain `prep` or `review`
renders from [presentation.md](./presentation.md) and never needs what is here.

Everything below reads the same fact sheet the summary report read. Verbose runs
add no queries — see
[hard rule 3](../SKILL.md#3-never-re-query-after-ingest).

## Triggers

| Phrasing | Renders |
| --- | --- |
| `cyclotic prep -v`, `--verbose`, `verbose`, `in detail` | the normal report, plus the inventory and per-person arithmetic |
| `cyclotic show cards`, `list tickets`, `list cards`, `with sizes`, `what is in the cycle` | the inventory alone |
| `cyclotic why chen`, `explain chen`, `how is chen 6.0d`, `break down chen` | one person's arithmetic alone |
| `cyclotic prep for chen -v` | Chen's arithmetic plus Chen's inventory |

`show cards` and `explain` accept the same mode words as any other run, so
`cyclotic show cards for next` lists the next cycle's tickets and
`cyclotic review -v` renders the verbose review.

## The rule verbose puts under most pressure

Detail is the shortest path to a performance-review instrument, and this is the
feature that will get there first if nobody watches it. Re-read
[hard rule 5](../SKILL.md#5-judge-the-plan-never-the-person) before rendering
anything here.

Verbose adds **rows and arithmetic**. It never adds judgment.

- Never sort or rank people by load, ticket count, or day total. Keep the roster
  in config order, always, so the table cannot be read as a leaderboard.
- Never render a per-person completion figure, in any mode.
  `cyclotic review -v` renders more carryover detail and more of the day
  arithmetic — never "Chen completed 4 of 7."
- Never annotate a row with anything but the numbers and the flags that already
  fired. No "light week", no "heavily loaded", no comparison to the roster
  average.

Correct: `Chen  6.0d+  10.0d  UNDER?  3 unestimated`, then Chen's six tickets
with their sizes.

Wrong: `Chen  6.0d+  (lowest on the team)` — a true statement, and a ranking.

**Audit:** in rendered verbose output, the roster appears in config order and no
line contains a comparative or an aggregate across people.

## Inventory

Every ticket in the target cycle, grouped by assignee in config order, then
unassigned, then anyone unlisted. Columns: identifier, size label, days, status,
title.

```text
CYCLE 47  prep   Aug 3-16   10 working days   20 tickets

Avery                                                    9.0d / 10.0d
  Ingest v2
    ENG-204  M    2.0d  In Progress  "retry budget for ingest"
    ENG-205  L    3.5d  Todo         "replay from offset"
    ENG-206  XS   0.5d  Todo         "drop the unused flag"
    ENG-260  -    0.0d  Todo         "close the stale ticket"
    ENG-155  M    2.0d  Todo         "retry budget for ingest"
    ENG-160  S    1.0d  In Progress  "replay the dead letters"

Blake                                                    0.0d / 10.0d
  no tickets in this cycle

Chen                                                     6.0d+ / 10.0d
  Auth migration
    ENG-210  M    2.0d  Todo         "auth cache warmup"
    ENG-211  L    3.5d  Todo         "session store cutover"
    ENG-212  XS   0.5d  Todo         "log the reject reason"
    ENG-201  --    --   Todo         "token refresh race"
    ENG-233  --    --   Todo         "audit the scope claims"
    ENG-240  --    --   Todo         "rotate the signing key"

Dara                                                    14.5d / 10.0d
  Ingest v2
    ENG-190  XXL  10.0d  Todo        "rewrite ingest pipeline"
    ENG-191  L     3.5d  Todo        "partition the queue"
    ENG-192  S     1.0d  Todo        "alert on lag"

unassigned                                               3.0d
  Gateway rework
    ENG-244  M    2.0d  Todo         "cache the label lookup"
    ENG-249  S    1.0d  Todo         "trim the debug output"

Priya Raman  (not in roster)                             3.5d
  Ingest v2
    ENG-270  M    2.0d  Todo         "split the ingest reader"
    ENG-271  XS   0.5d  Todo         "docs for the new flag"
    ENG-272  S    1.0d  Todo         "prune the old fixtures"
```

Render an unsized ticket's size and days as `--`, never as `0.0d`. A zero would
be a claim about its cost; `--` says the cycle does not know.

A ticket sized `-` renders `-` and `0.0d`, because zero days is what it means.

Group by project inside each person. A person holding work in four projects in
one cycle is a fact the summary table cannot show, and it is often the answer to
why their week is fragmented.

## Per-person arithmetic

What `explain` and a filtered verbose run render. Show the sum, the available-day
derivation, and everything excluded from both.

```text
Chen        6.0d+ against 10.0d       UNDER?

load        Auth migration
              ENG-210  M    2.0d
              ENG-211  L    3.5d
              ENG-212  XS   0.5d
                            -----
              sized         6.0d
              unsized       3 tickets, unknown days
                            -----
              total         6.0d+

available   10 working days   Aug 3-16, weekdays only
            no rotation in this cycle
                            -----
              total         10.0d

delta       not computed — 3 unsized tickets could be 1.5d or 30d

excluded    ENG-201  "token refresh race"        no estimate
            ENG-233  "audit the scope claims"    no estimate
            ENG-240  "rotate the signing key"    no estimate
```

Show the on-call subtraction when there is one, with the shift dates and the
cap that applied:

```text
available   10 working days   Aug 3-16, weekdays only
            oncall  Interrupts  Aug 3-7   5 weekdays  -5.0d
                    capped at oncall_cost_days = 5
                            -----
              total          5.0d
```

The `excluded` block is the point of this layout. A person's load is a number
built by leaving things out, and the summary row can only say how many were left
out. Naming them is what makes the number actionable — each line is a ticket
somebody has to size.

When the person holds no unsized tickets, render the signed delta in place of the
`not computed` line and omit the `excluded` block.

## Verbose team run

`cyclotic prep -v` renders, in order:

1. The normal `prep` report, unchanged, per
   [presentation.md](./presentation.md).
2. The inventory.
3. Per-person arithmetic for every roster member, in config order.

The summary comes first and stays intact. Someone who asked for detail still
wants the answer before the evidence, and re-ordering it so the tables come
first buries the flags.

## Follow-up questions

The fact sheet holds more than any layout renders — every ticket's project,
status, timestamps, and day value, plus the blind spots. After rendering, keep it
and answer follow-ups from it.

Answer directly, in a sentence or a few rows. Do not re-render the whole report
because one question was asked about one ticket.

Correct: asked "what project is ENG-233 in?", answer `Auth migration` from the
fact sheet.

Correct: asked "who has the XXL?", answer `Dara, ENG-190 "rewrite ingest
pipeline"` from the fact sheet.

Wrong: calling `list_issues` again to answer either — see
[hard rule 3](../SKILL.md#3-never-re-query-after-ingest).

A question the fact sheet cannot answer is a **new run**, not a new query. Say
which mode or scope would answer it and offer to run it.

Correct: asked "what did Chen finish last cycle?" during a `prep` run, say that
the run holds only the active cycle and offer `cyclotic review`.

Wrong: quietly querying the previous cycle mid-conversation, which produces
numbers from two different ingest passes in one thread with nothing marking the
seam.

## What verbose never adds

- A per-person completion or accuracy figure, in any mode.
- Any figure spanning more than the target cycle.
- Commentary on a person, a ranking, or a roster average.
- A ninth flag. Verbose shows the fact sheet's contents; it does not judge them.
