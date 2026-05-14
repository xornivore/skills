# Animation cast

Eleven ASCII animals, one per signal lane. Sourced from established
ASCII art rather than freehand.

One animal per signal category per per-project section, never one per
item. Color via the palette role in the heading — see
[../references/palettes.md](../references/palettes.md).

The cast deliberately mixes facing directions and sizes. The earlier
"all face right, 4-6 lines, 12-20 columns" rule was an aspiration;
the canonical art doesn't all conform, and the canonical art is the
point.

## Cast

### Bee — `shipped`

Active, momentum, just shipped. Motion lines trail right.

```text
              _   _
             ( | / )
           \\ \|/,'_
           (")(_)()))=-
              <\\
```

### Cat — `questions`

Sitting, curious, alert.

```text
 /\_/\
( o.o )
 > ^ <
```

### Cow — `stalls_aging`

Standing in a field of grass — head down, plodding.

```text
\|/          (__)
     `\------(oo)
       ||    (__)
       ||w--||     \|/
   \|/
```

### Snail — `stalls_no_pr`

Slow, antennae up, leaves no trail.

```text
    .----.   @   @
   / .-"-.`.  \v/
   | | '\ \ \_/ )
 ,-\ `-.' /.'  /
'---`----'----'
```

### Turtle — `stalls_silent`

Withdrawn, shell-textured, head still extended but quiet.

```text
                    __
         .,-;-;-,. /'_\
       _/_/_/_|_\_\) /
     '-<_><_><_><_>=/\
       `/_/====/_/-'\_\
        ""     ""    ""
```

### Fish — `stalls_blocked`

Small fish trailed by a larger one — surrounded, not moving forward.

```text
               O  o
          _\_   o
>('>   \\/  o\ .
       //\___=
          ''
```

### Penguin — `changes_scope`

Stands sentinel, eye spotting the change.

```text
         __
      -=(o '.
         '.-.\
         /|  \\
         '|  ||
          _\_):,_
```

### Snake — `changes_date`

Sinuous, shape-shifting, the milestone date moving.

```text
             ____
            / . .\
            \  ---<
             \  /
   __________/ /
-=:___________/
```

### Bat — `quality`

Wings out, alert, watching for what's missing.

```text
        _   ,_,   _
       / `'=) (='` \
      /.-.-.\ /.-.-.\
      `      "      `
```

### Dog — `retrospective`

Looking back, loyal, the run that just ended.

```text
  __      _
o'')}____//
 `_/      )
 (_(_/-(_/
```

### Spider — `scope drift`

Eight-legged, sideways and multidirectional, the scope creeping out.

```text
 ||  ||
 \\()//
//(__)\\
||    ||
```

## Lane → animal table

| Role | Animal |
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
| `scope drift` | Spider |

## Replacement

The cast is purely affective. Replacing an animal, changing its pose,
or adding a new one is a presentation-layer change — no signal-layer
file needs updating. Hard rule 12 binds.

## Audit

- Each lane has exactly one animal in the cast.
- One animal per signal category per per-project section (never one
  per item).
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
