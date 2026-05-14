# Presentation layer

Loaded at the Phase-2 presentation step, after the signal layer has
composed the brief. Defines palette routing, animation placement,
Unicode flourishes, the TTY/NO_COLOR contract, and the `share` mode's
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

## Unicode flourishes

One Unicode flourish max per line — never decorative, always
load-bearing:

| Glyph | Role | Meaning | ASCII fallback |
| --- | --- | --- | --- |
| `◇` | Lead stall / lookahead-unclarity line | "Noticed thing" | `*` |
| `→` | Lead question line | "Where does this point" | `>` |
| `─`, `├`, `└`, `│` | Section dividers, run header frame | Visual scaffolding | `-`, `+`, `+`, `\|` |
| `•` | Shipped-list bullet | "Item" | `*` |

ASCII fallback is used when `[ -t 1 ]` is false (not a TTY) OR
`$NO_COLOR` is set.

## TTY and NO_COLOR

Detection at render entry:

```bash
if [ -t 1 ] && [ -z "$NO_COLOR" ]; then
  USE_ANSI=1
else
  USE_ANSI=0
fi
```

When `USE_ANSI=0`:

- ANSI escapes are not emitted (plain ASCII output).
- Unicode flourishes degrade to ASCII per the table above.
- Animation cast still renders (ASCII is the medium of the cast
  anyway).
- Mood line, exec summary, all signals — content identical.

The principle: piped output is byte-identical to TTY output minus
ANSI escapes and Unicode flourishes. Audit by piping a `share` PNG
render's text version against a `>file` redirect of the TTY render
with ANSI stripped — they must match.

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
