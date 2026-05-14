# Interactive setup flow

Loaded when no config exists at `~/.config/linearazor/<group>.toml` and
the session is interactive (TTY present). Reconfigure mode
(`linearazor reconfigure`) loads this same flow.

The flow is conversational — one question at a time, with skip
allowed for optional steps. Never proceeds with an unscoped run; if
the user refuses to scope, exit with a one-line explanation.

## Welcome mascot

Render the duck from
[`../assets/animation.md`](../assets/animation.md) "Setup mascot" at
the top of the setup output, in the `shipped` palette role (a friendly
green). The duck appears only here and in the first ritual run after a
fresh `reconfigure` — never in normal brief output.

## Step 1: Detect workspace shape

Query Linear MCP for the list of teams. Two cases:

- **Multiple teams (≥ 2), each with a manageable member count
  (≤ 25):** present a pick list of teams. Continue with the chosen
  team. Skip to Step 3.
- **Exactly one team, OR a single team with many members (> 25):**
  the workspace is tag-partitioned. Continue with the only team (or
  ask the user to confirm the partition assumption) and ask for a
  working-group name in Step 2.

## Step 2: Ask for a working-group name

Free text. Becomes the config key (e.g. `infra`, `containers-blue`).
Validation: lowercase ASCII letters, digits, hyphens. 1–32 chars.
This is independent of Linear's team concept — it is the name of the
config file (`~/.config/linearazor/<group>.toml`).

## Step 3: Ask for member names

Free text. Comma- or newline-separated. Match each name against Linear
users by display name and email with fuzzy matching:

- **High-confidence match** (score ≥ 0.9, exact-or-near-exact on
  display name or email-local-part): include without per-line
  prompting. Show the full list at the end for a single confirmation.
- **Low-confidence match** (0.6 ≤ score < 0.9): show the best one to
  three candidates and ask "Which one (or none)?"
- **No match** (score < 0.6): list the name as unmatched. Offer:
  retry with a different name, skip, or accept the unmatched name
  (which will surface as a setup-health note in every brief).

No silent inclusion. Above-threshold matches are confirmed in a
single summary at the end of this step. Unresolved names are saved to
config exactly as entered.

## Step 4: Ask for project label scope (optional)

Query Linear MCP via `list_project_labels` (the **project-label**
namespace — not `list_issue_labels`) for labels carried by projects
whose state is `started` or whose latest milestone target date is
within the next 60 days. Present these as a pick list (suggestion).
Allow free text. Multiple labels allowed.

The `labels` array in config always resolves against the
project-label namespace. See
[horizon-and-scope.md](./horizon-and-scope.md) "Label resolution" for
the rationale.

Skip allowed — when no labels are set, the in-scope filter does not
apply the label clause and the candidate set is every project under
the team.

## Step 5: Ask for default horizon

Default `cycle`. Pick list: `cycle`, `week`, `2w`, `4w`, `milestone`.

## Step 6: Offer to persist

Show the rendered config (full TOML). Ask "Save to
`~/.config/linearazor/<group>.toml`?" Two paths:

- **Yes:** create the directory if needed
  (`mkdir -p ~/.config/linearazor`), write the file, confirm path.
- **No:** exit with a one-line note explaining how to manually save
  later (print the rendered TOML to stdout for copy-paste).

## Setup-health note

The first run after setup includes a setup-health line in the footer
listing unresolved names. Example:

```text
Setup health: 2 of 3 members resolved. Unresolved: "Bob 2".
```

This is the only place outside the disclaimer footer where member
names appear in the output.
