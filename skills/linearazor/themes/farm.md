# Theme: farm

The default animation theme for linearazor. Eleven lane icons plus a
setup mascot and an empty-brief mascot — sourced from public-commons
ASCII collections where possible, with two pieces freehand (signpost,
tumbleweed) where the commons had no compact canonical form.

For the theming contract (lane spec, padding rules, replacement rules,
audit cues) see [`../assets/animation.md`](../assets/animation.md).

## Cast

### shipped — Galloping horse

Frontal-ish horse face with two eyes and ears, trailing motion lines
behind. `Neil Smith` form from `ascii-art.de/ascii/ghi/horse.txt`.

```text
    ./|,,/|
   <   o o)
  <\ (    |
 <\\  |\  |
<\\\  |(__)
<\\\\  |
```

### questions — Cat

Front-face cat — sitting, curious, alert. Uncredited canonical form
from the ASCII commons.

```text
 /\_/\
( o.o )
 > ^ <
```

### stalls_aging — Cow

Standing in a field of grass — head down, plodding. Covers the
collapsed generic stalls sub-flavor (aging WIP, no PR linked, silent,
or scope-hygiene — see
[`../references/signals.md`](../references/signals.md)). Uncredited
canonical form from the ASCII commons.

```text
        (__)
`\------(oo)
  ||    (__)
  ||w--||     \|/
```

### stalls_blocked — Closed door

Two-paneled closed door with a doorknob — literal "path closed."
`ejm` form from the ASCII commons, vertically trimmed ~40%.

```text
__________
|  __  __  |
| |__||__| |
|  __  __()|
| |  ||  | |
| |__||__| |
|__________|
```

### changes_scope — Windmill

Blades turning with the wind — direction shifted. `PhS` form from
`ascii-art.de/ascii/uvw/windmill.txt`.

```text
     /\     /\
    '. \   / ,'
      `.\-/,'
       ( X   )
      ,'/ \`.\
    .' /   \ `,
     \/-----\/'
______ |_H___|____
```

### changes_date — Chicken

Head up, watching the hour pass. Neil Smith form from
`ascii-art.de/ascii/c/chicken.txt`.

```text
   \\
   (o>
\\_//)
 \_/_)
  _|_
```

### quality — Goose

Long-necked sentinel — geese alert at anything off. Head crop from
`hjw`'s canonical goose in `ascii-art.de/ascii/ghi/goose.txt`.

```text
        ___
    ,-""   `.
  ,'  _   e )`-._
 /  ,' `-._<.===-'
/  /
```

### retrospective — Dog

Floppy-eared dog head with a bit of neck — looking right at you, the
run that just ended, attentive. Uncredited canonical form from the
ASCII commons, cropped to head + neck.

```text
/^-----^\
V  o o  V
 |  Y  |
  \ Q /
  / - \
```

### changes_scope drift — Spider

Barn spider — eight legs, sideways and multidirectional. Sub-flavor
of `changes_scope` when the total scope-changes count across all
in-scope projects in the primary horizon is at least 3, signalling
sustained drift rather than a one-off change. Inherits the
`changes_scope` palette color. Uncredited canonical form from the
ASCII commons.

```text
 ||  ||
 \\()//
//(__)\\
||    ||
```

## Setup mascot — Barn

"Welcome to the farm — let's set things up." Appears only in the setup
flow ([`../references/setup-flow.md`](../references/setup-flow.md))
and in the first ritual run after a fresh `reconfigure`. Compact
silo-and-barn form from `asciiart.eu/buildings-and-places/houses`.

```text
 x
.-. _______|
|=|/     /  \
| |_____|_""_|
|_|_[X]_|____|
```

## Empty-brief mascot — Puzzled face

Appears only when every signal lane comes up empty across every
in-scope project. Replaces the mood line; the lane stack is suppressed.
Theme-agnostic uncredited canonical form from the ASCII commons.

```text
  .--.
 / o o \
|   ^   |
 \ --- /
```

## Lane → icon (farm)

| Role | Icon |
| --- | --- |
| `shipped` | Galloping horse |
| `questions` | Cat |
| `stalls_aging` (aging WIP / no PR / silent / scope-hygiene — collapsed) | Cow |
| `stalls_blocked` | Closed door |
| `changes_scope` | Windmill |
| `changes_date` | Chicken |
| `quality` | Goose |
| `retrospective` | Dog |
| `changes_scope` drift | Spider (overrides Windmill) |
| Setup mascot | Barn |
| Empty-brief mascot | Puzzled face |

## Provenance

The art in this file is sourced from established ASCII art collections
in the public commons, with one piece (signpost) built freehand
because no compact canonical form exists. Artist signatures were
stripped from the glyphs for visual consistency and recorded below.

- **Neil Smith** — galloping horse (frontal face with motion lines)
  and chicken. Sources: `ascii-art.de/ascii/ghi/horse.txt`,
  `ascii-art.de/ascii/c/chicken.txt`. Used verbatim with the artist
  signature stripped.
- **PhS** — windmill. Source:
  `ascii-art.de/ascii/uvw/windmill.txt`. Used verbatim with the
  artist signature stripped and common leading whitespace removed.
- **Hayley Wakenshaw** (`hjw`) — goose (head crop). Source:
  `ascii-art.de/ascii/ghi/goose.txt`. Cropped to head + neck.
- **ejm** — closed door. Source: ASCII commons. Vertically trimmed
  ~40% from the canonical (collapsed each panel's vertical bars).
- **Uncredited canonical** — cat, cow, dog (floppy-eared sitting),
  spider, puzzled face, plus the small barn from
  `asciiart.eu/buildings-and-places/houses`. Treated as effectively
  public-domain.
