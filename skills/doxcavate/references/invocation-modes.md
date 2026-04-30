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
