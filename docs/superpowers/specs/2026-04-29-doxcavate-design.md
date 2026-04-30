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
3. `~/.config/doxcavate/<repo-key>.yml` → honor it (see
   [Repo keying for external state](#32-repo-keying-for-external-state)
   — supports shadow mode and "hostile repo" use).
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

doxcavate supports three storage modes, ordered by how much lands in the
host repo:

- **integrated** *(default)* — config and docs live inside the host repo
  (`.doxcavate.yml`, repo-root `docs/`, co-located `<area>/docs/`). The
  team gets the docs in version control where they belong.
- **partial** — substance leaves
  (`how-it-works-*`, `learning-path-*`, `runbook-*`) live in the host
  repo; meta docs (`index.md`, `glossary.md`, `service-map.md`) and
  config live in the shadow tree:
  - Repo: leaves only, under the discovered docs layout.
  - Config: `~/.config/doxcavate/<repo-key>.yml`.
  - Meta-docs root: `~/.local/share/doxcavate/<repo-key>/docs/`.

  `partial` exists for the **partially-hostile-repo** case: the team
  accepts substance docs (a `how-it-works-foo.md` next to the code is
  uncontroversial) but pushes back on navigation/meta files that read as
  documentation infrastructure. The doc plan, glossary, and service map
  still get produced and persisted — just in the user-local shadow tree
  — so subsequent invocations can read them back. **Leaves committed to
  the repo must not link to shadow-located meta docs.** Shadow paths are
  per-machine and per-user; rendering `~/.local/...` links into a
  committed leaf would break for everyone else. Leaf-to-leaf
  cross-references (relative paths within the repo) are fine; meta-to-leaf
  references from the shadow tree to repo-committed leaves use repo-relative
  paths and resolve correctly when read alongside the repo.
- **shadow** — config and all docs live in a user-local tree, fully
  outside the host repo:
  - Config: `~/.config/doxcavate/<repo-key>.yml`
  - Docs root: `~/.local/share/doxcavate/<repo-key>/docs/`
    (mirrors the same hybrid layout, just re-rooted)

  Shadow exists for the **fully-hostile-repo** case: a contributor wants
  to make progress on personal documentation sanity in a codebase where
  committing *anything* under a docs convention is not practical (team
  resistance, frozen scope, contractor boundaries, etc.). Shadow docs use
  the same kinds, anchors, and sizing as integrated docs; the only
  differences are the root path and a `shadow: true` flag in the
  front-matter so the two trees never get confused if both ever coexist.

In `partial` mode, repo-committed leaves carry `shadow: false` and
shadow-located meta docs carry `shadow: true`. The flag remains a
per-doc statement, not a per-mode one.

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

- **Explicit:** the active config file sets
  `mode: integrated | partial | shadow`.
- **Implicit:** if no config is found and doxcavate is about to write the
  first artifact, it asks the user once which of the three modes to use,
  then writes the answer to the appropriate config location. doxcavate
  never silently writes outside the repo, and never silently adds
  meta-files to a repo that doesn't already have any.

The implicit prompt should explain the three modes briefly and lead with
**partial** when the repo has source-adjacent code areas but no
existing `docs/` tree — that's the case the mode was designed for.

## 4. Invocation modes

Two modes, picked from the user's prompt:

- **survey** — produces or refreshes the top-level doc index as a
  *doc plan*: an ordered, prioritized list of which `how-it-works-*`,
  `learning-path-*`, `runbook-*`, etc. should exist for this repo, each
  with a one-line rationale and a `status: missing | drafted | verified`
  marker. No leaf docs are written in survey mode.
- **draft** — produces or updates one specific doc named or implied by the
  prompt. Always reads the current top-level doc index (creating it if
  missing) before drafting, so leaves link into the broader plan.

Where the doc plan is read from and written to depends on the storage
mode (see [Storage modes](#31-storage-modes)):

- `integrated` — repo-root `docs/index.md` (or whatever path discovery
  resolved).
- `partial` — `~/.local/share/doxcavate/<repo-key>/docs/index.md`.
  The repo never receives an `index.md` in this mode.
- `shadow` — `~/.local/share/doxcavate/<repo-key>/docs/index.md`.

Same file shape; just re-rooted. Draft mode resolves the index path the
same way before reading it.

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
none is trusted on its own.
[Investigation methodology](#5-investigation-methodology) covers *how*
doxcavate explores; this section covers *what* it reads.

### 6.1 Code (source of truth)

Code is the primary input — it is what doxcavate ultimately documents.
Both survey and draft modes read code via inline Read/Grep or fan-out
Agent dispatches (see
[Investigation methodology](#5-investigation-methodology)). When
sources disagree, **code always wins.**
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
convention are still readable (per
[Tolerance for pre-existing docs](#73-tolerance-for-pre-existing-docs))
— verification does not require structural conformance.

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
shadow: false  # true iff this doc lives in a shadow tree (shadow mode, or meta docs in partial)
---
```

The `shadow` flag is a per-doc statement, not a per-mode one. In
`integrated` mode every doc has `shadow: false`; in `shadow` mode every
doc has `shadow: true`; in `partial` mode leaves carry `false` and
meta docs carry `true`. See
[Storage modes](#31-storage-modes).

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

**Leaves vs meta.** `how-it-works-*`, `learning-path-*`, and `runbook-*`
are *leaves* — substance docs about specific code or operations.
`index.md`, `glossary.md`, and `service-map.md` are *meta* — navigation
and reference docs about the docs themselves. The `partial`
[storage mode](#31-storage-modes) keeps leaves in the repo and writes
meta docs to the shadow tree.

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

## 8. Review methodology

Each new doc artifact goes through two review passes after the initial
draft: a **factcheck pass** that grounds the doc in code, and a
**persona pass** that asks whether the doc serves its intended reader.
The two passes have distinct concerns and run in this order — facts
before craft.

### 8.1 Factcheck pass

Mechanical, exhaustive. doxcavate extracts every factual claim from the
draft and verifies it against the codebase:

- **Claim shapes:** file paths, function/method/type names, "X calls Y"
  relationships, env vars, hostnames, config keys, command names and
  flags, file:line entry-point references.
- **Verification:** Read or Grep per claim; Bash where it helps. For
  larger drafts, fan out a dispatched agent — verification is
  parallel-shaped.
- **Outcomes:**
  - **Verified** → leave the claim in place.
  - **Contradicted** → fix the doc; never silently leave the bad
    claim in.
  - **Unverifiable** (claim about an external service the skill cannot
    reach) → carry the claim forward with an explicit
    `> note: not independently verified` callout.
- **Verification block as byproduct.** The grep patterns and shell
  commands the pass actually ran become the doc's `## Verification`
  anchor for `how-it-works-*` and `runbook-*`. The block is **commands
  only** for v1 — any reader (human or future drift-detection skill)
  can run them and compare results to the prose. Capturing expected
  output is a v2 expansion that pairs with drift detection.
- **Never skippable.** Factcheck is what makes a doxcavate doc worth
  trusting. There is no flag to skip it.

### 8.2 Persona pass

Heuristic. doxcavate adopts a persona keyed to the doc's kind and
re-reads the draft as that reader. Briefs are concrete on purpose —
abstract personas don't catch real failure modes.

| Doc kind | Persona |
| --- | --- |
| `how-it-works-*` | Skeptical technical reviewer (seasoned engineer) who will grep what you claim. |
| `learning-path-*` | Newcomer at hour zero who doesn't share your assumptions. |
| `runbook-*` | Operator who needs concise, actionable instructions leading to system recovery. |
| `service-map.md` | Completeness reviewer — looking for missing integrations and unstated assumptions. |
| `glossary.md` | Completeness reviewer — looking for missing terms and inconsistent definitions. |
| `index.md` | Skim-reader who needs to find the right doc in <30 seconds. |

#### 8.2.1 Output contract

The persona pass returns a **ranked list of ≤7 items**, each shaped:

```yaml
location: <line range or anchor in the draft>
problem: <one sentence describing what's wrong>
proposed_change: <one sentence describing what to do about it>
patch: |                  # optional
  <verbatim replacement text>
```

- The cap of 7 is hard. If the reviewer sees more than 7 issues, it
  triages and drops the lowest-ranked items. A 30-item review list is
  a reviewer-noise smell, not a doc-quality signal.
- **Items are ordered by priority, descending.** Substance first; nits
  last.
- **Patches when possible.** If the reviewer can produce the literal
  replacement text, it ships it in `patch`. The authoring agent applies
  the patch verbatim. If the reviewer lacks context to write a good
  patch, it ships the tuple without `patch` and the authoring agent
  writes the fix.

#### 8.2.2 Quality bar

The reviewer is **not** for bikeshedding or relentless critique:

- **Actionable, not aesthetic.** Every item names a specific change to
  apply.
- **Fix when possible.** "Identify a problem" without "propose a fix"
  is acceptable only when the fix requires context the reviewer cannot
  reach.
- **No taste arguments.** Two ways of phrasing the same fact, neither
  ambiguous nor wrong, is bikeshedding — skip it.
- **Brevity is a feature.** The cap exists to enforce triage; ranking
  exists so the lowest-priority items get dropped, not the
  highest-priority ones.

Examples of the bar:

| Don't | Do |
| --- | --- |
| "This section feels too long." | "Lines 45-60 repeat the env-var list from line 12. Replace with 'See env vars above.'" |
| "I'd phrase this differently." | "'Orchestrates ingestion' is ambiguous — code shows a fixed-size goroutine pool. Replace with 'spawns a fixed-size goroutine pool that processes ingestion tasks concurrently'." |
| "Add more detail." | "Verification block omits env vars set in `setup.sh:23`. Add `grep -E '^export INGEST_' setup.sh`." |
| "Not beginner-friendly enough." | "A newcomer won't know what 'ingestion topic' means. Either link to the glossary entry or define it inline on line 8." |
| "Consider restructuring." | "Move `## Verification` above `## External dependencies` — the operator persona needs verification first." |

### 8.3 Loop and termination

```text
draft
  → factcheck
  → persona (≤7 ranked items)
  → authoring agent applies all items
  → focused factcheck (only the regions the persona pass changed)
  → done
```

- **Default: single round.** One factcheck, one persona pass, one
  focused factcheck on the applied changes. No automatic re-run of
  persona.
- **Done** = focused factcheck clean, no outstanding contradictions.
  Unverifiable claims aren't contradictions; they ship with the
  `> note: not independently verified` callout.
- **Doc updates** (refresh of an existing doc): factcheck scopes to
  changed claims; persona runs only if the change is reader-visible
  (sectioning, anchors, voice). Internal-only edits skip persona by
  default.
- **Halt paths** for drastically broken drafts are described in
  [Escape hatches](#86-escape-hatches-too-many-issues-to-fix-in-one-pass).
  The loop never silently truncates a draft that needs to be rethought.

### 8.4 Opt-in deviations from the default

Two deviations are supported, signaled either via prompt hint or
`.doxcavate.yml`:

- **Thorough mode** — runs to fixed-point with a hard cap of 3 full
  rounds. Stops when the persona pass returns zero items, the
  factcheck pass shows zero contradictions, or the cap fires. Use
  when stakes warrant it (a cornerstone runbook, a learning path many
  newcomers will touch).
- **Skip persona** — runs factcheck only. Use for bulk-migration or
  format-only edits. Never available for newly drafted docs.

```yaml
# .doxcavate.yml
review:
  thorough: false        # default; true = run-to-fixed-point, cap 3 rounds
  persona: required      # default; "optional" = honor "skip persona" prompt hints
```

Prompt hints recognized by the skill: "rigorously" / "thorough review"
→ thorough mode; "skip persona" / "mechanical" / "format-only" → skip
persona (only when `review.persona: optional`).

### 8.5 Dispatched agents for review

Both passes can be dispatched as agents when the doc is long or the
codebase is large:

- **Factcheck dispatch:** "Here is the draft. Here is the codebase.
  Return every factual claim and the verification result (verified /
  contradicted / unverifiable) with evidence."
- **Persona dispatch:** "You are `<persona>`. Read this draft. Return
  the persona-pass output contract: a ranked list of ≤7 items, each
  with `location` / `problem` / `proposed_change` and an optional
  `patch`. Brevity is a feature. If you have more than 7 items, you've
  stopped triaging — drop the bottom ones."

Both agents are **read-only**. They never edit the doc. The authoring
agent applies findings in the main context, which keeps responsibility
clear and the resulting changes auditable.

### 8.6 Escape hatches: too many issues to fix in one pass

The cap of ≤7 ranked items + the ranking are how the review enforces
brevity on healthy docs. They are **not** a way to silently truncate
genuinely broken drafts. Two escape conditions halt the loop and
surface the situation so the plan can be rethought rather than
papered over.

#### 8.6.1 `E_TOO_MANY_CONTRADICTIONS` (factcheck overflow)

The factcheck pass halts and emits a structured diagnosis when
contradicted claims cross either threshold:

- **Ratio threshold:** more than 7 contradicted claims AND > 30% of
  extracted claims contradicted.
- **Absolute threshold:** more than 20 contradicted claims, regardless
  of ratio.

Output:

```yaml
result: halt
reason: E_TOO_MANY_CONTRADICTIONS
contradictions: <count> of <total claims>
ratio: <percentage>
top_examples:               # ranked; most drastic first
  - claim: <contradicted claim>
    evidence: <what the code actually says>
  - claim: ...
    evidence: ...
hypothesis: <best guess at root cause — stale assumptions, scope too
  broad, draft based on misunderstanding of the area, code refactored
  since prior doc, etc.>
```

doxcavate does **not** silently apply fixes from a draft that fails
this check — the doc is too far from reality for surface fixes to
help. The user is offered three recovery paths:

- **Redraft** — typical when the draft misunderstood the area.
- **Narrow scope** — when the draft tried to cover too much.
- **Re-investigate** — re-run the production-sources pass (existing
  docs, code, commits) before drafting again.

#### 8.6.2 `E_PERSONA_OVERFLOW` (persona overflow)

The persona reviewer self-reports the same situation in its own
domain. If it would have to drop **substantive** (non-nit) items to
fit the ≤7 cap, it returns an overflow result instead of the normal
ranked list:

```yaml
result: halt
reason: E_PERSONA_OVERFLOW
diagnosis: |
  <one paragraph from the persona's perspective on what's
  fundamentally wrong with the draft>
recommendation: <e.g., "redraft with X reorganization", "narrow
  scope to Y", "this doc kind is wrong for the audience and the
  draft should be re-classified as <other-kind>">
```

The same recovery options apply. Note that overflow is not the same
as "the persona sees flaws beyond rank 7" — those just get dropped per
the brevity rule. Overflow is reserved for cases where the doc fails
its persona structurally and patches at the line level won't help.

#### 8.6.3 Why explicit halt instead of silent truncation

Silent truncation of a broken draft trains future readers to distrust
the doc — they hit one wrong claim and stop trusting the rest. Explicit
halts cost more upfront but produce docs that stay trustworthy. The
escape hatches are the design choice that makes the brevity cap
honest.

## 9. Related services

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

## 10. Out of scope (v1)

- **Doc freshness / drift detection.** The `## Verification` anchor and
  `last_verified_commit` enable a future sibling skill to audit and
  refresh docs. doxcavate itself only writes them.
- **Auto-generated API references** (OpenAPI → markdown, godoc, etc.).
  Those are tool-shaped, not doc-shaped.
- **ADRs / decision records.** Worth revisiting in v2; deferred because
  they need commit-time discipline that a doc-after-the-fact skill can't
  manufacture.

## 11. Non-goals

- Replacing existing docs that already work.
- Producing exhaustive reference material. The skill's value is durable,
  navigable docs at sustainable size.
- Mandating a single layout. The skill follows the host repo's convention
  when one exists.

## 12. Open questions

- Should survey mode produce a single root `docs/index.md` or also seed
  per-subdir `index.md` stubs? (Leaning: root only; subdir indexes appear
  the first time a leaf doc lands in that subdir during draft mode.)
- In shadow mode, should doxcavate write a single user-local "meta-index"
  (`~/.local/share/doxcavate/index.md`) that lists all repos the user has
  shadow-documented? (Leaning: yes, but v1.1 — not strictly needed for
  the first release.)
- Should review personas be configurable per-repo (e.g., a custom
  oncall persona for a codebase with very specific operational
  conventions)? (Leaning: v2; v1 default briefs cover most cases.)
