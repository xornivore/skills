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
cast (see [`../themes/`](../themes/)). Pick adjectives and verbs that
fit the noun: a goose can be `patient`, a closed door cannot. A cow can
`linger`, a signpost cannot. The exemplars below use the default
`farm` cast; a new theme either ships its own exemplars in
`../themes/<name>.md` or relies on the same grammar applied to its
own icon nouns.

### Primary form (single-focus highlight)

`<adjective> <icon-noun> <verb> [object/context].`

Pick the one signal that most defines the run, name it with an
adjective + icon-noun + verb, and let the rest of the brief carry the
detail. The adjective qualifies the mood; the verb names the action.
One-icon lines are the default in most runs.

Exemplars (farm theme):

```text
A patient goose watches the June runtime cut for acceptance criteria.
```

```text
A galloping horse blows past ENG-481 — the backplane shipped Tuesday.
```

```text
A stubborn cow lingers on the scheduler refactor.
```

```text
A weathered signpost points the May cut out to May 21.
```

### Secondary form (when a connection is the point)

`<icon-noun-1> <verb> <icon-noun-2>.`

Reserve for runs where the *interaction* between two signals is the
headline. Most runs don't need this; when they do, pick exactly two
icons and a verb that names how they relate. The verb is the point —
vary it. Useful verbs: `watches`, `shadows`, `crosses paths with`,
`outruns`, `chases`, `waits for`, `finds`, `meets`, `avoids`. Pick
verbs that fit the nouns from the active theme.

Exemplars (farm theme):

```text
A dog watches a chicken — last cycle's lessons land just as June's
target slides.
```

```text
A horse outruns a cow — runtime shipped Tuesday, but the scheduler
still hasn't moved.
```

```text
A patient goose shadows a signpost — quality questions ride alongside
the date moving.
```

### Anti-patterns (avoid these)

```text
WRONG: Three cows, one horse, and a cat are here.
WRONG: Two horses, a goose, and a few chickens this week.
```

These are sort-shapers — they list the cast instead of noticing
anything. If the brief is genuinely about three lanes at once, pick
the most striking and let the lane stack carry the rest.

## Constraints (presentation-layer rules, not signals)

Hard rule 9 binds. No scoring, no streaks, no leaderboards. Forbidden
patterns:

| Wrong | Right |
| --- | --- |
| "Best week yet — 8 horses!" | "A galloping horse blows past ENG-481." |
| "Stall count up 30% from last cycle." | "A stubborn cow lingers on the scheduler refactor." |
| "Bob: 4 horses · Carol: 3 horses" | (No per-person framing in the mood line.) |
| "Icons as emoji decorations" | (No emoji. Color and prose carry the cast.) |
| "Three cows, one horse, and a cat are here." | "A patient goose watches the June cut for AC." |

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
to the active theme's cast under `../themes/`, and (b) appear in at
least one lane of the lane stack or in the lookahead block of the
same run.
