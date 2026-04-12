<!--
SINGLE SOURCE OF TRUTH: each decision lives in ONE place; everywhere else references it
by ID (FR-001, SC-001) and never restates it. Restating is the top cause of bloat and
drift. If two sections say the same thing, one is a copy. Cut it to a reference.

DISCOVERY LIVES IN THE QUESTIONS: orientation, clarifying interrogation, and the five
risk lenses ARE the section prompts below.

WHAT AND WHEN, NOT HOW: a good spec pins down WHAT to build, WHY it's needed, WHEN it
happens, what CONSTRAINS the solution, and how you'll know it worked. It never dictates
HOW to build it. That's the implementer's call: they work against the real code, and any
build detail frozen here only ties their hands and goes stale as the code moves.
-->

---
spec_monkey: "1.0.0"             # spec-monkey format version; also marks this as a spec-monkey spec
id: SPEC-NNN                     # stable handle; commits and other specs reference this
title: <short imperative title>
status: draft                    # draft → approved → implemented → shipped → archived
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owners: [<@handle>]
standards: standards.md          # the constitution (ONE of: standards.md | CLAUDE.md | AGENTS.md)
depends_on: []                   # other SPEC-NNN that must ship first — feeds "§ When it happens"
supersedes: []                   # SPEC-NNN this replaces (delta lineage)
---

# Spec: <title>

**Goal (verifiable):** <one sentence stating a delta you can check true or false: "X
moves from A to B", tied to an observable outcome a Success Criterion pins down. Not
"improve X". This is the single sentence a reviewer signs off on.>

## 1. The request
<!-- Q: In one or two sentences, what did the user actually ask for? Keep their intent
     faithful enough that a reviewer can catch drift. Summarize; don't paste the
     transcript. The mechanics live in "What it does"; don't restate them here. -->
> <one-to-two-sentence summary of the ask>

## 2. Why it matters
<!-- Q: What is broken or missing, and what does leaving it cost? Who benefits when it's
     fixed? Conclusion-first, a few sentences. -->

## 3. What it does
<!-- The observable change and the rules it must obey: behavior an outside observer can
     see, never the mechanism that produces it.-->

**Behavior**: <the observable flow in a few numbered steps: what an outside observer
sees happen, not the code that does it>

**Requirements**: the observable rules the change must satisfy. One rule per line, plain
English, keep the normative **SHALL**. Name the actor and the action; one condition per
sentence; describe behavior a reader can picture. A runtime condition may ride on the rule
as a leading **WHEN**; cross-change sequencing goes in "When it happens" instead. Skip
implementation or lint trivia, stacked clauses, and noun-form jargon.
- **FR-001**: (WHEN <trigger/condition>,) the system SHALL <plain, concrete, observable behavior>.
<!-- Good:     WHEN an article's row is saved, the system SHALL show it as read.
     HOW-leak (Bad): The system SHALL call markRead() in reader.ts after the DB write. ← names the seam -->
- **FR-002**: the system SHALL <plain, concrete, observable behavior>.

**Scope decisions to sign off** *(approach or operational calls a human must approve; omit if none)*
- **<decision>**: <the tradeoff, why this way, and the alternative rejected>. *<the question for the reviewer>*

**Out of scope**
- <excluded item>: <why, or where it lives instead>

## 4. When it happens
<!-- First-class: this change is about WHAT *and WHEN*. This section owns time and order.
     Statethe conditions and constraints, not the mechanism that enforces them. Omit a 
     sub-point as "N/A — reason" only after genuinely considering it. -->

**Triggers & preconditions**: <what conditions cause each behavior to occur (an event, a
schedule, on-demand, on a state change), and what must be true before it may run. A trigger
that belongs to exactly one FR stays on that FR; reference it here rather than restating.>

**Ordering & dependencies**: <what must exist or land first. Reference `depends_on` specs by
id; state any internal ordering the change requires ("the backfill must complete before the
new read path goes live"). State the CONSTRAINT, not the task list that satisfies it.>

**Rollout timing & gating**: <the sequence of going live and the gating conditions: "ship
only after N", "dark-launch, then enable when M holds". Name the risky moment and the
observable signal to watch. The mechanism (flag name, command) is HOW → harness; the
CONDITION is WHAT/WHEN → here.>

**Reversibility window**: <until when can this be undone, and what becomes permanent once it
ships (irreversible migrations, emitted events, external side effects)? The bounded cost of
backing out. The undo *procedure* is the implementor's; the *fact* of what's reversible and
until when is the spec's.>

## 5. How it fits
<!-- Ground the change in the system as it is today, at the level of TRUTHS and CONSTRAINTS,
     not a file tour. Do a blast-radius sweep: grep wide for the ripple 
     across potentially many unknown sites, and assume you missed something. If the sweep
     turns up scope you had not accounted for, loop back to the human before writing. -->

**What's true today (that constrains this)**: <the load-bearing facts about current behavior
the design rests on. Mark each as verified fact or assumption; an assumption with residual
risk also appears in "Open questions & assumptions".>

**Constraints**: <hard limits imposed on the change: platform, volume, must-reuse, compliance.
These are boundaries the design must respect, not facts about current behavior and not a
mechanism; a reviewer checks the direction against them. Write "none" only after considering all four.>

**Non-functional bounds**: <walk performance, security, reliability, accessibility; state each
that applies with its threshold ("first reconcile finishes under N min"; "no PII in logs"). A
bound checked post-ship also gets a Success criterion. Write "none" only after walking all four.>

**Depends on**: <external services / APIs / other specs / teams the change rides on. Cross-spec
ordering is echoed in "When it happens".>

## 6. Data & interface contracts *(omit as "N/A — reason" only if nothing crosses a boundary)*
<!-- ONLY the externally observable contracts this change introduces or alters: an API
     request/response, an event or message, a persisted record other code or teams depend on.
     Describe each as fields + meaning + invariants a reviewer can sign. Do NOT paste a
     language-typed struct or class: the concrete type, language, and storage are HOW the
     implementor picks. Purely internal types do not belong here at all. -->
- **<contract / entity>**: <what it represents; the fields that matter and their meaning
  (e.g. `status`: one of open | paid | shipped); the invariants that must hold; who consumes it>.

## 7. What could go wrong
<!-- Work EVERY lens. For each risk you surface, record a decision: HANDLE (→ covered by an FR,
     or listed here with how it's handled), ACCEPT (state why it's tolerable), or OUT-OF-SCOPE
     (say where it lives). An empty lens is valid only as "considered, none apply". Cite the FR
     a handled risk relates to. Skip a case an FR already fully pins. -->

**Failure & scale**: behavior at 10× / 1000× load or data; a dependency down, slow, or
rate-limited; concurrency, partial failure mid-operation, retries / idempotency; empty, huge,
malformed, or hostile input.
- <risk>: <what happens> → HANDLE | ACCEPT | OUT-OF-SCOPE (FR-0xx)

**Operational readiness**: how it's observed live (logs, metrics, alerts); how a break is
noticed; what config or environment it needs. State the observable NEED; the wiring is HOW → harness.
- <risk> → decision

**Trust boundary**: where untrusted input crosses into trusted code; who is authorized and what
happens on denied or expired credentials; what sensitive or personal data is touched and how it's
protected.
- <risk> → decision

**Implied work**: callers or consumers that must change too; migrations or backfills forced; docs,
configs, or types that go stale; what was assumed free but isn't.
- <risk> → decision    <!-- feeds "Who & what this touches" -->

**Better way**: is there a simpler or safer approach? Name it, then resolve: adopt it, or record
why this approach wins (→ a Scope decision in "What it does").
- <finding> → resolution

## 8. Who & what this touches
<!-- The reach beyond the behavior itself; draws on the Implied-work lens above. -->
**External**: <users, downstream data consumers, operators / runbooks, other services>
**Internal**: <callers, APIs, shared state that changes; what a rename or contract change ripples into, including what breaks at build time>
**Unchanged**: <the thing a reader will fear this breaks but it does NOT; naming it reassures>

## 9. How I know it works
<!-- What must be proven, and the commands that prove it. Success criteria are the verifiable
     definition of done; the Worked case shows one true instance. Verification is the one place the
     spec gets concrete: give the actual run commands so anyone can execute them and watch it pass. -->

**Success criteria** *(each a measurable, technology-agnostic outcome, observable end-to-end)*
- **SC-001**: <e.g. "a saved article shows read on reload", "95% of X complete within 1s">
<!-- not "uses Redis", not "the unit test passes": an outcome, not a mechanism -->

**Verification approach** *(what must be shown true, and the exact commands that show it)*
- <what evidence would convince a skeptic the requirements hold, and which SC/FR each piece of
  evidence covers. Any behavior that crosses a real boundary (a database, an HTTP call, a queue,
  a contract between two modules) MUST be proven end-to-end across that boundary, not only in
  isolation; a change with no such runtime behavior (a pure rename / refactor / docs edit) says so
  and why.>
- **Commands:** <the exact commands to run to verify success, so anyone can reproduce the result>

**Worked case** *(one concrete end-to-end example, with real values, not "the correct result")*
- **Given:** <real starting state> · **When:** <action> · **Then:** <exact expected values>

**Honest gap** *(what a passing check still would NOT prove, and what covers it instead: a manual
check, production log-watching. Omit only if the criteria truly prove everything.)*

## 10. Open questions & assumptions
<!-- The interrogation residue, kept honest. Every unverified belief the design leans on, and every
     unresolved question. This section MUST be empty (or each item explicitly deferred with a
     revisit trigger) before the human approves. Keep "the user decided X" OUT of here; a decision
     lives with its FR or its Scope decision. -->
- **Assumption:** <belief>; confidence <low | med | high>; if wrong, <impact>. Verify by <trigger>.
- **Open:** <question>; <blocking | deferred, revisit if SC-0xx fails>.

---

# Parse contract (lightweight)

The spec is **human-first Markdown** with a few machine-readable conventions. A parser reads it
without understanding the prose.

1. **Frontmatter**: YAML between the leading `---` fences holds every queryable scalar
   (`spec_monkey`, `id`, `status`, `depends_on`, `supersedes`). Never bury one in prose.
2. **Sections**: `^## (\d+)\. <name>`; the canonical set and order are the schema. Cite a section
   by its **header name**, never its number (numbers shift).
3. **IDs are the join keys**: `FR-NNN` (one SHALL rule) and `SC-NNN` (one verifiable outcome),
   unique within the spec. Risks and success criteria reference the FR they exercise; nothing
   is restated.
4. **Light conventions**: `- **Key:** value` is a key/value field; `**Group**` on its own line
   introduces the list/table/block that follows. Everything else is opaque prose keyed by its heading.
