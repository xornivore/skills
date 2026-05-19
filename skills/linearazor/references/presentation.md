# Presentation layer

Loaded at the Phase-2 presentation step, after the signal layer has
composed the brief. Defines palette routing, animation placement,
Unicode flourishes, the rendering-mode contract, and the `share` mode's
PNG export.

## Palette routing

Resolve the active palette per [palettes.md](./palettes.md). For each
emitted line, identify its signal role (from the signal-layer output)
and wrap the role's anchor text in the palette's ANSI escape for that
role.

What gets colored:

- **Project names** (as project sub-headers inside each lane).
- **Numbers** (`11 days`, `8d to target`).
- **Verbs** that carry the signal (`shipped`, `moved`, `silent`).
- **Identifiers** (`ENG-423`) — bold default Text role, not a colored
  accent.
- **Estimate-badge parentheses** (`(L)`, `(5)`, `(M)`) following an
  identifier — only the parens carry the lane color; the glyph between
  them stays plain. Hairline accent that lets the reader scan weight
  without competing with the identifier next to it.

What stays plain:

- Prose. Sentences are not colored.
- Punctuation, divider characters, spaces.
- The glyph inside an estimate badge (`L`, `5`, `M`) — see above.
- The `(<N>pt)` aggregate in the exec summary — the parens carry the
  lane color matching the lane count they follow; the `Npt` literal
  stays plain.

Rule of thumb: a single line carries one or two colored tokens. More
than three colored tokens on a line is a presentation-layer bug.

## Animation placement

The animation cast lives in [`../assets/animation.md`](../assets/animation.md).
One creature per signal category per brief — not one per project, not
one per item.

For each lane that has at least one finding across the in-scope
project set, render the creature once at the top of the lane, before
the lane title and the finding lines. All creatures face right toward
the finding list below.

If a lane is empty across every project, no creature renders for that
lane — the whole lane is omitted (see
[signals.md](./signals.md) "Lane order").

### ASCII art padding (universal)

Every ASCII art block — creature art, the setup duck, the empty-brief
mascot, the optional razor glyph in the run header — is bracketed by
exactly one blank line above and one blank line below. No exceptions,
no second blank for "breathing room," no zero-line tight-coupling
between the art and the heading beneath it.

**Audit:** in the rendered output, every ASCII art block has exactly
one blank line of separation on each side. Two or more blank lines, or
zero, is a violation.

### Column alignment within tabular bullets

Issue-stall and shipped-issue bullets follow a tabular shape so the
verb (`In Review`, `In Progress`, etc.) and the trailing
`(default threshold: N)` parenthetical line up across all bullets in
the same lane. Project sub-headers and prose bullets (the
scope-hygiene cycle-field-unpopulated / empty-project lines) are not
tabular and do not participate.

The tabular bullet has four left-aligned columns separated by exactly
two spaces:

```text
    •  <ID>     <estimate>  <stall-or-title-string>  (default threshold: N)
    ^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |  col 7   <- bullet content starts here per signal-modes.md
    col 4      <- bullet glyph per signal-modes.md indent rule
```

Column widths are computed per lane, not per brief:

- **ID column** — width = length of the longest ID in the lane's
  tabular bullets. IDs shorter than the column width are
  right-padded with spaces.
- **Estimate column** — width = length of the longest estimate
  badge in the lane's tabular bullets, including parentheses. Format
  is `(<name>)` where `<name>` is `estimate.name` (e.g. `(L)`,
  `(XS)`, `(5)`). When a bullet has no estimate, the slot renders as
  the same number of spaces. When no bullet in the lane carries an
  estimate, the column is omitted entirely (width zero, no separator
  spaces).
- **Stall-or-title column** — for stall bullets, this is the
  `<verb> <duration>` literal from the stall table in
  [signals.md](./signals.md). For shipped bullets, this is the issue
  title. Width = length of the longest such string in the lane.
  Padded on the right with spaces so the trailing parenthetical (when
  present) aligns.
- **Trailing parenthetical** — when present (`(default threshold:
  N)` for stalls; not used for shipped), it starts exactly two spaces
  after the padded stall-or-title column. Threshold values themselves
  vary (3 vs 7) — only the `(default threshold:` prefix needs to
  align across bullets.

The padding lets the eye scan a lane vertically and compare like
columns. Without padding, the `(S)` badge on one bullet pushes the
verb on that line right of the verb on a no-badge bullet next to it,
and the table degrades into ragged prose.

**Wrong** (no padding, ragged columns):

```text
    •  CON-1263  In Review 26 days  (default threshold: 3)
    •  CON-1344 (S)  In Review 14 days  (default threshold: 3)
    •  CON-993  In Progress 21 days  (default threshold: 7)
```

**Right** (padded, columns align):

```text
    •  CON-1263       In Review 26 days    (default threshold: 3)
    •  CON-1344  (S)  In Review 14 days    (default threshold: 3)
    •  CON-993        In Progress 21 days  (default threshold: 7)
```

**Audit:** for every lane with two or more tabular bullets, the
column at which the verb (first non-space character after the
estimate column) starts is identical across bullets. Likewise for
the trailing `(default threshold:` substring when present.

### Sub-flavor overrides

A lane may swap its default creature for a sub-flavor variant when a
stronger condition matches. The sub-flavor inherits the same palette
role as the lane it overrides.

| Lane | Default | Sub-flavor (when) | Color |
| --- | --- | --- | --- |
| `changes_scope` | Penguin | Spider — when the total scope-changes count across all in-scope projects in the primary horizon is at least 3 ("scope drift") | `changes_scope` |

When a sub-flavor renders, the default creature is suppressed for that
lane — never both.

### Stalls lane creature precedence

The stalls lane has four sub-flavors and one project-level scope-hygiene
variant (per [signals.md](./signals.md) "Stalls"). The lane carries one
creature for the brief. Precedence — top-down, first non-empty wins:

| Precedence | Sub-flavor | Creature | Fires when |
| --- | --- | --- | --- |
| 1 | `stalls_blocked` | Fish | any Blocked-without-blocker fires |
| 2 | `stalls_silent` | Turtle | any Silent fires OR any project-level scope-hygiene fires |
| 3 | `stalls_no_pr` | Snail | any No-PR fires OR any PR-linked-but-stuck fires |
| 4 | `stalls_aging` | Cow | any Aging-WIP / Review-aging / Awaiting-merge / Reverted fires |

New stall patterns map onto existing creatures — no new art, no new
palette roles. A project with no work tracked is quiet, not slow, so
a brief with only the scope-hygiene stall renders the turtle — same
family as a single silent issue, not the cow that marks aging WIP.

**Audit:** the stalls lane's creature corresponds to the highest-
precedence non-empty sub-flavor in the brief.

## Unicode flourishes

One Unicode flourish max per line — never decorative, always
load-bearing:

| Glyph | Role | Meaning | ASCII fallback |
| --- | --- | --- | --- |
| `◇` | Lead stall / lookahead-unclarity line | "Noticed thing" | `*` |
| `→` | Lead question line | "Where does this point" | `>` |
| `─`, `├`, `└`, `│` | Section dividers, run header frame | Visual scaffolding | `-`, `+`, `+`, `\|` |
| `•` | Shipped-list bullet | "Item" | `*` |

ASCII fallback is used in `plain` mode (see "Rendering modes" below).
`ansi` and `markdown` modes render the Unicode glyphs as-is.

## Rendering modes

The brief renders in one of three modes. Detect at render entry,
first hit wins:

```bash
if [ -n "$LINEARAZOR_MODE" ]; then
  MODE="$LINEARAZOR_MODE"          # explicit override: ansi | markdown | plain
elif [ -n "$CLAUDECODE" ]; then
  MODE=markdown                    # Claude Code chat session
elif [ -t 1 ] && [ -z "$NO_COLOR" ]; then
  MODE=ansi                        # real TTY, color allowed
else
  MODE=plain                       # piped, redirected, or NO_COLOR
fi
```

`NO_COLOR=1` is absolute on the auto path: it forces `plain` even on
a real TTY. An explicit `LINEARAZOR_MODE=ansi` overrides it.

### What each mode emits

| Element | `ansi` | `markdown` | `plain` |
| --- | --- | --- | --- |
| Color | truecolor ANSI per [palettes.md](./palettes.md) | **none — colorless by design** (see "Color in Claude Code chat" below) | none |
| Identifiers | `\x1b[1m<id>\x1b[0m` wrapped in OSC 8 hyperlink (bold, no accent color) | `**[CON-1053](url)**` | bare `CON-1053` |
| Link for identifier | OSC 8: `\x1b]8;;<url>\x1b\\CON-1053\x1b]8;;\x1b\\` | markdown link `[CON-1053](url)` | none |
| Unicode flourishes | as-is | as-is (markdown renderers handle them) | ASCII fallback per the table above |
| Animation cast | as-is | as-is, wrapped in a fenced ` ```text ` block | as-is |
| Mood line, exec summary, signal text | byte-identical content across all three modes | | |

In `markdown` mode, wrap each rendered animation block in a fenced
` ```text ` code block so the chat renderer preserves monospace and
the cast does not reflow.

### Why three modes

`ansi` is right for terminals — truecolor SGR escapes and OSC 8
hyperlinks render natively. It is also the substrate the `share`
mode renders before piping to `freeze` for PNG export (color
survives the pipeline). `markdown` is right for Claude Code chat
and other markdown-rendered surfaces, where ANSI shows as literal
escape junk and the renderer wants `**bold**` and `[text](url)`
instead. `plain` is the safe-fallback byte stream for pipes,
files, and CI logs — readable everywhere, decorative nowhere.

### Color in Claude Code chat

`markdown` mode is **colorless by design**. The skill makes no
attempt to color its output in Claude Code chat. Reasons, in order
of finality:

1. Claude Code renders assistant text as CommonMark in monospace.
   CommonMark has no color primitives.
2. Inline HTML / `<span style="color:...">` is not interpreted in
   Claude Code chat.
3. ANSI escape codes (`\x1b[38;2;...m`) appear as literal escape
   junk in chat output — they are terminal artifacts, not chat
   ones.
4. Diff fences (`` ```diff ``) do colorize, but they tie color to
   `+`/`-` line semantics, which would distort the signal meaning
   the skill is trying to preserve.

The user-facing implication: in Claude Code chat the brief carries
its structure through markdown bold, hyperlinks, fenced animation
blocks, and the prose itself. Color lives in two places —
`LINEARAZOR_MODE=ansi` for terminal output, and the `share` PNG
where `freeze` consumes the ANSI substrate. Both routes are
explicit user choices made outside chat.

**Wrong:** trying to fake color in chat with diff fences, emoji
swatches, or HTML spans.

**Right:** treat chat as colorless; offer ANSI for terminals and
PNG share-out for visual artifacts.

### Audit

- In `markdown` mode, the brief contains zero `\x1b` bytes.
- In `ansi` mode, every issue identifier is wrapped in `\x1b[1m`
  (bold) and an OSC 8 hyperlink — no accent color, consistent with
  the "Palette routing" rule.
- The `plain` mode output is byte-identical to `ansi`-with-ANSI-stripped
  output, modulo Unicode flourishes degraded to ASCII per the table
  above.

## Share as image

The `share` mode renders the full ritual brief, then exports it as a
carbon-style PNG (or SVG) via
[`charmbracelet/freeze`](https://github.com/charmbracelet/freeze).

### Detection and fallback

At the start of `share` mode, check `freeze` is on `$PATH`:

```bash
command -v freeze >/dev/null 2>&1
```

- **Present:** proceed with the freeze pipeline.
- **Absent:** print the one-line install hint and write a markdown
  fallback (the full ritual brief as plain markdown) to the same
  output path, with the file extension `.md` instead of `.png`. Never
  silently install. Never error out — the user always gets a
  shareable artifact.

Install hint:

```text
freeze not found. Install with:
  brew install charmbracelet/tap/freeze
  # or
  go install github.com/charmbracelet/freeze@latest
Falling back to markdown export at <path>.md
```

### Freeze invocation

The pipeline:

```bash
RENDER_OUT="${TMPDIR:-/tmp}/linearazor-<group>-<date>.png"
linearazor_render | freeze \
  --language ansi \
  --output "$RENDER_OUT" \
  --background "$PRIMARY_BG" \
  --font.family "JetBrains Mono" \
  --font.size 13 \
  --padding 24 \
  --margin 12 \
  --border.radius 8 \
  --shadow.blur 20 \
  --shadow.y 6
echo "$RENDER_OUT"
```

`$PRIMARY_BG` is the background hex from the active palette. For
`catppuccin-mocha`, `#1e1e2e` (base). For palettes without an
explicit background hex, default to black (`#000000`).

The margin, border-radius, and shadow flags give the PNG a framed
card look that reads well when pasted into Slack and document chat
surfaces. They are presentation polish — adjust per palette taste, but
keep the values in the same range so different palettes produce
artifacts that visually belong together.

`linearazor_render` produces an ANSI substrate per [Rendering
modes](#rendering-modes) — color escapes inline, OSC 8 hyperlinks on
identifiers, no markdown formatting. The disclaimer footer from
[`assets/footer.md`](../assets/footer.md) is omitted in `share` mode
(hard rule 7 — the PNG is a Slack-paste artifact and the footer reads
as noise outside its original terminal context).

### SVG variant

`linearazor share --svg` substitutes `--output` to `.svg`. SVG is
sharper and scales but does not always preview inline in Slack.

### Audit

The plain-text dump from `freeze --output text` (when supported) over
a `share` invocation must be byte-identical to the same brief rendered
to a TTY-fallback file via redirection.

## Layer-separation contract

Changes in this file (or any file under "Presentation layer" in
[the file layout](../../../docs/superpowers/specs/2026-05-13-linearazor-design.md#10-file-layout))
must not require edits to any signal-layer reference, asset, or audit
fixture. Hard rule 12 binds.
