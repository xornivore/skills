**Status:** draft
**Author:** xornivore
**Date:** 2026-05-19
**Skill folder:** `skills/linearazor/`
**Branch:** `worktree-feat-animation-themes`
**Extends:** [`2026-05-13-linearazor-design.md`](./2026-05-13-linearazor-design.md).

# linearazor — animation themes (second cast: vehicles)

## 1. Summary

The animation cast in `skills/linearazor/assets/animation.md` is hard-coded to a single set of creatures (the "animal kingdom" theme). This spec turns the cast into a themed asset: the lane spec stays canonical, but the *icons* for each lane can be swapped wholesale by a config field.

This change lands one new theme alongside the existing one — **vehicles**, a "things that move" cast — and the plumbing to add more themes later (noir, pirates, space) as presentation-layer-only changes.

Hard rule 12 (the no-art-affects-signals rule, see `SKILL.md`) is preserved: themes are purely affective, no signal-layer file changes when a theme is swapped.

## 2. Motivation

Two reasons:

1. **Reuse fatigue.** The current cast has shipped unchanged since the skill launched. Users who run linearazor weekly see the same eleven creatures every Monday. A second theme is a low-cost way to keep the brief feeling like a thing the user opted into rather than a stock template.
2. **The metaphor lines up.** linearazor's whole reason for existing is to make work *momentum* legible — what's shipping, what's stuck, what's drifting. A cast of vehicles encodes that metaphor directly: a race car ships fast, a wheelbarrow plods, a parked car is silent, a traffic cone blocks. Each lane gets an icon whose everyday meaning already matches the lane's signal.

## 3. Out of scope

- New signals, new lanes, new precedence rules. The lane → role table is unchanged; only the icon per lane swaps.
- Per-project, per-day, or per-mood theme rotation. The theme is a single `[render]` config field; the brief picks one cast per run.
- Per-creature overrides (the way `palette_overrides` lets you swap a single color). If a future user wants "noir cast but the cow for stalls_aging," they'll edit the asset directly.
- Migration tooling. Existing configs without `animation_theme` default to `animal-kingdom` — same cast they have today.
- Shipping noir / pirates / space / any third theme. Those are mentioned in the design as proof the structure scales, but not in this PR.

## 4. Config field

Add to `assets/config-template.toml` under `[render]`:

```toml
animation_theme = "animal-kingdom"   # animal-kingdom | vehicles
```

Validation:

- Value must be one of the themes listed in `assets/animation.md`. Unknown values fall back to `animal-kingdom` with a warning emitted to the chat the way unknown-palette warnings already work (see `references/palettes.md`).
- Missing field = `animal-kingdom` (no warning — that's the default).
- Listed at the *bottom* of the `[render]` block in the template, so users with old configs see it as "new option you might want" rather than something that broke.

The setup flow (`references/setup-flow.md`) asks about theme during the questions arc — one question, default `animal-kingdom`, ENTER to accept. Skippable for users who reconfigure non-interactively.

## 5. Asset structure: one file, multiple themes

`assets/animation.md` is restructured:

```text
# Animation cast

## 1. Lane spec       <-- canonical, theme-agnostic
   - lane roles + tone notes (the "what each lane communicates")
   - left-margin / padding rules
   - precedence rules (stalls precedence, scope-drift sub-flavor)
   - replacement rules
   - audit cues

## 2. Lane → role table   <-- canonical

## 3. Themes
   ### 3.1 Theme: animal-kingdom   <-- the current cast, moved here verbatim
        - one ASCII block per lane
        - setup mascot, empty-brief mascot
   ### 3.2 Theme: vehicles          <-- the new cast
        - same shape, different art
        - per-lane tone notes ("race car — momentum, motion lines trail right")
   ### 3.3 Adding a theme           <-- short authoring note for future PRs
```

One file. Cross-theme comparison stays cheap. Stays at depth-1 from `SKILL.md` per `skills/CLAUDE.md` "File references … must be at most one level deep."

## 6. Vehicles cast (lane → icon)

The role assignments. Actual art is sourced/curated in implementation; this table is the contract.

| Lane | Icon | Tone note |
| --- | --- | --- |
| `shipped` | race car | momentum, just zoomed past — motion lines trail right |
| `questions` | scooter | small, curious, hops around lanes |
| `stalls_aging` | rusted truck | sitting in the lot too long, paint peeling |
| `stalls_no_pr` | wheelbarrow | manual, no engine — work without automation backing it |
| `stalls_silent` | parked car | present, lights off, nothing moving |
| `stalls_blocked` | traffic cone / road barrier | literally blocked from moving forward |
| `changes_scope` | detour sign | the path changed |
| `changes_date` | odometer | the number moved |
| `quality` | traffic light | "did we check before going through?" |
| `retrospective` | horse trotting | the run that just ended — the user explicitly asked for a horse in the cast |
| `changes_scope` drift (≥3) | traffic jam / pile-up | sustained drift — replaces detour sign when drift threshold trips |
| Setup mascot | gas pump | conversational, single-shot, "let's get fueled up before the trip" |
| Empty-brief mascot | empty parking lot | honest about the nothing: "nothing parked here, you tell me if that's good" |

Cast size envelope mirrors animal-kingdom: each block 3-8 rows, ~10-30 columns, flush at column 0, public-commons ASCII (no freehand). Mixed facing directions allowed; canonical art is the point.

The horse in `retrospective` is deliberate — the user explicitly grouped "race car, truck, horse, wheelbarrow" together. Treating "vehicles" loosely as "modes of conveyance" lets the horse in. It's the only animate icon in the cast and signals "the previous era" against the mechanized lanes around it, which fits retrospective.

## 7. SKILL.md, presentation, setup-flow wording

The three callers that name the cast:

- **`SKILL.md`** — uses neutral phrasing like "the configured cast" or "the cast in `assets/animation.md`" instead of naming creatures. One creature per signal lane per brief still holds; the rule is theme-agnostic.
- **`references/presentation.md`** — same neutralization. The lane → role table stays; the lane → creature table moves to `assets/animation.md` as one-per-theme.
- **`references/setup-flow.md`** — gains one new question between the existing horizon / labels questions and the confirmation step. Default = `animal-kingdom`. Wording matches the existing question style.

The render description ("animation per [presentation.md] and [assets/animation.md]") stays, since the *file* hasn't moved.

## 8. Audit cues

- **Theme set is closed.** The set of legal `animation_theme` values is exactly the set of `## Theme: <name>` headings in `assets/animation.md`. **Audit:** parse those headings; the union must equal the enum used by the config validator and the setup-flow prompt.
- **Every theme covers every lane.** Each theme section contains exactly one ASCII block per lane in the canonical lane → role table, plus one setup mascot and one empty-brief mascot. **Audit:** for each `## Theme: <name>` subsection, count the role sub-headings and assert equality with the canonical list.
- **Theme is presentation-only.** Signal-layer files (`references/signals.md`, `references/signal-modes.md`, `references/horizon-and-scope.md`) must not reference any creature or icon by name. **Audit:** grep those files for icon nouns from any theme; expected count is zero.
- **Default theme is sticky.** Configs missing `animation_theme` default to `animal-kingdom` — the cast they had before this change. **Audit:** open a config without the field; the brief renders the animal-kingdom cast and emits no warning.

## 9. Implementation notes

- The reconfigure flow re-prompts for theme; existing configs are untouched until the user runs reconfigure or hand-edits.
- `pnpm lint` and `npx skills-ref validate ./skills/linearazor` both pass.
- Conventional commit: `feat(linearazor): add vehicles animation theme + theme switcher`.
- No AI attribution in commit messages or PR body (rule 7 in top-level `CLAUDE.md`).
