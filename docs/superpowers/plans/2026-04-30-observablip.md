# observablip Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `observablip` Claude Code skill — a read-only auditor that walks a target codebase, applies a three-dimension o11y rubric (missing telemetry, poor practices, structure-for-telemetry), filters via a precheck and a false-positive review pass, and emits a ranked, bounded list of findings.

**Architecture:** Skill packaged as Markdown content (no runtime code). One invocation mode (`audit`). `SKILL.md` is the lean entry point: pipeline routing, hard rules, reference index. `references/` holds the precheck rubric, three dimension rubrics, the FP-review rubric, and the output-schema spec — each loaded only at the pipeline step that needs it (stage-3 progressive disclosure). `assets/finding-template.md` is the per-finding fill template loaded at emit time.

**Tech Stack:** Markdown only. Validation by `pnpm lint` (`markdownlint-cli2` already in repo) and `npx skills-ref validate` against the agentskills.io spec. Skill installed via `npx skills add xornivore/skills@observablip --agent claude-code -y`. The skill is content for Claude Code, not executable code.

**Spec source:** `docs/superpowers/specs/2026-04-30-observablip-design.md`. The plan lifts content from numbered spec sections — when a step says "transcribe spec section N.M," paste the spec prose, then adapt to skill-instruction voice ("when invoked, do X" rather than "observablip does X").

**Authoring rules:** Follow `skills/CLAUDE.md` (skill-authoring conventions for this repo, derived from the agentskills.io specification). Read it before starting Task 1. The plan's structure (folders, file naming, frontmatter shape) is already aligned to those rules.

---

## Working environment

- Branch: `skill/observablip` (already created from `main`).
- Worktree: `.worktrees/observablip/`.
- All commands run from the worktree root.
- `pnpm install` has already run; husky is active. `pnpm lint` is clean at baseline.

## File structure

```text
skills/observablip/
├── SKILL.md
├── README.md
├── references/
│   ├── output-schema.md
│   ├── precheck.md
│   ├── missing-telemetry.md
│   ├── poor-practices.md
│   ├── structure-for-telemetry.md
│   └── false-positive-review.md
└── assets/
    └── finding-template.md
```

Plus one modification:

- `README.md` (top-level) — add an `observablip` row to the Skills table.

## Voice rules (apply to all skill files)

- Imperative: "when invoked, do X" — not "observablip does X." Per `skills/CLAUDE.md` 3.1.
- Strip hedge tokens (`may`, `might`, `could`, `ideally`, `we suggest`, `perhaps`).
- Replace `should` with `must` / `always` for non-negotiable rules.
- Each standalone rule paired with a correct example **and** a wrong example, per `skills/CLAUDE.md` 3.2.
- Mechanical rules carry an audit cue, per `skills/CLAUDE.md` 3.3.
- No `§`. Cross-references use plain Markdown anchor links per `docs/CLAUDE.md`.

## Phase 0 — Repo prep

(No prep tasks — worktree, deps, baseline already in place.)

---

## Phase 1 — Scaffold

### Task 1: Scaffold skill directory and finding template

**Files:**

- Create: `skills/observablip/` (dir, plus `references/` and `assets/` subdirs)
- Create: `skills/observablip/assets/finding-template.md`

**Source spec sections:** 5 (Output schema), 7 (Folder layout).

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p skills/observablip/references skills/observablip/assets
```

- [ ] **Step 2: Verify the directories exist and are empty**

```bash
find skills/observablip -type d
```

Expected:

```text
skills/observablip
skills/observablip/references
skills/observablip/assets
```

- [ ] **Step 3: Write `assets/finding-template.md`**

This is the per-finding fill template referenced at the emit step. The shape mirrors spec section 5 verbatim. Write the file with this exact content:

````markdown
# Finding template

Filled per finding at the emit step. Substitute the bracketed placeholders with values produced by the pipeline. Emit the rendered block with no surrounding fences (the example below is fenced for readability of this template document only).

```text
[{index}] {dimension} · {severity} · {file}:{line}
    {why_this_matters}
    Suggest: {suggest}
```

## Field rules

- `{index}` — 1-based; stable within a single run.
- `{dimension}` — one of `missing-telemetry`, `poor-practices`, `structure-for-telemetry`.
- `{severity}` — one of `high`, `med`, `low`. Severity is decided by the rubric file that produced the finding.
- `{file}:{line}` — the most informative line for the finding (start of the operation, not start of the file).
- `{why_this_matters}` — 1–2 lines naming the concrete consequence of leaving the gap. "A failure in any one is currently indistinguishable from the others in production logs" is acceptable; "improves observability" is not.
- `{suggest}` — the *shape* of the fix, not a code patch. Names a span, metric, log event, or structural change. If the codebase already imports OTel / slog / zap / structlog, the suggestion uses that vocabulary; otherwise it stays neutral ("a span", "a structured log").

## Footer template

After all findings are emitted, render this footer block once:

```text
---
scanned: {n_scanned} files
skipped: {n_skipped} ({skip_reasons_grouped})
fp-dropped: {n_fp_dropped}
shown: {n_shown} of {n_total} findings{overflow_note}
```

- `{skip_reasons_grouped}` — reason-keyed counts, comma-separated, e.g. `generated: 8, no-io: 6, test-fixture: 4, pure-data: 1`. Reasons come from the fixed set in `references/precheck.md`.
- `{overflow_note}` — if `n_shown < n_total`, append ` — narrow the target with a path or glob`. Otherwise empty.
````

- [ ] **Step 4: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 5: Commit**

```bash
git add skills/observablip/assets/finding-template.md
git commit -m "feat(observablip): scaffold skill dirs and finding template"
```

---

## Phase 2 — References (rubric content)

Each task in this phase creates one file under `skills/observablip/references/`. Each file is a standalone reference loaded only at the pipeline step that needs it. Cross-references between files use relative links (`[name](./other.md)`) — never deeper than one level.

Voice rules from the top of this plan apply throughout. Every standalone rule gets a correct/wrong example pair.

### Task 2: `references/output-schema.md`

**Files:**

- Create: `skills/observablip/references/output-schema.md`

**Source spec sections:** 4.5 (Rank and emit), 5 (Output schema), 6 (Hard rules — restate rules 4 and 5 as they bind to output).

- [ ] **Step 1: Write the file**

Required structure (Markdown headings, in order):

````markdown
# Output schema

Loaded at pipeline step 4.5 (rank and emit).

## Finding shape

[transcribe spec section 5 — full finding example block, then the field-rules list]

## Ranking

[transcribe spec section 4.5 — the three-tier ranking rules in order]

## Footer

[transcribe spec section 5 footer block, then list each footer field with the source step that supplies it]

## Bounded output

[restate hard rule 4 from spec section 6 — default cap 20 via `--max`, overflow surfaces with the literal string `narrow the target`, never silent truncation]

**Audit:** if the candidate finding count exceeds `--max`, the emitted output must contain the string `narrow the target`.

## Skip accounting

[restate hard rule 5 — every excluded file is counted in the footer aggregate under one of the fixed reason words from `references/precheck.md`. No silent exclusion.]

**Audit:** `scanned + skipped` in the footer must equal the resolved file count from pipeline step 4.1.

## Action checklist

When the agent reaches step 4.5:

1. Sort surviving findings per the ranking rules above.
2. Assign 1-based indices.
3. Render each finding through `assets/finding-template.md`.
4. Render the footer block, populating skip-reason counts from the precheck step's rejection log and `fp-dropped` from the FP-review step's drop count.
5. If the total exceeds `--max`, render only the top `--max` and append the overflow note.
````

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 3: Commit**

```bash
git add skills/observablip/references/output-schema.md
git commit -m "feat(observablip): add output-schema reference"
```

---

### Task 3: `references/precheck.md`

**Files:**

- Create: `skills/observablip/references/precheck.md`

**Source spec sections:** 4.2 (Per-file precheck), 6 (rule 5 Skip accounting).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Precheck — observable surface area

Loaded at pipeline step 4.2. Decides whether each resolved file is worth applying the rubric to. Files that fail are excluded with one of a fixed set of reasons; excluded files appear only in the footer aggregate.

## Pass criteria

A file passes the precheck if it has at least one of:

1. **A public/exported boundary** — HTTP handler, RPC server method, CLI entry, queue consumer, scheduled job.
2. **An external I/O call** — network, DB, filesystem, subprocess, or channel-spanning operation.
3. **Non-trivial error edges** — at least two distinct error returns or raise/throw points.

[For each criterion, write a 1–2 line "what counts" paragraph and one correct example + one wrong example, language-bias toward Go and Python. Sample for criterion 1 below; produce the same shape for 2 and 3.]

### Criterion 1 example — public boundary (correct)

```go
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) error {
    // ...
}
```

This is a request boundary — it passes the precheck.

### Criterion 1 example — public boundary (wrong)

```go
type IngestRecord struct {
    ID   string
    Body []byte
}
```

A pure data struct with no methods. No boundary. This file fails criterion 1.

## Skip reasons

Fixed set; no other reasons emitted:

- `generated` — file has the `Code generated by ... DO NOT EDIT` header (Go) or equivalent (Python `# Generated by ...`, TS `// @generated`).
- `no-io` — file passes none of the criteria above and has no external I/O.
- `test-fixture` — file is under a fixture directory or matches a test-fixture naming convention (`testdata/`, `__fixtures__/`, `*.golden`).
- `pure-data` — file declares only types/structs/dataclasses with no methods or only trivial accessors.
- `vendored` — file is under `vendor/`, `node_modules/`, or a `.gitignore`-listed dependency dir.

[For each skip reason, one correct/wrong example pair showing what triggers the reason and what does not.]

## What NOT to skip

- Files containing only test code (`*_test.go`, `tests/test_*.py`) are NOT auto-skipped — tests can themselves contain o11y anti-patterns the user wants flagged. They pass the precheck if they meet any of the three criteria.
- Files smaller than N lines are NOT auto-skipped on length alone. Length is not a signal of observable surface area.

## Action checklist

When the agent reaches step 4.2:

1. For each resolved file, check pass criteria 1–3 in order; the first match wins.
2. If none match, assign a skip reason from the fixed set above. If no reason fits, default to `no-io`.
3. Record the file path and reason in the precheck rejection log (consumed by the footer at step 4.5).
4. Pass surviving files to step 4.3.

**Audit:** every file resolved at step 4.1 must appear exactly once in either the surviving set or the rejection log.
````

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

- [ ] **Step 3: Commit**

```bash
git add skills/observablip/references/precheck.md
git commit -m "feat(observablip): add precheck reference"
```

---

### Task 4: `references/missing-telemetry.md`

**Files:**

- Create: `skills/observablip/references/missing-telemetry.md`

**Source spec sections:** 4.3 dimension 1.

This reference holds rubric dimension 1: places where telemetry is *absent* but warranted.

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Missing telemetry

Loaded at pipeline step 4.3 when applying dimension 1. Emit one finding per pattern match per surviving file. Severity is decided per pattern below.

## Pattern: operation without span at request boundary

**What to look for:** a function that handles an external request (HTTP/RPC/queue/CLI entry) and runs ≥2 sub-operations (DB call, external HTTP, file write, subprocess) with no `tracer.Start` / `with span(...)` / equivalent at the boundary.

**Severity:** `high` when on a public boundary; `med` otherwise.

**Why this matters template:** "A failure in any sub-operation is currently indistinguishable in production logs — there is no boundary span to correlate them under."

**Suggest template:** "wrap the operation in a span named `{verb}.{noun}` with attributes `{salient_inputs}`."

### Correct (do not flag)

```go
func (s *Server) Ingest(ctx context.Context, req *IngestReq) error {
    ctx, span := s.tracer.Start(ctx, "ingest.batch", trace.WithAttributes(
        attribute.Int("batch_size", len(req.Items)),
    ))
    defer span.End()
    if err := s.publishKafka(ctx, req); err != nil { return err }
    return s.writeS3(ctx, req)
}
```

### Wrong (flag this)

```go
func (s *Server) Ingest(ctx context.Context, req *IngestReq) error {
    if err := s.publishKafka(ctx, req); err != nil { return err }
    return s.writeS3(ctx, req)
}
```

## Pattern: error returned without structured context

**What to look for:** ...

[same shape — what to look for, severity, why-template, suggest-template, correct, wrong]

## Pattern: missing structured log at boundary

[same shape]

## Pattern: missing metric on hot path

[same shape]

## Pattern: missing trace/request-ID propagation

**What to look for:** a sub-operation that opens its own context with `context.Background()` instead of accepting a `ctx` parameter, severing trace propagation. Or a Python function that calls `requests.get(...)` without an existing trace header injection.

[severity, why, suggest, correct, wrong]

## What NOT to flag

- Files where every operation already has a span and every error already wraps with structured context. Use this list to back off the FP review.
- Single-call functions that delegate to one already-instrumented helper — the helper carries the telemetry; double-wrapping is noise.
- Pure functions with no I/O. (These should have been caught by the precheck; if one slips through, do not flag it here.)

## Action checklist

When the agent reaches step 4.3 dimension 1:

1. For each surviving file, scan for each pattern above in order.
2. For each match, build a candidate finding using the why-template and suggest-template, substituting from the matched code.
3. Forward all candidates to step 4.4 (FP review).
````

The implementer must populate the `[same shape]` placeholders with full pattern blocks before commit. Each pattern block must include all six elements: what-to-look-for, severity, why-template, suggest-template, correct example, wrong example.

- [ ] **Step 2: Verify no `[same shape]` placeholders remain**

```bash
grep -n '\[same shape\]\|\[transcribe' skills/observablip/references/missing-telemetry.md
```

Expected: no output (exit 1 from grep — that's the success state).

- [ ] **Step 3: Lint**

```bash
pnpm lint
```

- [ ] **Step 4: Commit**

```bash
git add skills/observablip/references/missing-telemetry.md
git commit -m "feat(observablip): add missing-telemetry rubric"
```

---

### Task 5: `references/poor-practices.md`

**Files:**

- Create: `skills/observablip/references/poor-practices.md`

**Source spec sections:** 4.3 dimension 2; 6 rule 3 (no verbatim secrets/PII).

This reference holds rubric dimension 2: telemetry that *exists* but is wrong. It also owns the regex set referenced by hard rule 3.

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Poor practices

Loaded at pipeline step 4.3 when applying dimension 2. One finding per pattern match per file. Severity per pattern.

## Pattern: log-then-throw / log-then-return

**What to look for:** the same error is logged at one level and then re-thrown / re-returned to a higher level that will likely log it again. Produces duplicate log lines in production for a single failure.

**Severity:** `med` when at internal layers; `low` for tight catch-and-rethrow shims.

[full pattern block: severity, why-template, suggest-template, correct, wrong]

## Pattern: log-as-print

**What to look for:** `fmt.Println` / `print()` / `console.log` used in production code paths instead of a structured logger. Strips level, timestamp, fields.

[full pattern block]

## Pattern: unstructured string log

**What to look for:** `log.Info(fmt.Sprintf("processed %d items for user %s", n, user))` — values interpolated into the message string instead of attached as structured fields.

[full pattern block]

## Pattern: raw PII or secret in log args

**What to look for:** a log call passes a value that matches one of the regex shapes below as a top-level argument, with no apparent redaction.

**Severity:** `high`.

[full pattern block — but: when authoring the finding, describe the *shape* (e.g. "a log call passes a raw email field") rather than quoting the line verbatim. This is hard rule 3.]

## Pattern: log spam in tight loops

**What to look for:** `log.Info` / equivalent inside a loop with no rate-limit, sample, or "log on transition" guard.

[full pattern block]

## Pattern: ambient `time.Now()` in observable paths

**What to look for:** a function that emits a timestamp into a metric or span attribute reads `time.Now()` directly instead of accepting an injected clock or `time.Now` reference. Hostile to deterministic tests; subtle skew across replicas.

[full pattern block]

## Pattern: error wrap with no metadata

**What to look for:** `fmt.Errorf("ingest: %w", err)` / `raise IngestError(...) from e` — wraps preserve the chain but add no additional structured fields (operation, key, attempt count).

[full pattern block]

## Secret / PII regex set

The audit cue for hard rule 3 references this list. Findings produced by this rubric must NOT include string literals matching:

- Email — `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
- JWT — `eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}`
- Bearer token header — `[Bb]earer\s+[A-Za-z0-9._\-]{16,}`
- AWS access key id — `AKIA[0-9A-Z]{16}`
- Generic high-entropy hex/base64 ≥ 32 chars next to a key-like token (`secret`, `token`, `key`, `password`, `pwd`).

When emitting a finding that references a log-call site matching any of these in its arguments, the finding's *quoted* content must redact the offending substring as `[redacted]` and surface only the field name and shape.

## What NOT to flag

- Logs in `cmd/*` startup output (banner, version, listening address) — these are operator-facing and unstructured by convention.
- Test-time `t.Logf` / `print` — tests are out of scope for this dimension.
- Wrap chains that *deliberately* drop metadata to anonymize at a trust boundary.

## Action checklist

When the agent reaches step 4.3 dimension 2:

1. Scan each surviving file for each pattern above.
2. Apply the redaction rule from the secret/PII list before adding a candidate to the queue.
3. Forward candidates to step 4.4.

**Audit:** for every emitted finding from this rubric, the rendered output must not contain a substring matching any regex in the secret/PII set above.
````

The implementer must replace each `[full pattern block]` with the full six-element block (what-to-look-for, severity, why-template, suggest-template, correct example, wrong example).

- [ ] **Step 2: Verify no placeholders remain**

```bash
grep -n '\[full pattern block\]\|\[same shape\]\|\[transcribe' skills/observablip/references/poor-practices.md
```

Expected: no output.

- [ ] **Step 3: Lint**

```bash
pnpm lint
```

- [ ] **Step 4: Commit**

```bash
git add skills/observablip/references/poor-practices.md
git commit -m "feat(observablip): add poor-practices rubric"
```

---

### Task 6: `references/structure-for-telemetry.md`

**Files:**

- Create: `skills/observablip/references/structure-for-telemetry.md`

**Source spec sections:** 4.3 dimension 3.

This reference holds rubric dimension 3: code shape that resists adding telemetry, even when none of dimensions 1 or 2 fire directly.

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# Structure for telemetry

Loaded at pipeline step 4.3 when applying dimension 3. One finding per pattern match per file. Severity per pattern.

## Pattern: function mixes unrelated I/O operations

**What to look for:** a single function that performs ≥2 logically distinct I/O concerns (e.g., ingestion *and* notification, fetch *and* cache-write, compute *and* persist) with no clear boundary between them. Adding a span at the function level conflates two operations; adding spans inside requires restructuring.

**Severity:** `med`. Higher when the function is on a public boundary.

[full pattern block: severity, why-template, suggest-template, correct, wrong]

## Pattern: no clear request/operation boundary

**What to look for:** a code path that performs an end-to-end operation (input → I/O → output) but the work is spread across multiple unscoped helpers with no enclosing function to attach a boundary span to. The "operation" is structural, not lexical.

[full pattern block]

## Pattern: errors as opaque strings

**What to look for:** error returns use `errors.New("invalid request")` / `raise ValueError("invalid request")` instead of typed/categorized error values that downstream code can match on (`errors.Is`, `isinstance`). Telemetry can attach the message but not classify the failure.

[full pattern block]

## Pattern: ambient state instead of context propagation

**What to look for:** a function that reads from a package-level global, a thread-local, or `os.Getenv` mid-operation instead of accepting parameters or reading from a propagated context. Hostile to per-request scoping in traces and metrics.

[full pattern block]

## Pattern: deep nesting hides error edges

**What to look for:** ≥3 nested `if err != nil` / `try` blocks within a function, where each error edge would warrant distinct telemetry but the structure makes wrapping each individually visually impossible.

[full pattern block]

## What NOT to flag

- Genuine pipelines (Go channel stages, generator chains) where the I/O concerns are explicitly composed and each stage has its own observable surface — even if they share a function.
- Helper functions deliberately sized to be inlined at use sites (very small, single-purpose).
- Recursive descent parsers / interpreters where deep nesting is the algorithm, not an o11y problem.

## Action checklist

When the agent reaches step 4.3 dimension 3:

1. Scan each surviving file for each pattern above.
2. Forward candidates to step 4.4.
````

The implementer must replace each `[full pattern block]` with a complete six-element block.

- [ ] **Step 2: Verify no placeholders remain**

```bash
grep -n '\[full pattern block\]\|\[same shape\]\|\[transcribe' skills/observablip/references/structure-for-telemetry.md
```

Expected: no output.

- [ ] **Step 3: Lint**

```bash
pnpm lint
```

- [ ] **Step 4: Commit**

```bash
git add skills/observablip/references/structure-for-telemetry.md
git commit -m "feat(observablip): add structure-for-telemetry rubric"
```

---

### Task 7: `references/false-positive-review.md`

**Files:**

- Create: `skills/observablip/references/false-positive-review.md`

**Source spec sections:** 4.4 (False-positive review pass).

- [ ] **Step 1: Write the file**

Required structure:

````markdown
# False-positive review

Loaded at pipeline step 4.4. Every candidate finding produced by step 4.3 is run through the four checks below in order. A candidate is dropped on the *first* check it fails. Surviving findings move to step 4.5; dropped ones increment the `fp-dropped` footer counter.

## Check 1: deliberate no-op fastpath

**Question:** is the candidate flagging a code path that exists *because* it's deliberately uninstrumented? (E.g., a feature-gate short-circuit that returns early before any work; a no-op stub for a disabled dependency.)

**Decision:** drop if yes — instrumenting a no-op fastpath produces noise, not signal.

[correct/wrong example pair]

## Check 2: outer middleware already covers it

**Question:** does an outer middleware, decorator, or interceptor in the same file (or imported via a clearly-named symbol like `WithTracing`, `@traced`, `RequestLogger`) already wrap the candidate's code path?

**Decision:** drop if yes — the boundary span/log is already attached one level up. Look in the same file before deciding; do not assume across imports without evidence.

[correct/wrong example pair]

## Check 3: covered at a higher boundary

**Question:** does the candidate's parent caller already attach a span/log/metric covering the same unit of work? Look one to two stack frames up if visible in the same file.

**Decision:** drop if yes. Keep if the parent frame is not visible in the file under audit (do not assume).

[correct/wrong example pair]

## Check 4: missing context is present elsewhere in the chain

**Question:** is the "missing context" the candidate flags actually attached at a different point in the operation (e.g., the request ID is added by the framework on entry; the user ID is in the context object the function accepts)?

**Decision:** drop if yes.

[correct/wrong example pair]

## What NOT to drop

- Findings where the rubric pattern is matched but the FP check is "the user might prefer a different tool." Subjective preference is not a false positive.
- Findings where the only counter-evidence is a comment promising future instrumentation.

## Action checklist

When the agent reaches step 4.4:

1. For each candidate from step 4.3, run checks 1–4 in order.
2. Drop on first match. Increment `n_fp_dropped`.
3. Surviving candidates pass to step 4.5 with their original dimension, severity, and templates intact.
````

The implementer must populate the four `[correct/wrong example pair]` placeholders, biasing examples toward Go and Python.

- [ ] **Step 2: Verify no placeholders remain**

```bash
grep -n '\[correct/wrong example pair\]\|\[same shape\]\|\[transcribe\|\[full pattern block\]' skills/observablip/references/false-positive-review.md
```

Expected: no output.

- [ ] **Step 3: Lint**

```bash
pnpm lint
```

- [ ] **Step 4: Commit**

```bash
git add skills/observablip/references/false-positive-review.md
git commit -m "feat(observablip): add false-positive review rubric"
```

---

## Phase 3 — Skill entry points

### Task 8: `skills/observablip/README.md`

Per-skill, human-facing. Brief — links to `SKILL.md`, install command, two-paragraph what-it-does, non-goals. Agents do not load this; it exists for humans browsing the GitHub repo.

**Files:**

- Create: `skills/observablip/README.md`

- [ ] **Step 1: Write the file**

````markdown
# observablip

A read-only Claude Code skill that audits a target codebase for missing telemetry, poor observability practices, and code structure that resists instrumentation. Emits a ranked, bounded list of findings — no patches, no autofix.

## Install

```bash
npx skills add xornivore/skills@observablip --agent claude-code -y
```

## What it does

When invoked, observablip walks the target (a path, glob, or `--diff` rev range), filters out files with no observable surface area, applies a three-dimension rubric (missing telemetry, poor practices, structure-for-telemetry), runs each candidate through a false-positive review pass, and emits up to `--max` findings (default 20) ranked by severity and blast radius. Each finding names the file and line, the o11y dimension, the concrete consequence of leaving the gap, and the *shape* of the fix.

The skill is read-only by design. It never edits files, runs target code, or recommends a specific telemetry vendor unless that vendor is already imported in the codebase.

## Non-goals

- Apply patches or autofix.
- Suggest architectural rewrites beyond the current function/file.
- Review for security, performance, correctness, or test coverage.
- Recommend specific telemetry vendors or backends.
- Score, grade, or rate the codebase.

## Entry point

Skill instructions live in [`SKILL.md`](./SKILL.md). The full design is in [`docs/superpowers/specs/2026-04-30-observablip-design.md`](../../docs/superpowers/specs/2026-04-30-observablip-design.md).
````

- [ ] **Step 2: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 3: Commit**

```bash
git add skills/observablip/README.md
git commit -m "docs(observablip): add per-skill README"
```

---

### Task 9: `skills/observablip/SKILL.md`

The skill's stage-2 entry point. Lean, decision-focused. Target ~150–200 lines.

**Files:**

- Create: `skills/observablip/SKILL.md`

**Source spec sections:** 1, 2, 3, 4, 6, 8.

- [ ] **Step 1: Write the file**

Use this exact frontmatter and structure. Substitute the trigger phrases from spec section 3 into the description; keep the description front-loaded with the most-used phrasings.

````markdown
---
name: observablip
description: Audits a codebase for missing telemetry, poor observability practices, and code structure that resists instrumentation. Read-only — emits a ranked, bounded finding list with no patches. Triggered by phrases like "observablip this", "observablip `pkg/foo`", "audit observability", "review telemetry", "find missing spans", "audit o11y on this PR", "review my logging", or any request to audit a codebase for observability gaps.
license: MIT
compatibility: Designed for Claude Code (or similar agentskills.io-compatible clients).
---

# observablip

Audits a codebase for missing telemetry, poor observability practices, and code structure that resists instrumentation. Read-only — emits a ranked, bounded finding list with no patches.

## Install

```bash
npx skills add xornivore/skills@observablip --agent claude-code -y
```

## When to use

Invoke when the user:

- Asks to audit, review, or "observablip" a path, package, glob, or PR diff.
- Mentions missing spans, missing logs, missing metrics, or "observability" / "telemetry" review.
- Asks "is this instrumented well enough?" or "what's missing for o11y in `X`?".

Do not invoke for:

- Requests to *write* or *apply* telemetry — observablip is read-only. Hand off to the user once findings are emitted.
- Security review, performance review, correctness review, or test coverage review.
- Vendor selection ("should I use Datadog or Honeycomb?").
- Audits from runtime data (traces, logs, metrics dumps). observablip reads source files only.

## Hard rules

[transcribe spec section 6 — six rules, each with its audit cue, in skill-instruction voice. Use imperative mood: "Never edit files", "Never quote …", etc. Keep audit cues verbatim from the spec.]

## Reference index

Read each reference only at the pipeline step that loads it. Each reference ends with `## Action checklist` — load and jump there.

- [output-schema](./references/output-schema.md) — finding fields, ranking, footer format. Load at step 4.5 (rank and emit).
- [precheck](./references/precheck.md) — observable-surface-area criteria + skip categories. Load at step 4.2 (per-file precheck).
- [missing-telemetry](./references/missing-telemetry.md) — rubric dimension 1. Load at step 4.3 dim 1.
- [poor-practices](./references/poor-practices.md) — rubric dimension 2 + secret/PII regex set. Load at step 4.3 dim 2.
- [structure-for-telemetry](./references/structure-for-telemetry.md) — rubric dimension 3. Load at step 4.3 dim 3.
- [false-positive-review](./references/false-positive-review.md) — FP-pass rubric. Load at step 4.4.

The per-finding render template lives at `assets/finding-template.md`, loaded at the emit substep of step 4.5.

## Top-level action checklist (when invoked)

1. **Resolve target.** Expand the path/glob (or `--diff` rev range) to a concrete file set. If the count exceeds 200, halt with a "narrow the target" prompt — never partially scan.
2. **Per-file precheck.** Load [precheck](./references/precheck.md). For each file, apply the pass criteria; assign a skip reason from the fixed set if it fails. Record the rejection log for the footer.
3. **Apply rubric.** For each surviving file:
   1. Load [missing-telemetry](./references/missing-telemetry.md); produce candidate findings for dimension 1.
   2. Load [poor-practices](./references/poor-practices.md); produce candidates for dimension 2. Apply the secret/PII redaction rule before queueing each candidate.
   3. Load [structure-for-telemetry](./references/structure-for-telemetry.md); produce candidates for dimension 3.
4. **False-positive review.** Load [false-positive-review](./references/false-positive-review.md). Run every candidate through checks 1–4 in order; drop on first match; increment `n_fp_dropped`.
5. **Rank and emit.** Load [output-schema](./references/output-schema.md). Rank surviving findings; render each through `assets/finding-template.md`; emit the footer block. If candidate count exceeds `--max`, render only the top `--max` and append the overflow note.
````

When transcribing hard rules from spec section 6, preserve the audit cues exactly — they are the rule's contract.

- [ ] **Step 2: Verify no placeholders remain**

```bash
grep -n '\[transcribe\|\[same shape\]\|\[full pattern block\]\|TBD\|TODO' skills/observablip/SKILL.md
```

Expected: no output.

- [ ] **Step 3: Frontmatter audit — no angle brackets**

```bash
awk '/^---$/{c++; next} c==1' skills/observablip/SKILL.md | grep -E '[<>]' && echo "VIOLATION" || echo "OK"
```

Expected: `OK`.

- [ ] **Step 4: SKILL.md size check**

```bash
wc -l skills/observablip/SKILL.md
```

Expected: ≤ 500 lines (target 150–200; warn if over 250).

- [ ] **Step 5: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 6: Commit**

```bash
git add skills/observablip/SKILL.md
git commit -m "feat(observablip): add SKILL.md entry point"
```

---

## Phase 4 — Repo integration

### Task 10: Add observablip row to top-level README skills table

**Files:**

- Modify: `README.md` (top-level)

- [ ] **Step 1: Read the current Skills table**

```bash
sed -n '/^## Skills/,/^## /p' README.md
```

The current table has one row (`doxcavate`). Add a second row for `observablip`.

- [ ] **Step 2: Insert the observablip row**

Apply this exact change. The existing table:

````markdown
| Name | Description |
| --- | --- |
| [doxcavate](./skills/doxcavate/SKILL.md) | Produces durable, structured documentation in codebases with sparse docs. Two modes (`survey`, `draft`); review-gated by factcheck and persona passes. |
````

becomes:

````markdown
| Name | Description |
| --- | --- |
| [doxcavate](./skills/doxcavate/SKILL.md) | Produces durable, structured documentation in codebases with sparse docs. Two modes (`survey`, `draft`); review-gated by factcheck and persona passes. |
| [observablip](./skills/observablip/SKILL.md) | Audits a codebase for missing telemetry, poor o11y practices, and code structure that resists instrumentation. Read-only ranked finding list, FP-reviewed and bounded. |
````

- [ ] **Step 3: Lint**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: list observablip in top-level skills table"
```

---

## Phase 5 — Validation

### Task 11: Final validation pass

Runs every gate from spec section 9 plus every audit cue from the hard rules.

**Files:** none modified by this task. All gates are read-only checks.

- [ ] **Step 1: `pnpm lint`**

```bash
pnpm lint
```

Expected: `0 error(s)`.

- [ ] **Step 2: `npx skills-ref validate`**

```bash
npx skills-ref validate ./skills/observablip
```

Expected: exit 0. If `skills-ref` is not resolvable, install from <https://github.com/agentskills/agentskills/tree/main/skills-ref> per `skills/CLAUDE.md` 6.

If validation produces warnings or errors, fix the underlying issue in the relevant file, re-commit, and re-run. Do not bypass.

- [ ] **Step 3: Frontmatter audit — no angle brackets in SKILL.md**

```bash
awk '/^---$/{c++; next} c==1' skills/observablip/SKILL.md | grep -E '[<>]' && echo "VIOLATION" || echo "OK"
```

Expected: `OK`.

- [ ] **Step 4: File-reference depth audit — no link in SKILL.md goes deeper than 1 level**

```bash
grep -nE '\]\(\./[^)]+/[^)]+/[^)]+\)' skills/observablip/SKILL.md
```

Expected: no output. Any hit means a reference goes ≥ 2 levels deep, which violates `skills/CLAUDE.md` 1.

- [ ] **Step 5: Author-attribution audit — hard rule 2**

```bash
grep -rE '@[a-zA-Z0-9_-]+|<[^>]+@[^>]+>' skills/observablip/
```

Expected: any hits must be unrelated to author attribution (e.g., `@example.com` inside a regex example). Verify each hit by hand.

- [ ] **Step 6: Section-sign audit — repo doc convention**

```bash
grep -rn '§' skills/observablip/
```

Expected: no output.

- [ ] **Step 7: Skill folder ↔ name match — agentskills.io spec**

```bash
awk '/^name:/{print $2}' skills/observablip/SKILL.md
```

Expected: `observablip` (matches the directory name byte-for-byte).

- [ ] **Step 8: SKILL.md size**

```bash
wc -l skills/observablip/SKILL.md
```

Expected: ≤ 500 lines.

- [ ] **Step 9: Final commit (only if any of the above produced a fix-commit since Task 10)**

If steps 1–8 all passed without changes, skip this step. Otherwise the fixes will already have been committed.

- [ ] **Step 10: Push and open PR**

```bash
git push -u origin skill/observablip
gh pr create --title "feat(observablip): add o11y-audit skill" --body "$(cat <<'EOF'
## Summary

- New read-only skill that audits a target for missing telemetry, poor o11y practices, and code structure that resists instrumentation.
- Single mode (`audit`); precheck filter + three-dimension rubric + FP review + ranked, bounded emit.
- Spec: docs/superpowers/specs/2026-04-30-observablip-design.md
- Plan: docs/superpowers/plans/2026-04-30-observablip.md

## Test plan

- [ ] `pnpm lint` clean on the PR branch
- [ ] `npx skills-ref validate ./skills/observablip` exits 0
- [ ] Hand-run observablip against a small Go and Python sample to spot-check finding quality
- [ ] Verify the six hard-rule audit cues (frontmatter, depth, author, section sign, name match, size)
EOF
)"
```

Expected: PR opens cleanly. CI runs `pnpm lint` and `commitlint`.

---

## Self-review

Run after the plan is written, before handing back to the user.

**1. Spec coverage.** Each spec section maps to at least one task:

- §1 Goal → header.
- §2 Non-goals → README (Task 8) + SKILL.md "When to use" (Task 9).
- §3 Invocation → SKILL.md frontmatter description + "When to use" (Task 9).
- §4.1 Resolve target → SKILL.md action checklist step 1 (Task 9).
- §4.2 Per-file precheck → references/precheck.md (Task 3).
- §4.3 Apply rubric → references/missing-telemetry.md, poor-practices.md, structure-for-telemetry.md (Tasks 4–6).
- §4.4 FP review → references/false-positive-review.md (Task 7).
- §4.5 Rank and emit → references/output-schema.md + assets/finding-template.md (Tasks 1, 2).
- §5 Output schema → references/output-schema.md + assets/finding-template.md (Tasks 1, 2).
- §6 Hard rules → SKILL.md (Task 9), audit cues verified in Task 11.
- §7 Folder layout → established by Tasks 1–9.
- §8 SKILL.md structure → Task 9.
- §9 Validation → Task 11.
- §10 Repo integration → Task 10 (top-level README); plus the install command embedded in Tasks 8, 9.
- §11 Open questions → none.

No gaps.

**2. Placeholder scan.** All `[transcribe …]`, `[same shape]`, `[full pattern block]`, and `[correct/wrong example pair]` markers in this plan are *instructions to the implementer*, paired with a verify-step that fails if the marker survives in the produced file. They are not unfilled placeholders in the plan itself.

**3. Type consistency.** Reference filenames are byte-identical across the file structure block, the SKILL.md reference index (Task 9), and each task title. Pipeline step numbers (4.1–4.5) are consistent across the spec, the SKILL.md action checklist, and each reference's "Action checklist" section. The skip-reason set (`generated`, `no-io`, `test-fixture`, `pure-data`, `vendored`) is consistent between Task 1's footer template and Task 3's `precheck.md`.
