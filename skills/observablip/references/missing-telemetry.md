# Missing telemetry

Load this reference at pipeline step 4.3 when applying dimension 1. This
dimension flags operations that are invisible to production observability:
no spans at boundaries, errors lacking structured context, missing boundary
logs, unmetered hot paths, and severed trace propagation.

## Pattern: operation without span at request boundary

**What to look for:** A function that handles an external request
(HTTP handler, RPC method, queue consumer, CLI entry point) and performs two
or more sub-operations — network calls, DB writes, cache lookups — with no
surrounding span and no `defer span.End()`. The absence is detectable by
scanning the function body for `tracer.Start` / `otel.Tracer` calls: if
none appear and the function calls two or more external helpers, flag it.

**Severity:** `high` when on a public boundary; `med` otherwise.

**Why-template:** "A failure in any sub-operation is currently
indistinguishable in production logs — there is no boundary span to
correlate them under."

**Suggest-template:** "wrap the operation in a span named `{verb}.{noun}`
with attributes `{salient_inputs}`."

**Correct (do not flag):**

```go
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) {
    ctx, span := s.tracer.Start(r.Context(), "ingest.handle",
        trace.WithAttributes(
            attribute.String("source", r.Header.Get("X-Source")),
        ),
    )
    defer span.End()

    if err := s.queue.Publish(ctx, r.Body); err != nil {
        span.RecordError(err)
        http.Error(w, "publish failed", http.StatusInternalServerError)
        return
    }
    if err := s.store.Write(ctx, r.Body); err != nil {
        span.RecordError(err)
        http.Error(w, "store failed", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusAccepted)
}
```

**Wrong (flag this):**

```go
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) {
    // No span — sub-operations are invisible in traces.
    if err := s.queue.Publish(r.Context(), r.Body); err != nil {
        http.Error(w, "publish failed", http.StatusInternalServerError)
        return
    }
    if err := s.store.Write(r.Context(), r.Body); err != nil {
        http.Error(w, "store failed", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusAccepted)
}
```

## Pattern: error returned without structured context

**What to look for:** A function returns `err` (Go) or raises an exception
(Python) without wrapping it with the operation name and the key input fields
that identify the call site — bare `return err` or `raise` with the original
exception unmodified.

**Severity:** `med`; `high` if at a request boundary.

**Why-template:** "On failure, the operator sees the leaf error string but no
operation context — diagnosing requires reading the call chain."

**Suggest-template:** "wrap the error with `fmt.Errorf` / structured-error
constructor adding op name and key inputs as fields, or attach as span/log
attributes."

**Correct (do not flag):**

```go
func (r *Registry) Lookup(ctx context.Context, id string) (*Record, error) {
    rec, err := r.db.QueryRow(ctx, "SELECT * FROM records WHERE id=$1", id)
    if err != nil {
        return nil, fmt.Errorf("registry.lookup id=%s: %w", id, err)
    }
    return rec, nil
}
```

**Wrong (flag this):**

```go
func (r *Registry) Lookup(ctx context.Context, id string) (*Record, error) {
    rec, err := r.db.QueryRow(ctx, "SELECT * FROM records WHERE id=$1", id)
    if err != nil {
        return nil, err // bare return — no op name, no id in the error
    }
    return rec, nil
}
```

## Pattern: missing structured log at boundary

**What to look for:** An HTTP handler, RPC method, or queue consumer whose
function body contains neither a structured log call at entry nor one at
return — no `log.InfoContext`, `slog.Info`, `logger.With(...).Info(...)`, or
equivalent emitting a stable event name for the operation.

**Severity:** `med` at internal layers; `high` at user-facing boundaries.

**Why-template:** "Throughput, latency, and failure-rate dashboards built on
log queries cannot count this operation, and alerting on error rate for it is
impossible without an anchor event to query."

**Suggest-template:** "emit one structured log at start with event name
`{verb}.{noun}.start` plus key inputs as fields, and one at end with event
name `{verb}.{noun}.done` plus status, duration, and key outputs."

**Correct (do not flag):**

```python
import logging

logger = logging.getLogger(__name__)


def process_job(job_id: str, payload: dict) -> dict:
    logger.info("job.process.start", extra={"job_id": job_id, "size": len(payload)})
    result = _run(payload)
    logger.info("job.process.done", extra={"job_id": job_id, "status": "ok"})
    return result
```

**Wrong (flag this):**

```python
import logging

logger = logging.getLogger(__name__)


def process_job(job_id: str, payload: dict) -> dict:
    # No structured log at entry or exit — the operation is uncountable
    # in log-query dashboards and unalertable on error rate.
    result = _run(payload)
    return result
```

## Pattern: missing metric on hot path

**What to look for:** A loop body, polling function, or request hot path that
executes repeatedly and contains no counter increment, histogram record, or
gauge update measuring throughput, latency, or error rate for that specific
path.

**Severity:** `med`; `low` when the enclosing function (the direct caller
visible in the same file) already records a counter or histogram on this
code path.

**Why-template:** "Performance regressions in this path are invisible — no
metric to detect a 10x slowdown or a stuck loop."

**Suggest-template:** "increment a counter named `{op_name}.calls` on entry,
a counter `{op_name}.errors` on exit-with-error, and a histogram
`{op_name}.duration_seconds` on exit; tag with op name."

**Correct (do not flag):**

```go
func (p *Poller) poll(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        case <-p.ticker.C:
            start := time.Now()
            err := p.check(ctx)
            p.metrics.pollDuration.Record(ctx, time.Since(start).Seconds())
            if err != nil {
                p.metrics.pollErrors.Add(ctx, 1)
            } else {
                p.metrics.pollSuccess.Add(ctx, 1)
            }
        }
    }
}
```

**Wrong (flag this):**

```go
func (p *Poller) poll(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        case <-p.ticker.C:
            // No metrics — a slowdown or error storm is invisible.
            p.check(ctx) //nolint:errcheck
        }
    }
}
```

## Pattern: missing trace/request-ID propagation

**What to look for:** A sub-operation that opens its own context with
`context.Background()` (Go) or issues an outbound HTTP call without
propagating tracing headers (Python `requests.get(url)` with no `headers`
argument injecting trace context) — detaching from the in-flight trace and
severing downstream correlation.

**Severity:** `high` at distributed-system boundaries; `med` for in-process
detached goroutines or threads.

**Why-template:** "Downstream spans/log lines cannot be correlated to the
originating request — distributed traces show two unrelated trees instead
of one."

**Suggest-template:** "thread the existing context (`ctx`) through the call;
for HTTP, use a tracing-aware transport that injects W3C trace headers."

**Correct (do not flag):**

```python
from opentelemetry.propagate import inject


def call_downstream(ctx_headers: dict, url: str) -> dict:
    headers = dict(ctx_headers)
    inject(headers)  # propagates traceparent + tracestate
    resp = requests.get(url, headers=headers, timeout=5)
    resp.raise_for_status()
    return resp.json()
```

**Wrong (flag this):**

```python
def call_downstream(ctx_headers: dict, url: str) -> dict:
    headers = dict(ctx_headers)
    # No inject(headers) — the downstream service starts a new trace root.
    resp = requests.get(url, headers=headers, timeout=5)
    resp.raise_for_status()
    return resp.json()
```

## What NOT to flag

- Files where every operation already has a span and every error already wraps
  with structured context. Use this list to back off the false-positive review.
- Single-call functions that delegate to one already-instrumented helper — the
  helper carries the telemetry; double-wrapping is noise.
- Pure functions with no I/O. These are caught by [precheck](./precheck.md);
  if one slips through, do not flag it here.

## Action checklist

When the agent reaches step 4.3 dimension 1:

1. For each surviving file from [precheck](./precheck.md), scan for each
   pattern above in order.
2. For each match, build a candidate finding using the why-template and
   suggest-template, substituting from the matched code.
3. If the codebase already imports OTel / slog / zap / structlog, use that
   vocabulary in the `suggest` field; otherwise stay neutral.
4. Forward all candidates to step 4.4 (false-positive review). The shape of
   the candidate matches [assets/finding-template.md](../assets/finding-template.md)
   — see [output-schema](./output-schema.md).
