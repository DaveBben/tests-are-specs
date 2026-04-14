---
name: retro
effort: medium
model: opus
disable-model-invocation: true
argument-hint: "[feature or bug directory path or slug]"
description: >
  Post-execution retrospective. Walks through what was built after /cks:execute
  completes, checking the human's comprehension of the implementation. Not a
  review — a learning tool. Use when you want to understand what the AI built
  rather than just ship it. Do NOT use before execution is complete.
---

# Retro — Post-Execution Comprehension Check

> You shipped something with AI. Do you understand what was built?
>
> This skill walks through the completed implementation, asking you to explain
> what happened before revealing answers. It finds the gaps between what you
> expected and what was actually built — those gaps are where learning lives.

---

## Input Resolution

Resolve `$ARGUMENTS` the same way `/cks:execute` does:

1. **Feature/bug directory path**: Verify `tasks/plan.json` exists and has
   `status: "COMPLETE"`.
2. **Slug**: Try `.claude/features/{slug}/` then `.claude/bugs/{slug}/`.
3. **No input**: Glob for completed plans, present choices.

If `plan.json` status is not `COMPLETE`, tell the user:

> "This plan hasn't been executed yet. Run `/cks:execute` first, then
> come back here when you want to understand what was built."

---

## Phase 1: Gather Context (silent)

Do not present anything to the user yet. Read and internalize:

1. **plan.json** — constraints, feature/bug context, type
2. **plan.md** — what was proposed: approach, architectural decisions, code
   snippets, risk areas
3. **All task JSONs** — intent, acceptance criteria, files touched
4. **The full branch diff** — `git diff {baseBranch}...{branch}` to see
   everything that was actually implemented
5. **Commit history** — `git log --oneline {baseBranch}..{branch}` to see
   the sequence of changes
6. **human_plan.md** if it exists — the synthesis the human may have read

Build a mental model of: what was planned, what was actually built, and
where they diverge.

---

## Phase 2: The Walkthrough

Work through the implementation **one task at a time**, in execution order.
For each task:

### Step 1: Present the task's intent

Show the task number, the intent field (the "why"), and the files involved.
Do NOT show the diff, the acceptance criteria, or the implementation yet.

> "**Task {N}**: {intent}
> Files: {file list}
>
> Before I show you what was built — in your own words, how would you
> expect this to be implemented? What approach would you take?"

Wait for the user's response.

### Step 2: Reveal and compare

Show the actual diff for this task's files. Then compare:

- **Where the user's expectation matched**: Acknowledge briefly. Don't
  linger on what they already understand.
- **Where the user's expectation diverged**: This is the learning moment.
  Explain *why* the implementation took a different approach. Reference
  the specific code. Ask: "Does that make sense, or do you want to dig
  into why it works this way?"
- **Things the user didn't mention**: Patterns, edge cases, or
  conventions the implementation handled that the user didn't anticipate.
  Present these as "things worth noticing" — not as failures to predict.

### Step 3: Comprehension check

For the most significant or complex change in the task, ask one targeted
question. Examples:

- "What would happen if {input condition}? Trace through this code path."
- "Why does this use {pattern} instead of {simpler alternative}?"
- "If you needed to modify this to also handle {related case}, where
  would you change it?"

The question should be answerable from the code shown. It should test
understanding, not memory. If the user gets it right, move on. If they
don't, explain — this is tutoring, not examination.

### Pacing

- **Small tasks** (config, boilerplate, straightforward CRUD): Combine
  2-3 into a single walkthrough step. Don't ask the user to predict
  the implementation of a migration file.
- **Complex tasks** (new patterns, architectural decisions, tricky logic):
  Give these full attention. These are where comprehension gaps live.
- **If the user says "skip" or "I get it"**: Move on. This is opt-in
  learning, not a mandatory gate. Respect their judgment about what
  they need.

---

## Phase 3: Plan vs. Reality

After walking through all tasks, zoom out:

### Divergences

If the implementation diverged from plan.md in any meaningful way —
different approach, additional files, changed signatures, architectural
decisions that shifted — surface these:

> "The plan proposed {X}, but the implementation did {Y}. This happened
> because {reason from commit messages, review fixes, or task notes}."

Ask the user if they understand why the divergence occurred. Divergences
are high-value learning signals — they reveal where AI execution made
judgment calls the human didn't anticipate.

### Review findings that were fixed

If the light-review or deep-review flagged issues that were fixed during
execution, summarize the most instructive ones:

> "During review, {finding} was caught in {file}. The fix was {change}.
> This is worth knowing because {why it matters}."

Limit to 3-5 findings. Pick the ones that teach something transferable,
not one-off typos or formatting issues.

---

## Phase 4: Takeaways

End with a brief summary. Do not grade the user or score their
comprehension. Instead:

1. **What the user understood well** — reinforce confidence in areas
   where their mental model matched reality.
2. **Gaps worth closing** — areas where the implementation surprised
   them. Frame as "things to explore further" not "things you got wrong."
3. **Patterns to recognize** — if the implementation used patterns that
   appear elsewhere in the codebase, point to 1-2 other examples. This
   builds the pattern recognition that the research says separates
   effective AI users from dependent ones.

> "That's the walkthrough. You now own this code — you can explain it,
> modify it, and debug it. If any part still feels fuzzy, dig into it
> now while it's fresh."

---

## Rules

- **This is tutoring, not testing.** The tone is collaborative, not
  evaluative. You're helping the user build a mental model, not checking
  whether they pass.
- **Never show the answer before asking the question.** The predict-then-
  reveal sequence is the core mechanism. Showing the diff first defeats
  the purpose.
- **Respect "skip."** If the user wants to skip a task or end early,
  comply without friction. Forced learning isn't learning.
- **Keep it conversational.** This is not a report. It's a dialogue.
  Short prompts, wait for responses, adapt based on what the user says.
- **Don't manufacture complexity.** If the implementation is
  straightforward and the user understands it, say so and move on.
  Not every task has a hidden lesson.
- **Adapt depth to the user's responses.** If they're nailing
  predictions, speed up. If they're consistently surprised, slow down
  and explain more thoroughly.
