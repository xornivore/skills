# Severity labels

The skill uses five severity labels, sourced from Google `reviewer/comments.html`. They control ranking order, posting behavior, and rendered prefix in comments.

## Labels

| Label | Meaning | Posted prefix | Posted event |
| --- | --- | --- | --- |
| required | Code health regression or correctness issue that must be addressed before merge. | (none — severity is implicit when blocking) | COMMENT (or REQUEST_CHANGES if user opts in) |
| optional | Good idea, would improve code health but not blocking. | `Optional:` or `Consider:` | COMMENT |
| nit | Minor preference, technically should be addressed but author may ignore. | `Nit:` | COMMENT |
| fyi | Informational only; no action expected. | `FYI:` | COMMENT |
| praise | Google "Good Things" — call out excellent design, exemplary tests. | `Praise:` | COMMENT |

## Verb forms in suggestions

Suggestion phrasing is derived from severity. The comment-style filter (see [posting-step.md](./posting-step.md)) enforces this on posted comments; the local renderer reflects the same shape.

| Severity | Suggestion verb form | Example |
| --- | --- | --- |
| required | Prescriptive ("Change X to Y") | "Move state validation before the token exchange." |
| optional | "Consider X" / "One option: X" | "Consider extracting the persistence step into a helper." |
| nit | "Prefer X" / "Could rename to X" | "Prefer `tokenStore` over `db` for the field name." |
| fyi | None (informational, no action) | (no suggestion) |
| praise | None (positive, no action) | (no suggestion) |

## Praise rule

When any qualifying praise candidate is found, at least one `praise` finding must be emitted. Phase-2 sub-agents are prompted with "and: surface one excellent thing in your scope if you find it." Praise findings render with `Praise:` prefix in posted comments and a `★` glyph in the local renderer (per [rich-rendering.md](./rich-rendering.md)).

## Ranking

Severity ranks ahead of principle: `required > optional > nit > fyi > praise`. Within severity, the principle priority order from [google-principles.md](./google-principles.md) applies as tiebreaker. See [output-format.md](./output-format.md) for the full ranking algorithm.

## Audit cues

- Every comment posted to GitHub from a non-`required` finding starts with the correct severity prefix (audit: grep posted body for one of `Optional:`, `Consider:`, `Nit:`, `FYI:`, `Praise:`).
- `required` comments do not carry a severity prefix (audit: grep posted body for `Required:` — any hit is a violation).
