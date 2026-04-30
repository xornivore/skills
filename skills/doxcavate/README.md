# doxcavate

Produces durable, structured documentation in codebases where written
docs are sparse. Two modes — `survey` (proposes a doc plan) and `draft`
(writes one specific doc end-to-end). Drafts are review-gated by a
factcheck pass and a kind-keyed persona pass.

## Install

```bash
npx skills add xornivore/skills@doxcavate --agent claude-code -y
```

## See also

- [`SKILL.md`](./SKILL.md) — entry point and routing.
- [`references/`](./references/) — deep content per topic.
- [`assets/`](./assets/) — skeletons for the six doc kinds.
- [Design spec](../../docs/superpowers/specs/2026-04-29-doxcavate-design.md).
