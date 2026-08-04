# Init flow

Loaded when no config exists at `~/.config/cyclotic/GROUP.toml` and the
session is interactive, or when the user says `cyclotic init` or
`cyclotic configure`.

Conversational — one question at a time, skip allowed on optional steps. Never
proceed to an unscoped run. When the user refuses to scope, exit with a
one-line explanation.

## Step 1: Team

Call `list_teams`. Multiple teams present a pick list. One team asks for
confirmation.

Record the team's `id` as well as its name. Every later query needs the id.

## Step 2: Group name

Free text. Becomes the config filename. Lowercase ASCII letters, digits, and
hyphens; 1 to 32 characters.

This is independent of Linear's team concept — it names the config file, so a
user can keep several scopes over one team.

## Step 3: Members

Free text, comma- or newline-separated. Fuzzy-match each entry against Linear
users on display name and email local-part:

- **High confidence** (0.9 and above): include without per-line prompting.
  Batch all of them into one confirmation at the end of the step.
- **Mid confidence** (0.6 to 0.9): show up to three candidates and ask which
  one, or none.
- **No match** (below 0.6): offer retry, skip, or save-as-entered.

Never include a name silently. Save unresolved names verbatim — they surface as
a footer note on every run so the gap stays visible.

## Step 4: Project labels

Call `list_project_labels` and present the results as a suggestion pick list.
Free text allowed, multiple allowed, skip allowed.

State explicitly that multiple labels **narrow** rather than widen: a project
must carry every listed label to be in scope. To widen the scope, use one
broader label rather than several narrow ones.

These resolve against the **project-label** namespace, not issue labels. Skip
leaves `labels` empty, which puts every project under the team in scope.

## Step 5: Estimation scale

Linear's MCP surface does not expose a team's estimation configuration —
`get_team` returns id, name, icon, and timestamps only. Derive the scale from
the team's own issues instead of asking the user to describe it.

1. Call `list_issues` for the team with `fields` of `estimate` and a limit of
   250.
2. Collect the distinct `estimate` objects. Each is
   `{ "value": 3, "name": "M" }` — the team's real point values paired with the
   team's real labels.
3. Sort by `value` and propose a `days` figure per row from the cheat sheet
   below, taking the midpoint of any range.
4. Show the derived table and ask the user to confirm or edit the `days`
   column.

The labels and point values come from evidence, so only `days` is a judgment.
Linear treats points as complexity, not calendar time; the `days` column is
this skill's translation and is the user's to edit.

| Label | Points | Days |
| --- | --- | --- |
| XS | 1 | 0.5 — a few hours, under a day |
| S | 2 | 1 |
| M | 3 | 2 |
| L | 5 | 3.5 — three to four days |
| XL | 8 | 5 — about a week |
| XXL | 13 | 10 — about two weeks |
| XXXL | 21 | 15 — three weeks or more |

When the sample turns up no estimates at all, present this full table, say that
no sized issues were found to derive from, and ask the user to confirm or
edit it.

A team using raw Fibonacci or a custom scale keeps its own point keys and
labels; only the day values need agreeing on.

Note that a label of `-` is Linear's explicit zero estimate. Map it to
`days = 0` and do not offer to edit it — zero days is what it means.

## Step 6: On-call schedules

When incident.io MCP is available, list schedules and offer a multi-select,
storing each one's name and id.

When it is not available, say the dependency is missing and ask whether to
record schedule names now for later use. Skip allowed.

When at least one schedule is recorded, ask what a rotation week costs in
working days (`oncall_cost_days`, default 5). A team whose rotation is quiet
enough to leave room for cycle work sets this lower.

## Step 7: Persist

Show the full rendered TOML. Template at
[assets/config-template.toml](../assets/config-template.toml).

- **Yes:** `mkdir -p ~/.config/cyclotic` and write the file. Confirm the path.
- **No:** print the TOML for manual copying and exit without writing.

Never write config without showing it first and getting a yes.

## What is never asked

**Cycle length.** It is read from Linear on every run, from the target cycle's
`startsAt` and `endsAt`. A cycle of unusual length gets the right denominator
without anyone editing anything.

**Per-person baseline capacity, PTO, or holidays.** Available days derive only
from cycle length and on-call rotation. A config'd baseline percentage encodes
a judgment about a person in a file, and manual absence figures go stale the
moment they are typed.

## Adding a member later

When F8 reports an unlisted contributor and the user accepts the offer to add
them, re-enter this flow at step 3 with the existing roster preloaded, then
step 7. Never edit the config file silently.
