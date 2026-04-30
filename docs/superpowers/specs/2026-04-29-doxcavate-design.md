---
spec: doxcavate
status: draft
date: 2026-04-29
---

# doxcavate — design

## 1. Premise

doxcavate is invoked in codebases where written documentation is sparse —
usually because velocity and team shape took priority over writing things
down. Its job is to produce durable, structured documentation over time
that humans and agents can both read fluently, so future work happens with
the right amount of rigor, safety, and confidence.

The skill is incremental and additive. It does not replace existing docs
that already work; it fills gaps, threads what exists into navigable paths,
and leaves a trail future skills (and humans) can keep current.

## 2. Doc taxonomy

A small, fixed vocabulary. File-name prefixes are part of the contract:
agents grep, route, and link by prefix without parsing prose.

| Kind | File pattern | Multiplicity | Role |
| --- | --- | --- | --- |
| Leaf reference | `how-it-works-<topic>.md` | many | Concise description of one feature, module, or "unit". Code-anchored. |
| Learning path | `learning-path-<topic>.md` | many | Onboarding tour + task-oriented runbook + (lower-priority) conceptual narrative. Threads `how-it-works-*` leaves into a reading order with checkpoints. |
| Service map | `service-map.md` | one per repo | Catalog of in-repo services and external services this codebase talks to, with the integration call sites. |
| Glossary | `glossary.md` | one per repo | Terms, acronyms, internal jargon. |
| Runbook | `runbook-<topic>.md` | many | Operational procedures: deploy, rollback, oncall response. |
| Index | `index.md` (or `README.md` if the host convention prefers) | one per docs subdir | Auto-maintained navigation backbone — what's here, what links where. |

Architecture-overview docs are deliberately not a separate slot. That role
is split between (a) the conceptual layer of `learning-path-*` and (b) the
navigational role of `index.md` files at multiple levels.

## 3. Layout & path discovery

doxcavate sniffs the host repo before writing anything:

1. If `.doxcavate.yml` exists at repo root → honor it (path config,
   related-repo pointers).
2. Else if `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` declares a docs path →
   honor it.
3. Else if the repo already has a `docs/` tree or `<pkg>/docs/` co-located
   dirs → match the existing convention.
4. Else → default to **hybrid layout**:
   - Repo-root `docs/` for cross-cutting docs:
     `docs/index.md`, `docs/glossary.md`, `docs/service-map.md`,
     `docs/runbook-*.md`, `docs/learning-path-*.md`.
   - Co-located `docs/` subdirs adjacent to source for
     `how-it-works-*.md` leaves and a per-subdir `index.md`
     (e.g. `pkg/<area>/docs/`, `services/<svc>/docs/`,
     `<module>/docs/` — match whatever the repo already calls a
     "code area").

Whatever the choice, doxcavate writes it back to `.doxcavate.yml` (creating
it on first run) so subsequent invocations don't re-decide.

## 4. Invocation modes

Two modes, picked from the user's prompt:

- **survey** — produces or refreshes the repo's top-level doc index
  (default `docs/index.md`; whatever path discovery resolved) as a
  *doc plan*: an ordered, prioritized list of which `how-it-works-*`,
  `learning-path-*`, `runbook-*`, etc. should exist for this repo, each
  with a one-line rationale and a `status: missing | drafted | verified`
  marker. No leaf docs are written in survey mode.
- **draft** — produces or updates one specific doc named or implied by the
  prompt. Always reads the current top-level doc index (creating it if
  missing) before drafting, so leaves link into the broader plan.

Routing rule:

- Prompt names a target ("doxcavate the ingestion pipeline" /
  "doxcavate `runbook-deploy`") → **draft**.
- Prompt asks for an inventory or onboarding pass ("doxcavate this repo" /
  "what should be documented?") → **survey**.
- Ambiguous → ask once.

## 5. Investigation methodology

Adaptive:

- **Inline reading** when the answer fits in <5 reads or follows a tight
  call chain. Use Read, Grep, Bash directly.
- **Fan-out via dispatched agents** when the question is parallel-shaped
  ("find all entry points", "list external deps", "map data flow",
  "find tests") or the repo is large. Use the host's Agent tool with
  `subagent_type=Explore` for read-only probes; `general-purpose` for
  deeper synthesis.

If `superpowers:dispatching-parallel-agents` is available, doxcavate
defers to it for survey mode. **doxcavate must not require superpowers** —
it works with the host's native tools alone, and treats superpowers
integration as an enhancement.

Survey mode is fan-out by default. Draft mode is inline by default and
escalates to fan-out as scope grows.

## 6. Doc structure

### 6.1 Front-matter (required on docs doxcavate writes)

```yaml
---
kind: how-it-works | learning-path | service-map | glossary | runbook | index
subject: <slug matching the file name suffix; omit for singletons>
related: [<other doc slugs>]
last_verified_commit: <repo HEAD sha at the moment doxcavate wrote/refreshed this doc>
last_verified_at: <ISO date of that write>
---
```

### 6.2 Required structural anchors per kind

- **`how-it-works-*`** — `## Summary` (≤3 sentences),
  `## Entry points` (file:line list),
  `## External dependencies` (services and libs it talks to, with
  integration call sites),
  `## Verification` (one or more shell commands or grep patterns an agent
  can run to confirm the doc still matches code).
- **`learning-path-*`** — `## Audience`,
  `## Prerequisites`,
  `## Reading order` (ordered list of `how-it-works-*` links plus code
  references),
  `## Checkpoints` ("you should now be able to…" prompts),
  optional `## Background` for the conceptual-narrative layer.
- **`runbook-*`** — `## When to use`,
  `## Procedure` (numbered, copy-pasteable),
  `## Verification`,
  `## Rollback`.
- **`service-map.md`** — `## In-repo services` (table),
  `## External services` (table with integration points),
  optional `## Diagram` (Mermaid).
- **`glossary.md`** — alphabetized definition list.
- **`index.md`** — `## What lives here`,
  `## Reading order` (if the subdir owns a learning-path),
  `## Doc plan` (in survey-mode root index: prioritized list of docs that
  should exist, with status markers).

### 6.3 Tolerance for pre-existing docs

The structural anchor requirement applies to docs doxcavate **creates or
rewrites**. doxcavate must read pre-existing docs without complaint, even
when they don't follow the convention. Migrating an old doc to the
convention is an explicit user request, not a side effect.

### 6.4 Sizing

Word-count targets keep "sizeable" honest:

- `how-it-works-*` ≤ 600 words
- `runbook-*` ≤ 800 words
- `learning-path-*` ≤ 1200 words
- `service-map.md` and `glossary.md` are reference shapes — they grow with
  the codebase, not with prose.

## 7. Related services

doxcavate documents *integration points*, not service internals. For each
external service:

1. Identify the integration call sites (HTTP clients, gRPC stubs, env
   vars, hostnames in config).
2. Add a row to `service-map.md`.
3. Reference it from `## External dependencies` in any `how-it-works-*`
   that touches it.

If `.doxcavate.yml` lists sibling repo paths or accessible OpenAPI / proto
URLs, doxcavate may follow them to enrich the service-map entry — but it
never writes docs *into* a sibling repo from outside.

## 8. Out of scope (v1)

- **Doc freshness / drift detection.** The `## Verification` anchor and
  `last_verified_commit` enable a future sibling skill to audit and
  refresh docs. doxcavate itself only writes them.
- **Auto-generated API references** (OpenAPI → markdown, godoc, etc.).
  Those are tool-shaped, not doc-shaped.
- **ADRs / decision records.** Worth revisiting in v2; deferred because
  they need commit-time discipline that a doc-after-the-fact skill can't
  manufacture.

## 9. Non-goals

- Replacing existing docs that already work.
- Producing exhaustive reference material. The skill's value is durable,
  navigable docs at sustainable size.
- Mandating a single layout. The skill follows the host repo's convention
  when one exists.

## 10. Open questions

- Should `.doxcavate.yml` be standardized as part of v1, or should the
  first release ship without a config file and rely on `CLAUDE.md`
  hints + sniffing? (Leaning: ship sniffing first, add the config file
  in v1.1 only if friction shows up.)
- Should survey mode produce a single root `docs/index.md` or also seed
  per-subdir `index.md` stubs? (Leaning: root only; subdir indexes appear
  the first time a leaf doc lands in that subdir during draft mode.)
