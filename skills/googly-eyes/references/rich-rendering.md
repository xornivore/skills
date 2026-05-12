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
| Severity REQUIRED | bold red (`ESC[1;31m`) | `REQUIRED ·` |
| Severity OPTIONAL | yellow (`ESC[33m`) | `OPTIONAL ·` |
| Severity NIT | cyan (`ESC[36m`) | `NIT ·` |
| Severity FYI | dim (`ESC[2m`) | `FYI ·` |
| Severity PRAISE | green (`ESC[32m`) + `★` glyph | `PRAISE ★ ·` |
| Diff `+` line | green | `+` prefix preserved |
| Diff `-` line | red | `-` prefix preserved |
| File path | bold | (none) |
| Principle | dim | (none) |
| Separator rule | dim | `─` U+2500 repeated to terminal width or 73 |

`ESC` in the table is the escape character (octal `\033`, hex `\x1b`). Emit the literal escape byte when `COLOR=on`.

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
