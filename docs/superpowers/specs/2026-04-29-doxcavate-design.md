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

doxcavate sniffs before writing anything. Discovery order:

1. `$DOXCAVATE_CONFIG` env var → honor it.
2. `.doxcavate.yml` at repo root → honor it.
3. `~/.config/doxcavate/<repo-key>.yml` → honor it
   (see §3.2 — supports shadow mode and "hostile repo" use).
4. `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` declares a docs path →
   honor it.
5. Repo already has a `docs/` tree or co-located `<area>/docs/` dirs →
   match the existing convention.
6. Default to **hybrid layout**:
   - Repo-root `docs/` for cross-cutting docs:
     `docs/index.md`, `docs/glossary.md`, `docs/service-map.md`,
     `docs/runbook-*.md`, `docs/learning-path-*.md`.
   - Co-located `docs/` subdirs adjacent to source for
     `how-it-works-*.md` leaves and a per-subdir `index.md`
     (e.g. `pkg/<area>/docs/`, `services/<svc>/docs/`,
     `<module>/docs/` — match whatever the repo already calls a
     "code area").

Whatever the choice, doxcavate writes it back to the active config file
(creating it on first run) so subsequent invocations don't re-decide.

### 3.1 Storage modes

doxcavate supports two storage modes:

- **integrated** *(default)* — config and docs live inside the host repo
  (`.doxcavate.yml`, repo-root `docs/`, co-located `<area>/docs/`). The
  team gets the docs in version control where they belong.
- **shadow** — config and docs live in a user-local tree, fully outside
  the host repo:
  - Config: `~/.config/doxcavate/<repo-key>.yml`
  - Docs root: `~/.local/share/doxcavate/<repo-key>/docs/`
    (mirrors the same hybrid layout, just re-rooted)

  Shadow exists for the **solo-contributor-in-a-hostile-repo** case: a
  contributor wants to make progress on personal documentation sanity in
  a codebase where committing meta-files or new top-level dirs is not
  practical (team resistance, frozen scope, contractor boundaries, etc.).
  Shadow docs use the same kinds, anchors, and sizing as integrated docs;
  the only differences are the root path and a `shadow: true` flag in
  the front-matter so the two trees never get confused if both ever
  coexist.

### 3.2 Repo keying for external state

When config or docs live outside the repo, doxcavate needs a stable key
per repo. Resolution order:

1. `git remote get-url origin` → slugified host + path
   (e.g., `github.com_acme_widgets`). Preferred.
2. Else: SHA1 of the repo's absolute filesystem path, truncated to 12
   chars.

The chosen key is recorded in the config so the same repo doesn't get
re-keyed if its remote changes later.

### 3.3 Mode selection

- **Explicit:** the active config file sets `mode: integrated | shadow`.
- **Implicit:** if no config is found and doxcavate is about to write the
  first artifact, it asks the user once whether to go integrated or
  shadow, then writes the answer to the appropriate config location.
  doxcavate never silently writes outside the repo, and never silently
  adds meta-files to a repo that doesn't already have any.

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

## 6. Production sources

doxcavate produces docs from three sources. Each has a specific role and
none is trusted on its own. §5 covers *how* doxcavate explores; this
section covers *what* it reads.

### 6.1 Code (source of truth)

Code is the primary input — it is what doxcavate ultimately documents.
Both survey and draft modes read code via inline Read/Grep or fan-out
Agent dispatches (§5). When sources disagree, **code always wins.**
Existing docs and commit history can suggest framing but they cannot
override what the code currently does.

### 6.2 Existing docs (treated as hypotheses)

doxcavate scans the repo for any markdown — repo-root `README.md`,
`docs/**`, `**/README.md`, `**/CONTRIBUTING.md`, package READMEs, doc
comments embedded in code, etc. Existing claims are read as
**hypotheses to verify**, not facts to repeat. doxcavate cross-checks
each against code:

- **Verified** → fold into the new doc; if the framing is good, adapt it.
- **Contradicted** → flag in the survey output (or the relevant
  `index.md`'s `## Doc plan` table) so the drift can be addressed.
  doxcavate does **not** silently rewrite or delete pre-existing docs.
- **Unverifiable** (e.g., a claim about an external service doxcavate
  cannot reach) → carry forward with an explicit
  `> note: from existing doc <path>; not independently verified`
  callout.

Pre-existing docs that don't follow doxcavate's structural-anchor
convention are still readable (per §7.3) — verification does not
require structural conformance.

### 6.3 Code commits (motivation + drift signal)

Git history is doxcavate's source of *why*. Code shows what; commits
show why and when. Used for:

- **Origin and evolution.** For the (lower-priority) conceptual layer
  of `learning-path-*`, `git log` against the relevant paths surfaces
  when a subsystem was introduced and what motivated the major changes
  since.
- **Decisions.** Commit messages frequently encode non-obvious choices.
  doxcavate harvests these as candidate items for `## Background`
  sections and as a v2 ADR seed list.
- **Drift indication.** When refreshing an existing doc, doxcavate
  diffs the documented paths against `last_verified_commit` (front-
  matter) to scope what changed since the doc was last verified. If
  the front-matter is missing, doxcavate falls back to "any commit
  touching the documented paths in the last 90 days."

doxcavate does **not** perform author attribution from `git blame`.
Knowing who wrote something is rarely useful in docs and risks
encoding social structure that ages badly.

doxcavate quotes commit subjects (with short SHAs) when a single commit
explains a non-obvious choice. Long commit-message bodies are
summarized, not quoted in full.

### 6.4 Reconciliation order

When all three sources are consulted (typical for survey mode and for
drafting a doc that has prior art), doxcavate reads in this order:

1. **Existing docs** — cheap, low-context, gives a map of what's
   already claimed.
2. **Code** — establishes ground truth.
3. **Commits** — adds motivation, dates, and drift context.

Then reconciles: code wins on facts; commits supply motivation when
prose is missing it; existing docs are graded
(verified / contradicted / unverifiable) and the result is folded into
the survey output or the new doc.

### 6.5 Future sources (deferred)

Out of scope for v1 but anchored here for design extensibility:

- **PRs and issues** (GitHub / Linear / etc.) — richer motivation than
  raw commits, especially for recent changes. Requires an external API
  dependency, hence deferred.
- **Tests** — encode expected behavior; especially useful for
  `## Verification` anchors and for catching code-vs-docs drift at the
  behavior level. Deferred until the basic three-source loop is stable.

## 7. Doc structure

### 7.1 Front-matter (required on docs doxcavate writes)

```yaml
---
kind: how-it-works | learning-path | service-map | glossary | runbook | index
subject: <slug matching the file name suffix; omit for singletons>
related: [<other doc slugs>]
last_verified_commit: <repo HEAD sha at the moment doxcavate wrote/refreshed this doc>
last_verified_at: <ISO date of that write>
---
```

### 7.2 Required structural anchors per kind

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

### 7.3 Tolerance for pre-existing docs

The structural anchor requirement applies to docs doxcavate **creates or
rewrites**. doxcavate must read pre-existing docs without complaint, even
when they don't follow the convention. Migrating an old doc to the
convention is an explicit user request, not a side effect.

### 7.4 Sizing

Word-count targets keep "sizeable" honest:

- `how-it-works-*` ≤ 600 words
- `runbook-*` ≤ 800 words
- `learning-path-*` ≤ 1200 words
- `service-map.md` and `glossary.md` are reference shapes — they grow with
  the codebase, not with prose.

## 8. Related services

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

## 9. Out of scope (v1)

- **Doc freshness / drift detection.** The `## Verification` anchor and
  `last_verified_commit` enable a future sibling skill to audit and
  refresh docs. doxcavate itself only writes them.
- **Auto-generated API references** (OpenAPI → markdown, godoc, etc.).
  Those are tool-shaped, not doc-shaped.
- **ADRs / decision records.** Worth revisiting in v2; deferred because
  they need commit-time discipline that a doc-after-the-fact skill can't
  manufacture.

## 10. Non-goals

- Replacing existing docs that already work.
- Producing exhaustive reference material. The skill's value is durable,
  navigable docs at sustainable size.
- Mandating a single layout. The skill follows the host repo's convention
  when one exists.

## 11. Open questions

- Should survey mode produce a single root `docs/index.md` or also seed
  per-subdir `index.md` stubs? (Leaning: root only; subdir indexes appear
  the first time a leaf doc lands in that subdir during draft mode.)
- In shadow mode, should doxcavate write a single user-local "meta-index"
  (`~/.local/share/doxcavate/index.md`) that lists all repos the user has
  shadow-documented? (Leaning: yes, but v1.1 — not strictly needed for
  the first release.)
