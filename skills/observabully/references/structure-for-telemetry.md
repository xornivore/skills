# Structure for telemetry

Load this reference at pipeline step 4.3 when applying dimension 3. This
dimension flags code shape that resists adding telemetry even when dimensions 1
and 2 do not fire directly.

## Pattern: function mixes unrelated I/O operations

**What to look for:** A single function performs two or more logically distinct
I/O concerns — e.g., ingestion AND notification, fetch AND cache-write, compute
AND persist — with no clear seam between them. Adding a span at the function
level conflates the operations; adding spans inside requires restructuring the
function body first.

**Severity:** `med`; `high` when the function is on a public boundary (HTTP
handler, RPC method, CLI entry, queue consumer, or scheduled job — recognizable
by signature or transport registration in the same file).

**Why-template:** "Telemetry attached to this function aggregates two unrelated
operations under one span — operators see latency and error rates that conflate
{op1} and {op2}, masking which subsystem is failing."

**Suggest-template:** "split into two functions named `{verb1}.{noun1}` and
`{verb2}.{noun2}`; the outer function becomes a coordinator with one span per
inner call."

**Correct (do not flag):**

```go
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) {
    if err := s.ingestRecord(r.Context(), r.Body); err != nil {
        http.Error(w, "ingest failed", http.StatusInternalServerError)
        return
    }
    if err := s.notifyDownstream(r.Context(), r.Body); err != nil {
        http.Error(w, "notify failed", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusAccepted)
}

func (s *Server) ingestRecord(ctx context.Context, body io.Reader) error {
    ctx, span := s.tracer.Start(ctx, "ingest.record")
    defer span.End()
    return s.store.Write(ctx, body)
}

func (s *Server) notifyDownstream(ctx context.Context, body io.Reader) error {
    ctx, span := s.tracer.Start(ctx, "notify.downstream")
    defer span.End()
    return s.queue.Publish(ctx, body)
}
```

**Wrong (flag this):**

```go
func (s *Server) HandleIngest(w http.ResponseWriter, r *http.Request) {
    // Ingest and notify are interleaved — no seam to attach separate spans.
    if err := s.store.Write(r.Context(), r.Body); err != nil {
        http.Error(w, "ingest failed", http.StatusInternalServerError)
        return
    }
    if err := s.queue.Publish(r.Context(), r.Body); err != nil {
        http.Error(w, "notify failed", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusAccepted)
}
```

## Pattern: no clear request/operation boundary

**What to look for:** A code path performs an end-to-end operation (input → I/O
→ output) but the work is spread across multiple unscoped helpers with no
enclosing function to attach a boundary span to. The operation is structural,
not lexical — there is no single call site that represents the full unit of
work.

**Severity:** `med`; `high` when the entry point is a public boundary (HTTP
handler, RPC method, CLI entry, queue consumer — recognizable by signature or
transport registration in the same file) calling the scattered helpers.

**Why-template:** "There is no single point at which to attach a boundary span
or success/failure log — operators reading traces see disconnected sub-spans
without an outer parent linking them as one logical operation."

**Suggest-template:** "wrap the work in a single function named `{verb}.{noun}`
that accepts a `ctx` and returns the result; attach the boundary span at this
new function."

**Correct (do not flag):**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def handle_order(ctx: dict, order_id: str, payload: dict) -> dict:
    with tracer.start_as_current_span("order.process"):
        validated = _validate(payload)
        saved = _save(order_id, validated)
        return _confirm(order_id, saved)
```

**Wrong (flag this):**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def handle_order(ctx: dict, order_id: str, payload: dict) -> dict:
    # No enclosing span — sub-steps emit orphaned spans with no shared parent.
    validated = _validate(payload)
    saved = _save(order_id, validated)
    return _confirm(order_id, saved)
```

## Pattern: errors as opaque strings

**What to look for:** Error returns use `errors.New("invalid request")` (Go) or
`raise ValueError("invalid request")` (Python) instead of typed or categorized
error values that downstream code can match on (`errors.Is` in Go;
`isinstance` over a closed set in Python). Telemetry can attach the message
string but cannot classify the failure class.

**Severity:** `med`.

**Why-template:** "Failure-rate dashboards group all '{error_string}' strings
as one bucket — operators cannot tell whether failures are {cause_a},
{cause_b}, or {cause_c}; classification requires re-parsing the message at
query time."

**Suggest-template:** "define a typed-error set (Go: `var Err{Cause} =
errors.New(...)` plus `errors.Is`; Python: `class {Cause}Error(BaseError)`);
telemetry attaches the typed name as a `failure_kind` attribute."

**Correct (do not flag):**

```go
var (
    ErrMissingField  = errors.New("missing field")
    ErrSchemaMismatch = errors.New("schema mismatch")
    ErrRateLimited   = errors.New("rate limited")
)

func Validate(req *Request) error {
    if req.Name == "" {
        return fmt.Errorf("validate: %w", ErrMissingField)
    }
    if req.Version != expectedVersion {
        return fmt.Errorf("validate: %w", ErrSchemaMismatch)
    }
    return nil
}
```

**Wrong (flag this):**

```go
func Validate(req *Request) error {
    if req.Name == "" {
        return errors.New("invalid request") // opaque — cannot errors.Is
    }
    if req.Version != expectedVersion {
        return errors.New("invalid request") // same string, different cause
    }
    return nil
}
```

## Pattern: ambient state instead of context propagation

**What to look for:** A function reads from a package-level global, a
thread-local, or `os.Getenv` mid-operation instead of accepting the value as a
parameter or reading it from a propagated context. Detectable by a bare global
variable read or `os.Getenv` call inside a function that also performs I/O.
Different requests share the same ambient state and cannot be distinguished by
observability tooling.

**Severity:** `med`; `high` when the ambient read is a tenant ID, request ID,
or user ID — these define the per-request boundary in tracing and are
detectable by variable name matching `tenant`, `request_id`, `user`, or `uid`.

**Why-template:** "Traces and metrics cannot scope by request — a per-tenant
counter increments globally instead of per-tenant, and span attributes show the
last-set value rather than the calling request's value."

**Suggest-template:** "thread the value through `context.Context` (Go) or as an
explicit parameter (Python); attach the value as a span attribute or metric tag
at the function boundary."

**Correct (do not flag):**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def record_event(tenant_id: str, event: dict) -> None:
    with tracer.start_as_current_span("event.record") as span:
        span.set_attribute("tenant_id", tenant_id)
        _write(tenant_id, event)
```

**Wrong (flag this):**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

_current_tenant = ""  # package-level ambient state


def record_event(tenant_id: str, event: dict) -> None:
    with tracer.start_as_current_span("event.record") as span:
        # Parameter is ignored — ambient global wins, telemetry attaches the
        # wrong value when concurrent requests overwrite the global.
        span.set_attribute("tenant_id", _current_tenant)
        _write(_current_tenant, event)
```

## Pattern: deep nesting hides error edges

**What to look for:** Three or more nested `if err != nil` blocks (Go) or
`try` / `except` blocks (Python) within a single function, where each error
edge warrants distinct telemetry context but the nested structure makes wrapping
each individually impractical without first flattening the control flow.

**Severity:** `med`.

**Why-template:** "Each error edge needs distinct context (which sub-step
failed, with what inputs); nested control flow forces a single error label
across all edges, so dashboards cannot distinguish {stage1} failures from
{stage3} failures."

**Suggest-template:** "flatten into early-return guard clauses (Go: `if err !=
nil { return wrap(...) }`; Python: `if err: raise {Stage}Error(stage, ...) from
err`); each return wraps with stage-specific context."

**Correct (do not flag):**

```go
func (p *Pipeline) Run(ctx context.Context, input []byte) ([]byte, error) {
    parsed, err := p.parser.Parse(ctx, input)
    if err != nil {
        return nil, fmt.Errorf("pipeline.run parse: %w", err)
    }
    validated, err := p.validator.Validate(ctx, parsed)
    if err != nil {
        return nil, fmt.Errorf("pipeline.run validate: %w", err)
    }
    result, err := p.executor.Execute(ctx, validated)
    if err != nil {
        return nil, fmt.Errorf("pipeline.run execute: %w", err)
    }
    return result, nil
}
```

**Wrong (flag this):**

```go
func (p *Pipeline) Run(ctx context.Context, input []byte) ([]byte, error) {
    parsed, err := p.parser.Parse(ctx, input)
    if err == nil {
        validated, err := p.validator.Validate(ctx, parsed)
        if err == nil {
            result, err := p.executor.Execute(ctx, validated)
            if err == nil {
                return result, nil
            }
            // all three error edges fall through here — indistinguishable
        }
    }
    return nil, err
}
```

## What NOT to flag

- Genuine pipelines (Go channel stages, generator chains) where I/O concerns
  are explicitly composed and each stage has its own observable surface — even
  if they share a function.
- Helper functions deliberately sized to be inlined at use sites (very small,
  single-purpose).
- Recursive descent parsers or interpreters where deep nesting is the algorithm,
  not an observability problem.

## Action checklist

When the agent reaches step 4.3 dimension 3:

1. For each surviving file from [precheck](./precheck.md), scan for each
   pattern above in order.
2. For each match, build a candidate finding using the why-template and
   suggest-template, substituting names from the matched code.
3. If the codebase already imports OTel / slog / zap / structlog, use that
   vocabulary in `suggest`; otherwise stay neutral.
4. Forward candidates to step 4.4. Shape per
   [assets/finding-template.md](../assets/finding-template.md) — see
   [output-schema](./output-schema.md).
