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

- **Project names** (in per-project headers).
- **Numbers** (`11 days`, `8d to target`).
- **Verbs** that carry the signal (`shipped`, `moved`, `silent`).
- **Identifiers** (`ENG-423`) — bold default Text role, not a colored
  accent.

What stays plain:

- Prose. Sentences are not colored.
- Punctuation, divider characters, spaces.

Rule of thumb: a single line carries one or two colored tokens. More
than three colored tokens on a line is a presentation-layer bug.

## Animation placement

The animation cast lives in [`../assets/animation.md`](../assets/animation.md).
One animal per signal category per per-project section — not one per
item.

For each signal lane that has at least one finding in the current
per-project block, render the animal once at the top of that lane,
left-aligned with two-space indent, before the finding lines. All
animals face right toward the finding list below.

If a signal lane is empty, no animal renders for that lane.

### Sub-flavor overrides

A per-project signal block may swap its default animal for a
sub-flavor variant when a stronger condition matches. The sub-flavor
inherits the same palette role as the lane it overrides.

| Lane | Default | Sub-flavor (when) | Color |
| --- | --- | --- | --- |
| `changes_scope` | Penguin | Spider — when the per-project scope-changes count is at least 3 ("scope drift") | `changes_scope` |

When a sub-flavor renders, the default animal is suppressed for that
block — never both.

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
| Color | truecolor ANSI per [palettes.md](./palettes.md) | none — markdown carries weight via bold | none |
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
hyperlinks render natively. `markdown` is right for Claude Code
chat and other markdown-rendered surfaces, where ANSI shows as
literal escape junk and the renderer wants `**bold**` and
`[text](url)` instead. `plain` is the safe-fallback byte stream for
pipes, files, and CI logs — readable everywhere, decorative
nowhere.

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

The pipeline (illustrative — pin flags at implementation time):

```bash
RENDER_OUT="${TMPDIR:-/tmp}/linearazor-<group>-<date>.png"
linearazor_render | freeze \
  --language ansi \
  --output "$RENDER_OUT" \
  --background "$PRIMARY_BG" \
  --font.family "JetBrains Mono" \
  --font.size 13 \
  --padding 24
echo "$RENDER_OUT"
```

`$PRIMARY_BG` is the background hex from the active palette. For
`catppuccin-mocha`, `#1e1e2e` (base). For palettes without an
explicit background hex, default to black (`#000000`).

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
