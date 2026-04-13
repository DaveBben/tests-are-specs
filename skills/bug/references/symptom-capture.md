# Symptom Capture — Phase 0

**Goal: Capture what the user observed through conversation. The output is
structured symptom data that feeds the research and reproduction phases.**

A good bug report answers one question: **what did you observe, and how can
someone else observe it too?**

## Step 1: Understand the Symptom

Start by listening. Ask the user to describe what happened in their own words.

After hearing the description, check for **diagnosis leakage** — is the user
describing a root cause instead of an observable symptom?

**Diagnosis signals to push back on:**

- Technical jargon as the primary description ("race condition," "null pointer,"
  "cache invalidation bug," "memory leak")
- The description explains *why* something happens rather than *what* happens
- The user leads with a code location ("the bug is in `handleSubmit`")

**If diagnosis detected:**

> "That sounds like a diagnosis of the cause. Let's capture the symptom first —
> what did you or the user actually see? For example, instead of 'race
> condition in the save handler,' what observable behavior happened? Did data
> disappear? Did the page freeze? Did stale content display?"

Help them reframe. The diagnosis may be correct, but it belongs in the
research phase, not the symptom description.

**Scope check:** If the description contains multiple distinct bugs ("and also,
there's another issue where..."), push back:

> "That sounds like two separate bugs. Let's capture one at a time — which one
> is more urgent? We'll create a card for the other one after."

See [anti-patterns.md](anti-patterns.md) for the full
list of patterns to watch for during this phase.

## Step 2: The Bug Conversation

Work through these topics conversationally — do NOT present them as a
checklist. Ask 1-2 questions at a time, build on answers, and push back on
vagueness.

**These rounds organize YOUR thinking — they are not a script to follow
literally.** The user's answers will naturally jump between rounds. Follow
their thread, cover the gaps organically, and only use the round structure
to check that nothing was missed before moving to research.

### Round A: Environment

Establish where and when this bug was observed:

- Operating system and version
- Browser or runtime and version (if applicable)
- Application version or build number
- Deployment environment (production, staging, local dev)
- Any relevant configuration (feature flags, user role, account type)

Don't ask for every field if they're not relevant. A backend API bug doesn't
need a browser version. Use judgment.

### Round B: Steps to Reproduce

Walk through what the user did, step by step:

- **Start state**: What was true before the bug appeared?
- **Actions**: What did they do, in what order?
- **Observation**: At which step did the unexpected behavior appear?

**Push back on vagueness:**

- "It just breaks" -> "What exactly do you see when it breaks?"
- "Sometimes it happens" -> "Can you describe the last time it happened?"
- "It doesn't work" -> "What specifically doesn't work? What did you expect
  to see vs. what appeared?"

The goal is **a sequence someone else can follow to trigger the bug
consistently.** If the user can't reproduce it reliably, note that explicitly.

### Round C: Expected vs Actual Behavior

Both must be concrete and specific:

- **Expected**: What should have happened? If the user doesn't know the
  expected behavior, help them reason about it from the feature's intent.
- **Actual**: What did happen? Include specifics: error messages (exact text),
  visual state, data returned, HTTP status codes, timing.

### Round D: Severity and Impact

Establish the business impact:

- **Who is affected?** All users? A specific segment? Just one user?
- **How often?** Every time? Intermittently? Only under specific conditions?
- **Is there a workaround?** Can users accomplish their goal another way?
- **What's the blast radius?** Data loss? Security exposure? Feature unusable?

**Severity levels:**

| Level | Criteria |
|-------|----------|
| Critical | Data loss, security vulnerability, complete feature outage, no workaround |
| High | Core feature broken, significant user impact, no reasonable workaround |
| Medium | Feature broken but workaround exists, or non-core feature broken |
| Low | Cosmetic issue, minor inconvenience, edge case with easy workaround |

Help the user calibrate — people tend to overrate severity of bugs they
personally encountered.

### Round E: Evidence

Ask what evidence exists:

- Screenshots or screen recordings
- Error messages (exact text, not paraphrased)
- Log output or stack traces
- Network requests/responses (HTTP status, response body)

If the user has none: "Can you reproduce the bug now and capture the error
message or a screenshot?"

## Step 3: Confirm Before Research

Before proceeding to automated phases, summarize the symptom back to the
user:

> "Here's what I've captured:
>
> **Symptom**: [title — must describe the symptom, not the cause]
> **Environment**: [key details]
> **Steps to Reproduce**: [numbered steps]
> **Expected**: [what should happen]
> **Actual**: [what does happen]
> **Severity**: [level] — [impact summary]
>
> I'll now research the codebase and attempt to reproduce this
> programmatically. Anything to correct before I proceed?"

**Do not proceed to Phase 1 until the user acknowledges the summary.**

## Step 4: Generate Exploration Questions

After the user confirms the symptom summary, generate **10 Exploration
Questions** — specific, codebase-answerable questions that the Explore
agents in Phase 1 **MUST answer with `file:line` evidence**. These
questions force agents to trace the **downstream ripple** of the bug and
its fix, not just the immediate code path where the symptom appears.

Generate the questions from the confirmed symptom data (environment,
reproduction steps, expected vs actual behavior, severity). Each question
should connect the bug to parts of the codebase the agents might otherwise
overlook.

Good exploration questions for bugs target:
- **Code path callers**: "What other code paths call the function where
  the symptom manifests? Could they exhibit the same bug?"
- **Shared state**: "Does the affected code path share state (caches,
  singletons, globals) with other features that might mask or amplify
  the bug?"
- **Test coverage gaps**: "Which tests exercise this code path, and what
  scenarios do they miss?"
- **Error handling**: "How does the code path handle failures at each
  step? Could a swallowed error explain the symptom?"
- **Recent changes**: "What commits touched these files in the last 2
  weeks? Could a recent change have introduced a regression?"
- **Configuration sensitivity**: "Are there config values, feature flags,
  or environment variables that could change this code path's behavior?"
- **Similar patterns**: "Does the same pattern (e.g., cache invalidation,
  state update, event dispatch) exist elsewhere? Are those instances
  affected too?"
- **Data flow boundaries**: "Where does data cross module or service
  boundaries in this path? Could serialization, type coercion, or
  validation at a boundary explain the symptom?"
- **Documentation & contracts**: "Are there API contracts, type
  definitions, or documented invariants that the buggy behavior violates?"
- **Rollback impact**: "If we fix this, what downstream consumers of the
  current (buggy) behavior might break because they adapted to it?"

Not all categories will apply to every bug. Generate the 10 questions
most relevant to *this specific symptom*. Record the questions in
research.md (see template).

---

## Conversation Rules

- **One question at a time.** Do not dump a list of 10 questions — multiple
  questions overwhelm users and produce lower-quality answers as they rush
  through items.
- **Push back on vagueness.** Every vague statement gets restated in specific
  terms: "When you say 'it breaks,' I interpret that as [specific behavior].
  Is that right?"
- **Name the anti-pattern.** When you see a common mistake, name it:
  "That's a diagnosis, not a symptom," or "That reproduction step assumes
  too much."
- **Celebrate good input.** When the user provides a clear reproduction
  sequence or exact error message, acknowledge it — positive reinforcement
  helps them know what detail level is useful.
- **The conversation IS the Phase 0 deliverable.** Do not write the symptom
  summary silently.

---

## Common Failure Patterns

- **Confident divergence** — The AI traces the obvious code path, infers the
  rest, and misses downstream consumers, shared state, or callers in
  unexpected locations that are also affected by the bug or its fix. The 10
  Exploration Questions exist specifically to force outward exploration beyond
  the immediate symptom site.
- **Skimming instead of reading** — Phase 1 exists because the AI reads at
  signature level and moves on. Force deep reading: "read the full function
  body", "trace every caller."
- **Planning before researching** — Research must complete BEFORE any plan.
- **Pseudocode in the plan** — The plan must contain actual code snippets.
- **Scope creep into refactoring** — Bug fixes must be minimal. The "What
  NOT to Do" section prevents this.
- **Reproduction test committed prematurely** — The Phase 2 test is a draft.
  Do not commit it. The task breakdown assigns proper test writing to the
  TDD agent.
- **Diagnosis in the symptom title** — The title describes what the user
  sees, not what the code does wrong.
