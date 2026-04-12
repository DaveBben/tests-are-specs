# Story Decomposition Techniques

Use these techniques when creating the story breakdown in Phase 2.
**Always slice vertically — never horizontally.**

---

## Spike Stories (First-Class Concept)

When the architecture flags unknowns or spikes, the first story should
be a time-boxed spike that resolves them before feature work begins.

**When to create a spike:**
- Architecture lists unknowns about API behavior, platform capabilities,
  or integration approaches
- A technology is new, beta, or undocumented and core assumptions depend
  on it
- The integration approach with an external system is uncertain
- Performance characteristics are unknown and affect architectural
  decisions

**Spike format:**
- Questions to answer (not acceptance criteria)
- Definition of done focused on knowledge output
- Timebox (1-3 days typically)
- Explicit note that code is throwaway

**Spike is NOT:**
- A prototype (spikes produce knowledge, prototypes produce code)
- An open-ended research task (questions must be specific and answerable)
- A way to avoid committing to a design (spike answers questions, then
  you commit)

---

## Architecture-Driven Decomposition (Primary Technique)

When an architecture document exists with per-epic detail, derive
stories from its structure:

1. **Unknowns → Spike story** — resolve what you don't know
2. **Components → Feature stories** — one story per component the epic
   touches, each producing independently testable output
3. **State / data model → State story** — if the architecture defines a
   schema or state machine, state management is its own story
4. **Integration → Orchestration story** — wiring components together
   into a pipeline or workflow

This produces a natural dependency chain: spike → foundation components
→ state → integration.

---

## Vertical Slicing

Each story delivers end-to-end value for one slice of the epic. Like
slicing a layered cake vertically — you get every layer in every slice.

**Good vertical slices:**
- By pipeline stage: "Detect new files" / "Transcribe audio" /
  "Classify text" / "Create note" — each stage produces testable output
- By persona: "Admin can invite members" / "Member can accept invitation"
- By workflow step: "User can create draft" / "User can submit for review"
- By data type: "Import from CSV" / "Import from JSON"
- By business rule: "Basic pricing" / "Volume discount pricing"

**Pipeline-stage slicing is valid vertical slicing** when each stage
produces independently testable output. "Detect new files" is a vertical
slice because you can test it end-to-end (file appears → event emitted).
"Write the database layer" is NOT a vertical slice because it has no
independently testable user or developer value.

**Never slice horizontally:**
- "Backend story" / "Frontend story" / "Database story" — these create
  dependencies and deliver no value in isolation
- Exception: when the backend and frontend are genuinely independent
  products (different teams, different release cycles)

---

## SPIDR Framework (Mike Cohn)

Five techniques for splitting stories that are too large:

- **Spike**: Time-boxed investigation for unknowns (see above)
- **Paths**: Different user paths through the same capability
- **Interfaces**: Different I/O channels or platforms
- **Data**: Simplify or restrict data initially
- **Rules**: Relax business rules initially, add constraints later

---

## The Hamburger Method

Slice stories from most valuable to least:

1. **Walking skeleton**: Thinnest end-to-end path (first story)
2. **Essential toppings**: Core business rules and validations
3. **Nice toppings**: Enhanced UX, edge case handling, performance
4. **The works**: Advanced features, integrations, admin tools

---

## Story Independence Test

For each story, verify:
- Can it be built and tested independently?
- Does it deliver value to at least one persona on its own?
- Can it be estimated without knowing the implementation of other stories?
- Can you demo it and get meaningful feedback?

If a story fails these checks, it may need to be merged with another
story or restructured.
