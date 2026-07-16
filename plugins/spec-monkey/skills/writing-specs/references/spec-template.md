<!--
A SPEC IS A FOLDER OF THREE DOCUMENTS, ONE PER READER. This reference lays out every file to create. Each block below marked `FILE: <path>` is a separate file, delimited by an HTML comment. Create each at its path under docs/specs/{slug}/:

  docs/specs/{slug}/
    spec.md              the decision brief — the reviewer's document; approve or reject from it alone
    detail/contract.md   the build contract — what the implementer builds and the auditor checks
    detail/evidence.md   the review-time evidence — reasoning a deep reviewer opens on doubt

WHY THIS SPLIT: each reader wants a different slice, not a different amount: the reviewer the judgment layer, the implementer and auditor the mechanical layer, a deep reviewer the reasoning. Keep spec.md readable on its own; give each detail file a heading and a backlink so it stands alone too.

THE SECTION SET IS THE SCHEMA: every canonical section below must exist in its fixed home file, under its canonical heading; or, for a folded block (Coverage exceptions, Worked case, Contingencies), its canonical `**bold**` key. A detail section with nothing to say gets a justified `N/A — reason`, never silence; only the brief subsections marked as omittable may be dropped. Cite a section by its heading or bold key, never by a number or a position.

ONE SPEC, ONE DECISION: a spec covers exactly one independent decision. If the work spans several (distinct sign-off owners, reviewers, lifecycles/revert boundaries, or success criteria that partition into disjoint groups), split it into sequenced children linked by depends_on. The shared ground they stand on (the goal, data contracts, and invariants) lives in the project spec (kind: project), authored by grounding-specs; each child sets parent to it and cites its INV-NNN.

SINGLE SOURCE OF TRUTH: each fact lives in ONE section; everywhere else references it by ID (FR-001, SC-001), by section heading, or by a Markdown link. A one-line headline in the brief with the detail in a detail/ file is disclosure, not duplication. But the same sentence in two places is a copy. Cut it to a reference.

WHAT AND WHEN, NOT HOW: pin down WHAT to build, WHY, WHEN it happens, what CONSTRAINS it, and how you'll know it worked. Never dictate HOW: that's the implementer's call against the real code. The one exception is verification: the run commands that prove success are concrete (*Verification approach & commands*, in detail/contract.md).

Two interviews fill this template. shaping-specs/references/interview-questions.md works out the reasoning (the evidence file, plus the brief's Drivers and Decisions to sign off); writing-specs/references/interview-questions.md pins down the contract (requirements, data/interface, timing, verification). Work the questions to discover; use this template only to compose the answers.
-->

<!-- ===================== FILE: spec.md ===================== -->

---
spec_monkey: "1.3.0"             # spec-monkey format version; also marks this as a spec-monkey spec
id: SPEC-NNN                     # stable handle; commits and other specs reference this
kind: work-item                  # work-item (this template) | project (grounding-specs' project-template.md)
parent: SPEC-000                 # the project spec this grounds on; cite its INV-NNN, never restate them.
                                 # Omit only for a one-off change with no project spec.
title: <short imperative title>
status: draft                    # draft → approved → implemented → shipped → archived
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owners: [<@handle>]
standards: standards.md          # the constitution (ONE of: standards.md | CLAUDE.md | AGENTS.md)
depends_on: []                   # other SPEC-NNN that must ship first — feeds "When it happens"
supersedes: []                   # SPEC-NNN this replaces (delta lineage)
---

# Spec: <title>

## Decision brief
<!-- The whole of spec.md a reader must see. Decisions and blocking risk live HERE, not in a detail file. Keep it to about one screen. -->

### Goal
<!-- One sentence: a delta you can check true or false ("X moves from A to B"), tied to an observable outcome a success criterion pins down. Not "improve X". The sentence a reviewer signs. -->

### The request
> <one-to-two-sentence faithful summary of the ask; lets a reviewer catch drift>

### Drivers
<!-- The "why", as bullets. More than one unrelated driver is a signal the spec may be doing more than one job. Re-check the one-decision rule. -->
- <what is broken or missing, what leaving it costs, who benefits when fixed>

### Decisions to sign off
<!-- Approach or operational calls a human must approve. The most important thing to surface. Tag each with its owner. Omit only if genuinely none. -->
- **<decision>** · owner: <compliance | infra | product | …>: <the tradeoff, why this way, the alternative rejected>. *<the question for the reviewer>*

### Blocking open questions
<!-- ONLY the questions that gate the release. The rest live under *Open questions & assumptions* in detail/evidence.md. Omit if none. -->
- **Open (blocking):** <question>; gates <what it blocks>.

### Blast radius & reversibility
<!-- One line each. The full touch-list is *Who & what this touches* (detail/evidence.md); the backout detail is *When it happens* (detail/contract.md). -->
- **Blast radius:** <one line: the reach if this misbehaves>
- **Reversibility:** <one line: until when it can be undone, and what becomes permanent once it ships>

### Rollout / cutover gate
<!-- The CONDITION under which this turns on ("ship only after N", "dark-launch, enable when M holds"). The mechanics (flag name, command sequence) are HOW → *When it happens* in detail/contract.md. -->

## Contents
<!-- The reading contract. Keep the promise lines below in the composed spec. They route each reader. Keep the section lists so a reader routes without opening both files. -->

**How to read this spec:** the approver can sign off from the brief above alone, opening the files below on doubt. The implementer and the auditor load the contract whole. A deep reviewer reads everything.

- [The contract](detail/contract.md), what the implementer builds and the auditor checks: *Requirements & success criteria* · *Constraints & non-functional bounds* · *Data & interface contract* · *When it happens* · *Out of scope* · *Known limitations & honest gaps* (incl. coverage exceptions) · *Verification approach & commands* (incl. the worked case)
- [The evidence](detail/evidence.md), the review-time reasoning: *What's true today* · *Failure modes* (incl. contingencies) · *Who & what this touches* · *Open questions & assumptions*

<!-- ===================== FILE: detail/contract.md ===================== -->

# The contract
> Part of [spec.md](../spec.md) — <title>

<!-- The build contract is everything that binds: what the implementer builds against and the auditor checks against. Review-time reasoning goes in evidence.md, not here. This file is loaded whole into an implementing agent's context. -->

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

<!-- Part of the contract. Never bury it. What a passing check still would NOT prove, and what covers it instead (a manual check, production log-watching); plus each risk the design ACCEPTs rather than handles. Canonical home for accepted risk; *Failure modes* (evidence.md) references back here rather than restating. -->
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

<!-- ===================== FILE: detail/evidence.md ===================== -->

# The evidence
> Part of [spec.md](../spec.md) — <title>

<!-- The review-time reasoning: what a deep reviewer needs to judge the design, and what the author needed to reach it. After approval this file is rarely opened. Nothing that binds may live only here. A risk decision recorded in *Failure modes* must land in its contract home (an FR, *Known limitations & honest gaps*, or *Out of scope*); this file keeps the per-risk reasoning, and the auditor reads it as the index when tracing those decisions. -->

## What's true today

<!-- The load-bearing facts about current behavior the design rests on. Mark each verified fact or assumption; an assumption with residual risk also appears under *Open questions & assumptions*. -->
- <fact the design rests on> — <verified fact | assumption>

## Failure modes

<!-- Work EVERY lens. Each risk gets a decision: HANDLE (→ an FR), ACCEPT (→ Known limitations & honest gaps), or OUT-OF-SCOPE (say where it lives). An empty lens is valid only as "considered, none apply". Cite the FR a handled risk relates to. The **Contingencies** block at the end is the exception: fallbacks carry a trigger, not a decision, and bind nothing. -->

**Failure & scale**: behavior at 10× / 1000× load or data; a dependency down, slow, or rate-limited; concurrency, partial failure mid-operation, retries / idempotency; empty, huge, malformed, or hostile input.
- <risk>: <what happens> → HANDLE | ACCEPT | OUT-OF-SCOPE (FR-0xx)

**Operational readiness**: how it's observed live (logs, metrics, alerts); how a break is noticed; what config or environment it needs.
- <risk> → decision

**Trust boundary**: where untrusted input crosses into trusted code; who is authorized and what happens on denied or expired credentials; what sensitive or personal data is touched and protected.
- <risk> → decision

**Implied work**: callers or consumers that must change too; migrations or backfills forced; docs, configs, or types that go stale; what was assumed free but isn't.
- <risk> → decision

**Better way**: is there a simpler or safer approach? Name it, then resolve: adopt it, or record why this approach wins (→ a Decision to sign off).
- <finding> → resolution

**Contingencies**
<!-- Conditional fallbacks that fire ONLY if a trigger hits: not something the release must satisfy to ship, and not verifiable now. Kept OUT of the requirements list. Each sits here with its trigger. Mark as "N/A — reason" if none. -->
- **WHEN <trigger>**: <the fallback, and who acts>.

## Who & what this touches

**External**: <users, downstream data consumers, operators / runbooks, other services>

**Internal**: <callers, APIs, shared state that changes; what a rename or contract change ripples into, including what breaks at build time>

**Unchanged**: <the thing a reader will fear this breaks but it does NOT; naming it reassures>

## Open questions & assumptions

<!-- The non-blocking residue (blocking ones live in spec.md). Every unverified belief the design leans on. Empty (or each item explicitly deferred with a revisit trigger) before the human approves. Keep "the user decided X" OUT: a decision lives with its FR or its Decision to sign off. -->
- **Assumption:** <belief>; confidence <low | med | high>; if wrong, <impact>. Verify by <trigger>.
- **Open:** <question>; deferred, revisit if <SC-0xx fails>.

<!-- ===================== END OF FILES ===================== -->

<!--
PARSE CONTRACT (lightweight). A spec is human-first Markdown across a folder, with a few machine-readable conventions a parser can read without understanding the prose:

1. Layout: docs/specs/{slug}/spec.md plus docs/specs/{slug}/detail/contract.md and docs/specs/{slug}/detail/evidence.md. spec.md is the entry point and holds the frontmatter and the decision brief; contract.md holds the binding sections; evidence.md holds the review-time sections. (Specs written under format 1.0.0 spread the equivalent sections one-per-file under detail/; locate a section by its heading either way.)
2. Frontmatter: YAML between the leading `---` fences in spec.md holds every queryable scalar (spec_monkey, id, kind, parent, status, depends_on, supersedes). Never bury one in prose.
3. Sections: the canonical section set is the schema. Each section lives in its fixed home file, under its canonical heading; or, for a folded block, its canonical `**bold**` key (convention 5); the mapping is spec.md's Contents block. Cite a section by its heading or key, never a number.
4. IDs are the join keys: FR-NNN (one SHALL obligation) and SC-NNN (one verifiable outcome), unique across the spec. Each SC sits directly beneath the FR it verifies under *Requirements & success criteria*.
5. Light conventions: `- **Key:** value` is a key/value field; `**Group**` on its own line introduces the block that follows. Everything else is opaque prose keyed by its heading.
-->
