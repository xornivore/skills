# codexloop

Loops a GitHub PR through OpenAI Codex code review until it comes back
clean. Each cycle posts `@codex review` and waits for a fresh review of
the current head. It then fixes or rebuts every finding, resolves the
Codex threads, and pushes. The loop is bounded, five cycles by default.

Adapted from Greptile's [greploop](https://github.com/greptileai/skills/tree/main/greploop)
(MIT, Copyright (c) 2026 Greptile AI). The Python helper is modelled on
Ras Mic's [greploop rewrite](https://github.com/michaelshimeles/skills/tree/main/greploop).
Changes from greploop:

- It targets Codex (`chatgpt-codex-connector[bot]`) instead of Greptile.
- GitHub only.
- Freshness comes from Codex's own markers: the review-state JSON and
  the reviewed-commit receipt.

## Install

```bash
npx skills add xornivore/skills@codexloop --agent claude-code -y
```

Needs Python 3.10+, `git`, and authenticated `gh`. The repository must
have the Codex GitHub integration enabled.

## How to use

- `codexloop #123`
- `codexloop` on a branch with an open PR
- `codexloop https://github.com/owner/repo/pull/123 --max-iterations 3`
- `codexloop --focus "for security regressions"`

See [SKILL.md](./SKILL.md) for the workflow. See
[references/helper.md](./references/helper.md) for the helper script.

## Tests

```bash
uv run --with pytest --no-project python -m pytest -q skills/codexloop/tests
```
