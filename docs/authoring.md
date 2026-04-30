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
