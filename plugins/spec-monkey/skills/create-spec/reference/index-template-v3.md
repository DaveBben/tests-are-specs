# Index Template — v3

Read this when producing a feature's `_index.md` in Phase 2, before writing any slice spec.
This is the **v3** form; legacy `schema: v2` features use `index-template.md` and are frozen.

A feature is **sliced**: it lands as a folder at `docs/specs/features/{slug}/` holding one
complete `{slice}.md` per slice (see `spec-template-v3.md`) plus this `_index.md` at the root.
The `_index.md` is the feature's overview, ordering map, and **Definition of Done** — thin by
design. Each slice file carries the full spec contract; `_index.md` carries none of it.

## Front-matter

Every v3 `_index.md` opens with a YAML block (`---` fences) so the linter can validate it:

```
---
schema_version: v3
name: {slug}
status: {rollup — computed, see below}
created: {YYYY-MM-DD}
modified: {YYYY-MM-DD}
drafter: {name}
slices: {N}
spec_creation:
  total_cost:
  total_duration:
  usage_by_models:
depends_on: []
---
```

- `schema_version` — always `v3`. Readers and tooling branch on it (legacy features carry
  `schema: v2`).
- `name` — the feature slug; matches the folder name.
- `status` — the **rollup** status, computed from the Slices-table `Status` cells (below).
  Never stored independently of the table, so it can't drift.
- `created` — `YYYY-MM-DD`, set once; never changes.
- `modified` — `YYYY-MM-DD`, refreshed whenever a slice's status changes or the slice set
  changes. Equals `created` at creation. The Spec Index "Updated" column mirrors this date.
- `drafter` — who authored the feature; default to `git config user.name`.
- `slices` — the count of slice rows in the table.
- `spec_creation` — optional run metadata for the `/spec-monkey:create-spec` session that
  drafted this feature. Feature-level (one drafting session covers all slices). Leave blank
  while drafting; recorded afterward from the session's end-of-session API summary. When filled
  it carries `total_cost`, `total_duration`, and `usage_by_models` (one entry per model:
  `model`, `input`, `output`, `cache_read`, `cache_write`, `cost`).
- `depends_on` — optional list of **other feature slugs** this whole feature depends on (bare
  slugs naming sibling folders under `docs/specs/features/`). Empty list when none. Slice-to-
  slice ordering lives in the Slices table and each slice's own `depends_on`.

### Computing the rollup `status`

Derive it from the `Status` cells in the Slices table (slice statuses are the v3 enum
`Draft` | `Reviewed` | `Implemented` | `Superseded`):

- **Any slice still `Draft`** → `Draft`
- **All slices `Reviewed`, none `Implemented`** → `Reviewed` (the whole feature is ready to implement)
- **Some but not all `Implemented`** → `In Progress — {k}/{N} slices implemented`
- **All slices `Implemented`** → `Implemented`
- **`Superseded`** — reserved for retiring the whole feature.

This rollup string is exactly what the Spec Index row mirrors (`reference/spec-index.md`).
`/spec-monkey:execute-spec` recomputes it each time a slice finalizes.

## Body

```markdown
# {Feature title}

## Why
{1-3 sentences — the problem today, why it's worth doing now. Same bar as a slice's Why,
scoped to the whole feature. Outcome-oriented.}

## Summary
{1-3 sentences — the feature's intent across all slices. Not procedure.}

## Slices

| # | Slice | File | Depends on | Status | What it ships |
|---|-------|------|------------|--------|---------------|
| 1 | Data model | `data-model.md` | — | Draft | persisted schema + migration |
| 2 | API endpoint | `api-endpoint.md` | `data-model` | Draft | POST route over the new schema |

## Ordering notes
{Prose only where the Depends-on column can't carry it: an optional slice, two slices safe to
ship in either order, a slice that must ship behind a flag until a later slice lands. Skip this
section entirely if the table says it all.}

## Definition of Done
{The feature-level acceptance checklist — the qualitative bar that, when every box is checked,
means the whole feature is genuinely shipped, not just each slice merged. One observable
condition per line; written so a human reviewer can tick it. Cover the end-to-end outcome, the
cross-slice integration, and the cleanup the slices defer. Example:}

- [ ] Every slice is `Implemented` and its PR merged.
- [ ] {The end-to-end outcome works against real conditions — name it: e.g. "a summarized article carries a non-NULL 768-dim embedding on a nightly run."}
- [ ] {Cross-slice integration holds — the wiring slice actually calls the capability slice; no dead code left behind a flag.}
- [ ] {The feature-level success metric is met or measured — quote the number.}
- [ ] {Deferred cleanup is done — old path deleted, flag removed, docs/spec.md Current State updated.}
- [ ] The full gate (lint + types + tests) passes on the integrated result.
```

## The Slices table

This table is the **authoritative ordering and dependency record** for the feature. Each
slice's own front-matter `depends_on` mirrors only its row here; if the two disagree, this
table wins.

- **`#`** — human reading order. Not binding; the `Depends on` column carries the binding
  order. No numeric filename prefixes — slugs stay stable when you reorder.
- **`Slice`** — short human label.
- **`File`** — the slice's filename (e.g. `data-model.md`). Must match a real sibling file.
- **`Depends on`** — sibling slice slugs (filename minus `.md`) this slice needs implemented
  first; `—` when none. These slugs feed each slice's front-matter `depends_on`.
- **`Status`** — the slice's lifecycle state, from the v3 enum (`Draft` | `Reviewed` |
  `Implemented` | `Superseded`). `/spec-monkey:execute-spec` flips the cell at finalize.
- **`What it ships`** — one line: the shippable, production-safe increment this slice delivers
  on its own.

### Authoring rules

- Every `File` slug and every `Depends on` slug must resolve to a real sibling `{slug}.md`.
  The reference linter enforces this.
- A slice slug must **not** equal the feature slug, and none may be `_index` (reserved for
  this file).
- **Single-slice feature** still uses this format — folder + `_index.md` + one slice file, one
  table row with `Depends on` = `—`, and a Definition of Done covering that one slice's
  end-to-end outcome. There is no bare-`spec.md` path.
