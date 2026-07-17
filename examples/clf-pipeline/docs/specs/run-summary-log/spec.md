---
spec_monkey: "1.6.0"
id: SPEC-002
kind: work-item
parent: SPEC-000
profile: light              # trivial lane: one file, the droppable sections dropped (not "N/A"). See spec-template.md "The light profile".
title: Log a run summary line when the loader finishes
status: approved
approved_by: [@dave]
approved_date: 2026-07-15
created: 2026-07-15
updated: 2026-07-15
owners: [@dave]
standards: AGENTS.md
depends_on: [SPEC-001]
supersedes: []
---

# Spec: Log a run summary line when the loader finishes

<!--
This is a LIGHT-PROFILE (trivial-lane) spec: a single spec.md, no detail/ split. One obvious
approach, no live failure modes, no new shared fact — a reviewer reads it in a glance. It still
grounds on the project spec and still gets signed. The full design/contract split (detail/*.md)
is dropped here, not stubbed with "N/A". Contrast with the full-ceremony dataset-loader spec.
-->

## Goal

When a loader run finishes, an operator sees one summary line — dropped-row count and per-split
sizes — instead of scrolling the log to piece it together.

## The request

> Print a one-line summary at the end of a loader run so we can eyeball what it produced.

## Requirements & success criteria

### Run summary

**Behavior**: after the loader has written all splits, it emits one INFO log line stating how many
rows it dropped and how many examples landed in each of train, val, and test.

**Requirements & success criteria**

- **FR-001**: WHEN a loader run completes successfully, the system SHALL log exactly one summary
  line reporting the dropped-row count and the per-split example counts (train, val, test).
  - **SC-001**: after a run over the 11-row worked fixture, the completion log contains one line
    reading `run complete: dropped=1 train=8 val=1 test=1`, and no example `text` appears anywhere
    in that line.

## Constraints & non-functional bounds

**Constraints**: the summary line upholds the project spec's **INV-004** — no raw example `text` in
logs. Counts and split names only; never a row's contents. No new data contract: the numbers come
from the SplitManifest the loader (SPEC-001) already writes.

## Verification approach & commands

- One test runs the loader over the worked fixture and asserts the summary line's exact text, then
  asserts no fixture `text` value appears in the captured log — covering SC-001 and the INV-004 bound.

**Worked case**

- **Given:** the 11-row fixture from SPEC-001 (10 valid, 1 dropped) with `seed=42`. · **When:** the
  loader completes. · **Then:** the final log line reads `run complete: dropped=1 train=8 val=1 test=1`
  and contains none of the fixture's example text.

**Commands:** `uv run pytest tests/test_loader.py -k summary_line`
