# False-positive review

Load this reference at pipeline step 4.4. Apply it to every candidate
produced by step 4.3 before any finding reaches the output.

**Polarity note — read this before applying any check.** In the dimension
rubrics (missing-telemetry, poor-practices, structure-for-telemetry),
**Correct** means "code is good — do not flag" and **Wrong** means "code
has a problem — flag it." This file inverts that polarity. Here, a
**candidate already exists** and the question is whether to keep it or
discard it. **Correct (do not drop)** means "the candidate is real —
forward it to step 4.5." **Wrong (drop the candidate)** means "the
candidate is a false positive — discard it and increment `n_fp_dropped`."

Every candidate finding from step 4.3 passes through the four checks below
in order. A candidate is dropped on the **first check it fails** (i.e., the
first check that returns yes). Surviving candidates move to step 4.5; dropped
ones increment the `fp-dropped` footer counter — see
[output-schema](./output-schema.md).

## Check 1: deliberate no-op fastpath

**Question:** is the candidate flagging a code path that exists because it
is deliberately uninstrumented? Examples: a feature-gate short-circuit that
returns early before any work; a no-op stub for a disabled dependency; a
benchmark/test-only path guarded by a build tag.

**Decision:** drop the candidate if yes — instrumenting a no-op fastpath
produces noise, not signal.

**How to detect:** look for a guard at the top of the function whose body
returns immediately (`if !flag.Enabled() { return nil }`,
`if disabled { return }`), a build tag (`//go:build`), or a feature-gate
flag whose name matches `disabled|noop|stub|skip`.

**Correct (do not drop) — candidate survives:**

```go
// Candidate: missing-telemetry / operation without span at request boundary
// FP check: the guard returns only when auth is disabled; the hot path
// proceeds to real work — no-op fastpath rule does NOT apply.
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) {
    if s.flags.AuthDisabled() {
        // auth gate: skips auth check, but ingest work continues below
        s.doIngest(w, r)
        return
    }
    if err := s.auth.Verify(r.Context(), r); err != nil {
        http.Error(w, "unauthorized", http.StatusUnauthorized)
        return
    }
    s.doIngest(w, r)
}

func (s *Server) doIngest(w http.ResponseWriter, r *http.Request) {
    // No span — this is the real work path; the candidate stands.
    if err := s.queue.Publish(r.Context(), r.Body); err != nil {
        http.Error(w, "publish failed", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusAccepted)
}
```

**Wrong (drop the candidate) — false positive:**

```go
//go:build noop

// Candidate: missing-telemetry / operation without span at request boundary
// FP check: the entire file is compiled only under the "noop" build tag;
// the function body returns immediately with no I/O — instrumenting this
// path is pure noise. Drop the candidate.
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusAccepted)
}
```

## Check 2: outer middleware/decorator covers it

**Question:** does an outer middleware, decorator, or interceptor in the same
file (or imported via a clearly-named symbol like `WithTracing`, `@traced`,
`RequestLogger`, `Instrumented(...)`) already wrap the candidate's code path?

**Decision:** drop the candidate if yes — the boundary span/log is already
attached one level up. Look in the same file before deciding; do not assume
across imports without evidence.

**How to detect:** search the same file for known middleware/decorator names
(`WithTracing`, `Instrumented`, `@traced`, `@traceable`, `@with_tracing`,
`RequestLogger`, `Tracing(...)`, `otelhttp.NewHandler`); confirm the
candidate's function is registered through one of them.

**Correct (do not drop) — candidate survives:**

```python
# Candidate: missing-telemetry / missing structured log at boundary
# FP check: no middleware or decorator wraps process_job in this file;
# the candidate is real — forward it to step 4.5.
import logging

logger = logging.getLogger(__name__)


def process_job(job_id: str, payload: dict) -> dict:
    # No structured log at entry or exit — the candidate stands.
    result = _run(payload)
    return result


def main() -> None:
    jobs = _fetch_jobs()
    for job in jobs:
        process_job(job["id"], job["data"])
```

**Wrong (drop the candidate) — false positive:**

```python
# Candidate: missing-telemetry / missing structured log at boundary
# FP check: the same file registers process_job through @with_tracing,
# which supplies the boundary span and log — the candidate is redundant.
# Drop it.
from tracing import with_tracing
import logging

logger = logging.getLogger(__name__)


@with_tracing(event="job.process")
def process_job(job_id: str, payload: dict) -> dict:
    result = _run(payload)
    return result
```

## Check 3: covered at a higher boundary

**Question:** does the candidate's parent caller (visible in the same file,
one to two stack frames up) already attach a span/log/metric covering the
same unit of work?

**Decision:** drop the candidate if yes — the parent already attaches the
boundary instrumentation. Keep the candidate if the parent frame is not
visible in the file under audit; do not assume across files.

**How to detect:** find a function in the same file that calls the
candidate's function and inspect whether that caller has a span/log at its
entry covering the call.

**Correct (do not drop) — candidate survives:**

```go
// Candidate: missing-telemetry / operation without span at request boundary
// FP check: the caller (handleBatch) is visible in the same file but has
// no span of its own — neither frame provides the boundary instrumentation.
// The candidate stands.
func (s *Server) handleBatch(w http.ResponseWriter, r *http.Request) {
    // No span here either — caller provides no coverage.
    items := parseItems(r.Body)
    for _, item := range items {
        s.processItem(r.Context(), item)
    }
    w.WriteHeader(http.StatusAccepted)
}

func (s *Server) processItem(ctx context.Context, item Item) {
    // No span — candidate flagged this; caller has no span either.
    if err := s.store.Write(ctx, item.Key, item.Value); err != nil {
        s.logger.Error("store.write.failed", "key", item.Key, "err", err)
    }
}
```

**Wrong (drop the candidate) — false positive:**

```go
// Candidate: missing-telemetry / operation without span at request boundary
// FP check: the caller (handleBatch) is visible in the same file and wraps
// the call to processItem inside a span — the parent frame covers this unit
// of work. Drop the candidate.
func (s *Server) handleBatch(w http.ResponseWriter, r *http.Request) {
    ctx, span := s.tracer.Start(r.Context(), "batch.handle")
    defer span.End()

    items := parseItems(r.Body)
    for _, item := range items {
        s.processItem(ctx, item)
    }
    w.WriteHeader(http.StatusAccepted)
}

func (s *Server) processItem(ctx context.Context, item Item) {
    // No span here — but the parent span in handleBatch covers this work.
    if err := s.store.Write(ctx, item.Key, item.Value); err != nil {
        s.logger.Error("store.write.failed", "key", item.Key, "err", err)
    }
}
```

## Check 4: missing context already present in the call chain

**Question:** is the "missing context" the candidate flags actually attached
at a different point in the operation — e.g., the request-id is added by a
framework hook on entry; the user-id is in the `ctx` object the function
accepts and is auto-attached by an OTel processor; the operation-name is set
as a span attribute one frame up?

**Decision:** drop the candidate if the missing context appears anywhere on
the visible call chain in the same file. Keep if it is genuinely absent
throughout.

**How to detect:** search the same file for the field name (`request_id`,
`tenant_id`, `user_id`, `op`) being set as a span attribute, log field, or
context value; confirm it is on a frame that wraps the candidate.

**Correct (do not drop) — candidate survives:**

```python
# Candidate: poor-practices / missing context — tenant_id absent from span
# FP check: tenant_id is never set as a span attribute or log field anywhere
# in this file's call chain. The candidate is real — forward it.
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def handle_request(payload: dict) -> dict:
    with tracer.start_as_current_span("request.handle"):
        # tenant_id is available in payload but never attached to the span.
        result = process_payload(payload)
        return result


def process_payload(payload: dict) -> dict:
    # Neither this frame nor its caller sets tenant_id on the span.
    return _transform(payload)
```

**Wrong (drop the candidate) — false positive:**

```python
# Candidate: poor-practices / missing context — tenant_id absent from span
# FP check: the parent frame (handle_request) sets tenant_id on the span
# before calling process_payload; the attribute propagates to child spans
# via the OTel context. The candidate "missing tenant_id" is wrong. Drop it.
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def handle_request(tenant_id: str, payload: dict) -> dict:
    with tracer.start_as_current_span("request.handle") as span:
        span.set_attribute("tenant_id", tenant_id)
        result = process_payload(payload)
        return result


def process_payload(payload: dict) -> dict:
    # tenant_id is already on the parent span; no gap here.
    return _transform(payload)
```

## What NOT to drop

- Findings where the rubric pattern is matched but the only counter-argument
  is "the team uses different conventions" or "the user prefers a different
  tool." Subjective preference is not a false positive.
- Findings where the only counter-evidence is a comment promising future
  instrumentation (`// TODO: add span`). A comment is not instrumentation.
- Findings where the proposed fix is described as "too verbose" or
  "stylistic." Keep if the rubric pattern fired.

## Action checklist

When the agent reaches step 4.4:

1. For each candidate produced by step 4.3, run checks 1–4 in order.
2. Drop on the first check that returns yes. Increment `n_fp_dropped`.
3. Surviving candidates pass to step 4.5 with their original dimension,
   severity, why-template, and suggest-template intact — see
   [output-schema](./output-schema.md).

**Audit:** every candidate produced by step 4.3 must appear exactly once in
either the surviving set forwarded to step 4.5 or in `n_fp_dropped`.
