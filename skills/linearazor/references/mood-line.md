# Mood line

Loaded at the Phase-2 presentation step. The mood line is one
sentence at the top of the full-ritual output, in the tool's voice.
Animals serve as a unit of measure when they appear in the line.

## Voice

Specific, observational, light. Names what is in the brief without
verdicts.

Exemplars (the model should imitate this register):

```text
Three cows in the field this week, one bee, and a lemur with a good question.
```

```text
Two bees and a beaver this cycle — the field is quiet, but the snail
on ENG-446 is worth a look.
```

```text
An owl this morning — looking back at the May runtime cut so the June
one doesn't end the same way.
```

```text
A chameleon and three foxes — the runtime project is changing shape
faster than it's moving.
```

```text
A heron and two questions — the next cycle has acceptance criteria
to nail down.
```

## Constraints (presentation-layer rules, not signals)

Hard rule 9 binds. No scoring, no streaks, no leaderboards. Forbidden
patterns:

| Wrong | Right |
| --- | --- |
| "Best week yet — 8 bees!" | "Three bees and a beaver this week." |
| "Stall count up 30% from last cycle." | "Three cows in the field — worth a chat about ENG-423 and ENG-446." |
| "Bob: 4 bees · Carol: 3 bees" | (No per-person framing in the mood line.) |
| "Animals as emoji decorations" | (No emoji. Color and prose carry the cast.) |

The brief never tallies animals across runs as metrics. There is no
state file in which to persist counters — the rule is structurally
enforced.

## Suppression

`linearazor` invocations with `no-mood` suppress the mood line:

| Mode | Default | With `no-mood` |
| --- | --- | --- |
| `brief` | mood line present | suppressed |
| `digest` | mood line present | suppressed |
| full ritual | mood line present | suppressed |
| `share` | mood line present | suppressed |

## Composition input

The mood line is generated last in the Phase-2 pipeline, after all
per-project blocks and the lookahead block are composed. The model
sees the full draft brief and selects animal references that actually
appear in the rendered output — never invents a unit not present.

**Audit:** every animal name appearing in the mood line must appear
in at least one per-project block or the lookahead block of the same
run.
