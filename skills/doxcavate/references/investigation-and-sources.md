# Investigation and production sources

How doxcavate explores (the *how*) and what doxcavate reads (the *what*).
Each pass below feeds drafts and reviews; none is trusted on its own.

## Investigation methodology

Adaptive:

- **Inline reading** when the answer fits in fewer than five reads or
  follows a tight call chain. Use Read, Grep, Bash directly.
- **Fan-out via dispatched agents** when the question is parallel-shaped
  ("find all entry points", "list external deps", "map data flow", "find
  tests") or the repo is large. Use the host's Agent tool with
  `subagent_type=Explore` for read-only probes; `general-purpose` for
  deeper synthesis.

If `superpowers:dispatching-parallel-agents` is available, defer to it
for survey mode. **Do not require superpowers** — work with the host's
native tools alone, and treat superpowers integration as an
enhancement.

Survey mode is fan-out by default. Draft mode is inline by default and
escalates to fan-out as scope grows.

## Production sources

Three sources feed every draft. Each has a specific role; none is
trusted on its own.

### Code (source of truth)

Code is the primary input — it is what the skill ultimately documents.
Both survey and draft modes read code via inline Read/Grep or fan-out
Agent dispatches (see [Investigation methodology](#investigation-methodology)).
When sources disagree, **code always wins.** Existing docs and commit
history can suggest framing but they cannot override what the code
currently does.

### Existing docs (treated as hypotheses)

Scan the repo for any markdown — repo-root `README.md`, `docs/**`,
`**/README.md`, `**/CONTRIBUTING.md`, package READMEs, doc comments
embedded in code, etc. Existing claims are read as **hypotheses to
verify**, not facts to repeat. Cross-check each against code:

- **Verified** — fold into the new doc; if the framing is good, adapt it.
- **Contradicted** — flag in the survey output (or the relevant
  `index.md`'s `## Doc plan` table) so the drift can be addressed.
  Do **not** silently rewrite or delete pre-existing docs.
- **Unverifiable** (e.g., a claim about an external service doxcavate
  cannot reach) — carry forward with an explicit
  `> note: from existing doc <path>; not independently verified`
  callout.

Pre-existing docs that don't follow doxcavate's structural-anchor
convention are still readable (see
[Tolerance for pre-existing docs](./doc-kinds.md#tolerance-for-pre-existing-docs))
— verification does not require structural conformance.

### Code commits (motivation + drift signal)

Git history is doxcavate's source of *why*. Code shows what; commits show
why and when. Used for:

- **Origin and evolution.** For the (lower-priority) conceptual layer of
  `learning-path-*`, `git log` against the relevant paths surfaces when a
  subsystem was introduced and what motivated the major changes since.
- **Decisions.** Commit messages frequently encode non-obvious choices.
  Harvest these as candidate items for `## Background` sections and as a
  v2 ADR seed list.
- **Drift indication.** When refreshing an existing doc, diff the
  documented paths against `last_verified_commit` (front-matter) to scope
  what changed since the doc was last verified. If the front-matter is
  missing, fall back to "any commit touching the documented paths in the
  last 90 days."

Do **not** perform author attribution from `git blame`. Knowing who wrote
something is rarely useful in docs and risks encoding social structure
that ages badly.

Quote commit subjects (with short SHAs) when a single commit explains a
non-obvious choice. Long commit-message bodies are summarized, not quoted
in full.

### Reconciliation order

When all three sources are consulted (typical for survey mode and for
drafting a doc that has prior art), read in this order:

1. **Existing docs** — cheap, low-context; gives a map of what's already
   claimed.
2. **Code** — establishes ground truth.
3. **Commits** — adds motivation, dates, and drift context.

Then reconcile: code wins on facts; commits supply motivation when prose
is missing it; existing docs are graded (verified / contradicted /
unverifiable) and the result is folded into the survey output or the new
doc.

### Future sources (deferred)

Out of scope for v1 but anchored here for design extensibility:

- **PRs and issues** (GitHub / Linear / etc.) — richer motivation than
  raw commits, especially for recent changes. Requires an external API
  dependency, hence deferred.
- **Tests** — encode expected behavior; especially useful for
  `## Verification` anchors and for catching code-vs-docs drift at the
  behavior level. Deferred until the basic three-source loop is stable.

## Related services

Document *integration points*, not service internals. For each
external service discovered during investigation:

1. Identify the integration call sites (HTTP clients, gRPC stubs, env
   vars, hostnames in config).
2. Add a row to `service-map.md`.
3. Reference it from `## External dependencies` in any `how-it-works-*`
   doc that touches the service.

If `.doxcavate.yml` lists sibling repo paths or accessible OpenAPI /
proto URLs, follow them to enrich the service-map entry — but
**never write docs into a sibling repo from outside.**

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
