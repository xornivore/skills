# cyclotic — design spec

**Status:** authoritative, implemented
**Author:** xornivore
**Date:** 2026-08-03
**Skill folder:** `skills/cyclotic/`
**Branch:** `feat/cyclotic`

The Linear MCP shapes and constraints in [ingest](#5-ingest-and-fact-sheet)
were verified against a live workspace. They are what the MCP returns, not
what the GraphQL API documents.

## 1. Summary

`cyclotic` reads a scoped slice of a Linear workspace and checks how well a
cycle is prepared. It answers several questions:

- **Is the team's capacity allocated?** Who is holding more days of work than
  the cycle has room for, and who is holding none at all.
- **Are the issues in the cycle sized and assigned?** An unsized ticket cannot
  be weighed against anyone's capacity; an unassigned one belongs to nobody.
- **Are the projects behind the cycle groomed?** Whether there is a sized,
  unclaimed queue to pull from next, or a pile of raw tickets nobody has
  triaged.
- **Was unfinished work from the last cycle accounted for?** What came across,
  and whether it was never started, stuck in progress, or waiting on review.
- **Does rotation time come out of the right person's capacity?** A week on an
  on-call schedule is a week not spent on cycle work.
- **Is anyone doing cycle work who is not on the roster?**

Two modes, and the tense is the difference between them. `cyclotic prep` asks
how well a cycle about to be worked **is** prepared, while there is still time
to change it. `cyclotic review` asks how well the cycle that just closed **was**
prepared, and what that left behind. Both accept a person filter.

The skill names individuals, because it reports load per person. It does not
judge them — see [hard rule 5](#95-judge-the-plan-never-the-person).

`cyclotic` supersedes `linearazor`, whose removal is part of the implementation
work in [repo changes](#12-repo-changes). Nothing carries over except the init
and config pattern (group name, team, fuzzy-matched member roster, project-label
scope) and two pipeline disciplines: a fact sheet between ingest and render, and
a prohibition on re-querying Linear during render.

## 2. Differentiation

Linear has a cycle view and per-assignee filters. What it does not do is put
assignment, sizing, on-call rotation, and prior-cycle carryover in one place and
total them up per person — or tell you that a project's backlog holds forty
tickets and none of them are sized.

| Axis | Linear cycle view | `cyclotic` |
| --- | --- | --- |
| Question | What is in this cycle? | How well is this cycle prepared? |
| Capacity | Story points, no day translation | T-shirt sizes translated to working days |
| On-call | Not modeled | Rotation weeks deducted from available days |
| Carryover | Visible per issue | Grouped by why it did not land |
| Backlog | A list | Rated: ready / unsized / owned-but-unscheduled |
| Scope | Team | Working group: team plus optional project labels plus a roster |
| History | Retains every past cycle | Retains nothing — no per-person trend can be built from it |

Composes with the other skills in this repo without overlap: `googly-eyes`
reviews code, `observablip` reviews telemetry, `doxcavate` reviews
documentation, `cyclotic` reviews the plan.

## 3. Modes and invocation

| User phrasing | Mode | Target cycle |
| --- | --- | --- |
| `cyclotic prep` | prep | active cycle |
| `cyclotic prep next` | prep | next upcoming cycle |
| `cyclotic prep for avery` | prep, filtered | active cycle |
| `cyclotic review` | review | most recently completed cycle |
| `cyclotic review for avery` | review, filtered | most recently completed cycle |
| `cyclotic init` | setup | — |
| `cyclotic configure` | setup (alias of `init`) | — |

Bare `cyclotic` with no mode word routes to `prep`.

Three modifiers compose with any mode, each with its own layout in
`references/verbose.md`, loaded only when one is present:

| Modifier | Phrasings | Adds |
| --- | --- | --- |
| verbose | `-v`, `--verbose`, `verbose`, `in detail` | ticket inventory and per-person arithmetic, after the normal report |
| inventory | `show cards`, `list tickets`, `list cards`, `with sizes` | the ticket inventory alone |
| explain | `explain avery`, `why avery`, `break down avery` | one person's arithmetic alone |

The inventory is the answer to "what is actually in this cycle, and at what
size" — a question the summary report cannot answer, because it renders only
flagged tickets and a healthy cycle has none. The `explain` layout names the
tickets excluded from a person's load, which is the part of a load figure the
summary can only count.

Verbose is where [hard rule 5](#95-judge-the-plan-never-the-person) is most
likely to erode, so the layouts are explicit about it: verbose adds rows and
arithmetic, never a ranking, a roster average, or a per-person completion
figure. The roster stays in config order so the table cannot be read as a
leaderboard.

The person filter matches on first name or full name, case-insensitively,
against the config roster. An ambiguous first name (two roster members named
Avery) asks which one rather than guessing. An unmatched filter exits with a
one-line message listing the roster — it never falls back to an unfiltered run.

Cycle length comes from Linear (`list_cycles` start and end dates), never from
config. Available days are the **weekdays** between those dates, because a
two-week cycle is ten working days, not fourteen. A cycle of unusual length gets
the right denominator without anyone editing anything.

## 4. Config

Location: `~/.config/cyclotic/<group>.toml`. Hand-editable. The skill rewrites
it only from `init` / `configure`, and only after showing the rendered result
and getting confirmation.

```toml
# version = 1
# cyclotic scope: infra

group   = "infra"
team    = "Engineering"
members = ["Avery Stone", "Blake Ruiz", "Chen Ito", "Dara Okafor"]
labels  = []                  # PROJECT labels, AND semantics; empty = whole team

[capacity]
oncall_cost_days = 5          # cost of one rotation week
                              # cycle length is read from Linear, not set here

[capacity.sizes]              # Linear estimate points -> label + working days
1  = { label = "XS",   days = 0.5 }   # a few hours, under a day
2  = { label = "S",    days = 1   }
3  = { label = "M",    days = 2   }
5  = { label = "L",    days = 3.5 }   # 3-4 days
8  = { label = "XL",   days = 5   }   # ~1 week
13 = { label = "XXL",  days = 10  }   # ~2 weeks
21 = { label = "XXXL", days = 15  }   # 3+ weeks

[[oncall.schedules]]
name = "Interrupts"
id   = "01ABCDEFGHIJKLMNOPQRSTUVWX"
```

Notes:

- **`labels`** resolves against the **project-label** namespace
  (`list_project_labels`), not issue labels. Multiple labels intersect: a
  project must carry every listed label to be in scope. To widen the scope, use
  one broader label rather than several narrow ones.
- **`capacity.sizes`** keys are Linear's numeric `estimate.value`. Linear's
  T-shirt scale sits on top of Fibonacci points, which is where the keys above
  come from. Linear treats points as complexity, not calendar time; the `days`
  column is this skill's translation and is the user's to edit. `init` derives
  the scale from the team's own issues and shows the mapping for confirmation.
  See [init flow](#61-estimation-scale-detection).
- **`XL` and larger are always flagged for splitting**, by label — `XL`, `XXL`,
  `XXXL`, and anything above. A ticket estimated at a week or more offers no
  checkpoint inside the cycle. A team whose scale tops out at `L` never sees
  this flag, and should not: `L` is three to four days.
- **Linear counts an unestimated issue as 1 point. `cyclotic` does not.** An
  issue with no `estimate` key contributes zero days and is reported as unknown,
  never silently treated as an `XS`. See
  [hard rule 4](#94-unestimated-work-never-reads-as-spare-capacity).
- **An explicit zero estimate is sized.** Linear's estimate picker offers
  `No estimate` and `-` as separate choices, and teams can enable `-` to mean a
  deliberate zero. A `-` issue (`estimate.value` of `0`) contributes zero days,
  does not increment the unestimated counter, and is not flagged. Only a missing
  `estimate` key is unestimated. Conflating the two would nag about a decision
  already made and would suppress that person's capacity delta for no reason.
- **`oncall.schedules`** is a list of tables so a group covering several
  rotations charges each. Empty list disables on-call lookup entirely.
- **No `[render]` section.** Output is plain text. There is no palette, no
  theme, no animation cast, and no image export. Signal is carried by words,
  structure, and column alignment.

## 5. Ingest and fact sheet

All Linear reads happen in one phase and land in a fact sheet. Render consumes
only the fact sheet ([hard rule 3](#93-never-re-query-after-ingest)).

### 5.1 Linear queries

1. `list_cycles` for the configured team with `type` **omitted** → every cycle
   the team has. Sort by `startsAt` and resolve the target, the prior cycle, and
   the next cycle positionally, per [carryover](#54-carryover). One call covers
   all three.
2. `list_projects` for the team, filtered by `labels` when set → the in-scope
   project set, with each project's `lead`.
3. `list_issues` for the target cycle → id, title, assignee, estimate, status,
   status type, project, `startedAt`, `createdAt`.
4. `list_issues` for the landing cycle → carryover candidates, classified per
   [carryover](#54-carryover).
5. `list_issues` per in-scope project, filtered client-side to issues with no
   `cycleId` → the backlog behind the cycle, with assignee and estimate.

Query 5 is the widest, for two reasons. `list_issues` has no "in no cycle"
filter — the `cycle` parameter matches one specific cycle — so the exclusion
happens on the client. And it runs once per project. Bound it: request only the
fields the backlog table needs, and cap at a configurable page depth, reporting
the cap in the footer when it truncates
([hard rule 6](#96-state-blind-spots-once)).

### 5.1.1 MCP response shapes

Four shapes decide whether the report is right:

- **Null fields are omitted, not null.** An unestimated issue has no
  `estimate` key; an unassigned one has no `assignee` key; an issue outside a
  project has no `project` key. Test key presence.
- **An issue's `id` is the human identifier** (`ENG-201`). There is no separate
  `identifier` field.
- **`estimate` is an object**: `{ "value": 3, "name": "M" }`. `name` is the
  team's own label, which makes the team's scale readable at query time and is
  where [estimation scale detection](#61-estimation-scale-detection) gets its
  labels from.
- **Cycles carry four daily-snapshot history arrays.** The last element of
  `issueCountHistory` is the issue count at close; `completedIssueCountHistory`,
  `scopeHistory`, and `completedScopeHistory` mirror it for completions and
  points. These are the only record of a closed cycle's true size. All four are
  **empty for a cycle that has not started**, so `prep next` must never index
  `[last]` without checking.

`list_cycles` requires only `teamId`; `type` is optional, and omitting it
enumerates every cycle the team has — verified live, with no pagination and no
reliable ordering. Sort by `startsAt` client-side. Passing `type: "all"` is
rejected despite the tool description mentioning it.

`isCurrent` is the only temporal flag on a cycle. There is no `completedAt`,
`archivedAt`, or status field, so a cycle that closed yesterday is shaped
exactly like the active one apart from that flag; past and future are derived
from the dates. A cycle's `title` is omitted when it has no name — fall back to
`number`. Cycle numbers can have gaps, so neighbours are found by date order,
never by `number - 1`.

Point totals never convert to days. The points-to-days map is not linear (3
points is 2 days, 5 is 3.5), so a summed `scopeHistory` figure cannot be
translated. Day totals are always summed per issue.

**Working days.** `startsAt` is the first day; `endsAt` is **exclusive** — it
names the day after the last. Working days are the weekdays from
`date(startsAt)` to `date(endsAt) - 1 day` inclusive. A cycle running
`2026-08-03T05:00:00Z` to `2026-08-17T05:00:00Z` covers Aug 3-16 and has 10
working days; treating `endsAt` as inclusive yields 11 and overstates
everyone's available days.

### 5.2 incident.io queries (optional)

For each entry in `oncall.schedules`, fetch shifts overlapping the target
cycle's date range and map each shift's user to a roster member by email, then
by display name.

incident.io MCP is an **optional dependency**. When it is not installed, or
`oncall.schedules` is empty, or a lookup fails, the run proceeds with no
rotation deductions and the footer states that rotations were not checked and
available days may therefore be overstated. The skill never silently treats
"no data" as "nobody is on call."

### 5.3 Fact sheet

A compact YAML structure holding: the resolved cycle (name, number, start, end,
working days), the roster with resolved Linear user ids, per-person issue lists
with estimates resolved to day values, carryover grouped by state type,
in-scope projects with lead and backlog counts by readiness cell, on-call shifts
mapped to roster members, and a list of blind spots accumulated during ingest.

Template ships at `assets/factsheet-template.yaml`.

### 5.4 Carryover

Linear moves unfinished work forward on its own. When a cycle ends, every open
issue rolls into the next cycle, and per Linear's documentation there is no way
to keep unfinished issues in a closed cycle. A closed cycle therefore holds
**only** `completed` and `canceled` issues — verified live: a cycle that closed
with 48 issues and 28 completions now returns 32, every one of them completed
or canceled.

So carryover is read from the cycle the work rolled **into**. Reading the cycle
it rolled out of returns an empty set every time, which renders as a clean
close and is the most dangerous possible wrong answer.

| Mode | Target cycle | Cycle read | Section heading |
| --- | --- | --- | --- |
| `prep` | active `C` | `C` itself, plus prior cycle `P` | `CARRYOVER FROM P` |
| `prep next` | next `N` | `N` itself | `ALREADY IN FLIGHT` |
| `review` | most recently completed `P` | the active cycle `C` | `CARRYING INTO C` |

In `prep` the question is "what arrived here already in flight," so the cycle
read is the target. In `review` the question is "what is leaving this cycle
unfinished," so the cycle read is the one after the target; the target is read
only for what landed.

`prep next` is the exception, and its heading says so. The active cycle has not
closed, so nothing has rolled out of it. What a next cycle can show is work
someone began ahead of schedule — real, but not carryover, and calling it
carryover would report a transfer that has not happened.

**Classification.** Two buckets are provable from timestamps and one is
inferred, and they use different boundaries. Collapsing them onto one boundary
is the failure mode this section exists to prevent.

Provable, for an issue whose status type is `started`:

| Mode | Was already in flight when |
| --- | --- |
| `prep` | `startedAt` earlier than `C.startsAt` |
| `prep next` | `startedAt` present at all |
| `review` | `startedAt` earlier than `P.endsAt` |

Split these into **in progress** and **in review**, the latter being a `started`
issue whose `status` matches the team's review wording. An issue whose
`startedAt` is at or after the boundary is new work, not carryover.

Inferred, for an issue whose status type is `backlog` or `unstarted`. Linear
retains no per-issue cycle membership, so nothing records which cycle an
untouched issue sat in, and this bucket is a judgment from `createdAt`:

| Mode | Never started when |
| --- | --- |
| `prep` | `createdAt` earlier than **`P.startsAt`** |
| `prep next` | no such bucket |
| `review` | `createdAt` earlier than `P.endsAt` |

In `prep` the boundary is the **prior cycle's start**, not the target's. Every
ticket is created before the cycle it is planned into, so testing `createdAt`
against `C.startsAt` matches all normally-planned work and reports an entire
well-groomed cycle as carryover — 15 of 16 tickets in the `healthy` fixture, 17
of 20 in `messy`. An issue that already existed before the previous cycle began
and is still unstarted has demonstrably sat through a cycle.

The cost is a known miss: an issue created during `P` and never started has a
`createdAt` between `P.startsAt` and `C.startsAt`, where nothing distinguishes it
from work planned into `C` during cooldown. That is a footer blind spot, stated
whenever the bucket is evaluated, hit or miss. Widening the boundary to catch it
swamps the section, and an empty bucket with no caveat reads as proof that
nothing was left unstarted.

`prep` without a prior cycle has no never-started bucket, and neither does
`prep next` — every issue in a cycle that has not started was created before it,
so the test carries no information.

The prior cycle is also queried directly for unfinished issues — normally empty,
but it catches a run made before rollover and an issue pinned in place. Merge and
dedupe by `id`.

**Reconciliation.** Classification is a judgment from timestamps; it cannot
recover which issues belonged to the cycle at the moment it closed. The cycle's
own totals are exact, so they bound the report:

```text
left = issueCountHistory[last] - count(issues currently in the cycle)
```

The only issues that leave a closed cycle are those that rolled forward or were
moved to backlog or triage during cooldown, so `left` is the true carryover
count. Both directions of disagreement are reported: a classified set smaller
than `left` leaves work that cannot be matched to a named ticket, and one larger
than `left` contains false positives that were never in the target. Either way
the difference is a footer blind spot, and the list is never padded to match.

**Reconciliation is `review`-only.** It needs a full member count for the closed
cycle, which `review` has because the target is queried in full. In `prep` the
closed cycle is `P`, queried only for unfinished issues — a deliberately
near-empty filter — so the count is unavailable and the `prep` heading carries
the classified count alone.

**Days-in-state is not available.** The MCP surface exposes no per-state
transition timestamp. `startedAt` records when work first began, so the figure
rendered is days since `startedAt`, labelled `since started`.

**The `review` landed denominator comes from `issueCountHistory`**, not from
counting current members. The unfinished issues have already left, so counting
members reports `28 of 32` when the truth is `28 of 48` — a flattering number
built by hiding the work that rolled out.

**The landed day denominator** is every issue still in the target cycle,
completed or canceled, plus every sized carryover issue attributed to it. It
cannot be complete: an unattributed issue that left has no reachable estimate and
an unestimated issue has no days at all, so it carries a trailing `+` whenever
either is true — the same "plus an unknown amount" the capacity table uses.

**The `review` carryover heading's point total** is `scopeHistory[last]` minus
the summed `estimate.value` of the issues still in the cycle. It is the one
figure in the report denominated in points rather than days, because it comes
from the history arrays and a point total cannot be converted.

## 6. Init flow

Conversational, one question at a time, skip allowed on optional steps. Never
proceeds to an unscoped run.

1. **Team.** `list_teams`. Multiple teams → pick list. One team → confirm.
2. **Group name.** Free text, becomes the config filename. Lowercase ASCII
   letters, digits, hyphens; 1–32 chars.
3. **Members.** Free text, comma- or newline-separated. Fuzzy-match each
   against Linear users on display name and email local-part. High-confidence
   matches (≥ 0.9) are batched into one confirmation at the end.
   Mid-confidence (0.6–0.9) shows up to three candidates and asks. No match
   offers retry, skip, or save-as-entered. Unresolved names are saved verbatim
   and surface as a footer note on every run.
4. **Project labels.** `list_project_labels` as a suggestion pick list, free
   text allowed, multiple allowed, skip allowed. State explicitly that multiple
   labels narrow rather than widen.
5. **Estimation scale.** See below.
6. **On-call schedules.** If incident.io MCP is available, list schedules and
   offer a multi-select, storing name and id. If not available, ask whether to
   record schedule names now for later, and note the dependency is missing.
   Skip allowed. When at least one schedule is recorded, ask what a rotation
   week costs in working days (`oncall_cost_days`, default 5) — a team whose
   rotation is quiet enough to leave room for cycle work sets this lower.
7. **Persist.** Show the full rendered TOML. On yes, `mkdir -p
   ~/.config/cyclotic` and write. On no, print the TOML for manual copy and
   exit without writing.

Cycle length is never asked for. It is read from Linear on every run.

### 6.1 Estimation scale detection

The MCP surface does not expose a team's estimation configuration — `get_team`
returns id, name, icon, and timestamps only. So the scale is derived from the
team's own issues rather than described by the user:

1. `list_issues` for the team with `fields` of `estimate`, limit 250.
2. Collect the distinct `estimate` objects. Each is
   `{ "value": 3, "name": "M" }` — the team's real point values paired with the
   team's real labels.
3. Sort by `value` and propose a `days` figure per row from the cheat sheet
   below, taking the midpoint of any range.
4. Show the derived table; the user confirms or edits the `days` column.

Labels and point values come from evidence, so only `days` is a judgment. A
label of `-` maps to zero days and is not offered for editing — zero days is
what it means.

| Label | Points | Days |
| --- | --- | --- |
| XS | 1 | a few hours, under a day |
| S | 2 | ~1 day |
| M | 3 | ~2 days |
| L | 5 | 3-4 days |
| XL | 8 | ~1 week |
| XXL | 13 | ~2 weeks |
| XXXL | 21 | 3+ weeks |

When the sample turns up no estimates at all, present this full table, say that
no sized issues were found to derive from, and ask the user to confirm or edit
it. Either way the table is shown before it is written — the user confirms the
numbers, the skill never assumes them silently.

A team using raw Fibonacci or a custom scale keeps its own point keys and
labels; only the day values need agreeing on.

## 7. Capacity math

Pure arithmetic over the fact sheet. No queries.

**Load.** For each roster member, sum `capacity.sizes[estimate.value].days`
over their issues in the target cycle. An issue with no `estimate` key
contributes `0` and increments that person's `unestimated` counter. An issue
whose `estimate.value` is `0` contributes `0` and does **not** increment it —
it is sized, and the answer was zero. An issue whose `estimate.value` has no
entry in `capacity.sizes` contributes `0`, increments `unestimated`, and adds a
blind spot naming the unmapped value; this happens when a team extends its scale
after `init` ran.

**Available days.** Start at the cycle's weekday count, from Linear's start and
end dates. For each on-call shift mapped to that person, subtract the count of
the shift's weekdays that fall inside the cycle window, capped at
`capacity.oncall_cost_days` per shift. Floor the result at `0`.

A shift straddling a cycle boundary is charged only for the part inside the
cycle. A one-week rotation fully inside a ten-day cycle costs 5 days; the same
rotation split across two cycles costs each cycle only its own days.

**Verdict.** In precedence order, where `u` is that person's count of issues
with no `estimate` key:

| Verdict | Condition |
| --- | --- |
| `EMPTY` | zero issues in the target cycle |
| `OVER` | `u == 0` and `load > available`, or `u > 0` and `load >= available` |
| `full` | `u == 0` and `load == available` |
| `UNDER` | `u == 0` and `load < available` |
| `UNDER?` | `u > 0` and `load < available` |

`EMPTY` outranks `UNDER`: having no work at all is a different problem from
having light work.

`full` requires `u == 0`. Sized work that exactly fills the cycle, alongside
unsized tickets, is over by an unknown amount, not in balance.

There is no tolerance band and no configurable threshold. The signed delta is
rendered next to the verdict, so magnitude is visible without inventing a knob —
a row reading `-0.5 UNDER` is half a day short and needs no attention, while
`+11.0 OVER` is two weeks of work that will not fit.

The delta is suppressed, and only the verdict rendered, when the person has
unestimated issues. The real delta is unknown, so a number computed over the
sized issues alone would be made up.

**Unestimated work never reads as spare capacity.** A person with any
unestimated issues has their load rendered with a trailing `+` (`6.0d+`),
meaning "plus an unknown amount," and the count in the notes column. Their
verdict is never a bare `UNDER` and never `full` while `unestimated > 0`. See
[hard rule 4](#94-unestimated-work-never-reads-as-spare-capacity).

## 8. Flags

Every flag below fires from the fact sheet alone.

| # | Flag | Fires when | Surfaces as | Modes |
| --- | --- | --- | --- | --- |
| F1 | over capacity | `load > available` | capacity-table verdict | prep |
| F2 | empty | roster member with zero issues in the target cycle | capacity-table verdict | prep |
| F3 | no estimate | assigned target-cycle issue with no `estimate` key | own section | prep, review |
| F4 | needs split | target-cycle issue labelled `XL` or larger | own section | prep |
| F5 | unassigned in cycle | target-cycle issue with no `assignee` key | own section | prep |
| F6 | carryover | unfinished work that crossed a cycle boundary, per [carryover](#54-carryover) | own section | prep, review |
| F7 | backlog readiness | per in-scope project, see below | own section | prep |
| F8 | unlisted contributor | target-cycle assignee absent from the roster | own section | prep |

F1 and F2 never get their own section — they are verdicts in the capacity table,
which is why `prep` has no `OVER CAPACITY` heading. `review` renders neither,
because it has no capacity table.

`review` carries only F3 and F6. It reports what landed and what is leaving
unfinished; sizing, assignment, and backlog grooming are decisions for the cycle
being planned, not the one already closed.

**F5 unassigned in cycle** and **F8 unlisted contributor** both carry a day total
in their heading. These issues are sized and committed but sit in no capacity
row, so without the total they are the cycle work that no figure in the report
accounts for. The two flags differ only in why the work is unaccounted for —
nobody owns it, or its owner is not on the roster — so they carry the same
figure.

**F6 carryover** subdivides by why it did not land, using state type and the
boundary comparison in [carryover](#54-carryover):

- **never started** — state type `backlog` or `unstarted`, created before the
  boundary. The sharpest signal: it was planned, and nothing happened.
- **in progress** — state type `started`, work began before the boundary.
  Rendered with days since `startedAt`.
- **in review** — a `started` state whose name matches review wording, when the
  team has one. Rendered with days since `startedAt`.

The heading carries the authoritative issue count from the cycle's history
arrays, so it can exceed the number of issues named beneath it; the shortfall is
a footer blind spot.

**F7 backlog readiness** classifies each in-scope project's issues that are in
no cycle across two axes, assigned and sized:

| Cell | Meaning |
| --- | --- |
| unassigned + sized | **ready** — the queue to pull from. Healthy. |
| unassigned + unsized | **unsized** — no estimate, so no way to fit it in a cycle |
| assigned + either | **owned/unsched** — someone owns it, nothing schedules it |

A project with a good `ready` count and zero `unsized` still gets a row. The
section reports every in-scope project, not only the troubled ones — a lead
planning the next cycle needs to see which projects have sized work waiting and
which have nothing to pull from.

**F8 unlisted contributor** names the person, their issue count, their day total,
and offers to add them to the roster. Without it, someone who joins the team and
is never added to `members` has their work dropped from every report, and nothing
in the output says so.

## 9. Hard rules

### 9.1 Read-only against Linear

Every Linear MCP call is a read. The skill writes exactly one thing: its own
config file under `~/.config/cyclotic/`.

Every flag needs human judgment — the right estimate, who takes the project,
how to split an oversized ticket. There is no mechanical fix to offer, so a
write path would add risk and buy nothing.

**Audit:** no Linear MCP write tool appears in any run; no `Edit` or `Write`
targets a path outside `~/.config/cyclotic/`; no `Bash` call mutates the user's
repos.

### 9.2 Never run unscoped

No config and an interactive session → the init flow. No config and a
non-interactive session → exit with `no scope configured; run "cyclotic init"`.
Never enumerate the workspace.

**Audit:** every ingest query carries either a team filter or an explicit
project-id set derived from config.

### 9.3 Never re-query after ingest

If render needs a fact, that fact is missing from the fact sheet, which is an
ingest bug. Fix it in ingest.

This holds after the report too. The fact sheet is kept for the rest of the
conversation and follow-up questions are answered from it — it carries every
ticket's project, status, timestamps, and day value, far more than any layout
renders. A question the fact sheet cannot answer is a **new run**, not a new
query: the skill names the mode that would answer it and offers to run it.
Querying mid-conversation would mix two ingest passes in one thread with nothing
marking the seam.

**Audit:** `references/presentation.md`, `references/flags.md`,
`references/capacity.md`, and `references/verbose.md` contain no instruction to
call Linear or incident.io MCP.

### 9.4 Unestimated work never reads as spare capacity

A load figure computed over unestimated issues understates reality. Rendering
it bare invites the reader to hand that person more work.

Correct: `Chen   6.0d+   10.0d           UNDER?   3 unestimated`

Wrong: `Chen   6.0d    10.0d    -4.0   UNDER`

Wrong: `Avery 10.0d+   10.0d            full     1 unestimated`

**Audit:** for any person with `unestimated > 0`, the rendered load ends in `+`,
no signed delta appears on that row, and the verdict is neither a bare `UNDER`
nor `full`.

### 9.5 Judge the plan, never the person

Flags describe tickets, load, and sizing. Statements about the plan are in
scope. Verdicts about a person are not.

Correct: `Dara's cycle holds 14.5d against 10.0d available.`

Wrong: `Dara is overcommitted.` / `Dara is slow.` / `Dara completed 58% of
their estimate.`

No scores, no percentages of a person's output, no ranking of people against
each other, no tracking of an individual across cycles. `review` mode keeps
completion totals at team level so there is no per-person figure to rank.

Without this rule a capacity tool turns into a performance-review instrument.
It is also the rule that constrains the skill's main feature, which makes it
the one most likely to get quietly dropped during implementation.

**Audit:** grep rendered output for a roster member's name adjacent to any of
`slow|behind|underperform|overcommitted|%`; any hit outside a day-count context
is a violation.

### 9.6 State blind spots once

The footer names, in one line each and only when true: rotations not checked;
issues excluded for having no estimate; backlog query truncated at the page cap;
roster names that never resolved to a Linear user; carryover the cycle's totals
imply but that cannot be attributed to a named ticket, or classified carryover
that overshoots those totals; estimate values with no entry in the sizes map; and
that the never-started bucket is inferred from creation date.

The never-started caveat renders whenever the bucket is evaluated, hit or miss.
An empty bucket is exactly the case a reader would otherwise take as proof that
nothing was left unstarted.

A reader who is not told about a gap assumes there was none.

**Audit:** when `oncall.schedules` is empty or incident.io MCP is absent, the
footer contains the rotations-unchecked line.

### 9.7 Plain text only

No ANSI escapes, no emoji, no image export, no `[render]` config. Output renders
as markdown. Tables use markdown table syntax; fixed-width blocks are used only
where column alignment carries meaning.

**Audit:** rendered output contains no `\x1b[` sequence and no character in the
Emoji property range.

## 10. Presentation

### 10.1 `prep` section order

1. **Header** — cycle name and number, mode, calendar date range, working days.
2. **Capacity table** — one row per roster member: load, available, signed
   delta, verdict, notes.
3. **CARRYOVER FROM prior cycle** — grouped never-started / in-progress /
   in-review. Headed `ALREADY IN FLIGHT` in `prep next`.
4. **NO ESTIMATE** — issue identifier, assignee, title.
5. **NEEDS SPLIT** — issue identifier, assignee, size, title.
6. **UNASSIGNED IN CYCLE** — issue identifier, size, title, with the day total
   in the heading.
7. **BACKLOG BEHIND THE CYCLE** — readiness table, one row per project, with a
   trailing list of the owned-but-unscheduled identifiers.
8. **UNLISTED IN ROSTER** — name, issue count, day total.
9. **Footer** — blind spots.

Every section that names an issue renders its title. Titles arrive in the same
query as the estimate, so they cost nothing, and an identifier alone cannot be
discussed without opening Linear.

The header renders the **calendar** range, `first_day` to `last_day`. The
working-day count sits beside it and does the other job, so rendering the last
weekday instead would contradict the fact sheet and make the cycle look shorter
than Linear shows it.

Empty sections are omitted entirely. The capacity table is the exception: in
`prep` it renders even when every row is unremarkable, because a table of four
`full` rows is the answer to "is this cycle allocated."

### 10.2 `review` section order

1. **Header.**
2. **Landed line** — `landed N of M issues, Xd of Yd`. Team level only.
3. **CARRYING INTO `<next cycle>`** — same three-way grouping as carryover.
4. **NO ESTIMATE, SO UNCOUNTED** — issues excluded from the day totals.
5. **Footer.**

### 10.3 Filtered runs

`for <person>` collapses to person-major: that person's capacity row, then
their target-cycle issues grouped by project with sizes, then only the flags
touching them, then the readiness rows for projects they lead or hold work in.
The team capacity table is suppressed — a filtered run must not become a
back-door team comparison ([hard rule 5](#95-judge-the-plan-never-the-person)).

### 10.4 Verbose, inventory, and explain

Layouts live in `references/verbose.md`, loaded only when a run carries one of
the modifiers in [modes and invocation](#3-modes-and-invocation). A plain `prep`
never pays for them.

The **inventory** lists every ticket in the target cycle grouped by assignee in
config order, then unassigned, then unlisted contributors, with identifier, size
label, days, status, and title, subgrouped by project. An unsized ticket renders
`--` for size and days rather than `0.0d`, because a zero would be a claim about
its cost.

The **per-person arithmetic** shows the sum that produced a load figure, the
available-day derivation including any on-call subtraction and the cap that
applied, and a named list of every ticket excluded from both. The excluded block
is the point of the layout: a load figure is built by leaving things out, and the
summary row can only say how many.

A **verbose team run** renders the normal report first, then the inventory, then
per-person arithmetic for every roster member. The summary stays intact and
first; someone who asked for detail still wants the answer before the evidence.

### 10.5 Reference layouts

The layout below is the `messy` fixture rendered, so its arithmetic is
checkable against `tests/fixtures/messy.mcp.yaml`.

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

The days figure on an in-flight issue is labelled `since started`, not
`in state`. The MCP surface exposes no per-state transition timestamp, so
`startedAt` is all there is, and labelling it `in review` would claim a
measurement that does not exist.

## 11. File layout

```text
skills/cyclotic/
├── SKILL.md                      # triggers, mode routing, pipeline, hard rules
├── README.md                     # human-facing, links into SKILL.md
├── references/
│   ├── init-flow.md              # setup, fuzzy match, estimation-scale detection
│   ├── ingest.md                 # Linear + incident.io queries, fact sheet
│   ├── capacity.md               # load, available days, verdicts
│   ├── flags.md                  # each flag: condition, wording, audit cue
│   ├── presentation.md           # section order, table layouts, filter collapse
│   └── verbose.md                # inventory, per-person arithmetic, follow-ups
├── assets/
│   ├── config-template.toml
│   └── factsheet-template.yaml
└── tests/
    └── fixtures/
        ├── healthy.mcp.yaml      # everything sized, assigned, in balance
        ├── messy.mcp.yaml        # over, empty, unsized, oversized, unlisted
        └── cycle-close.mcp.yaml  # review mode, mixed carryover states
```

Six references, two assets, three fixtures. All references are one level deep
from `SKILL.md`, per `skills/CLAUDE.md`.

Fixtures are agent-verifiable scenarios, not automated tests — the repo's only
gate is `markdownlint`. They exist so the capacity arithmetic and flag
conditions can be checked against a known input without a live workspace.

## 12. Repo changes

- Add `skills/cyclotic/` per the layout above.
- Delete `skills/linearazor/` in full.
- Delete the five `linearazor` design specs under `docs/superpowers/specs/`
  (`2026-05-13`, `2026-05-14`, and three dated `2026-05-19`), and the
  implementation plan at `docs/superpowers/plans/2026-05-14-linearazor.md`. They
  document a skill that no longer exists; git history retains them.
- Replace the `linearazor` row in the top-level `README.md` skills table with a
  `cyclotic` row.

## 13. Out of scope

Deliberately excluded, with the reason:

- **Per-person completion percentages and estimate-accuracy trends.** Requires
  multi-cycle history per individual and turns the tool into a scorecard.
  Conflicts with [hard rule 5](#95-judge-the-plan-never-the-person).
- **PTO, holidays, and per-person baseline capacity.** Available days derive
  only from cycle length and on-call rotation. Manual absence figures go stale
  the moment they are typed, and a config'd baseline percentage encodes a
  judgment about a person in a file.
- **Writing to Linear.** See [hard rule 1](#91-read-only-against-linear).
- **Parallel sub-agent dispatch.** Query volume is bounded and the computation
  is arithmetic. `linearazor` needed it for per-project prose generation;
  `cyclotic` does not.
- **Issues in the cycle with no project.** A plausible planning flag, held back
  until the eight in [flags](#8-flags) prove insufficient.
- **Palette, themes, animation cast, PNG export.** Output is plain text
  ([hard rule 7](#97-plain-text-only)).
