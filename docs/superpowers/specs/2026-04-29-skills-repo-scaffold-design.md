# Skills Repo Scaffold — Design

**Date:** 2026-04-29
**Repo:** `xornivore/skills`
**Status:** approved

## Intent

A personal collection of Claude Code skills authored by Ivan Ilichev. Public visibility is incidental — the repo is curated for self-use, not as a marketed product. Distribution channel is `npx skills add xornivore/skills@<name> --agent claude-code -y`.

Authoring is bootstrapped from third-party skills (notably `anthropics/skills@skill-creator`) rather than a homegrown skill template.

## Non-Goals

- Not a Claude Code plugin marketplace (no `.claude-plugin/`).
- Not a multi-agent distribution (Claude Code only — no `.agents`/`.continue` artifacts).
- Not a `CONTEXT.md`-style shared-vocabulary repo — skills are self-contained.
- Not bucketed (no `engineering`/`productivity`/`misc`/`personal`/`deprecated` folders). Flat layout.

## Stack

- **Content:** Markdown only.
- **Tooling:** Node + pnpm for lint, hooks, commit-message validation, and CI. Tooling stays at the repo root and never enters individual `skills/<name>/` folders.

## Layout

```
/
├─ .github/workflows/lint.yml       # CI
├─ .husky/                          # pre-commit + commit-msg hooks
├─ .markdownlint-cli2.jsonc         # markdownlint config
├─ .gitignore
├─ .worktrees/                      # gitignored — branch worktrees
├─ CLAUDE.md                        # rules for Claude in this repo
├─ LICENSE                          # MIT
├─ README.md                        # thin: intent + install + skill table
├─ commitlint.config.cjs
├─ package.json
├─ pnpm-lock.yaml
├─ docs/
│  ├─ authoring.md                  # canonical authoring loop
│  └─ superpowers/
│     ├─ specs/                     # brainstorm output (tracked)
│     └─ plans/                     # writing-plans output (tracked)
└─ skills/
   └─ <skill-name>/
      └─ SKILL.md
```

## Tooling

### Dev dependencies (pnpm)

- `markdownlint-cli2`
- `husky`
- `lint-staged`
- `@commitlint/cli`
- `@commitlint/config-conventional`

### `package.json` scripts

- `lint` — `markdownlint-cli2 "**/*.md" "#node_modules"`
- `lint:fix` — same with `--fix`
- `prepare` — `husky` (one-time hook installer)

### Hooks (`.husky/`)

- `pre-commit` → `pnpm lint-staged`
- `commit-msg` → `pnpm commitlint --edit "$1"`

### `lint-staged` config

```json
{ "*.md": ["markdownlint-cli2 --fix"] }
```

### `commitlint.config.cjs`

```js
module.exports = { extends: ['@commitlint/config-conventional'] };
```

### CI (`.github/workflows/lint.yml`)

- Triggers: `pull_request`, `push` to `main`.
- Steps: checkout, setup-pnpm + setup-node (with pnpm cache), `pnpm install --frozen-lockfile`, `pnpm lint`, run commitlint over the PR's commit range (`commitlint --from origin/main --to HEAD`).

## `.gitignore`

```
# pnpm / node
node_modules/
.pnpm-store/
*.log

# OS / editors
.DS_Store
.idea/
.vscode/

# worktrees
.worktrees/
```

## `CLAUDE.md` rules

1. **Skill authoring.** Before creating or editing any skill under `skills/`, invoke the `skill-creator` skill from `anthropics/skills`. Install if needed with
   `npx skills add anthropics/skills@skill-creator --agent claude-code -y`.
   `superpowers:writing-skills` is acceptable as a secondary when available.
2. **Worktrees.** Non-trivial changes happen on a branch inside `./.worktrees/<branch>/` via `superpowers:using-git-worktrees`.
3. **Lint gate.** `pnpm lint` must pass before committing. Do not bypass hooks (no `--no-verify`).
4. **README sync.** Every skill under `skills/` MUST be listed in the top-level `README.md` with a one-line description and a link to its `SKILL.md`.
5. **Conventional commits.** Format: `<type>(<scope>): <subject>`. Type ∈ `feat | fix | docs | chore | refactor | test | ci`. Scope is the skill folder name when the change touches a single skill; omit scope for repo-wide changes.
6. **Install docs.** Each skill's documentation MUST show the install command:
   `npx skills add xornivore/skills@<skill-name> --agent claude-code -y`
   (Claude Code only — avoids `.agents`/`.continue` clutter).
7. **No AI attribution in commits or PRs.** Commit messages, PR titles, and PR bodies MUST NOT include `Co-Authored-By: Claude …`, `🤖 Generated with [Claude Code]`, "made with Claude," or any equivalent attribution to Claude, Codex, Copilot, or other AI tools. The only exception is when the user explicitly asks for attribution on that specific commit or PR.

## `README.md`

Thin and stable. Sections:

1. **Intent** — one paragraph: "personal Claude Code skills, public for sharing, install via `npx skills`."
2. **Install** — the `npx skills add` patterns (with and without `@<skill-name>`), copied verbatim from the user's brief.
3. **Skills** — table of `name | description | link to SKILL.md`. Maintained per CLAUDE.md rule 4.
4. **Authoring** — short pointer to `docs/authoring.md` and the one-line "no AI attribution in commits unless explicitly requested" note.

## `docs/authoring.md`

The canonical authoring loop, ordered:

1. Ensure `skill-creator` is installed:
   `npx skills add anthropics/skills@skill-creator --agent claude-code -y`
2. Create a branch worktree under `./.worktrees/<branch>/` via `superpowers:using-git-worktrees`.
3. Invoke `skill-creator` to scaffold or edit the skill.
4. Update `README.md` skill table.
5. Run `pnpm lint` (auto-fixed by pre-commit hook anyway).
6. Commit using conventional-commits format, no AI attribution.

## `LICENSE`

MIT, copyright Ivan Ilichev, 2026.

## Acceptance criteria

- Empty repo bootstrapped with all files above; `pnpm install` succeeds and produces a lockfile.
- `pnpm lint` runs clean against the bootstrap content.
- `git commit` is blocked when staged Markdown fails markdownlint.
- `git commit` is blocked when the message violates conventional-commits.
- A dummy commit message containing `Co-Authored-By: Claude` is rejected by either commitlint config or a custom guard. (See open question below.)
- CI passes on a PR that introduces a trivial, lint-clean Markdown change.
- README skill table starts empty (or with a placeholder) and the install snippet is verbatim from the user's brief.

## Open question

How aggressively to enforce rule 7 (no AI attribution). Options:

- **A.** Document-only — rely on CLAUDE.md and reviewer discipline.
- **B.** Add a `commit-msg` regex guard that rejects `Co-Authored-By: (Claude|Codex|Copilot)` and the `🤖 Generated with` footer. Simple shell check; does not require commitlint.
- **C.** Both A and B, plus a CI step that scans the PR's commit range for the same patterns.

Recommendation: **B** at minimum, escalating to **C** if a slip ever ships. Decide during planning.
