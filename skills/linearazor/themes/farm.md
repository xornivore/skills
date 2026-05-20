# Theme: farm

The default animation theme for linearazor. Eleven lane icons plus a
setup mascot and an empty-brief mascot — sourced from public-commons
ASCII collections where possible, with two pieces freehand (signpost,
tumbleweed) where the commons had no compact canonical form.

For the theming contract (lane spec, padding rules, replacement rules,
audit cues) see [`../assets/animation.md`](../assets/animation.md).

## Cast

### shipped — Tractor

Plowing a field, exhaust trailing. Reads as "work just rolled
through." Tom Bampton (`tom`), trimmed from
`ascii-art.de/ascii/t/tractor.txt`.

```text
              ~~
:::          o  _||
:::---------[|<[___]
:::| | | |  (_)    o
```

### questions — Walking cat

Side-profile cat in motion — alert, sniffing forward. `fsc/as` form
from `ascii-art.de/ascii/c/cat.txt`.

```text
_                ___       _.--.
\`.|\..----...-'`   `-._.-'_.-'`
/  ' `         ,       __.--'
)/' _/     \   `-_,   /
```

### stalls_aging — Cow

Standing in a field of grass — head down, plodding. Uncredited
canonical form from the ASCII commons.

```text
        (__)
`\------(oo)
  ||    (__)
  ||w--||     \|/
```

### stalls_no_pr — Lamb

Small, hesitant, soft outline. Freehand for this cast — no compact
canonical lamb (the only one in the commons is `jgs`'s 11-row piece,
too tall for the cast envelope).

```text
 _.~~._
( o.o  )
 `~~~~`
 /|  |\
```

### stalls_silent — Chickens on nests

Brooding hens, plural — present and patient, not moving. Two-hen strip
extracted from `jgs`'s 12-row grid in
`ascii-art.de/ascii/c/chicken.txt`.

```text
   _       _
 _-(_)-  _-(_)-
`(___)  `(___)
 // \\   // \\
```

### stalls_blocked — Mule

Stubborn-as-a-mule — planted feet, refusing. `Asik` form from
`ascii-art.de/ascii/def/donkey.txt`.

```text
   _\
    /`b
/####J
 |\ ||
```

### changes_scope — Signpost

Wooden sign with an arrow — the way changed. Freehand for this cast;
no compact canonical signpost exists in the public commons.

```text
 _________
|   -->   |
'---------'
    |
   _|_
```

### changes_date — Rooster

Cock-a-doodle-doo, the hour arrived. `ejm97` form from
`ascii-art.de/ascii/pqr/rooster.txt`.

```text
   www
   (*)<
   )((
__/  ))
( _\/_  /
( (    \|\
        ,, ,,
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

Looking back, loyal — the run that just ended. Uncredited canonical
form from the ASCII commons.

```text
_      __
\\____{(``o
(      \_'
 \_)-\_)_)
```

### changes_scope drift — Tumbleweed

Sub-flavor of `changes_scope` when the total scope-changes count
across all in-scope projects in the primary horizon is at least 3.
Inherits the `changes_scope` palette color. Freehand for this cast; no
canonical tumbleweed exists in the public commons.

```text
 .-.    .-.    .-.
((.))  ((.))  ((.))   ~~~
 `-'    `-'    `-'
```

## Setup mascot — Farmhouse

"Welcome to the farm — let's set things up." Appears only in the setup
flow ([`../references/setup-flow.md`](../references/setup-flow.md))
and in the first ritual run after a fresh `reconfigure`. `StfoReK`
form from `ascii-art.de/ascii/ghi/house.txt`.

```text
  _m_
/\___\
|_|""|
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
| `shipped` | Tractor |
| `questions` | Walking cat |
| `stalls_aging` | Cow |
| `stalls_no_pr` | Lamb |
| `stalls_silent` | Chickens on nests |
| `stalls_blocked` | Mule |
| `changes_scope` | Signpost |
| `changes_date` | Rooster |
| `quality` | Goose |
| `retrospective` | Dog |
| `changes_scope` drift | Tumbleweed (overrides Signpost) |
| Setup mascot | Farmhouse |
| Empty-brief mascot | Puzzled face |

## Provenance

The art in this file is sourced from established ASCII art collections
in the public commons, with two pieces (signpost, tumbleweed) built
freehand because no compact canonical form exists. Artist signatures
were stripped from the glyphs for visual consistency and recorded
below.

- **Tom Bampton** (`tom`) — tractor. Source:
  `ascii-art.de/ascii/t/tractor.txt`. Trimmed: shorter field on the
  left.
- **fsc / as** — walking cat. Source: `ascii-art.de/ascii/c/cat.txt`.
  Cropped to the top four rows of the piece (head + walking body).
- **Asik** — mule (donkey). Source:
  `ascii-art.de/ascii/def/donkey.txt`. Used verbatim.
- **Joan G. Stark** (`jgs`) — chickens on nests (two-hen strip from a
  larger grid). Source: `ascii-art.de/ascii/c/chicken.txt`.
- **ejm97** — rooster. Source: `ascii-art.de/ascii/pqr/rooster.txt`.
  Used as the seven-row form.
- **Hayley Wakenshaw** (`hjw`) — goose (head crop). Source:
  `ascii-art.de/ascii/ghi/goose.txt`. Cropped from a 16-row canon to
  the top five rows (head + long neck).
- **StfoReK** — farmhouse. Source: `ascii-art.de/ascii/ghi/house.txt`.
  Trimmed ground line.
- **Uncredited canonical** — cow, dog, puzzled face. Treated as
  effectively public-domain.
- **Freehand** — lamb, signpost, tumbleweed. Composed for this cast
  because no canonical compact piece exists in the surveyed
  collections (`ascii-art.de`, `asciiart.eu`, `ascii.co.uk`,
  `chris.com/ASCII`). Replace with canonical art if a fit is found.
