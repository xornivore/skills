---
name: doxcavate
description: Use when invoked in a codebase that has sparse or missing documentation, to produce durable, structured docs that humans and agents can both read fluently. Two modes — `survey` (proposes a doc plan in `docs/index.md`) and `draft` (writes one specific doc end-to-end). Triggered by phrases like "doxcavate this repo", "doxcavate the X", "what should be documented?", or any explicit request to inventory or write project documentation.
license: MIT
compatibility: Designed for Claude Code (or similar agentskills.io-compatible clients).
---

# doxcavate

Producing durable, structured documentation in codebases where written
docs are sparse — readable by humans and agents alike.

## Install

```bash
npx skills add xornivore/skills@doxcavate --agent claude-code -y
```

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

```text
Invoked
  ├─ Prompt names a doc target?      → DRAFT mode
  ├─ Prompt asks for inventory?       → SURVEY mode
  └─ Ambiguous?                       → ask once, then route
```

## Mode summary

Two **invocation modes**:

- **survey** — produce or refresh the top-level doc index as a
  prioritized doc plan. No leaf docs are written. See
  [invocation-modes](./references/invocation-modes.md).
- **draft** — produce or update one specific doc end-to-end. Always
  reads the index first; runs the production-sources flow; copies the
  matching template; runs review before declaring done. See
  [invocation-modes](./references/invocation-modes.md) and
  [doc-kinds](./references/doc-kinds.md).

Three **storage modes** decide where docs and config live:

- **integrated** *(default)* — everything in the host repo.
- **leaves-only** — substance leaves in the repo; meta docs (`index.md`,
  `glossary.md`, `service-map.md`) and config in the shadow tree. For
  the partially-hostile-repo case.
- **shadow** — everything in a user-local shadow tree. For the
  fully-hostile-repo case.

See [layout-and-discovery](./references/layout-and-discovery.md) for
discovery, mode selection, and the repo-keying convention.

## Hard rules

1. **Never silently write outside the host repo.** Shadow and
   leaves-only are opt-in and require user acknowledgment on first
   write. See
   [layout-and-discovery](./references/layout-and-discovery.md).
2. **Never silently add meta-files** (`.doxcavate.yml`, `docs/`) to a
   repo that has none. Ask first.
3. **In `leaves-only`, leaves committed to the repo must not link to
   shadow-located meta docs.** Shadow paths are per-machine and
   per-user; rendering them into a committed leaf would break for
   everyone else. Leaf-to-leaf links inside the repo are fine.
4. **Code wins on facts.** When sources disagree, the code is the
   ground truth. See
   [investigation-and-sources](./references/investigation-and-sources.md).
5. **Factcheck is non-skippable.** No flag, no prompt hint, no config
   override skips the factcheck pass. See
   [review-methodology](./references/review-methodology.md).
6. **Persona output is capped at 7 ranked items.** No exceptions. If
   the reviewer would have to drop substantive items to fit, it emits
   `E_PERSONA_OVERFLOW` and halts. See
   [review-methodology](./references/review-methodology.md).
7. **No `git blame` author attribution** in any doc doxcavate writes.

## Reference index

> Read each reference only at the action step that calls for it — not
> eagerly during activation. This is how the skill stays lean in the
> agent's context (progressive disclosure, stage 3).

- [doc-kinds](./references/doc-kinds.md) — taxonomy, front-matter,
  required structural anchors per kind, sizing targets. Read when
  drafting or reviewing structural conformance.
- [layout-and-discovery](./references/layout-and-discovery.md) —
  config sniffing, the three storage modes (integrated, leaves-only,
  shadow), repo keying. Read at the discovery step (always the first
  step).
- [invocation-modes](./references/invocation-modes.md) — survey vs
  draft, routing rules, action checklists. Read once mode is decided.
- [investigation-and-sources](./references/investigation-and-sources.md)
  — adaptive investigation, the three production sources (code,
  existing docs, commits), reconciliation order. Read at the start of
  any draft.
- [review-methodology](./references/review-methodology.md) — the
  factcheck-then-persona two-pass loop, output contract, opt-in
  deviations, dispatched agents, escape hatches. Read after a draft is
  produced.
- [personas](./references/personas.md) — review-persona briefs per
  doc kind. Read when constructing the persona-pass dispatch prompt.

## Templates

When drafting a new doc, copy the matching template from `assets/`:

- `assets/how-it-works-template.md`
- `assets/learning-path-template.md`
- `assets/service-map-template.md`
- `assets/glossary-template.md`
- `assets/runbook-template.md`
- `assets/index-template.md`

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
