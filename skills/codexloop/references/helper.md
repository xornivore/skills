# codex_review.py helper

`scripts/codex_review.py` wraps every GitHub call the loop needs. Run it
from the target repository with authenticated `gh`. Every subcommand
prints JSON on stdout. Errors print `{"status": "error", "message": …}`
on stderr and exit 1.

## Subcommands

| Command | Side effects | Purpose |
| --- | --- | --- |
| `start --repo O/R --pr N --output FILE [--focus TEXT] [--force]` | Posts one PR comment (unless adopting) | Snapshot state, post `@codex review`, record the attempt |
| `wait FILE [--timeout 900] [--interval 15]` | Read-only | Poll until a fresh result for the recorded head |
| `threads --repo O/R --pr N` | Read-only | Unresolved Codex review threads, all pages, full discussions |
| `resolve ID [ID ...]` | Resolves threads | Batched `resolveReviewThread` mutation |

## start

- Reserves `FILE` atomically before anything else. A rerun with the same
  path fails with `FileExistsError` and cannot double-post.
- Snapshots issue comments, PR reviews and PR reactions. `wait` ignores
  anything already in the snapshot unless its body changed.
- If the latest Codex summary says a review is `running`:
  - For the current head, `start` **adopts** it. The attempt file is
    written with `mode: adopted` and no comment is posted.
  - For an older commit, `start` refuses. Wait for that review to
    finish, then rerun `start`. After `--stuck-after` seconds (default
    1800) a running review counts as stuck and no longer blocks.
    `--force` posts regardless.
- Re-reads the head just before posting. If the head moved, `start`
  releases the reservation and errors.
- Before posting, `start` writes the attempt with `status: posting` and
  the exact trigger body. If the POST outcome is lost (a `gh` timeout,
  for example), `start` errors with "trigger outcome unknown". Run
  `wait` on that same file. Never post again by hand.

## Attempt states

| `status` | Meaning | What `wait` does |
| --- | --- | --- |
| `preparing` | `start` stopped before posting | Errors: remove the file, rerun `start` |
| `posting` | POST sent, outcome unknown | Finds the trigger comment that is not in the snapshot and has the same body, saves it, then waits. Errors if none landed |
| `triggered` | Trigger confirmed (`posted`) or review adopted (`adopted`) | Waits for the result |

## wait

Each poll re-reads the head before and after fetching. A moved head is
an error: start a new attempt for the new revision.

A result counts only when it is new since the trigger, came from a
trusted bot login, and is tied to the recorded head. "New" means the
snapshot did not contain it, or its body changed, and its timestamp is
at or after the trigger. Equal timestamps count because GitHub records
whole seconds. Precedence:

1. **PR review** by the bot with `commit_id` equal to the head. Result
   `clean: false`, with inline `findings` attached (severity, title,
   path, line, url).
2. **Receipt comment** containing "Didn't find any major issues", whose
   `**Reviewed commit:**` prefix matches the head. Result `clean: true`.
3. **Summary state marker** with `code_review.commit_sha` equal to the
   head:
   - `completed` with `has_any_findings: false` is `clean: true`.
   - `completed` with findings keeps waiting for the review to post.
   - `running` keeps waiting.
   - `failed` stops.
4. **New 👍 reaction** on the PR by the bot. Result `clean: true` with
   `source: reaction`. The reaction names no commit, so it counts only
   when no other review can still finish. It is ignored while any Codex
   summary shows a run for another commit, and for attempts whose
   `start` posted past a running review (`bypassed_running`). Mention a
   reaction-sourced result in the report.

An adopted attempt snapshots after its review began, so a finished
review or receipt can already be in the snapshot. For adopted attempts,
an unchanged snapshot item still counts if its timestamp is strictly
after the adopted start. An unchanged summary never counts.

A usage-limit comment from the bot stops the attempt immediately.
The default timeout is 15 minutes. Observed reviews take 2.5 to 7.5
minutes.

The payload formats behind these rules are in `codex-signals.md`,
linked from the `wait` step of `SKILL.md`.

## threads

GraphQL `reviewThreads` paginated to the end. A thread is kept when it is
unresolved and its first comment's author is Codex. GraphQL reports the
login without the `[bot]` suffix; the helper normalizes that. Each entry
has `id`, `outdated`, `severity`, `title`, `path`, `line` (falling back to
the original line for outdated threads), `url`, and
`discussion` (every comment, all pages: author and body). Read the discussion
before deciding a thread is addressed.

## Trusted logins

The default trusted login is `chatgpt-codex-connector[bot]`. For a
different installation, pass repeatable `--bot EXACT_LOGIN` to `start`
and `threads`. The attempt file records the list, so `wait` uses it too.

## Tests

```bash
uv run --with pytest --no-project python -m pytest -q skills/codexloop/tests
```
