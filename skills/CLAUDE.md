# CLAUDE.md (`skills/`)

Skill-authoring conventions for `xornivore/skills`. Loaded automatically
when Claude Code is operating under `skills/`. Defers to the top-level
`CLAUDE.md` for everything else (commits, hooks, lint, AI attribution,
worktree policy).

This file encodes the [agentskills.io specification](https://agentskills.io/specification)
plus a small set of repo-specific conventions. The spec is the open
standard the skill format follows; the repo conventions are how this
particular repository chooses to apply it.

## 1. Folder layout (canonical)

Each skill is a top-level folder under `skills/`:

```text
skills/<skill-name>/
├── SKILL.md          # required
├── README.md         # encouraged (per-skill, links into SKILL.md and references/)
├── references/       # optional — deep documentation, loaded on demand
├── assets/           # optional — templates, images, data files
├── scripts/          # optional — executable helpers
└── ...               # additional dirs allowed but discouraged
```

- The folder name **must match** the `name` frontmatter field in
  `SKILL.md`.
- Templates, document skeletons, and data files go in `assets/`. Do
  **not** create a `templates/` folder; the spec uses `assets/` for
  this role.
- Reference files go in `references/`. Keep individual reference files
  focused — agents load them on demand, so smaller files mean smaller
  context.
- File references in `SKILL.md` must be **at most one level deep**
  (e.g., `./references/foo.md`, `./assets/bar.md`). Do not nest
  reference chains.

## 2. `SKILL.md` frontmatter (required)

```yaml
---
name: <skill-name>
description: <what + when, with trigger keywords>
license: <SPDX id or short reference, optional but recommended>
compatibility: <intended client family, optional>
metadata:                       # optional
  author: <handle>
  version: "<semver>"
allowed-tools: <space-separated, optional, experimental>
---
```

### `name`

- 1-64 characters.
- Lowercase ASCII letters, digits, and hyphens only.
- Must not start or end with a hyphen.
- Must not contain consecutive hyphens.
- **Must match the parent directory name.**

### `description`

- 1-1024 characters.
- Non-empty.
- Must describe **what** the skill does and **when** to invoke it.
- Should include trigger keywords agents can match against.
- Avoid vague descriptions ("Helps with X.") — they hurt skill
  discovery.

### `license` (recommended)

Add `license: MIT` (or whatever the repo LICENSE specifies) so the
skill can be redistributed across the agentskills.io ecosystem
without ambiguity. `xornivore/skills` is MIT-licensed.

### `compatibility` (recommended for skills with external requirements)

Use this to declare environment expectations:

```yaml
compatibility: Designed for Claude Code (or similar agentskills.io-compatible clients).
```

Or, when the skill needs specific tooling:

```yaml
compatibility: Requires git, gh, and access to GitHub API.
```

Most skills don't need this field. Skip it if there are no
environment requirements.

## 3. `SKILL.md` body

- Recommended ≤ 500 lines. Move detailed reference material into
  `references/`.
- Lead with: triggers ("when to use"), routing/decision flow, hard
  rules, then a reference index.
- Voice is imperative ("when invoked, do X"), not descriptive
  ("doxcavate does X"). The reader is the agent that's about to act.
- Cross-references to other files use relative Markdown links
  (`[name](./references/foo.md)`); the repo's
  `[no-section-sign rule](../docs/CLAUDE.md#cross-references-between-sections)`
  applies here too.

## 4. Progressive disclosure

The agentskills.io spec defines three loading stages — your skill must
be structured so each stage delivers what the agent needs without
loading the next prematurely.

| Stage | Trigger | What loads | Token budget |
| --- | --- | --- | --- |
| 1 — Metadata | Agent startup (every session) | `name` + `description` from frontmatter | ~100 tokens |
| 2 — Instructions | Agent decides the skill matches the task | Full `SKILL.md` body | < 5000 tokens recommended |
| 3 — Resources | A specific action step calls for them | Files under `references/`, `assets/`, `scripts/` | as needed |

Authoring practices that make progressive disclosure work:

- **Front-load discovery in `description`.** A vague description
  starves stage 1 — agents won't reach stage 2.
- **Keep `SKILL.md` lean and decision-focused.** Triggers, routing,
  hard rules, and a reference index. Detail goes in `references/`.
  This is what keeps stage 2 small.
- **Pull references in at the moment they're needed**, not eagerly in
  a "see also" preamble. The `SKILL.md` action checklist is the right
  place: each step references the file it needs (e.g., "Run
  discovery; see [layout-and-discovery](./references/layout-and-discovery.md)").
- **Split `references/` by topic, not by document length.** One topic
  per file means agents load only the slice they need. A 2000-line
  `everything.md` defeats stage 3.
- **`assets/` and `scripts/` are stage-3 too.** Don't inline template
  bodies in `SKILL.md`; link to `assets/<kind>-template.md` and let
  the agent read it when it's about to use it.

## 5. Install command

Every `SKILL.md` and per-skill `README.md` MUST show the install
command:

```bash
npx skills add xornivore/skills@<skill-name> --agent claude-code -y
```

This is also rule 6 in the top-level `CLAUDE.md`.

## 6. Validation

Before opening a PR for a new or modified skill:

```bash
pnpm lint                                   # markdownlint
npx skills-ref validate ./skills/<skill-name>
```

The agentskills.io reference validator is canonical. If
`npx skills-ref` doesn't resolve, fall back to installing from
<https://github.com/agentskills/agentskills/tree/main/skills-ref>.

The validator must exit 0 before the PR is mergeable. CI integration
for `skills-ref` is tracked as a follow-up; until then, validation is
a hard rule but a manual gate.

## 7. README sync

Every skill under `skills/` MUST appear in the top-level `README.md`
skills table with a one-line description and a link to its `SKILL.md`.
This is rule 4 in the top-level `CLAUDE.md` — restated here because
adding a skill always pairs with a README update.

## 8. Authoring loop

Use `skill-creator` (from `anthropics/skills`) as the primary authoring
tool. `superpowers:writing-skills` is acceptable as a secondary when
available. From a worktree:

```bash
npx skills add anthropics/skills@skill-creator --agent claude-code -y
```

Then invoke the skill-creator skill to scaffold or edit the target
skill. This is rule 1 in the top-level `CLAUDE.md`.

## 9. Quick checklist (before opening a PR)

- [ ] Folder name matches `name` frontmatter
- [ ] `name` is 1-64 lowercase-and-hyphen chars, no edge or
      consecutive hyphens
- [ ] `description` is 1-1024 chars, names *what* and *when*, includes
      triggers
- [ ] `license` and `compatibility` set (if applicable)
- [ ] `SKILL.md` body ≤ 500 lines
- [ ] File references are ≤ 1 level deep from `SKILL.md`
- [ ] No section signs (`§`) — see `docs/CLAUDE.md`
- [ ] Install command in `SKILL.md` and per-skill `README.md`
- [ ] Top-level `README.md` skills table updated
- [ ] `pnpm lint` clean
- [ ] `npx skills-ref validate ./skills/<skill-name>` exits 0
