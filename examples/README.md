# Examples

Worked, end-to-end examples of a spec-monkey spec set, for a made-up project. They exist to show the format
in use — every canonical section filled with real content, one file per reader. They are illustrative, not a
real system.

## `clf-pipeline` — a sentiment classifier training pipeline

```
clf-pipeline/docs/specs/
  project/spec.md              the project spec (kind: project) — grounding-specs' output:
                               shared Dataset/ModelArtifact contracts, INV-001..004, constraints,
                               and the work-item map
  dataset-loader/              a FULL work-item spec (kind: work-item) — shaping-specs + writing-specs' output,
    spec.md                    grounded on the project spec (parent: SPEC-000):
    detail/contract.md           the decision brief, the build contract, the design reasoning
    detail/design.md
  run-summary-log/             a LIGHT work-item spec (profile: light) — the trivial lane:
    spec.md                    one file, reduced section set, still grounded and still signed
```

Read `project/spec.md` first, then the `dataset-loader` spec. Notice the work item **cites** the project
spec's invariants by ID (`grounds INV-001`, `grounds INV-003`, `grounds INV-004`) and references the shared
**Dataset** contract rather than restating it; the only contract it defines locally is the new
**SplitManifest**. It does *not* ground INV-002 — that governs the ModelArtifact the evaluator writes; the
loader only makes that provenance recordable (see FR-002).

Then read `run-summary-log/spec.md` for the contrast: the **trivial lane** (`profile: light`). It is one
`spec.md`, no `detail/` split — one FR/SC, grounded on `SPEC-000` and upholding `INV-004` (no raw text in
logs), still carrying a full gate record. The reasoning-and-contract split is *dropped*, not stubbed with
`N/A` — that is what makes the light profile light instead of the full ceremony hollowed out. Both specs lint
clean under the same `tools/spec-lint.py` (the linter checks a light spec against the reduced schema); run
`python3 tools/spec-lint.py examples/clf-pipeline/docs/specs` to see it, and add `--status` for the roll-up.
