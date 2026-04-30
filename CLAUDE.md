# CLAUDE.md

Repo-specific rules for Claude when working in `xornivore/skills`. These
override Claude Code defaults where they conflict.

## 1. Skill authoring

Before creating or editing anything under `skills/`, invoke the
`skill-creator` skill from `anthropics/skills`. Bootstrap install:

```bash
npx skills add anthropics/skills@skill-creator --agent claude-code -y
```

`superpowers:writing-skills` is acceptable as a secondary when available.

Skill-authoring conventions (folder layout, frontmatter rules, validation)
live in [`skills/CLAUDE.md`](./skills/CLAUDE.md). It encodes the
[agentskills.io specification](https://agentskills.io/specification) plus
repo-specific rules and is loaded automatically when working under
`skills/`.

## 2. Worktrees

Non-trivial changes happen on a feature branch inside `./.worktrees/<branch>/`
via `superpowers:using-git-worktrees`. Direct commits to `main` are reserved
for trivial repo-meta changes (and `main` is branch-protected).

## 3. Lint gate

`pnpm lint` must pass before committing. The `pre-commit` hook auto-fixes
staged Markdown via `lint-staged`. Do not bypass hooks (`--no-verify` is
forbidden) without explicit user approval on that specific commit.

## 4. README sync

Every skill under `skills/` MUST appear in the top-level `README.md` skills
table with a one-line description and a link to its `SKILL.md`. When a skill
is added, removed, or renamed, the table is updated in the same commit.

## 5. Conventional commits

Format: `<type>(<scope>): <subject>`.

- `<type>` ∈ `feat | fix | docs | chore | refactor | test | ci`
- `<scope>` is the skill folder name when the change touches a single skill;
  omit the scope for repo-wide changes.

Enforced by `commitlint` via the `commit-msg` hook.

## 6. Install docs

Each skill's `SKILL.md` (and any per-skill README) MUST show the install
command:

```bash
npx skills add xornivore/skills@<skill-name> --agent claude-code -y
```

Claude Code only — avoids `.agents` / `.continue` clutter on consumer
machines.

## 7. No AI-tool attribution in commits or PRs

Commit messages, PR titles, and PR bodies MUST NOT include:

- `Co-Authored-By: Claude <noreply@anthropic.com>` (or any AI co-author)
- `🤖 Generated with [Claude Code]` footers
- "Made with Claude," "Authored with Codex," "Copilot-assisted," etc.

Enforced by the `commit-msg` hook for commits; reviewer discipline for PR
titles/bodies. The only exception is when the user explicitly asks for the
attribution on that specific commit or PR.
