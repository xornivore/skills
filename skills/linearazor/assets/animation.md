# Animation cast

Twelve hand-drawn ASCII animals. One per signal category per per-project
section — not one per item.

All animals face right (toward the finding list below). Mood through
pose, not features. Color via the palette role in the heading —
see [palettes.md](../references/palettes.md).

## Core cast

### Bee — `shipped`

Active, momentum, just shipped.

```text
   \   /
    \,/
   __o___
  /     /
 /_____/   --> done
```

### Lemur — `questions`

Upside down, asking a good question.

```text
        __
       /  \
       \../
       (oo)
     ___||___
    /        \
```

### Cow (in field) — `stalls_aging`

Lying down. Has been here a while.

```text
        ___
       (o,o)
     __/    \____
    (  cow      )___
     \____   ___/
          ||
```

### Snail — `stalls_no_pr`

Moving, but no PR trail behind it.

```text

    .---,
   ( o   `-.
  ()  __    `-.
   `-(__)------'
```

### Turtle — `stalls_silent`

Withdrawn, no signal.

```text
       __
    __/  \__
   /_O    O_\
  /   ____   \
   `--`  `--`
```

### Beaver — `shipped` (praise / active building)

Used at the per-project block when the project shipped strongly.

```text
      _____
     /     \___
    ( beaver  /
     \____/--`
       ||  ||
```

## Extended cast (used sparingly)

### Fox — `changes_scope`

Scope spotted, slipping in or out.

```text
       /\___/\
      ( o   o )
       >  v  <
       /     \--
      (  fox   )---
       \_____/
```

### Chameleon — `changes_date`

Milestone date moved (color shift).

```text
         __
        / .)
   ____( ( )
  /  __ \_  \__
 (__/      ===
```

### Mole — `stalls_blocked`

Underground, blocked, hidden cause.

```text
      ____
   __/o  o\__
  /   __    \
 ( ===    mole)
  `\_/-`---`
```

### Heron — `quality` and lookahead unclarities

Watching, patience, waiting for clarity.

```text
   >.
   / \
  /  /
 /  /
  ||
 _||___
```

### Owl — `retrospective`

Looking back to look forward.

```text
     ___
    (o.o)
    (===)
   /     \
   `-||-`
    || ||
```

### Crab — sideways movement, scope drift

```text

    __||__
   /  o o \
  ( =/  \= )
   `--vv--`
```

## Mood through pose

The cow lies down to read "aging." The lemur hangs upside down to read
"curious / contrarian." The turtle's eyes are closed (`O` versus `o`)
to read "silent." Pose carries the lane meaning — color and animal
identity reinforce, but pose leads.

## Replacement

The cast is purely affective. Replacing an animal, changing its pose,
or adding a new one is a presentation-layer change — no signal-layer
file needs updating. Hard rule 12 binds.

## Audit

- All animals 4–6 lines tall, 12–20 columns wide.
- All face right.
- One animal per signal category per per-project section (never one
  per item).
- No emoji anywhere in this file.
