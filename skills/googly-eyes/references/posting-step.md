# Posting step

The post step is invoked separately from review. It is the only writing step in the skill — review is read-only.

## Invocation

- `googly-eyes post` — promote findings from the most recent in-session review.
- `googly-eyes post --from <file>` — promote from a saved review output file (cross-session use).

## Selection

| Flag | Posts |
| --- | --- |
| (default) | all `required` findings only |
| `--include optional` | adds `optional` |
| `--include nit,fyi,praise` | adds the named severities |
| `--only <ids>` | exactly the listed finding IDs |
| `--exclude <ids>` | every selected severity minus excluded IDs |

When the selection includes any `required` or `optional`, prompt once before composing the review:

> "You have N praise findings available — include them?"

## Composition

`gh pr review --comment` does not support multi-inline reviews natively. Use the GitHub API directly:

```bash
gh api repos/<owner>/<repo>/pulls/<pr>/reviews \
  --method POST \
  --field event=COMMENT \
  --field body="$SUMMARY" \
  --field "comments=$COMMENTS_JSON"
```

Where:

- `$SUMMARY` is the rendered summary body (see [Summary body](#summary-body) below).
- `$COMMENTS_JSON` is a JSON array of `{path, line, body}` objects.

One atomic review per invocation. Never split into multiple review POSTs.

## Idempotency

Before posting, fetch existing reviews:

```bash
gh pr view <pr> --json reviews -q '.reviews[].body' | grep -F '<!-- googly-eyes:v1 -->'
```

If a match is found, refuse to post unless `--force` is set. The HTML marker in the summary body is how repeat runs detect "we already reviewed this."

## Comment-style filter

Every comment is run through this filter before the body is sent. Reject and rewrite:

| Rule | Reject pattern | Rewrite |
| --- | --- | --- |
| No second-person blame | `^(why did you\|you should\|you forgot\|you missed)` | Subject-on-code: "the concurrency model here…", "this function adds complexity…" |
| Every comment has a `why` | Body lacks "Because" or "This" clause | Block the comment — finding is malformed |
| Prefer pointing-out over prescribing (non-required) | Imperative verbs in non-required findings ("Change X", "Move Y") | "Consider X" / "One option: Y" |
| Severity prefix | Non-required body missing prefix | Prepend `Optional:` / `Consider:` / `Nit:` / `FYI:` / `Praise:` |

## Summary body

```text
👀 googly-eyes review — <commit SHA>

Triage: size=<small|medium|large>, scope=<single|mixed>, description=<strong|weak>

Required: N  ·  Optional: M  ·  Nit: K  ·  FYI: J  ·  Praise: P
Filed below as inline comments.

<!-- googly-eyes:v1 -->
```

## Event type

Default `event=COMMENT`. User opts into `event=REQUEST_CHANGES` with `--request-changes`, valid only if at least one `required` finding is in the selection. Per Google `reviewer/pushback.html`: improving code health happens in small steps; default to the lighter event.

## Failure modes

| Condition | Behavior |
| --- | --- |
| `gh` not authenticated | Print rendered comments and summary to stdout; instruct user to authenticate (`gh auth login`) and re-run. |
| PR closed | Refuse to post; print finding list as terminal output. |
| PR authored by current user (self-review) | Allow (Google practice); add `--self-review` advisory to summary. |
| Finding line missing from PR diff (file changed since review) | Fall back to file-level comment with `(originally @ L<N>)` in body. |
| Local-diff mode, no open PR | Post step unavailable; skill exits cleanly after finding list. |

## Audit cues

- No posted comment body starts with a second-person phrase (audit: regex `^(Why did you|You should|You forgot|You missed)` over composed comments).
- Every non-`required` comment body starts with one of the five severity prefixes (audit: regex `^(Optional|Consider|Nit|FYI|Praise):` over non-required comment bodies).
- Every composed summary contains the idempotency marker `<!-- googly-eyes:v1 -->` (audit: grep the summary body before POST).
