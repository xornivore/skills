# Ingest and fact sheet

Every Linear and incident.io read happens in this phase and lands in the fact
sheet. Rendering consumes only the fact sheet — never re-query afterwards.

## Linear MCP response shapes

These shapes are what the MCP actually returns. Relying on a different shape
produces a report that looks right and is wrong.

**Null fields are omitted entirely**, not returned as `null`. An issue with no
estimate has no `estimate` key at all; an unassigned issue has no `assignee`
key; an issue outside any project has no `project` key. Test for key
presence, never for a `null` value.

**`id` on an issue is the human identifier**, such as `ENG-201`. There is no
separate `identifier` field. Render `id` directly.

**`estimate` is an object**, not a number:

```json
{ "id": "ENG-204", "estimate": { "value": 3, "name": "M" } }
```

`value` is the numeric point value; `name` is the team's own label for it
(`XS`, `S`, `M`, `L`, `XL`, `XXL`, `XXXL`, or `-`). Take the label from
`estimate.name` rather than deriving it from the point value — the team's
scale is authoritative and this is where it surfaces.

`estimate.name` of `-` is Linear's explicit zero estimate. It is a deliberate
sizing decision meaning "this costs nothing," and it is **sized**. Only a
missing `estimate` key is unestimated. When `estimate.value` is `0` but the
key is present, treat it as sized-zero regardless of the label.

**`statusType`** is one of `backlog`, `unstarted`, `started`, `completed`,
`canceled`. Use it for every state decision. Use `status` (the team's own
state name, such as `In Review`) only for matching review wording.

**Pagination** returns `hasNextPage` and `cursor`. Follow the cursor up to the
page cap, then record a blind spot.

**Cycle objects** come back as:

```json
{
  "id": "364ef080-...", "title": "FY27Q3-10", "number": 19,
  "startsAt": "2026-08-03T05:00:00.000Z",
  "endsAt": "2026-08-17T05:00:00.000Z",
  "completedIssueCountHistory": [7], "issueCountHistory": [46],
  "completedScopeHistory": [9], "scopeHistory": [77],
  "isCurrent": true
}
```

The four history arrays are one daily snapshot per element. The **last**
element is the value at the moment the cycle closed. `issueCountHistory` and
`completedIssueCountHistory` count issues; `scopeHistory` and
`completedScopeHistory` total estimate points.

Never convert a `scopeHistory` point total into days. The points-to-days map
is not linear (3 points is 2 days, 5 points is 3.5), so a summed point total
cannot be translated. Day totals are always summed per issue.

## Resolving the target cycle

`list_cycles` accepts only `teamId` and `type`, where `type` is one of
`current`, `previous`, or `next`. There is no way to list all cycles, so
resolve each cycle with its own call:

| Mode | Target cycle | Call |
| --- | --- | --- |
| `prep` | active | `type: current` |
| `prep next` | next upcoming | `type: next` |
| `review` | most recently completed | `type: previous` |

When the call for the target returns an empty array, the team has no such
cycle. Exit with a one-line message naming the team, such as
`Engineering has no active cycle; cycles may be disabled for this team.`
Never fall back to a different cycle.

### Working days

`startsAt` is the first day. **`endsAt` is exclusive** — it is midnight at the
boundary, so it names the day *after* the last day of the cycle.

1. First day is the calendar date of `startsAt`.
2. Last day is the calendar date of `endsAt` minus one day.
3. Working days is the count of Monday-to-Friday dates from first to last,
   inclusive.

A cycle running `2026-08-03T05:00:00Z` to `2026-08-17T05:00:00Z` covers
Aug 3 through Aug 16 and has **10** working days. Treating `endsAt` as
inclusive yields 11 and overstates everyone's available days.

Cycle length varies. Linear teams adjust dates around holidays and offsites,
and a cycle can be 1 to 8 weeks. Always count weekdays from the dates
returned; never assume ten.

## Queries

Request only the fields each table needs. `list_issues` takes a `fields`
array, and narrowing it is what keeps the widest query affordable.

1. **Target cycle** — `list_cycles` per the table above. Also resolve the
   cycle referenced by [carryover](#carryover), and the neighbour cycle whose
   name appears in the carryover heading.
2. **In-scope projects** — `list_projects` for the team. When `labels` is set
   in config, keep only projects carrying **every** listed label. Record each
   project's `lead`.
3. **Target-cycle issues** — `list_issues` with `cycle` set to the target
   cycle's `id`, and `fields` of `title`, `estimate`, `assignee`, `status`,
   `statusType`, `project`, `startedAt`, `createdAt`.
4. **Carryover** — see [carryover](#carryover).
5. **Backlog behind the cycle** — for each in-scope project, `list_issues`
   with `project` set and `fields` of `estimate`, `assignee`, `statusType`,
   `cycleId`. Keep only issues with **no `cycleId` key** and a `statusType` of
   `backlog` or `unstarted`.

`list_issues` has no filter for "in no cycle" — the `cycle` parameter matches
a specific cycle. Query 5 therefore filters on the client side, which makes it
the widest query. Bound it: cap at `backlog_page_cap` pages per project
(default 4 pages of 250) and record a blind spot naming each project that
truncated.

## Carryover

Linear moves unfinished work forward automatically. When a cycle ends, every
open issue rolls into the next cycle, and per Linear's documentation there is
no way to keep unfinished issues in a closed cycle. A closed cycle therefore
contains **only** `completed` and `canceled` issues.

The consequence: querying a closed cycle for issues that are not completed
returns an empty set every time. Read carryover from the cycle the work rolled
**into**, not the one it rolled out of.

| Mode | Target | Read carryover from | Heading |
| --- | --- | --- | --- |
| `prep` | active cycle C | C itself, plus the prior cycle P | `CARRYOVER FROM P` |
| `prep next` | next cycle N | N itself, plus the active cycle C | `CARRYOVER FROM C` |
| `review` | closed cycle T | the cycle after T, which is the active one | `CARRYING INTO name-of-active` |

In `prep` the question is "what arrived here already in flight," so the
landing cycle is the target. In `review` the question is "what is leaving this
cycle unfinished," so the landing cycle is the one after the target; the
target itself is read only for what landed.

### Classifying carryover

Let `B` be the boundary: the target cycle's `startsAt` in `prep`, or the
target cycle's `endsAt` in `review`. For each issue in the landing cycle whose
`statusType` is not `completed` and not `canceled`:

- **in progress** — `startedAt` is present and earlier than `B`, and
  `statusType` is `started`. Work demonstrably began before the boundary, so
  this issue was already in flight.
- **in review** — as above, and `status` matches review wording for this team
  (`In Review`, `Review`, `Code Review`, `PR Review`). Check `status` against
  the team's own state names; a team with no review state has no such bucket.
- **never started** — `statusType` is `backlog` or `unstarted`, and
  `createdAt` is earlier than `B`. The issue was planned before the boundary
  and nothing has happened to it. This is the sharpest signal in the section.

An issue whose `startedAt` is at or after `B` is new work in the landing
cycle, not carryover. Exclude it.

Also query the prior cycle directly for issues that are not `completed` and
not `canceled`. This is normally empty, but catches two real cases: a run made
before the rollover has happened, and an issue deliberately pinned in place.
Merge any hits into the buckets above and dedupe by `id`.

### Reconciling against the cycle's own totals

The classification above is a judgment from timestamps and cannot recover
which issues belonged to the closed cycle at the moment it closed. Its totals
are exact, so use them to bound the report.

For the closed cycle, count how many issues left it:

```text
left = issueCountHistory[last] - count(issues currently in the cycle)
```

The only issues that leave a closed cycle are the ones that rolled forward or
were moved to backlog or triage during cooldown. When the classified carryover
set is smaller than `left`, record the difference as a blind spot rather than
padding the list.

Example: a cycle whose `issueCountHistory` ends at 48 and which now holds 32
issues had 16 leave. Classifying 13 of them leaves 3 unattributed, and the
footer says so.

### Landed line for review

`review` reports what landed at team level only. Take the numerator by
counting issues currently in the target cycle whose `statusType` is
`completed`. Take the denominator from `issueCountHistory[last]`, **not** from
the current member count — the unfinished issues have already left, so
counting current members reports `28 of 32` when the truth is `28 of 48`.

Sum days per completed issue from the sizes map. Never derive days from
`completedScopeHistory`.

## incident.io queries

For each entry in `oncall.schedules`, fetch shifts overlapping the target
cycle's date range. Map each shift's user to a roster member by email first,
then by display name.

incident.io MCP is an **optional dependency**. When it is not installed, or
`oncall.schedules` is empty, or a lookup fails, proceed with no rotation
deductions and record the rotations-not-checked blind spot. Never treat "no
data" as "nobody is on call" — that silently overstates available days.

## Fact sheet

Emit the fact sheet before computing anything. Template at
[assets/factsheet-template.yaml](../assets/factsheet-template.yaml).

It holds: the resolved cycle with working-day count; the roster with resolved
Linear user ids; per-person issue lists with estimates already resolved to day
values; carryover grouped by bucket; in-scope projects with lead and backlog
counts per readiness cell; on-call shifts mapped to roster members; and the
list of blind spots accumulated during ingest.

Anything the report needs must be in here. A fact discovered later is an
ingest bug.
