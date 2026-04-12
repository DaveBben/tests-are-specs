# Claude KISS — Keep it Simple Stupid

A focused set of Claude Code skills that turn ideas and bugs into implemented, reviewed code. No multi-stage planning pipelines. Direct entry points only.

## Routing

```
Is this a new codebase or one you haven't onboarded yet?
  └── Yes → /onboard  (creates CLAUDE.md + spec.md, then come back here)

Is the change one or two lines?
  └── Yes → Use vanilla Claude Code with plan mode. No skills needed.

Is it a bug?
  └── Yes → /bug → then /execute

Is it a new feature or capability?
  └── Yes → /feature → then /execute
```

### Depth Modes

Not every change needs the full pipeline. Pick the depth that matches your situation:

| Mode | When to use | What to do |
|------|------------|------------|
| **Quick fix** | You know exactly what to change, < ~50 lines | Skip /feature entirely. Write a task JSON manually and run `/execute`, or just use vanilla Claude Code. |
| **Experienced** | You know the codebase well, the feature is straightforward | Run `/feature` — when gates present output, confirm quickly or say "continue" to keep moving. The workflow won't block you unless something looks structurally wrong. |
| **Full pipeline** | New to the codebase, complex feature, high-risk area, or compliance-sensitive work | Run `/feature` — engage with every gate, review the devil's advocate challenges carefully, annotate the plan thoroughly. This is the maximum-guidance path. |

---

## Skills

| Skill | What it does | Artifacts produced |
|---|---|---|
| `/onboard` | Sets up context for a new or existing codebase | `CLAUDE.md`, `spec.md` |
| `/feature` | Investigates scope, produces a plan and TDD task files | `.claude/features/{slug}/plan.md`, `.claude/features/{slug}/tasks/task_N.md` |
| `/bug` | Captures symptom, root cause, and fix tasks | `.claude/bugs/{slug}/plan.md`, `.claude/bugs/{slug}/tasks/task_N.md` |
| `/execute` | Implements tasks: TDD cycle + two-tier review + PR | Branch, commits, PR |
| `/light-review` | Single-agent code review across all dimensions | Review report |
| `/deep-review` | Four-agent parallel review (security, reliability, maintainability, performance) | Consolidated review report |

---

## Skill Details

### `/onboard`

Run this first on any codebase — new or existing. The skill reads the repository, asks targeted questions about purpose, tech stack, conventions, and constraints, then produces:

- **`CLAUDE.md`** — quick-reference context that Claude Code loads on every conversation
- **`spec.md`** — living specification describing what the system does, key decisions, and known constraints

Once onboarded, `/feature` and `/bug` plans have rich context to work from, reducing the questions they need to ask.

### `/feature`

Investigative conversation that clarifies scope, constraints, and acceptance criteria. The skill reads any existing `CLAUDE.md` and `spec.md` for context, explores the codebase, then produces:

- **`plan.md`** — what is being built, why, constraints, and scope boundaries
- **`task_N.md` files** — one per task, each with: relevant files (strict boundary for the executor), acceptance criteria (GIVEN/WHEN/THEN), verification description, and explicit anti-scope (Do NOT list)

A `devils-advocate` agent challenges the plan before it is finalized.

Multi-repo: when a feature spans multiple repositories, `/feature` records all repository paths and tags each task with its target repository via the `repository` field in task JSON.

### `/bug`

Guides the user through: symptom description, environment, reproduction steps, expected vs actual behavior, severity, and root cause investigation. Produces:

- **`plan.md`** — bug context, root cause, severity
- **`task_N.md` files** — fix tasks with the same TDD structure as feature tasks

Execute with `/execute`.

### `/execute`

Takes a feature or bug plan directory and processes all tasks:

1. Create branch (`feature/{slug}` or `bugfix/{slug}`)
2. For each task: 3-agent TDD cycle (`tdd-test-writer` → `tdd-code-implementor` → `tdd-code-refactor`)
3. `/light-review` after each task — fast review, findings fixed before moving on
4. `/deep-review` after all tasks — thorough cross-cutting review, findings fixed
5. Push branch + create PR using `gh`

Multi-repo: tasks are tagged with their target repository via the `repository` field. Each repo is processed sequentially: `cd` to repo → branch → tasks → light review per task → deep review → PR.

### `/light-review`

Single-agent review covering correctness, readability, security surface, and maintainability in one pass. Used automatically by `/execute` after each task. Can also be invoked standalone.

### `/deep-review`

Four agents run in parallel, each focused on one dimension:

| Agent | Focus |
|---|---|
| `security-reviewer` | Injection, access control, data exposure |
| `reliability-reviewer` | Correctness, race conditions, resource lifecycle |
| `maintainability-reviewer` | Readability, compatibility, conventions |
| `performance-reviewer` | N+1 queries, blocking I/O, resource leaks |

Results are consolidated into a single report. Used automatically by `/execute` after all tasks for a repo complete.

---

## Agents

| Agent | Role | Used by |
|---|---|---|
| `devils-advocate` | Challenges feature plan scope, criteria, and assumptions | `/feature` |
| `tdd-test-writer` | RED phase — writes failing tests from acceptance criteria | `/execute` |
| `tdd-code-implementor` | GREEN phase — minimum code to make tests pass | `/execute` |
| `tdd-code-refactor` | REFACTOR phase — improves code while keeping tests green | `/execute` |
| `generic-code-reviewer` | All-dimensions fast review | `/light-review` |
| `security-reviewer` | Injection, access control, data exposure | `/deep-review` |
| `reliability-reviewer` | Correctness, race conditions, resource lifecycle | `/deep-review` |
| `maintainability-reviewer` | Readability, compatibility, conventions | `/deep-review` |
| `performance-reviewer` | N+1 queries, blocking I/O, resource leaks | `/deep-review` |

---

## Artifact Storage

Plans and tasks are stored per-project inside `.claude/`:

```
{project-root}/
  .claude/
    features/
      {slug}/
        plan.md
        tasks/
          task_0.md
          task_1.md
    bugs/
      {slug}/
        plan.md
        tasks/
          task_0.md
```

`plan.md` contains metadata, context, and constraints for the feature or bug. `task_N.md` files contain individual TDD tasks: relevant files, acceptance criteria, verification, and anti-scope.

---

## File Structure

```
claude-kiss/
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

**Onboard first, question less.** `/onboard` front-loads context gathering. Every downstream skill benefits: `/feature` asks fewer questions when `CLAUDE.md` and `spec.md` already exist.

**Gap-driven questioning.** Skills analyze what context already exists and only ask about what is missing.

**Artifacts are explicit contracts.** Every skill specifies what it produces and why. `/execute` knows exactly what to consume.

**TDD by default.** RED (failing test) then GREEN (implement) then REFACTOR. Tests and implementation live in the same task.

**Context isolation between TDD phases — best-effort, not enforced.** The test-writer agent receives `testContext` (interfaces, types, contracts) but not `implementationContext` (implementation details). This is enforced by prompt instructions and by splitting context into separate fields in the task JSON. However, the test-writer agent has Read/Glob/Grep tools and *could* read implementation files or plan.md if it chose to — there is no filesystem-level enforcement available in the current agent framework. The isolation is designed to remove the *incentive* for the test-writer to look at implementation details, not to make it *impossible*. In practice this produces meaningfully better tests than a single-agent approach, but it is not a guarantee.

**Two-tier review.** `/light-review` after each task (fast, focused). `/deep-review` after all tasks per repo (thorough, cross-cutting). Both are automatic during `/execute`.

**One branch, one PR per repo.** All tasks for a repo commit to a single branch. Deep review covers the full change set.

**Multi-repo in one invocation.** `/execute` groups tasks by repository and processes each sequentially: branch → tasks → reviews → PR.

**Bugs use the same execution path.** `/bug` creates the plan. `/execute` implements it. Identical TDD cycle, identical review gates.

**Skip the skills when you don't need them.** One- or two-line changes do not need a plan file. Use vanilla Claude Code with plan mode.
