# Interview questions

The discovery instrument for the **project spec**. Not its layout: it follows the order you interrogate in, working backwards from every field [`project-template.md`](project-template.md) needs filled. Discover here; compose the answers afterward.

## How to use it

- **A conversation, not a questionnaire.** These are prompts, not a script. Skip what doesn't apply, reword to fit the user's context, and let each answer reshape the next question.
- **Ask relentlessly, one at a time.** Plain language, in the user's own words. No menu of options unless the choice is genuinely discrete and low-stakes.
- **Reflect every answer back.** "I think you mean X, which implies Y, right?" Surface the implication.
- **Recurse.** When an answer opens a sub-decision, chase it before moving on.
- **Separate decisions from assumptions.** On an existing codebase, mark each shared fact as *verified from the code* or *assumed*; ratify the assumptions with the human.
- **Keep it thin.** If a fact isn't shared across work items, or you can't defend it yet, it does not belong in the project spec. Push back on scope creep.
- **Write for one read.** One idea per sentence; caveats get their own sentence. Lists over running prose; never a wall of text, prefer multiple turns.

The areas below run in a natural discovery order. Each notes the template field(s) it fills.

---

## A. What we're building
*(fills: What we're building)*

- In two or three sentences, what is this system and what is it for? This is the frame every work item inherits.
- Greenfield, or does code already exist? If it exists, we read the shared contracts out of the code and ratify them; if not, we elicit them here.
- Who and what consumes this system at its edges?

## B. Shared data contracts
*(fills: Shared data contracts)*

- What are the canonical things this system stores or moves: the entities more than one work item will touch? Name each.
- For each: what does it represent, which fields matter and what do they mean, and what invariants must always hold on it? (Logical shape only; the concrete type and storage are the implementer's.)
- Which work items read it, and which write it? A contract only one work item touches is not shared. Leave it out.

## C. Invariants
*(fills: Invariants)*

- What must be true *system-wide*, across every work item, no matter which one is running? ("All inbound requests are signature-verified"; "money is stored in integer cents.")
- State each as a checkable property, not a wish. If you cannot say how it would be checked, it is an assumption. Record it as one.
- For each: what breaks, and how widely, if a single work item violates it? (This is why it lives here, not in one spec.)

## D. Trust boundaries
*(fills: Trust boundaries)*

- Where does untrusted input cross into trusted code at the system level? (A public endpoint, an uploaded file, a third-party callback.)
- At each boundary: who is authorized, what is verified, and what happens on denied or malformed input?
- What sensitive or personal data does the system hold, and what rule protects it everywhere?

## E. Architectural constraints
*(fills: Constraints)*

- What hard, expensive-to-reverse calls bound every work item: language, runtime, datastore, framework, deployment target, compliance regime?
- For each load-bearing one: why this way, and what was the alternative you rejected?
- What must be reused rather than rebuilt? What is off-limits to change?

## F. Work items & sequencing
*(fills: Work items & sequencing)*

- Break the goal into the work items you can see now. Name each in a line.
- What must land before what? State the ordering as a constraint ("the loader ships before the trainer"), not a schedule.
- Which is the first slice you'd actually build? (It gets the first work-item spec.)

## G. Scope & residue
*(fills: Out of scope · residual risk shown at the human gate)*

- What is explicitly *not* part of this system, that a reader might assume is?
- What shared decisions are you deliberately deferring until the work teaches you more? (These stay out of v1 and arrive by amendment.)
- What unverified beliefs does the whole design still rest on? For each: confidence, and the impact if wrong.
