# 👀 googly-eyes

Holistic Google-shaped code review for pull requests and local diffs. Audits against all ten principles from Google's [eng-practices code review guide][eng-practices], emits a ranked, principle-tagged finding list with rich local diff rendering, and optionally posts selected findings as a GitHub PR review.

This is the principled-review lens. It is not a bug filter — for the confidence-scored bug-hunt variant, use the `code-review` skill from the official Claude plugins marketplace.

## Install

```bash
npx skills add xornivore/skills@googly-eyes --agent claude-code -y
```

## How to use

Once installed, invoke by mentioning a PR or asking for a review:

- `googly-eyes #123`
- `googly-eyes https://github.com/owner/repo/pull/123`
- `googly-eyes` on a branch with an open PR (auto-detects)
- `googly-eyes --base main` to review the current branch's diff vs `main`, no PR required

For mechanics, see [SKILL.md](./SKILL.md). For principles and posting behavior, see the references under [references/](./references/).

## What it covers

All ten Google review principles, first-class:

design · complexity · tests · functionality · naming · comments · documentation · every-line · consistency · style

Plus the two CL-author concerns from the same guide:

small-cl (size and scope) · description (PR title and body quality)

Plus an advisory specialty flag (auth/crypto, concurrency, public API, perf paths) that recommends adding a specialty reviewer.

## What it does not cover

- Bug-hunting with confidence scoring — see the `code-review` skill.
- Observability gaps — see [observablip](../observablip/SKILL.md).
- Documentation drafting — see [doxcavate](../doxcavate/SKILL.md).
- Auto-merge or auto-approval — never.

## Differentiation from `code-review`

| | `code-review` | `googly-eyes` |
| --- | --- | --- |
| Frame | Bug hunter | Holistic Google-shaped review |
| Filter | ≥ 80 confidence; drops quality/tests/docs as noise | Nothing filtered out; severity-labeled by the model |
| Output | Single GitHub comment with bug list | Ranked finding list with principle tags + severity labels + rich local diff rendering; PR posting is opt-in |
| Architecture | Parallel agents, confidence scoring | Two-phase: triage → focused review (adaptive) |
| Author-side use | No — PR-only | Yes — works on local diffs pre-PR for self-review |
| Scope guidance | Doesn't address CL size | small-cl is first-class, surfaced in triage |

The two compose. `code-review` is the noise-filtered bug gate; `googly-eyes` is the principled-review lens.

[eng-practices]: https://google.github.io/eng-practices/review/
