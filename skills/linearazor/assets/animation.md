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

## Setup mascot

The duck appears only in the setup flow ([`../references/setup-flow.md`](../references/setup-flow.md))
and in the first ritual run after a fresh `reconfigure`. It is not
tied to a signal lane and never appears in normal brief output —
those have the mood line plus per-project animals already.

The rubber-duck-debugging association is intentional: the setup flow
is conversational, asks the user to articulate their workspace
shape one question at a time, and the duck is the universal "let me
explain this to you" companion.

```text
    __
___( o)>
\ <_. )
 `---'
```

## Empty-brief mascot

The puzzled face appears only when the ritual runs but every signal
lane comes up empty across every in-scope project — nothing shipped,
no questions, no changes, no stalls, no quality findings. Replaces
the mood line in that case; the per-project blocks are suppressed
since they would all be `No completions in window`.

Honest about the edge case: "I looked, nothing surfaced — you tell me
if that's good." Better than rendering an empty brief or a forced
upbeat mood line.

```text
       .--.
      / o o \
     |   ^   |
      \ --- /
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
