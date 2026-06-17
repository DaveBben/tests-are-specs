---
name: onboard
description: "Use when onboarding a new or existing repository — setting up, initializing, or documenting a repo for the first time. Creates CLAUDE.md (quick-reference context), spec.md (living project specification), and .claude/rules/ files (spec maintenance and domain-scoped context loading). For multi-domain projects, also creates technical domain-scoped spec.md files."
disable-model-invocation: true
argument-hint: "[output-path]"
model: opus
effort: high
---

# Onboard — Repository Setup

## What Goes Where

| spec.md | CLAUDE.md |
|---------|-----------|
| Current state — what's actually implemented (goes first) | Tech stack and versions |
| What's NOT yet implemented — stubs and placeholders | Directory structure |
| Architecture overview and external dependencies | Development commands |
| Deployment & infrastructure | Build/test/lint commands |
| Testing strategy (what exists and what's missing) | Package manager |
| Boundaries & constraints | Environment setup |
| Gotchas — institutional knowledge not in the code | Critical constraints |
| System context (if part of a larger platform) | — |
| Ownership, known issues, tech debt | — |

---

**Write the prose to be read on one pass.** When you draft the prose in these docs — Current State, Architecture overview, Gotchas, Project Identity — follow the readable style in `references/writing-style.md` (read it when you reach Phase 3 and Phase 4). It shapes sentences only. It complements — it does not loosen — the density rules in `references/quality-guide.md` and `references/spec-standards.md` (semantic density, named lists, exact commands, "Not yet implemented" lists).

## Workflow

### Phase 1: Unified Discovery

One exploration pass gathers everything needed for both documents. Focus on the project root and first-level subdirectories. Do not recurse past the second directory level unless you need to verify a specific technical domain boundary (e.g., checking whether `src/auth/middleware/` imports from `src/billing/` to determine if they communicate through direct imports or contracts). When you go deeper, state what you're checking and return to the top level. **Stop exploring during this phase once you have concrete answers for each category below** — do not continue reading files for additional supporting evidence. Over-retrieval wastes context and delays the user. (Phase 5's decision-gap check may require targeted follow-up reads — that is a separate, scoped activity.)

**Gather for CLAUDE.md:**
- Primary language(s), frameworks, and their versions
- Package manager and build system
- Linter/formatter configs (`.eslintrc*`, `ruff.toml`, `pyproject.toml [tool.ruff]`, etc.)
- Top-level directory structure with one-line purposes
- Build/test/lint/format/run commands

**Gather for spec.md:**
- Test configuration — framework, conventions, coverage gaps
- **Test coverage summary** — identify which areas are well-tested, partially tested, and untested. An agent's ability to write verification commands depends on knowing where tests exist. Scan test directories and map test files to source files to produce a 1-2 line coverage summary.
- CI/CD config (`.github/workflows/`, `Jenkinsfile`, etc.)
- Git history — what has actually shipped? (`git log --oneline -20`; skip for new repos)
- Key architectural patterns from the code itself
- **Entry-point symbols** — for the main flow, identify the specific function or method where behavior originates (e.g., `PipelineController.processNext()`, not just `PipelineController`). Name these in Current State so agents can jump directly to the right location.
- External dependencies and their integration points
- **Implemented vs. aspirational** — look for `TODO`, `FIXME`, `NotImplementedError`, stub files, placeholder comments
- For pipelines or multi-stage systems: trace data flows between stages, document handoff contracts

**Identify technical domains:**

A **technical domain** is a subsystem with its own deployment target, hard interface boundaries, or divergent constraints — distinct enough that a single spec section covering both areas would require constant clarification of which rules apply where.

Directory structure is a starting point, not a conclusion. Subdirectories often represent architectural layers (models, controllers, routes, utils) rather than separate technical domains.

The core question is: **if you wrote one spec section covering both areas, would a reader need to constantly ask "does this constraint apply to X or Y?"** If yes, they are separate technical domains. Test candidate directories against these signals to answer that question:

**Strong signals — any one likely means a separate technical domain:**
- **Separate deployment targets** — deploys to a different service, runtime, or pipeline (e.g., Lambda vs. ECS, CDK stack vs. application code). Different deployment means independent lifecycle, independent failure modes, and different operational context.
- **Hard interface boundaries** — areas that communicate only through contracts (APIs, queues, events, shared database tables) rather than direct function calls. If you can't import across the boundary, it's a technical domain boundary.
- **Divergent constraints** — areas governed by meaningfully different rules, even if they share infrastructure. An auth subsystem with compliance requirements and a billing subsystem with financial audit constraints are separate technical domains even if they deploy together — the constraints an AI must respect when working in each are different.

**Supporting signals — strengthen the case but insufficient alone:**
- Separate entry points (own handler, main, or index — not shared)
- Distinct external dependency sets (different APIs, databases, or services)
- Independent CI jobs or test suites
- Can fail independently — one area breaking does not break the other

**Structured evaluation:** For each pair of candidate directories, answer three questions: (1) Do they share a deployment target? (2) Do they communicate through direct imports or through contracts? (3) Are they governed by the same constraints? If all three answers are shared/direct/same → one domain. If any answer is separate/contract/different → likely separate domains. This makes the evaluation systematic rather than intuitive — intuitive grouping defaults to directory structure, which is the anti-pattern.

**Consolidation check:** If two candidate directories share the same deployment target, communicate through direct imports, and are governed by the same constraints, they are one technical domain even if they live in separate directories.

**Anti-pattern — do not do this:** Labeling `src/models/`, `src/controllers/`, `src/routes/` as separate technical domains. These are architectural layers within a single technical domain — they share a deployment target, call each other directly, and have no divergent constraints.

Record each technical domain with its root directory and a one-line description. Simple apps have 0-1 technical domains; multi-service systems have 2-5.

**Confirm with the user before proceeding.** Present your technical domain assessment — list each identified technical domain with its root directory, one-line description, and which strong signal(s) justified it. If you concluded the project is single-technical-domain, state that and explain why (e.g., "all subdirectories share a deployment target, import each other directly, and have no divergent constraints"). The user may disagree with the count in either direction — they may know of boundaries the code doesn't make obvious, or they may see technical domains you identified as a single unit. **Do not proceed past Phase 1 until the user confirms the technical domain list.**

**Gather for both:**
- Existing files: `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, `spec.md`, `SPEC.md`, `docs/architecture.md`, `README.md`, `CONTRIBUTING.md`

**For new or empty projects**, interview the user. Ask these essential questions one at a time:
1. What is currently implemented and working in this project?
2. What does this project do and who uses it?
3. Why does this project exist? What problem does it solve?

Follow up based on gaps — external services, failure behavior, testing, CI/CD, ownership, known issues, tech debt, things an AI should never touch, non-obvious gotchas.

**For mature/brownfield codebases** (rough indicators: >50k lines via `find . -name '*.{ext}' | xargs wc -l`, or >2 years of git history via `git log --reverse --format=%ai | head -1`, or any project where discovery surfaced ambiguous patterns), add a technical domain risks interview after initial discovery. Generate **up to 5 targeted questions based on what you actually found** during exploration — not generic examples. Each question should reference a specific discovery. If the quality filter below eliminates candidates, generate fewer rather than padding with low-value questions.

**Quality filter for interview questions:** each question must (1) reference a specific file, pattern, or discovery, and (2) the answer must change what you write in the spec. If the answer would be "interesting to know" but wouldn't appear in any spec section, the question is wasted. Questions that resolve ambiguity between competing patterns are highest-value; questions that confirm something you're already confident about are lowest.

Examples of targeted questions (adapt to what you found):
- "I found 3 different auth patterns (`src/auth/jwt.ts`, `src/middleware/session.ts`, `src/legacy/basic-auth.ts`) — is one canonical?" → answer goes in Gotchas
- "The database has both soft-delete (`deleted_at` columns) and hard-delete tables — which is the convention for new tables?" → answer goes in Boundaries

**Stopping criterion:** stop at the first set of questions. Do not ask follow-up rounds — Phase 7 review gives the user a chance to add anything missed.

Present all mature-codebase questions at once (unlike the new-project interview above, which is one-at-a-time). Capture answers in a `## Gotchas` section in spec.md — these are the highest-value items in the spec.

### Phase 2: Check for Existing Files

If the exploration found existing files, ask about each in a single interaction:

- **CLAUDE.md found**: "A CLAUDE.md already exists. Would you like to **(a)** update it to match best-practice format while preserving your content, or **(b)** start fresh?"
- **spec.md found** (also check `SPEC.md`, `PROJECT-SPEC.md`): Before asking the user, compare the Current State section against what discovery found. If they diverge, show the specific drift: "spec.md exists but its Current State appears stale: - Spec says: '[quote from Current State]' - Code shows: '[what discovery found]' Would you like to **(a)** update it (I'll fix the drift and match best-practice format), or **(b)** start fresh?"

Then ask: **"This workflow creates both CLAUDE.md and spec.md. If you only need CLAUDE.md, say so now — otherwise we'll proceed with both."**

If the user opts out of spec.md, skip Phases 4, 5, and the spec.md portions of Phases 6-7.

**Merge rules when updating existing files:**
- **Existing content wins** for human-judgment sections (Project Identity, Critical Constraints, motivation, ownership, boundaries)
- **Discovery data wins** for factual sections (versions, commands, current state, testing strategy, deployment)
- **Blend rule** for sections that mix both (Architecture Decisions, Gotchas): keep the existing *rationale and judgment* (the "why"), but update *factual claims* (paths, versions, what exists) from discovery silently. When discovery contradicts an existing *rationale* (not just a factual claim), flag the conflict to the user rather than overwriting.

### Phase 3: Draft CLAUDE.md

Read [references/quality-guide.md](references/quality-guide.md) for principles. Use [references/claude-md-format.md](references/claude-md-format.md) for the exact section structure.

- **Fill from exploration data**: Tech Stack and Codebase Map, Operational Commands, Pointers to Deeper Docs. If a command category was not found, include a placeholder comment like `<!-- add test command -->`.
- **Leave blank with HTML comment placeholder**: Project Identity — this requires human judgment and cannot be reliably inferred.
- **Critical Constraints**: Leave blank with a placeholder comment unless spec.md is being created in this run. If spec.md is being created, pre-populate with:
  ```
  - After significant implementation changes, update docs/specs/spec.md Current State
    (and subsystem spec.md if the change is subsystem-scoped). Stale specs are
    worse than no specs.
  ```
  Add a second placeholder comment for any additional human-judgment constraints.
- **If spec.md is being created in this run**, include a pointer in Pointers to Deeper Docs: `` `docs/specs/spec.md` — project spec, architecture overview, and spec index ``. If the user opted out of spec.md in Phase 2, omit this pointer.

**CLAUDE.md self-review** before proceeding to Phase 4:
- [ ] Under 200 lines
- [ ] Every command is exact and copy-pasteable (no "run the tests" — the actual command)
- [ ] No content that belongs in spec.md (architecture, boundaries, current state, external deps)
- [ ] No linter-enforced style rules (those belong in linter config)
- [ ] Project Identity is either filled with what/why/who or left as a placeholder — not filled with technology descriptions
- [ ] Directory layout is top-level only — no deep subdirectory trees

Fix any issues found. One pass only.

### Phase 4: Draft spec.md

Draft using [spec-template.md](references/spec-template.md) for structure, [spec-standards.md](references/spec-standards.md) for principles, [spec-section-guidance.md](references/spec-section-guidance.md) for section guidance, and [writing-style.md](references/writing-style.md) for the prose style of every narrative section. Read writing-style.md now if you haven't this session.

**Include a `## Table of Contents` after the header block** (title, dates, status, blurb) listing all sections with anchor links. Omit entries for sections you didn't include (e.g., Technical Domain Specs for single-technical-domain projects).

**Write Current State first — it is section #1 in the spec.** Get it right before proceeding. It anchors every other section and is the most important thing the spec communicates. It must describe only what is actually implemented and working today. No future tense. Keep it a **navigation layer, not a knowledge dump**: a 2-4 sentence system-level summary, then a `**Components**` list with exactly one line per component (`file — entry-point symbol — one-clause role — → feature-spec`), anchoring only the entry point and delegating all per-component detail to that component's feature spec. A full paragraph per component — every symbol, setting, and edge case — is the failure mode to avoid; see the navigation-layer guidance in [spec-section-guidance.md](references/spec-section-guidance.md). Include a named **"Not yet implemented"** list for any stubs, placeholders, or intentionally incomplete features — do not bury these in prose.

**Include a System Context section only if** this project is part of a larger platform, has adjacent services with explicit ownership boundaries, or if the project's origin prevents a wrong technical assumption. Omit it for standalone projects.

**Include a Gotchas section if** Phase 1 or the mature codebase interview surfaced institutional knowledge that isn't derivable from the code — naming traps, hidden side effects, things that have caused incidents. Omit if none exist.

**If Phase 1 identified 2+ technical domains:** Write a slim, system-level root spec (target 60-100 lines). Technical domain-specific content (external deps, testing gaps, known issues, tech debt, technical domain boundaries) goes in technical domain specs created in Phase 8.

**If single-technical-domain project:** Include everything in the root spec (target 100-200 lines).
Skip Phase 8.

Do not include tech stack, directory structure, or dev commands — those belong in CLAUDE.md.

### Phase 5: Self-Review

Before presenting to the user, review the whole spec.md draft against these checks from [references/spec-standards.md](references/spec-standards.md) — apply each check to every section, not just the first:

**Required sections present:**
- [ ] Current State (most critical — must be section #1, must describe what is implemented today)
- [ ] Architecture Overview
- [ ] External Dependencies (shared only, if multi-technical-domain)
- [ ] Testing Strategy (infrastructure only, if multi-technical-domain)
- [ ] Boundaries & Constraints (project-wide only, if multi-technical-domain)
- [ ] Spec Index section with Subsystems and Features tables

**Content quality:**
- [ ] Current State uses past/present tense only — no "will", "planned", "upcoming"
- [ ] Stubs and incomplete features are in a named "Not yet implemented" list in Current State (not buried in prose)
- [ ] No tech stack, directory structure, or dev commands (those belong in CLAUDE.md)
- [ ] No content that restates what the code already shows
- [ ] External dependency table includes "Constraints / Can't Do" column (not just failure behavior)
- [ ] Boundaries & Constraints includes "ask if not covered by this spec" in Ask First
- [ ] Each line answers "what agent decision does this inform?" — remove lines that can't answer

**Density check:**
- [ ] System Context section is present only if this project has platform boundaries or an origin constraint that prevents a wrong technical assumption — omit for standalone projects
- [ ] Gotchas section is present if Phase 1 surfaced institutional knowledge not in the code
- [ ] No human motivation included unless it prevents a specific wrong technical assumption

**Split check (multi-technical-domain only):**
- [ ] No technical domain-specific external deps in root (they go in technical domain specs)
- [ ] No technical domain-specific known issues or tech debt in root
- [ ] No technical domain-specific boundaries in root
- [ ] Root spec under 100 lines

**Anti-patterns to remove:**
- [ ] Future roadmap items or planned features
- [ ] Standard language conventions the AI already knows
- [ ] Code style rules enforced by a linter
- [ ] Organizational motivation without a decision-informing constraint attached

Fix any issues found. Maximum 2 passes of the checklist above — after that, note remaining findings for the user.

**Decision-gap check (separate from the checklist passes above):** After the checklist passes, step back and classify the project: is it greenfield, mature monolith, multi-service platform, or internal tool? The risk profile differs — a greenfield project's invisible walls are framework limitations and external API constraints; a mature monolith's are legacy conventions and undocumented side effects. Anchor the questions below to this classification.

Then ask: *"If I got this wrong, what would break silently, be hard to reverse, or require a production fix?"* Generate exactly one question per category below — only if discovery surfaced a specific candidate. If a category has no candidate, skip it rather than inventing one.

| Category | What to look for | Where the answer goes |
|----------|-----------------|----------------------|
| **Invisible walls** | Capability constraints or integration limits not visible from the code — what the system *can't* do (rate limits, context windows, non-recursive APIs, output format restrictions) | External Dependencies "Constraints / Can't Do" column |
| **Settled decisions that look unsettled** | Multiple patterns in the codebase where one should be canonical — e.g., two HTTP clients, three auth approaches, mixed error-handling styles | Gotchas |
| **Silent side effects** | Operations that appear safe but have non-obvious consequences in this specific codebase — e.g., migrations auto-run on deploy, queue submissions are not idempotent, config object is mutated in-flight | Gotchas |

Each question must reference the specific file, pattern, or discovery that prompted it. Go find the answer — read files, run `git log`, grep for patterns — then update the relevant spec section before proceeding to Phase 6.

### Phase 6: Write Files

1. If `$ARGUMENTS` provides an output path, use it for CLAUDE.md. Otherwise default to the project root.
2. Write CLAUDE.md to the project root.
3. Write spec.md to `docs/specs/spec.md`. Create the `docs/specs/` directory if it doesn't exist.
4. Verify the CLAUDE.md Pointers to Deeper Docs section includes a pointer to `docs/specs/spec.md`.
5. Add a `## Spec Index` section at the end of `docs/specs/spec.md` with the header and an empty subsystems table (populated in Phase 8 if applicable) and an empty features table:

```markdown
## Spec Index

### Subsystems
| Spec | Path | Description |
|------|------|-------------|

### Features
| Feature | Path | Status | Updated | Description |
|---------|------|--------|---------|-------------|
```

This index is the discovery mechanism for all specs in the project. The `/spec-monkey:create-spec` skill reads this table to find related features and appends one rollup row per feature when creating one — the Path points at the feature's `index.md`, and the Status rolls up across that feature's slices.

### Phase 7: Review with User

Tell the user the files are written and ask them to review. Prompt them to check:

**For CLAUDE.md:**
- Which sections have placeholders they should fill in (Project Identity, Critical Constraints, or any others left blank)

**For spec.md:**
- Does the Current State section accurately describe what is implemented and working today, with nothing aspirational or future-tense?
- Are all stubs and incomplete features named in the "Not yet implemented" list?
- Does this accurately describe the project?
- Is anything missing that would cause an AI to make wrong assumptions?
- Are the failure behaviors and capability constraints (what the dependency *can't* do) for external dependencies accurate?
- Is anything included that's obvious from reading the code? (remove it if so)
- Are there gotchas — non-obvious traps or institutional knowledge — that aren't captured?

Iterate — applying their feedback as edits to the files. End each round of changes by asking: **"Any other changes, or reply 'approved' to finalise?"**

**When to push back on feedback:** if user feedback would violate a quality principle (CLAUDE.md over 200 lines, adding linter rules, duplicating spec.md content, adding future-tense items to Current State), flag the conflict:
> "That would [specific violation]. The quality guide recommends [alternative]. Want to proceed anyway, or adjust?"
When feedback would degrade the file, flag the conflict and ask before applying it — as shown above. Cap revision at 3 rounds; after that, suggest approving and iterating in a future session.

Once the user replies "approved", update the **Status** field in spec.md (and any technical domain specs) from `Draft` to `Active`, and update the **Last verified** date to today.

### Phase 8: Technical Domain-Scoped Specs

If Phase 1 identified **2 or more technical domains**, create a technical domain spec for each.

#### Step 1: Draft Technical Domain Specs

Write each to `docs/specs/subsystems/{domain-slug}/spec.md` using [domain-spec-template.md](references/domain-spec-template.md). Derive `{domain-slug}` from the domain name (lowercase, hyphens). Each spec is **under 100 lines**. Content gathered in Phase 1 but excluded from root (technical domain-specific deps, testing gaps, issues, boundaries) belongs here — don't leave it orphaned.

**Prioritization when the 100-line cap is tight** (in order — cut from the bottom):
1. **Interface Contracts** — what this domain exposes and consumes (highest value — this is why domain specs exist)
2. **Gotchas** — non-obvious traps specific to this domain
3. **Domain Boundaries** — Always/Ask First/Never rules for this domain
4. **Current State** — what's implemented in this domain now
5. **Known Issues** — currently broken things
6. **Domain Conventions** — naming, patterns (lowest priority — these are derivable from the code)

**Do not duplicate the root spec.md.** Shared conventions, project-wide boundaries, and deployment info stay at root. Omit empty sections.

Present drafts to the user for review before finalizing.

#### Step 2: Create Loading Rules

For each technical domain spec, create a path-scoped rule in `.claude/rules/` that loads the spec when Claude works in that directory. Rules use YAML frontmatter with a `paths` field for scoping:

```markdown
# .claude/rules/{domain-name}-context.md
---
paths:
  - "{domain-dir}/**/*"
---

Read docs/specs/subsystems/{domain-slug}/spec.md for technical domain-specific
conventions, interface contracts, and boundaries before making changes in this area.
```

#### Step 2b: Verify Rules Load

After creating rule files, verify each one by checking that the glob pattern matches actual files in the technical domain directory:

```
ls {domain-dir}/**/* | head -3
```

If the glob returns no files, fix the pattern — common mistakes are missing `**` and wrong directory prefix.

#### Step 3: Update Spec Index

Add each subsystem spec to the Subsystems table in `docs/specs/spec.md`'s Spec Index section:

```markdown
| {Domain Name} | `docs/specs/subsystems/{domain-slug}/spec.md` | {one-line description} |
```

Also add a pointer in CLAUDE.md's "Pointers to Deeper Docs" section to `docs/specs/spec.md` if not already present.

#### When NOT to Create Technical Domain Specs

- Project has only 1 technical domain — root spec.md is sufficient
- A subsystem has no technical domain-specific conventions, or its conventions are already in root — move them there, don't duplicate

---

## Gotchas

- **Don't guess commands** — If you can't find evidence of a command in config files, scripts, or docs, use a placeholder comment (`<!-- add test command -->`) instead of inventing one. Getting the package manager wrong (`npm` vs `pnpm` vs `yarn`) is a common failure.
- **Leave human-judgment sections as placeholders** — Project Identity and Critical Constraints require human input. Do not fill these with generic advice.
- **Keep CLAUDE.md under 200 lines** — A CLAUDE.md that's too long defeats its purpose as quick-reference context.
- **Don't skip discovery for existing projects** — Even when the user describes the project verbally, explore the codebase first — the code is the source of truth.
- **Don't confuse project spec with change spec** — If the user starts describing a specific feature or bug fix mid-interview, redirect them to `/spec-monkey:create-spec` or `/spec-monkey:bug` for that work.
- **Keep cross-references in sync** — When writing or moving files, verify CLAUDE.md's pointer to `docs/specs/spec.md` is correct and the Spec Index is up to date.
- **Don't conflate layers with technical domains** — `src/lambda_fn/` and `src/backend/` may look like siblings in a directory listing, but if they deploy separately or have divergent constraints, they are separate technical domains. Conversely, `src/models/`, `src/controllers/`, `src/routes/` share a deployment target, import each other directly, and have no divergent constraints — they are layers within one technical domain. Always apply the litmus test and signals from Phase 1, not directory names.
- **This skill targets the root CLAUDE.md** — For subdirectory CLAUDE.md files in a monorepo, scope content to that package's technical domain.

---
