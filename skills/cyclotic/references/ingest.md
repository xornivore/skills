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

`title` is the only optional key — a cycle with no name omits it. Fall back to
`number`.

The four history arrays are one daily snapshot per element. The **last**
element is the value at the moment the cycle closed. `issueCountHistory` and
`completedIssueCountHistory` count issues; `scopeHistory` and
`completedScopeHistory` total estimate points.

**The history arrays are empty for a cycle that has not started yet.** Check
for an empty array before reading `[last]`, or `prep next` fails on a cycle
that has no snapshots.

Never convert a `scopeHistory` point total into days. The points-to-days map
is not linear (3 points is 2 days, 5 points is 3.5), so a summed point total
cannot be translated. Day totals are always summed per issue.

## Resolving the target cycle

`list_cycles` requires only `teamId`. **`type` is optional, and omitting it
returns every cycle the team has** — past, active, and scheduled. Take one
enumeration call and resolve every cycle the run needs from it. Passing
`type: "all"` is rejected even though the tool description mentions it; omit
the parameter instead.

The response is a bare array with no pagination and **no reliable order**. Sort
by `startsAt`, then read positionally:

| Cycle | Where it is |
| --- | --- |
| active `C` | the entry whose `isCurrent` is `true` |
| prior `P` | the entry immediately before `C` |
| next `N` | the entry immediately after `C` |

Order by `startsAt` rather than by `number`. Cycle numbers can have gaps where
a cycle was deleted, so `C.number - 1` is not reliably the prior cycle.

`isCurrent` is the only temporal flag the server sends. There is no
`completedAt`, `archivedAt`, or status field, so a cycle that closed yesterday
is shaped exactly like an active one apart from this flag. Derive past from
`endsAt` earlier than now, future from `startsAt` later than now.

| Mode | Target cycle |
| --- | --- |
| `prep` | `C` |
| `prep next` | `N` |
| `review` | `P` |

An empty array means cycles are disabled for the team. No entry with
`isCurrent` means the team is between cycles. Either way, exit with a one-line
message naming the team, such as `Engineering has no active cycle; cycles may
be disabled for this team.` Never fall back to a different cycle.

A missing `P` or `N` is ordinary — a team's first cycle has no prior, and a team
that has not scheduled ahead has no next. Handle it where it matters rather than
exiting: `review` and `prep next` have no target and exit, while `prep` runs
without a never-started carryover bucket per [carryover](#carryover).

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

1. **Cycles** — one `list_cycles` call with `teamId` alone, resolved per the
   table above. This single call yields the target, the prior cycle, and the
   next cycle; no further cycle queries are needed.
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

| Mode | Target | Read from | Heading |
| --- | --- | --- | --- |
| `prep` | active cycle `C` | `C` itself, plus the prior cycle `P` | `CARRYOVER FROM P` |
| `prep next` | next cycle `N` | `N` itself | `ALREADY IN FLIGHT` |
| `review` | closed cycle `P` | the active cycle `C` | `CARRYING INTO C` |

In `prep` the question is "what arrived here already in flight," so the cycle
read is the target. In `review` it is "what is leaving this cycle unfinished,"
so the cycle read is the one after the target; the target itself is read only
for what landed.

`prep next` is the exception, and its heading says so. The active cycle has not
closed, so nothing has rolled out of it yet. What a next cycle can show is work
someone began ahead of schedule — real, and worth seeing, but not carryover.
Naming it carryover would report a transfer that has not happened.

### Classifying carryover

Two buckets are provable from timestamps and one is inferred. Keep them apart:
they carry different confidence, and the inferred one is where this section goes
wrong when the boundary is picked carelessly.

**Provable — work demonstrably began before a boundary.** For each issue in the
cycle read above whose `statusType` is `started`:

| Mode | Was already in flight when |
| --- | --- |
| `prep` | `startedAt` is earlier than `C.startsAt` |
| `prep next` | `startedAt` is present at all |
| `review` | `startedAt` is earlier than `P.endsAt` |

Split these into **in progress** and **in review**, where in-review is a
`started` issue whose `status` matches this team's review wording (`In Review`,
`Review`, `Code Review`, `PR Review`). Check `status` against the team's own
state names; a team with no review state has no such bucket.

An issue whose `startedAt` is at or after the boundary is new work, not
carryover. Exclude it.

**Inferred — never started.** An issue with `statusType` of `backlog` or
`unstarted` carries no timestamp saying which cycle it sat in, and Linear does
not retain per-issue cycle membership. So this bucket is a judgment from
`createdAt`:

| Mode | Never started when |
| --- | --- |
| `prep` | `createdAt` is earlier than **`P.startsAt`** |
| `prep next` | no such bucket |
| `review` | `createdAt` is earlier than `P.endsAt` |

In `prep` the boundary is the **prior cycle's start**, not the target's. Every
ticket is created before the cycle it is planned into, so testing `createdAt`
against `C.startsAt` matches all normally-planned work and reports an entire
well-groomed cycle as carryover. An issue that already existed before the
previous cycle began, and is still unstarted, has demonstrably sat through a
cycle.

Correct, for a cycle `C` starting Aug 3 after a cycle `P` starting Jul 20: an
unstarted issue created Jul 15 is carryover.

Wrong: an unstarted issue created Aug 1 counted as carryover. It predates
`C.startsAt`, but it is work planned into `C` during cooldown.

This boundary misses an issue created during `P` and never started — its
`createdAt` falls between `P.startsAt` and `C.startsAt`, where nothing
distinguishes it from work planned into `C`. Record that blind spot rather than
widening the boundary and swamping the section.

When there is no prior cycle, `prep` has no never-started bucket. Say so in the
footer. `prep next` has none either: every issue in a cycle that has not started
yet was created before it, so the test carries no information.

Also query the prior cycle directly for issues that are not `completed` and
not `canceled`. This is normally empty, but catches two real cases: a run made
before the rollover has happened, and an issue deliberately pinned in place.
Merge any hits into the buckets above and dedupe by `id`.

### Reconciling against the cycle's own totals

The classification above is a judgment from timestamps and cannot recover
which issues belonged to the closed cycle at the moment it closed. The cycle's
history arrays are exact, so use them to bound the report.

For the closed cycle, count how many issues left it:

```text
left = issueCountHistory[last] - count(issues currently in the cycle)
```

The only issues that leave a closed cycle are the ones that rolled forward or
were moved to backlog or triage during cooldown, so `left` is the true carryover
count. Compare it against the classified set both ways:

- **Classified fewer than `left`** — the difference is work that cannot be
  matched to a named ticket. Record it as a blind spot. Never pad the list.
- **Classified more than `left`** — the excess are false positives, issues in
  the landing cycle that were never in the target. Render the classified list,
  take the heading count from `left`, and record the overshoot as a blind spot.

Example: a cycle whose `issueCountHistory` ends at 48 and which now holds 32
issues had 16 leave. Classifying 13 of them leaves 3 unattributed, and the
footer says so.

**This works in `review` only.** It needs a full member count for the closed
cycle, and `review` has one because the target cycle is queried in full. In
`prep` the closed cycle is `P`, which is queried only for unfinished issues — a
deliberately near-empty filter — so `count(issues currently in P)` is not
available. Never compute `left` in `prep`; the heading there carries the
classified count alone.

### Landed line for review

`review` reports what landed at team level only.

**Issue counts.** The numerator is issues currently in the target cycle whose
`statusType` is `completed`. The denominator is `issueCountHistory[last]`,
**not** the current member count — the unfinished issues have already left, so
counting current members reports `28 of 32` when the truth is `28 of 48`.

**Day totals.** Sum days per issue from the sizes map. Never derive days from
`completedScopeHistory`.

- Numerator: the completed issues.
- Denominator: every issue still in the target cycle, completed or canceled,
  plus every sized carryover issue attributed to it.

The denominator cannot be complete. An unattributed issue that left the cycle
has no reachable estimate, and an unestimated issue has no days at all. Suffix
it with `+` whenever either is true — the same "plus an unknown amount" the
capacity table uses.

Worked example. A cycle holds 9 issues worth 18.0d, of which 7 completed issues
are worth 15.0d. It has 6.5d of sized carryover attributed to it, plus one
unestimated carryover issue. It renders:

```text
landed 7 of 14 issues, 15.0d of 24.5d+
```

**Heading point total.** The `review` carryover heading carries the points that
left the cycle:

```text
points_left = scopeHistory[last] - sum(estimate.value over issues now in the cycle)
```

Points, not days. This is the only figure in the report denominated in points,
because it comes from the history arrays, and a point total cannot be converted
to days.

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
