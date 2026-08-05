# Flags

Every flag fires from the fact sheet alone. No queries.

| # | Flag | Fires when | Surfaces as | Modes |
| --- | --- | --- | --- | --- |
| F1 | over capacity | load is greater than available | capacity-table verdict | prep |
| F2 | empty | roster member with zero issues in the target cycle | capacity-table verdict | prep |
| F3 | no estimate | assigned target-cycle issue with no `estimate` key | own section | prep, review |
| F4 | needs split | target-cycle issue sized `XL` or larger | own section | prep |
| F5 | unassigned in cycle | target-cycle issue with no `assignee` key | own section | prep |
| F6 | carryover | unfinished work that crossed a cycle boundary | own section | prep, review |
| F7 | backlog readiness | per in-scope project, see below | own section | prep |
| F8 | unlisted contributor | target-cycle assignee absent from the roster | own section | prep |

F1 and F2 never get their own section — they are verdicts in the capacity
table, which is why `prep` has no `OVER CAPACITY` heading. `review` renders
neither, because it has no capacity table.

`review` carries only F3 and F6. It reports what landed and what is leaving
unfinished. Sizing, assignment, and backlog grooming are decisions for the
cycle being planned, not the one already closed.

## F3 no estimate

Fires on an assigned target-cycle issue with **no `estimate` key**.

A ticket sized `-` (Linear's explicit zero) does not fire this flag. Someone
sized it and the answer was zero, which is an answer. Flagging it would nag
about a decision that was already made and would suppress that person's
capacity delta for no reason.

Correct: `ENG-201 Chen` listed, where `ENG-201` has no `estimate` key.

Wrong: `ENG-244 Chen` listed, where `ENG-244` has
`estimate: {value: 0, name: "-"}`.

**Audit:** every identifier in this section corresponds to a fact-sheet issue
with no `estimate` key.

## F4 needs split

Fires on a target-cycle issue whose `estimate.name` is `XL`, `XXL`, `XXXL`, or
anything the team's scale places above `XL`. Match on the label from
`estimate.name`, not on a hardcoded point value — a team using raw Fibonacci
labels its own sizes.

A ticket estimated at a week or more offers no checkpoint inside the cycle.

A team whose scale tops out at `L` never sees this flag, and must not: `L` is
three to four days.

Render identifier, assignee, size, and title — the title is what makes a split
discussable.

## F5 unassigned in cycle

Fires on a target-cycle issue with no `assignee` key.

Carry a **day total in the heading**, not only a count. These issues are sized
and committed but sit in nobody's load, so without the total they are the one
pool of cycle work that no figure in the report accounts for.

Correct: `UNASSIGNED IN CYCLE (2, 3.0d)`

Wrong: `UNASSIGNED IN CYCLE (2)`

## F6 carryover

Fires on unfinished work that crossed a cycle boundary. The boundary differs per
mode and per bucket — take it from
[classifying carryover](./ingest.md#classifying-carryover) rather than assuming
one boundary serves all three:

- **never started** — `statusType` of `backlog` or `unstarted`, created before
  the **prior cycle's start** in `prep`, or before the target's end in `review`.
  The sharpest signal: it was planned, and nothing happened. Inferred from
  `createdAt`, not proven, so it always carries a footer caveat.
- **in progress** — `statusType` of `started`, work began before the boundary.
  Proven by `startedAt`.
- **in review** — a `started` issue whose `status` matches the team's review
  wording, when the team has such a state.

Order the buckets never-started, in-progress, in-review. Never-started leads
because it is the one that needs a decision rather than a nudge.

In `prep next` the section is headed `ALREADY IN FLIGHT` and carries no
never-started bucket. Nothing has rolled out of the active cycle, because it has
not closed.

### Days figure

Render in-progress and in-review issues with days since `startedAt`, labelled
`since started`.

Count **calendar days**, as `date(today) - date(startedAt)` — not elapsed hours
floored to a whole number. An issue started late on Jul 22 and read on Aug 3 is
12 days old, not 11. Flooring elapsed time makes the figure jitter with the
hour a run happens, so two runs on the same day disagree.

Linear's MCP surface exposes no per-state transition timestamp — there is no
field for when an issue entered its current state. `startedAt` records when
work first began. Label the figure for what it is.

Correct: `ENG-160  Avery  L   9d since started`

Wrong: `ENG-160  Avery  L   9d in review` — implies a measurement of time in
the review state, which is not available.

### Heading

In `prep`, carry the classified issue count. In `review`, carry the
authoritative count and point total that left the cycle, both derived in
[reconciling](./ingest.md#reconciling-against-the-cycles-own-totals) — the count
is `left`, and the point total is `scopeHistory[last]` minus the points of the
issues still in the cycle.

Correct, for `review`: `CARRYING INTO 47 (5 issues, 10 pts)`

Correct, for `prep`: `CARRYOVER FROM 46 (6)`

The `review` heading is authoritative, so it can exceed the number of issues
named beneath it. That shortfall goes in the footer as a blind spot. Never pad
the list to match the total.

## F7 backlog readiness

Classifies each in-scope project's issues that are in no cycle across two
axes, assigned and sized:

| Cell | Meaning |
| --- | --- |
| unassigned + sized | **ready** — the queue to pull from. Healthy. |
| unassigned + unsized | **unsized** — no estimate, so no way to fit it in a cycle |
| assigned + either | **owned/unsched** — someone owns it, nothing schedules it |

Report **every** in-scope project, not only the troubled ones. A project with
a good `ready` count and zero `unsized` still gets a row — a lead planning the
next cycle needs to see which projects have sized work waiting and which have
nothing to pull from.

Mark a project with no `lead` as `no lead` in the notes column.

List the `owned/unsched` identifiers under the table. They are the actionable
cell: each one is a decision someone already made and then dropped.

## F8 unlisted contributor

Fires when a target-cycle issue's assignee is not in the config roster.

Name the person, their issue count, their day total, and offer to add them to
the roster.

Carry the **day total in the heading**, for the same reason F5 does: an unlisted
contributor has no capacity row, so their committed work is counted nowhere else
in the report. Reporting three issues without their 3.5 days hides the size of
the hole.

Correct: `UNLISTED IN ROSTER (1, 3.5d)`

Wrong: `UNLISTED IN ROSTER (1)`

Without this flag, someone who joins the team and is never added to `members`
has their work dropped from every report, and nothing in the output says so.

This is the one flag whose offer leads to a config write, and only through the
init flow with the usual confirmation. Never edit config silently.

## Fixture expectations

Fixtures under `tests/fixtures/` are agent-verifiable scenarios, not an
automated suite. Read a fixture, run the arithmetic by hand, and compare.

| Fixture | Expected |
| --- | --- |
| `healthy.mcp.yaml` | every row `full` or a small negative `UNDER`; no F3, F4, F5, F6, F8; F7 shows non-zero `ready` for every project |
| `messy.mcp.yaml` | one `OVER`, one `EMPTY`, one `UNDER?` with suppressed delta, F4 on one `XXL`, F5 and F8 both carrying a day total, F6 with exactly two issues out of twenty |
| `cycle-close.mcp.yaml` | `review` mode; landed line denominator from `issueCountHistory`, not current members; carryover split across all three buckets; a reconciliation blind spot in the footer |

The prep-mode carryover boundary is the one both prep fixtures are built to
catch. `healthy` has 15 unstarted tickets and `messy` has 17, all created before
their target cycle opened. Testing `createdAt` against the target's `startsAt`
reports every one of them as carryover; testing it against the prior cycle's
`startsAt` reports none in `healthy` and exactly the two planted in `messy`. A
run that fires F6 on more than two tickets in `messy` has the wrong boundary.
