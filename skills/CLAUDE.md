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
- The entry-point file is named exactly `SKILL.md` — uppercase basename,
  lowercase extension. Variants like `skill.md`, `Skill.md`, or
  `SKILL.MD` will not be recognized by the skills CLI or by clients
  loading via the agentskills.io contract.
- Templates, document skeletons, and data files go in `assets/`. Do
  **not** create a `templates/` folder; the spec uses `assets/` for
  this role.
- Reference files go in `references/`. Keep individual reference files
  focused — agents load them on demand, so smaller files mean smaller
  context.
- File references in `SKILL.md` must be **at most one level deep**
  (e.g., `./references/foo.md`, `./assets/bar.md`). Do not nest
  reference chains.
- A per-skill `README.md` is for humans browsing the GitHub repo —
  agents do not load it. Keep it brief and link out to `SKILL.md`.
  (Some external authoring guides discourage it as wasted bytes; the
  human audience reading the repo is worth the cost here.)

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

The description is the load gate. Stage 1 of progressive disclosure
shows only `name` + `description` to every agent at startup, so this
field decides whether the skill is ever activated for a given task.
Vague descriptions starve discovery; jargon-heavy descriptions miss
real user phrasing.

Rules:

- 1-1024 characters; non-empty.
- Follow this shape: **what the skill does**, then **when to invoke
  it**, then **trigger phrases users would actually type or say**.
- Use the user's vocabulary, not internal API or class names. If a
  user says "fix this bug" but the description talks about
  `BugRepairAgentBuilder`, the skill won't trigger when it should.
- Front-load the most important phrasing. Some clients (Claude Code,
  for example) cap the visible portion of the description at ~1,500
  characters once many skills are installed; anything past that may
  be truncated in the listing.
- Avoid hedge wording ("Helps with X.", "Useful for Y.") — name what
  it does and when, directly.

Strong:

```yaml
description: Reviews Go code for repository-specific style, library, and testing conventions. Use when reviewing Go pull requests, fixing review comments, or when the user mentions "Go review", "go vet", or "go fmt".
```

Weak:

```yaml
description: Helps with Go code.                              # vague
description: Validates Go AST against StyleProfile rules.     # internal jargon, no user triggers
description: Implements GoLintingAgentBuilder.                # talks about implementation, not use
```

### Frontmatter safety: no angle brackets

Frontmatter values are pulled into the agent's stage-1 startup context
verbatim. Text wrapped in `<…>` can be interpreted as tag syntax by
the host and is a known prompt-injection vector. Treat `<` and `>` as
forbidden characters in every frontmatter field — write the value out
in plain language, even when describing a placeholder.

Wrong:

```yaml
description: Reviews PRs touching <auth> and <billing> code paths.
```

Correct:

```yaml
description: Reviews PRs touching auth and billing code paths.
```

**Audit:** grep the YAML block at the top of `SKILL.md` for the regex
`[<>]`. Any hit is a violation.

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
- Cross-references to other files use relative Markdown links
  (`[name](./references/foo.md)`); the repo's
  `[no-section-sign rule](../docs/CLAUDE.md#cross-references-between-sections)`
  applies here too.

### 3.1 Voice: directives, not implications

Skill bodies are read by an agent that's about to act, not by a
human reader. Models follow direct commands more reliably than they
infer intent from hedged prose.

- Write in the imperative mood: "Always X.", "Never Y.",
  "When invoked, route to mode Z.".
- Strip hedge tokens. The common offenders in skill bodies are
  "may", "might", "could", "ideally", "we suggest", "perhaps".
  These are fine in human prose; in skill bodies they water down
  the directive and cost reliable triggering.
- "should" deserves its own line. To a human reader it carries the
  weight of "you really ought to do this." To a model it reads as
  a soft hint that can be safely ignored. When a rule is
  non-negotiable, write "must" or "always" — never "should".
- Frame the reader as the actor: "When invoked, do X" beats
  "Doxcavate does X". The skill body addresses the agent that's
  about to act.

This rule is scoped to skill bodies. Prose docs under `docs/` follow
[`docs/CLAUDE.md`](../docs/CLAUDE.md), which is tuned for human
readers and uses different voice rules.

### 3.2 Examples per rule

Every standalone rule in a skill body should be paired with a
**correct** example and a **wrong** example showing what the rule
prevents. Concrete examples teach faster than abstract prose, and
they let an agent (or human reviewer) match real cases against the
rule by shape.

If a rule is small enough that examples would add no signal (a
one-line obvious constraint), it's fine to skip them — the
exception, not the default.

### 3.3 Audit cues

Where a rule is mechanically checkable, include a short note
describing **how to detect violations**. This makes the rule
self-validating: a reviewer (human or future skill-review agent) can
follow the cue without re-deriving the test.

Examples:

```markdown
**Audit:** parse the YAML at the top of `SKILL.md`; if any value
matches the regex `[<>]`, the rule is violated.
```

```markdown
**Audit:** for every `skills/<dir>/SKILL.md`, parse the frontmatter
`name` and assert it is byte-identical to `<dir>` — a mismatch is the
violation.
```

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

## 9. Common anti-patterns

Quick-reference list of what tends to go wrong, grouped by surface.
Use during review.

### Frontmatter

- **Vague description.** "Helps with X." or "Useful for Y." — won't
  trigger reliably. Apply the formula in section 2 (`description`).
- **Internal-jargon description.** Talks about classes, APIs, or
  builder names, not what the user actually types. Lead with the
  user's vocabulary.
- **Name / folder mismatch.** `name: foo` in `skills/bar/SKILL.md` —
  fails the spec contract.
- **Angle brackets in frontmatter.** Any `<…>` text inside a
  frontmatter value — risks tag-syntax interpretation in the agent's
  stage-1 startup context.

### Structure

- **Wrong filename case.** `skill.md`, `Skill.md`, or `SKILL.MD`.
  The skills CLI only recognizes `SKILL.md` (basename uppercase,
  extension lowercase).
- **`templates/` folder.** The spec slot for templates is `assets/`.
  Use `assets/<kind>-template.md`.

### Body voice and content

- **Hedged body voice.** Skill body reads in the conditional mood
  ("we may want to", "ideally", "could") instead of giving the
  agent direct orders. Rewrite as imperatives. Watch `should` in
  particular — see section 3.1.
- **Rules without examples.** A standalone rule with no
  correct/wrong pair leaves the rule abstract. Add a concrete
  example unless the rule is one-line obvious.
- **Missing audit cues.** A mechanically-checkable rule with no
  "how to detect violations" note costs reviewer time and blocks
  automation later.

### Progressive disclosure

- **Bloated `SKILL.md`.** Body over 500 lines, or full of long
  reference material that belongs in `references/`. Defeats stage 2.
- **Eager reference loading.** SKILL.md instructs the agent to
  "read all references on activation" instead of pulling each
  reference at the step that needs it. Defeats stage 3.

## 10. Quick checklist (before opening a PR)

- [ ] Parent directory name and `name` field are byte-identical
- [ ] Entry point file is `SKILL.md` (basename uppercase, extension
      lowercase) — not `Skill.md`, `skill.md`, or `SKILL.MD`
- [ ] `name` is 1-64 chars; lowercase ASCII letters, digits, hyphens
      only; no leading, trailing, or doubled hyphens
- [ ] `description` follows the what + when + user-trigger formula,
      front-loaded, written in user vocabulary (not internal class /
      builder names)
- [ ] Frontmatter contains no `<` or `>` anywhere
- [ ] `license` and `compatibility` set when applicable
- [ ] `SKILL.md` body ≤ 500 lines and uses imperative voice
- [ ] Standalone rules in the body each carry a correct example and
      a wrong example (or are clearly one-line obvious)
- [ ] Mechanical rules carry an audit cue
- [ ] References pulled in at the action step that needs them, not
      eagerly in a "see also" preamble
- [ ] File references are ≤ 1 level deep from `SKILL.md`
- [ ] No section signs (`§`) — see `docs/CLAUDE.md`
- [ ] Install command in `SKILL.md` and per-skill `README.md`
- [ ] Top-level `README.md` skills table updated
- [ ] `pnpm lint` clean
- [ ] `npx skills-ref validate ./skills/<skill-name>` exits 0
