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
