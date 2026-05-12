# Pragmatic Programmer citation catalog

Pragmatic Programmer principles enrich the `why` field of a finding when they cleanly apply. They never replace the Google principle as the primary tag and never act as a gate. The `pp` field on a finding (see [finding-record-template.md](../assets/finding-record-template.md)) carries the citation as a slug.

## When to cite

Cite a PP principle when:

- The finding's reasoning is more sharply named by the PP principle than by the Google principle alone.
- The PP citation adds explanatory power for the author (an experienced reader knows the principle and can act on it faster).
- The mapping is one-to-one, not a stretch. If the reasoning needs to be bent to fit a PP slug, omit `pp`.

Never invent a PP citation to fill the `pp` field. Omission is the correct default.

## Catalog

| Slug | Principle | Cleanest mapping to Google |
| --- | --- | --- |
| dry | Don't Repeat Yourself | design, complexity |
| orthogonality | Orthogonality / single reason to change | design, complexity |
| tracer-bullets | Tracer Bullets / end-to-end thin slice first | tests, design |
| broken-windows | Broken Windows / pay back small rot now | every-line, context |
| decoupling | Decoupling / Law of Demeter | design |
| etc | Easier-to-Change / design for change | design, complexity |
| program-by-coincidence | Programming By Coincidence / understand why it works | functionality, tests |
| dbc | Design By Contract / preconditions and postconditions | tests, functionality |
| ruthless-tests | Tests as deliberate adversaries | tests |
| crash-early | Crash Early / fail at the first sign of trouble | functionality |

## Render

In the local output `why` line, the PP citation appears as a parenthetical: `... (Pragmatic Programmer: orthogonality).` The slug is rendered as the human-readable name, not the slug itself.

## Hard rules

- `pp` is optional. Never required.
- One PP citation per finding maximum. If two would fit, choose the one that adds more explanatory power for the author.
- Never cite PP for triage-only principles (`small-cl`, `description`, `specialty`). Those have their own canonical sources (Google `small-cls.html`, `cl-descriptions.html`).
