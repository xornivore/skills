# Theme: farm

The default animation theme for linearazor. Eleven lane icons plus a
setup mascot and an empty-brief mascot — sourced from public-commons
ASCII collections where possible, with two pieces freehand (signpost,
tumbleweed) where the commons had no compact canonical form.

For the theming contract (lane spec, padding rules, replacement rules,
audit cues) see [`../assets/animation.md`](../assets/animation.md).

## Cast

### shipped — Galloping horse

Slanted body, mane streaming, motion implied. `ejm96` form from
`ascii-art.de/ascii/ghi/horse.txt`.

```text
 _,,
"-=\~     _
   \\~___( ~
  _|/---\\_
  \        \
```

### questions — Walking cat

Side-profile walking cat — alert head on the left, body extending
right. `BP` form from `ascii-art.de/ascii/c/cat.txt`.

```text
  /\_/\
  >^.^<.---.
 _'-`-'     )\
(6--\ |--\ (`.`-.
    --'  --'  ``-'
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

### stalls_no_pr — Pig

Lying-down pig, curly tail — present and slow, doing pig things,
producing nothing visible to a PR. `Asik` form from
`ascii-art.de/ascii/pqr/pig.txt`.

```text
  ___&
e'^_ )
  " "
```

### stalls_silent — Chicken

A chicken sitting still in the coop — present, alert, not moving
forward. Neil Smith form from `ascii-art.de/ascii/c/chicken.txt`.

```text
   \\
   (o>
\\_//)
 \_/_)
  _|_
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

Looking back, loyal — the run that just ended. `hjw` (Hayley
Wakenshaw) form from the ASCII commons.

```text
   __
o-''|\_____/)
 \_/|_)     )
    \  __  /
    (_/ (_/
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
| `questions` | Walking cat |
| `stalls_aging` | Cow |
| `stalls_no_pr` | Pig |
| `stalls_silent` | Chicken |
| `stalls_blocked` | Mule |
| `changes_scope` | Signpost |
| `changes_date` | Rooster |
| `quality` | Goose |
| `retrospective` | Dog |
| `changes_scope` drift | Spider (overrides Signpost) |
| Setup mascot | Barn |
| Empty-brief mascot | Puzzled face |

## Provenance

The art in this file is sourced from established ASCII art collections
in the public commons, with two pieces (signpost, broken fence) built
freehand because no compact canonical form exists. Artist signatures
were stripped from the glyphs for visual consistency and recorded
below.

- **ejm96** — galloping horse. Source:
  `ascii-art.de/ascii/ghi/horse.txt`. Used verbatim.
- **BP** — walking cat. Source: `ascii-art.de/ascii/c/cat.txt`. Used
  verbatim with the artist signature stripped.
- **Asik** — pig and mule (donkey). Sources:
  `ascii-art.de/ascii/pqr/pig.txt`,
  `ascii-art.de/ascii/def/donkey.txt`. Used verbatim with signatures
  stripped.
- **Neil Smith** — chicken. Source:
  `ascii-art.de/ascii/c/chicken.txt`. Used verbatim with the artist
  signature stripped.
- **ejm97** — rooster. Source: `ascii-art.de/ascii/pqr/rooster.txt`.
  Used as the seven-row form.
- **Hayley Wakenshaw** (`hjw`) — goose (head crop) and dog. Sources:
  `ascii-art.de/ascii/ghi/goose.txt` (cropped to head + neck),
  ASCII commons (dog).
- **Uncredited canonical** — barn (small barn from
  `asciiart.eu/buildings-and-places/houses`), cow, spider, puzzled
  face. Treated as effectively public-domain.
- **Freehand** — signpost. Composed for this cast because no
  canonical compact piece exists in the surveyed collections. Replace
  with canonical art if a fit is found.
