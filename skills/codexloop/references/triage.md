# Triaging Codex findings

Codex tags each inline finding with a severity badge. Use it to order the
work, not as a verdict. Judge every finding against the code.

| Badge | Meaning | Default action |
| --- | --- | --- |
| P0 | Breaks correctness, security, or data | Fix, or stop and ask if the fix is out of scope |
| P1 | Likely bug or significant regression | Fix unless you can show it is wrong |
| P2 | Lower-impact bug, edge case, or robustness gap | Fix when cheap and in scope; otherwise rebut with a reason |

## Rules

- Verify before acting. Reproduce the issue, or trace the code path,
  before changing code. Codex reviews a diff and can miss context.
- Never change correct code just to quiet the bot. A rebuttal with
  evidence is a valid outcome.
- Keep fixes inside the PR's scope. A finding that needs a new feature,
  an API change, or a product call stops the loop.
- Pair each fix with a test when the project has tests for that area.
- Reply on the thread before resolving a rebutted finding, so a human
  reviewer can see why.

Correct rebuttal reply:

```text
Not an issue: `parseRange` is only called after `validate()` in
src/range.ts:41, which rejects empty input. Covered by
test/range.test.ts "rejects empty".
```

Wrong rebuttal reply:

```text
Won't fix.
```

## Replying on a thread

Reply with the REST endpoint, using the first comment's numeric ID (the
`url` fragment `discussion_rNNN` holds it):

```bash
gh api repos/OWNER/REPO/pulls/N/comments/COMMENT_ID/replies \
  --method POST -f body="REASON"
```
