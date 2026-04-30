# Persona review

Heuristic. Adopt a persona keyed to the doc's kind and re-read the
draft as that reader. Briefs are concrete on purpose — abstract
personas don't catch real failure modes.

## Persona by doc kind

| Doc kind | Persona |
| --- | --- |
| `how-it-works-*` | Skeptical seasoned engineer who will grep what you claim. |
| `learning-path-*` | Newcomer at hour zero who doesn't share your assumptions. |
| `runbook-*` | Operator who needs concise, actionable instructions leading to system recovery. |
| `service-map.md` | Completeness reviewer — looking for missing integrations and unstated assumptions. |
| `glossary.md` | Completeness reviewer — looking for missing terms and inconsistent definitions. |
| `index.md` | Skim-reader who needs to find the right doc in under 30 seconds. |

Full persona briefs are prompt templates, not references. Load them
from `assets/persona-prompts/<kind>.md` at the dispatch step. Quote
the brief verbatim in the dispatch prompt.

## Dispatch

When the doc is long or the codebase is large, dispatch the persona
review as an agent:

> "You are `<persona>`. Read this draft. Return the persona-pass
> output contract: a ranked list of ≤7 items, each with `location` /
> `problem` / `proposed_change` and an optional `patch`. Brevity is
> a feature. If you have more than 7 items, you've stopped
> triaging — drop the bottom ones."

The dispatched agent is read-only; the authoring agent applies
findings.

## Output contract

Return a **ranked list of ≤7 items**, each shaped:

```yaml
location: <line range or anchor in the draft>
problem: <one sentence describing what's wrong>
proposed_change: <one sentence describing what to do about it>
patch: |                  # optional
  <verbatim replacement text>
```

- The cap of 7 is hard. If the reviewer sees more than 7 issues,
  triage and drop the lowest-ranked items. A 30-item review list is a
  reviewer-noise smell, not a doc-quality signal.
- **Items are ordered by priority, descending.** Substance first; nits
  last.
- **Patches when possible.** If the reviewer can produce the literal
  replacement text, it ships it in `patch`. The authoring agent
  applies the patch verbatim. If the reviewer lacks context to write
  a good patch, it ships the tuple without `patch` and the authoring
  agent writes the fix.

## Quality bar

The reviewer is **not** for bikeshedding or relentless critique:

- **Actionable, not aesthetic.** Every item names a specific change
  to apply.
- **Fix when possible.** "Identify a problem" without "propose a fix"
  is acceptable only when the fix requires context the reviewer
  cannot reach.
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

## Escape hatch: `E_PERSONA_OVERFLOW`

If the reviewer would have to drop **substantive** (non-nit) items
to fit the ≤7 cap, return an overflow result instead of the normal
ranked list:

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

The same three recovery options apply (redraft / narrow scope /
re-investigate). Overflow is **not** "the persona sees flaws beyond
rank 7" — those just get dropped per the brevity rule. Overflow is
reserved for cases where the doc fails its persona structurally and
patches at the line level won't help.

## Action checklist

1. Look up the persona for the doc's kind in the table above.
2. Load `assets/persona-prompts/<kind>.md` and quote the brief
   verbatim in the dispatch prompt.
3. Dispatch the review (or run inline for short drafts).
4. If reviewer reports `E_PERSONA_OVERFLOW` → halt and offer the
   three recovery options.
5. Otherwise apply all returned items, preferring `patch` over
   textual instruction.
6. Hand back to [review-loop](./review-loop.md) for the focused
   factcheck.
