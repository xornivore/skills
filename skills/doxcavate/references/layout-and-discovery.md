# Layout and path discovery

Sniff before writing anything. Resolve the active config, the docs root,
and the storage mode in this order.

## Discovery order

1. `$DOXCAVATE_CONFIG` env var — honor it.
2. `.doxcavate.yml` at repo root — honor it.
3. `~/.config/doxcavate/<repo-key>.yml` — honor it (see
   [Repo keying for external state](#repo-keying-for-external-state) —
   supports shadow mode and "hostile repo" use).
4. `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` declares a docs path — honor it.
5. Repo already has a `docs/` tree or co-located `<area>/docs/` dirs — match
   the existing convention.
6. Default to **hybrid layout**:
   - Repo-root `docs/` for cross-cutting docs:
     `docs/index.md`, `docs/glossary.md`, `docs/service-map.md`,
     `docs/runbook-*.md`, `docs/learning-path-*.md`.
   - Co-located `docs/` subdirs adjacent to source for
     `how-it-works-*.md` leaves and a per-subdir `index.md`
     (e.g. `pkg/<area>/docs/`, `services/<svc>/docs/`,
     `<module>/docs/` — match whatever the repo already calls a
     "code area").

Whatever the choice, write it back to the active config file (creating it
on first run) so subsequent invocations don't re-decide.

## Storage modes

### integrated (default)

Config and docs live inside the host repo (`.doxcavate.yml`, repo-root
`docs/`, co-located `<area>/docs/`). The team gets the docs in version
control where they belong.

### shadow

Config and docs live in a user-local tree, fully outside the host repo:

- Config: `~/.config/doxcavate/<repo-key>.yml`
- Docs root: `~/.local/share/doxcavate/<repo-key>/docs/`
  (mirrors the same hybrid layout, just re-rooted)

Shadow exists for the **solo-contributor-in-a-hostile-repo** case: a
contributor wants to make progress on personal documentation sanity in a
codebase where committing meta-files or new top-level dirs is not
practical (team resistance, frozen scope, contractor boundaries, etc.).
Shadow docs use the same kinds, anchors, and sizing as integrated docs;
the only differences are the root path and a `shadow: true` flag in the
front-matter so the two trees never get confused if both ever coexist.

## Repo keying for external state

When config or docs live outside the repo, doxcavate needs a stable key
per repo. Resolution order:

1. `git remote get-url origin` — slugified host + path
   (e.g., `github.com_acme_widgets`). Preferred.
2. Else: SHA1 of the repo's absolute filesystem path, truncated to 12
   chars.

Record the chosen key in the config so the same repo doesn't get re-keyed
if its remote changes later.

## Mode selection

- **Explicit:** the active config file sets `mode: integrated | shadow`.
- **Implicit:** if no config is found and a write is about to happen, ask
  the user once whether to go integrated or shadow, then write the answer
  to the appropriate config location.

Never silently write outside the host repo. Never silently add meta-files
to a repo that doesn't already have any.

## Action checklist (when invoked)

When doxcavate is invoked in a new repo:

1. Walk the discovery order; resolve the config file path (or that none
   exists yet).
2. If no config exists and a write is about to happen, ask the user once:
   "integrated (commits to this repo) or shadow (user-local, off-repo)?".
   Record the answer in the appropriate config location.
3. Compute and pin the `<repo-key>` (preferring the `origin` remote URL
   slug; falling back to a 12-char SHA1 of the repo path).
4. Resolve the docs root using sniffed conventions or the hybrid default.
