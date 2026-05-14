# Tone rules

The blameless, signals-not-verdicts voice. Loaded by Phase-2 signal
composition and by every parallel sub-agent. Phrasing rules apply
across all signal lanes.

## Subject-on-issue, never subject-on-person

Hard rule 3 binds: findings name behaviors and identifiers, never
authors.

| Wrong | Right |
| --- | --- |
| "Bob hasn't moved ENG-423 since Monday." | "ENG-423 has been In Progress 11 days." |
| "Carol is behind on the runtime milestone." | "Two issues attached to the runtime milestone are aging." |
| "@bob.wu owns this stall." | "ENG-446 has no PR linked." |
| "The team is slipping." | "Three milestones moved this cycle." |

Forbidden tokens in any emitted prose outside the setup-health footer:

- Any configured member display name.
- Any `@`-prefixed handle.
- Pronouns referring to a person — `they`, `their`, `she`, `he`,
  `his`, `her`, `them`. (Pronouns referring to issues / projects /
  milestones are fine: "ENG-423 has been In Progress 11 days; its
  blocker closed Tuesday.")

**Audit:** grep the rendered prose for the configured member display
names. Any match outside the literal setup-health footer is a
violation. The setup-health footer is the only place member names
appear (and only when name resolution failed).

## Signals, not verdicts

Hard rule 4 binds: no red/yellow/green markers, no severity prefixes,
no judgment vocabulary.

Forbidden tokens:

- Severity vocabulary: `CRITICAL`, `AT RISK`, `BEHIND SCHEDULE`,
  `FAILING`, `BLOCKED` (as a prefix label — the actual `Blocked`
  status from Linear is fine in factual context).
- Decoration: red/yellow/green dots, traffic lights, severity badges.
- Emoji other than the optional razor glyph in the run header
  (hard rule 6).

| Wrong | Right |
| --- | --- |
| "ENG-423 AT RISK — 11 days in progress." | "ENG-423  In Progress 11 days  (default threshold: 7)" |
| "Milestone \"May runtime cut\" is BEHIND SCHEDULE." | `Milestone "May runtime cut" moved from May 14 -> May 21` |
| "Stall." | The factual stall line, with the cow animal rendered above it by the presentation layer. |

**Audit:** grep over the output for `CRITICAL|AT RISK|BEHIND|FAILING`. Any match is a violation.

## Questions are questions

Hard rule 5 binds: every line in the questions block ends with `?`.
Same rule for lookahead unclarities rendered as questions (when the
signal source is "no acceptance criteria" with a question framing).

| Wrong | Right |
| --- | --- |
| "ENG-423 needs an update." | "What's the next concrete step on ENG-423, and is anything blocking it?" |
| "Check on the runtime milestone." | "Is the appetite for the runtime milestone still well-framed?" |

**Audit:** lines in the questions block must match `\?\s*$`.

## Celebrate first

Hard rule 8 binds: the brief leads with the `shipped` lane when it
has content; lanes render in fixed order; an empty `shipped` lane is
omitted entirely and the next non-empty lane leads — never opening
with `stalls` while `shipped` has content.

| Wrong | Right |
| --- | --- |
| Brief opens with the `Stalls` lane while the `Shipped` lane also exists with items. | Brief opens with `Shipped`, then questions, changes, stalls, quality, retrospective. |
| Rendering an empty `Shipped` section with `No completions in window` as a placeholder. | Omitting the `Shipped` lane entirely; the next non-empty lane leads. |

## No scoring, no streaks, no leaderboards

Hard rule 9 binds: the mood line counts animals as flavor; the brief
never tallies them across runs as metrics. There is no state file in
which to persist counters — the rule is structurally enforced.

| Wrong | Right |
| --- | --- |
| "3rd consecutive week with zero stalls — great streak!" | "Three projects shipped this week and one is waiting on a question." |
| "Bob's velocity is up 20% over last cycle." | (No per-person framing. No cross-run comparison.) |

## Acknowledge missing context once

Hard rule 7 binds: full-ritual runs end with the literal disclaimer
string from [`../assets/footer.md`](../assets/footer.md). One line,
unmodified.

## Lookahead voice

Lookahead findings adopt the same tone rules. Unclarities lean toward
question phrasing when the signal source is "no clear definition of
done" — because asking a question is itself the action.

| Wrong | Right |
| --- | --- |
| "ENG-505 is underspecified." | "What does done look like for ENG-505?" |
| "Milestone slipping risk." | `"June runtime cut" — 0 started, 35d to target` |

## Retrospective voice

Retrospective lines are forward-looking only — "what would we want to
know earlier next time?" Never "what went wrong."

| Wrong | Right |
| --- | --- |
| "We missed the May runtime cut because Carol was overloaded." | "What signaled the May runtime cut was at risk that we could have caught earlier?" |
| "Should have caught the scope creep on ENG-470." | "What changed about our understanding of the runtime project that drove the scope changes this cycle? Was it the work or the framing?" |
