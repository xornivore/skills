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

```yaml
---
kind: how-it-works | learning-path | service-map | glossary | runbook | index
subject: <slug matching the file name suffix; omit for singletons>
related: [<other doc slugs>]
last_verified_commit: <repo HEAD sha at the moment doxcavate wrote/refreshed this doc>
last_verified_at: <ISO date of that write>
shadow: false  # set true only when the doc lives outside the host repo (see layout-and-discovery.md)
---
```

## Required structural anchors per kind

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

## Leaves vs meta

`how-it-works-*`, `learning-path-*`, and `runbook-*` are *leaves* —
substance docs about specific code or operations. `index.md`,
`glossary.md`, and `service-map.md` are *meta* — navigation and
reference docs about the docs themselves. The split matters for the
`leaves-only` storage mode: leaves go to the host repo, meta docs go to
the shadow tree. See
[layout-and-discovery](./layout-and-discovery.md) for the storage-mode
matrix.

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
