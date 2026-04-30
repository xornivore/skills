# Skills Repo Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap `xornivore/skills` from an empty repo to a lint-gated, hook-enforced, CI-checked Markdown skills repo, ready to host individual Claude Code skills installed via `npx skills add`.

**Architecture:** Markdown-only content under `skills/<name>/SKILL.md`, flat layout. Node + pnpm provide tooling at the repo root (markdownlint, husky, lint-staged, commitlint) and never enter skill folders. Conventional commits are enforced via a `commit-msg` hook that also rejects AI-tool attribution footers.

**Tech Stack:** pnpm, `markdownlint-cli2`, `husky` (v9+), `lint-staged`, `@commitlint/cli` + `@commitlint/config-conventional`, GitHub Actions.

**Reference spec:** `docs/superpowers/specs/2026-04-29-skills-repo-scaffold-design.md`.

**Branching:** All work for this plan lands on a feature branch `scaffold` inside `./.worktrees/scaffold/`. Main is protected; merge via PR.

---

## File Structure

Files created by this plan (all paths relative to repo root):

| Path | Responsibility |
|---|---|
| `.gitignore` | Exclude pnpm, editor, OS, and `.worktrees/` artifacts |
| `package.json` | devDeps, scripts, `lint-staged` config, packageManager pin |
| `pnpm-lock.yaml` | pnpm lockfile (generated) |
| `.markdownlint-cli2.jsonc` | markdownlint rules |
| `commitlint.config.cjs` | conventional-commits config |
| `.husky/pre-commit` | runs `lint-staged` |
| `.husky/commit-msg` | runs `commitlint` + AI-attribution guard |
| `.github/workflows/lint.yml` | CI: install + lint + commitlint range check |
| `LICENSE` | MIT, Ivan Ilichev, 2026 |
| `README.md` | thin: intent, install, skills table, authoring pointer |
| `CLAUDE.md` | the 7 repo-specific rules for Claude |
| `docs/authoring.md` | canonical authoring loop |
| `skills/.gitkeep` | tracks the otherwise-empty `skills/` directory |

---

## Task 1: Create scaffold worktree and branch

**Files:**
- Create: `./.worktrees/scaffold/` (linked worktree pointing at branch `scaffold`)

- [ ] **Step 1: Verify clean working tree on `main`**

Run: `git status`
Expected: `On branch main` and `nothing to commit, working tree clean`. The only commit so far is the spec commit (`docs: add skills repo scaffold spec`).

- [ ] **Step 2: Create the worktree**

Run from repo root:

```bash
mkdir -p .worktrees
git worktree add -b scaffold .worktrees/scaffold main
```

Expected: `Preparing worktree (new branch 'scaffold')` and `HEAD is now at <sha> docs: add skills repo scaffold spec`.

- [ ] **Step 3: cd into the worktree for the rest of the plan**

Run: `cd .worktrees/scaffold`
All subsequent commands in this plan run from inside `.worktrees/scaffold/` unless otherwise noted.

- [ ] **Step 4: Verify the branch**

Run: `git branch --show-current`
Expected: `scaffold`

---

## Task 2: Initialize pnpm with packageManager pin

**Files:**
- Create: `package.json`

- [ ] **Step 1: Detect installed pnpm version**

Run: `pnpm --version`
Record the output (e.g. `9.12.3`). If pnpm is not installed, install it via Corepack: `corepack enable && corepack prepare pnpm@latest --activate`, then re-run.

- [ ] **Step 2: Write `package.json`**

Replace `<PNPM_VERSION>` with the version from Step 1.

```json
{
  "name": "xornivore-skills",
  "version": "0.0.0",
  "private": true,
  "description": "Personal Claude Code skills by Ivan Ilichev",
  "license": "MIT",
  "packageManager": "pnpm@<PNPM_VERSION>",
  "scripts": {
    "lint": "markdownlint-cli2 \"**/*.md\" \"#node_modules\" \"#.worktrees\"",
    "lint:fix": "markdownlint-cli2 --fix \"**/*.md\" \"#node_modules\" \"#.worktrees\"",
    "prepare": "husky"
  },
  "devDependencies": {},
  "lint-staged": {
    "*.md": "markdownlint-cli2 --fix"
  }
}
```

- [ ] **Step 3: Verify**

Run: `cat package.json | head -5`
Expected: contains `"name": "xornivore-skills"`.

- [ ] **Step 4: Commit**

```bash
git add package.json
git commit -m "chore: initialize pnpm package.json"
```

Note: the `commit-msg` hook is not yet installed, so this commit is not validated. Subsequent commits after Task 7 will be.

---

## Task 3: Write `.gitignore`

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Write the file**

```gitignore
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

- [ ] **Step 2: Verify**

Run: `git check-ignore -v node_modules/x .worktrees/x .DS_Store 2>&1`
Expected: each path is reported as ignored by `.gitignore`.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add gitignore for pnpm, editors, and worktrees"
```

---

## Task 4: Add markdownlint config and devDep

**Files:**
- Create: `.markdownlint-cli2.jsonc`
- Modify: `package.json` (devDependencies via pnpm)

- [ ] **Step 1: Install markdownlint-cli2**

Run: `pnpm add -D markdownlint-cli2`
Expected: `package.json` `devDependencies` now contains `markdownlint-cli2`; `pnpm-lock.yaml` is created; `node_modules/` populated.

- [ ] **Step 2: Write `.markdownlint-cli2.jsonc`**

```jsonc
{
  "config": {
    "default": true,
    "MD013": false,
    "MD033": false,
    "MD041": false,
    "MD024": { "siblings_only": true }
  },
  "globs": ["**/*.md"],
  "ignores": ["node_modules", ".worktrees"]
}
```

Rationale (do not include in the file): MD013 disables line-length (Markdown isn't code); MD033 allows inline HTML in READMEs; MD041 allows non-H1 first lines (e.g. badges); MD024 allows duplicate headings under different parents (`## Examples` repeated under different sections).

- [ ] **Step 3: Run lint to verify it passes against the existing spec**

Run: `pnpm lint`
Expected: exit code 0; no findings against `docs/superpowers/specs/2026-04-29-skills-repo-scaffold-design.md` or this plan.

If findings appear, fix them in the corresponding files before continuing — do not loosen the config further.

- [ ] **Step 4: Commit**

```bash
git add package.json pnpm-lock.yaml .markdownlint-cli2.jsonc
git commit -m "chore: add markdownlint-cli2 config and lint scripts"
```

---

## Task 5: Install husky and add `pre-commit` hook

**Files:**
- Create: `.husky/pre-commit`
- Modify: `package.json` (devDependencies via pnpm)

- [ ] **Step 1: Install husky and lint-staged**

Run: `pnpm add -D husky lint-staged`

- [ ] **Step 2: Initialize husky**

Run: `pnpm exec husky init`
Expected: creates `.husky/pre-commit` containing `npm test` (default) and adds the `prepare` script if missing. Husky 9+ uses plain shell — no shebang or `source husky.sh` line is needed.

- [ ] **Step 3: Replace the default `pre-commit` content**

Overwrite `.husky/pre-commit` with:

```sh
pnpm exec lint-staged
```

- [ ] **Step 4: Make sure the hook is executable**

Run: `chmod +x .husky/pre-commit`

- [ ] **Step 5: Verify the hook fires by staging a deliberately broken Markdown file**

```bash
printf '# Bad heading\n#duplicate\n' > /tmp/bad.md
cp /tmp/bad.md skills/.scratch.md
git add skills/.scratch.md
git commit -m "chore: test pre-commit hook" || echo "EXPECTED: commit blocked"
```

Expected: the commit is blocked because `markdownlint-cli2` finds violations in `skills/.scratch.md`. (`lint-staged` may auto-fix some of them; for any that remain, the commit fails.)

- [ ] **Step 6: Clean up**

```bash
git restore --staged skills/.scratch.md
rm -f skills/.scratch.md
```

- [ ] **Step 7: Commit the hook setup**

```bash
git add package.json pnpm-lock.yaml .husky/pre-commit
git commit -m "chore: add husky pre-commit hook running lint-staged"
```

---

## Task 6: Add commitlint config and devDep

**Files:**
- Create: `commitlint.config.cjs`
- Modify: `package.json` (devDependencies via pnpm)

- [ ] **Step 1: Install commitlint**

Run: `pnpm add -D @commitlint/cli @commitlint/config-conventional`

- [ ] **Step 2: Write `commitlint.config.cjs`**

```js
module.exports = {
  extends: ['@commitlint/config-conventional'],
};
```

- [ ] **Step 3: Verify a good message passes**

Run: `echo "feat(scaffold): example" | pnpm exec commitlint`
Expected: exit code 0, no output.

- [ ] **Step 4: Verify a bad message fails**

Run: `echo "wip stuff" | pnpm exec commitlint || echo "EXPECTED: commitlint rejected the message"`
Expected: non-zero exit and `subject may not be empty` / `type may not be empty` errors.

- [ ] **Step 5: Commit**

```bash
git add package.json pnpm-lock.yaml commitlint.config.cjs
git commit -m "chore: add commitlint with conventional config"
```

---

## Task 7: Add `commit-msg` hook with commitlint + AI-attribution guard

**Files:**
- Create: `.husky/commit-msg`

- [ ] **Step 1: Write the hook**

Overwrite `.husky/commit-msg` with:

```sh
msg_file="$1"

# 1. Conventional-commits format (commitlint).
pnpm exec commitlint --edit "$msg_file" || exit 1

# 2. Reject AI-tool attribution unless explicitly authored by the user.
#    Patterns intentionally case-insensitive. Add new tools as needed.
if grep -E -i '^Co-Authored-By:[[:space:]]*(Claude|Codex|Copilot|GPT|ChatGPT|Anthropic)' "$msg_file" >/dev/null; then
  echo "ERROR: AI-tool Co-Authored-By trailers are not permitted." >&2
  echo "       Remove the trailer or, if intentional, bypass via 'git commit --no-verify' (discouraged)." >&2
  exit 1
fi

if grep -E -i '(generated with[[:space:]]*\[?claude code\]?|made with[[:space:]]*claude|authored with[[:space:]]*codex|copilot[- ]assisted)' "$msg_file" >/dev/null; then
  echo "ERROR: AI-tool attribution footers are not permitted." >&2
  echo "       Remove the footer or, if intentional, bypass via 'git commit --no-verify' (discouraged)." >&2
  exit 1
fi
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x .husky/commit-msg`

- [ ] **Step 3: Verify the conventional-commits gate**

```bash
git commit --allow-empty -m "wip stuff" || echo "EXPECTED: blocked"
```

Expected: blocked by commitlint with `type may not be empty` / `subject may not be empty`.

- [ ] **Step 4: Verify the AI-attribution gate (Co-Authored-By)**

```bash
git commit --allow-empty -m "$(cat <<'EOF'
chore: test attribution guard

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" || echo "EXPECTED: blocked"
```

Expected: blocked with `ERROR: AI-tool Co-Authored-By trailers are not permitted.`

- [ ] **Step 5: Verify the AI-attribution gate (footer)**

```bash
git commit --allow-empty -m "$(cat <<'EOF'
chore: test attribution guard

Generated with [Claude Code]
EOF
)" || echo "EXPECTED: blocked"
```

Expected: blocked with `ERROR: AI-tool attribution footers are not permitted.`

- [ ] **Step 6: Verify a clean conventional commit passes**

```bash
git commit --allow-empty -m "chore: verify commit-msg hook"
```

Expected: succeeds.

- [ ] **Step 7: Drop the verification commit so it does not pollute history**

Run: `git reset --hard HEAD~1`
Expected: removes the empty `chore: verify commit-msg hook` commit only. Confirm with `git log --oneline -3` that the previous Task-6 commit is at the tip.

- [ ] **Step 8: Commit the hook**

```bash
git add .husky/commit-msg
git commit -m "chore: add commit-msg hook with commitlint and AI-attribution guard"
```

---

## Task 8: Add `LICENSE`

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Write the MIT license**

```text
MIT License

Copyright (c) 2026 Ivan Ilichev

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Commit**

```bash
git add LICENSE
git commit -m "chore: add MIT license"
```

---

## Task 9: Add `README.md`

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write the README**

```markdown
# xornivore/skills

Personal [Claude Code](https://claude.com/claude-code) skills by Ivan Ilichev.
Public for sharing; curated for self-use.

## Installing skills

```bash
# Install a specific skill (Claude Code only, no .agents/.continue clutter)
npx skills add xornivore/skills@<skill-name> --agent claude-code -y

# List available skills in this repo (omit @name)
npx skills add xornivore/skills --agent claude-code -y
```

The `@<skill-name>` must match the skill's registered name, not article shorthand.

## Skills

| Name | Description |
|---|---|
| _none yet_ | _Skills will be listed here as they are added._ |

## Authoring

Skills here are authored with [`anthropics/skills@skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator):

```bash
npx skills add anthropics/skills@skill-creator --agent claude-code -y
```

See `docs/authoring.md` for the canonical loop.

Commits and pull requests in this repo do **not** include AI-tool attribution
(no `Co-Authored-By: Claude`, no `Generated with [Claude Code]` footers) unless
explicitly requested. The `commit-msg` hook enforces this.

## License

MIT — see `LICENSE`.
```

- [ ] **Step 2: Run lint**

Run: `pnpm lint`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add thin README with intent, install, and authoring pointer"
```

---

## Task 10: Add `CLAUDE.md`

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write the file**

```markdown
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
```

- [ ] **Step 2: Run lint**

Run: `pnpm lint`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md with the seven repo rules"
```

---

## Task 11: Add `docs/authoring.md`

**Files:**
- Create: `docs/authoring.md`

- [ ] **Step 1: Write the file**

```markdown
# Authoring a skill

The canonical loop. Run from the repo root.

1. Ensure `skill-creator` is installed:

   ```bash
   npx skills add anthropics/skills@skill-creator --agent claude-code -y
   ```

2. Create a worktree for the new skill:

   ```bash
   git worktree add -b skill/<skill-name> .worktrees/<skill-name> main
   cd .worktrees/<skill-name>
   ```

3. Invoke `skill-creator` to scaffold or edit `skills/<skill-name>/SKILL.md`.

4. Update the skills table in the top-level `README.md`.

5. Run `pnpm lint` (the `pre-commit` hook auto-fixes most issues).

6. Commit with conventional-commits format and **no** AI-tool attribution:

   ```bash
   git commit -m "feat(<skill-name>): describe the skill"
   ```

7. Push and open a PR into `main`. CI runs `pnpm lint` and `commitlint` over
   the PR's commit range.
```

- [ ] **Step 2: Run lint**

Run: `pnpm lint`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add docs/authoring.md
git commit -m "docs: add canonical authoring loop"
```

---

## Task 12: Track empty `skills/` directory

**Files:**
- Create: `skills/.gitkeep`

- [ ] **Step 1: Create the placeholder**

Run: `mkdir -p skills && touch skills/.gitkeep`

- [ ] **Step 2: Commit**

```bash
git add skills/.gitkeep
git commit -m "chore: track empty skills/ directory"
```

---

## Task 13: Add CI workflow

**Files:**
- Create: `.github/workflows/lint.yml`

- [ ] **Step 1: Create the workflow directory**

Run: `mkdir -p .github/workflows`

- [ ] **Step 2: Write the workflow**

```yaml
name: lint

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - name: Install
        run: pnpm install --frozen-lockfile

      - name: Markdown lint
        run: pnpm lint

      - name: Commitlint (PR commit range)
        if: github.event_name == 'pull_request'
        run: |
          pnpm exec commitlint \
            --from "${{ github.event.pull_request.base.sha }}" \
            --to   "${{ github.event.pull_request.head.sha }}" \
            --verbose
```

Note: commitlint runs only on `pull_request` because `push` to `main` may carry merged PR commits whose individual messages were already validated upstream, and there is no useful "from/to" range on a fast-forward push of multiple commits.

- [ ] **Step 3: Run lint locally**

Run: `pnpm lint`
Expected: exit 0 (the workflow file is YAML, not Markdown — markdownlint ignores it).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/lint.yml
git commit -m "ci: add markdownlint and commitlint workflow"
```

---

## Task 14: Acceptance verification, push, and PR

**Files:** none (verification only).

- [ ] **Step 1: Fresh-install sanity check**

Run from `.worktrees/scaffold/`:

```bash
rm -rf node_modules
pnpm install --frozen-lockfile
```

Expected: succeeds without warnings about a missing lockfile.

- [ ] **Step 2: Lint clean**

Run: `pnpm lint`
Expected: exit 0.

- [ ] **Step 3: Bad-Markdown commit is blocked**

```bash
printf '# Bad\n#nospace\n' > /tmp/bad.md
cp /tmp/bad.md skills/.scratch.md
git add skills/.scratch.md
git commit -m "chore: should be blocked" || echo "EXPECTED: blocked"
git restore --staged skills/.scratch.md
rm -f skills/.scratch.md
```

Expected: commit blocked by `lint-staged` / `markdownlint-cli2`.

- [ ] **Step 4: Bad-commit-message is blocked**

```bash
git commit --allow-empty -m "wip" || echo "EXPECTED: blocked"
```

Expected: blocked by commitlint.

- [ ] **Step 5: AI-attribution commit is blocked**

```bash
git commit --allow-empty -m "$(cat <<'EOF'
chore: attribution guard test

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" || echo "EXPECTED: blocked"
```

Expected: blocked by the `commit-msg` hook with `ERROR: AI-tool Co-Authored-By trailers are not permitted.`

- [ ] **Step 6: Push the branch**

Run from `.worktrees/scaffold/`:

```bash
git push -u origin scaffold
```

Expected: branch pushed; on protected `main`, this push is allowed because the target is `scaffold`, not `main`.

- [ ] **Step 7: Open the PR**

Run:

```bash
gh pr create \
  --base main \
  --head scaffold \
  --title "scaffold: bootstrap repo with markdownlint, hooks, commitlint, and CI" \
  --body "$(cat <<'EOF'
## Summary

Bootstraps `xornivore/skills` from an empty repo to a Markdown-only Claude Code skills repo with:

- pnpm + `markdownlint-cli2` for `*.md` lint
- husky `pre-commit` (lint-staged) and `commit-msg` (commitlint + AI-attribution guard)
- GitHub Actions `lint.yml` (markdownlint + commitlint over PR range)
- `CLAUDE.md` codifying skill authoring, worktrees, lint gate, README sync, conventional commits, install docs, and the no-AI-attribution rule
- `docs/authoring.md` canonical loop
- MIT `LICENSE`, thin `README.md`, empty `skills/` placeholder

Spec: `docs/superpowers/specs/2026-04-29-skills-repo-scaffold-design.md`.
Plan: `docs/superpowers/plans/2026-04-29-skills-repo-scaffold.md`.

## Test plan

- [x] `pnpm install --frozen-lockfile` succeeds
- [x] `pnpm lint` is clean
- [x] Bad-Markdown commit is blocked by `pre-commit`
- [x] Non-conventional commit message is blocked by `commit-msg`
- [x] `Co-Authored-By: Claude` and `Generated with [Claude Code]` are blocked by `commit-msg`
- [ ] CI `lint.yml` passes on this PR
EOF
)"
```

Expected: PR URL is printed.

- [ ] **Step 8: Wait for CI to go green**

Run: `gh pr checks --watch`
Expected: all checks succeed. If `lint` fails, fix the offending file, commit (`fix: address markdownlint finding`), and re-push.

- [ ] **Step 9: Merge**

After CI is green and the user has reviewed:

```bash
gh pr merge --squash --delete-branch
```

(Confirm with the user before merging — this is a protected-branch operation.)

- [ ] **Step 10: Clean up the worktree**

From repo root (not the worktree):

```bash
cd /Users/ivan.ilichev/git/xornivore/skills
git worktree remove .worktrees/scaffold
git fetch --prune
```

Expected: the worktree is removed and the local `scaffold` branch reference is cleaned up.

---

## Self-review notes

- **Spec coverage:** All sections of `2026-04-29-skills-repo-scaffold-design.md` are mapped to a task. Layout (Tasks 2–13), tooling devDeps (Tasks 4–6), hooks (Tasks 5, 7), CI (Task 13), gitignore (Task 3), CLAUDE.md (Task 10), README (Task 9), `docs/authoring.md` (Task 11), LICENSE (Task 8), `skills/` placeholder (Task 12). Open question on rule-7 enforcement is resolved as **B** (commit-msg regex guard, Task 7).
- **Acceptance criteria:** Steps in Task 14 mirror each acceptance criterion in the spec.
- **Type/identifier consistency:** Hook names (`pre-commit`, `commit-msg`), config files (`.markdownlint-cli2.jsonc`, `commitlint.config.cjs`), and script names (`lint`, `lint:fix`, `prepare`) are consistent across tasks.
- **No placeholders:** Every config file, hook script, README, CLAUDE.md, license, and workflow is provided in full. The only intentional placeholder is `<PNPM_VERSION>` in Task 2 Step 2, which the executor fills from Task 2 Step 1.
