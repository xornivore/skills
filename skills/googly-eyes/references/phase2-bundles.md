# Phase 2 bundles

Phase 2 dispatches based on the triage verdict:

- **small** → single-pass review covering all four bundles in one model context.
- **medium** or **large** → four parallel sub-agents, one per bundle. Main agent merges, dedupes, and ranks.

The four bundles below are the canonical division. Do not invent new bundles, do not split bundles, do not skip a bundle. Each principle belongs to exactly one bundle.

## Bundle 1: Architecture lens

**Principles:** design, complexity

**Sub-agent prompt template:**

> You are reviewing a diff for two principles: **design** and **complexity**, sourced from Google eng-practices `reviewer/looking-for.html`.
>
> Read the diff and the triage report. For each finding you file:
>
> - `principle` is exactly `design` or `complexity`.
> - `severity` follows the rules in `severity-labels.md` (file path: `../severity-labels.md`).
> - `why` cites the principle by name and gives the reasoning.
> - `suggestion` follows the verb form for the chosen severity.
>
> Also: surface one excellent thing in your scope if you find it (`severity: praise`).
>
> Output: a YAML list of finding records matching the schema in `assets/finding-record-template.md`. No prose around the list.

## Bundle 2: Correctness lens

**Principles:** tests, functionality

**Sub-agent prompt template:** same shape as Bundle 1, with `principle` constrained to `tests` or `functionality`.

`tests` covers tests-as-design: maintainability, true-fail behavior, no false positives, the test as a contract on the production code. `functionality` covers edge cases, concurrency, UI impact — but does not cross into bug-hunting-with-confidence-scoring; for `functionality` findings, the `why` must trace to a code-health concern, not "this might be a bug at runtime."

## Bundle 3: Readability lens

**Principles:** naming, comments, style, consistency

**Sub-agent prompt template:** same shape as Bundle 1, with `principle` constrained to `naming`, `comments`, `style`, or `consistency`.

`comments` enforces comments-as-why: a comment that describes what the code does is itself the finding (severity `nit`, suggestion "remove or rewrite as why").

`style` and `consistency` defer to repository style guides when present. The bundle does not re-implement a linter's job — file a `style` finding only when the style choice degrades readability beyond what a linter would mechanically flag.

## Bundle 4: Completeness lens

**Principles:** documentation, every-line, context

**Sub-agent prompt template:** same shape as Bundle 1, with `principle` constrained to `documentation`, `every-line`, or treated as the catch-all when no other principle fits cleanly.

`documentation` flags missing README / reference doc updates when the change requires them (per Google `reviewer/looking-for.html`). It does not write the docs — for that, point at the `doxcavate` skill via an `fyi` finding with `suggestion: "invoke doxcavate to draft the missing doc"`.

`every-line` is the catch-all for code that warrants comment but does not fit another principle. Use sparingly.

Context — the file-and-system framing — does the change degrade code health in adjacent code? Findings file at the location of the adjacent code, not the changed line, with `location.line` pointing at the affected context. Context findings use `principle: every-line` with the `why` clause naming the context concern.

## Merge and dedupe

After Phase 2 returns, the main agent:

1. Collects all findings from the bundles (parallel mode) or the single pass (small mode).
2. Adds the triage findings (`T-…` IDs) into the same pool.
3. Deduplicates per `(file, line ± 2, principle)`. On collision: keep highest severity; concatenate `why` clauses if non-redundant.
4. Bundles structural findings at function scope when they apply to the whole function (cite the function header line).
5. Ranks per [output-format.md](./output-format.md).
6. Caps per severity per [output-format.md](./output-format.md).
