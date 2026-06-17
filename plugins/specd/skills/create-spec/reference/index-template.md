# Index Template

Read this when producing a feature's `index.md` in Phase 2, before writing any slice spec. A feature is **sliced**: it lands as a folder at `docs/specs/features/{slug}/` holding one complete `{slice}.md` per slice plus this `index.md` at the root. The `index.md` is the feature's overview and ordering map — thin by design. Each slice file carries the full spec contract (`spec-template.md`); `index.md` carries none of it.

## Front-matter

Every `index.md` opens with a YAML front-matter block (`---` fences) so the linter can validate it:

```
---
name: {slug}
status: {rollup — computed, see below}
created: {YYYY-MM-DD}
modified: {YYYY-MM-DD}
drafter: {name}
slices: {N}
depends_on: []
---
```

- `name` — the feature slug; matches the folder name.
- `status` — the **rollup** status, computed from the Slices-table `Status` cells (below). Never stored independently of the table, so it can't drift.
- `created` — `YYYY-MM-DD`, set once; never changes.
- `modified` — `YYYY-MM-DD`, refreshed whenever a slice's status changes or the slice set changes. Equals `created` at creation. The Spec Index "Updated" column mirrors this date.
- `drafter` — who authored the feature; default to `git config user.name`.
- `slices` — the count of slice rows in the table.
- `depends_on` — optional list of **other feature slugs** this whole feature depends on (e.g. `['auth-rework']`). Bare slugs naming sibling feature folders under `docs/specs/features/`. Empty list when none. This is feature-to-feature ordering; slice-to-slice ordering lives in the Slices table and each slice's own `depends_on`.

### Computing the rollup `status`

Derive it from the `Status` cells in the Slices table:

- **No slice implemented** → `Waiting Implementation`
- **Some but not all implemented** → `In Progress — {k}/{N} slices implemented`
- **All implemented** → `Implemented`
- `Superseded` / `Deprecated` — reserved for retiring the whole feature.

This rollup string is exactly what the Spec Index row mirrors (`reference/spec-index.md`). `/specd:execute-spec` recomputes it each time a slice finalizes.

## Body

```markdown
# {Feature title}

## Why
{1-3 sentences — the problem today, why it's worth doing now. Same bar as a
spec's Why, scoped to the whole feature.}

## Summary
{1-3 sentences — the feature's intent across all slices. Not procedure.}

## Slices

| # | Slice | File | Depends on | Status | What it ships |
|---|-------|------|------------|--------|---------------|
| 1 | Data model | `data-model.md` | — | Waiting Implementation | persisted schema + migration |
| 2 | API endpoint | `api-endpoint.md` | `data-model` | Waiting Implementation | POST route over the new schema |

## Ordering notes
{Prose only where the Depends-on column can't carry it: an optional slice,
two slices safe to ship in either order, a slice that must ship behind a flag
until a later slice lands. Skip this section entirely if the table says it all.}
```

## The Slices table

This table is the **authoritative ordering and dependency record** for the feature. Each slice's own front-matter `depends_on` mirrors only its row here; if the two ever disagree, this table wins.

- **`#`** — human reading order. Not binding; the `Depends on` column carries the binding order. No numeric filename prefixes — slugs stay stable when you reorder.
- **`Slice`** — short human label.
- **`File`** — the slice's filename (e.g. `data-model.md`). Must match a real sibling file in the folder.
- **`Depends on`** — sibling slice slugs (filename minus `.md`) this slice needs implemented first; `—` when none. These slugs feed each slice's front-matter `depends_on`.
- **`Status`** — the slice's lifecycle state, from the spec status enum (`Waiting Implementation` | `Implemented` | `Superseded` | `Deprecated` | `Needs Revision`). `/specd:execute-spec` flips the cell at finalize.
- **`What it ships`** — one line: the shippable, production-safe increment this slice delivers on its own.

### Authoring rules

- Every `File` slug and every `Depends on` slug must resolve to a real sibling `{slug}.md`. The reference linter enforces this.
- A slice slug must **not** equal the feature slug, and none may be `index` (reserved for this file).
- **Single-slice feature** still uses this format — folder + `index.md` + one slice file, one table row with `Depends on` = `—`. Don't shortcut to a bare `spec.md`; there is no bare-spec path.
