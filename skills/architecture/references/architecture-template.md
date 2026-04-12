# Architecture Template

Copy-paste starting point for the architecture document. Narrative format —
write for the engineer who will build from this, not for a review board.

```markdown
# [System Name] — Architecture Document

**Last updated:** [Date]
**Author:** [Name]
**Status:** Living document — updated as each epic begins delivery

---

## 1. System Overview

### 1.1 Purpose

[1-2 sentences describing what this system does and why it exists. Connect
to the initiative's problem statement if one exists.]

### 1.2 System Context

[Describe how the system fits into its environment. What external systems
does it interact with? What does it depend on? What does it NOT own?
Write as a prose list of external systems with a sentence each explaining
the relationship.]

### 1.3 Major Components

[ASCII diagram showing the major internal components and how they connect.
Follow with a paragraph per component describing its responsibility.]

```
[ASCII component diagram here]
```

**[Component Name]** — [1-2 sentences: what it does, what goes in, what
comes out. Stateful or stateless?]

[Repeat for each component.]

### 1.4 Data Flow

[Describe the primary flow of data through the system as a numbered
sequence. This is the "happy path" — how data moves from input to output
under normal conditions.]

1. [Step 1]
2. [Step 2]
...

[Add a brief paragraph on what happens when a step fails.]

### 1.5 Key Architectural Decisions

[Each decision as a prose paragraph with a bold title. Include: what was
decided, why (trace to a constraint or quality need), and what
alternatives were rejected. Keep it readable — no formal ADR structure
needed.]

**[Decision title].**
[What was decided and why. What alternatives were considered and rejected.
What constraint or quality attribute drove this choice.]

[Repeat for each key decision. Typically 3-7 decisions for a
moderate-sized system.]

### 1.6 Non-Functional Requirements

[Bullet list of the quality attributes and operational requirements that
shape the architecture. Include specific numbers or thresholds where
possible — "under 100MB RAM while idle" not "low memory usage."]

- **[Category]:** [Specific requirement with threshold]
- **[Category]:** [Specific requirement]

---

## 2. Epic [N] — [Epic Title]

[Repeat this section for each epic. This section covers the architectural
detail needed to write stories for this specific epic.]

### 2.1 Components Involved

[Which components from the system overview are touched by this epic, and
in what capacity. Brief — just orient the reader.]

### 2.2 [Component Name] — Detail

[Deep technical detail for each component this epic touches. Include:]

- What it monitors/processes/produces
- Key technical challenges or design considerations
- API shape or interface contract (input → output)
- Specific technology APIs being used

[Repeat for each component involved in this epic.]

### 2.3 Unknowns and Spikes

[Technical questions that need investigation before or during story work.
These are things you can't fully design up front — they need a spike or
proof of concept.]

- [Unknown 1 — what you don't know and why it matters]
- [Unknown 2]

[If no unknowns, state "No significant unknowns identified."]

### 2.4 State / Data Model (if applicable)

[Schema, state machine, or data model relevant to this epic's scope.
Include concrete schemas when they clarify the design. For SQL, show the
CREATE TABLE. For state machines, list the states and transitions.]

### 2.5 Error Handling Strategy

[How errors are handled within this epic's scope. Distinguish between
transient failures (retry) and permanent failures (log and surface).
Describe what happens on daemon/process restart if applicable.]

### 2.6 What We Defer to Later Epics

[Explicitly name what this epic does NOT build that later epics will add.
This prevents scope confusion during story writing.]

---

[Repeat Section 2 for each epic: Section 3 for Epic 2, Section 4 for
Epic 3, etc.]
```
