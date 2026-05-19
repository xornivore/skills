**Status:** draft
**Author:** xornivore
**Date:** 2026-05-19
**Skill folder:** `skills/linearazor/`
**Branch:** `feat/linearazor-labels-and-semantics`
**Extends:** [`2026-05-13-linearazor-design.md`](./2026-05-13-linearazor-design.md).

# linearazor — labels filter as AND, not OR

## 1. Summary

Flip the `labels` filter in `~/.config/linearazor/<group>.toml` from
union to intersection. A project is in scope only when it carries
**all** of the configured project labels, not at least one of them.

## 2. Motivation

Real workspaces use multiple project-label dimensions at once — team
color (`eng:containers-blue`), quarter (`FY27Q2`), driver
(`Eng-Driven`), customer (`Customer`). Useful scopes are conjunctions
("the blue team's Q2 work"), not disjunctions ("anything blue or
anything Q2"). The union default broadens scope when the user adds a
label, which is the opposite of intent: people add labels to narrow.

The change also makes the filter compose naturally with the
scope-hygiene stall from
[`2026-05-19-linearazor-scope-hygiene-and-stalls-design.md`](./2026-05-19-linearazor-scope-hygiene-and-stalls-design.md):
a project that loses its `FY27Q2` tag drops out of the in-scope set
cleanly, and a project mislabeled `FY27Q3` flags itself by being
absent from the brief.

## 3. Scope

Three reference files change. Phase-1 ingest gains a single line of
behavior (intersect, not union). No new config keys, no schema
changes, no new ingest fields.

- `skills/linearazor/references/horizon-and-scope.md` — change
  "carrying at least one of the configured labels" to "carrying every
  one of the configured labels", and the prose under "Label
  resolution" that talks about taking the union of those projects'
  issues.
- `skills/linearazor/references/ingest-and-factsheet.md` — change the
  "Project narrowing" step from a union over per-label `list_projects`
  calls to an intersection.
- `skills/linearazor/references/setup-flow.md` — a one-line note in
  step 4 (project-label scope) explaining that multiple labels narrow
  by intersection.

## 4. Behavior

### 4.1 In-scope set

When `labels = []`, every project under the configured team is in the
candidate set. Unchanged.

When `labels = ["A"]`, the candidate set is every project carrying
label `A`. Unchanged (single-label case looks the same under OR and
AND).

When `labels = ["A", "B"]`, the candidate set is every project
carrying **both** `A` and `B`. **Changed.**

When `labels = ["A", "B", "C"]`, the candidate set is every project
carrying all three. **Changed.**

### 4.2 Phase-1 query plan

Linear MCP's `list_projects --label <id>` filters by a single label.
To intersect across N labels, call once per label and intersect the
returned project-ID sets:

```python
candidate_ids = None
for label_id in resolved_label_ids:
    response = list_projects(team=team_id, label=label_id, limit=50, ...)
    ids = {p.id for p in response.projects}
    candidate_ids = ids if candidate_ids is None else candidate_ids & ids
```

The smallest set wins each iteration, so order doesn't matter. Pagination
loops independently per label call; the intersection is computed across
fully-paginated sets.

### 4.3 Setup flow

Step 4 of the interactive setup remains a pick list of project labels
with free-text additions. The only behavior change is the trailing
explanation:

> Picking multiple labels narrows the scope to projects carrying every
> selected label. To broaden ("blue or Q2"), use a single broader label
> instead.

### 4.4 Empty intersection

When no project carries every configured label, the candidate set is
empty, the in-scope set is empty, and the brief renders the empty-brief
mascot per existing rule
([signal-modes.md](../../../skills/linearazor/references/signal-modes.md)
"Empty-brief case"). The setup-health footer carries a single line
noting the empty intersection so the cause is visible:

```text
Setup health: labels intersection produced 0 projects. Loosen the
labels in ~/.config/linearazor/<group>.toml or pick fewer.
```

## 5. Backward compatibility

Existing configs with a single-label `labels` array behave identically.
Configs with multiple labels were almost never useful under the union
semantic (broader-than-broadest is rarely what people want), so the
risk of a regression on existing users is low.

If a user relied on the union behavior, the migration path is one of:

- Use a broader single label (often the right answer — the union of
  several specific labels is usually expressible as one looser label).
- Run the skill twice with different `labels` and read both briefs.

No deprecation period; the change ships in one PR with a clear
release note.

## 6. Audit

- For every shipped brief, the set of projects appearing as
  sub-headers in any lane must be a subset of the intersection of
  `list_projects --label <id>` over each configured label.
- For configs with `labels.length > 1`, no project sub-header may
  carry a label set that misses any one of the configured labels.

## 7. Out of scope

- Mixed semantics (e.g. `labels_any = [...]` + `labels_all = [...]`).
  Two config keys for one filter is too many — most workspaces resolve
  to a single conjunction. Revisit if a real user wants the mix.
- Negative filters (`labels_not = [...]`). Same reasoning.
- Issue-label filtering. The skill scopes by project labels only;
  issue labels remain metadata in `openIssues[].labels`.

## 8. Open questions

None.
