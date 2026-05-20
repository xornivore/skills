# Animation cast

The cast is a themed asset. Each theme provides one icon per signal
lane plus a setup mascot and an empty-brief mascot. The lane spec is
canonical — themes only swap the *icons*, not the roles.

## Active theme

The active theme is selected by the `[render] animation_theme` field
in `<group>.toml`. Default: `farm`. Legal values are exactly the
filenames under [`../themes/`](../themes/) (each theme is one
`<name>.md` file). An unknown or missing value falls back to `farm`.

Currently shipped:

- [`../themes/farm.md`](../themes/farm.md) — `farm`

To add a theme: drop a new file at `../themes/<name>.md` following the
shape of `farm.md`. The file name becomes a legal `animation_theme`
value automatically — there is no second registry to update.

## Lane spec

The roles are theme-agnostic. Each theme file maps these roles to
icons.

| Role | Tone |
| --- | --- |
| `shipped` | Active, momentum, just shipped |
| `questions` | Curious, alert |
| `stalls_aging` | Been sitting too long |
| `stalls_no_pr` | Slow, manual, no automation backing it |
| `stalls_silent` | Present but not moving |
| `stalls_blocked` | Constrained from moving forward |
| `changes_scope` | The path moved |
| `changes_date` | The clock moved |
| `quality` | Looking closely at what's there and what isn't |
| `retrospective` | Looking back at what just ran |
| `changes_scope` drift (≥ 3) | Sub-flavor of `changes_scope`; replaces the default icon when total scope-changes count across all in-scope projects in the primary horizon is at least 3 |

Each theme file also provides:

- One **setup mascot** — rendered only by the setup flow and the first
  ritual run after a fresh `reconfigure`. See
  [`../references/setup-flow.md`](../references/setup-flow.md).
- One **empty-brief mascot** — rendered only when every signal lane
  comes up empty across every in-scope project.

## Rendering rules

One icon per signal category per brief, never one per project and
never one per item. Color via the palette role in the lane heading —
see [`../references/palettes.md`](../references/palettes.md).

Every icon block is bracketed by exactly one blank line above and one
blank line below in the rendered output — see
[`../references/presentation.md`](../references/presentation.md)
"ASCII art padding (universal)". Same rule applies to the setup mascot
and the empty-brief mascot.

The cast deliberately mixes facing directions and sizes within a
theme. Themes target compact public-commons ASCII art (3-8 rows,
~10-30 columns); perfect uniformity is not the goal.

**Left-margin convention.** Every icon renders flush left at column 0
of the source block. The renderer adds no extra leading indent — the
icon sits directly above the lane title and project sub-headers below
it. Replacing an icon? Strip any leading whitespace shared by all rows
before committing it; the leftmost glyph of at least one row must sit
at column 0.

## Replacement

The cast is purely affective. Replacing an icon, changing its pose,
adding a new one, or shipping a new theme is a presentation-layer
change — no signal-layer file needs updating. Hard rule 12 binds.

## Audit

- Each theme file covers every role in the lane spec exactly once,
  plus exactly one setup mascot and one empty-brief mascot.
  **Audit:** for each `../themes/<name>.md`, count the `###`
  sub-headings under "Cast" plus the two mascot sub-headings;
  expected count equals the number of roles in the lane spec (11,
  including the drift sub-flavor) plus two.
- The set of theme filenames equals the set of legal
  `animation_theme` config values. **Audit:** `ls ../themes/*.md`;
  the basename set equals the enum that the setup flow and the config
  validator honor.
- One icon per signal category per brief (never one per project,
  never one per item).
- Every ASCII art block in the rendered output is bracketed by
  exactly one blank line above and one blank line below.
- No emoji anywhere in any theme file.
