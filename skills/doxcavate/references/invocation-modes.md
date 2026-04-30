# Invocation modes

doxcavate has two modes. Pick from the user's prompt; ask once when
ambiguous.

## survey

Produces or refreshes the top-level doc index as a *doc plan*: an
ordered, prioritized list of which `how-it-works-*`, `learning-path-*`,
`runbook-*`, etc. should exist for this repo, each with a one-line
rationale and a `status: missing | drafted | verified` marker.

**No leaf docs are written in survey mode.** The output is the plan only.

## draft

Produces or updates one specific doc named or implied by the prompt.
Always reads the current top-level doc index (creating it if missing)
before drafting, so leaves link into the broader plan.

## Index path by storage mode

The index path is always resolved against the active storage mode (see
[layout-and-discovery](./layout-and-discovery.md)):

| Mode | Index path |
| --- | --- |
| `integrated` | repo-root `docs/index.md` (or whatever path discovery resolved) |
| `partial` | `~/.local/share/doxcavate/<repo-key>/docs/index.md` |
| `shadow` | `~/.local/share/doxcavate/<repo-key>/docs/index.md` |

In `partial`, the repo never receives an `index.md`. The doc plan,
glossary, and service map are still produced and persisted — just under
the shadow tree — so subsequent invocations can read them back.

## Routing

| Prompt shape | Mode |
| --- | --- |
| Names a target ("doxcavate the ingestion pipeline" / "doxcavate `runbook-deploy`") | draft |
| Asks for inventory or onboarding ("doxcavate this repo" / "what should be documented?") | survey |
| Ambiguous | ask once |

## Action checklist

- Survey: resolve the index path for the active mode, load the existing
  `index.md` (if any), inventory the repo, propose the doc plan, write
  it back to that path, stop.
- Draft: resolve the index path for the active mode, load `index.md`,
  identify the target, follow the production sources flow
  ([investigation-and-sources](./investigation-and-sources.md)), draft
  the doc using the matching template ([doc-kinds](./doc-kinds.md)),
  then run review ([review-methodology](./review-methodology.md)) before
  declaring done.

In `partial`, when drafting a leaf, never link from the leaf to a
shadow-located meta doc. Linking between leaves (relative paths inside
the repo) is fine.
