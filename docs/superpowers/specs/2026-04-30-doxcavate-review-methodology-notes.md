---
spec: doxcavate
status: notes (follow-up brainstorm material)
date: 2026-04-30
followup_to: 2026-04-29-doxcavate-design.md
---

# doxcavate review methodology — follow-up brainstorm notes

Working notes captured during PR #3. The actual review-methodology
section will be drafted in a follow-up PR after #3 merges. Saved here so
the discussion isn't lost. **This file is a working artifact and should
be deleted as part of the follow-up PR that converts these notes into
spec content.**

## Two-pass review

Each new doc goes through two passes after the initial draft. Facts
before craft.

1. **Factcheck pass** — mechanical, exhaustive. Extract every factual
   claim (file paths, function/method/type names, "X calls Y", env
   vars, hostnames, command flags, file:line entry-point references)
   and verify against the codebase via Read/Grep/Bash. Outcomes:
   verified / contradicted / unverifiable. The verification commands
   actually run become the doc's `## Verification` block — the block
   is not speculative, it's the literal trail of the pass.
2. **Persona pass** — heuristic. Adopt a persona keyed to the doc's
   kind, re-read the draft as that reader, produce concrete changes.

## Personas (per doc kind)

| Doc kind | Persona |
| --- | --- |
| `how-it-works-*` | Skeptical technical reviewer (seasoned engineer) who will grep what you claim. |
| `learning-path-*` | Newcomer at hour zero who doesn't share your assumptions. |
| `runbook-*` | Operator who needs concise, actionable instructions leading to system recovery. |
| `service-map.md` | Completeness reviewer — looking for missing integrations and unstated assumptions. |
| `glossary.md` | Completeness reviewer — looking for missing terms and inconsistent definitions. |
| `index.md` | Skim-reader who needs to find the right doc in <30 seconds. |

## Feedback quality bar

Two loops only land at the sweet spot of effectiveness when the feedback
is actionable. The review passes are **not** for bikeshedding or
relentless critique. The bar:

- **Actionable, not aesthetic.** Every piece of feedback names a
  specific change to apply.
- **If the reviewer can produce the fix, the reviewer produces the
  fix.** Reviewer output is ideally a patch (or near-patch) the
  authoring agent applies. "Identify a problem" without "propose a
  fix" is acceptable only when the fix requires context the reviewer
  cannot reach.
- **No taste arguments.** Two ways of phrasing the same fact, neither
  ambiguous nor wrong, is bikeshedding — skip it.
- **Brevity is a feature.** Reviewer output should fit on one screen
  for a doc of typical size. A long review list is a smell that the
  reviewer is generating noise.

### Example: bad vs. good feedback

| Don't | Do |
| --- | --- |
| "This section feels too long." | "Lines 45-60 repeat the env-var list from line 12. Replace with 'See env vars above.'" |
| "I'd phrase this differently." | "'Orchestrates ingestion' is ambiguous — code shows a fixed-size goroutine pool. Replace with 'spawns a fixed-size goroutine pool that processes ingestion tasks concurrently'." |
| "Add more detail." | "Verification block omits env vars set in `setup.sh:23`. Add `grep -E '^export DOX_' setup.sh` to the verification block." |
| "Not beginner-friendly enough." | "A newcomer won't know what 'ingestion topic' means. Either link to the glossary entry or define it inline on line 8." |
| "Consider restructuring." | "Move `## Verification` above `## External dependencies` — the operator persona needs verification first." |

## Loop and termination

```text
draft → factcheck → persona → (changes? → focused factcheck → done) | done
```

- **New docs:** one full factcheck pass and one full persona pass
  required.
- **Doc updates / refreshes:** factcheck scopes to changed claims;
  persona pass runs only if the change is reader-visible (sectioning,
  anchors, voice). Internal-only edits skip persona.
- **Done** = both passes ran cleanly with no outstanding contradictions.
  Unverifiable claims are not contradictions — they are explicitly
  acknowledged via the `> note: not independently verified` callout.

## Dispatched agents

Both passes can be dispatched as agents for long docs or large repos:

- **Factcheck dispatch:** "Here is the draft. Here is the codebase.
  Return every factual claim and the verification result (verified |
  contradicted | unverifiable) with evidence."
- **Persona dispatch:** "You are `<persona>`. Read this draft. Return a
  prioritized list of concrete changes to apply (ideally as patches),
  each with a short rationale. Brevity over completeness — the goal is
  actionable feedback, not an exhaustive critique."

Both agents are read-only — they never edit the doc. The main-context
authoring agent applies findings. This keeps responsibility clear and
the resulting changes auditable.

## Still open

- How strict should factcheck be on truly trivial edits (typo fix,
  link rewording, prose with no factual change)? Leaning: factcheck
  always runs, but scopes tightly to claims that changed. Never skips
  entirely.
- Should personas be configurable per-repo (e.g., a custom oncall
  persona for a repo with very specific operational conventions)?
  Leaning: v2. v1 default briefs cover most cases.
- Verification block contents — just commands, or commands + expected
  output? Leaning: commands only for v1; expected-output pairs better
  with the future drift-detection sibling skill.

## Follow-up plan

Open a follow-up PR after PR #3 merges. The new section likely lands as
section 8 in the spec ("Review methodology"), between "Doc structure"
and "Related services", incorporating these notes plus any refinements
that surface in the brainstorm. **Delete this notes file as part of
that PR.**
