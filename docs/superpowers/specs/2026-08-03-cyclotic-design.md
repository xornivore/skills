# cyclotic — design spec

**Status:** authoritative
**Author:** xornivore
**Date:** 2026-08-03
**Skill folder (planned):** `skills/cyclotic/`
**Branch:** `feat/cyclotic`

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
- **`capacity.sizes`** keys are Linear's numeric `estimate` values. Linear's
  T-shirt scale sits on top of Fibonacci points, which is where the keys above
  come from. Linear treats points as complexity, not calendar time; the `days`
  column is this skill's translation and is the user's to edit. `init` detects
  the team's configured estimation scale and shows the derived mapping for
  confirmation. See [init flow](#61-estimation-scale-detection).
- **`XL` and larger are always flagged for splitting**, by label — `XL`, `XXL`,
  `XXXL`, and anything above. A ticket estimated at a week or more offers no
  checkpoint inside the cycle. A team whose scale tops out at `L` never sees
  this flag, and should not: `L` is three to four days.
- **Linear counts an unestimated issue as 1 point. `cyclotic` does not.** An
  issue with no estimate contributes zero days and is reported as unknown, never
  silently treated as an `XS`. See
  [hard rule 4](#94-unestimated-work-never-reads-as-spare-capacity).
- **`oncall.schedules`** is a list of tables so a group covering several
  rotations charges each. Empty list disables on-call lookup entirely.
- **No `[render]` section.** Output is plain text. There is no palette, no
  theme, no animation cast, and no image export. Signal is carried by words,
  structure, and column alignment.

## 5. Ingest and fact sheet

All Linear reads happen in one phase and land in a fact sheet. Render consumes
only the fact sheet ([hard rule 3](#93-never-re-query-after-ingest)).

### 5.1 Linear queries

1. `list_cycles` for the configured team → resolve the target cycle, plus the
   **carryover source cycle** and the **neighbour cycle name** per the table in
   [carryover source](#54-carryover-source).
2. `list_projects` for the team, filtered by `labels` when set → the in-scope
   project set, with each project's `lead`.
3. `list_issues` for the target cycle → id, identifier, title, assignee,
   estimate, state, state type, project.
4. `list_issues` for the carryover source cycle, restricted to issues whose
   state type is not `completed` and not `canceled` → carryover.
5. `list_issues` for in-scope projects, restricted to issues in no cycle →
   the backlog behind the cycle, with assignee and estimate.

Query 5 is the widest. Bound it: request only the fields the backlog table
needs, and cap at a configurable page depth, reporting the cap in the footer
when it truncates ([hard rule 6](#96-state-blind-spots-once)).

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

### 5.4 Carryover source

The two modes read carryover from different cycles. Getting this backwards
produces a plausible-looking but wrong report, so it is stated explicitly.

| Mode | Target cycle | Carryover read from | Section heading |
| --- | --- | --- | --- |
| `prep` | active (or next) | the cycle **before** the target | `CARRYOVER FROM <prior>` |
| `review` | most recently completed | **the target cycle itself** | `CARRYING INTO <next>` |

In `prep`, the question is "what arrived here already in flight," so the source
is the preceding cycle. In `review`, the question is "what is leaving this cycle
unfinished," so the source is the closing cycle itself; the next cycle is
resolved only to name it in the heading.

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

Read the team's issue-estimation configuration. When the scale is exposed, map
its ordered values onto labels and propose day values from this cheat sheet,
taking the midpoint of any range:

| Label | Points | Days |
| --- | --- | --- |
| XS | 1 | a few hours, under a day |
| S | 2 | ~1 day |
| M | 3 | ~2 days |
| L | 5 | 3-4 days |
| XL | 8 | ~1 week |
| XXL | 13 | ~2 weeks |
| XXXL | 21 | 3+ weeks |

When the scale is not exposed through MCP, present this mapping and ask the user
to confirm or edit it. Either way the derived table is shown before it is
written — the user confirms the numbers, the skill never assumes them silently.

A team using raw Fibonacci or a custom scale keeps its own point keys; only the
labels and day values need agreeing on.

## 7. Capacity math

Pure arithmetic over the fact sheet. No queries.

**Load.** For each roster member, sum `capacity.sizes[estimate].days` over
their issues in the target cycle. An issue with a null or zero estimate
contributes `0` and increments that person's `unestimated` counter.

**Available days.** Start at the cycle's weekday count, from Linear's start and
end dates. For each on-call shift mapped to that person, subtract the count of
the shift's weekdays that fall inside the cycle window, capped at
`capacity.oncall_cost_days` per shift. Floor the result at `0`.

A shift straddling a cycle boundary is charged only for the part inside the
cycle. A one-week rotation fully inside a ten-day cycle costs 5 days; the same
rotation split across two cycles costs each cycle only its own days.

**Verdict.** In precedence order:

| Verdict | Condition |
| --- | --- |
| `EMPTY` | zero issues in the target cycle |
| `OVER` | `load > available` |
| `full` | `load == available` |
| `UNDER` | `load < available` |

`EMPTY` outranks `UNDER`: having no work at all is a different problem from
having light work.

There is no tolerance band and no configurable threshold. The signed delta is
rendered next to the verdict, so magnitude is visible without inventing a knob —
a row reading `-0.5 UNDER` is half a day short and needs no attention, while
`+11.0 OVER` is two weeks of work that will not fit.

The delta is suppressed, and only the verdict rendered, when the person has
unestimated issues. The real delta is unknown, so a number computed over the
sized issues alone would be made up.

**Unestimated work never reads as spare capacity.** A person with any
unestimated issues has their load rendered with a trailing `+` (`6.0d+`),
meaning "plus an unknown amount." Their verdict may not be `UNDER` while
`unestimated > 0`; it renders as `UNDER?` with the count. See
[hard rule 4](#94-unestimated-work-never-reads-as-spare-capacity).

## 8. Flags

Every flag below fires from the fact sheet alone.

| # | Flag | Fires when | Surfaces as | Modes |
| --- | --- | --- | --- | --- |
| F1 | over capacity | `load > available` | capacity-table verdict | prep |
| F2 | empty | roster member with zero issues in the target cycle | capacity-table verdict | prep |
| F3 | no estimate | assigned target-cycle issue with null or zero estimate | own section | prep, review |
| F4 | needs split | target-cycle issue labelled `XL` or larger | own section | prep |
| F5 | unassigned in cycle | target-cycle issue with no assignee | own section | prep |
| F6 | carryover | issue in the carryover source cycle that never completed | own section | prep, review |
| F7 | backlog readiness | per in-scope project, see below | own section | prep |
| F8 | unlisted contributor | target-cycle assignee absent from the roster | own section | prep |

F1 and F2 never get their own section — they are verdicts in the capacity table,
which is why `prep` has no `OVER CAPACITY` heading. `review` renders neither,
because it has no capacity table.

`review` carries only F3 and F6. It reports what landed and what is leaving
unfinished; sizing, assignment, and backlog grooming are decisions for the cycle
being planned, not the one already closed.

**F5 unassigned in cycle** carries a day total in its heading. These issues are
sized and committed but sit in nobody's load, so without the total they are the
one pool of cycle work that no figure in the report accounts for.

**F6 carryover** subdivides by why it did not land, using state type:

- **never started** — state type `backlog` or `unstarted`. The sharpest signal:
  it was planned, and nothing happened.
- **in progress** — state type `started`. Rendered with days-in-state.
- **in review** — a `started` state whose name matches review wording, when the
  team has one. Rendered with days-in-state.

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

**F8 unlisted contributor** names the person, their issue count, and offers to
add them to the roster. Without it, someone who joins the team and is never
added to `members` has their work dropped from every report, and nothing in the
output says so.

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

**Audit:** `references/presentation.md` and `references/flags.md` contain no
instruction to call Linear or incident.io MCP.

### 9.4 Unestimated work never reads as spare capacity

A load figure computed over unestimated issues understates reality. Rendering
it bare invites the reader to hand that person more work.

Correct: `Chen   6.0d+   10.0d           UNDER?   3 unestimated`

Wrong: `Chen   6.0d    10.0d    -4.0   UNDER`

**Audit:** for any person with `unestimated > 0`, the rendered load ends in `+`
and the verdict is not bare `UNDER`.

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
roster names that never resolved to a Linear user.

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

1. **Header** — cycle name and number, mode, date range, working days.
2. **Capacity table** — one row per roster member: load, available, verdict,
   signed delta, on-call marker.
3. **CARRYOVER FROM `<prior cycle>`** — grouped never-started / in-progress /
   in-review.
4. **NO ESTIMATE** — issue identifier and assignee.
5. **NEEDS SPLIT** — issue identifier, assignee, title.
6. **UNASSIGNED IN CYCLE** — issue identifier and size, with the day total in
   the heading.
7. **BACKLOG BEHIND THE CYCLE** — readiness table, one row per project, with a
   trailing list of the owned-but-unscheduled identifiers.
8. **UNLISTED IN ROSTER** — name and issue count.
9. **Footer** — blind spots.

Empty sections are omitted entirely. The capacity table is the exception: in
`prep` it renders even when every row is unremarkable, because a table of four
`fits` rows is the answer to "is this cycle allocated."

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

### 10.4 Reference layouts

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
    ENG-160  Avery   L    9d in state
  in review (1)
    ENG-171  Chen    S    4d in state

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
│   └── presentation.md           # section order, table layouts, filter collapse
├── assets/
│   ├── config-template.toml
│   └── factsheet-template.yaml
└── tests/
    └── fixtures/
        ├── healthy.mcp.yaml      # everything sized, assigned, in balance
        ├── messy.mcp.yaml        # over, empty, unsized, oversized, unlisted
        └── cycle-close.mcp.yaml  # review mode, mixed carryover states
```

Five references, two assets, three fixtures. All references are one level deep
from `SKILL.md`, per `skills/CLAUDE.md`.

Fixtures are agent-verifiable scenarios, not automated tests — the repo's only
gate is `markdownlint`. They exist so the capacity arithmetic and flag
conditions can be checked against a known input without a live workspace.

## 12. Repo changes

- Add `skills/cyclotic/` per the layout above.
- Delete `skills/linearazor/` in full.
- Delete the five `linearazor` design specs under `docs/superpowers/specs/`
  (`2026-05-13`, `2026-05-14`, and three dated `2026-05-19`). They document a
  skill that no longer exists; git history retains them.
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
