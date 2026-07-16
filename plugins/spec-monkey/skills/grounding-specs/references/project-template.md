<!--
THE PROJECT SPEC IS ONE FILE: docs/specs/project/spec.md. It is the shared ground every work-item spec references. Keep it thin: roughly one to two screens. It is a LIVING document: start with what is shared and certain now, and grow it by amendment as the work reveals more.

WHAT BELONGS HERE: facts every work item shares: canonical data contracts, system-wide invariants, trust boundaries, and hard architectural constraints, plus the planned work items and their order.

WHAT DOES NOT: work-item requirements (FR/SC), implementation detail, and coding conventions (those live in the constitution: standards.md / CLAUDE.md / AGENTS.md).

SINGLE SOURCE OF TRUTH: each shared fact lives here once, with an ID (INV-NNN, or a named entity). Work-item specs cite the ID; they never restate the fact. The work-item format is a separate file: writing-specs/references/spec-template.md.
-->

---
spec_monkey: "1.5.0"             # spec-monkey format version; also marks this as a spec-monkey spec
id: SPEC-000                     # the project spec's stable handle; work items set parent to it.
                                 # SPEC-000 is the convention for a single project spec; a monorepo
                                 # with several gives each a distinct id.
kind: project                    # project (this template) | work-item (spec-template.md)
title: <system name>
status: draft                    # draft → approved (amendments re-approve)
version: 1                       # living-doc version; bump on every amendment
approved_by: []                  # who granted the gate; filled when status reaches approved.
                                 # A self-set flip with no human recorded here is not a gate.
approved_date:                   # YYYY-MM-DD the human approved; set with approved_by.
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owners: [<@handle>]
standards: standards.md          # the constitution (ONE of: standards.md | CLAUDE.md | AGENTS.md)
---

# Project: <system name>

## What we're building
<!-- Two or three sentences: the system, its purpose, and its edges. The frame every work item inherits. Not a feature list. -->

## Shared data contracts
<!-- The canonical entities more than one work item touches. Fields + meaning + invariants a reviewer can sign. NO language-typed struct: the concrete type and storage are the implementer's. An entity only one work item touches does not belong here. Mark "N/A — reason" only after real thought. -->
- **<Entity>**: <what it represents; the fields that matter and their meaning
  (e.g. `status`: one of open | paid | shipped); the invariants that hold; who reads it, who writes it>.

## Invariants
<!-- System-wide rules every work item must uphold, each a checkable property, not a wish. A rule you can't say how to check is an assumption. Keep it out until it firms up. -->
- **INV-001**: <the rule as a property that holds across the whole system>.

## Trust boundaries
<!-- Where untrusted input crosses into trusted code, at the system level. One line each. -->
- **<boundary>**: <what enters; who is authorized; what is verified; what happens on denied/malformed input>.

## Constraints
<!-- The hard, expensive-to-reverse architectural calls that bind every work item: language, runtime, datastore, framework, deployment target, compliance, must-reuse. A concrete tech choice is expected here: this is the one place it belongs. Give the reason and the rejected alternative for the load-bearing ones. -->
- **<constraint>**: <the limit; why this way; the alternative rejected>.

## Work items & sequencing
<!-- The planned work-item specs and their order. The cut plan, not a promise: it grows and reorders as the work teaches you. Each becomes a child spec (shaping-specs then writing-specs) with parent: SPEC-000. -->
- **<slug>** — <one line: the one decision it owns> — depends_on: [<slug>, …] — status: planned | drafted | implemented

## Out of scope
<!-- What this system will NOT do, that a reader might assume it does. -->
- <excluded item>: <why, or where it lives instead>.

<!--
PARSE CONTRACT (lightweight):
1. Location: docs/specs/project/spec.md. `kind: project` in the frontmatter marks it.
2. Frontmatter YAML holds every queryable scalar: spec_monkey, id (SPEC-000), kind, status, version, approved_by, approved_date.
3. IDs are join keys: INV-NNN (one system-wide invariant) and the entity names under Shared data contracts. Work-item specs reference these; they do not copy them.
4. Sections are the schema: each canonical heading above is a fixed home. A section with nothing to say gets "N/A — reason", never silence.
-->
