<!--
A SPEC IS A FOLDER, NOT ONE FILE. This reference lays out every file to create. Each block below
marked `FILE: <path>` is a separate file, delimited by an HTML comment. Create each at its path
under docs/specs/{slug}/:

  docs/specs/{slug}/
    spec.md            the decision brief + a table of contents — always read this first
    detail/<name>.md   one file per section, opened on demand

WHY SPLIT: spec.md stays short and standalone, so a reader who opens only it still gets a correct
picture and can decide approve / push back / route to a specialist. The contract and the evidence
live in detail/, one section per file, so a reader — or an agent — opens only what they need. Keep
spec.md readable on its own; keep each detail file self-contained, with a heading and a backlink.

ONE SPEC, ONE DECISION: a spec covers exactly one independent decision. If the work spans several
(distinct sign-off owners, reviewers, lifecycles/revert boundaries, or success criteria that
partition into disjoint groups), split it — a parent holds the goal, shared contract, and
orchestration; each child holds one decision.

SINGLE SOURCE OF TRUTH: each fact lives in ONE file; everywhere else references it by ID (FR-001,
SC-001), by section name, or by a Markdown link. A one-line headline in the brief with the detail
in a detail/ file is disclosure, not duplication — but the same sentence in two places is a copy.
Cut it to a reference.

WHAT AND WHEN, NOT HOW: pin down WHAT to build, WHY, WHEN it happens, what CONSTRAINS it, and how
you'll know it worked. Never dictate HOW — that's the implementer's call against the real code. The
one exception is verification: the run commands that prove success are concrete (detail/verification.md).

The interview that fills this template lives in interview-questions.md. Work the questions to
discover; use this template only to compose the answers.
-->

<!-- ===================== FILE: spec.md ===================== -->

---
spec_monkey: "1.0.0"             # spec-monkey format version; also marks this as a spec-monkey spec
id: SPEC-NNN                     # stable handle; commits and other specs reference this
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
<!-- The whole of spec.md a reader must see. Decisions and blocking risk live HERE, not in a
     detail file. Keep it to about one screen. -->

### Goal
<!-- One sentence: a delta you can check true or false ("X moves from A to B"), tied to an
     observable outcome a success criterion pins down. Not "improve X". The sentence a reviewer signs. -->

### The request
> <one-to-two-sentence faithful summary of the ask; lets a reviewer catch drift>

### Drivers
<!-- The "why", as bullets. More than one unrelated driver is a signal the spec may be doing more
     than one job — re-check the one-decision rule. -->
- <what is broken or missing, what leaving it costs, who benefits when fixed>

### Decisions to sign off
<!-- Approach or operational calls a human must approve. The most important thing to surface. Tag
     each with its owner. Omit only if genuinely none. -->
- **<decision>** · owner: <compliance | infra | product | …>: <the tradeoff, why this way, the
  alternative rejected>. *<the question for the reviewer>*

### Blocking open questions
<!-- ONLY the questions that gate the release. The rest live in detail/open-questions.md. Omit if none. -->
- **Open (blocking):** <question>; gates <what it blocks>.

### Blast radius & reversibility
<!-- One line each. The full touch-list is detail/impact.md; the backout detail is detail/when-it-happens.md. -->
- **Blast radius:** <one line: the reach if this misbehaves>
- **Reversibility:** <one line: until when it can be undone, and what becomes permanent once it ships>

### Rollout / cutover gate
<!-- The CONDITION under which this turns on ("ship only after N", "dark-launch, enable when M holds").
     The mechanics (flag name, command sequence) are HOW → detail/when-it-happens.md. -->

## Contents
<!-- The table of contents. The contract and the evidence live in detail/; open what you need. Keep
     the one-line descriptions so a reader routes without opening every file. -->

**The contract** — what the sign-off binds you to
- [Requirements & success criteria](detail/requirements.md) — the observable rules and their proofs
- [Constraints & non-functional bounds](detail/constraints.md) — the limits the design must respect
- [Data & interface contract](detail/data-contract.md) — shapes and interfaces that cross a boundary
- [Out of scope](detail/out-of-scope.md) — what this deliberately does not do
- [Known limitations & honest gaps](detail/known-limitations.md) — accepted risk and what stays unproven
- [Coverage](detail/coverage.md) — every requirement maps to a proof, or a declared gap

**Evidence & detail** — what the implementer and a deep reviewer need
- [What's true today](detail/context.md) — the current-state facts the design rests on
- [Verification approach & commands](detail/verification.md) — the evidence and the exact commands
- [Worked case](detail/worked-case.md) — one concrete end-to-end example with real values
- [Failure modes](detail/failure-modes.md) — the five risk lenses and each decision
- [When it happens](detail/when-it-happens.md) — triggers, ordering, rollout mechanics, reversibility
- [Who & what this touches](detail/impact.md) — the full blast radius, external and internal
- [Open questions & assumptions](detail/open-questions.md) — the non-blocking residue
- [Contingencies](detail/contingencies.md) — fallbacks that fire only if a trigger hits

<!-- ===================== FILE: detail/requirements.md ===================== -->

# Requirements & success criteria
> Part of [spec.md](../spec.md) — <title>

<!-- The core of the contract. Group by subsystem/seam so a reviewer reads only their cluster; a
     single-subsystem change is simply one group. Each FR carries the success criterion that proves
     it, right beneath it. Grouping here also pre-draws the cut lines if the spec is ever split. -->

## <Subsystem / seam name>
<!-- Repeat this block per subsystem. -->

**Behavior**: <the observable flow in a few numbered steps: what an outside observer sees happen,
not the code that does it>

**Requirements & success criteria**
<!-- One FR = one independently verifiable obligation. Name the actor and the action; one condition
     per sentence; behavior a reader can picture. If a single pass/fail test can't settle it, split
     it — no **and**-joined SHALLs, no embedded list of behaviors. A runtime condition may ride as a
     leading **WHEN**; cross-change sequencing goes in detail/when-it-happens.md. Any guarantee word
     (every, only, always, never, cannot) here or in the Goal must trace to an FR whose check is as
     strong as the verb; where the check is weaker, downgrade the wording (mitigated, reduced,
     anchored). Skip implementation/lint trivia and jargon. -->
- **FR-001**: (WHEN <trigger/condition>,) the system SHALL <plain, concrete, observable behavior>.
  - **SC-001**: <measurable, technology-agnostic outcome that proves FR-001 on the running system>
<!-- Good:     WHEN an article's row is saved, the system SHALL show it as read. → SC: on reload it shows read.
     HOW-leak (Bad): The system SHALL call markRead() in reader.ts after the DB write. ← names the seam -->
- **FR-002**: the system SHALL <plain, concrete, observable behavior>.
  - **SC-002**: <the outcome that proves FR-002>

<!-- ===================== FILE: detail/constraints.md ===================== -->

# Constraints & non-functional bounds
> Part of [spec.md](../spec.md) — <title>

**Constraints**: <hard limits the design must respect: platform, volume, must-reuse, compliance.
Not facts about current behavior, not a mechanism. Write "none" only after considering all four.>

**Non-functional bounds**: <performance, security, reliability, accessibility — each that applies
with its threshold ("first reconcile finishes under N min"; "no PII in logs"). A bound checked
post-ship also gets a success criterion. Write "none" only after walking all four.>

<!-- ===================== FILE: detail/data-contract.md ===================== -->

# Data & interface contract
> Part of [spec.md](../spec.md) — <title>

<!-- Omit as "N/A — reason" if nothing crosses a boundary. ONLY externally observable contracts this
     change introduces or alters: an API request/response, an event/message, a persisted record other
     code depends on. Fields + meaning + invariants a reviewer can sign. NO language-typed struct —
     the concrete type and storage are HOW. Purely internal types do not belong here. -->
- **<contract / entity>**: <what it represents; the fields that matter and their meaning
  (e.g. `status`: one of open | paid | shipped); the invariants that must hold; who consumes it>.

<!-- ===================== FILE: detail/out-of-scope.md ===================== -->

# Out of scope
> Part of [spec.md](../spec.md) — <title>

- <excluded item>: <why, or where it lives instead>

<!-- ===================== FILE: detail/known-limitations.md ===================== -->

# Known limitations & honest gaps
> Part of [spec.md](../spec.md) — <title>

<!-- Part of the contract — never bury it. What a passing check still would NOT prove, and what
     covers it instead (a manual check, production log-watching); plus each risk the design ACCEPTs
     rather than handles. Canonical home for accepted risk; detail/failure-modes.md references back
     here rather than restating. -->
- <admitted gap or accepted risk>: <what it leaves unproven, and what (if anything) covers it>

<!-- ===================== FILE: detail/coverage.md ===================== -->

# Coverage
> Part of [spec.md](../spec.md) — <title>

<!-- The final-sweep artifact. Every FR has an SC beside it in detail/requirements.md, or is listed
     here as a declared gap with a reason. A behavior an FR marks "must preserve" gets its own SC.
     List only the exceptions; no silent blanks. -->
- <FR-0xx: untested — reason (see Known limitations & honest gaps)>

<!-- ===================== FILE: detail/context.md ===================== -->

# What's true today
> Part of [spec.md](../spec.md) — <title>

<!-- The load-bearing facts about current behavior the design rests on. Mark each verified fact or
     assumption; an assumption with residual risk also appears in detail/open-questions.md. -->
- <fact the design rests on> — <verified fact | assumption>

<!-- ===================== FILE: detail/verification.md ===================== -->

# Verification approach & commands
> Part of [spec.md](../spec.md) — <title>

<!-- What evidence would convince a skeptic the requirements hold, and which SC/FR each piece covers.
     Any behavior that crosses a real boundary (a database, an HTTP call, a queue, a contract between
     two modules) MUST be proven end-to-end across that boundary, not only in isolation; a pure
     rename / refactor / docs edit says so and why. -->
- <what evidence convinces a skeptic, and which SC/FR it covers>

**Commands:** <the exact commands to run to verify success, so anyone can reproduce the result>

<!-- ===================== FILE: detail/worked-case.md ===================== -->

# Worked case
> Part of [spec.md](../spec.md) — <title>

<!-- One concrete end-to-end example, with real values, not "the correct result". -->
- **Given:** <real starting state> · **When:** <action> · **Then:** <exact expected values>

<!-- ===================== FILE: detail/failure-modes.md ===================== -->

# Failure modes
> Part of [spec.md](../spec.md) — <title>

<!-- Work EVERY lens. Each risk gets a decision: HANDLE (→ an FR), ACCEPT (→ Known limitations &
     honest gaps), or OUT-OF-SCOPE (say where it lives). An empty lens is valid only as "considered,
     none apply". Cite the FR a handled risk relates to. -->

**Failure & scale**: behavior at 10× / 1000× load or data; a dependency down, slow, or rate-limited;
concurrency, partial failure mid-operation, retries / idempotency; empty, huge, malformed, or
hostile input.
- <risk>: <what happens> → HANDLE | ACCEPT | OUT-OF-SCOPE (FR-0xx)

**Operational readiness**: how it's observed live (logs, metrics, alerts); how a break is noticed;
what config or environment it needs.
- <risk> → decision

**Trust boundary**: where untrusted input crosses into trusted code; who is authorized and what
happens on denied or expired credentials; what sensitive or personal data is touched and protected.
- <risk> → decision

**Implied work**: callers or consumers that must change too; migrations or backfills forced; docs,
configs, or types that go stale; what was assumed free but isn't.
- <risk> → decision

**Better way**: is there a simpler or safer approach? Name it, then resolve: adopt it, or record why
this approach wins (→ a Decision to sign off).
- <finding> → resolution

<!-- ===================== FILE: detail/when-it-happens.md ===================== -->

# When it happens
> Part of [spec.md](../spec.md) — <title>

**Triggers & preconditions**: <what conditions cause each behavior to occur (an event, a schedule,
on-demand, a state change), and what must be true before it may run. A trigger owned by one FR stays
on that FR; reference it here.>

**Ordering & dependencies**: <what must exist or land first. Reference `depends_on` specs by id;
state internal ordering ("the backfill must complete before the new read path goes live"). State the
CONSTRAINT, not the task list.>

**Rollout mechanics**: <the sequence of going live. The brief's rollout/cutover gate states the
CONDITION; this is how the rollout proceeds once the condition holds.>

**Reversibility detail**: <the bounded backout. The brief states the fact and window; this is the
detail of what's reversible and what's permanent (irreversible migrations, emitted events, external
side effects).>

<!-- ===================== FILE: detail/impact.md ===================== -->

# Who & what this touches
> Part of [spec.md](../spec.md) — <title>

**External**: <users, downstream data consumers, operators / runbooks, other services>

**Internal**: <callers, APIs, shared state that changes; what a rename or contract change ripples
into, including what breaks at build time>

**Unchanged**: <the thing a reader will fear this breaks but it does NOT; naming it reassures>

<!-- ===================== FILE: detail/open-questions.md ===================== -->

# Open questions & assumptions
> Part of [spec.md](../spec.md) — <title>

<!-- The non-blocking residue (blocking ones live in spec.md). Every unverified belief the design
     leans on. Empty (or each item explicitly deferred with a revisit trigger) before the human
     approves. Keep "the user decided X" OUT — a decision lives with its FR or its Decision to sign off. -->
- **Assumption:** <belief>; confidence <low | med | high>; if wrong, <impact>. Verify by <trigger>.
- **Open:** <question>; deferred, revisit if <SC-0xx fails>.

<!-- ===================== FILE: detail/contingencies.md ===================== -->

# Contingencies
> Part of [spec.md](../spec.md) — <title>

<!-- Conditional fallbacks that fire ONLY if a trigger hits: not something the release must satisfy
     to ship, and not verifiable now. Kept OUT of the requirements list — each sits here with its
     trigger. Omit (or "N/A — reason") if none. -->
- **WHEN <trigger>**: <the fallback, and who acts>.

<!-- ===================== END OF FILES ===================== -->

<!--
PARSE CONTRACT (lightweight). A spec is human-first Markdown across a folder, with a few
machine-readable conventions a parser can read without understanding the prose:

1. Layout: docs/specs/{slug}/spec.md plus docs/specs/{slug}/detail/<name>.md. spec.md is the entry
   point and holds the frontmatter and the decision brief; each detail file is one section.
2. Frontmatter: YAML between the leading `---` fences in spec.md holds every queryable scalar
   (spec_monkey, id, status, depends_on, supersedes). Never bury one in prose.
3. Sections: cite a section by its file name or its heading, never a number. The canonical file set
   is the schema. spec.md links each detail file from its Contents table.
4. IDs are the join keys: FR-NNN (one SHALL obligation) and SC-NNN (one verifiable outcome), unique
   across the spec. Each SC sits directly beneath the FR it verifies in detail/requirements.md.
5. Light conventions: `- **Key:** value` is a key/value field; `**Group**` on its own line
   introduces the block that follows. Everything else is opaque prose keyed by its heading.
-->
