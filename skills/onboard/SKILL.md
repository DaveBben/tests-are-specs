---
name: onboard
description: >
  Use when onboarding a new or existing repository. Creates both CLAUDE.md (quick-reference
  context for Claude) and spec.md (living project specification). Do NOT use for reviewing
  existing files without changes, or for creating .claude/rules/ files.
disable-model-invocation: true
argument-hint: "[output-path]"
effort: high
---

# Onboard — Repository Setup

Creates both CLAUDE.md and spec.md in a single workflow. CLAUDE.md is quick-reference context
(tech stack, commands, constraints). spec.md is a living specification (current state,
architecture, boundaries, ownership). Together they give Claude everything it needs to work
effectively in a repository.

## What Goes Where

| spec.md | CLAUDE.md |
|---------|-----------|
| Why the project exists | Tech stack and versions |
| Current state — what's actually implemented | Directory structure |
| Architecture overview and external dependencies | Development commands |
| Deployment & infrastructure | Build/test/lint commands |
| Testing strategy (what exists and what's missing) | Package manager |
| Boundaries & constraints | Environment setup |
| Ownership, known issues, tech debt | Critical constraints |

Do not duplicate content between the two files.

---

## Workflow

### Phase 1: Unified Discovery

One exploration pass gathers everything needed for both documents. Focus on the project root
and first-level subdirectories. Do not recurse deeply into source directories. **Stop
exploring once you have concrete answers for each category below** — do not continue
reading files for additional supporting evidence. Over-retrieval wastes context and
delays the user.

**Gather for CLAUDE.md:**
- Primary language(s), frameworks, and their versions
- Package manager and build system
- Linter/formatter configs (`.eslintrc*`, `ruff.toml`, `pyproject.toml [tool.ruff]`, etc.)
- Top-level directory structure with one-line purposes
- Build/test/lint/format/run commands

**Gather for spec.md:**
- Test configuration — framework, conventions, coverage gaps
- CI/CD config (`.github/workflows/`, `Jenkinsfile`, etc.)
- Git history — what has actually shipped? (`git log --oneline -20`; skip for new repos)
- Key architectural patterns from the code itself
- External dependencies and their integration points
- **Implemented vs. aspirational** — look for `TODO`, `FIXME`, `NotImplementedError`, stub files, placeholder comments
- For pipelines or multi-stage systems: trace data flows between stages, document handoff contracts

**Gather for both:**
- Existing files: `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, `spec.md`, `SPEC.md`, `docs/architecture.md`, `README.md`, `CONTRIBUTING.md`

**For new or empty projects**, interview the user. Ask one question at a time, starting with essentials:
1. What is currently implemented and working in this project?
2. What does this project do and who uses it?
3. Why does this project exist? What problem does it solve?

Follow up based on gaps — external services, failure behavior, testing, CI/CD, ownership, known issues, tech debt, things an AI should never touch, non-obvious gotchas.

**For mature/brownfield codebases** (>50k lines or >2 years of git history),
add a domain risks interview after initial discovery. Generate **3-5 targeted
questions based on what you actually found** during exploration — not generic
examples. Each question should reference a specific discovery:

Examples of targeted questions (adapt to what you found):
- "I found 3 different auth patterns (`src/auth/jwt.ts`, `src/middleware/session.ts`,
  `src/legacy/basic-auth.ts`) — is one canonical, or do different areas use different
  approaches?"
- "The database has both soft-delete (`deleted_at` columns) and hard-delete tables —
  which is the convention for new tables?"
- "I see `src/lib/internal-http` wrapping all outbound HTTP — must all new integrations
  use this, or can they use fetch directly?"

Present all questions at once. Capture answers in a `## Domain Gotchas` section
in spec.md. These are the highest-value items in the spec — institutional
knowledge that prevents the most expensive AI mistakes.

### Phase 2: Check for Existing Files

If the exploration found existing files, ask about each in a single interaction:

- **CLAUDE.md found**: "A CLAUDE.md already exists. Would you like to **(a)** update it to match best-practice format while preserving your content, or **(b)** start fresh?"
- **spec.md found** (also check `SPEC.md`, `PROJECT-SPEC.md`): Before asking the
  user, compare the Current State section against what discovery found. If they
  diverge, show the specific drift:
  > "spec.md exists but its Current State appears stale:
  > - Spec says: '[quote from Current State]'
  > - Code shows: '[what discovery found]'
  >
  > Would you like to **(a)** update it (I'll fix the drift and match best-practice
  > format), or **(b)** start fresh?"

  If no drift detected, ask without the warning.

Then ask: **"This workflow creates both CLAUDE.md and spec.md. If you only need CLAUDE.md, say so now — otherwise we'll proceed with both."**

If the user opts out of spec.md, skip Phases 4, 5, and the spec.md portions of Phases 6-7.

**Merge rules when updating existing files:**
- Existing content wins for human-judgment sections (Project Identity, Critical Constraints, motivation, ownership, boundaries, architecture decisions)
- Discovery data wins for factual sections (versions, commands, current state, testing strategy, deployment)
- Merge and deduplicate where both sources have content

### Phase 3: Draft CLAUDE.md

Read [references/quality-guide.md](references/quality-guide.md) for principles. Use
[references/claude-md-format.md](references/claude-md-format.md) for the exact section structure.

Using discovery data, draft each section per the format reference:

- **Fill from exploration data**: Tech Stack and Codebase Map, Operational Commands, Pointers to Deeper Docs. If a command category was not found, include a placeholder comment like `<!-- add test command -->`.
- **Leave blank with HTML comment placeholder**: Project Identity and Critical Constraints — these require human judgment and cannot be reliably inferred.
- **Always include** a pointer to spec.md in Pointers to Deeper Docs (it will be created in Phase 4): `` `spec.md` — current project state, architecture overview, and working constraints ``

### Phase 4: Draft spec.md

Read [references/spec-standards.md](references/spec-standards.md) for principles and anti-patterns.
Use [references/spec-template.md](references/spec-template.md) for the section structure. Consult
[references/spec-section-guidance.md](references/spec-section-guidance.md) for what makes each section good.

**Write Current State first, before any other section.** Get it right before proceeding —
it anchors every other section and is the most important thing the spec communicates. It
must describe only what is actually implemented and working today. No future tense.

Do not include tech stack, directory structure, or dev commands — those belong in CLAUDE.md.

### Phase 5: Self-Review

Before presenting to the user, review the spec.md draft against these checks
from [references/spec-standards.md](references/spec-standards.md):

**Required sections present:**
- [ ] Current State (most critical — must describe what is implemented today)
- [ ] Architecture Overview
- [ ] External Dependencies
- [ ] Testing Strategy
- [ ] Boundaries & Constraints

**Content quality:**
- [ ] Current State uses past/present tense only — no "will", "planned", "upcoming"
- [ ] No tech stack, directory structure, or dev commands (those belong in CLAUDE.md)
- [ ] No content that restates what the code already shows
- [ ] External dependency failure behaviors are documented, not just their names

**Anti-patterns to remove:**
- [ ] Future roadmap items or planned features
- [ ] Standard language conventions the AI already knows
- [ ] Code style rules enforced by a linter

Fix any issues found. If fixes were significant, run through the checklist
once more. **Maximum 2 passes** — after 2 passes, note remaining findings
for the user rather than looping further.

### Phase 6: Review with User

Present both drafts together. Ask:

**For CLAUDE.md:**
- Note which sections have placeholders the user should fill in (Project Identity, Critical Constraints, or any others left blank)

**For spec.md:**
- "Does the Current State section accurately describe what is implemented and working today, with nothing aspirational or future-tense?"
- "Does this accurately describe the project?"
- "Is anything missing that would cause an AI to make wrong assumptions?"
- "Are the failure behaviors and constraints for external dependencies accurate?"
- "Is anything included that's obvious from reading the code?" (remove it if so)

Iterate until the user approves.

### Phase 7: Write Files

1. If `$ARGUMENTS` provides an output path, use it. If it's a directory, write both files inside it. Otherwise default to the project root.
2. Write CLAUDE.md and spec.md
3. Verify the CLAUDE.md Pointers to Deeper Docs section includes the spec.md pointer
4. Tell the user which sections have placeholders they should fill in

### Phase 8: Domain-Scoped Context (large projects only)

If the project has **5 or more distinct subsystem directories** (e.g., `src/auth/`,
`src/billing/`, `src/api/`, `src/workers/`, `src/notifications/`), suggest
creating subdirectory CLAUDE.md files:

> "This project has {N} distinct subsystems. A single root CLAUDE.md will
> grow past the 200-line cap as conventions accumulate. Consider adding
> scoped context files for the largest subsystems:
>
> - `src/auth/CLAUDE.md` — auth-specific conventions, session handling quirks
> - `src/billing/CLAUDE.md` — billing domain rules, Stripe integration patterns
>
> These load automatically when Claude reads files in those directories.
> Each should contain only conventions specific to that subsystem — shared
> rules stay in the root CLAUDE.md."

Only suggest this for subsystems that surfaced domain-specific conventions
during discovery. Do not create empty subdirectory files.

---

## Gotchas

- **Don't guess commands** — If you can't find evidence of a command in config files, scripts, or docs, use a placeholder comment (`<!-- add test command -->`) instead of inventing one. Getting the package manager wrong (`npm` vs `pnpm` vs `yarn`) is a common failure.
- **Leave human-judgment sections as placeholders** — Project Identity and Critical Constraints require human input. Do not fill these with generic advice.
- **Keep CLAUDE.md under 200 lines** — A CLAUDE.md that's too long defeats its purpose as quick-reference context.
- **Don't skip discovery for existing projects** — Even when the user describes the project verbally, explore the codebase first — the code is the source of truth.
- **Don't describe what will be built** — spec.md captures current state only. Redirect future plans to `/cks:feature`.
- **Specs balloon quickly** — If a section restates what the code already shows, cut it.
- **Don't confuse project spec with change spec** — If the user starts describing a specific feature or bug fix mid-interview, redirect them to `/cks:feature` for that work.
- **Keep cross-references in sync** — When writing or moving files, verify CLAUDE.md's pointer to spec.md is correct.
- **This skill targets the root CLAUDE.md** — For subdirectory CLAUDE.md files in a monorepo, scope content to that package's domain.

---

## Living Document Maintenance

Both documents should be kept current as the project evolves.

**spec.md** should be updated whenever:
- A feature ships or is removed
- The architecture changes significantly
- A new external dependency is added or removed
- The deployment infrastructure changes
- A known issue is resolved or a new one is discovered
- Ownership changes

**The Current State section is the most time-sensitive.** After any significant implementation
session, read it and correct anything that no longer matches the code.

**CLAUDE.md** should be updated whenever:
- Tooling changes (new package manager, different test runner, etc.)
- Directory structure changes significantly
- New critical constraints are discovered

### Drift Detection

After writing both files, suggest a lightweight drift detection approach:

> "To catch spec drift, consider adding a CI step or post-merge hook that
> checks whether files touched in a PR overlap with architecture sections
> in spec.md. For example, a simple script that greps changed file paths
> against the Files Affected patterns in spec.md and adds a PR comment:
> 'This PR touches areas documented in spec.md — please verify the docs
> are still accurate.'
>
> `/cks:execute` also checks spec.md freshness during pre-flight and will
> remind you if it hasn't been updated recently."

This is a suggestion, not an automated installation — the user decides
whether to implement it.

### Automatic Spec Updates via Claude Code Rules

After writing both files, also suggest adding a rule file:

> "To keep spec.md current automatically, you can add a Claude Code rule
> at `.claude/rules/spec-update.md` with:
>
> ```
> After completing a feature implementation that changes the project's
> capabilities, check spec.md and update the Current State section if
> it no longer matches reality.
> ```
>
> This activates in every Claude session (not just /cks:execute), catching
> drift from manual changes too. `/cks:execute` also updates spec.md
> automatically after completing all tasks."

---

