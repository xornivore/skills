# Mood line

Loaded at the Phase-2 presentation step. The mood line is one
sentence at the top of the full-ritual output, in the tool's voice.
Icons from the active animation theme serve as a unit of measure when
they appear in the line.

## Voice

Specific, observational, light. Names what is in the brief without
verdicts. **Verbs do the work** — a catalog-style "X and Y and Z are
here" reads like a sort-shaper. A single icon *doing* something reads
like a teammate noticing.

The grammar is theme-agnostic; the *vocabulary* is the active theme's
cast (see [`../assets/animation.md`](../assets/animation.md)). Pick
adjectives and verbs that fit the noun: a bat can be `patient`, a race
car cannot. A cow can `linger`, an odometer cannot. Drop the adjective
or pick a different verb when the active theme's noun rejects the
animal-kingdom default.

### Primary form (single-focus highlight)

`<adjective> <icon-noun> <verb> [object/context].`

Pick the one signal that most defines the run, name it with an
adjective + icon-noun + verb, and let the rest of the brief carry the
detail. The adjective qualifies the mood; the verb names the action.
One-icon lines are the default in most runs.

#### Exemplars — `animal-kingdom`

```text
A patient bat watches the June runtime cut for acceptance criteria.
```

```text
An impatient bee circles ENG-481 — the backplane shipped Tuesday.
```

```text
A stubborn cow lingers on the scheduler refactor.
```

```text
A drifting penguin nudges the May cut out to May 21.
```

#### Exemplars — `vehicles`

```text
A patient stop sign waits at the June runtime cut for acceptance criteria.
```

```text
A sport car blows past ENG-481 — the backplane shipped Tuesday.
```

```text
An old pick-up truck sits on the scheduler refactor.
```

```text
An exit sign moves the May cut out to May 21.
```

### Secondary form (when a connection is the point)

`<icon-noun-1> <verb> <icon-noun-2>.`

Reserve for runs where the *interaction* between two signals is the
headline. Most runs don't need this; when they do, pick exactly two
icons and a verb that names how they relate. The verb is the point —
vary it. Useful verbs: `watches`, `shadows`, `crosses paths with`,
`outruns`, `chases`, `waits for`, `finds`, `meets`, `avoids`. Pick
verbs that fit the nouns from the active theme.

#### Exemplars — `animal-kingdom`

```text
A dog watches a snake — last cycle's lessons land just as June's
target slides.
```

```text
A bee outruns a cow — runtime shipped Tuesday, but the scheduler
still hasn't moved.
```

```text
A patient bat shadows a snake — quality questions ride alongside
the date moving.
```

#### Exemplars — `vehicles`

```text
A horse trails an exit sign — last cycle's lessons land just as June's
target slides.
```

```text
A sport car outruns a pick-up truck — runtime shipped Tuesday, but the
scheduler still hasn't moved.
```

```text
A patient stop sign shadows an exit sign — quality questions ride
alongside the date moving.
```

### Anti-patterns (avoid these)

```text
WRONG: Three cows, one bee, and a cat are here.
WRONG: Two snakes, a bat, and a few penguins this week.
WRONG: Three pick-up trucks, one sport car, and a scooter are here.
```

These are sort-shapers — they list the cast instead of noticing
anything. If the brief is genuinely about three lanes at once, pick
the most striking and let the lane stack carry the rest.

## Constraints (presentation-layer rules, not signals)

Hard rule 9 binds. No scoring, no streaks, no leaderboards. Forbidden
patterns:

| Wrong | Right |
| --- | --- |
| "Best week yet — 8 bees!" | "An impatient bee circles ENG-481." |
| "Stall count up 30% from last cycle." | "A stubborn cow lingers on the scheduler refactor." |
| "Bob: 4 bees · Carol: 3 bees" | (No per-person framing in the mood line.) |
| "Icons as emoji decorations" | (No emoji. Color and prose carry the cast.) |
| "Three cows, one bee, and a cat are here." | "A patient bat watches the June cut for AC." |

The brief never tallies icons across runs as metrics. There is no
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

The mood line is generated last in the Phase-2 pipeline, after the
full lane stack and the lookahead block are composed. The model sees
the full draft brief plus the active theme's cast and selects icon
references that actually appear in the rendered output — never invents
a unit not present in the brief, and never names an icon from a
non-active theme.

**Audit:** every icon noun appearing in the mood line must (a) belong
to the active theme's cast in `../assets/animation.md`, and (b) appear
in at least one lane of the lane stack or in the lookahead block of
the same run.
