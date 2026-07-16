# The contract
> Part of [spec.md](../spec.md) — Ingest a HuggingFace dataset into leak-free versioned splits

## Requirements & success criteria

### Ingestion

**Behavior**: the loader fetches the named dataset by id and revision, checks each row against the Dataset
schema and the known label set, rejects rows whose text exceeds the max length, and drops and counts any
row that fails. If the source cannot be reached, it aborts before writing anything.

**Requirements & success criteria**

- **FR-001**: WHEN a fetched row fails schema validation, carries a label outside the known set, or exceeds
  the max text length, the system SHALL drop it and increment a dropped-row counter.
  - **SC-001**: given an input with N such rows, the run reports exactly N dropped and none of them appear
    in any output split.
- **FR-002**: the system SHALL record the source `dataset_id` and `source_revision` on the Dataset version
  it produces. *(the provenance INV-002 later records on a ModelArtifact — this FR makes it recordable)*
  - **SC-002**: the produced version's manifest shows the exact `dataset_id` and `source_revision` requested
    on the command line.
- **FR-003**: WHEN the dataset source is unreachable after the configured retries, the system SHALL abort
  with a nonzero exit and write no partial Dataset version.
  - **SC-003**: with the source mocked to fail every attempt, the process exits nonzero and no version
    directory is created.

### Splitting

**Behavior**: the loader partitions the validated examples into train, val, and test, stratified by label,
assigning every example to exactly one split, reproducibly from a seed.

**Requirements & success criteria**

- **FR-004**: the system SHALL assign each validated example to exactly one of train, val, or test.
  *(grounds INV-001)*
  - **SC-004**: the union of the three split id-sets equals all validated example ids, and the three sets are
    pairwise disjoint (zero shared ids).
- **FR-005**: WHEN run again with the same `dataset_id`, `source_revision`, and `seed`, the system SHALL
  produce an identical example-to-split assignment. *(grounds INV-003)*
  - **SC-005**: two runs with `seed=42` produce byte-identical split id-sets.
- **FR-006**: on a dataset of at least 1,000 rows, the system SHALL keep each split's per-label frequency
  within 2 percentage points of the overall label distribution.
  - **SC-006**: for every label and every split, `|split_freq − overall_freq| ≤ 0.02` on a dataset of at
    least 1,000 rows.

## Constraints & non-functional bounds

**Constraints**: the output is the project spec's **Dataset** contract (SPEC-000); the language/framework and
on-disk-registry constraints under SPEC-000 *Constraints* apply unchanged. Local to this work item: the max
text length is a fixed config value, not a per-run flag.

**Non-functional bounds**: no raw example `text` appears in logs or the manifest *(grounds INV-004)*; a
100,000-row dataset splits in under 2 minutes on the single GPU node.

## Data & interface contract

- **SplitManifest** (new): the per-version index this loader writes — `dataset_id`, `source_revision`,
  `seed`, per-split example counts, the known label set, and `dropped_row_count`. Consumed by the trainer and
  the evaluator to locate and trust a version. The per-example `{id, text, label}` shape is SPEC-000's
  **Dataset** contract and is not restated here.

## When it happens

**Triggers & preconditions**: an on-demand CLI invocation. Precondition: the `dataset_id` and
`source_revision` are pinned (see the brief's blocking open question).

**Ordering & dependencies**: no upstream dependency (`depends_on: []`). Downstream, the trainer (SPEC-000)
must not start against a version until that version passes the rollout gate.

**Rollout mechanics**: the loader produces a candidate version, runs the leak check (SC-004) and the balance
bound (SC-006), and marks the version available only on pass.

**Reversibility detail**: versions are additive and regenerable; a version becomes effectively permanent once
a ModelArtifact trains on it, since INV-002 pins that provenance.

## Out of scope

- Private or gated datasets that need an auth token: v1 handles public datasets only.
- Caching downloads across runs: each run re-fetches.
- Any transformation of `text` beyond validation — no normalization, no augmentation.

## Known limitations & honest gaps

- The balance bound (FR-006) assumes single-label examples; multi-label datasets are out of scope (SPEC-000),
  and FR-006 is undefined for them.
- Datasets over ~1M rows are unsupported in v1: stratification holds every label's full index in memory.
  Larger inputs are OUT-OF-SCOPE, not silently truncated.

**Coverage exceptions**

- None — every FR-001 through FR-006 has an SC beside it.

## Verification approach & commands

- Unit tests cover each FR against its SC: drop-and-count (FR-001), provenance recording (FR-002), abort with
  the source mocked to fail (FR-003), split coverage and disjointness (FR-004), determinism across two runs
  (FR-005), and per-label balance on a 1,000-row synthetic set (FR-006). One integration test runs the real
  loader end-to-end on a small on-disk fixture, crossing the fetch-and-write boundary, and asserts the
  SplitManifest — this proves SC-001, SC-002, and SC-004 across the real seam, not just in isolation. A
  separate test asserts no raw example `text` appears in any emitted log line or in the SplitManifest,
  covering the INV-004 bound.

**Worked case**

- **Given:** an 11-row fixture — 10 valid (6 `pos`, 4 `neg`) and 1 malformed row carrying an unknown label —
  with `seed=42`. · **When:** the loader runs against revision `abc123`. · **Then:** `dropped_row_count` = 1,
  split sizes are train=8 / val=1 / test=1, the three split id-sets are pairwise disjoint, and the
  SplitManifest records `source_revision: abc123`.

**Commands:** `uv run pytest tests/test_loader.py`; then end-to-end
`uv run python -m clf.loader --dataset <id> --revision abc123 --seed 42 --out data/v1 && uv run python -m clf.check_splits data/v1`.
