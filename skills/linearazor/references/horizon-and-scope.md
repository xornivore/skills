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

## Lookahead suppression and mode interaction

The lookahead block is suppressed under any of these conditions:

| Condition | Trigger |
| --- | --- |
| Explicit suppression | User invoked `linearazor lookahead off` |
| Implicit suppression | Primary horizon is `since <date>` (anchor mode is backward-facing) |
| Per-mode suppression | `brief` mode (slack-paste is current-cycle only) |
| Empty-set suppression | The lookahead window resolves to no in-scope issues and no in-scope milestones |

Mode-by-mode rendering of the lookahead block:

| Mode | Lookahead behavior |
| --- | --- |
| `brief` | Always suppressed |
| `digest` | Collapsed to a one-liner per project |
| full ritual | Own section after the lane stack |
| `share` | Inherits full ritual; renders into the PNG |

Composition rule: when both an explicit-suppression flag and a mode
suppression apply, suppression wins. `linearazor share lookahead off`
renders the share PNG without the lookahead block. `linearazor digest
lookahead 2` widens the lookahead window before applying digest's
one-liner-per-project shape.

## In-scope set (primary horizon)

An issue is in scope when all apply:

- Belongs to the configured Linear team.
- Belongs to a project carrying **every** one of the configured
  labels (when `labels` is non-empty in config). Multiple labels
  intersect — they narrow scope, not broaden it. Configured labels are
  **project labels**, not issue labels — see "Label resolution" below.
- Satisfies the composite horizon filter — at least one of:
  - Assigned to a cycle whose window intersects the primary horizon.
  - Attached to a milestone whose target date falls in the primary
    horizon.
  - Has a `dueDate` in the primary horizon window.
  - Was In Progress at any point in the primary horizon window
    (catches issues not bound to a cycle, milestone, or due date).

## Label resolution

Linear has two distinct label namespaces:

- **Project labels** — applied to projects. Used to scope a digest
  to a sub-team or initiative without tagging every issue.
- **Issue labels** — applied to individual issues (e.g. `bug`,
  `enhancement`). Used for issue-level classification.

The `labels` array in `~/.config/linearazor/<group>.toml` resolves to
**project labels**. Phase 1 looks up label IDs via Linear's
`list_project_labels` (not `list_issue_labels`) and uses them to filter
projects. With multiple labels, Phase 1 calls `list_projects --label
<id>` once per label and intersects the returned project-ID sets, so
the candidate project set is exactly the projects carrying every
configured label. The candidate issue set is the union of all
in-cycle issues under those projects before the horizon filter
applies.

**Why project-labels.** Most teams scope by initiative or sub-team
membership, which is a property of the project, not of each issue.
Forcing every issue to carry a redundant tag is friction the team
won't sustain. Project labels give a stable scope anchor that
survives churn at the issue level.

**Wrong:** resolve the configured label as an issue label and filter
issues directly — returns empty when the label is applied at the
project level only.

**Wrong:** with multiple configured labels, take the union of
per-label project sets — that broadens scope each time the user adds
a label, the opposite of intent.

**Right:** resolve every configured label as a project label,
intersect the per-label project sets, then include every in-cycle
issue under the resulting projects.

**Audit:** Phase-1 ingest must call `list_project_labels` to resolve
the configured `labels`; calling `list_issue_labels` on the configured
`labels` array is the violation. Unresolved label names go to
`factSheet.unresolved` for the setup-health footer.

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
