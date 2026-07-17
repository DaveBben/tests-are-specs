<!--
THE DESIGN FILE — shaping-specs' output format, self-contained.

design.md is the whole product of shaping-specs: the converged reasoning a change rests on, worked out from a
fuzzy ask by weighing approaches, then drafted so writing-specs can compose the spec without re-interviewing.
It lives at docs/specs/{slug}/detail/design.md. shaping-specs writes this file and only this file;
writing-specs reads it (with the project spec) and composes spec.md and detail/contract.md from it.

It is a reviewable, gated artifact: reviewing-design critiques it, and a human approves it (status: approved)
before writing-specs turns it into a contract. That is why it carries its own light frontmatter and gate
record.

ALTITUDE: WHAT, WHY, and the high-level approach — never the file manifest, the exact symbols, or a typed code
block. The Approach section describes the shape of the solution, not the code that implements it.

THE SECTION SET IS THE SCHEMA: every section below exists under its canonical heading. A section with nothing
to say gets a justified "N/A — reason", never silence.
-->

---
spec_monkey: "1.7.0"             # spec-monkey format version; also marks this as a spec-monkey artifact
id: SPEC-NNN                     # the work item's handle; the design and the spec.md it feeds share it
kind: design                     # this file (shaping's output). The spec.md it feeds is kind: work-item.
parent: SPEC-000                 # the project spec this grounds on; cite its INV-NNN, never restate them.
                                 # Omit only for a one-off change with no project spec.
title: <short imperative title>
status: draft                    # draft → approved. The design gate: a human approves the converged design
                                 # before writing-specs composes the contract. Regresses to draft on a
                                 # material change to the approach.
approved_by: []                  # who approved the design; filled when status reaches approved, and cleared
                                 # if a material change regresses it. A self-set flip with no human here is
                                 # not a gate.
approved_date:                   # YYYY-MM-DD the human approved; set and cleared with approved_by.
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# The design
> Part of [spec.md](../spec.md) — <title>

## The request
<!-- Faithful one-to-two-sentence summary of the ask, even when it starts fuzzy. Lets a reviewer catch drift later. -->
> <the ask, in the user's terms>

## Goal
<!-- One sentence: a delta you can check true or false ("X moves from A to B"), tied to an observable
outcome a success criterion will pin down. Not "improve X". -->

## Drivers
<!-- The "why", as bullets. More than one unrelated driver is a signal the change may be doing more than
one job — re-check the one-decision gate. -->
- <what is broken or missing, what leaving it costs, who benefits when fixed>

## What's true today
<!-- The load-bearing facts about current behavior the design rests on. Mark each verified fact or
assumption; an assumption with residual risk also appears under Open questions & assumptions. -->
- <fact the design rests on> — <verified fact | assumption>

## Approach
<!-- The chosen shape of the solution, in high-level prose: what will be built and how the pieces fit,
enough that an implementer knows the intended shape without being handed a file or symbol. This section
carries design intent into implementing-specs, so make it real — but keep it above the code.

- Describe the shape: the moving parts and how they connect, the sequence, where the change sits in what
  exists. Prose, not a task list.
- Call out the non-obvious things: the parts a reader wouldn't guess, the sharp edges, the deliberate
  choices and what they rule out. This is where the value is; a bland restatement of the goal is not an
  approach.
- Survey the landscape, then converge. Name the genuinely different design philosophies open here — 2-3 real
  ones, not one plan and two strawmen — and for each its tradeoff and cost (runtime, complexity, operational
  burden, dollars, what it forecloses later). Then say why the chosen one wins. This is the heart of shaping:
  an ask that arrived fuzzy ("extract prefills with an LLM") leaves as a defended choice among the real
  alternatives. If only one sane approach exists, say so rather than manufacturing options.

Stay above the code: no file/seam manifest, no typed struct, no exact symbols — that is the implementer's
call against the real code. "A background worker drains a durable queue and retries with backoff" is the
altitude; "retry_worker.py polls RetryQueue every 5s" is HOW, and it does not belong here.

This section records the *engineer's* reasoning, sharpened by critique — not the AI's reasoning presented for
approval. If the engineer can't defend a choice here in their own words, that's a signal the shaping isn't
done, not a formatting gap to paper over. -->

## Failure modes
<!-- Work EVERY lens. Each risk gets a decision: HANDLE (→ an FR writing-specs will write), ACCEPT (→ Known
limitations & honest gaps), or OUT-OF-SCOPE (say where it lives). An empty lens is valid only as
"considered, none apply". The Contingencies block at the end is the exception: a fallback carries a trigger,
not a decision, and binds nothing. -->

**Failure & scale**: behavior at 10× / 1000× load or data; a dependency down, slow, or rate-limited;
concurrency, partial failure mid-operation, retries / idempotency; empty, huge, malformed, or hostile input.
- <risk>: <what happens> → HANDLE | ACCEPT | OUT-OF-SCOPE (FR-0xx)

**Operational readiness**: how it's observed live (logs, metrics, alerts); how a break is noticed; what
config or environment it needs.
- <risk> → decision

**Trust boundary**: where untrusted input crosses into trusted code; who is authorized and what happens on
denied or expired credentials; what sensitive or personal data is touched and protected.
- <risk> → decision

**Implied work**: callers or consumers that must change too; migrations or backfills forced; docs, configs,
or types that go stale; what was assumed free but isn't.
- <risk> → decision

**Better way**: is there a simpler or safer approach? Name it, then resolve: adopt it (fold it into
Approach), or record why the chosen approach wins.
- <finding> → resolution

**Contingencies**
<!-- Conditional fallbacks that fire ONLY if a trigger hits: not something the release must satisfy to ship,
and not verifiable now. Kept OUT of the requirements list. Mark "N/A — reason" if none. -->
- **WHEN <trigger>**: <the fallback, and who acts>.

## Verification strategy
<!-- High-level and prose: how we would know this works, not the exact commands. Name the evidence that would
convince a skeptic the approach holds — the behaviors to prove end-to-end, the failure modes above that need a
test, and anything that can only be checked by hand or in production. writing-specs turns this into the
concrete *Verification approach & commands* (the runnable commands and the worked case) in the contract; keep
this at the strategy level. If a behavior can't be tested, say so here — an approach you can't describe a test
for is usually underbaked, and catching that now is cheap. -->
- <what we'd prove, and how we'd know it held — prose, no exact commands>

## Who & what this touches

**External**: <users, downstream data consumers, operators / runbooks, other services>

**Internal**: <callers, APIs, shared state that changes; what a rename or contract change ripples into,
including what breaks at build time>

**Unchanged**: <the thing a reader will fear this breaks but it does NOT; naming it reassures>

## Open questions & assumptions
<!-- Every unverified belief the design leans on, and every unresolved question. Flag the release-gating
ones: writing-specs promotes those to the brief's Blocking open questions. Empty (or each item explicitly
deferred with a revisit trigger) before the human approves. Keep "the user decided X" OUT: a decision lives
with its Approach or its FR. -->
- **Assumption:** <belief>; confidence <low | med | high>; if wrong, <impact>. Verify by <trigger>.
- **Open:** <question>; deferred, revisit if <SC-0xx fails>.

<!--
WHAT WRITING-SPECS DOES WITH THIS FILE (for reference; not shaping's job):
- carries The request, Goal, and Drivers into spec.md's brief, refining only on real drift;
- turns the Approach's weighed decisions into the brief's Decisions to sign off;
- turns the Verification strategy into the contract's concrete Verification approach & commands;
- promotes the release-gating items here into the brief's Blocking open questions;
- binds the constraint facts and HANDLE risks into detail/contract.md.
The full spec-folder layout and parse contract live in writing-specs/references/spec-template.md.
-->
