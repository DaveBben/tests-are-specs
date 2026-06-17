# Spec Index Lifecycle

Read this at the end of Phase 2, when updating the Spec Index (`docs/specs/spec.md`) after the user approves a feature. Add or update the entry in the **Features** table.

A feature is one row, **not** one row per slice. The row points at the feature's `index.md`, and its status is the **rollup** computed across the feature's slices (see `reference/index-template.md`). Slice-level status lives inside `index.md`, never in the Spec Index.

## Row format

One row per feature, pointing at `index.md`:

```markdown
| {Feature title} | `docs/specs/features/{slug}/index.md` | {rollup status} | {YYYY-MM-DD} | {one-line description} |
```

The Status column mirrors `index.md`'s front-matter `status` verbatim — one of these three rollup forms:

- `Waiting Implementation` — no slice implemented yet.
- `In Progress — {k}/{N} slices implemented` — some, not all.
- `Implemented` — every slice implemented.

(Plus `Superseded` / `Deprecated` when the whole feature is retired.) The Status never names a single slice.

## Status values

- **Waiting Implementation** — feature written, no slice implemented yet
- **In Progress — {k}/{N} slices implemented** — some slices done, some not
- **Implemented** — every slice's `/spec-monkey:execute-spec` finished and verification passed
- **Superseded** — replaced by a newer feature that covers this change
- **Deprecated** — feature abandoned or removed
- **Needs Revision** — feature needs changes before it can be implemented

## Updated column

The **Updated** column mirrors `index.md`'s front-matter `modified` date — set both to today's date (`YYYY-MM-DD`) on every lifecycle event:

- **Creating**: new row, status `Waiting Implementation`, Updated = today. Added by `/spec-monkey:create-spec`.
- **Updating**: `/spec-monkey:execute-spec` refreshes the rollup Status and Updated each time a slice finalizes. Adding or editing a slice in `/spec-monkey:create-spec` also bumps Updated. Update the description too if the feature scope changed.
- **Deleting**: never delete the row — set status to `Superseded` or `Deprecated` and refresh Updated. Keeping the row preserves the audit trail so the decision isn't relitigated.
