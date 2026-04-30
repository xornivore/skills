# CLAUDE.md (`docs/`)

Doc-authoring conventions for `xornivore/skills`. Loaded automatically
when Claude Code is operating under `docs/`. Defers to the top-level
`CLAUDE.md` for everything else (commit format, AI-attribution rules,
worktree policy, lint gate).

## Cross-references between sections

- **Avoid the section sign (`§`).** It looks scholarly, doesn't render
  cleanly for skim-readers, isn't always announced by screen readers,
  and requires an unusual keystroke. Prefer plain links.
- **Link to sections by anchor** when referencing them — clickable and
  self-naming. GitHub renders Markdown anchors from headings as
  lowercase, dot-stripped, hyphenated slugs:

  ```text
  ## 5. Investigation methodology   →  #5-investigation-methodology
  ### 3.2 Repo keying for ...       →  #32-repo-keying-for-...
  ```

  Form: `[Section name](#5-investigation-methodology)`.
- **Plain "section 5" prose is acceptable** when an inline link would
  add visual noise (e.g., inside a parenthetical that already has
  another link). Avoid raw `5` with no context.
- **Prefer named over numeric** when both work. Numbers shift as the
  doc grows; names stay stable.

## Voice

- Plain, direct, terse. The reader's time is the budget.
- Em-dashes are fine — they read naturally and we use them constantly.
- `i.e.` and `e.g.` are OK in moderation. `viz.`, `cf.`, `ibid.`,
  `q.v.`, etc. are not.
- Skip throat-clearing ("It is worth noting that…", "Importantly,…").
  If it's worth noting, just write it.

## File layout under `docs/`

- **Spec / design docs:** `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
  Excluded from `markdownlint` by design — they're working artifacts
  and lint rules tuned for shipped docs over-constrain them.
- **Reference / authoring guides** (like this file): top of `docs/`.
- **Anything else:** ask before adding new top-level subdirs under
  `docs/`; structure is light on purpose.

## Scope

- Hard rule for everything under `docs/`.
- Recommended for skill prose (`SKILL.md`, per-skill READMEs under
  `skills/`) for consistency, but not enforced there.
