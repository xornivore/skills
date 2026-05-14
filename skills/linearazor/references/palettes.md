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
ASCII. See [presentation.md](./presentation.md) "Rendering modes."

## ANSI escape emission

In `ansi` rendering mode (real TTY) every colored token wraps in a
truecolor SGR escape and a reset:

```text
\x1b[38;2;R;G;Bm<token>\x1b[0m
```

`R`, `G`, `B` are the decimal RGB values of the role's hex.
`\x1b[0m` resets all attributes. The catppuccin-mocha ANSI table below
spells the literals out; for the other shipped palettes, derive the
escape from the hex column using the same formula.

Identifiers (`CON-1053`) wrap in `\x1b[1m<id>\x1b[0m` (bold, no
accent color) per the "What gets colored" rule above — and then wrap
that whole bold token in an OSC 8 hyperlink so the identifier is
clickable in supporting terminals. See "Rendering modes" in
[presentation.md](./presentation.md) for the OSC 8 form.

In `markdown` rendering mode (Claude Code chat, no real TTY), emit
no ANSI escapes — use markdown formatting and links per
[presentation.md](./presentation.md). In `plain` mode, no color or
formatting; bare ASCII.

## Roles

Role names are palette-independent. Every shipped palette assigns the
same roles to its accents — only the hues change.

| Role | What it colors |
| --- | --- |
| `shipped` | Shipped lead-in, momentum, bee animal |
| `questions` | Questions lane, cat animal, `→` flourish |
| `changes_scope` | Scope-change lines, penguin animal |
| `changes_date` | Date-move lines, snake animal |
| `stalls_aging` | Aging-WIP stall lines, cow animal |
| `stalls_no_pr` | No-PR-linked stall lines, snail animal |
| `stalls_silent` | Silent stall lines, turtle animal |
| `stalls_blocked` | Blocked-without-blocker stall lines, fish animal |
| `quality` | Quality lines, bat animal |
| `retrospective` | Retrospective block, dog animal |
| `lookahead` | Lookahead block headings and milestone lines |
| `metadata` | Dim context — file paths, timestamps, footer text |

## Bundled palettes

### catppuccin-mocha (default)

Truecolor. Source: <https://github.com/catppuccin/catppuccin>.

| Role | Hex | ANSI escape |
| --- | --- | --- |
| `shipped` | `#a6e3a1` (green) | `\x1b[38;2;166;227;161m` |
| `questions` | `#b4befe` (lavender) | `\x1b[38;2;180;190;254m` |
| `changes_scope` | `#fab387` (peach) | `\x1b[38;2;250;179;135m` |
| `changes_date` | `#cba6f7` (mauve) | `\x1b[38;2;203;166;247m` |
| `stalls_aging` | `#fab387` (peach) | `\x1b[38;2;250;179;135m` |
| `stalls_no_pr` | `#fab387` (peach) | `\x1b[38;2;250;179;135m` |
| `stalls_silent` | `#74c7ec` (sapphire) | `\x1b[38;2;116;199;236m` |
| `stalls_blocked` | `#9399b2` (overlay2) | `\x1b[38;2;147;153;178m` |
| `quality` | `#89dceb` (sky) | `\x1b[38;2;137;220;235m` |
| `retrospective` | `#cba6f7` (mauve) | `\x1b[38;2;203;166;247m` |
| `lookahead` | `#89dceb` (sky) | `\x1b[38;2;137;220;235m` |
| `metadata` | `#7f849c` (overlay1) | `\x1b[38;2;127;132;156m` |

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
