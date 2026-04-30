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
| --- | --- |
| _none yet_ | _Skills will be listed here as they are added._ |

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
