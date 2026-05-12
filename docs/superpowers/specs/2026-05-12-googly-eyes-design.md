# googly-eyes — design spec

**Status:** draft
**Author:** Ivan Ilichev
**Date:** 2026-05-12
**Skill folder (planned):** `skills/googly-eyes/`
**Branch:** `feat/googly-eyes`

## 1. Summary

`googly-eyes` reviews pull requests and local diffs against Google's
canonical [engineering practices code review guide][google-cr], emits a
ranked, principle-tagged finding list with rich local rendering, and
optionally posts selected findings as a GitHub PR review.

Pragmatic Programmer principles are cited as supporting reasoning when
they cleanly apply to a finding's *why*; they never replace the Google
principle as the primary tag, and never act as a gate.

The skill is read-only by default. Only the explicit `post` subcommand
writes (via `gh api`), and only after the user approves the rendered
comment set.

[google-cr]: https://google.github.io/eng-practices/review/

## 2. Differentiation vs existing `code-review` skill

The `code-review` skill (claude-plugins-official) is a confidence-scored
bug filter — multi-agent parallel scan, ≥80-confidence threshold,
explicitly drops "general code quality, lack of test coverage, general
security issues, poor documentation" as noise. Output is a single GitHub
comment with high-confidence bugs only.

`googly-eyes` is the opposite lens: a holistic Google-shaped review
where all 10 principles are first-class.

| Axis | `code-review` | `googly-eyes` |
| --- | --- | --- |
| Frame | Bug hunter | Holistic Google-shaped review |
| Filter | ≥80 confidence; drops quality/tests/docs as noise | Nothing filtered out; severity-labeled by the model |
| Output | Single GitHub comment with bug list | Ranked finding list with principle tags + severity labels + rich local diff rendering; PR posting is opt-in step |
| Architecture | Parallel agents, confidence scoring | Two-phase: triage → focused review (adaptive) |
| Author-side use | No — PR-only | Yes — works on local diffs pre-PR for self-review |
| Scope guidance | Doesn't address CL size | Small-CL is first-class, surfaced in triage |

The two skills compose; they don't replace each other. `code-review` is
the noise-filtered bug gate. `googly-eyes` is the principled-review
lens.

## 3. Inputs & target detection

Routing happens in `SKILL.md` entry. Three cases:

1. **Explicit PR ref** (`googly-eyes #123` or full URL): fetch via
   `gh pr diff` and `gh pr view --json title,body,author,number,headRefOid`.
2. **Branch with open PR**: auto-detect via
   `gh pr view --json number` from the current branch. Treat as case 1.
3. **No PR**: diff current branch against base (default `main`,
   configurable via skill arg). PR-title/body inputs replaced by
   branch commit messages.

Hard rules: never silently switch modes mid-run. If both PR and local
diff are detectable, prefer the explicit argument if supplied;
otherwise prefer the PR (higher-fidelity target).

## 4. Architecture: two-phase flow

### 4.1 Phase 1 — Triage (cheap, always runs)

A single model pass producing a structured triage report.

| Check | Output |
| --- | --- |
| **CL size scoring** | LOC added/changed/removed, file count. Verdict: `small` (≤100 LOC, ≤5 files), `medium` (≤400 LOC), `large` (>400 LOC or >15 files). Source: Google `small-cls.html`. |
| **Scope-mix detection** | Heuristic: refactor + feature in the same CL? renames + behavior changes? Flag if mixed. |
| **CL description quality** | PR title + body (or branch commit messages) against Google `cl-descriptions.html`: imperative first line, body explains *why*, anti-patterns (`Fix bug`, `Phase 1`, etc.). |
| **File map** | Grouped by directory; flags generated files, vendored code, tests vs prod. |
| **Specialty triggers** | Path/keyword heuristics: changes in auth/crypto, concurrency primitives (mutex, channel, goroutine, async), public APIs, perf-critical paths → advisory note ("consider specialty reviewer for X"). |

Triage produces both a structured handoff (consumed by Phase 2) and
visible findings (`small-cl`, `description`, `specialty`).

CL size policy: flag prominently in triage but **still review**. An
oversized CL gets a `required`-severity `small-cl` finding leading the
output, with a split-strategy suggestion (stack / horizontal /
vertical, per Google `small-cls.html`). The full review still runs.

### 4.2 Phase 2 — Focused review (adapts to triage)

Branching rule:

- **`small`** → single-pass review covering all remaining principles in
  one context window.
- **`medium` / `large`** → dispatch parallel sub-agents, one per
  principle bundle:

  | Bundle | Principles |
  | --- | --- |
  | Architecture lens | design, complexity |
  | Correctness lens | tests-as-design, functionality |
  | Readability lens | naming, comments-as-why, style, consistency |
  | Completeness lens | documentation, every-line, context |

Each sub-agent returns findings as structured records. The main agent
merges, dedupes, ranks, applies severity labels.

`small-cl` and `description` were emitted by triage and are not
re-derived in Phase 2.

## 5. Finding schema

```yaml
- principle: design          # one of the 10 Google principles, or
                             # 'small-cl' | 'description' | 'specialty'
  severity: required         # required | optional | nit | fyi | praise
  location:
    file: path/to/file.go
    line: 42                 # or range '42-58' for structural findings
  observation: <factual: what in the code triggered the finding>
  why: <reasoning: cites the Google principle; optionally cites a
        Pragmatic Programmer principle when it cleanly applies>
  suggestion: <preferred direction, or empty when the author should
               decide>
```

## 6. Severity vocabulary (Google `comments.html`)

| Label | When | Posting behavior |
| --- | --- | --- |
| `required` | Code health regression or correctness issue that must be addressed before merge. Per Google `standard.html`: "Don't accept CLs that degrade the code health of the system." | `REQUEST_CHANGES` if user opts in; else `COMMENT` |
| `optional` | Good idea, would improve code health but not blocking. Prefixed `Optional:` or `Consider:`. | `COMMENT` |
| `nit` | Minor preference, technically should be addressed but author can ignore. Prefixed `Nit:`. | `COMMENT` |
| `fyi` | Informational only; no action expected. Prefixed `FYI:`. | `COMMENT` |
| `praise` | Google's "Good Things" — call out excellent design, exemplary tests, useful comments. Prefixed `Praise:`. | `COMMENT` |

**Rule:** at least one `praise` finding when any qualifies. Phase-2
sub-agents are prompted with "and: surface one excellent thing in your
scope if you find it."

## 7. Output: rich local rendering

### 7.1 Ranking

1. By severity: `required` > `optional` > `nit` > `fyi` > `praise`.
2. Within severity, by principle priority (Google: "design is the most
   important thing"):
   `design > complexity > tests > functionality > naming > comments >
   documentation > every-line > consistency > style`.
3. Tiebreaker: file (alphabetical) then line ascending.

Triage findings (`small-cl`, `description`, `specialty`) appear in the
triage summary block at the top, separate from the principle-ranked
list.

### 7.2 Dedupe

- `(file, line ± 2, principle)` collisions merge → keep highest severity,
  concatenate `why` if non-redundant.
- Structural findings (e.g., "this function is over-complex") bundle at
  function scope, not repeated per line.

### 7.3 Bounded output

| Severity | Cap |
| --- | --- |
| required | 20 |
| optional | 15 |
| nit | 10 |
| fyi | 5 |
| praise | unbounded (typically 1–3) |

If capped, append: `N more <severity> findings suppressed; consider
splitting this CL for thorough review` — which doubles as
reinforcement of the small-CL principle.

### 7.4 Top-of-output: file map

Before the findings, a scannable file map with severity badges and LOC
deltas, mirroring what a reviewer sees in the GitHub file tree:

```text
pkg/auth/oauth.go     1R · 2O · 1N · 0F · 1P     (+47/-12)
pkg/auth/state.go     0R · 1O · 0N · 0F · 0P     (+18/-4)
internal/db/token.go  1R · 0O · 0N · 0F · 0P     (+8/-2)
```

### 7.5 Per-finding diff context (default render)

Each finding renders with the actual code hunk inline, drawn from the
diff. The hunk preserves `+`/`-` markers from the change.

```text
─────────────────────────────────────────────────────────────────────────
REQUIRED · design                                        finding #1 of 4
pkg/auth/oauth.go:42-58
─────────────────────────────────────────────────────────────────────────
Why:  This function handles callback parsing, token exchange, AND
      database persistence in one body. Three unrelated reasons to
      change. Violates orthogonality (Pragmatic Programmer).

Suggestion: split into `parseCallback`, `exchangeCode`, `persistToken`.
Let the HTTP handler compose them.

   40 │   func (s *Server) Callback(w http.ResponseWriter, r *http.Request) {
   41 │       ctx := r.Context()
   42 │ +     code := r.URL.Query().Get("code")
   43 │ +     state := r.URL.Query().Get("state")
   44 │ +     if !s.verifyState(state) { ... }
   45 │ +     tok, err := s.exchange(ctx, code)
   ...
   56 │ +     if err := s.db.SaveToken(ctx, tok); err != nil { ... }
   57 │ +     http.Redirect(w, r, "/", 302)
   58 │   }
─────────────────────────────────────────────────────────────────────────
```

### 7.6 Color & TTY

- TTY detected: ANSI colors — `+` lines green, `-` lines red, severity
  label colored (red / yellow / cyan / dim by severity), file path bold,
  principle dim.
- Not a TTY (piped, redirected): plain ASCII, no escape codes. Same
  content.
- `NO_COLOR` env var respected (<https://no-color.org>).

Detection: `[ -t 1 ] && [ -z "$NO_COLOR" ]`. The skill ships no renderer
dependency — ANSI escapes are composed inline. Optionally pipe to
`delta` or `bat --paging=never` if the user has them; never required.

### 7.7 Verbosity flags

Three render modes, defaulting to medium:

| Flag | Shows |
| --- | --- |
| `--compact` | File map + finding list, no hunks. For very large CLs. |
| (default) | File map + findings with per-finding hunk (5-line context). |
| `--detailed` | Above plus full file diff inline, findings interleaved at their line (annotated-diff mode). |

### 7.8 Implementation notes

- Hunks are sliced from the diff already in memory; no extra `git`
  calls per finding.
- Line numbers use the post-image numbering (the new file's line
  numbers), matching what GitHub shows.
- Structural findings show the function header line as anchor, but the
  hunk spans the function body.
- Findings outside any diff hunk (rare; e.g., context-only files
  flagged for a deletion concern) render a 5-line `git show` excerpt
  labeled `(context-only)`.

## 8. Posting step

### 8.1 Invocation

Posting is separate from the review step. Never auto-runs.

- `googly-eyes post` — promotes findings from the most recent
  in-session review.
- `googly-eyes post --from <file>` — promotes from a saved review
  output file (cross-session use).

Hard rule (in `SKILL.md`): the skill must render every comment exactly
as it will appear on GitHub and wait for explicit user approval before
any `gh` write. No batch auto-post.

### 8.2 Selection

| Spec | Posts |
| --- | --- |
| (default) | all `required` findings only |
| `--include optional` | adds `optional` |
| `--include nit,fyi,praise` | adds the named severities |
| `--only <ids>` | exactly the listed finding IDs |
| `--exclude <ids>` | every selected severity minus excluded IDs |

`praise` findings: when the selection includes any `required` or
`optional`, prompt once: "N praise findings available — include them?"

### 8.3 Composition (gh API)

`gh pr review --comment` does not support multi-inline reviews
natively. Use:

```bash
gh api repos/<owner>/<repo>/pulls/<pr>/reviews \
  --method POST \
  --field event=COMMENT \
  --field body=<summary> \
  --field comments=<JSON array of {path, line, body}>
```

One atomic review per invocation.

### 8.4 Idempotent posting

Before posting, fetch `gh pr view <pr> --json reviews` and check for an
existing review whose summary body contains the marker
`<!-- googly-eyes:v1 -->`. If present, warn and require `--force`.

### 8.5 Comment-style enforcement (Google `comments.html`)

Every emitted comment is run through a style filter before render:

| Rule | Enforcement |
| --- | --- |
| Focus on code, not author | Reject phrasing using second-person blame ("why did you…", "you should…"). Rewrite to subject-on-code ("the concurrency model here adds complexity without measurable benefit"). |
| Explain the *why* | Every comment body must contain a "Because…" / "This…" clause from the finding's `why`. Comments without a `why` are blocked. |
| Prefer pointing out, not prescribing | If the finding has a `suggestion`, render as "Consider X" / "One option: X" — not "Change to X". Prescriptive phrasing allowed for `required` only. |
| Severity prefix on non-required | `Optional:` / `Consider:` / `Nit:` / `FYI:` / `Praise:` literally prefixed at start of comment body. `required` has no prefix (severity is implicit when blocking). |

### 8.6 Summary review body

```text
googly-eyes review — <commit SHA>

Triage: size=<small|medium|large>, scope=<single|mixed>, description=<strong|weak>

Required: N  ·  Optional: M  ·  Nit: K  ·  FYI: J  ·  Praise: P
Filed below as inline comments.

<!-- googly-eyes:v1 -->
```

### 8.7 Event type

Default: `COMMENT`. User opts into `REQUEST_CHANGES` with
`--request-changes`, valid only if at least one `required` finding is
in the selection. Per Google `pushback.html`: "Improving code health
tends to happen in small steps" — request-changes is the heavier
hammer; default to the lighter one.

### 8.8 Failure modes

| Condition | Behavior |
| --- | --- |
| `gh` not authenticated | Print rendered comments to stdout; instruct user to authenticate and re-run. |
| PR closed | Refuse; print finding list as terminal output. |
| PR is by current user (self-review) | Allow (Google practice); add `--self-review` advisory to summary. |
| Finding line missing from PR diff (file changed since review) | Fall back to file-level comment with `(originally @ L<N>)` in body. |
| Local-diff mode, no open PR | Post step unavailable; skill exits cleanly after finding list. |

## 9. File layout

Per the repo's `skills/CLAUDE.md` (agentskills.io spec + repo
conventions): keep `SKILL.md` lean (≤500 lines, decision-focused),
split detail into `references/`, pull references at the step that
needs them.

```text
skills/googly-eyes/
├── SKILL.md                          # entry point; routing + triage + reference index
├── README.md                         # human-facing; install command + link to SKILL.md
├── references/
│   ├── google-principles.md          # the 10 principles, verbatim citations, when each applies
│   ├── severity-labels.md            # Required / Optional / Nit / FYI / Praise — when to use each
│   ├── triage-heuristics.md          # CL-size thresholds, scope-mix detection, specialty triggers
│   ├── phase2-bundles.md             # principle bundle definitions, sub-agent prompts
│   ├── pragmatic-citations.md        # PP principles + which Google principle they enrich
│   ├── posting-step.md               # gh review composition, comment style rules, examples
│   ├── output-format.md              # finding record schema, ranking, render modes
│   └── rich-rendering.md             # ANSI / TTY / hunk-slicing details
├── assets/
│   ├── triage-report-template.md     # structured triage output skeleton
│   └── finding-record-template.md    # structured per-finding skeleton
└── tests/                            # dev-only fixtures; not loaded by the skill
    └── fixtures/                     # curated diffs for manual smoke runs
```

Loading strategy (stage 2 → stage 3):

| Step in SKILL.md flow | Reference loaded |
| --- | --- |
| Detect target / fetch diff | (none — Bash + gh) |
| Run triage | `triage-heuristics.md`, `assets/triage-report-template.md` |
| Decide single-pass vs parallel | `phase2-bundles.md` |
| Sub-agent dispatch (parallel branch) | each sub-agent loads `google-principles.md` for its bundle + `assets/finding-record-template.md` |
| Merge / rank | `output-format.md` |
| Render locally | `rich-rendering.md` |
| Cite Pragmatic Programmer (when applicable) | `pragmatic-citations.md` |
| Posting step (opt-in) | `posting-step.md` |

## 10. Hard rules (encoded in `SKILL.md` body)

These appear as imperatives in the SKILL body per the repo's voice
rules (`skills/CLAUDE.md` §3.1 — "must" / "never", not "should"):

1. **Never post without explicit user confirmation.** Render every
   comment exactly as it will appear on GitHub and wait for explicit
   approval before any `gh` write. No batch auto-post.
2. **Never invent code locations.** Every finding's `file:line` must
   reference a line present in the diff. Structural findings cite the
   function header line.
3. **Never fabricate the `why`.** Each finding must trace to one of the
   10 Google principles, or to `small-cl` / `description` / `specialty`.
   No principle, no finding.
4. **Never recommend "clean it up later".** Per Google `pushback.html`:
   refactors and follow-ups are filed as bugs, not promises. The skill
   emits `Optional:` findings for things the author can defer — but
   never accepts "I'll fix it in a follow-up" as a resolution path
   within the same review.
5. **Triage before review.** Always run Phase 1 first. Phase 2 reads
   from triage output, never re-derives size or scope-mix.
6. **Idempotent posting.** Before posting, check for the existing
   `<!-- googly-eyes:v1 -->` marker on the PR. If present, require
   `--force`. Prevents duplicate reviews on re-runs.
7. **Read-only by default.** The review step (Phase 1 + Phase 2 +
   finding list) makes zero writes — no files, no git, no GitHub. Only
   the explicit `post` subcommand writes.
8. **Auto-detect target deterministically.** If both PR and local diff
   are detectable, prefer the explicit argument if supplied; otherwise
   prefer the PR (higher-fidelity target). Never silently switch modes
   mid-run.

## 11. Out of scope

- **Bug-hunting with confidence scoring.** That is `code-review`'s job.
  `googly-eyes` does not filter findings by confidence; it filters by
  severity (the author's tool, not the algorithm's).
- **Observability gaps.** That is `observablip`'s job. `googly-eyes`
  may emit an `FYI` finding pointing at `observablip` if missing
  telemetry is glaring; it never tries to do the audit itself.
- **Documentation drafting.** That is `doxcavate`'s job. `googly-eyes`
  flags doc-update misses (per Google's "Documentation" principle) but
  does not write the docs.
- **Auto-merge or auto-approval.** Never. The skill proposes; the
  human (or another skill) approves.
- **XP / pair-programming guidance.** Excluded by design.

## 12. Validation

Before opening a PR for the skill:

```bash
pnpm lint                                          # markdownlint + lint-staged
npx skills-ref validate ./skills/googly-eyes       # agentskills.io reference validator
```

Both must exit 0. Audit cues encoded in the `SKILL.md` body for each
mechanical rule:

- Folder name = frontmatter `name`
  (audit: `basename $(dirname SKILL.md)` matches the `name:` field).
- No angle brackets in frontmatter (audit: grep frontmatter for `[<>]`).
- File refs ≤ 1 level deep from `SKILL.md` (audit: grep markdown links
  for path depth > 1).
- README install command present (audit: grep for
  `npx skills add xornivore/skills@googly-eyes`).

## 13. Testing strategy

Three layers, scaled to skill complexity:

1. **Smoke tests (manual, in-repo).** Run `googly-eyes` against
   curated fixture diffs:
   - A clean, well-scoped 80-LOC CL → expect small triage, mostly
     praise and nits.
   - An over-large mixed-scope 800-LOC CL → expect `small-cl` and
     scope-mix at top, sub-agents dispatched.
   - A CL with a poor description ("fix bug") → expect description
     finding in triage.
   - A CL touching `pkg/auth/*` → expect specialty trigger.

   Fixtures live in `skills/googly-eyes/tests/fixtures/` — not part of
   the skill body itself; loaded only for manual runs.

2. **Posting dry-run.** `googly-eyes post --dry-run` renders the `gh`
   API payload to stdout without sending. Used to verify comment-style
   enforcement: no second-person blame, every comment carries a `why`,
   severity prefixes correct.

3. **Skill validator.** `npx skills-ref validate` covers the spec
   mechanics (frontmatter shape, folder layout, install command, no
   `<>`).

No automated end-to-end test against real GitHub — too brittle, too
much surface. Smoke tests on fixtures + dry-run rendering is the
practical bar.

## 14. References (research artifacts)

- Google engineering practices code review guide:
  <https://google.github.io/eng-practices/review/>
  - Reviewer's guide: `standard.html`, `looking-for.html`,
    `navigate.html`, `speed.html`, `comments.html`, `pushback.html`.
  - CL author's guide: `cl-descriptions.html`, `small-cls.html`,
    `handling-comments.html`.
- Existing `code-review` skill (claude-plugins-official) — the bug-hunt
  comparison point. Local source:
  `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/code-review/`.
- Pragmatic Programmer principles (Hunt & Thomas, 20th anniversary
  edition): DRY, orthogonality, tracer bullets, broken windows,
  decoupling, ETC, programming-by-coincidence.
