# Poor practices

Load this reference at pipeline step 4.3 when applying dimension 2. This
dimension flags telemetry that exists but is wrong: duplicate logs, unstructured
output, sensitive data in log args, loop spam, ambient clocks, and bare wraps.

## Pattern: log-then-throw / log-then-return

**What to look for:** The same error is logged at an inner layer and then
re-thrown or re-returned to an outer layer that will also log it — producing
duplicate log lines for a single failure. Detect by finding a `log.*Error` /
`logger.error` / `logging.error` call inside an `if err != nil` block (Go) or
an `except` block (Python) that is immediately followed by `return err` or
`raise`.

**Severity:** `med` when at internal layers; `low` for shim adapters whose
only job is catching a third-party error type and re-raising as a domain type.

**Why-template:** "A single failure produces duplicate log lines at multiple
layers — operators searching for the root cause see N copies and lose the
deduplication invariant log queries assume."

**Suggest-template:** "log once at the outer boundary OR delete the inner log;
the inner layer must propagate the error structurally and let the boundary
handle observability."

**Correct (do not flag):**

```go
func (r *Registry) Lookup(ctx context.Context, id string) (*Record, error) {
    rec, err := r.db.QueryRow(ctx, "SELECT * FROM records WHERE id=$1", id)
    if err != nil {
        return nil, fmt.Errorf("registry.lookup id=%s: %w", id, err)
    }
    return rec, nil
}

func (s *Server) HandleLookup(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    rec, err := s.registry.Lookup(r.Context(), id)
    if err != nil {
        s.logger.Error("lookup.failed", "id", id, "err", err)
        http.Error(w, "not found", http.StatusNotFound)
        return
    }
    _ = json.NewEncoder(w).Encode(rec)
}
```

**Wrong (flag this):**

```go
func (r *Registry) Lookup(ctx context.Context, id string) (*Record, error) {
    rec, err := r.db.QueryRow(ctx, "SELECT * FROM records WHERE id=$1", id)
    if err != nil {
        r.logger.Error("lookup.failed", "id", id, "err", err) // inner log
        return nil, fmt.Errorf("registry.lookup id=%s: %w", id, err)
    }
    return rec, nil
}

func (s *Server) HandleLookup(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    rec, err := s.registry.Lookup(r.Context(), id)
    if err != nil {
        s.logger.Error("lookup.failed", "id", id, "err", err) // duplicate log
        http.Error(w, "not found", http.StatusNotFound)
        return
    }
    _ = json.NewEncoder(w).Encode(rec)
}
```

## Pattern: log-as-print

**What to look for:** `fmt.Println` / `fmt.Printf` / `print()` / `console.log`
used in production code paths — outside test files and outside `cmd/*` startup
banners — instead of a structured logger.

**Severity:** `med`.

**Why-template:** "Output has no level, no timestamp, and no fields — operators
cannot filter by severity or correlate across distributed components; the line
is invisible to log aggregators tuned for structured input."

**Suggest-template:** "replace with the project's structured logger at level
`info` / `warn` / `error` and attach key fields as structured attributes."

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
def process_job(job_id: str, payload: dict) -> dict:
    print(f"processing job {job_id}")  # no level, no fields, invisible to aggregators
    result = _run(payload)
    print("done")
    return result
```

## Pattern: unstructured string log

**What to look for:** Values interpolated into the message string instead of
passed as structured fields — e.g., `log.Info(fmt.Sprintf("processed %d items
for user %s", n, user))` in Go or `logger.info(f"processed {n} items for user
{user}")` in Python. The signal is a format-string call or f-string as the
first argument to the logger.

**Severity:** `med`.

**Why-template:** "Field values are baked into the message string — log queries
cannot filter or aggregate by `user_id` or `item_count`; every variation
creates a new unique message that breaks cardinality-bounded dashboards."

**Suggest-template:** "emit the log with a stable message string and pass
values as structured fields — `logger.info("{verb}.{noun}", count=n,
user_id=user)`."

**Correct (do not flag):**

```python
import logging

logger = logging.getLogger(__name__)


def ingest(user: str, items: list) -> None:
    logger.info("items.processed", extra={"user_id": user, "item_count": len(items)})
```

**Wrong (flag this):**

```python
import logging

logger = logging.getLogger(__name__)


def ingest(user: str, items: list) -> None:
    logger.info(f"processed {len(items)} items for user {user}")  # values in message
```

## Pattern: raw PII or secret in log args

**What to look for:** A log call passes a value that matches one of the regex
shapes from the [Secret / PII regex set](#secret--pii-regex-set) as a
top-level argument, with no apparent redaction — the raw email address, token
string, or key value is passed directly to a log method.

**Severity:** `high`.

**Why-template:** "Sensitive data flows into log retention — emails, tokens, or
keys end up in long-lived storage and downstream search indexes, creating
compliance and breach exposure."

**Suggest-template:** "redact at log-call time — replace the value with a
stable hash, a length-only marker (`len=N`), or a typed placeholder; never
pass the raw value."

**Correct (do not flag):**

```go
func (s *Server) HandleLogin(w http.ResponseWriter, r *http.Request) {
    email := r.FormValue("email")
    s.logger.Info("login.attempt", "email_hash", sha256hex(email))
    if err := s.auth.Verify(r.Context(), email, r.FormValue("password")); err != nil {
        s.logger.Warn("login.failed", "email_hash", sha256hex(email), "err", err)
        http.Error(w, "unauthorized", http.StatusUnauthorized)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

**Wrong (flag this):**

```go
func (s *Server) HandleLogin(w http.ResponseWriter, r *http.Request) {
    email := r.FormValue("email")
    s.logger.Info("login.attempt", "email", email) // raw email in log arg
    if err := s.auth.Verify(r.Context(), email, r.FormValue("password")); err != nil {
        s.logger.Warn("login.failed", "email", email, "err", err) // raw email in log arg
        http.Error(w, "unauthorized", http.StatusUnauthorized)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

When producing a finding from this pattern, the finding text must describe the
shape (e.g., "a log call passes a raw email field") rather than quoting the
matched line verbatim. This is hard rule 3 from the spec. Apply the redaction
rule from the regex set BEFORE adding the candidate to the queue.

## Pattern: log spam in tight loops

**What to look for:** A `log.Info` / `logger.info` / equivalent call inside a
loop body with no rate-limit guard, sample counter, or "log on state
transition" condition. The loop must iterate at request rate or on a
hot ticker; apply this only when the loop body executes more than once per
inbound request or per scheduler tick.

**Severity:** `med` when the enclosing function is an HTTP handler, RPC method,
queue consumer, or hot-ticker callback (recognizable by signature or transport
registration in the same file); `low` when the loop iterates over a value
bounded at the call site by a literal or const N < 10.

**Why-template:** "A single request produces thousands of log lines — log
volume drowns alerting, rate-limits ingestion, and increases retention cost
without proportional signal."

**Suggest-template:** "log the loop entry and exit with counts, error count,
and duration instead of per-iteration; if per-iteration logging is required,
sample every `{sample_n}`th iteration or guard on a state transition."

**Correct (do not flag):**

```python
import logging

logger = logging.getLogger(__name__)


def drain_queue(queue: list) -> int:
    error_count = 0
    logger.info("queue.drain.start", extra={"size": len(queue)})
    for item in queue:
        if not _process(item):
            error_count += 1
    logger.info(
        "queue.drain.done",
        extra={"size": len(queue), "errors": error_count},
    )
    return error_count
```

**Wrong (flag this):**

```python
import logging

logger = logging.getLogger(__name__)


def drain_queue(queue: list) -> int:
    error_count = 0
    for item in queue:
        logger.info("processing item", extra={"item": item})  # log per iteration
        if not _process(item):
            error_count += 1
    return error_count
```

## Pattern: ambient `time.Now()` in observable paths

**What to look for:** A function that emits a timestamp into a metric or span
attribute reads `time.Now()` directly instead of accepting an injected clock or
a `now`-typed function reference. The signal is a bare `time.Now()` call inside
a function that also calls a metrics recorder, span attribute setter, or
structured log with a time field.

**Severity:** `low`.

**Why-template:** "Tests cannot pin time; replicas with skewed clocks emit
inconsistent timestamps that break time-window aggregation and replay
debugging."

**Suggest-template:** "accept a `clock` parameter (interface or function
reference) defaulting to `time.Now`, then inject a fake clock in tests."

**Correct (do not flag):**

```go
type Recorder struct {
    clock func() time.Time
}

func (r *Recorder) RecordLatency(ctx context.Context, rec metrics.Recorder, start time.Time) {
    rec.RecordDuration(ctx, "op.duration_seconds", r.clock().Sub(start))
}
```

**Wrong (flag this):**

```go
type Recorder struct{}

func (r *Recorder) RecordLatency(ctx context.Context, rec metrics.Recorder, start time.Time) {
    rec.RecordDuration(ctx, "op.duration_seconds", time.Now().Sub(start))
}
```

## Pattern: error wrap with no metadata

**What to look for:** `fmt.Errorf("label: %w", err)` / `raise DomainError(str(e)) from e`
that preserves the chain but adds no structured fields — no operation name, no
key identifier (ID, path, batch), no attempt count. The pattern is a wrap whose
string literal contains only a fixed label with no `%s` / `%d` interpolations
for call-site data.

**Severity:** `med`.

**Why-template:** "The wrap chain shows the call path but adds no operation
context — operators see `ingest: write: connection refused` but not which key,
retry, or batch the call was for."

**Suggest-template:** "include op-relevant fields as interpolations or typed
error attributes — `fmt.Errorf("{op_name} key=%s attempt=%d: %w", {key},
{n}, err)` or a structured-error type with named fields."

**Correct (do not flag):**

```go
func (w *Writer) Write(ctx context.Context, key string, n int, data []byte) error {
    if err := w.store.Put(ctx, key, data); err != nil {
        return fmt.Errorf("writer.write key=%s attempt=%d: %w", key, n, err)
    }
    return nil
}
```

**Wrong (flag this):**

```go
func (w *Writer) Write(ctx context.Context, key string, n int, data []byte) error {
    if err := w.store.Put(ctx, key, data); err != nil {
        return fmt.Errorf("writer.write: %w", err) // no key, no attempt count
    }
    return nil
}
```

## Secret / PII regex set

The audit cue for spec hard rule 3 references this list. When emitting a
finding from the "raw PII or secret in log args" pattern, the finding must NOT
include any string literal matching the regexes below. Redact at
finding-render time.

- **Email:** `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
- **JWT:** `eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}`
- **Bearer token header:** `[Bb]earer\s+[A-Za-z0-9._\-]{16,}`
- **AWS access key ID:** `AKIA[0-9A-Z]{16}`
- **High-entropy hex/base64 >= 32 chars near a key-like token:** `(?i)\b(secret|token|key|password|pwd)\b[^=]{0,16}[=:\s]\s*['"]?[A-Za-z0-9+/=_-]{32,}`

Render rule: when emitting a finding that quotes a code region matching any of
these, replace the offending substring with `[redacted]` and surface the field
name and shape in the finding's `why_this_matters`.

## What NOT to flag

- Logs in `cmd/*` startup output (banner, version, listening address) — these
  are operator-facing and unstructured by convention.
- Test-time `t.Logf` / `print` calls — tests are out of scope for this
  dimension.
- Wrap chains that deliberately drop metadata to anonymize at a trust boundary.

## Action checklist

When the agent reaches step 4.3 dimension 2:

1. Scan each surviving file from [precheck](./precheck.md) for each pattern
   above in order.
2. Apply the redaction rule from the secret/PII set BEFORE adding a candidate
   to the queue. The finding's quoted regions must not contain any substring
   matching the regex set.
3. If the codebase already imports OTel / slog / zap / structlog, use that
   vocabulary in `suggest`; otherwise stay neutral.
4. Forward candidates to step 4.4. Shape per
   [assets/finding-template.md](../assets/finding-template.md) — see
   [output-schema](./output-schema.md).

**Audit:** for every emitted finding from this rubric, the rendered output must
not contain a substring matching any regex in the secret/PII set above.
