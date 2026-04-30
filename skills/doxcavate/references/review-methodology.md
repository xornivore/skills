# Review methodology

Every newly drafted doc goes through two review passes: a **factcheck
pass** that grounds the doc in code, and a **persona pass** that asks
whether the doc serves its intended reader. Facts before craft.

## Factcheck pass

Mechanical, exhaustive. Extract every factual claim from the draft and
verify it against the codebase:

- **Claim shapes:** file paths, function/method/type names, "X calls Y"
  relationships, env vars, hostnames, config keys, command names and
  flags, `file:line` entry-point references.
- **Verification:** Read or Grep per claim; Bash where it helps. For
  larger drafts, fan out a dispatched agent — verification is
  parallel-shaped.
- **Outcomes:**
  - **Verified** — leave the claim in place.
  - **Contradicted** — fix the doc; never silently leave the bad claim
    in.
  - **Unverifiable** (claim about an external service the skill cannot
    reach) — carry the claim forward with an explicit
    `> note: not independently verified` callout.
- **Verification block as byproduct.** The grep patterns and shell
  commands the pass actually ran become the doc's `## Verification`
  anchor for `how-it-works-*` and `runbook-*`. The block is **commands
  only** for v1 — any reader (human or future drift-detection skill) can
  run them and compare results to the prose. Capturing expected output is
  a v2 expansion that pairs with drift detection.
- **Never skippable.** Factcheck is what makes a doxcavate doc worth
  trusting. There is no flag to skip it.

## Persona pass

Heuristic. Adopt a persona keyed to the doc's kind and re-read the draft
as that reader. Briefs are concrete on purpose — abstract personas don't
catch real failure modes.

| Doc kind | Persona |
| --- | --- |
| `how-it-works-*` | Skeptical technical reviewer (seasoned engineer) who will grep what you claim. |
| `learning-path-*` | Newcomer at hour zero who doesn't share your assumptions. |
| `runbook-*` | Operator who needs concise, actionable instructions leading to system recovery. |
| `service-map.md` | Completeness reviewer — looking for missing integrations and unstated assumptions. |
| `glossary.md` | Completeness reviewer — looking for missing terms and inconsistent definitions. |
| `index.md` | Skim-reader who needs to find the right doc in under 30 seconds. |

Persona briefs (full text per kind) live in
[personas](./personas.md).

### Output contract

The persona pass returns a **ranked list of ≤7 items**, each shaped:

```yaml
location: <line range or anchor in the draft>
problem: <one sentence describing what's wrong>
proposed_change: <one sentence describing what to do about it>
patch: |                  # optional
  <verbatim replacement text>
```

- The cap of 7 is hard. If the reviewer sees more than 7 issues, it
  triages and drops the lowest-ranked items. A 30-item review list is a
  reviewer-noise smell, not a doc-quality signal.
- **Items are ordered by priority, descending.** Substance first; nits
  last.
- **Patches when possible.** If the reviewer can produce the literal
  replacement text, it ships it in `patch`. The authoring agent applies
  the patch verbatim. If the reviewer lacks context to write a good
  patch, it ships the tuple without `patch` and the authoring agent
  writes the fix.

### Quality bar

The reviewer is **not** for bikeshedding or relentless critique:

- **Actionable, not aesthetic.** Every item names a specific change to
  apply.
- **Fix when possible.** "Identify a problem" without "propose a fix" is
  acceptable only when the fix requires context the reviewer cannot
  reach.
- **No taste arguments.** Two ways of phrasing the same fact, neither
  ambiguous nor wrong, is bikeshedding — skip it.
- **Brevity is a feature.** The cap exists to enforce triage; ranking
  exists so the lowest-priority items get dropped, not the
  highest-priority ones.

Examples of the bar:

| Don't | Do |
| --- | --- |
| "This section feels too long." | "Lines 45-60 repeat the env-var list from line 12. Replace with 'See env vars above.'" |
| "I'd phrase this differently." | "'Orchestrates ingestion' is ambiguous — code shows a fixed-size goroutine pool. Replace with 'spawns a fixed-size goroutine pool that processes ingestion tasks concurrently'." |
| "Add more detail." | "Verification block omits env vars set in `setup.sh:23`. Add `grep -E '^export INGEST_' setup.sh`." |
| "Not beginner-friendly enough." | "A newcomer won't know what 'ingestion topic' means. Either link to the glossary entry or define it inline on line 8." |
| "Consider restructuring." | "Move `## Verification` above `## External dependencies` — the operator persona needs verification first." |

## Loop and termination

```text
draft
  → factcheck
  → persona (≤7 ranked items)
  → authoring agent applies all items
  → focused factcheck (only the regions the persona pass changed)
  → done
```

- **Default: single round.** One factcheck, one persona pass, one
  focused factcheck on the applied changes. No automatic re-run of
  persona.
- **Done** = focused factcheck clean, no outstanding contradictions.
  Unverifiable claims aren't contradictions; they ship with the
  `> note: not independently verified` callout.
- **Doc updates** (refresh of an existing doc): factcheck scopes to
  changed claims; persona runs only if the change is reader-visible
  (sectioning, anchors, voice). Internal-only edits skip persona by
  default.
- **Halt paths** for drastically broken drafts are described in
  [Escape hatches](#escape-hatches). The loop never silently truncates a
  draft that needs to be rethought.

## Opt-in deviations

Two deviations are supported, signaled either via prompt hint or
`.doxcavate.yml`:

- **Thorough mode** — runs to fixed-point with a hard cap of 3 full
  rounds. Stops when the persona pass returns zero items, the factcheck
  pass shows zero contradictions, or the cap fires. Use when stakes
  warrant it (a cornerstone runbook, a learning path many newcomers will
  touch).
- **Skip persona** — runs factcheck only. Use for bulk-migration or
  format-only edits. Never available for newly drafted docs.

```yaml
# .doxcavate.yml
review:
  thorough: false        # default; true = run-to-fixed-point, cap 3 rounds
  persona: required      # default; "optional" = honor "skip persona" prompt hints
```

Prompt hints recognized by the skill: "rigorously" / "thorough review" →
thorough mode; "skip persona" / "mechanical" / "format-only" → skip
persona (only when `review.persona: optional`).

## Dispatched agents for review

Both passes can be dispatched as agents when the doc is long or the
codebase is large:

- **Factcheck dispatch:** "Here is the draft. Here is the codebase.
  Return every factual claim and the verification result (verified /
  contradicted / unverifiable) with evidence."
- **Persona dispatch:** "You are `<persona>`. Read this draft. Return
  the persona-pass output contract: a ranked list of ≤7 items, each with
  `location` / `problem` / `proposed_change` and an optional `patch`.
  Brevity is a feature. If you have more than 7 items, you've stopped
  triaging — drop the bottom ones."

Both agents are **read-only**. They never edit the doc. The authoring
agent applies findings in the main context, which keeps responsibility
clear and the resulting changes auditable.

## Escape hatches

The cap of ≤7 ranked items + the ranking are how the review enforces
brevity on healthy docs. They are **not** a way to silently truncate
genuinely broken drafts. Two escape conditions halt the loop and surface
the situation so the plan can be rethought rather than papered over.

### `E_TOO_MANY_CONTRADICTIONS` (factcheck overflow)

The factcheck pass halts and emits a structured diagnosis when
contradicted claims cross either threshold:

- **Ratio threshold:** more than 7 contradicted claims AND more than 30%
  of extracted claims contradicted.
- **Absolute threshold:** more than 20 contradicted claims, regardless of
  ratio.

Output:

```yaml
result: halt
reason: E_TOO_MANY_CONTRADICTIONS
contradictions: <count> of <total claims>
ratio: <percentage>
top_examples:               # ranked; most drastic first
  - claim: <contradicted claim>
    evidence: <what the code actually says>
  - claim: ...
    evidence: ...
hypothesis: <best guess at root cause — stale assumptions, scope too
  broad, draft based on misunderstanding of the area, code refactored
  since prior doc, etc.>
```

Do **not** silently apply fixes from a draft that fails this check — the
doc is too far from reality for surface fixes to help. Offer the user
three recovery paths:

- **Redraft** — typical when the draft misunderstood the area.
- **Narrow scope** — when the draft tried to cover too much.
- **Re-investigate** — re-run the production-sources pass (existing
  docs, code, commits) before drafting again.

### `E_PERSONA_OVERFLOW` (persona overflow)

The persona reviewer self-reports the same situation in its own domain.
If it would have to drop **substantive** (non-nit) items to fit the ≤7
cap, it returns an overflow result instead of the normal ranked list:

```yaml
result: halt
reason: E_PERSONA_OVERFLOW
diagnosis: |
  <one paragraph from the persona's perspective on what's
  fundamentally wrong with the draft>
recommendation: <e.g., "redraft with X reorganization", "narrow
  scope to Y", "this doc kind is wrong for the audience and the
  draft should be re-classified as different-kind">
```

The same recovery options apply. Overflow is **not** the same as "the
persona sees flaws beyond rank 7" — those just get dropped per the
brevity rule. Overflow is reserved for cases where the doc fails its
persona structurally and patches at the line level won't help.

### Why explicit halt

Silent truncation of a broken draft trains future readers to distrust the
doc — they hit one wrong claim and stop trusting the rest. Explicit halts
cost more upfront but produce docs that stay trustworthy. The escape
hatches are the design choice that makes the brevity cap honest.

## Action checklist (after a draft is produced)

1. Run the factcheck pass. If thresholds tripped → emit
   `E_TOO_MANY_CONTRADICTIONS` and halt.
2. Run the persona pass for the doc's kind (see
   [personas](./personas.md)). If reviewer reports overflow → emit
   `E_PERSONA_OVERFLOW` and halt.
3. Apply all returned items, preferring `patch` over textual instruction.
4. Run the focused factcheck on changed regions only.
5. If thorough mode (config or prompt hint), repeat 1–4 until factcheck
   shows zero contradictions and persona returns zero items, or until 3
   rounds elapsed.
6. Done.
