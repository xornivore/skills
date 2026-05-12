# googly-eyes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `googly-eyes` Claude Code skill — a holistic PR reviewer that audits pull requests and local diffs against Google's eng-practices code review guide (all 10 principles), emits a ranked, principle-tagged finding list with rich local diff rendering, and optionally posts selected findings as a GitHub PR review.

**Architecture:** Skill packaged as Markdown content (no runtime code). One invocation surface (`googly-eyes` with optional `post` subcommand). `SKILL.md` is the lean entry point: target detection, two-phase routing (triage → focused review), hard rules, reference index. `references/` holds eight focused files — the principles catalog, severity vocabulary, triage heuristics, Phase-2 bundles, Pragmatic Programmer citation catalog, output schema, rich-rendering details, and posting-step composition — each loaded only at the pipeline step that needs it (stage-3 progressive disclosure). `assets/` holds two fill templates (triage report, finding record) loaded at emit time.

**Tech Stack:** Markdown only. Validation by `pnpm lint` (`markdownlint-cli2` already in repo) and `npx skills-ref validate` against the agentskills.io spec. Skill installed via `npx skills add xornivore/skills@googly-eyes --agent claude-code -y`. The skill is content for Claude Code, not executable code — bash snippets inside `SKILL.md` are executed by the agent at runtime against the user's environment (`gh`, `git`, terminal).

**Spec source:** `docs/superpowers/specs/2026-05-12-googly-eyes-design.md`. The plan lifts content from numbered spec sections — when a step says "transcribe spec section N.M," paste the spec prose and adapt to skill-instruction voice ("when invoked, do X" rather than "googly-eyes does X").

**Authoring rules:** Follow `skills/CLAUDE.md` (skill-authoring conventions for this repo, derived from the agentskills.io specification). Read it before starting Task 1. Doc voice and cross-reference rules in `docs/CLAUDE.md` apply to this plan file and to the per-skill `README.md`. The plan's structure (folders, file naming, frontmatter shape) is already aligned to those rules.

---

## Working environment

- Branch: `feat/googly-eyes-skill` (already created from `main`).
- Worktree: `.worktrees/googly-eyes-skill/`.
- All commands run from the worktree root.
- `pnpm install` has already run for sibling worktrees; husky is active. Run `pnpm install` once at the start of Task 1 if `node_modules/` is missing in this worktree (worktrees share `.git` but not `node_modules`).

## Target file structure

```text
skills/googly-eyes/
├── SKILL.md
├── README.md
├── references/
│   ├── google-principles.md
│   ├── severity-labels.md
│   ├── triage-heuristics.md
│   ├── phase2-bundles.md
│   ├── pragmatic-citations.md
│   ├── output-format.md
│   ├── rich-rendering.md
│   └── posting-step.md
├── assets/
│   ├── triage-report-template.md
│   └── finding-record-template.md
└── tests/
    └── fixtures/
        ├── small-clean.diff
        ├── large-mixed.diff
        ├── weak-description.diff
        └── security-path.diff
```

Plus one modification:

- `README.md` (top-level) — move the `googly-eyes` row from the "In design" subsection to the active Skills table.

## Voice rules (apply to all skill files)

- Imperative: "when invoked, do X" — not "googly-eyes does X." Per `skills/CLAUDE.md` section 3.1.
- Strip hedge tokens (`may`, `might`, `could`, `ideally`, `we suggest`, `perhaps`).
- Replace `should` with `must` / `always` for non-negotiable rules.
- Each standalone rule paired with a correct example and a wrong example, per `skills/CLAUDE.md` section 3.2.
- Mechanical rules carry an audit cue, per `skills/CLAUDE.md` section 3.3.
- No `§`. Cross-references use plain Markdown anchor links or plain prose, per `docs/CLAUDE.md`.
- No angle brackets in any frontmatter value, per `skills/CLAUDE.md` section 2.

## Phase 0 — Repo prep

(No prep tasks — worktree, branch, and baseline already in place.)

---

## Phase 1 — Scaffold and templates

### Task 1: Scaffold directory tree and asset templates

**Files:**

- Create: `skills/googly-eyes/` (plus `references/`, `assets/`, `tests/fixtures/` subdirs)
- Create: `skills/googly-eyes/assets/triage-report-template.md`
- Create: `skills/googly-eyes/assets/finding-record-template.md`

**Source spec sections:** 4 (triage), 5 (finding schema), 9 (file layout).

- [ ] **Step 1: Ensure node_modules is present in the worktree**

```bash
[ -d node_modules ] || pnpm install
```

Expected: either no output (already present) or pnpm completes; husky reinstalls hooks.

- [ ] **Step 2: Create the directory tree**

```bash
mkdir -p skills/googly-eyes/references skills/googly-eyes/assets skills/googly-eyes/tests/fixtures
```

- [ ] **Step 3: Verify directories exist and are empty**

```bash
find skills/googly-eyes -type d
```

Expected:

```text
skills/googly-eyes
skills/googly-eyes/references
skills/googly-eyes/assets
skills/googly-eyes/tests
skills/googly-eyes/tests/fixtures
```

- [ ] **Step 4: Write `assets/triage-report-template.md`**

The triage report is the structured handoff from Phase 1 to Phase 2 and the visible top-of-output block. Write the file with this exact content:

````markdown
# Triage report template

Filled at the end of Phase 1 (triage). Substitute bracketed placeholders with values produced by the triage pass. Render the filled block at the top of the user-facing output, before the file map and findings.

```text
Triage
------
Target:       [PR #N | local diff vs <base>]
Commit:       [short SHA]
Files:        [F file(s)]
LOC:          +[added] / -[removed]

Size:         [small | medium | large]
              [N LOC, F files — small ≤ 100 LOC and ≤ 5 files;
               medium ≤ 400 LOC; large > 400 LOC or > 15 files]

Scope:        [single | mixed]
              [if mixed, name the mixed concerns, e.g. "refactor + feature"]

Description:  [strong | weak | n/a-for-local-diff]
              [one-line verdict — what is missing or what is good]

Specialty:    [none | listed]
              [comma-separated list of advisory triggers, e.g.
               "auth/crypto path, concurrency primitive"]
```

Hard rules:

- The triage block is rendered verbatim from this template — no reordering, no additional rows.
- `Size`, `Scope`, `Description`, `Specialty` each correspond to one Phase-1 finding when the verdict is anything other than green (small / single / strong / none). Those findings are filed by triage and not re-derived in Phase 2.
- When the target is a local diff with no open PR, `Description` is `n/a-for-local-diff`; the description-quality check is skipped.
````

- [ ] **Step 5: Write `assets/finding-record-template.md`**

The finding record is the unit of output. Every finding produced by triage or Phase 2 conforms to this shape. Write the file with this exact content:

````markdown
# Finding record template

Filled per finding at the emit step. Every finding — triage or Phase-2 — conforms to this shape. The fields are listed in source-of-truth order; the local renderer presents them in display order (severity label, location, why, suggestion, hunk).

```yaml
- id:          <stable id, e.g. "F-001"; assigned by main agent after merge/dedupe>
  principle:   <one of: design | complexity | tests | functionality | naming |
                comments | documentation | every-line | style | consistency |
                small-cl | description | specialty>
  severity:    <one of: required | optional | nit | fyi | praise>
  location:
    file:      <repo-relative path>
    line:      <single line number, or range "L1-L2" for structural findings>
  observation: <factual: what in the code triggered this. No evaluation here.>
  why:         <reasoning: cites the Google principle by name. May cite one
                Pragmatic Programmer principle by name when it cleanly applies.
                Begins with "Because" or "This".>
  suggestion:  <preferred direction, or empty when the author should decide.
                Render verb form depends on severity (see severity-labels.md).>
  pp:          <optional. Pragmatic Programmer principle slug, e.g.
                "orthogonality", "dry", "broken-windows". Omit when no clean
                mapping. See pragmatic-citations.md.>
```

Hard rules:

- A finding without `principle` is a bug — reject it before emit.
- A finding without `why` is a bug — reject it before emit.
- `pp` is optional and may be omitted. Never invent a PP citation to fill the field.
- `observation` must be factual. Evaluative language ("badly written", "ugly") goes nowhere; the evaluation belongs in `why` and is grounded in the principle.
````

- [ ] **Step 6: Validate templates lint clean**

```bash
pnpm lint
```

Expected: exits 0. Markdownlint passes on both new files.

- [ ] **Step 7: Audit templates against required content**

```bash
grep -c "principle:" skills/googly-eyes/assets/finding-record-template.md
grep -c "severity:" skills/googly-eyes/assets/finding-record-template.md
grep -c "Triage" skills/googly-eyes/assets/triage-report-template.md
```

Expected: each grep returns at least 1.

- [ ] **Step 8: Commit**

```bash
git add skills/googly-eyes/assets/
git commit -m "feat(googly-eyes): scaffold skill dir and asset templates"
```

---

## Phase 2 — Reference files

Each reference is a focused, stage-3 document loaded at one specific step in the SKILL.md pipeline. Keep each file under 200 lines where possible. Write in declarative voice (descriptions of rules + tables), not skill-body imperatives — the SKILL.md body issues the orders; the references inform the action.

### Task 2: Write `references/google-principles.md`

**Files:**

- Create: `skills/googly-eyes/references/google-principles.md`

**Source spec sections:** 2 (differentiation), 4.2 (Phase 2 bundles), 7.1 (ranking, principle priority).

This is the load-bearing reference — it carries verbatim Google guidance so the model has principle definitions when grading findings. Single file (not 10 files) because the principles are cross-referenced in Google's own structure.

- [ ] **Step 1: Write the file**

Structure (write all sections; content sketched here, see source URLs for verbatim quotes):

````markdown
# Google code review principles

Canonical source: [Google eng-practices](https://google.github.io/eng-practices/review/). This reference holds the ten principles the skill grades against, plus the priority order used by ranking, plus when each principle applies.

## Priority order

For ranking within a severity bucket, principles are ordered by Google's own emphasis ("the most important thing to cover in a review is the overall design of the CL"):

1. design
2. complexity
3. tests
4. functionality
5. naming
6. comments
7. documentation
8. every-line
9. consistency
10. style

This order is the tiebreaker used by [output-format.md](./output-format.md). It is not a filter — every principle is first-class.

## 1. Design

Quote from `reviewer/looking-for.html`: "The most important thing to cover in a review is the overall design of the CL."

A `design` finding is filed when:

- The change does not fit the codebase or the library it lives in.
- The change introduces a system boundary that should not exist, or crosses a boundary it should not.
- The change adds a dependency or coupling that complicates future change.
- The timing of the change is wrong (e.g., adds API surface that the system is not ready to support).

[continue this section pattern through all 10 principles — for each, give a verbatim Google quote, a "filed when" list, and a 1-2 line note on cheapest evidence to point to]

## 2. Complexity

Quote from `reviewer/looking-for.html`: "Is the CL more complex than it should be? ... Developers are likely to introduce bugs when they try to call or modify this code."

A `complexity` finding is filed when:
[...]

## 3. Tests

[...]

## 4. Functionality

[...]

## 5. Naming

[...]

## 6. Comments

[...]

## 7. Documentation

[...]

## 8. Every line

[...]

## 9. Consistency

[...]

## 10. Style

[...]

## Triage-only principles

These three principles are filed only by Phase 1 (triage), never by Phase 2:

- **small-cl** — sourced from `developer/small-cls.html`. Verdict from triage size scoring; severity scales with deviation. See [triage-heuristics.md](./triage-heuristics.md).
- **description** — sourced from `developer/cl-descriptions.html`. Verdict from triage description-quality check. Skipped for local-diff target.
- **specialty** — advisory only. Never `required`. See [triage-heuristics.md](./triage-heuristics.md) for trigger patterns.
````

Source URLs to quote verbatim from (one quote per principle):

- design, complexity, tests, naming, comments, style, consistency, documentation, every-line, context, good-things → `reviewer/looking-for.html`
- functionality → `reviewer/looking-for.html`
- standard / "code health" framing → `reviewer/standard.html`
- small-cl → `developer/small-cls.html`
- description → `developer/cl-descriptions.html`

- [ ] **Step 2: Validate file is well-formed**

```bash
pnpm lint
```

Expected: exits 0.

- [ ] **Step 3: Audit all 10 principles are present**

```bash
for p in design complexity tests functionality naming comments documentation every-line consistency style; do
  grep -q "^## .*${p}" skills/googly-eyes/references/google-principles.md \
    || echo "MISSING: $p"
done
```

Expected: no output (all 10 present).

- [ ] **Step 4: Audit no angle brackets in body content**

```bash
grep -nE "[<>]" skills/googly-eyes/references/google-principles.md | grep -v '```' | head
```

Expected: no output, or only matches inside fenced code blocks (placeholder syntax in YAML examples).

- [ ] **Step 5: Commit**

```bash
git add skills/googly-eyes/references/google-principles.md
git commit -m "feat(googly-eyes): add Google principles reference"
```

### Task 3: Write `references/severity-labels.md`

**Files:**

- Create: `skills/googly-eyes/references/severity-labels.md`

**Source spec sections:** 6 (severity vocabulary), 8.5 (comment-style enforcement).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
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
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "| required |" skills/googly-eyes/references/severity-labels.md
grep -c "| praise |" skills/googly-eyes/references/severity-labels.md
```

Expected: lint clean, each grep returns at least 1.

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/severity-labels.md
git commit -m "feat(googly-eyes): add severity labels reference"
```

### Task 4: Write `references/triage-heuristics.md`

**Files:**

- Create: `skills/googly-eyes/references/triage-heuristics.md`

**Source spec sections:** 4.1 (Phase 1 triage), 1.1 (branding — for the report header).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Triage heuristics

Phase 1 (triage) is one model pass that produces the structured report consumed by Phase 2 and rendered at the top of user-facing output. Triage is cheap (no per-line review) and always runs first.

## Checks

### CL size scoring

Compute three numbers from the diff:

- `loc_added`: lines added (post-image).
- `loc_removed`: lines removed (pre-image).
- `files_touched`: count of distinct files changed.

Verdict ladder, in order — first match wins:

| Verdict | Threshold |
| --- | --- |
| small  | `loc_added + loc_removed ≤ 100` AND `files_touched ≤ 5` |
| medium | `loc_added + loc_removed ≤ 400` AND `files_touched ≤ 15` |
| large  | otherwise |

A `small-cl` finding is filed only when verdict is `medium` or `large`. Severity scales with deviation:

- medium → `optional` severity
- large → `required` severity

Suggestion field cites split strategy from Google `developer/small-cls.html`: stacking, by-files, horizontal, vertical.

### Scope-mix detection

Scan the file map for two patterns:

- **Refactor + feature**: file renames or move-without-modify in the same CL as added or changed callsites elsewhere.
- **Mixed concerns**: changes in two or more orthogonal subsystems (e.g., `pkg/auth/*` AND `pkg/billing/*`).

If detected, file a `small-cl` finding (yes — scope-mix is a small-cls concern per Google) with `severity = optional`, and a `suggestion` that points at "vertical split" from `developer/small-cls.html`.

### CL description quality

Skipped when target is a local diff with no PR. When target is a PR, evaluate PR title + body against Google `developer/cl-descriptions.html`:

| Defect | Evidence | Severity |
| --- | --- | --- |
| First line is not imperative | Title starts with gerund ("Adding…", "Fixing…") or noun ("Improvements to…") | nit |
| First line is an anti-pattern | Matches one of: `Fix bug`, `Fix build`, `Add patch`, `Moving code from A to B`, `Phase 1`, `Add convenience functions`, `kill weird URLs` | required |
| Body missing | PR body is empty or single line | optional |
| Body explains "what" without "why" | No clause that gives the reasoning, motivation, or trade-off | optional |
| Body contains relevant context | Bug numbers, benchmark results, design doc links | (praise candidate) |

### Specialty triggers

Advisory only. Never `required`. Severity is always `fyi`. Detect by path or keyword in the diff:

| Trigger | Patterns |
| --- | --- |
| auth / crypto | paths matching `(auth|oauth|crypt|jwt|session|secret)` (case-insensitive) |
| concurrency | added or changed `(sync\.|mutex|channel|goroutine|async|await|atomic\.|Lock\(|Unlock\()` |
| public API | changes to exported symbols (capitalized identifiers in Go, exported in package.json/index, etc.) |
| perf-critical | path matches `(hot|bench|perf|cache)` or file annotated `// PERF` |

A specialty finding's `suggestion` names the kind of reviewer to add ("consider a security reviewer for these auth changes").

## Triage emit format

Triage writes one [triage-report-template.md](../assets/triage-report-template.md)-shaped block PLUS one finding-record per non-green verdict (size > small, scope = mixed, description weak, any specialty). The findings get IDs `T-1`, `T-2`, … to distinguish from Phase-2 IDs (`F-1`, `F-2`, …).

## Hard rules

- Triage never re-derives size or scope-mix in Phase 2. Phase 2 reads the triage report.
- Triage never grades any of the ten Google principles other than `small-cl` and `description`. Those are Phase 2's job.
- When triage emits a `large` size finding at `required` severity, Phase 2 still runs. The CL is reviewed; the small-cl finding leads the output.
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "small-cl" skills/googly-eyes/references/triage-heuristics.md
grep -c "scope-mix" skills/googly-eyes/references/triage-heuristics.md
grep -c "specialty" skills/googly-eyes/references/triage-heuristics.md
```

Expected: lint clean, each grep returns at least 1.

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/triage-heuristics.md
git commit -m "feat(googly-eyes): add triage heuristics reference"
```

### Task 5: Write `references/phase2-bundles.md`

**Files:**

- Create: `skills/googly-eyes/references/phase2-bundles.md`

**Source spec sections:** 4.2 (Phase 2 focused review), 6 (severity vocabulary).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
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

**Sub-agent prompt template:**

[same shape as Bundle 1, principles substituted]

`tests` covers tests-as-design: maintainability, true-fail behavior, no false positives, the test as a contract on the production code. `functionality` covers edge cases, concurrency, UI impact — but does not cross into bug-hunting-with-confidence-scoring; for `functionality` findings, the `why` must trace to a code-health concern, not "this might be a bug at runtime."

## Bundle 3: Readability lens

**Principles:** naming, comments, style, consistency

**Sub-agent prompt template:**

[same shape; principles substituted]

`comments` enforces comments-as-why: a comment that describes what the code does is itself the finding (severity `nit`, suggestion "remove or rewrite as why").

`style` and `consistency` defer to repository style guides when present. The bundle does not re-implement a linter's job — file a `style` finding only when the style choice degrades readability beyond what a linter would mechanically flag.

## Bundle 4: Completeness lens

**Principles:** documentation, every-line, context

**Sub-agent prompt template:**

[same shape; principles substituted]

`documentation` flags missing README / reference doc updates when the change requires them (per Google `reviewer/looking-for.html`). It does not write the docs — for that, point at the `doxcavate` skill via an `fyi` finding with `suggestion: "invoke doxcavate to draft the missing doc"`.

`every-line` is the catch-all for code that warrants comment but does not fit another principle. Use sparingly.

`context` is the file-and-system framing — does the change degrade code health in adjacent code? Findings file at the location of the adjacent code, not the changed line, with `location.line` pointing at the affected context.

## Merge and dedupe

After Phase 2 returns, the main agent:

1. Collects all findings from the bundles (parallel mode) or the single pass (small mode).
2. Adds the triage findings (`T-…` IDs) into the same pool.
3. Deduplicates per `(file, line ± 2, principle)`. On collision: keep highest severity; concatenate `why` clauses if non-redundant.
4. Bundles structural findings at function scope when they apply to the whole function (cite the function header line).
5. Ranks per [output-format.md](./output-format.md).
6. Caps per severity per [output-format.md](./output-format.md).
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "## Bundle " skills/googly-eyes/references/phase2-bundles.md
```

Expected: lint clean, grep returns 4 (one per bundle).

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/phase2-bundles.md
git commit -m "feat(googly-eyes): add Phase 2 bundles reference"
```

### Task 6: Write `references/pragmatic-citations.md`

**Files:**

- Create: `skills/googly-eyes/references/pragmatic-citations.md`

**Source spec sections:** 1 (PP as reasoning vocabulary), 5 (finding schema, `pp` field).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Pragmatic Programmer citation catalog

Pragmatic Programmer principles enrich the `why` field of a finding when they cleanly apply. They never replace the Google principle as the primary tag and never act as a gate. The `pp` field on a finding (see `finding-record-template.md`) carries the citation as a slug.

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
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "^| " skills/googly-eyes/references/pragmatic-citations.md
```

Expected: lint clean, grep returns at least 10 (catalog rows + header).

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/pragmatic-citations.md
git commit -m "feat(googly-eyes): add Pragmatic Programmer citation catalog"
```

### Task 7: Write `references/output-format.md`

**Files:**

- Create: `skills/googly-eyes/references/output-format.md`

**Source spec sections:** 5 (schema), 7.1-7.4 (ranking, dedupe, caps, file map).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Output format

This reference defines: finding-record schema, ranking algorithm, dedupe rules, bounded output, file-map block, top-of-output structure.

## Finding record schema

Source: [assets/finding-record-template.md](../assets/finding-record-template.md). Every finding — triage or Phase-2 — conforms to that template.

## Ranking algorithm

Two-key sort, descending:

1. Severity: required > optional > nit > fyi > praise.
2. Principle priority (tiebreaker within severity):
   `design > complexity > tests > functionality > naming > comments > documentation > every-line > consistency > style`.
3. Final tiebreaker: file (alphabetical) then `location.line` ascending.

Triage findings (`small-cl`, `description`, `specialty`) do not enter the principle-ranked list — they render in the triage block at the top of output, in the order produced by [triage-heuristics.md](./triage-heuristics.md).

## Dedupe

After all findings are collected:

- Group by `(file, line ± 2, principle)`. On collision, keep the highest-severity record; concatenate non-redundant `why` clauses with `; ` separator; preserve at most one `suggestion` (highest severity wins; on tie, longer suggestion wins).
- Structural findings ("this function is over-complex", "this type hierarchy is too deep") bundle at function scope. The bundled finding's `location.line` is a range starting at the function header line.

## Bounded output

Per-severity caps, applied after dedupe:

| Severity | Cap |
| --- | --- |
| required | 20 |
| optional | 15 |
| nit | 10 |
| fyi | 5 |
| praise | unbounded |

When a severity is capped, append at the bottom of that section in the rendered output:

`N more <severity> findings suppressed; consider splitting this CL for thorough review`

(The suppression message reinforces small-cl when the CL is the cause.)

## File map

Render the file map immediately after the triage block, before the findings. Format:

```text
<repo-relative file path>  <R>R · <O>O · <N>N · <F>F · <P>P  (+<added>/-<removed>)
```

One row per file. Columns aligned. Sort by total finding count descending, then by file path ascending.

## Top-of-output structure

```text
👀 googly-eyes review — <target ref> @ <short SHA>

<triage block from triage-report-template.md>

<file map>

## Required (N)
<finding records in display order>

## Optional (M)
<...>

## Nit / FYI / Praise
<...>

## Next step
<one of:
  - Post selected findings to PR #<N> — run: googly-eyes post
  - Split this CL before review — see Triage
  - Iterate on findings locally — re-run after edits>
```

## Audit cues

- The header line literally starts with `👀 googly-eyes review —` (audit: regex on rendered output).
- No `required` finding is emitted without a `suggestion` (audit: scan emitted YAML).
- No finding is emitted whose `principle` is outside the allowed set (audit: scan emitted YAML against the list in [google-principles.md](./google-principles.md) plus `small-cl`, `description`, `specialty`).
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "## " skills/googly-eyes/references/output-format.md
```

Expected: lint clean, grep returns at least 6 (one per section).

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/output-format.md
git commit -m "feat(googly-eyes): add output format reference"
```

### Task 8: Write `references/rich-rendering.md`

**Files:**

- Create: `skills/googly-eyes/references/rich-rendering.md`

**Source spec sections:** 7.5-7.8 (per-finding diff context, color, verbosity, implementation notes).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Rich rendering

This reference covers ANSI/TTY detection, per-finding hunk slicing, color palette, and verbosity modes. The renderer is composed inline by the agent — no external dependency.

## TTY and color detection

Compute once at the start of the render step:

```bash
if [ -t 1 ] && [ -z "$NO_COLOR" ]; then
  COLOR=on
else
  COLOR=off
fi
```

- `COLOR=on`: emit ANSI escapes.
- `COLOR=off`: emit plain ASCII. Same content, no escape codes.

`NO_COLOR` honors <https://no-color.org>.

## Palette

| Element | ANSI | Fallback (no color) |
| --- | --- | --- |
| Severity REQUIRED | bold red (`\033[1;31m`) | `REQUIRED ·` |
| Severity OPTIONAL | yellow (`\033[33m`) | `OPTIONAL ·` |
| Severity NIT | cyan (`\033[36m`) | `NIT ·` |
| Severity FYI | dim (`\033[2m`) | `FYI ·` |
| Severity PRAISE | green (`\033[32m`) + `★` glyph | `PRAISE ★ ·` |
| Diff `+` line | green | `+` prefix preserved |
| Diff `-` line | red | `-` prefix preserved |
| File path | bold | (none) |
| Principle | dim | (none) |
| Separator rule | dim | `─` U+2500 repeated to terminal width or 73 |

## Verbosity modes

| Flag | Renders |
| --- | --- |
| `--compact` | Triage block + file map + flat finding list (severity, principle, location, why). No hunks. |
| (default) | Triage block + file map + per-finding hunk view (5 lines of post-image context, with `+`/`-` markers preserved). |
| `--detailed` | All of default, plus full file diff inline. Findings interleaved at their line. |

Default is the default. `--compact` is for very large CLs where hunks would bloat the output; `--detailed` is for thorough single-file review.

## Per-finding hunk

The hunk is sliced from the diff already in memory (no extra `git` call). Show three lines of context above the finding's first line and one line below, with the finding's line range marked. Use `+` and `-` from the post-image diff hunk.

Example (default verbosity, color off):

```text
─────────────────────────────────────────────────────────────────────────
REQUIRED · design                                        finding #1 of 4
pkg/auth/oauth.go:42-58
─────────────────────────────────────────────────────────────────────────
Why:  This function handles callback parsing, token exchange, AND
      database persistence in one body. Three unrelated reasons to
      change. Violates orthogonality (Pragmatic Programmer).

Suggestion: split into parseCallback, exchangeCode, persistToken.

   40 │   func (s *Server) Callback(w http.ResponseWriter, r *http.Request) {
   41 │       ctx := r.Context()
   42 │ +     code := r.URL.Query().Get("code")
   43 │ +     state := r.URL.Query().Get("state")
   ...
   58 │   }
─────────────────────────────────────────────────────────────────────────
```

## Line numbering

Post-image line numbers (the new file's numbers), matching what GitHub shows. Structural findings show the function header line as anchor and the range spans the function body.

## Findings outside the diff

For the rare case where a finding's `location.line` falls outside any diff hunk (context-only files flagged for a deletion concern in an adjacent file), render a 5-line `git show <SHA>:<file>` excerpt labeled `(context-only)` in place of the hunk.

## Audit cues

- The renderer never emits escape codes when `NO_COLOR` is set (audit: pipe output through `cat -v | grep ESC` and confirm empty).
- Default mode includes one hunk per finding (audit: count `─{60,}` rules and finding records; counts match).
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "COLOR=" skills/googly-eyes/references/rich-rendering.md
grep -c "compact\|detailed" skills/googly-eyes/references/rich-rendering.md
```

Expected: lint clean, each grep returns at least 1.

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/rich-rendering.md
git commit -m "feat(googly-eyes): add rich rendering reference"
```

### Task 9: Write `references/posting-step.md`

**Files:**

- Create: `skills/googly-eyes/references/posting-step.md`

**Source spec sections:** 8.1-8.8 (invocation, selection, composition, idempotency, comment style, summary body, event type, failure modes).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Posting step

The post step is invoked separately from review. It is the only writing step in the skill — review is read-only.

## Invocation

- `googly-eyes post` — promote findings from the most recent in-session review.
- `googly-eyes post --from <file>` — promote from a saved review output file (cross-session use).

## Selection

| Flag | Posts |
| --- | --- |
| (default) | all `required` findings only |
| `--include optional` | adds `optional` |
| `--include nit,fyi,praise` | adds the named severities |
| `--only <ids>` | exactly the listed finding IDs |
| `--exclude <ids>` | every selected severity minus excluded IDs |

When the selection includes any `required` or `optional`, prompt once before composing the review:

> "You have N praise findings available — include them?"

## Composition

`gh pr review --comment` does not support multi-inline reviews natively. Use the GitHub API directly:

```bash
gh api repos/<owner>/<repo>/pulls/<pr>/reviews \
  --method POST \
  --field event=COMMENT \
  --field body="$SUMMARY" \
  --field "comments=$COMMENTS_JSON"
```

Where:

- `$SUMMARY` is the rendered summary body (see [Summary body](#summary-body) below).
- `$COMMENTS_JSON` is a JSON array of `{path, line, body}` objects.

One atomic review per invocation. Never split into multiple review POSTs.

## Idempotency

Before posting, fetch existing reviews:

```bash
gh pr view <pr> --json reviews -q '.reviews[].body' | grep -F '<!-- googly-eyes:v1 -->'
```

If a match is found, refuse to post unless `--force` is set. The HTML marker in the summary body is how repeat runs detect "we already reviewed this."

## Comment-style filter

Every comment is run through this filter before the body is sent. Reject and rewrite:

| Rule | Reject pattern | Rewrite |
| --- | --- | --- |
| No second-person blame | `^(why did you|you should|you forgot|you missed)` | Subject-on-code: "the concurrency model here…", "this function adds complexity…" |
| Every comment has a `why` | Body lacks "Because" or "This" clause | Block the comment — finding is malformed |
| Prefer pointing-out over prescribing (non-required) | Imperative verbs in non-required findings ("Change X", "Move Y") | "Consider X" / "One option: Y" |
| Severity prefix | Non-required body missing prefix | Prepend `Optional:` / `Consider:` / `Nit:` / `FYI:` / `Praise:` |

## Summary body

```text
👀 googly-eyes review — <commit SHA>

Triage: size=<small|medium|large>, scope=<single|mixed>, description=<strong|weak>

Required: N  ·  Optional: M  ·  Nit: K  ·  FYI: J  ·  Praise: P
Filed below as inline comments.

<!-- googly-eyes:v1 -->
```

## Event type

Default `event=COMMENT`. User opts into `event=REQUEST_CHANGES` with `--request-changes`, valid only if at least one `required` finding is in the selection. Per Google `reviewer/pushback.html`: improving code health happens in small steps; default to the lighter event.

## Failure modes

| Condition | Behavior |
| --- | --- |
| `gh` not authenticated | Print rendered comments and summary to stdout; instruct user to authenticate (`gh auth login`) and re-run. |
| PR closed | Refuse to post; print finding list as terminal output. |
| PR authored by current user (self-review) | Allow (Google practice); add `--self-review` advisory to summary. |
| Finding line missing from PR diff (file changed since review) | Fall back to file-level comment with `(originally @ L<N>)` in body. |
| Local-diff mode, no open PR | Post step unavailable; skill exits cleanly after finding list. |

## Audit cues

- No posted comment body starts with a second-person phrase (audit: regex `^(Why did you|You should|You forgot|You missed)` over composed comments).
- Every non-`required` comment body starts with one of the five severity prefixes (audit: regex `^(Optional|Consider|Nit|FYI|Praise):` over non-required comment bodies).
- Every composed summary contains the idempotency marker `<!-- googly-eyes:v1 -->` (audit: grep the summary body before POST).
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "## " skills/googly-eyes/references/posting-step.md
```

Expected: lint clean, grep returns at least 8.

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/references/posting-step.md
git commit -m "feat(googly-eyes): add posting step reference"
```

---

## Phase 3 — SKILL.md and per-skill README

### Task 10: Write `SKILL.md` (the entry point)

**Files:**

- Create: `skills/googly-eyes/SKILL.md`

**Source spec sections:** all — SKILL.md is the routing surface that loads the references at their action steps.

The body must stay under 500 lines per `skills/CLAUDE.md`. Use the imperative voice and pair each rule with a correct / wrong example per `skills/CLAUDE.md` section 3.2.

- [ ] **Step 1: Write the frontmatter**

```yaml
---
name: googly-eyes
description: Reviews pull requests and local diffs against Google's eng-practices code review guide (design, complexity, tests, naming, comments, style, consistency, documentation, every-line, context) and emits a ranked, principle-tagged finding list with rich local diff rendering. Optional follow-up step posts selected findings as a GitHub PR review. Invoke when the user says "googly-eyes this PR", "review by the canon", "principled code review", "Google-style review", "review this CL", or pastes a PR URL and asks for a code review. 👀
license: MIT
compatibility: Requires git and gh; PR-mode requires authenticated GitHub access. Terminal rendering optimized for ANSI-capable TTYs.
---
```

Audit cues:

- Folder name = name field. (`basename $(dirname SKILL.md)` is `googly-eyes`.)
- No `<` or `>` characters anywhere in the frontmatter values.

- [ ] **Step 2: Write the body**

The body sections, in order:

````markdown
# googly-eyes

👀 Holistic Google-shaped code review. Emits a ranked, principle-tagged finding list with rich local diff rendering. Optional `post` step files selected findings as a GitHub PR review.

## Install

```bash
npx skills add xornivore/skills@googly-eyes --agent claude-code -y
```

## When to invoke

Trigger phrases the user types or says:

- "googly-eyes this PR"
- "googly-eyes #123" / "googly-eyes <pr-url>"
- "review by the canon"
- "principled code review"
- "Google-style review"
- "review this CL"
- After pasting a PR URL: "code review please"

Do not invoke for:

- Bug-hunting with confidence scoring — that is the `code-review` skill's job.
- Observability gaps — that is `observablip`'s job.
- Drafting documentation — that is `doxcavate`'s job.

## Pipeline (the order is fixed)

1. **Detect target.** See [Target detection](#target-detection) below.
2. **Phase 1 — Triage.** Always runs. See [triage-heuristics.md](./references/triage-heuristics.md) and emit a triage block per [assets/triage-report-template.md](./assets/triage-report-template.md).
3. **Phase 2 — Focused review.** Dispatch per triage verdict. See [phase2-bundles.md](./references/phase2-bundles.md).
4. **Merge, dedupe, rank.** See [output-format.md](./references/output-format.md).
5. **Render.** See [rich-rendering.md](./references/rich-rendering.md).
6. **(Optional) Post.** Only when the user explicitly invokes `googly-eyes post`. See [posting-step.md](./references/posting-step.md).

## Target detection

Three cases, evaluated in order — first match wins:

1. **Explicit PR ref.** If the invocation includes `#<N>` or a `https://github.com/<owner>/<repo>/pull/<N>` URL, fetch:

   ```bash
   gh pr diff <N>
   gh pr view <N> --json title,body,author,number,headRefOid,baseRefName,url
   ```

2. **Branch with open PR.** If `git branch --show-current` returns a branch and `gh pr view --json number 2>/dev/null` succeeds, treat as case 1 with that PR number.

3. **No PR.** Diff current branch against base (default `main`, override with `--base <ref>`):

   ```bash
   BASE=${BASE_OVERRIDE:-main}
   git diff "$BASE"...HEAD
   ```

   Replace PR-title and PR-body inputs with the branch's commit-message log:

   ```bash
   git log "$BASE"..HEAD --pretty=format:"%s%n%n%b%n---"
   ```

Hard rules:

- Never silently switch modes mid-run. If both an explicit PR ref and a local diff are detectable, the explicit ref wins.
- If `gh` is not authenticated and a PR target is required, exit with a clear error pointing at `gh auth login`. Do not fall back to local diff in that case — the user asked for a PR review.

Correct example:

> User: "googly-eyes #42"
> Skill: fetches PR #42, runs Phase 1 + Phase 2, renders output with `Target: PR #42`.

Wrong example:

> User: "googly-eyes #42"
> Skill: `gh` is not authenticated; falls back to local diff and renders output with `Target: local diff vs main`. — Violates "never silently switch modes."

## Phase 1 — Triage

Run one pass producing the triage report. See [triage-heuristics.md](./references/triage-heuristics.md) for the size, scope-mix, description-quality, and specialty checks. Emit:

- One filled triage block from [assets/triage-report-template.md](./assets/triage-report-template.md).
- Zero or more finding records (T-1, T-2, …) for non-green verdicts, per [assets/finding-record-template.md](./assets/finding-record-template.md).

Hand the filled triage block and its findings to Phase 2 as structured input.

## Phase 2 — Focused review

Decision rule on Phase-2 dispatch (read this from the triage size verdict):

- `small` → single-pass review. Run all four bundles' prompt content in one model context.
- `medium` or `large` → dispatch four parallel sub-agents, one per bundle, using the prompt templates in [phase2-bundles.md](./references/phase2-bundles.md).

Each sub-agent (or the single-pass run) returns YAML finding records matching [assets/finding-record-template.md](./assets/finding-record-template.md).

## Merge, dedupe, rank

After Phase 2 returns:

1. Pool triage findings (`T-…`) and Phase-2 findings (`F-…`).
2. Dedupe per `(file, line ± 2, principle)`. Keep highest severity; concatenate non-redundant `why` clauses.
3. Rank per [output-format.md](./references/output-format.md).
4. Apply per-severity caps.
5. Render per [rich-rendering.md](./references/rich-rendering.md).

## Output

The rendered output has six blocks, in this order:

1. Header line: `👀 googly-eyes review — <target> @ <SHA>`
2. Triage block (from triage-report-template.md)
3. File map (per output-format.md)
4. `## Required (N)` followed by required finding records
5. `## Optional (M)`, `## Nit (K)`, `## FYI (J)`, `## Praise (P)` in that order
6. `## Next step` — one of: post selected findings, split CL, iterate locally

## Hard rules

1. **Never post without explicit user confirmation.** Render every comment exactly as it will appear on GitHub. Wait for explicit approval before any `gh` write. No batch auto-post.

   Correct: "Here are the N comments I will post. Reply `confirm` to send."
   Wrong: posting immediately after composing the review body.

2. **Never invent code locations.** Every finding's `file:line` must reference a line present in the diff. Structural findings cite the function header line.

   Correct: `pkg/auth/oauth.go:42-58` where the function spans those lines.
   Wrong: `pkg/auth/oauth.go:200` when the diff only touches lines 42-58.

3. **Never fabricate the `why`.** Each finding must trace to one of the ten Google principles, or to `small-cl` / `description` / `specialty`. No principle, no finding.

   Correct: `principle: design`, `why: "This function has three unrelated reasons to change..."`.
   Wrong: `principle: design`, `why: "Feels off."` — no Google principle reasoning.

4. **Never recommend "clean it up later."** Per Google `pushback.html`, refactors and follow-ups are filed as bugs, not promises. Emit `Optional:` findings for things the author can defer; never accept "I'll fix it in a follow-up" as a resolution path inside the review.

   Correct: `severity: optional, suggestion: "Consider extracting the helper now; if deferred, file an issue."`
   Wrong: `severity: required, suggestion: "OK to address in follow-up CL."`

5. **Triage before review.** Always run Phase 1 first. Phase 2 reads from triage, never re-derives size or scope-mix.

   Correct: Phase 2 prompt receives `triage.size = "medium"` as an input.
   Wrong: Phase 2 sub-agent re-counts files and recomputes size.

6. **Idempotent posting.** Before posting, check for the existing `<!-- googly-eyes:v1 -->` marker on the PR. If present, require `--force`.

   Correct: bail out with "Existing googly-eyes review detected; re-run with --force to replace."
   Wrong: posting a duplicate review without checking.

7. **Read-only by default.** The review pipeline (steps 1-5) makes zero writes — no files, no git, no GitHub. Only the explicit `post` subcommand writes.

   Correct: terminal output, no `git`/`gh` mutations during review.
   Wrong: any `git commit`, `gh pr edit`, or file write during a review run.

8. **Auto-detect target deterministically.** Per the rules in [Target detection](#target-detection) above.

## Branding

Every user-facing surface that names the skill starts with the 👀 (eyes) glyph: header line, posted summary body. The glyph is brand-only — never inside finding `why` or `suggestion` fields. See spec section 1.1.

## Reference index

| Step | Reference |
| --- | --- |
| Target detection | (inline, this file) |
| Triage checks | [triage-heuristics.md](./references/triage-heuristics.md) |
| Triage emit format | [assets/triage-report-template.md](./assets/triage-report-template.md) |
| Phase 2 dispatch and bundles | [phase2-bundles.md](./references/phase2-bundles.md) |
| Per-finding record schema | [assets/finding-record-template.md](./assets/finding-record-template.md) |
| Severity vocabulary | [references/severity-labels.md](./references/severity-labels.md) |
| Google principle definitions | [references/google-principles.md](./references/google-principles.md) |
| Pragmatic citations | [references/pragmatic-citations.md](./references/pragmatic-citations.md) |
| Ranking, dedupe, caps, file map | [references/output-format.md](./references/output-format.md) |
| Terminal rendering | [references/rich-rendering.md](./references/rich-rendering.md) |
| Posting to GitHub | [references/posting-step.md](./references/posting-step.md) |
````

- [ ] **Step 3: Validate frontmatter**

```bash
# Folder name = name field
[ "$(basename $(dirname skills/googly-eyes/SKILL.md))" = "googly-eyes" ] && echo OK
# No angle brackets in frontmatter
sed -n '/^---$/,/^---$/p' skills/googly-eyes/SKILL.md | grep -nE "[<>]" && echo "VIOLATION" || echo "frontmatter clean"
```

Expected: `OK` and `frontmatter clean`.

- [ ] **Step 4: Validate body**

```bash
pnpm lint
wc -l skills/googly-eyes/SKILL.md
```

Expected: lint clean. Line count under 500.

- [ ] **Step 5: Validate all reference links resolve and are ≤ 1 level deep**

```bash
grep -oE '\]\(\./[^)]+\)' skills/googly-eyes/SKILL.md | sed 's/](\.\///;s/)$//' | while read p; do
  [ -e "skills/googly-eyes/$p" ] || echo "BROKEN: $p"
  depth=$(echo "$p" | tr -cd '/' | wc -c)
  [ "$depth" -le 1 ] || echo "TOO DEEP: $p"
done
```

Expected: no output (all resolve and ≤ 1 level deep).

- [ ] **Step 6: Run the agentskills.io validator**

```bash
npx skills-ref validate ./skills/googly-eyes
```

Expected: exits 0.

- [ ] **Step 7: Commit**

```bash
git add skills/googly-eyes/SKILL.md
git commit -m "feat(googly-eyes): add SKILL.md (entry point + routing + hard rules)"
```

### Task 11: Write per-skill `README.md`

**Files:**

- Create: `skills/googly-eyes/README.md`

**Source spec sections:** 1 (summary), 1.1 (branding), 2 (differentiation).

Per-skill README is for humans browsing the repo on GitHub. Keep it brief, link out to `SKILL.md`.

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Validate**

```bash
pnpm lint
grep -c "npx skills add xornivore/skills@googly-eyes" skills/googly-eyes/README.md
```

Expected: lint clean, grep returns at least 1 (install command present).

- [ ] **Step 3: Commit**

```bash
git add skills/googly-eyes/README.md
git commit -m "feat(googly-eyes): add per-skill README"
```

---

## Phase 4 — Smoke fixtures, top-level wire-up, final validation

### Task 12: Add smoke test fixtures

**Files:**

- Create: `skills/googly-eyes/tests/fixtures/small-clean.diff`
- Create: `skills/googly-eyes/tests/fixtures/large-mixed.diff`
- Create: `skills/googly-eyes/tests/fixtures/weak-description.diff`
- Create: `skills/googly-eyes/tests/fixtures/security-path.diff`

Fixtures are unified-diff files used for manual smoke runs only. They are not loaded by the skill itself; they exist so a reviewer (human or agent) can run the skill against known inputs.

- [ ] **Step 1: Generate `small-clean.diff`**

A clean, well-scoped CL: ≤ 100 LOC, single subsystem, imperative-first-line description.

```bash
cat > skills/googly-eyes/tests/fixtures/small-clean.diff <<'EOF'
Subject: Cap result page size to 50 to avoid OOM on large queries

Large result pages were causing OOM in the API worker pool. Cap the page
size at 50 and document the cap in the API response.

Tested with the load harness; p99 worker RSS drops from 1.2 GiB to 380 MiB.

diff --git a/pkg/api/results.go b/pkg/api/results.go
index 1234abc..5678def 100644
--- a/pkg/api/results.go
+++ b/pkg/api/results.go
@@ -10,6 +10,9 @@ type Page struct {
     Total int   `json:"total"`
 }

+// MaxPageSize is the hard cap. See ADR-014.
+const MaxPageSize = 50
+
 func (s *Server) List(ctx context.Context, req *ListReq) (*Page, error) {
-    if req.Size <= 0 {
+    if req.Size <= 0 || req.Size > MaxPageSize {
         req.Size = 20
     }
EOF
```

- [ ] **Step 2: Generate `large-mixed.diff`**

A large CL mixing refactor (rename) with a feature (new endpoint). Should produce a `small-cl` finding at `required` and a scope-mix finding.

```bash
# Construct a synthetic diff with >400 LOC and a rename + feature pattern.
# Use a fixture-builder loop so the file size is realistic.
{
  echo "Subject: Refactor user package and add /v2/users endpoint"
  echo ""
  echo "Multi-concern change."
  echo ""
  for i in $(seq 1 50); do
    echo "diff --git a/pkg/user/file${i}.go b/pkg/userv2/file${i}.go"
    echo "similarity index 100%"
    echo "rename from pkg/user/file${i}.go"
    echo "rename to pkg/userv2/file${i}.go"
  done
  echo "diff --git a/pkg/api/v2/users.go b/pkg/api/v2/users.go"
  echo "new file mode 100644"
  echo "--- /dev/null"
  echo "+++ b/pkg/api/v2/users.go"
  for i in $(seq 1 500); do
    echo "+// new endpoint line ${i}"
  done
} > skills/googly-eyes/tests/fixtures/large-mixed.diff
```

- [ ] **Step 3: Generate `weak-description.diff`**

A reasonable code change with a Google-anti-pattern PR description ("Fix bug").

```bash
cat > skills/googly-eyes/tests/fixtures/weak-description.diff <<'EOF'
Subject: Fix bug

diff --git a/pkg/billing/charge.go b/pkg/billing/charge.go
index abc1234..def5678 100644
--- a/pkg/billing/charge.go
+++ b/pkg/billing/charge.go
@@ -42,7 +42,7 @@ func (s *Service) Charge(ctx context.Context, amt int64) error {
-    if amt <= 0 {
+    if amt < 0 {
         return ErrInvalidAmount
     }
EOF
```

- [ ] **Step 4: Generate `security-path.diff`**

A change in an auth path that should trigger the specialty advisory.

```bash
cat > skills/googly-eyes/tests/fixtures/security-path.diff <<'EOF'
Subject: Relax state-token validation to support legacy clients

Legacy mobile clients send state tokens without the v2 nonce prefix.
Accept both shapes during the migration window.

diff --git a/pkg/auth/state.go b/pkg/auth/state.go
index aaa1111..bbb2222 100644
--- a/pkg/auth/state.go
+++ b/pkg/auth/state.go
@@ -22,7 +22,7 @@ func (v *Verifier) Verify(token string) error {
-    if !strings.HasPrefix(token, "v2:") {
+    if !strings.HasPrefix(token, "v2:") && !strings.HasPrefix(token, "v1:") {
         return ErrBadPrefix
     }
EOF
```

- [ ] **Step 5: Validate fixtures exist and parse as diffs**

```bash
for f in small-clean large-mixed weak-description security-path; do
  [ -s "skills/googly-eyes/tests/fixtures/${f}.diff" ] || echo "MISSING: $f"
done
```

Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add skills/googly-eyes/tests/
git commit -m "test(googly-eyes): add smoke fixture diffs"
```

### Task 13: Update top-level README and run final validation

**Files:**

- Modify: `README.md` (top-level)

**Source spec sections:** 1.1 (branding), repo CLAUDE.md rule 4 (README sync).

- [ ] **Step 1: Move googly-eyes from "In design" to active Skills table**

Open `README.md` at the repo root and apply this edit:

In the active `## Skills` table, after the `observablip` row, add:

```markdown
| 👀 [googly-eyes](./skills/googly-eyes/SKILL.md) | Reviews PRs and local diffs against Google's eng-practices code review guide (all 10 principles). Rich local diff rendering, principle-tagged ranked findings, opt-in posting via `gh`. |
```

Then delete the `### In design` subsection and its row entirely (it is no longer needed).

- [ ] **Step 2: Verify the README**

```bash
grep -c "googly-eyes" README.md
grep -c "In design" README.md
```

Expected: first grep returns at least 1 (active table row). Second grep returns 0 (subsection removed).

- [ ] **Step 3: Lint and full skills-ref validate**

```bash
pnpm lint
npx skills-ref validate ./skills/googly-eyes
```

Expected: both exit 0.

- [ ] **Step 4: Smoke run the skill against one fixture (manual)**

This step is informational — the agent executing the plan should do a one-pass dry-run mentally walking through the SKILL.md against `small-clean.diff` to confirm the routing, triage, and output sections produce sensible content. The actual smoke run happens when an end user invokes the skill.

```bash
ls skills/googly-eyes/tests/fixtures/small-clean.diff
cat skills/googly-eyes/SKILL.md | head -20
```

Expected: fixture exists and SKILL.md is the entry point.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs(googly-eyes): move skill from in-design to active in README"
```

- [ ] **Step 6: Push and open the implementation PR**

```bash
git push -u origin feat/googly-eyes-skill
gh pr create --title "feat(googly-eyes): implement skill per spec" --body "$(cat <<'EOF'
## Summary

Implements the `googly-eyes` skill per the merged spec at `docs/superpowers/specs/2026-05-12-googly-eyes-design.md`.

- SKILL.md entry point with two-phase routing (triage → focused review)
- Eight reference files covering principles, severity, triage, bundles, Pragmatic citations, output format, rendering, posting
- Two asset templates (triage report, finding record)
- Four smoke-test fixture diffs for manual runs
- Top-level README moved from "In design" to active

## Test plan

- [ ] `pnpm lint` clean
- [ ] `npx skills-ref validate ./skills/googly-eyes` exits 0
- [ ] Manual smoke run against each fixture in `skills/googly-eyes/tests/fixtures/`
- [ ] Dry-run of `googly-eyes post` against a real PR to confirm comment-style filter behavior
EOF
)"
```

Expected: PR opens; URL printed.

---

## Self-review checklist

(Run after writing the plan — not a subagent dispatch.)

- [ ] Every spec section maps to a task. Spec section coverage:
  - Section 1 (summary) → Task 11 (README), Task 10 (SKILL.md description)
  - Section 1.1 (branding) → Task 10 (SKILL.md header), Task 11 (README), Task 13 (top-level README)
  - Section 2 (differentiation) → Task 11 (README differentiation table)
  - Section 3 (target detection) → Task 10 (SKILL.md `## Target detection`)
  - Section 4.1 (triage) → Task 4 (triage-heuristics.md)
  - Section 4.2 (Phase 2 bundles) → Task 5 (phase2-bundles.md)
  - Section 5 (finding schema) → Task 1 (finding-record-template.md)
  - Section 6 (severity vocabulary) → Task 3 (severity-labels.md)
  - Section 7.1-7.4 (ranking, dedupe, caps, file map) → Task 7 (output-format.md)
  - Section 7.5-7.8 (rendering) → Task 8 (rich-rendering.md)
  - Section 8 (posting step) → Task 9 (posting-step.md)
  - Section 9 (file layout) → all Phase-2 and Phase-3 tasks
  - Section 10 (hard rules) → Task 10 (SKILL.md `## Hard rules`)
  - Section 11 (out of scope) → Task 11 (per-skill README)
  - Section 12 (validation) → Task 10 step 6, Task 13 step 3
  - Section 13 (testing) → Task 12 (fixtures), Task 13 step 4

- [ ] No placeholders (TBD, TODO, "implement later") in any task body.
- [ ] Type consistency: principle slugs (`design`, `complexity`, …) match across all tasks. Severity slugs (`required`, `optional`, `nit`, `fyi`, `praise`) match. Finding ID prefixes (`T-`, `F-`) consistent.
- [ ] Every task ends in a commit step.
- [ ] All file paths use the `skills/googly-eyes/` prefix (no stray paths from sibling skills).
