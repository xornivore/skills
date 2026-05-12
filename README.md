# xornivore/skills

[Claude Code](https://claude.com/claude-code) skills; public for sharing; curated for self-use.

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
| --- | --- |
| [doxcavate](./skills/doxcavate/SKILL.md) | Produces durable, structured documentation in codebases with sparse docs. Two modes (`survey`, `draft`); review-gated by factcheck and persona passes. |
| [observablip](./skills/observablip/SKILL.md) | Audits a codebase for missing telemetry, poor o11y practices, and code structure that resists instrumentation. Read-only ranked finding list, FP-reviewed and bounded. |
| 👀 [googly-eyes](./skills/googly-eyes/SKILL.md) | Reviews PRs and local diffs against Google's eng-practices code review guide (all 10 principles). Rich local diff rendering, principle-tagged ranked findings, opt-in posting via `gh`. |

## Authoring

Skills here are authored with [`anthropics/skills@skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator):

```bash
npx skills add anthropics/skills@skill-creator --agent claude-code -y
```

See [`docs/authoring.md`](./docs/authoring.md) for the canonical loop.

Commits and pull requests in this repo do **not** include AI-tool attribution
(no `Co-Authored-By: Claude`, no `Generated with [Claude Code]` footers) unless
explicitly requested. The `commit-msg` hook enforces this.

## License

MIT — see [`LICENSE`](./LICENSE).
