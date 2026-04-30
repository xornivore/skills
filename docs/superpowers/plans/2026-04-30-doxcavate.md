# doxcavate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `doxcavate` Claude Code skill that produces and maintains
durable, structured documentation in codebases where written docs are sparse —
readable by humans and agents alike.

**Architecture:** Skill packaged as Markdown content (no runtime code). `SKILL.md`
is the entry point: lean, with mode routing (survey vs draft), a decision flow,
and a reference index pointing to detail files. `references/` holds deep content
for each spec section. `templates/` provides skeletons for the six doc kinds.
Triggered when the user invokes the skill or asks doxcavate to inspect or
document a codebase.

**Tech Stack:** Markdown only. Validation by `pnpm lint`
(`markdownlint-cli2` already in repo). Skill installed via the `skills` CLI
(`npx skills add xornivore/skills@doxcavate --agent claude-code -y`). The skill
is content for Claude Code, not executable code.

**Spec source:** `docs/superpowers/specs/2026-04-29-doxcavate-design.md`. The
plan lifts content from numbered spec sections — when a step says "transcribe
spec section N.M," paste the exact prose, then adapt to skill-instruction voice
("when invoked, do X" rather than "doxcavate does X").

---

## Working environment

- Branch: `plan/doxcavate` (already created off `origin/main`).
- Worktree: `.worktrees/doxcavate-plan/`.
- All commands run from the worktree root unless stated.

## File structure

```text
skills/doxcavate/
├── SKILL.md
├── README.md
├── references/
│   ├── doc-kinds.md
│   ├── layout-and-discovery.md
│   ├── invocation-modes.md
│   ├── investigation-and-sources.md
│   ├── review-methodology.md
│   └── personas.md
└── templates/
    ├── how-it-works.md
    ├── learning-path.md
    ├── service-map.md
    ├── glossary.md
    ├── runbook.md
    └── index.md
```

Plus repo-level changes:

- `README.md` (top-level) — add doxcavate row to the Skills table.

---

## Phase 1 — Scaffolding

### Task 1: Bootstrap skill-creator and create folder

**Files:**

- Create: `skills/doxcavate/` (empty dirs `references/` and `templates/`)

- [ ] **Step 1: Install skill-creator (per repo CLAUDE.md rule 1)**

```bash
npx skills add anthropics/skills@skill-creator --agent claude-code -y
```

Expected: skill-creator becomes available; no error. If already installed, the
command is idempotent.

- [ ] **Step 2: Create the skill folder layout**

```bash
mkdir -p skills/doxcavate/references skills/doxcavate/templates
```

- [ ] **Step 3: Verify the layout**

```bash
ls -la skills/doxcavate/
```

Expected: shows `references/` and `templates/` subdirs.

- [ ] **Step 4: No commit yet** — Task 2 commits the first real content.

---

### Task 2: Minimal SKILL.md frontmatter + install command

**Files:**

- Create: `skills/doxcavate/SKILL.md`

- [ ] **Step 1: Write the minimal SKILL.md**

```markdown
---
name: doxcavate
description: Use when invoked in a codebase that has sparse or missing documentation, to produce durable, structured docs that humans and agents can both read fluently. Two modes — `survey` (proposes a doc plan in `docs/index.md`) and `draft` (writes one specific doc end-to-end). Triggered by phrases like "doxcavate this repo", "doxcavate the X", "what should be documented?", or any explicit request to inventory or write project documentation.
---

# doxcavate

Producing durable, structured documentation in codebases where written docs
are sparse.

## Install

```bash
npx skills add xornivore/skills@doxcavate --agent claude-code -y
```

<!-- This SKILL.md is a stub during scaffolding. Task 5 fills it in. -->
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/SKILL.md
git commit -m "feat(doxcavate): scaffold SKILL.md with frontmatter and install command"
```

Note: the `references/` and `templates/` dirs are empty so git won't track them
yet. They'll get tracked when their first file lands in Phase 3 / Phase 4.

---

### Task 3: Add doxcavate row to top-level README

**Files:**

- Modify: `README.md` (top-level)

- [ ] **Step 1: Open the top-level README and find the Skills table**

The current Skills table in `README.md` reads:

```markdown
## Skills

| Name | Description |
| --- | --- |
| _none yet_ | _Skills will be listed here as they are added._ |
```

- [ ] **Step 2: Replace the placeholder row with a doxcavate row**

```markdown
## Skills

| Name | Description |
| --- | --- |
| [doxcavate](./skills/doxcavate/SKILL.md) | Produces durable, structured documentation in codebases with sparse docs. Two modes (`survey`, `draft`); review-gated by factcheck and persona passes. |
```

- [ ] **Step 3: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: list doxcavate in top-level skills table"
```

---

## Phase 2 — References (deep content)

Each task in this phase creates one reference file under
`skills/doxcavate/references/`. Each file is a standalone, self-contained
section of the skill's deep content. Cross-references between files use
relative Markdown links (e.g., `[doc kinds](./doc-kinds.md)`).

**Voice:** these are skill-instruction documents. Prefer "when invoked, do X"
over "doxcavate does X". Section headings should be plain (no `§`,
per `docs/CLAUDE.md`).

### Task 4: `references/doc-kinds.md`

**Files:**

- Create: `skills/doxcavate/references/doc-kinds.md`

**Source spec sections:** 2 (Doc taxonomy), 7.1 (Front-matter), 7.2 (Required
structural anchors), 7.3 (Tolerance for pre-existing docs), 7.4 (Sizing).

- [ ] **Step 1: Write the file**

Top-of-file content (do not include the `<!-- truncated -->` placeholder; this
is the literal content to write):

```markdown
# Doc kinds

doxcavate writes a small, fixed vocabulary of doc kinds. File-name prefixes
are part of the contract — agents grep, route, and link by prefix without
parsing prose.

## Taxonomy

| Kind | File pattern | Multiplicity | Role |
| --- | --- | --- | --- |
| Leaf reference | `how-it-works-<topic>.md` | many | Concise description of one feature, module, or "unit". Code-anchored. |
| Learning path | `learning-path-<topic>.md` | many | Onboarding tour + task-oriented runbook + (lower-priority) conceptual narrative. Threads `how-it-works-*` leaves into a reading order with checkpoints. |
| Service map | `service-map.md` | one per repo | Catalog of in-repo services and external services this codebase talks to, with the integration call sites. |
| Glossary | `glossary.md` | one per repo | Terms, acronyms, internal jargon. |
| Runbook | `runbook-<topic>.md` | many | Operational procedures: deploy, rollback, oncall response. |
| Index | `index.md` (or `README.md` if the host convention prefers) | one per docs subdir | Auto-maintained navigation backbone — what's here, what links where. |

Architecture-overview docs are deliberately not a separate slot. Their role is
split between the conceptual layer of `learning-path-*` and the navigational
role of `index.md` files at multiple levels.

## Front-matter (required on docs doxcavate writes)

\`\`\`yaml
---
kind: how-it-works | learning-path | service-map | glossary | runbook | index
subject: <slug matching the file name suffix; omit for singletons>
related: [<other doc slugs>]
last_verified_commit: <repo HEAD sha at the moment doxcavate wrote/refreshed this doc>
last_verified_at: <ISO date of that write>
shadow: false  # set true only when the doc lives outside the host repo (see layout-and-discovery.md)
---
\`\`\`

## Required structural anchors per kind

[transcribe verbatim from spec section 7.2]

## Tolerance for pre-existing docs

The structural anchor requirement applies to docs doxcavate **creates or
rewrites**. Read pre-existing docs without complaint, even when they don't
follow the convention. Migrating an old doc to the convention is an explicit
user request, not a side effect.

## Sizing

Word-count targets keep "sizeable" honest:

- `how-it-works-*` ≤ 600 words
- `runbook-*` ≤ 800 words
- `learning-path-*` ≤ 1200 words
- `service-map.md` and `glossary.md` are reference shapes — they grow with
  the codebase, not with prose.
```

The triple-backtick YAML block above contains escaped backticks in this plan
because the plan itself is Markdown. When writing the file, use literal triple
backticks — not the escaped form.

For the "Required structural anchors per kind" section, copy the bullet list
from spec section 7.2 verbatim.

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`. Note: `skills/**/*.md` is linted (no exclusion),
so this file is subject to lint rules.

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/references/doc-kinds.md
git commit -m "feat(doxcavate): add doc-kinds reference"
```

---

### Task 5: `references/layout-and-discovery.md`

**Files:**

- Create: `skills/doxcavate/references/layout-and-discovery.md`

**Source spec sections:** 3 (Layout & path discovery), 3.1 (Storage modes),
3.2 (Repo keying for external state), 3.3 (Mode selection).

- [ ] **Step 1: Write the file**

Structure to follow:

```markdown
# Layout and path discovery

Sniff before writing anything. Resolve the active config, the docs root,
and the storage mode in this order.

## Discovery order

[transcribe spec section 3 list, 6 items]

## Storage modes

### integrated (default)

[transcribe spec section 3.1 integrated mode bullet]

### shadow

[transcribe spec section 3.1 shadow mode bullet, including config and docs-root paths and the solo-contributor-in-hostile-repo rationale]

## Repo keying for external state

[transcribe spec section 3.2]

## Mode selection

[transcribe spec section 3.3]

## Action checklist (when invoked)

When doxcavate is invoked in a new repo:

1. Walk the discovery order; resolve the config file path (or that none
   exists yet).
2. If no config exists and a write is about to happen, ask the user once:
   "integrated (commits to this repo) or shadow (user-local, off-repo)?".
   Record the answer in the appropriate config location.
3. Compute and pin the `<repo-key>` (preferring the `origin` remote URL
   slug; falling back to a 12-char SHA1 of the repo path).
4. Resolve the docs root using sniffed conventions or the hybrid default.

Never silently write outside the host repo. Never silently add meta-files
to a repo that has none.
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/references/layout-and-discovery.md
git commit -m "feat(doxcavate): add layout-and-discovery reference"
```

---

### Task 6: `references/invocation-modes.md`

**Files:**

- Create: `skills/doxcavate/references/invocation-modes.md`

**Source spec section:** 4 (Invocation modes).

- [ ] **Step 1: Write the file**

```markdown
# Invocation modes

doxcavate has two modes. Pick from the user's prompt; ask once when
ambiguous.

## survey

Produces or refreshes the repo's top-level doc index (default
`docs/index.md` — whatever the path discovery resolved) as a *doc plan*:
an ordered, prioritized list of which `how-it-works-*`, `learning-path-*`,
`runbook-*`, etc. should exist for this repo, each with a one-line
rationale and a `status: missing | drafted | verified` marker.

**No leaf docs are written in survey mode.** The output is the plan only.

## draft

Produces or updates one specific doc named or implied by the prompt.
Always reads the current top-level doc index (creating it if missing)
before drafting, so leaves link into the broader plan.

## Routing

| Prompt shape | Mode |
| --- | --- |
| Names a target ("doxcavate the ingestion pipeline" / "doxcavate `runbook-deploy`") | draft |
| Asks for inventory or onboarding ("doxcavate this repo" / "what should be documented?") | survey |
| Ambiguous | ask once |

## Action checklist

- Survey: load existing `index.md` (if any), inventory the repo, propose
  the doc plan, write it back to `index.md`, stop.
- Draft: load `index.md`, identify the target, follow the production
  sources flow ([investigation-and-sources](./investigation-and-sources.md)),
  draft the doc using the matching template
  ([doc-kinds](./doc-kinds.md)), then run review
  ([review-methodology](./review-methodology.md)) before declaring done.
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/references/invocation-modes.md
git commit -m "feat(doxcavate): add invocation-modes reference"
```

---

### Task 7: `references/investigation-and-sources.md`

**Files:**

- Create: `skills/doxcavate/references/investigation-and-sources.md`

**Source spec sections:** 5 (Investigation methodology), 6 (Production sources)
including 6.1–6.5, 9 (Related services).

- [ ] **Step 1: Write the file**

Structure:

```markdown
# Investigation and production sources

How doxcavate explores (the *how*) and what doxcavate reads (the *what*).
Each pass below feeds drafts and reviews; none is trusted on its own.

## Investigation methodology

[transcribe spec section 5 — adaptive: inline reads vs fan-out via
dispatched agents, with the superpowers-as-enhancement caveat]

## Production sources

### Code (source of truth)

[transcribe spec section 6.1]

### Existing docs (treated as hypotheses)

[transcribe spec section 6.2 — verified / contradicted / unverifiable
grading; how to handle each]

### Code commits (motivation + drift signal)

[transcribe spec section 6.3 — origin/evolution, decision harvesting,
drift indication via last_verified_commit; no git blame]

### Reconciliation order

[transcribe spec section 6.4 — existing docs → code → commits → reconcile]

### Future sources (deferred)

[transcribe spec section 6.5 — PRs/issues, tests; v1.1+]

## Related services

doxcavate documents *integration points*, not service internals. For each
external service discovered during investigation:

1. Identify the integration call sites (HTTP clients, gRPC stubs, env
   vars, hostnames in config).
2. Add a row to `service-map.md`.
3. Reference it from `## External dependencies` in any `how-it-works-*`
   doc that touches the service.

If `.doxcavate.yml` lists sibling repo paths or accessible OpenAPI / proto
URLs, doxcavate may follow them to enrich the service-map entry — but it
**never writes docs into a sibling repo from outside.**

## Action checklist (during draft mode)

1. Resolve the docs root and load the top-level `index.md`.
2. Read existing docs that overlap the target (cheap; gives a map of
   prior claims).
3. Read code (the ground truth — adaptive: inline for tight chains,
   fan-out for parallel-shaped questions).
4. Read commits scoped to the relevant code paths (for motivation,
   evolution, and drift signals).
5. Identify external services touched by the target; record them per
   the **Related services** procedure above.
6. Reconcile per the order above before drafting.
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/references/investigation-and-sources.md
git commit -m "feat(doxcavate): add investigation-and-sources reference"
```

---

### Task 8: `references/review-methodology.md`

**Files:**

- Create: `skills/doxcavate/references/review-methodology.md`

**Source spec sections:** 8.1 (Factcheck pass), 8.2 (Persona pass) including
8.2.1 (Output contract) and 8.2.2 (Quality bar), 8.3 (Loop and termination),
8.4 (Opt-in deviations), 8.5 (Dispatched agents for review), 8.6 (Escape
hatches) including 8.6.1, 8.6.2, 8.6.3.

This is the longest reference file. Transcribe each subsection in order.

- [ ] **Step 1: Write the file**

```markdown
# Review methodology

Every newly drafted doc goes through two review passes: a **factcheck
pass** that grounds the doc in code, and a **persona pass** that asks
whether the doc serves its intended reader. Facts before craft.

## Factcheck pass

[transcribe spec section 8.1 in full — claim shapes, verification
approach, outcomes (verified/contradicted/unverifiable), verification
block as byproduct, never-skippable]

## Persona pass

[transcribe spec section 8.2 intro + persona table]

### Output contract

[transcribe spec section 8.2.1 — ranked list of ≤7 items, YAML schema
with location/problem/proposed_change/optional patch, hard cap, ranking,
patches-when-possible]

### Quality bar

[transcribe spec section 8.2.2 — actionable / fix-when-possible /
no-taste-arguments / brevity-is-a-feature, plus the bad-vs-good
examples table]

## Loop and termination

[transcribe spec section 8.3 — single-round default flow, focused
factcheck on changed regions, doc-update behavior, halt cross-ref to
escape hatches]

## Opt-in deviations

[transcribe spec section 8.4 — thorough mode (run-to-fixed-point, cap 3),
skip persona, prompt hints, .doxcavate.yml config snippet]

## Dispatched agents for review

[transcribe spec section 8.5 — both passes can fan out; reviewers are
read-only; authoring agent applies findings]

## Escape hatches

### `E_TOO_MANY_CONTRADICTIONS` (factcheck overflow)

[transcribe spec section 8.6.1 — thresholds, halt YAML output,
recovery paths]

### `E_PERSONA_OVERFLOW` (persona overflow)

[transcribe spec section 8.6.2 — self-report mechanism, halt YAML
output, recovery paths]

### Why explicit halt

[transcribe spec section 8.6.3]

## Action checklist (after a draft is produced)

1. Run the factcheck pass. If thresholds tripped → emit
   `E_TOO_MANY_CONTRADICTIONS` and halt.
2. Run the persona pass for the doc's kind (see
   [personas](./personas.md)). If reviewer reports overflow → emit
   `E_PERSONA_OVERFLOW` and halt.
3. Apply all returned items, preferring `patch` over textual
   instruction.
4. Run the focused factcheck on changed regions only.
5. If thorough mode (config or prompt hint), repeat 1–4 until
   factcheck shows zero contradictions and persona returns zero items,
   or until 3 rounds elapsed.
6. Done.
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/references/review-methodology.md
git commit -m "feat(doxcavate): add review-methodology reference"
```

---

### Task 9: `references/personas.md`

**Files:**

- Create: `skills/doxcavate/references/personas.md`

**Source spec section:** 8.2 (persona table). Each persona gets a
short brief that the persona-pass dispatch prompt will quote verbatim.

- [ ] **Step 1: Write the file**

```markdown
# Review personas

Each doc kind has a single review persona. The persona pass adopts the
brief below and re-reads the draft as that reader. Briefs are concrete on
purpose — abstract personas don't catch real failure modes.

## `how-it-works-*` — skeptical seasoned engineer

You are a skeptical, seasoned engineer who has worked in this stack for
many years. You read this doc with a terminal open. You will grep every
file path, function name, and call relationship the doc claims. If the
prose says "X calls Y" and the code does not show that call, you will
say so with a line number. You don't tolerate vague hand-wave language;
"orchestrates" without specifics is a smell. You are not impressed by
length — a tight 200-word doc beats a sprawling 1000-word one.

## `learning-path-*` — newcomer at hour zero

You are a newcomer to the codebase, on day one, hour zero. You don't
share the assumptions the team takes for granted. Acronyms with no
expansion stop you cold. References to "the X system" without a link
to where X is defined send you searching. You measure the doc by the
question: could you, having read this and only this, take the next
concrete step (clone, run, find, modify)? If not, the doc is failing
you.

## `runbook-*` — operator focused on system recovery

You are an operator paged at an inconvenient hour. The system is in a
bad state. You need concise, actionable instructions that lead to
system recovery. You do not have time for context, theory, or
"why". You scan to the procedure and execute. Every step that doesn't
move you toward recovery is friction. Verification commands must come
*after* the procedure, not before — confirm the fix worked, don't gate
the fix on a precondition check.

## `service-map.md` — completeness reviewer (services)

You are reading this map to learn what the codebase talks to. You ask:
"is anything missing?". You scan the codebase looking for HTTP clients,
gRPC stubs, env vars suggesting endpoints, hostnames in config, and
match each to a row in the map. Anything found in code without a row is
a gap. Anything in the map without a code reference is suspect. You are
not interested in prose; you want the list to be complete and grounded.

## `glossary.md` — completeness reviewer (terms)

You are reading the glossary to learn the team's vocabulary. You ask:
"is anything missing?". You scan the codebase for acronyms, internal
nouns, and recurring jargon. Anything used >3 times in code without a
definition is a gap. Definitions that contradict each other across
docs are bugs. You don't write essays; one line per term is plenty.

## `index.md` — skim-reader

You arrived from a link or grep. You need to find the right doc in
under 30 seconds. You scan headings, scan the doc-plan table, and
either click through or backtrack. A wall of prose loses you. Tables,
short bullets, and clear status markers (`missing`, `drafted`,
`verified`) win.
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/references/personas.md
git commit -m "feat(doxcavate): add review personas reference"
```

---

## Phase 3 — Templates (one per doc kind)

Each template is a skeleton. Templates are copied verbatim into the
target doc location at the start of drafting; the skill fills in the
placeholders during the production-sources phase, then review enforces
the structural anchors.

Each template starts with the front-matter block and includes every
required structural anchor for its kind. Placeholders use angle brackets
(`<like-this>`).

### Task 10: `templates/how-it-works.md`

**Files:**

- Create: `skills/doxcavate/templates/how-it-works.md`

- [ ] **Step 1: Write the file**

```markdown
---
kind: how-it-works
subject: <topic-slug>
related: []
last_verified_commit: <sha>
last_verified_at: <YYYY-MM-DD>
shadow: false
---

# How it works: <Topic>

## Summary

<One to three sentences. What is this thing, what role does it play in the
codebase, and what is the single most important thing a reader should
know.>

## Entry points

- `<path/to/file.ext>:<line>` — <one-line explanation>
- `<path/to/file.ext>:<line>` — <one-line explanation>

## External dependencies

- `<service or library>` — <how this code talks to it; integration call sites>

## Verification

\`\`\`bash
<grep or shell command>
\`\`\`

\`\`\`bash
<grep or shell command>
\`\`\`

<!-- Sizing target: ≤ 600 words. Trim before declaring done. -->
```

When writing the file, use literal triple backticks around shell blocks.

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/templates/how-it-works.md
git commit -m "feat(doxcavate): add how-it-works template"
```

---

### Task 11: `templates/learning-path.md`

**Files:**

- Create: `skills/doxcavate/templates/learning-path.md`

- [ ] **Step 1: Write the file**

```markdown
---
kind: learning-path
subject: <topic-slug>
related: []
last_verified_commit: <sha>
last_verified_at: <YYYY-MM-DD>
shadow: false
---

# Learning path: <Topic>

## Audience

<Who this is for. Be specific — a "newcomer at hour zero" learning path is
shaped differently from one for a seasoned operator picking up a new area.>

## Prerequisites

- <Concrete thing the reader should already know or have running>
- <Concrete thing>

## Reading order

1. [How <X> works](<path/to/how-it-works-x.md>) — <one-line why>
2. <Code reference: `path/to/file.ext` — what to look at>
3. [How <Y> works](<path/to/how-it-works-y.md>) — <one-line why>

## Checkpoints

- After step <N>: you should be able to <verb a concrete artifact, run a
  command, or trace a flow>.
- After step <M>: you should be able to <verb a concrete artifact>.

## Background (optional)

<Conceptual narrative — origin, evolution, mental model. Lower priority
than the procedural layer; include only when it clarifies the rest.>

<!-- Sizing target: ≤ 1200 words. Trim before declaring done. -->
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/templates/learning-path.md
git commit -m "feat(doxcavate): add learning-path template"
```

---

### Task 12: `templates/service-map.md`

**Files:**

- Create: `skills/doxcavate/templates/service-map.md`

- [ ] **Step 1: Write the file**

```markdown
---
kind: service-map
related: []
last_verified_commit: <sha>
last_verified_at: <YYYY-MM-DD>
shadow: false
---

# Service map

## In-repo services

| Service | Path | Role | Entry point |
| --- | --- | --- | --- |
| `<name>` | `<path>` | <one-line role> | `<file:line>` |

## External services

| Service | Integration call site | Notes |
| --- | --- | --- |
| `<name>` | `<file:line>` | <env vars, auth, etc.> |

## Diagram (optional)

\`\`\`mermaid
<Mermaid graph here, optional>
\`\`\`
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/templates/service-map.md
git commit -m "feat(doxcavate): add service-map template"
```

---

### Task 13: `templates/glossary.md`

**Files:**

- Create: `skills/doxcavate/templates/glossary.md`

- [ ] **Step 1: Write the file**

```markdown
---
kind: glossary
related: []
last_verified_commit: <sha>
last_verified_at: <YYYY-MM-DD>
shadow: false
---

# Glossary

Alphabetized definitions. Keep entries to one or two sentences. Cross-link
to `how-it-works-*` docs when a term has a deeper page.

## A

**<Term>**
: <Definition>.

## B

**<Term>**
: <Definition>.

<!-- Continue alphabetically. Empty letter sections are fine to omit
until populated. -->
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/templates/glossary.md
git commit -m "feat(doxcavate): add glossary template"
```

---

### Task 14: `templates/runbook.md`

**Files:**

- Create: `skills/doxcavate/templates/runbook.md`

- [ ] **Step 1: Write the file**

```markdown
---
kind: runbook
subject: <topic-slug>
related: []
last_verified_commit: <sha>
last_verified_at: <YYYY-MM-DD>
shadow: false
---

# Runbook: <Topic>

## When to use

<One to two sentences describing the symptom, alert, or scheduled
operation that brings someone here.>

## Procedure

1. <Step. Copy-pasteable command or precise UI action.>
2. <Step.>
3. <Step.>

## Verification

\`\`\`bash
<command that confirms success>
\`\`\`

## Rollback

1. <Step.>
2. <Step.>

<!-- Sizing target: ≤ 800 words. Trim before declaring done. -->
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/templates/runbook.md
git commit -m "feat(doxcavate): add runbook template"
```

---

### Task 15: `templates/index.md`

**Files:**

- Create: `skills/doxcavate/templates/index.md`

- [ ] **Step 1: Write the file**

```markdown
---
kind: index
related: []
last_verified_commit: <sha>
last_verified_at: <YYYY-MM-DD>
shadow: false
---

# <Area name> docs index

## What lives here

- [<Doc title>](<filename.md>) — <one-line summary>
- [<Doc title>](<filename.md>) — <one-line summary>

## Reading order

<Optional: include only if this subdir owns a learning path. List the
ordered reading path here, linking into the relevant docs.>

## Doc plan (root index only)

<In the repo-root index.md produced by survey mode, the doc plan goes
here as a prioritized list with status markers.>

| Priority | Doc | Status | Rationale |
| --- | --- | --- | --- |
| 1 | `how-it-works-<topic>` | missing | <one-line why this matters> |
| 2 | `runbook-<topic>` | missing | <one-line why> |
| 3 | `learning-path-<topic>` | missing | <one-line why> |
```

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/templates/index.md
git commit -m "feat(doxcavate): add index template"
```

---

## Phase 4 — Wire SKILL.md to references and templates

### Task 16: Fill in SKILL.md routing and reference index

**Files:**

- Modify: `skills/doxcavate/SKILL.md` (replace the stub from Task 2)

- [ ] **Step 1: Replace SKILL.md content**

Open the file and replace the body (keep the frontmatter from Task 2
verbatim — name, description). New body:

```markdown
# doxcavate

Producing durable, structured documentation in codebases where written
docs are sparse — readable by humans and agents alike.

## Install

\`\`\`bash
npx skills add xornivore/skills@doxcavate --agent claude-code -y
\`\`\`

## When to use

Invoke doxcavate when:

- The user asks to inventory or document a codebase ("doxcavate this
  repo", "what should be documented?", "doxcavate the X").
- The user names a specific doc to write or refresh ("doxcavate
  `runbook-deploy`", "write a how-it-works for the ingestion
  pipeline").
- The user asks doxcavate to update existing docs after code changes.

Do **not** invoke doxcavate for:

- Auto-generated API references (OpenAPI → Markdown, godoc, etc.) —
  those are tool-shaped, not doc-shaped.
- ADRs / decision records — they need commit-time discipline doxcavate
  can't manufacture after the fact.

## Decision flow

\`\`\`text
Invoked
  ├─ Prompt names a doc target?      → DRAFT mode
  ├─ Prompt asks for inventory?       → SURVEY mode
  └─ Ambiguous?                       → ask once, then route
\`\`\`

## Mode summary

- **survey** — produce or refresh the repo's top-level doc index as a
  prioritized doc plan. No leaf docs are written. See
  [invocation-modes](./references/invocation-modes.md).
- **draft** — produce or update one specific doc end-to-end. Always
  reads the index first; runs the production-sources flow; copies the
  matching template; runs review before declaring done. See
  [invocation-modes](./references/invocation-modes.md) and
  [doc-kinds](./references/doc-kinds.md).

## Hard rules

1. **Never silently write outside the host repo.** Shadow mode is opt-in
   and requires user acknowledgment on first write. See
   [layout-and-discovery](./references/layout-and-discovery.md).
2. **Never silently add meta-files** (`.doxcavate.yml`, `docs/`) to a
   repo that has none. Ask first.
3. **Code wins on facts.** When sources disagree, the code is the
   ground truth. See
   [investigation-and-sources](./references/investigation-and-sources.md).
4. **Factcheck is non-skippable.** No flag, no prompt hint, no config
   override skips the factcheck pass. See
   [review-methodology](./references/review-methodology.md).
5. **Persona output is capped at 7 ranked items.** No exceptions. If
   the reviewer would have to drop substantive items to fit, it emits
   `E_PERSONA_OVERFLOW` and halts. See
   [review-methodology](./references/review-methodology.md).
6. **No `git blame` author attribution** in any doc doxcavate writes.

## Reference index

- [doc-kinds](./references/doc-kinds.md) — taxonomy, front-matter,
  required structural anchors per kind, sizing targets.
- [layout-and-discovery](./references/layout-and-discovery.md) —
  config sniffing, integrated vs shadow modes, repo keying.
- [invocation-modes](./references/invocation-modes.md) — survey vs
  draft, routing rules, action checklists.
- [investigation-and-sources](./references/investigation-and-sources.md)
  — adaptive investigation, the three production sources (code,
  existing docs, commits), reconciliation order.
- [review-methodology](./references/review-methodology.md) — factcheck
  + persona two-pass loop, output contract, opt-in deviations,
  dispatched agents, escape hatches.
- [personas](./references/personas.md) — review-persona briefs per
  doc kind.

## Templates

When drafting a new doc, copy the matching template:

- `templates/how-it-works.md`
- `templates/learning-path.md`
- `templates/service-map.md`
- `templates/glossary.md`
- `templates/runbook.md`
- `templates/index.md`

## Top-level action checklist (when invoked)

1. Run discovery (resolve config, docs root, storage mode). See
   [layout-and-discovery](./references/layout-and-discovery.md).
2. Route to survey or draft based on the prompt.
3. **Survey:** inventory the repo, propose the doc plan, write
   `index.md`, stop.
4. **Draft:**
   1. Load `index.md`.
   2. Run the production-sources flow.
   3. Copy the matching template.
   4. Fill in placeholders using the reconciled sources.
   5. Run the factcheck pass (never skippable).
   6. Run the persona pass (cap of ≤7 ranked items, optional patches).
   7. Apply all returned items.
   8. Run the focused factcheck on changed regions.
   9. Done — or, in thorough mode, repeat steps 5–8 up to 3 total
      rounds.
```

In the actual file, use literal triple backticks instead of the escaped
form shown above.

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Read the file end-to-end as if invoking doxcavate**

Open `skills/doxcavate/SKILL.md` and read it cold. Verify:

- Routing decision is unambiguous.
- Each reference link resolves to a file you actually created.
- Hard rules are clear and free of contradictions.

If anything is unclear, fix inline.

- [ ] **Step 4: Commit**

```bash
git add skills/doxcavate/SKILL.md
git commit -m "feat(doxcavate): wire SKILL.md routing, hard rules, and reference index"
```

---

### Task 17: `skills/doxcavate/README.md` (per-skill README)

**Files:**

- Create: `skills/doxcavate/README.md`

- [ ] **Step 1: Write the file**

```markdown
# doxcavate

Produces durable, structured documentation in codebases where written
docs are sparse. Two modes — `survey` (proposes a doc plan) and `draft`
(writes one specific doc end-to-end). Drafts are review-gated by a
factcheck pass and a kind-keyed persona pass.

## Install

\`\`\`bash
npx skills add xornivore/skills@doxcavate --agent claude-code -y
\`\`\`

## See also

- [`SKILL.md`](./SKILL.md) — entry point and routing.
- [`references/`](./references/) — deep content per topic.
- [`templates/`](./templates/) — skeletons for the six doc kinds.
- [Design spec](../../docs/superpowers/specs/2026-04-29-doxcavate-design.md).
```

In the actual file, use literal triple backticks.

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/doxcavate/README.md
git commit -m "docs(doxcavate): add per-skill README"
```

---

## Phase 5 — Smoke test and PR

### Task 18: End-to-end smoke walk-through

**Goal:** read the skill cold, as if you were Claude Code being invoked
in a target repo, and confirm the routing produces sensible behavior on
a few canned prompts.

- [ ] **Step 1: Walk through "doxcavate this repo"**

Open `skills/doxcavate/SKILL.md`. Trace the decision flow with the
prompt "doxcavate this repo".

- Expected route: SURVEY mode.
- Next: read `references/layout-and-discovery.md` (discovery flow),
  resolve docs root, then read
  `references/invocation-modes.md` for survey-mode actions.

If any step is unclear or a referenced file doesn't exist, fix inline.

- [ ] **Step 2: Walk through "doxcavate `runbook-deploy`"**

- Expected route: DRAFT mode for `runbook-deploy.md`.
- Next: discovery → load index → run production sources → copy
  `templates/runbook.md` → fill → factcheck → persona (operator
  brief) → apply → focused factcheck → done.

- [ ] **Step 3: Walk through "doxcavate the ingestion pipeline"**

- Expected route: DRAFT mode for `how-it-works-ingestion-pipeline.md`.
- Next: same as above with `templates/how-it-works.md` and the
  skeptical-engineer persona.

- [ ] **Step 4: Walk through a hostile-repo case**

Imagine a target repo with no `docs/`, no `.doxcavate.yml`, no
`CLAUDE.md` docs path, and the user asks "doxcavate this repo".

- Expected: discovery falls through to step 6 (default hybrid layout).
- Mode-selection step 8.3.x kicks in: ask once "integrated or
  shadow?" before writing anything.
- If user picks shadow: write config to
  `~/.config/doxcavate/<repo-key>.yml`, docs root resolves to
  `~/.local/share/doxcavate/<repo-key>/docs/`, every doc carries
  `shadow: true` in front-matter.

If any of these paths is unclear in the skill content, fix inline.

- [ ] **Step 5: Run a final lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 6: Commit any inline fixes**

```bash
git add skills/doxcavate/
git commit -m "fix(doxcavate): smoke-walk fixes"
```

If no fixes were needed, skip the commit.

---

### Task 19: Push branch and open PR

- [ ] **Step 1: Push**

```bash
git push -u origin plan/doxcavate
```

- [ ] **Step 2: Open the PR**

```bash
gh pr create --title "feat(doxcavate): implement skill per design spec" --body "$(cat <<'EOF'
## Summary

Implements the \`doxcavate\` skill per the design spec at
\`docs/superpowers/specs/2026-04-29-doxcavate-design.md\` and the
implementation plan at
\`docs/superpowers/plans/2026-04-30-doxcavate.md\`.

## What lands

- \`skills/doxcavate/SKILL.md\` — entry point with routing, hard rules,
  and reference index.
- \`skills/doxcavate/references/\` — deep content per spec section.
- \`skills/doxcavate/templates/\` — skeletons for the six doc kinds.
- \`skills/doxcavate/README.md\` — per-skill README.
- Top-level \`README.md\` updated to list doxcavate in the skills table.

## Test plan

- [ ] Install in a sandbox repo: \`npx skills add xornivore/skills@doxcavate --agent claude-code -y\`
- [ ] Invoke with "doxcavate this repo" — expect survey-mode behavior, doc plan written to \`docs/index.md\`
- [ ] Invoke with "doxcavate \\\`runbook-deploy\\\`" — expect draft-mode behavior, runbook template populated and review-gated
- [ ] Invoke in a repo with no \`docs/\` — confirm the integrated-vs-shadow prompt fires before any write
- [ ] Lint passes (\`pnpm lint\`)
EOF
)"
```

Note: the heredoc above uses single-quoted EOF to prevent interpolation,
plus escaped backticks in the body.

- [ ] **Step 3: Note the PR URL** (returned by the command above) for
  the user.

---

## Self-review (run after the plan is written)

Before declaring this plan done, walk it once with fresh eyes:

1. **Spec coverage:** every numbered spec section (1–12) is referenced
   by at least one task. Open questions (section 12) are not
   implementation targets.
2. **Placeholder scan:** no "TBD", no "implement later", no "similar to
   Task N". Every code/content step shows the actual content.
3. **Type/name consistency:** the persona briefs in `personas.md`
   match the table in `review-methodology.md`. The hard rules in
   `SKILL.md` match the spec sections they reference. The template
   front-matter shape matches `doc-kinds.md`.

If any gap is found, add or amend the relevant task inline.
