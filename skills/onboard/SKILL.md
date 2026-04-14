---
name: onboard
description: >
  Use when onboarding a new or existing repository. Creates CLAUDE.md (quick-reference
  context), spec.md (living project specification), and .claude/rules/ files (spec
  maintenance and domain-scoped context loading). For multi-domain projects, also creates
  domain-scoped spec.md files. Do NOT use for reviewing existing files without changes.
disable-model-invocation: true
argument-hint: "[output-path]"
model: opus
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

**Identify domains:**
- From the top-level directory structure, identify **distinct subsystems or
  deployment units** — areas with their own conventions, dependencies, or
  interfaces. Examples: `backend/`, `frontend/`, `workers/`, `infra/`,
  or `src/auth/`, `src/billing/` in a monolith.
- A simple app may have 0-1 domains (just the root spec.md is sufficient).
  A multi-service system may have 2-5. Record each with its root directory
  and a one-line description.
- Let the user confirm, add, or remove domains before proceeding. They may
  identify domains the directory structure doesn't make obvious (e.g., a
  shared library that serves as an internal API boundary).

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

**If Phase 1 identified 2+ domains:** Write a slim, system-level root spec (target
60-100 lines). Domain-specific content (external deps, testing gaps, known issues,
tech debt, domain boundaries) goes in domain specs created in Phase 8. Don't put
domain-specific content in the root — it will be loaded unnecessarily when the agent
works in an unrelated domain.

**If single-domain project:** Include everything in the root spec (target 100-200 lines).
Skip Phase 8.

Do not include tech stack, directory structure, or dev commands — those belong in CLAUDE.md.

### Phase 5: Self-Review

Before presenting to the user, review the spec.md draft against these checks
from [references/spec-standards.md](references/spec-standards.md):

**Required sections present:**
- [ ] Current State (most critical — must describe what is implemented today)
- [ ] Architecture Overview
- [ ] External Dependencies (shared only, if multi-domain)
- [ ] Testing Strategy (infrastructure only, if multi-domain)
- [ ] Boundaries & Constraints (project-wide only, if multi-domain)
- [ ] Domain Specs pointer table (if multi-domain)

**Content quality:**
- [ ] Current State uses past/present tense only — no "will", "planned", "upcoming"
- [ ] No tech stack, directory structure, or dev commands (those belong in CLAUDE.md)
- [ ] No content that restates what the code already shows
- [ ] External dependency failure behaviors are documented, not just their names

**Split check (multi-domain only):**
- [ ] No domain-specific external deps in root (they go in domain specs)
- [ ] No domain-specific known issues or tech debt in root
- [ ] No domain-specific boundaries in root
- [ ] Root spec under 100 lines

**Anti-patterns to remove:**
- [ ] Future roadmap items or planned features
- [ ] Standard language conventions the AI already knows
- [ ] Code style rules enforced by a linter

Fix any issues found. If fixes were significant, run through the checklist
once more. **Maximum 2 passes** — after 2 passes, note remaining findings
for the user rather than looping further.

### Phase 6: Write Files

1. If `$ARGUMENTS` provides an output path, use it. If it's a directory, write both files inside it. Otherwise default to the project root.
2. Write CLAUDE.md and spec.md to disk.
3. Verify the CLAUDE.md Pointers to Deeper Docs section includes the spec.md pointer.

### Phase 7: Review with User

Tell the user the files have been written and ask them to open and review them. Say something like:

> "I've written CLAUDE.md and spec.md — please open them and review. Let me know what you'd like to change."

**Prompt them to check:**

**For CLAUDE.md:**
- Which sections have placeholders they should fill in (Project Identity, Critical Constraints, or any others left blank)

**For spec.md:**
- Does the Current State section accurately describe what is implemented and working today, with nothing aspirational or future-tense?
- Does this accurately describe the project?
- Is anything missing that would cause an AI to make wrong assumptions?
- Are the failure behaviors and constraints for external dependencies accurate?
- Is anything included that's obvious from reading the code? (remove it if so)

Iterate — applying their feedback as edits to the files — until the user approves. Once approved, update the **Status** field in spec.md (and any domain specs) from `Draft` to `Active`, and update the **Last verified** date to today.

### Phase 8: Domain-Scoped Specs

If Phase 1 identified **2 or more domains**, create a domain spec for each.

#### Step 1: Draft Domain Specs

For each domain, write `{domain-dir}/spec.md` using the
[domain-spec-template.md](references/domain-spec-template.md). Each domain
spec is **under 100 lines** and contains:

- What this domain owns and does NOT own
- Current state of this domain specifically
- Domain-specific conventions
- Interface contracts (internal + exposed + domain-specific external deps)
- Testing — coverage gaps and domain-specific test conventions
- Domain boundaries — domain-specific Always/Ask First/Never rules
- Known issues in this domain
- Gotchas and anti-patterns

Content that was gathered during Phase 1 discovery but excluded from the
root spec (domain-specific deps, testing gaps, known issues, tech debt,
domain boundaries) goes here. This is the primary home for that content
— don't leave it orphaned.

**Do not duplicate the root spec.md.** Shared conventions, project-wide
boundaries, and deployment info stay at root. Omit empty sections rather
than including placeholders.

These are **drafts** — present them to the user for review just like the
root spec.md. LLM-generated context files that aren't human-reviewed
reduce resolution rates (ETH Zurich, 2602.11988).

#### Step 2: Create Loading Rules

For each domain spec, create a path-scoped rule in `.claude/rules/`
that loads the spec when Claude works in that directory. Rules use
YAML frontmatter with a `paths` field for scoping:

```markdown
# .claude/rules/{domain-name}-context.md
---
paths:
  - "{domain-dir}/**/*"
---

Read {domain-dir}/spec.md for domain-specific conventions, interface
contracts, and boundaries before making changes in this area.
```

#### Step 2b: Verify Rules Load

After creating rule files, verify each one by checking that the glob
pattern matches actual files in the domain directory:

```
ls {domain-dir}/**/* | head -3
```

If the glob returns no files, the pattern is wrong and the rule will
never trigger. Fix the pattern before proceeding. Common mistakes:
missing `**` for recursive matching, wrong directory prefix.

#### Step 3: Update Root Pointers

Add a `## Domain Specs` section to the root spec.md listing each
domain spec with its path and one-line description. Add a pointer in
CLAUDE.md's "Pointers to Deeper Docs" section.

#### When NOT to Create Domain Specs

- Project has only 1 domain or is a simple app — root spec.md is sufficient
- A subsystem has no domain-specific conventions — don't create an empty spec
- The domain's conventions are already in the root spec — move them to the
  domain spec instead of duplicating

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

## Spec Maintenance Rule

After writing all files, create `.claude/rules/spec-maintenance.md`
(no `paths` frontmatter — this loads unconditionally every session):

```markdown
# Spec Maintenance

After implementing a feature, update `spec.md` Current State if it no longer reflects reality. For changes scoped to a subdirectory with its own `spec.md`, update that domain spec too. Always update the Last verified date on any spec you touch.
```

Also add to CLAUDE.md's Critical Constraints section:

```
- After significant implementation changes, update spec.md Current State
  (and domain spec.md if the change is domain-scoped). Stale specs are
  worse than no specs.
```

Then suggest drift detection to the user:

> "To catch spec drift in CI, consider a post-merge hook that checks
> whether files touched in a PR overlap with paths documented in spec.md
> and flags them for review."

---