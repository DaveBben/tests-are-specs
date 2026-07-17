---
spec_monkey: "1.6.0"
id: SPEC-000
kind: project
title: Sentiment classifier training pipeline
status: approved
version: 1
approved_by: [@dave]
approved_date: 2026-07-14
created: 2026-07-14
updated: 2026-07-14
owners: [@dave]
standards: AGENTS.md
---

# Project: Sentiment classifier training pipeline

## What we're building

A pipeline that turns a public HuggingFace text dataset into a trained binary sentiment classifier and an
honest eval report. It reads datasets from HuggingFace at its input edge, and writes versioned model
artifacts to a local on-disk registry at its output edge. A separate inference service consumes those
artifacts (out of scope here).

## Shared data contracts

- **Dataset**: a versioned, on-disk snapshot of labeled examples. Fields: `dataset_id`, `source_revision`,
  `version`, and per example `{id, text, label}` where `label` is one of the known label set (`pos` | `neg`).
  Invariants: an example belongs to exactly one split; every `label` is in the known set. Written by the
  loader; read by the trainer (train/val) and the evaluator (test).
- **ModelArtifact**: a trained model plus its provenance and scores. Fields: `model_id`, the `dataset_id` and
  `version` it trained on, `metrics` (accuracy, F1 per label), `created_at`. Written by the evaluator; read
  by the inference service (out of scope).

## Invariants

- **INV-001**: no example `id` appears in more than one split of a given Dataset version (leak-free splits).
- **INV-002**: every ModelArtifact records the exact `dataset_id` and `version` it trained on (reproducibility).
- **INV-003**: splitting is deterministic — the same `(dataset_id, source_revision, seed)` always yields the
  same example-to-split assignment.
- **INV-004**: no raw example text is written to logs, metrics, or artifact metadata.

## Trust boundaries

- **HuggingFace ingestion**: untrusted external data enters at the loader. What enters: arbitrary `text` and
  `label` values from a public dataset. Verified: each row is checked against the Dataset schema and the
  known label set, and rows over a max text length are rejected. On malformed input: the row is dropped and
  counted, never silently ingested.

## Constraints

- **Language & framework**: Python 3.12+, `uv`, PyTorch — the team's existing stack. TensorFlow was rejected
  for ecosystem fit with the rest of the codebase.
- **Single-node**: training runs on one GPU node; no distributed or multi-GPU training in this project (cost
  and operational simplicity).
- **On-prem storage**: datasets and artifacts live on the local disk registry, not cloud object storage
  (data-residency requirement).

## Work items & sequencing

- **dataset-loader** — ingest a HuggingFace dataset into a leak-free, versioned Dataset — depends_on: [] — status: drafted
- **trainer** — train the classifier on a Dataset version, write a ModelArtifact — depends_on: [dataset-loader] — status: planned
- **evaluator** — score a model on the test split and record its metrics — depends_on: [trainer] — status: planned
- **run-summary-log** — log a one-line run summary when the loader finishes (trivial lane, light profile) — depends_on: [dataset-loader] — status: approved

## Out of scope

- Model serving / the inference service: it consumes ModelArtifacts but is a separate system.
- Hyperparameter search and data augmentation: v1 trains one fixed configuration.
- Multi-label or multi-class classification: the label set is binary.
