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
  dataset-loader/              one work-item spec (kind: work-item) — shaping-specs + writing-specs' output,
    spec.md                    grounded on the project spec (parent: SPEC-000):
    detail/contract.md           the decision brief, the build contract, the review-time evidence
    detail/evidence.md
```

Read `project/spec.md` first, then the `dataset-loader` spec. Notice the work item **cites** the project
spec's invariants by ID (`grounds INV-001`, `grounds INV-003`, `grounds INV-004`) and references the shared
**Dataset** contract rather than restating it; the only contract it defines locally is the new
**SplitManifest**. It does *not* ground INV-002 — that governs the ModelArtifact the evaluator writes; the
loader only makes that provenance recordable (see FR-002).
