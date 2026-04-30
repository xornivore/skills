# Factcheck pass

Mechanical, exhaustive. Extract every factual claim from the draft and
verify it against the codebase. Run this *before* any persona
review — facts before craft.

## Claim shapes

File paths, function/method/type names, "X calls Y" relationships, env
vars, hostnames, config keys, command names and flags, `file:line`
entry-point references.

## Verification

Read or Grep per claim; Bash where it helps. For larger drafts, fan
out a dispatched agent — verification is parallel-shaped.

**Factcheck dispatch prompt:** "Here is the draft. Here is the
codebase. Return every factual claim and the verification result
(verified / contradicted / unverifiable) with evidence." The
dispatched agent is read-only; the authoring agent applies findings.

## Outcomes

- **Verified** — leave the claim in place.
- **Contradicted** — fix the doc; never silently leave the bad claim
  in.
- **Unverifiable** (claim about an external service the skill cannot
  reach) — carry the claim forward with an explicit
  `> note: not independently verified` callout.

## Verification block as byproduct

The grep patterns and shell commands the pass actually ran become the
doc's `## Verification` anchor for `how-it-works-*` and `runbook-*`.
The block is **commands only** for v1 — any reader (human or future
drift-detection skill) can run them and compare results to the prose.
Capturing expected output is a v2 expansion that pairs with drift
detection.

## Non-skippable

There is no flag, prompt hint, or config override that skips factcheck.
Factcheck is what makes a doxcavate doc worth trusting.

## Escape hatch: `E_TOO_MANY_CONTRADICTIONS`

Halt the factcheck pass and emit a structured diagnosis when
contradicted claims cross either threshold:

- **Ratio threshold:** more than 7 contradicted claims AND more than
  30% of extracted claims contradicted.
- **Absolute threshold:** more than 20 contradicted claims, regardless
  of ratio.

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

Do **not** silently apply fixes from a draft that fails this check —
the doc is too far from reality for surface fixes to help. Offer the
user three recovery paths:

- **Redraft** — typical when the draft misunderstood the area.
- **Narrow scope** — when the draft tried to cover too much.
- **Re-investigate** — re-run the production-sources pass (existing
  docs, code, commits) before drafting again.

## Action checklist

1. Extract every claim from the draft.
2. Verify each claim (Read / Grep / Bash; fan out for large drafts).
3. If thresholds tripped → emit `E_TOO_MANY_CONTRADICTIONS` and halt.
4. Otherwise: leave Verified claims; fix Contradicted ones in place;
   carry Unverifiable forward with the callout.
5. Capture the run commands as the doc's `## Verification` anchor.
6. Hand off to persona review (see
   [persona-review](./persona-review.md)).
