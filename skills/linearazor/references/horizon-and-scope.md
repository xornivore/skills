# Horizon, lookahead, and scope

Loaded at the "resolve scope plus horizon plus lookahead" step in the
`SKILL.md` pipeline. Defines how the primary horizon window, the
lookahead window, and the in-scope issue set are computed.

## Primary horizon

| Horizon | Window |
| --- | --- |
| `cycle` (default) | Current Linear cycle's start to end |
| `week` | Monday of current week to Friday |
| `2w` / `4w` | Today minus N weeks to today |
| `milestone` | Today to the next project milestone target date in scope |
| `since <date>` | The given date to today (overrides horizon anchor) |

If the user's phrasing is ambiguous and `default_horizon` is not set in
config, prompt once interactively. In non-interactive sessions, fall
back to `cycle` without prompting.

## Lookahead window (auto-tiered)

The lookahead window is always computed unless the user passes
`lookahead off` or the primary horizon is `since <date>` (which is
explicitly backward-facing).

| Primary horizon | Lookahead window |
| --- | --- |
| `cycle` | The next Linear cycle after the active one |
| `week` / `2w` / `4w` | Today's primary window-end plus the same window length |
| `milestone` | The milestone after the next-in-scope one |
| `since <date>` | Suppressed |

`lookahead 2` looks two tiers ahead instead of one — concatenate the
two windows for the lookahead set.

## In-scope set (primary horizon)

An issue is in scope when all apply:

- Belongs to the configured Linear team.
- Carries at least one of the configured labels (when `labels` is
  non-empty in config).
- Satisfies the composite horizon filter — at least one of:
  - Assigned to a cycle whose window intersects the primary horizon.
  - Attached to a milestone whose target date falls in the primary
    horizon.
  - Has a `dueDate` in the primary horizon window.
  - Was In Progress at any point in the primary horizon window
    (catches issues not bound to a cycle, milestone, or due date).

## Lookahead set

The lookahead set uses the same composite filter against the lookahead
window. Lookahead issues are tracked in `lookaheadIssues[]` separate
from `openIssues[]` — never bleed into the primary signal lanes (hard
rule 11).

## Filters that compose with horizon

The `for <member>` and `on <project>` modes narrow the in-scope set
after the horizon filter applies:

- `for <member>`: keep only issues where assignee OR creator matches
  the configured member identifier.
- `on <project>`: keep only issues whose `project.name` matches the
  given pattern (case-insensitive, substring).

Filters compose as set intersection. `linearazor for Bob Wu on
infra` narrows to issues both assigned to Bob and in the infra
project.

## First-run / no-scope behavior

When no config exists at `~/.config/linearazor/<group>.toml`:

- **Interactive session** (TTY present): enter the setup flow
  ([`setup-flow.md`](./setup-flow.md)).
- **Non-interactive session** (no TTY, harness loop): exit with the
  one-line message
  `no scope configured; ask the user to run "linearazor reconfigure"`.
  Hard rule 2 binds: never dump the workspace.

When the user passes an explicit `--scope <group>` and that group is
not configured, treat it the same as no-scope: setup or exit.
