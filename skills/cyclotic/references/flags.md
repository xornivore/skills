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

Fires on unfinished work that crossed a cycle boundary, classified per
[ingest.md](./ingest.md). Subdivide by why it did not land:

- **never started** — `statusType` of `backlog` or `unstarted`, created before
  the boundary. The sharpest signal: it was planned, and nothing happened.
- **in progress** — `statusType` of `started`, work began before the boundary.
- **in review** — a `started` issue whose `status` matches the team's review
  wording, when the team has such a state.

Order the buckets never-started, in-progress, in-review. Never-started leads
because it is the one that needs a decision rather than a nudge.

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

Carry the issue count. In `review`, also carry the point total that left the
cycle, taken from the cycle's own history arrays.

When the reconciliation in [ingest.md](./ingest.md) shows fewer classified
issues than the cycle's totals imply, the difference goes in the footer as a
blind spot. Never pad the list to match the total.

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

Name the person, their issue count, and offer to add them to the roster.

Without this flag, someone who joins the team and is never added to `members`
has their work dropped from every report, and nothing in the output says so.

This is the one flag whose offer leads to a config write, and only through the
init flow with the usual confirmation. Never edit config silently.

## Fixture expectations

Fixtures under `tests/fixtures/` are agent-verifiable scenarios, not an
automated suite. Read a fixture, run the arithmetic by hand, and compare.

| Fixture | Expected |
| --- | --- |
| `healthy.mcp.yaml` | every row `full` or a small negative `UNDER`; no F3, F4, F5, F8; F7 shows non-zero `ready` for every project |
| `messy.mcp.yaml` | one `OVER`, one `EMPTY`, one `UNDER?` with suppressed delta, F4 on one `XXL`, F5 with a day total, F8 naming one person |
| `cycle-close.mcp.yaml` | `review` mode; landed line denominator from `issueCountHistory`, not current members; carryover split across all three buckets; a reconciliation blind spot in the footer |
