---
spec_monkey: "1.5.0"
id: SPEC-001
kind: design
parent: SPEC-000
title: Ingest a HuggingFace dataset into leak-free versioned splits
status: approved
approved_by: [@dave]
approved_date: 2026-07-14
created: 2026-07-14
updated: 2026-07-14
---

# The design
> Part of [spec.md](../spec.md) — Ingest a HuggingFace dataset into leak-free versioned splits

## The request

> Build the loader: pull a sentiment dataset from HuggingFace and turn it into train/test splits we can
> train on.

## Goal

A named HuggingFace dataset becomes a versioned, on-disk Dataset with train/val/test splits that share no
example, so the trainer and evaluator have a reproducible input.

## Drivers

- The trainer and evaluator (SPEC-000 work items) have no input to consume; nothing produces a Dataset today.
- A hand-rolled split risks leakage between train and test, which silently inflates every downstream metric.

## What's true today

- No dataset pipeline exists in the repo; nothing produces a Dataset version. — verified fact
- The HuggingFace `datasets` library is already in the project's dependency set. — verified fact
- The target dataset exposes a `label` column with values in `{pos, neg}`. — assumption

## Approach

A single batch loader owns the whole path from HuggingFace to an on-disk Dataset version: fetch the named
dataset at a pinned revision, validate and drop malformed rows with a count, deduplicate, then split before
anything is written. The split is stratified 80/10/10 by label and seeded, so the same inputs always produce
the same three files and the label balance holds even on a smaller dataset. A SplitManifest is written
alongside the splits, so the trainer and evaluator locate a version without re-deriving the split.

The non-obvious things:
- The leak-free guarantee (INV-001) comes from splitting a deduplicated row set once, up front — not from
  checking for overlap after the fact. An implementer who splits first and dedups each file separately breaks
  it.
- Determinism (INV-003) rests on both the pinned source revision and the seed. Pin only one and
  reproducibility is lost.
- Validation runs before the split, so a malformed row never lands in a split and never skews the balance.

Approaches weighed:
- **A custom stratified, seeded splitter (chosen).** Owns determinism, stratification, and the manifest.
- **HuggingFace's built-in `train_test_split`.** Simpler, but no stratification guarantee and no control over
  determinism or the manifest — rejected, and recorded as the *Split strategy* decision to sign off.

## Failure modes

**Failure & scale**: behavior at 10× / 1000× load or data; a dependency down, slow, or rate-limited;
concurrency, partial failure mid-operation, retries / idempotency; empty, huge, malformed, or hostile input.
- Dataset too large to hold every label index in memory: ACCEPT — v1 caps at ~1M rows (*Known limitations &
  honest gaps*).
- HuggingFace source down or rate-limited mid-fetch: HANDLE (FR-003) — retry with backoff, then abort with
  no partial output.
- Empty, oversized, or malformed rows: HANDLE (FR-001) — validated and dropped with a count.

**Operational readiness**: how it's observed live (logs, metrics, alerts); how a break is noticed; what
config or environment it needs.
- A silent bad run is only caught if counts are visible: HANDLE (FR-001, and the no-text bound) — emit
  `dropped_row_count` and per-split counts as structured metrics, with no raw `text` per INV-004.

**Trust boundary**: where untrusted input crosses into trusted code; who is authorized and what happens on
denied or expired credentials; what sensitive or personal data is touched and protected.
- Untrusted `text` and `label` values from the public dataset: HANDLE (FR-001) — schema, label-set, and
  length validation at ingestion. This is the loader's half of SPEC-000's *HuggingFace ingestion* boundary.
  No raw text reaches logs (INV-004).

**Implied work**: callers or consumers that must change too; migrations or backfills forced; docs, configs,
or types that go stale; what was assumed free but isn't.
- The trainer and evaluator must read the new SplitManifest to locate a version: HANDLE — the contract
  publishes it (*Data & interface contract*); the CLI gets a short usage doc.

**Better way**: is there a simpler or safer approach? Name it, then resolve: adopt it, or record why this
approach wins.
- HuggingFace's built-in `train_test_split` is simpler: rejected — it gives no stratification guarantee and
  no control over determinism or the manifest. Recorded as the *Split strategy* decision to sign off.

**Contingencies**
- **WHEN** more than a small threshold of rows carry a label outside the known set on a later revision (a
  sign the dataset itself changed): the loader aborts instead of dropping most of the data, and surfaces the
  new label for a human to decide whether to extend the label set.

## Verification strategy

- Prove the leak-free property (INV-001) end-to-end: build a Dataset version from a known input and confirm
  no example appears in more than one split. This is the load-bearing guarantee; a unit test on the splitter
  alone is not enough — verify it on a written version.
- Prove determinism (INV-003): run the loader twice with the same revision and seed, and confirm the three
  splits come out identical.
- Prove validation: feed malformed and out-of-label rows, confirm they are dropped with an accurate
  `dropped_row_count`, and confirm no raw `text` reaches logs (INV-004).
- The stratified balance bound is checkable only where the dataset is large enough; it holds at ≥1,000 rows
  and is best-effort below that.

## Who & what this touches

**External**: the ML engineers who run the pipeline from the CLI; the HuggingFace dataset source.

**Internal**: the trainer and evaluator, future consumers of the SplitManifest and Dataset; the on-disk
registry path they read from.

**Unchanged**: the inference service — it reads ModelArtifacts, never raw datasets, so this change does not
touch it.

## Open questions & assumptions

- **Assumption:** the chosen dataset is single-label with labels `{pos, neg}`; confidence med; if wrong,
  FR-006 and the label-set validation need multi-label handling. Verify by reading the dataset card before
  pinning the revision.
- **Open:** whether to cache downloads across runs; deferred, revisit if fetch time dominates run time.
