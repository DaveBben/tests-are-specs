# Spec Index Lifecycle

Read this at the end of Phase 2, when updating the Spec Index
(`docs/specs/spec.md`) after the user approves a spec. Add or update
the entry in the **Features** table.

## Row format

New specs use status `Waiting Implementation`:

```markdown
| {Spec title} | `docs/specs/features/{slug}/spec.md` | Waiting Implementation | {YYYY-MM-DD} | {one-line description} |
```

## Status values

- **Waiting Implementation** — spec written, not yet implemented
- **Implemented** — `/specd:execute-spec` finished and verification passed
- **Superseded** — replaced by a newer spec that covers this change
- **Deprecated** — spec abandoned or its feature was removed
- **Needs Revision** — spec needs changes before it can be implemented

## Updated column

The **Updated** column tracks the spec lifecycle — set it to today's
date (`YYYY-MM-DD`) on every lifecycle event:

- **Creating**: new row, status `Waiting Implementation`, Updated =
  today.
- **Updating**: refresh Updated whenever you edit the spec or change
  its status (e.g. to `Needs Revision`). Update the description too if
  the scope changed.
- **Deleting**: never delete the row — set status to `Superseded` or
  `Deprecated` and refresh Updated. Keeping the row preserves the
  audit trail so the decision isn't relitigated.
