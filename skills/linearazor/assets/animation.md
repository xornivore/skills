# Animation cast

The cast is a themed asset. The lane spec is canonical — every theme
covers the same eleven signal lanes plus a setup mascot and an
empty-brief mascot. Only the *icons* swap.

The active theme is selected by the `[render] animation_theme` field
in `<group>.toml`. Legal values are exactly the `## Theme:` headings in
this file: `animal-kingdom` (default) and `vehicles`. An unknown or
missing value falls back to `animal-kingdom`.

One icon per signal category per brief, never one per project and
never one per item. Color via the palette role in the heading — see
[../references/palettes.md](../references/palettes.md).

Every icon block is bracketed by exactly one blank line above and one
blank line below in the rendered output — see
[`../references/presentation.md`](../references/presentation.md)
"ASCII art padding (universal)". Same rule applies to the setup mascot
and the empty-brief mascot.

The cast deliberately mixes facing directions and sizes. Compact
public-commons ASCII is the brief; perfect uniformity is not.

**Left-margin convention.** Every icon renders flush left at column 0
of the source block. The renderer adds no extra leading indent — the
icon sits directly above the lane title and project sub-headers below
it, none of which carry the old per-project two-space lane indent that
this convention used to compensate for. Replacing an icon? Strip any
leading whitespace shared by all rows before committing it; the
leftmost glyph of any row must sit at column 0.

## Lane spec

The roles are theme-agnostic. Each theme's section below maps these
roles to icons.

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

## Themes

### Theme: animal-kingdom

The original cast. Whimsical register, eleven creatures and friends.

#### shipped — Bee

Active, momentum, just shipped. Motion lines trail right.

```text
   _   _
  ( | / )
\\ \|/,'_
(")(_)()))=-
   <\\
```

#### questions — Cat

Sitting, curious, alert.

```text
 /\_/\
( o.o )
 > ^ <
```

#### stalls_aging — Cow

Standing in a field of grass — head down, plodding.

```text
        (__)
`\------(oo)
  ||    (__)
  ||w--||     \|/
```

#### stalls_no_pr — Snail

Slow, antennae up, leaves no trail.

```text
    .----.   @   @
   / .-"-.`.  \v/
   | | '\ \ \_/ )
 ,-\ `-.' /.'  /
'---`----'----'
```

#### stalls_silent — Turtle

Withdrawn, shell-textured, head still extended but quiet.

```text
               __
    .,-;-;-,. /'_\
  _/_/_/_|_\_\) /
'-<_><_><_><_>=/\
  `/_/====/_/-'\_\
   ""     ""    ""
```

#### stalls_blocked — Fish

Small fish trailed by a larger one — surrounded, not moving forward.

```text
               O  o
          _\_   o
>('>   \\/  o\ .
       //\___=
          ''
```

#### changes_scope — Penguin

Stands sentinel, eye spotting the change.

```text
      __
    .` o)=-
   /.-.`
  //  |\
  ||  |`
_,:(_/_
```

#### changes_date — Snake

Sinuous, shape-shifting, the milestone date moving.

```text
             ____
            / . .\
            \  ---<
             \  /
   __________/ /
-=:___________/
```

#### quality — Bat

Wings out, alert, watching for what's missing.

```text
  _   ,_,   _
 / `'=) (='` \
/.-.-.\ /.-.-.\
`      "      `
```

#### retrospective — Dog

Looking back, loyal, the run that just ended.

```text
_      __
\\____{(``o
(      \_'
 \_)-\_)_)
```

#### changes_scope drift — Spider

Eight-legged, sideways and multidirectional. Sub-flavor of the
`changes_scope` signal — rendered in place of the penguin when the
total scope-changes count across all in-scope projects in the primary
horizon is at least 3, signalling sustained drift rather than a
one-off change. Inherits the `changes_scope` palette color.

```text
 ||  ||
 \\()//
//(__)\\
||    ||
```

#### Setup mascot — Duck

Appears only in the setup flow ([`../references/setup-flow.md`](../references/setup-flow.md))
and in the first ritual run after a fresh `reconfigure`. Never in
normal brief output. The rubber-duck-debugging association is
intentional: the setup flow is conversational, asks the user to
articulate their workspace shape one question at a time, and the duck
is the universal "let me explain this to you" companion.

```text
    __
___( o)>
\ <_. )
 `---'
```

#### Empty-brief mascot — Puzzled face

Appears only when the ritual runs but every signal lane comes up empty
across every in-scope project — nothing shipped, no questions, no
changes, no stalls, no quality findings. Replaces the mood line in
that case; the whole lane stack is suppressed since every lane would
be empty. Honest about the edge case: "I looked, nothing surfaced —
you tell me if that's good." Better than rendering an empty brief or a
forced upbeat mood line.

```text
  .--.
 / o o \
|   ^   |
 \ --- /
```

#### Lane → icon (animal-kingdom)

| Role | Icon |
| --- | --- |
| `shipped` | Bee |
| `questions` | Cat |
| `stalls_aging` | Cow |
| `stalls_no_pr` | Snail |
| `stalls_silent` | Turtle |
| `stalls_blocked` | Fish |
| `changes_scope` | Penguin |
| `changes_date` | Snake |
| `quality` | Bat |
| `retrospective` | Dog |
| `changes_scope` drift | Spider (overrides Penguin) |
| Setup mascot | Duck |
| Empty-brief mascot | Puzzled face |

### Theme: vehicles

Things that move. Mechanical register; the cast lines up directly
with the momentum metaphor that the brief is already organized around.

#### shipped — Race car

Momentum, just zoomed past — motion lines trail right.

```text
   ______
 _/______\_
|  o    o  |  ~~~
'-(O)--(O)-'
```

#### questions — Scooter

Small, curious, hops around lanes.

```text
  __
 /  \
|o   \____
 \________\
   o----o
```

#### stalls_aging — Rusted truck

Sitting in the lot too long; paint peeling, dots for weathering.

```text
 _____
|_:_:_|____
|__,______|
 /o\.    /o\.
 \_/     \_/
```

#### stalls_no_pr — Wheelbarrow

Manual, no engine — work without automation backing it.

```text
  ______
 /      \_____
/________  \  \
\  ___  /---O )
 \(___)/    \/
```

#### stalls_silent — Parked car

Present, lights off, nothing moving. Dots stand in for windows seen
from the side at night.

```text
     _________
 __/           \__
|  . . . . . . .  |
'-(_)---------(_)-'
```

#### stalls_blocked — Traffic cone

Literally blocking the lane.

```text
    /\
   /  \
  /----\
 /  ==  \
/________\
__________
```

#### changes_scope — Detour sign

Diamond sign, arrow pointing the new way.

```text
  /\
 /->\
/----\
\    /
 \  /
  \/
```

#### changes_date — Odometer

The number moved.

```text
 _________
| _______ |
||0|0|9|3||
||_|_|_|_||
|_________|
```

#### quality — Traffic light

"Did we check before going through?"

```text
 ___
|(O)|
| o |
| o |
|___|
  |
```

#### retrospective — Horse

The run that just ended — a horse rounding out the stable of
mechanized lanes. Animate among machines, the way a retro looks back
at the work that's already left the road.

```text
  ,~~,
 /    \____
|  o       \,
 \    ____,'
  |  |
  |  |
```

#### changes_scope drift — Traffic jam

Three vehicles pressed together — sub-flavor of `changes_scope` when
the total scope-changes count across all in-scope projects in the
primary horizon is at least 3. Inherits the `changes_scope` palette
color.

```text
 _____    _____    _____
/__|__\__/__|__\__/__|__\
 '-o-'    '-o-'    '-o-'
```

#### Setup mascot — Gas pump

Conversational, single-shot — "let's get fueled up before the trip."
Appears only in the setup flow and the first ritual run after a fresh
`reconfigure`.

```text
 ____
| $$ |__
|____|  )
|    |_/
|____|
```

#### Empty-brief mascot — Empty parking lot

Appears only when every signal lane comes up empty across every
in-scope project. Two empty stalls; nothing parked, nothing moving.
Honest about the edge case the same way the puzzled face is in
animal-kingdom.

```text
|         |         |
|    -    |    -    |
|_________|_________|
```

#### Lane → icon (vehicles)

| Role | Icon |
| --- | --- |
| `shipped` | Race car |
| `questions` | Scooter |
| `stalls_aging` | Rusted truck |
| `stalls_no_pr` | Wheelbarrow |
| `stalls_silent` | Parked car |
| `stalls_blocked` | Traffic cone |
| `changes_scope` | Detour sign |
| `changes_date` | Odometer |
| `quality` | Traffic light |
| `retrospective` | Horse |
| `changes_scope` drift | Traffic jam (overrides Detour sign) |
| Setup mascot | Gas pump |
| Empty-brief mascot | Empty parking lot |

## Adding a theme

A new theme is one new `### Theme: <name>` section under "Themes",
covering every role in the lane spec plus the setup and empty-brief
mascots, and ending with a "Lane → icon (`<name>`)" table. The theme
name becomes a legal value of the `animation_theme` config field
automatically — there is no second registry to update.

When picking a theme, two practical constraints:

- Compact ASCII. Each icon block 3-8 rows, roughly 10-30 columns.
  Public-commons ASCII art is the source — no freehand. Strip leading
  whitespace so every row's leftmost glyph sits at column 0.
- Theme-agnostic role coverage. Every role in the lane spec gets an
  icon, plus the setup and empty-brief mascots. No partial themes.

The role assignments themselves can be loose ("a horse counts as a
vehicle if you squint, and that's fine") — themes are presentation
polish, not signal fidelity.

## Replacement

The cast is purely affective. Replacing an icon, changing its pose,
adding a new one, or shipping a new theme is a presentation-layer
change — no signal-layer file needs updating. Hard rule 12 binds.

## Audit

- Each `### Theme:` section covers every role in the lane spec exactly
  once, plus exactly one setup mascot, one empty-brief mascot, and one
  `Lane → icon (<theme>)` summary table at the end. **Audit:** for
  each theme section, count the `####` sub-headings; expected count
  equals the number of roles in the lane spec (11, including the
  drift sub-flavor) plus three (setup mascot, empty-brief mascot,
  lane → icon table) — currently 14.
- The set of `### Theme:` headings equals the set of legal
  `animation_theme` config values. **Audit:** parse the headings; the
  union equals the enum that the setup flow and the config validator
  honor.
- One icon per signal category per brief (never one per project,
  never one per item).
- Every ASCII art block in the rendered output is bracketed by
  exactly one blank line above and one blank line below.
- No emoji anywhere in this file.

## Provenance (TODO)

The art in this file is sourced from established ASCII art collections
in the public commons. Artist signatures were stripped at assembly
time for visual consistency; restoring per-piece attribution is
tracked as follow-up work before the skill is published outside this
repo. Until that pass lands, the safe redistribution stance is: this
file is a presentation-layer asset of the `linearazor` skill,
authored from cultural-commons ASCII art, shipped under the repo's
MIT license alongside the rest of the skill code.

### animal-kingdom

Known artists to credit when the attribution pass happens:

- **Joan G. Stark** (`jgs`) — turtle, bat
- **Shanaka Dias** (`snd`) — penguin
- **Hayley Wakenshaw** (`hjw`) — duck
- **Stef00** — bee
- The cat, cow, snail, fish, snake, dog, spider, and puzzled-face
  pieces come from uncredited canonical forms in the ASCII commons
  and are treated as effectively public-domain.

### vehicles

The race car, scooter, rusted truck, wheelbarrow, parked car, traffic
cone, detour sign, odometer, traffic light, horse, traffic jam, gas
pump, and empty parking lot are stylized from uncredited canonical
forms in the ASCII commons and treated as effectively public-domain.
Same attribution-pass treatment applies before external publication.
