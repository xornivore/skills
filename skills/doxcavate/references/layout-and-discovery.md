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

Three modes, ordered by how much lands in the host repo.

### integrated (default)

Config and docs live inside the host repo (`.doxcavate.yml`, repo-root
`docs/`, co-located `<area>/docs/`). The team gets the docs in version
control where they belong.

### partial

Substance leaves (`how-it-works-*`, `learning-path-*`, `runbook-*`) live
in the host repo; meta docs (`index.md`, `glossary.md`, `service-map.md`)
and config live in the shadow tree:

- Repo: leaves only, under the discovered docs layout.
- Config: `~/.config/doxcavate/<repo-key>.yml`.
- Meta-docs root: `~/.local/share/doxcavate/<repo-key>/docs/`.

`partial` exists for the **partially-hostile-repo** case: the team
accepts substance docs (a `how-it-works-foo.md` next to the code is
uncontroversial) but pushes back on navigation/meta files that read as
documentation infrastructure. The doc plan, glossary, and service map
still get produced and persisted — just in the user-local shadow tree —
so subsequent invocations can read them back.

**Leaves committed to the repo must not link to shadow-located meta
docs.** Shadow paths are per-machine and per-user; rendering
`~/.local/...` links into a committed leaf would break for everyone
else. Leaf-to-leaf cross-references (relative paths within the repo)
are fine; meta-to-leaf references from the shadow tree to repo-committed
leaves use repo-relative paths and resolve correctly when read alongside
the repo.

In `partial` mode, repo-committed leaves carry `shadow: false` and
shadow-located meta docs carry `shadow: true`.

### shadow

Config and all docs live in a user-local tree, fully outside the host
repo:

- Config: `~/.config/doxcavate/<repo-key>.yml`
- Docs root: `~/.local/share/doxcavate/<repo-key>/docs/`
  (mirrors the same hybrid layout, just re-rooted)

Shadow exists for the **fully-hostile-repo** case: a contributor wants
to make progress on personal documentation sanity in a codebase where
committing *anything* under a docs convention is not practical (team
resistance, frozen scope, contractor boundaries, etc.). Shadow docs use
the same kinds, anchors, and sizing as integrated docs; the only
differences are the root path and a `shadow: true` flag in the
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

- **Explicit:** the active config file sets
  `mode: integrated | partial | shadow`.
- **Implicit:** if no config is found and a write is about to happen, ask
  the user once which of the three modes to use, then write the answer
  to the appropriate config location.

Never silently write outside the host repo. Never silently add meta-files
to a repo that doesn't already have any.

## Mode by signal

When running implicit mode selection, recognize the situation rather
than the mode name. The table below maps observable signals to the
recommended mode; the implicit prompt should describe the *effect*
("substance docs near code, navigation in a user-local tree") rather
than the internal name.

| Signal | Recommended mode |
| --- | --- |
| Repo has an existing `docs/` tree, a `.doxcavate.yml`, or a `CLAUDE.md` / `AGENTS.md` declaring a docs path | `integrated` |
| Repo has source-adjacent code areas (`pkg/`, `services/`, etc.) but no top-level `docs/` and no doc meta-files; user is fine committing substance docs near code but not navigation/infrastructure files | `partial` |
| User signals "I can't commit anything to this repo" (contractor codebase, frozen scope, fully read-only or external repo, personal exploration) | `shadow` |
| Inferred default contradicts an explicit user preference | honor the user; record the answer in the config |

User-facing wording for the implicit prompt — describe the effect, not
the name:

1. "Commit everything to this repo" → `integrated`. Default when the
   team welcomes documentation.
2. "Commit substance docs (`how-it-works`, `learning-path`, `runbook`)
   near the code; keep navigation/reference docs (`index`, `glossary`,
   `service-map`) in a user-local tree" → `partial`. Default when the
   team accepts docs near code but pushes back on top-level
   documentation infrastructure.
3. "Keep everything in a user-local tree, off-repo entirely" →
   `shadow`. Default when nothing can be committed to the codebase.

When in doubt, ask. Record the answer in the active config file.

## Action checklist (when invoked)

When doxcavate is invoked in a new repo:

1. Walk the discovery order; resolve the config file path (or that none
   exists yet).
2. If no config exists and a write is about to happen, ask the user once
   which mode to use:

   - `integrated` — commits both leaves and meta docs to this repo.
   - `partial` — commits substance leaves to this repo; meta docs
     (`index.md`, `glossary.md`, `service-map.md`) live in the shadow
     tree.
   - `shadow` — nothing is committed to this repo; everything lives in
     the shadow tree.

   Record the answer in the appropriate config location.
3. Compute and pin the `<repo-key>` (preferring the `origin` remote URL
   slug; falling back to a 12-char SHA1 of the repo path).
4. Resolve the docs root(s) using sniffed conventions or the hybrid
   default. In `partial`, resolve two roots: the repo leaves root
   and the shadow meta-docs root.
