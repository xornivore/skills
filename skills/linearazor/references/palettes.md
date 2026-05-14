# Palettes

Loaded at the Phase-2 presentation step. Bundled named palettes plus
the role mapping that survives across palettes.

## Resolution order

At render time, the palette is chosen in this order — first hit wins:

1. `LINEARAZOR_PALETTE=<name>` env var.
2. Config `[render].palette` name.
3. Per-role overrides in `[render.palette_overrides]` (any role can
   be remapped to a different role name or a hex literal).
4. Built-in defaults for the selected palette.

`NO_COLOR=1` is absolute — bypasses all of the above and renders plain
ASCII. See [presentation.md](./presentation.md) "TTY and NO_COLOR."

## Roles

Role names are palette-independent. Every shipped palette assigns the
same roles to its accents — only the hues change.

| Role | What it colors |
| --- | --- |
| `shipped` | Shipped lead-in, momentum, beaver/bee animal |
| `questions` | Questions lane, lemur animal, `→` flourish |
| `changes_scope` | Scope-change lines, fox animal |
| `changes_date` | Date-move lines, chameleon animal |
| `stalls_aging` | Aging-WIP stall lines, cow animal |
| `stalls_no_pr` | No-PR-linked stall lines, snail animal |
| `stalls_silent` | Silent stall lines, turtle animal |
| `stalls_blocked` | Blocked-without-blocker stall lines, mole animal |
| `quality` | Quality lines, heron animal |
| `retrospective` | Retrospective block, owl animal |
| `lookahead` | Lookahead block headings and milestone lines |
| `metadata` | Dim context — file paths, timestamps, footer text |

## Bundled palettes

### catppuccin-mocha (default)

Truecolor. Source: <https://github.com/catppuccin/catppuccin>.

| Role | Hex |
| --- | --- |
| `shipped` | `#a6e3a1` (green) |
| `questions` | `#b4befe` (lavender) |
| `changes_scope` | `#fab387` (peach) |
| `changes_date` | `#cba6f7` (mauve) |
| `stalls_aging` | `#fab387` (peach) |
| `stalls_no_pr` | `#fab387` (peach) |
| `stalls_silent` | `#74c7ec` (sapphire) |
| `stalls_blocked` | `#9399b2` (overlay2) |
| `quality` | `#89dceb` (sky) |
| `retrospective` | `#cba6f7` (mauve) |
| `lookahead` | `#89dceb` (sky) |
| `metadata` | `#7f849c` (overlay1) |

### catppuccin-latte

Light-terminal mirror.

| Role | Hex |
| --- | --- |
| `shipped` | `#40a02b` (green) |
| `questions` | `#7287fd` (lavender) |
| `changes_scope` | `#fe640b` (peach) |
| `changes_date` | `#8839ef` (mauve) |
| `stalls_aging` | `#fe640b` (peach) |
| `stalls_no_pr` | `#fe640b` (peach) |
| `stalls_silent` | `#209fb5` (sapphire) |
| `stalls_blocked` | `#8c8fa1` (overlay2) |
| `quality` | `#04a5e5` (sky) |
| `retrospective` | `#8839ef` (mauve) |
| `lookahead` | `#04a5e5` (sky) |
| `metadata` | `#9ca0b0` (overlay1) |

### solarized-dark

Source: <https://ethanschoonover.com/solarized/>.

| Role | Hex |
| --- | --- |
| `shipped` | `#859900` (green) |
| `questions` | `#268bd2` (blue) |
| `changes_scope` | `#cb4b16` (orange) |
| `changes_date` | `#6c71c4` (violet) |
| `stalls_aging` | `#cb4b16` (orange) |
| `stalls_no_pr` | `#cb4b16` (orange) |
| `stalls_silent` | `#2aa198` (cyan) |
| `stalls_blocked` | `#586e75` (base01) |
| `quality` | `#2aa198` (cyan) |
| `retrospective` | `#6c71c4` (violet) |
| `lookahead` | `#2aa198` (cyan) |
| `metadata` | `#586e75` (base01) |

### tokyo-night

Source: <https://github.com/folke/tokyonight.nvim>.

| Role | Hex |
| --- | --- |
| `shipped` | `#9ece6a` (green) |
| `questions` | `#bb9af7` (purple) |
| `changes_scope` | `#ff9e64` (orange) |
| `changes_date` | `#7aa2f7` (blue) |
| `stalls_aging` | `#ff9e64` (orange) |
| `stalls_no_pr` | `#ff9e64` (orange) |
| `stalls_silent` | `#7dcfff` (cyan) |
| `stalls_blocked` | `#565f89` (comment) |
| `quality` | `#7dcfff` (cyan) |
| `retrospective` | `#bb9af7` (purple) |
| `lookahead` | `#7dcfff` (cyan) |
| `metadata` | `#565f89` (comment) |

### monochrome

One accent plus dim. For terminals with limited color support or for
users who want minimal color.

| Role | Hex |
| --- | --- |
| All non-metadata roles | `#ffffff` (bold) |
| `metadata` | `#777777` (dim) |

Layer accent via bold or underline rather than hue.

## Hex literal overrides

Any role in `[render.palette_overrides]` accepts:

- A role name from the selected palette (`shipped = "rosewater"` →
  use rosewater for the shipped role).
- A hex literal (`shipped = "#f9e2af"`).

Validation: hex literals must match `^#[0-9a-fA-F]{6}$`. Anything else
is rejected with a one-line config error.
