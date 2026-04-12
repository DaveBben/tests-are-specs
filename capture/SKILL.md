---
name: capture
description: >
  Use when the user asks to document what a project currently does, create a spec.md,
  capture current project state, or create a living specification for a codebase. Creates
  a spec.md that represents the actual current state of the repository — what IS implemented,
  not what will be. This is a living document Claude should keep current as code changes.
  Do NOT use for per-change feature or bug specs (use solution instead). Do NOT use for
  CLAUDE.md files (use onboard-claude instead).
disable-model-invocation: true
argument-hint: "[output-path]"
effort: high
skills:
  - spec-standards
---

# Capture — Project State Specification

Create a spec.md that captures the current, actual state of a repository. The spec.md is
a **living document** — not a design doc, not a roadmap, not an aspirational vision. It
answers: "What is this project actually doing right now, and what does someone need to know
to work in this codebase effectively?"

**Keep it up to date.** When you make changes to this codebase, check spec.md and update
any sections that no longer accurately reflect what the code does. The Current State section
in particular must stay current — it is the fastest way to orient any reader, human or AI.

## Important Distinction

spec.md is NOT a CLAUDE.md file. CLAUDE.md covers tech stack, directory structure, and
development commands. spec.md goes deeper: current implementation state, architecture,
testing strategy, deployment, ownership, known issues, and constraints that CLAUDE.md
does not capture.

spec.md describes **current** state. Change plans (task-decomposition) describe **future**
state. If you find yourself writing about what the project will do, stop — redirect that
content to a change spec.

## Workflow

### Phase 1: Discovery

Before writing anything, gather context. For existing projects, explore the codebase first:

1. Read CLAUDE.md, README.md, package.json / pyproject.toml / Cargo.toml (or equivalent). Check for existing spec files (`spec.md`, `SPEC.md`, `PROJECT-SPEC.md`) at the root of the project or inside the docs folder.
2. Examine directory structure to understand project organization
3. Look at test configuration to identify testing framework and conventions
4. Check git history for recent activity — what has actually shipped? (`git log --oneline -20`; skip for new repos)
5. Look at CI/CD config (`.github/workflows/`, `Jenkinsfile`, etc.) to understand deployment
6. Identify key architectural patterns from the code itself
7. **Distinguish implemented vs. aspirational.** Pay close attention to what is actually working vs. what is stubbed, in-progress, or TODO'd. The Current State section depends on this distinction. Look for `TODO`, `FIXME`, `NotImplementedError`, stub files, and placeholder comments.
8. For pipelines or multi-stage systems, trace the data that flows between stages and document handoff contracts and resource ownership (locks, cleanup, state transitions)
9. Surface non-obvious architectural decisions (unusual library choices, custom abstractions, deliberate omissions of common tools) and ask the user why they were made

For new projects, interview the user. Do not ask all questions at once — start with the most
important and follow up as needed. Ask only one question at a time.

**Essential questions (ask first):**
- What is currently implemented and working in this project?
- What does this project do and who uses it?
- Why does this project exist? What problem does it solve?

**Follow-up questions (ask based on gaps):**
- What external services or APIs does this integrate with?
- How should the system behave when external dependencies fail? What are your timeout/retry/rate-limit policies?
- What capability constraints do your external APIs have? (context windows, output format limits, per-call latency, non-recursive operations, instructions-at-init vs per-call)
- What testing framework and conventions are used? What areas have good coverage vs. gaps?
- How does the app get from code to production? What does the CI/CD pipeline look like?
- Who owns this repo? Who should be contacted if something breaks?
- What is currently broken or known to be degraded?
- What technical debt has been intentionally deferred?
- What should an AI coder never touch or change?
- Are there non-obvious gotchas or runtime traps in this codebase?
- What significant architectural decisions have been made, and why?

### Phase 2: Check for Existing spec.md

If Phase 1 found an existing `spec.md` (or similar spec file like `SPEC.md`, `PROJECT-SPEC.md`):

1. Read the existing file
2. Ask the user: "A project spec already exists. Would you like to **(a)** update it to match the current template format while preserving your content, or **(b)** start fresh?"
3. If the user chooses (a), preserve existing content and map it into the new template format in Phase 3. Existing content wins for human-judgment sections (motivation, ownership, boundaries, architecture decisions); discovery data wins for factual sections (current state, testing strategy, deployment).
4. If the user chooses (b), proceed as if no file exists

If no existing spec was found, skip directly to Phase 3.

### Phase 3: Draft the Spec

The preloaded `spec-standards` skill contains the template, section guidance, key principles,
and anti-patterns. Use it as the authoritative source for all drafting decisions. Read the
template and section guidance files linked in `spec-standards`' table of contents.

**Write Current State first, before any other section.** Get it right before proceeding —
it anchors every other section and is the most important thing the spec communicates. It
must describe only what is actually implemented and working today. No future tense.

### Phase 4: Audit Review Loop

Before presenting to the user, run an internal review loop to catch structural issues:

1. Write the draft to the output path (or a temporary file)
2. Launch an `audit-reviewer` agent, passing the file path. The reviewer will check the draft as a spec.md against `spec-standards` — required sections, content quality, and anti-patterns
3. Fix any BLOCKING or SHOULD_FIX issues the reviewer identifies
4. If fixes were significant, re-run the audit reviewer on the updated draft
5. **Maximum 2 audit iterations** — after 2 passes, proceed to Phase 5 with any remaining findings noted for the user

### Phase 5: Review with User

Present the draft to the user. Ask specifically:
- "Does the Current State section accurately describe what is implemented and working today, with nothing aspirational or future-tense?"
- "Does this accurately describe the project?"
- "Is anything missing that would cause an AI to make wrong assumptions?"
- "Are the failure behaviors and constraints for external dependencies accurate?"
- "Is anything included that's obvious from reading the code?" (remove it if so)

Iterate until the user approves.

### Phase 6: Write the File

If the user provided an output path argument, save the spec there. If the argument is a directory
path, write `spec.md` inside that directory. Otherwise, default to `spec.md` at the project root.

User-provided output path: `$ARGUMENTS`

If the project already has a CLAUDE.md, suggest adding a pointer to its Pointers to Deeper Docs section:
```markdown
- `spec.md` — current project state, architecture overview, and working constraints
```

---

## Living Document Maintenance

This spec should be updated whenever:
- A feature ships or is removed
- The architecture changes significantly
- A new external dependency is added or removed
- The deployment infrastructure changes
- A known issue is resolved or a new one is discovered
- Ownership changes

**The Current State section is the most time-sensitive.** After any significant implementation
session, read it and correct anything that no longer matches the code.

At the start of a session in a repo with spec.md, read it and note any sections that appear
stale. If Current State is more than a few weeks old and significant work has been done,
offer to update it before proceeding with new work.

---

## What NOT to Include

See `spec-standards > Anti-Patterns` for the full list. Key exclusions:

- Future plans, roadmap items, or features that are not yet implemented — those belong in change specs or a backlog
- Standard language conventions the AI already knows
- Code style rules enforced by a linter (never send an LLM to do a linter's job)
- Information that changes frequently (use references to external docs instead)
- Content that belongs in CLAUDE.md (tech stack, directory structure, dev commands)

## Gotchas

- **Don't skip Phase 1 discovery for existing projects.** Even when the user describes the project verbally, explore the codebase first — the code is the source of truth and often contradicts assumptions.
- **Don't describe what will be built.** If the user starts narrating a planned feature during discovery, document what already exists and redirect future work to `/task-decomposition` for that work. Keep spec.md at the current-state level.
- **Specs balloon quickly.** If a section restates what the code already shows, cut it.
- **Don't confuse project spec with change spec.** If the user starts describing a specific feature or bug fix mid-interview, redirect them to `/task-decomposition` for that work and keep the project spec at the overview level.
- **Keep CLAUDE.md pointers in sync.** When updating the spec.md location or filename, verify that any CLAUDE.md pointer still points to the correct path.

## Relationship to Other Artifacts

```
spec.md (this skill)           -- What does this project do right now? How is it structured? What are the rules?
   |
   v
/task-decomposition → plan.md  -- What change, why, and how? (story → tasks)
   |
   v
/execute                       -- TDD implementation: RED test → GREEN code
```

The project spec feeds into change plans, which feed into task breakdowns. Use `/task-decomposition`
to create change plans that reference this project spec.

## Additional Resources

### Standards Reference
- **`spec-standards`** — Preloaded skill with template, section guidance, key principles, and anti-patterns
