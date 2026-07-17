<!--
A SPEC IS A FOLDER OF THREE DOCUMENTS, ONE PER READER:

  docs/specs/{slug}/
    spec.md              the decision brief — the reviewer's document; approve or reject from it alone
    detail/contract.md   the build contract — what the implementer builds and the auditor checks
    detail/design.md   the design reasoning — shaping-specs' output, opened on doubt

This reference lays out the two files writing-specs composes: spec.md and detail/contract.md. Each block below marked `FILE: <path>` is a separate file, delimited by an HTML comment; create each at its path under docs/specs/{slug}/. detail/design.md is written by shaping-specs, not here; its format is in shaping-specs/references/design-template.md, and you read it as your input.

WHY THIS SPLIT: each reader wants a different slice, not a different amount: the reviewer the judgment layer, the implementer and auditor the mechanical layer, a deep reviewer the reasoning. Keep spec.md readable on its own; give each detail file a heading and a backlink so it stands alone too.

THE SECTION SET IS THE SCHEMA: every canonical section below must exist in its fixed home file, under its canonical heading; or, for a folded block (Coverage exceptions, Worked case, Contingencies), its canonical `**bold**` key. A detail section with nothing to say gets a justified `N/A — reason`, never silence; only the brief subsections marked as omittable may be dropped. Cite a section by its heading or bold key, never by a number or a position. THE ONE EXCEPTION is the light profile below, where the trivial lane genuinely drops the reasoning-and-contract split.

THE LIGHT PROFILE (the trivial lane). running-lifecycle triages a small-but-signable item — one obvious approach, no live failure modes, no new shared fact, a build a reviewer reads in a glance — onto a light contract. This is the profile that lets it be light instead of the full schema hollowed out with `N/A`:

  - Set `profile: light` in the frontmatter (the default, omitted, is `full`). This is the machine-readable flag that says the reduced schema is deliberate; the linter checks a light spec against the reduced set, not the full one.
  - ONE file: `spec.md`. No `detail/contract.md`, no `detail/design.md` — the split earns its keep only when a reviewer and an implementer want different slices, and a trivial slice has no separate reasoning layer to file away. The FR/SC contract lives directly in `spec.md`.
  - REQUIRED even when light: the frontmatter (including a real gate record once approved), a `## Goal`, `## The request`, a `## Requirements & success criteria` block with at least one FR and its SC beside it, and `## Verification approach & commands` with a worked case and the commands. A light spec is still signed and still grounds on the project spec (set `parent`, cite its `INV-NNN`).
  - DROPPED, not stubbed: the design-file sections (What's true today, Failure modes, Who & what this touches, Open questions & assumptions), the Contents reading contract, and any brief section that has genuinely nothing to say (Decisions to sign off, Blocking open questions, Blast radius, Rollout gate). Drop them by leaving them out — do NOT write `N/A` for them; that is the full ceremony with hollow answers, the thing the light profile exists to avoid.
  - When in doubt, take the full profile. The light lane is for the item whose whole contract fits on one screen; the moment there is a real failure mode to reason about or a second seam, it is not trivial. See examples/clf-pipeline/docs/specs/run-summary-log/spec.md for a worked light spec.

The rest of this template is the FULL profile.

ONE SPEC, ONE DECISION: a spec covers exactly one independent decision. If the work spans several (distinct sign-off owners, reviewers, lifecycles/revert boundaries, or success criteria that partition into disjoint groups), split it into sequenced children linked by depends_on. The shared ground they stand on (the goal, data contracts, and invariants) lives in the project spec (kind: project), authored by grounding-specs; each child sets parent to it and cites its INV-NNN.

SINGLE SOURCE OF TRUTH: each fact lives in ONE section; everywhere else references it by ID (FR-001, SC-001), by section heading, or by a Markdown link. A one-line headline in the brief with the detail in a detail/ file is disclosure, not duplication. But the same sentence in two places is a copy. Cut it to a reference.

WHAT AND WHEN, NOT HOW: pin down WHAT to build, WHY, WHEN it happens, what CONSTRAINS it, and how you'll know it worked. Never dictate HOW: that's the implementer's call against the real code. The one exception is verification: the run commands that prove success are concrete (*Verification approach & commands*, in detail/contract.md).

Two interviews feed a spec. shaping-specs/references/interview-questions.md works the reasoning out into detail/design.md; writing-specs/references/interview-questions.md pins down the contract (requirements, data/interface, timing, verification). Work the questions to discover; use this template to compose spec.md and detail/contract.md from the design.
-->

<!-- ===================== FILE: spec.md ===================== -->

---
spec_monkey: "1.6.0"             # spec-monkey format version; also marks this as a spec-monkey spec
id: SPEC-NNN                     # stable handle; commits and other specs reference this
kind: work-item                  # work-item (this template) | project (grounding-specs' project-template.md)
profile: full                    # full (this template, the default — omit it) | light (the trivial lane:
                                 # one spec.md, reduced section set; see "THE LIGHT PROFILE" in the header)
parent: SPEC-000                 # the project spec this grounds on; cite its INV-NNN, never restate them.
                                 # SPEC-000 is the convention for the one project spec; a repo with more
                                 # than one gives each a distinct id and points parent at the right one.
                                 # Omit only for a one-off change with no project spec.
title: <short imperative title>
status: draft                    # draft → approved → implemented → shipped → archived.
                                 # Runs backward on an amendment: an approved+ spec whose contract
                                 # must change regresses to draft (writing-specs "Amending an
                                 # approved spec"). archived also ends a superseded spec.
approved_by: []                  # who granted the gate; filled when status first reaches approved, and
                                 # cleared if an amendment regresses status to draft. A self-set flip
                                 # with no human recorded here is not a gate.
approved_date:                   # YYYY-MM-DD the human approved; set and cleared with approved_by.
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owners: [<@handle>]
standards: standards.md          # the constitution (ONE of: standards.md | CLAUDE.md | AGENTS.md)
depends_on: []                   # other SPEC-NNN that must ship first — feeds "When it happens"
supersedes: []                   # SPEC-NNN this replaces (delta lineage)
---

# Spec: <title>

## Decision brief
<!-- The whole of spec.md a reader must see. The ask, the drivers, and the approach were approved at the design gate and live in detail/design.md; the brief does not restate them. What lives HERE is the goal this contract delivers, the decisions to sign off, and the blocking risk. Keep it to about one screen. -->

### Goal
<!-- One sentence: a delta you can check true or false ("X moves from A to B"), tied to an observable outcome a success criterion pins down. Not "improve X". The sentence a reviewer signs, carried from the design's Goal — the design holds the request and drivers behind it. -->

### Decisions to sign off
<!-- Approach or operational calls a human must approve. The most important thing to surface. Tag each with its owner. Omit only if genuinely none. -->
- **<decision>** · owner: <compliance | infra | product | …>: <the tradeoff, why this way, the alternative rejected>. *<the question for the reviewer>*

### Blocking open questions
<!-- ONLY the questions that gate the release. The rest live under *Open questions & assumptions* in detail/design.md. Omit if none. -->
- **Open (blocking):** <question>; gates <what it blocks>.

### Blast radius & reversibility
<!-- One line each. The full touch-list is *Who & what this touches* (detail/design.md); the backout detail is *When it happens* (detail/contract.md). -->
- **Blast radius:** <one line: the reach if this misbehaves>
- **Reversibility:** <one line: until when it can be undone, and what becomes permanent once it ships>

### Rollout / cutover gate
<!-- The CONDITION under which this turns on ("ship only after N", "dark-launch, enable when M holds"). The mechanics (flag name, command sequence) are HOW → *When it happens* in detail/contract.md. -->

## Contents
<!-- The reading contract. Keep the promise lines below in the composed spec. They route each reader. Keep the section lists so a reader routes without opening both files. -->

**How to read this spec:** the design — the ask, the drivers, the approach — was reviewed and approved at the design gate; the approver signs the contract off from the brief above, opening the files below on doubt. The implementer and the auditor load the contract whole. A deep reviewer reads everything.

- [The contract](detail/contract.md), what the implementer builds and the auditor checks: *Requirements & success criteria* · *Constraints & non-functional bounds* · *Data & interface contract* · *When it happens* · *Out of scope* · *Known limitations & honest gaps* (incl. coverage exceptions) · *Verification approach & commands* (incl. the worked case)
- [The design](detail/design.md), the approved reasoning: *The request* · *Drivers* · *What's true today* · *Approach* · *Failure modes* (incl. contingencies) · *Who & what this touches* · *Open questions & assumptions*

<!-- ===================== FILE: detail/contract.md ===================== -->

# The contract
> Part of [spec.md](../spec.md) — <title>

<!-- The build contract is everything that binds: what the implementer builds against and the auditor checks against. Review-time reasoning goes in design.md, not here. This file is loaded whole into an implementing agent's context. -->

## Requirements & success criteria

<!-- The core of the contract. Group by subsystem/seam so a reviewer reads only their cluster; a single-subsystem change is simply one group. Each FR carries the success criterion that proves it, right beneath it. Grouping here also pre-draws the cut lines if the spec is ever split. -->

### <Subsystem / seam name>
<!-- Repeat this block per subsystem. -->

**Behavior**: <the observable flow in a few numbered steps: what an outside observer sees happen, not the code that does it>

**Requirements & success criteria**
<!-- One FR = one independently verifiable obligation. Name the actor and the action; one condition per sentence; behavior a reader can picture. If a single pass/fail test can't settle it, split it: no **and**-joined SHALLs, no embedded list of behaviors. A runtime condition may ride as a leading **WHEN**; cross-change sequencing goes under *When it happens*. Any guarantee word (every, only, always, never, cannot) here or in the Goal must trace to an FR whose check is as strong as the verb; where the check is weaker, downgrade the wording (mitigated, reduced, anchored). Skip implementation/lint trivia and jargon. -->
- **FR-001**: (WHEN <trigger/condition>,) the system SHALL <plain, concrete, observable behavior>.
  - **SC-001**: <measurable, technology-agnostic outcome that proves FR-001 on the running system>
<!-- Good:     WHEN an article's row is saved, the system SHALL show it as read. → SC: on reload it shows read.
     HOW-leak (Bad): The system SHALL call markRead() in reader.ts after the DB write. ← names the seam -->
- **FR-002**: the system SHALL <plain, concrete, observable behavior>.
  - **SC-002**: <the outcome that proves FR-002>

## Constraints & non-functional bounds

**Constraints**: <hard limits the design must respect: platform, volume, must-reuse, compliance. Not facts about current behavior, not a mechanism. Write "none" only after considering all four.>

**Non-functional bounds**: <performance, security, reliability, accessibility, each that applies with its threshold ("first reconcile finishes under N min"; "no PII in logs"). A bound checked post-ship also gets a success criterion. Write "none" only after walking all four.>

## Data & interface contract

<!-- Mark as "N/A — reason" if nothing crosses a boundary. ONLY externally observable contracts this change introduces or alters: an API request/response, an event/message, a persisted record other code depends on. Fields + meaning + invariants a reviewer can sign. NO language-typed struct: the concrete type and storage are HOW. Purely internal types do not belong here. -->
- **<contract / entity>**: <what it represents; the fields that matter and their meaning (e.g. `status`: one of open | paid | shipped); the invariants that must hold; who consumes it>.

## When it happens

**Triggers & preconditions**: <what conditions cause each behavior to occur (an event, a schedule, on-demand, a state change), and what must be true before it may run. A trigger owned by one FR stays on that FR; reference it here.>

**Ordering & dependencies**: <what must exist or land first. Reference `depends_on` specs by id; state internal ordering ("the backfill must complete before the new read path goes live"). State the CONSTRAINT, not the task list.>

**Rollout mechanics**: <the sequence of going live. The brief's rollout/cutover gate states the CONDITION; this is how the rollout proceeds once the condition holds.>

**Reversibility detail**: <the bounded backout. The brief states the fact and window; this is the detail of what's reversible and what's permanent (irreversible migrations, emitted events, external side effects).>

## Out of scope

- <excluded item>: <why, or where it lives instead>

## Known limitations & honest gaps

<!-- Part of the contract. Never bury it. What a passing check still would NOT prove, and what covers it instead (a manual check, production log-watching); plus each risk the design ACCEPTs rather than handles. Canonical home for accepted risk; *Failure modes* (design.md) references back here rather than restating. -->
- <admitted gap or accepted risk>: <what it leaves unproven, and what (if anything) covers it>

**Coverage exceptions**
<!-- The final-sweep artifact. Every FR has an SC beside it under *Requirements & success criteria*, or is listed here as a declared gap with a reason. A behavior an FR marks "must preserve" gets its own SC. List only the exceptions; no silent blanks. -->
- <FR-0xx: untested — reason>

## Verification approach & commands

<!-- What evidence would convince a skeptic the requirements hold, and which SC/FR each piece covers. Any behavior that crosses a real boundary (a database, an HTTP call, a queue, a contract between two modules) MUST be proven end-to-end across that boundary, not only in isolation; a pure rename / refactor / docs edit says so and why. -->
- <what evidence convinces a skeptic, and which SC/FR it covers>

**Worked case**
<!-- One concrete end-to-end example, with real values, not "the correct result". -->
- **Given:** <real starting state> · **When:** <action> · **Then:** <exact expected values>

**Commands:** <the exact commands to run to verify success, so anyone can reproduce the result>

<!-- detail/design.md is shaping-specs' output; its format is in shaping-specs/references/design-template.md. writing-specs reads it as input and does not create it. -->

<!-- ===================== END OF FILES ===================== -->

<!--
PARSE CONTRACT (lightweight). A spec is human-first Markdown across a folder, with a few machine-readable conventions a parser can read without understanding the prose:

1. Layout: docs/specs/{slug}/spec.md plus docs/specs/{slug}/detail/contract.md and docs/specs/{slug}/detail/design.md. spec.md is the entry point and holds the frontmatter and the decision brief; contract.md holds the binding sections; design.md holds the review-time sections. (Specs written under format 1.0.0 spread the equivalent sections one-per-file under detail/; locate a section by its heading either way.)
2. Frontmatter: YAML between the leading `---` fences in spec.md holds every queryable scalar (spec_monkey, id, kind, profile, parent, status, approved_by, approved_date, depends_on, supersedes). Never bury one in prose. The gate record (approved_by, approved_date) is present once status reaches approved and cleared when an amendment regresses it. `profile` is `full` (default, omit) or `light`; a `light` spec is a single spec.md carrying the FR/SC directly, and the linter pair-checks it there instead of in detail/contract.md.
3. Sections: the canonical section set is the schema. Each section lives in its fixed home file, under its canonical heading; or, for a folded block, its canonical `**bold**` key (convention 5); the mapping is spec.md's Contents block. Cite a section by its heading or key, never a number.
4. IDs are the join keys: FR-NNN (one SHALL obligation) and SC-NNN (one verifiable outcome), unique across the spec. Each SC sits directly beneath the FR it verifies under *Requirements & success criteria*.
5. Light conventions: `- **Key:** value` is a key/value field; `**Group**` on its own line introduces the block that follows. Everything else is opaque prose keyed by its heading.
-->
