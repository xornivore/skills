---
name: codexloop
description: |
  Drives a GitHub pull request to a clean OpenAI Codex code review in
  bounded cycles. Posts "@codex review", waits for a fresh review of the
  current commit, fixes or rebuts each P0/P1/P2 finding, resolves the
  Codex threads, pushes, and repeats until Codex finds no major issues.
  Adapted from Greptile's greploop skill (greptileai/skills), with the
  Python review helper modelled on Ras Mic's fork (michaelshimeles/skills).
  GitHub only. Invoke when the user says "codexloop", "codex loop",
  "loop on codex review", "get codex to sign off on this PR", "fix the
  codex comments until it's clean", "keep running @codex review", or asks
  to address chatgpt-codex-connector feedback on a PR.
license: MIT
compatibility: Requires Python 3.10+, git, jq, and authenticated gh with push access. The Codex GitHub integration (chatgpt-codex-connector) must be enabled on the repository.
metadata:
  author: xornivore
  version: "1.0"
  upstream: greptileai/skills greploop, michaelshimeles/skills greploop
allowed-tools: Bash(gh:*) Bash(git:*) Bash(python3:*)
---

# codexloop

Improve a GitHub PR using Codex review feedback until a fresh review of the
current head reports no findings and no Codex threads remain unresolved.
Codex's verdict complements the project's own checks and your judgment; it
does not replace them.

Adapted from [greploop](https://github.com/greptileai/skills/tree/main/greploop)
by Greptile (MIT). The bundled helper is modelled on the
[greploop rewrite](https://github.com/michaelshimeles/skills/tree/main/greploop)
by Ras Mic. GitHub only. GitLab and Perforce are out of scope.

## Install

```bash
npx skills add xornivore/skills@codexloop --agent claude-code -y
```

## Inputs

- **PR number or URL.** When omitted, use the PR for the current branch:
  `gh pr view --json number,url,headRefName,headRepository`.
- `--max-iterations N`: review cycles, default 5. Each cycle costs a Codex
  review against the user's usage limits, and takes 3 to 8 minutes.
- `--focus TEXT`: extra instructions appended to the trigger, for example
  `--focus "for security regressions"` posts `@codex review for security regressions`.

Apply the user's existing authorization and scope. A request to only read
Codex's feedback does not authorize edits, pushes, or trigger comments.

## Setup

1. Resolve `OWNER/REPO` and the PR number. Confirm the PR is open and that
   its head branch is the branch checked out in your working tree. If it
   is not, stop and ask. Never switch another task's checkout.
2. Set `REVIEW` to the absolute path of `scripts/codex_review.py` inside
   this skill. Record the run's start time and give the run its own
   attempt directory, so earlier runs never collide with or count toward
   this one:

   ```bash
   RUN_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   RUN_DIR=".artifacts/codexloop/pr-N/${RUN_START//:/}"   # e.g. .../2026-10-17T015314Z
   ```

   Shell variables do not persist between commands, so reuse the literal
   values in later steps. Add `.artifacts/` to `.git/info/exclude` so
   attempt files are never committed.
3. Make sure the working tree has no unpushed task changes before the
   first trigger. Codex reviews the pushed head, not your local edits.

## Review cycle

Repeat, counting every cycle against the cap, including cycles that
produce no edits:

1. **Start one attempt.** Read the helper contract in
   [helper](./references/helper.md) before the first run.

   ```bash
   python3 "$REVIEW" start --repo OWNER/REPO --pr N \
     --output RUN_DIR/attempt-1.json
   ```

   If Codex is already reviewing this exact head (an automatic review on
   push, for example), `start` adopts that run instead of posting a
   duplicate. Never post `@codex review` by hand. Rapid repeated triggers
   get silently dropped and burn usage.
2. **Wait for the fresh result.**

   ```bash
   python3 "$REVIEW" wait RUN_DIR/attempt-1.json
   ```

   It exits 0 with `review_ready` JSON, or exits 1 with an error message.
   An error is a stop condition. Do not retry `start` with the same file,
   and do not fall back to reading older reviews. When a result looks
   wrong, or Codex's comment format seems to have changed, compare the
   raw payloads against [codex-signals](./references/codex-signals.md).
3. **Collect every open finding.** Take the `findings` from the result,
   then list all unresolved Codex threads, including ones from earlier
   commits:

   ```bash
   python3 "$REVIEW" threads --repo OWNER/REPO --pr N
   ```

   Older unresolved threads stay relevant until addressed, even when
   `outdated` is true.
4. **Check the exit condition.** Finish when the result has
   `"clean": true`, `threads` returns an empty list, and the project's
   relevant checks pass. Otherwise continue.
5. **Triage each finding in context.** Read the file and the whole thread
   discussion. Severity guidance lives in
   [triage](./references/triage.md).
   - Valid: fix it within the PR's scope.
   - False positive: write down the reason and the evidence (a test, a
     code path, a spec line). Reply on the thread with that reasoning
     before resolving it.
   - Out of scope or needs a product decision: stop the loop and ask.
6. **Publish.** Run the relevant checks. Stage explicit paths, never
   `git add -A`. Commit using the repository's convention, push, and only
   then resolve the threads whose fixes are published:

   ```bash
   python3 "$REVIEW" resolve THREAD_ID [THREAD_ID ...]
   ```

   If no code changed (every finding was rebutted), skip the commit and
   push. A clean re-review still needs a new attempt.

   **Audit:** before each commit, `git diff --cached --name-only` must
   list only files you edited for this cycle's findings. Any other path
   is a violation; unstage it.
7. **Next cycle.** Use a new attempt file (`attempt-2.json`, and so on).
   A changed head invalidates the previous attempt.

Correct:

```text
cycle 2: wait -> review_ready, clean=false, 2 findings (P1, P2)
         fixed P1 in src/sync.ts, rebutted P2 with test evidence
         git add src/sync.ts test/sync.test.ts; commit; push
         resolve PRRT_kw...a PRRT_kw...b
         start --output .../attempt-3.json
```

Wrong:

```text
cycle 2: wait -> timed out
         gh pr comment N --body "@codex review"   # manual re-trigger
         reads the 👍 reaction from cycle 1 and reports "clean"
```

## Stop conditions

Stop and report when any of these hold:

- Success: a clean, fresh review of the current head, zero unresolved
  Codex threads, and checks passing.
- The iteration cap is reached. Never raise it on your own.
- `wait` errors: timeout, failed review, usage limit, or a moved head.
- A finding requires a scope or product decision.
- Codex keeps raising the same rebutted finding for two cycles. Report
  it as a disagreement rather than changing correct code to please the
  bot.

Never resolve threads from other reviewers. Never merge unless asked.

**Audit:** at the end of the run, check these three counts.

- The number of `attempt-*.json` files in `RUN_DIR` must not exceed
  the cap.
- Count the `@codex review` comments you authored since `RUN_START`.
  `--slurp` combines all pages, so `jq` prints one total:

  ```bash
  gh api --paginate --slurp "repos/OWNER/REPO/issues/N/comments?per_page=100" \
    | jq --arg me "$(gh api user --jq .login)" --arg since "RUN_START" \
      '[add[] | select(.user.login == $me and .created_at >= $since
          and (.body | startswith("@codex review")))] | length'
  ```

  The total must equal the number of attempt files in `RUN_DIR` with
  `"mode": "posted"`. A higher count means a manual re-trigger.
- Every thread passed to `resolve` must be one that `threads` returned,
  which guarantees it is a Codex thread.

## Report

Always end with this block:

```text
codexloop complete.            (or: codexloop stopped: REASON)
  PR:          https://github.com/OWNER/REPO/pull/N
  Head:        abc1234 (reviewed)
  Cycles:      2 of 5
  Final:       clean via comment   (clean / findings / timeout / error)
  Fixed:       3 findings (2 P1, 1 P2)
  Rebutted:    1 finding (P2, reason given on thread)
  Remaining:   0
  Checks:      pnpm test, pnpm lint
```

When anything remains, list each item as `path:line [P1] title`, with the
suggested next step.
