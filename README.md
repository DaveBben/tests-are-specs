# Claude KISS — Keep it Simple Stupid

A focused set of Claude Code skills that turn ideas and bugs into implemented, reviewed code. No multi-stage planning pipelines. Direct entry points only.

## Installation

Install as a Claude Code plugin:

```bash
# Add the marketplace
/plugin marketplace add <owner>/backlog-driven-development

# Install the plugin
/plugin install cks@cks-marketplace
```

Or test locally:

```bash
claude --plugin-dir ./backlog-driven-development
```

All skills are namespaced under `cks:` (e.g., `/cks:feature`, `/cks:execute`).

---

## Routing

```
Is this a new codebase or one you haven't onboarded yet?
  └── Yes → /cks:onboard  (creates CLAUDE.md + spec.md, then come back here)

Is the change one or two lines?
  └── Yes → Use vanilla Claude Code with plan mode. No skills needed.

Is it a bug?
  └── Yes → /cks:bug → then /cks:execute

Is it a new feature or capability?
  └── Yes → /cks:feature → then /cks:execute

Want to understand what was just built?
  └── Yes → /cks:retro (after /cks:execute completes)
```

### Depth Modes

Not every change needs the full pipeline. Pick the depth that matches your situation:

| Mode | When to use | What to do |
|------|------------|------------|
| **Quick fix** | You know exactly what to change, < ~50 lines | Skip /cks:feature entirely. Write a task JSON manually and run `/cks:execute`, or just use vanilla Claude Code. |
| **Experienced** | You know the codebase well, the feature is straightforward | Run `/cks:feature` — when gates present output, confirm quickly or say "continue" to keep moving. The workflow won't block you unless something looks structurally wrong. |
| **Full pipeline** | New to the codebase, complex feature, high-risk area, or compliance-sensitive work | Run `/cks:feature` — engage with every gate, review the devil's advocate challenges carefully, annotate the plan thoroughly. This is the maximum-guidance path. |

---

## Skills

| Skill | What it does | Artifacts produced |
|---|---|---|
| `/cks:onboard` | Sets up context for a new or existing codebase | `CLAUDE.md`, `spec.md` |
| `/cks:feature` | Investigates scope, produces a plan and TDD task files | `.claude/features/{slug}/plan.md`, `.claude/features/{slug}/tasks/task_N.md`, `.claude/features/{slug}/human_plan.md` |
| `/cks:bug` | Captures symptom, root cause, and fix tasks | `.claude/bugs/{slug}/plan.md`, `.claude/bugs/{slug}/tasks/task_N.md`, `.claude/bugs/{slug}/human_plan.md` |
| `/cks:execute` | Implements tasks: TDD cycle + two-tier review + PR | Branch, commits, PR |
| `/cks:retro` | Post-execution comprehension walkthrough — understand what was built | Dialogue (no artifacts) |
| `/cks:light-review` | Single-agent code review across all dimensions | Review report |
| `/cks:deep-review` | Four-agent parallel review (security, reliability, maintainability, performance) | Consolidated review report |

---

## Skill Details

### `/cks:onboard`

Run this first on any codebase — new or existing. The skill reads the repository, asks targeted questions about purpose, tech stack, conventions, and constraints, then produces:

- **`CLAUDE.md`** — quick-reference context that Claude Code loads on every conversation
- **`spec.md`** — living specification describing what the system does, key decisions, and known constraints

Once onboarded, `/cks:feature` and `/cks:bug` plans have rich context to work from, reducing the questions they need to ask.

### `/cks:feature`

Investigative conversation that clarifies scope, constraints, and acceptance criteria. The skill reads any existing `CLAUDE.md` and `spec.md` for context, explores the codebase, then produces:

- **`plan.md`** — what is being built, why, constraints, and scope boundaries
- **`task_N.md` files** — one per task, each with: relevant files (strict boundary for the executor), acceptance criteria (GIVEN/WHEN/THEN), verification description, and explicit anti-scope (Do NOT list)
- **`human_plan.md`** — concise synthesis of all artifacts for developers who want to implement the feature themselves rather than using `/cks:execute`

A `devils-advocate` agent challenges the plan before it is finalized.

Multi-repo: when a feature spans multiple repositories, `/cks:feature` records all repository paths and tags each task with its target repository. Works best with monorepos or co-located repos. For separate repos, contract stubs decouple execution — see `/cks:execute` docs.

### `/cks:bug`

Guides the user through: symptom description, environment, reproduction steps, expected vs actual behavior, severity, and root cause investigation. Produces:

- **`plan.md`** — bug context, root cause, severity
- **`task_N.md` files** — fix tasks with the same TDD structure as feature tasks
- **`human_plan.md`** — concise synthesis of all artifacts for developers who want to fix the bug themselves rather than using `/cks:execute`

Execute with `/cks:execute`.

### `/cks:execute`

Takes a feature or bug plan directory and processes all tasks:

1. Create branch (`feature/{slug}` or `bugfix/{slug}`)
2. For each task: 3-agent TDD cycle (`tdd-test-writer` → `tdd-code-implementor` → `tdd-code-refactor`)
3. `/cks:light-review` after each task — fast review, findings fixed before moving on
4. `/cks:deep-review` after all tasks — thorough cross-cutting review, findings fixed
5. Push branch + create PR using `gh`

Multi-repo: tasks are tagged with their target repository. Each repo is processed sequentially with contract stubs to decouple cross-repo dependencies.

### `/cks:retro`

Post-execution comprehension check. After `/cks:execute` completes, this skill walks through the implementation task by task, asking you to predict how each task was implemented before revealing the actual diff. Finds the gaps between what you expected and what was built — those gaps are where learning happens.

Use this when:
- You used `/cks:execute` on unfamiliar code or a new codebase
- You want to own the code the AI produced, not just ship it
- You're growing into a domain and want to build mental models faster

Not a review, not a gate — a learning tool. Entirely opt-in, skip any task at any time.

### `/cks:light-review`

Single-agent review covering correctness, readability, security surface, and maintainability in one pass. Used automatically by `/cks:execute` after each task. Can also be invoked standalone.

### `/cks:deep-review`

Four agents run in parallel, each focused on one dimension:

| Agent | Focus |
|---|---|
| `security-reviewer` | Injection, access control, data exposure |
| `reliability-reviewer` | Correctness, race conditions, resource lifecycle |
| `maintainability-reviewer` | Readability, compatibility, conventions |
| `performance-reviewer` | N+1 queries, blocking I/O, resource leaks |

Results are consolidated into a single report. Used automatically by `/cks:execute` after all tasks for a repo complete.

---

## Agents

| Agent | Role | Used by |
|---|---|---|
| `devils-advocate` | Challenges feature plan scope, criteria, and assumptions | `/cks:feature` |
| `plan-verifier` | Fact-checks plan.md references against the codebase | `/cks:feature` |
| `human-plan-synthesizer` | Synthesizes artifacts into a human-readable implementation guide | `/cks:feature`, `/cks:bug` |
| `tdd-test-writer` | RED phase — writes failing tests from acceptance criteria | `/cks:execute` |
| `tdd-code-implementor` | GREEN phase — minimum code to make tests pass | `/cks:execute` |
| `tdd-code-refactor` | REFACTOR phase — improves code while keeping tests green | `/cks:execute` |
| `generic-code-reviewer` | All-dimensions fast review | `/cks:light-review` |
| `security-reviewer` | Injection, access control, data exposure | `/cks:deep-review` |
| `reliability-reviewer` | Correctness, race conditions, resource lifecycle | `/cks:deep-review` |
| `maintainability-reviewer` | Readability, compatibility, conventions | `/cks:deep-review` |
| `performance-reviewer` | N+1 queries, blocking I/O, resource leaks | `/cks:deep-review` |

---

## Artifact Storage

Plans and tasks are stored per-project inside `.claude/`:

```
{project-root}/
  .claude/
    features/
      {slug}/
        plan.md
        human_plan.md
        tasks/
          task_0.md
          task_1.md
    bugs/
      {slug}/
        plan.md
        human_plan.md
        tasks/
          task_0.md
```

`plan.md` contains metadata, context, and constraints for the feature or bug. `task_N.md` files contain individual TDD tasks: relevant files, acceptance criteria, verification, and anti-scope.

---

## File Structure

```
cks/
  .claude-plugin/
    plugin.json
    marketplace.json
  skills/
    feature/
      SKILL.md
      references/
        templates.md
        implementation-guidance.md
    bug/
      SKILL.md
      references/
        templates.md
    execute/
      SKILL.md
    retro/
      SKILL.md
    light-review/
      SKILL.md
    deep-review/
      SKILL.md
    onboard/
      SKILL.md
      references/
        quality-guide.md
        claude-md-format.md
        spec-standards.md
        spec-template.md
        spec-section-guidance.md
  agents/
    devils-advocate.md
    plan-verifier.md
    human-plan-synthesizer.md
    tdd-test-writer.md
    tdd-code-implementor.md
    tdd-code-refactor.md
    generic-code-reviewer.md
    security-reviewer.md
    reliability-reviewer.md
    maintainability-reviewer.md
    performance-reviewer.md
```

---

## Design Principles

**Onboard first, question less.** `/cks:onboard` front-loads context gathering. Every downstream skill benefits: `/cks:feature` asks fewer questions when `CLAUDE.md` and `spec.md` already exist.

**Gap-driven questioning.** Skills analyze what context already exists and only ask about what is missing.

**Artifacts are explicit contracts.** Every skill specifies what it produces and why. `/cks:execute` knows exactly what to consume.

**TDD by default.** RED (failing test) then GREEN (implement) then REFACTOR. Tests and implementation live in the same task.

**Context isolation between TDD phases — best-effort, not enforced.** The test-writer agent receives `testContext` (interfaces, types, contracts) but not `implementationContext` (implementation details). This is enforced by prompt instructions and by splitting context into separate fields in the task JSON. However, the test-writer agent has Read/Glob/Grep tools and *could* read implementation files or plan.md if it chose to — there is no filesystem-level enforcement available in the current agent framework. The isolation is designed to remove the *incentive* for the test-writer to look at implementation details, not to make it *impossible*. In practice this produces meaningfully better tests than a single-agent approach, but it is not a guarantee.

**Two-tier review.** `/cks:light-review` after each task (fast, focused). `/cks:deep-review` after all tasks per repo (thorough, cross-cutting). Both are automatic during `/cks:execute`.

**One branch, one PR per repo.** All tasks for a repo commit to a single branch. Deep review covers the full change set.

**Multi-repo support.** `/cks:execute` groups tasks by repository. Cross-repo dependencies use contract stubs for decoupled execution. Works best with monorepos or co-located repos.

**Bugs use the same execution path.** `/cks:bug` creates the plan. `/cks:execute` implements it. Identical TDD cycle, identical review gates.

**Skip the skills when you don't need them.** One- or two-line changes do not need a plan file. Use vanilla Claude Code with plan mode.
