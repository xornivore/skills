# Codex review signals on GitHub

What `chatgpt-codex-connector[bot]` posts, as observed on public PRs in
October 2026. The helper parses these; read this file only when a result
looks wrong, or when Codex's format appears to have changed.

## Trigger

A PR comment `@codex review`, optionally followed by focus text
(`@codex review for security regressions`). Automatic reviews can also
fire when a PR is opened or marked ready. Review rules come from a
`## Code Review Rules` section in the nearest `AGENTS.md`.

## Summary comment (edited in place)

```text
<!-- codex-pull-request-review-summary -->
<!-- codex-review-state:v1 {"code_review":{"commit_sha":"f88576b…","has_any_findings":true,"has_unresolved_findings":true,"status":"completed"},"security_review":{…}} -->

## Codex Review Summary
| Review | Status | Commit | Review trigger |
```

- `status` is one of `running`, `completed`, `failed`, or `null`.
- Trust the findings flags only when `status` is `completed` and
  `commit_sha` matches the head. A `failed` review can still say
  `has_any_findings: true`.

## Review with findings

A PR review, `state: COMMENTED`, with `commit_id` set to the full SHA:

```text
<!-- codex-review-receipt:v1 -->
### 💡 Codex Review
Here are some automated review suggestions for this pull request.
**Reviewed commit:** `b85d6bb0f5`
```

Its inline comments belong to that review (`pull_request_review_id`):

```text
**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  Reconcile immediately when the base SHA changes**

Explanation paragraph.

Useful? React with 👍 / 👎.
```

The badges seen are `P0` (red), `P1` (orange) and `P2` (yellow). `line`
is null when the line is outdated; `original_line` still has it.

## No findings

Any of these signals, often together:

- An issue comment: `Codex Review: Didn't find any major issues. Keep them coming!`
  followed by ``**Reviewed commit:** `ad9c434454` ``. The closing phrase varies.
  The apostrophe may be a typographic `’`.
- A summary marker showing `completed` with `has_any_findings: false`.
- A 👍 (`+1`) reaction by the bot on the PR itself. It is never removed
  and names no commit, so an old 👍 means nothing for a new head.

While a review runs, the bot puts 👀 on the PR.

## Failures

The bot posts issue comments such as "You have reached your Codex usage
limits for code reviews." Treat them as a hard stop. Many rapid
`@codex review` comments can go unanswered without any error.
