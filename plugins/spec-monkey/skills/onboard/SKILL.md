---
name: onboard
description: "Use when onboarding a new or existing repository — setting up, initializing, or documenting a repo for the first time. Creates standards.md (the project constitution — invariants, commands, testing, structure, code style, git workflow, and agent boundaries), a thin CLAUDE.md pointer, spec.md (living project specification), and .claude/rules/ files (spec maintenance and domain-scoped context loading). For multi-domain projects, also creates technical domain-scoped spec.md files."
disable-model-invocation: true
argument-hint: "[output-path]"
model: opus
effort: high
---

# Onboard — Repository Setup

## What Goes Where

This skill produces three artifacts. Each owns one job. Never duplicate content across them — a fact lives in exactly one file, and the other two point at it.

| standards.md — the constitution | spec.md — current state | CLAUDE.md — thin pointer |
|---------------------------------|-------------------------|--------------------------|
| Invariants — the non-negotiable rules that gate every change | Current state — what's actually implemented (goes first) | Pointer to `standards.md` (the constitution) |
| Commands — exact invocations with flags | What's NOT yet implemented — stubs and placeholders | Pointer to `docs/specs/spec.md` (current state) |
| Testing — framework, layout, how to run | Architecture overview and external dependencies | Project Identity — what/why/who (human judgment) |
| Project structure — top-level dirs, entry point | Deployment & infrastructure | Genuinely quick-reference context an agent needs at a glance |
| Code style — config + ONE real snippet from this repo | Testing strategy (what exists and what's missing) | — |
| Git workflow — branch, commit, PR rules | Boundaries section — points at `standards.md`, does not restate it | — |
| Boundaries — three tiers: ✅ always / ⚠️ ask-first / 🚫 never | Gotchas — institutional knowledge not in the code | — |
| — | System context (if part of a larger platform) | — |
| — | Ownership, known issues, tech debt | — |

**`standards.md` is the DRY master.** It holds the invariants and the six areas (Commands, Testing, Project structure, Code style, Git workflow, Boundaries). Every v3 slice spec references it via `standards:` front-matter and inlines only a short, slice-relevant excerpt. The commands, structure, and boundaries that used to live in CLAUDE.md now live here. Do not restate the six areas in CLAUDE.md — that breaks the DRY-constitution rule.

**The file is named `standards.md` by default.** If the repo already uses `CLAUDE.md` or `AGENTS.md` as its agent constitution, you may keep that name instead. Pick **one** name and use that exact form everywhere — in each slice's `standards:` front-matter and in every in-prose mention.

---

**Write the prose to be read on one pass.** When you draft the prose in these docs — standards.md invariants, Current State, Architecture overview, Gotchas, Project Identity — follow the readable style in `references/writing-style.md` (read it when you reach Phase 3 and Phase 4). It shapes sentences only. It complements — it does not loosen — the density rules in `references/quality-guide.md` and `references/spec-standards.md` (semantic density, named lists, exact commands, "Not yet implemented" lists).

`standards.md` is drafted from the `create-spec` skill's `reference/standards-template.md` — the source of truth for its structure. Read that template when you reach Phase 3.

## Workflow

### Phase 1: Unified Discovery

One exploration pass gathers everything needed for both documents. Focus on the project root and first-level subdirectories. Do not recurse past the second directory level unless you need to verify a specific technical domain boundary (e.g., checking whether `src/auth/middleware/` imports from `src/billing/` to determine if they communicate through direct imports or contracts). When you go deeper, state what you're checking and return to the top level. **Stop exploring during this phase once you have concrete answers for each category below** — do not continue reading files for additional supporting evidence. Over-retrieval wastes context and delays the user. (Phase 5's decision-gap check may require targeted follow-up reads — that is a separate, scoped activity.)

**Gather for standards.md (the constitution):**
- Primary language(s), frameworks, and their versions
- Package manager and build system
- Linter/formatter configs (`.eslintrc*`, `ruff.toml`, `pyproject.toml [tool.ruff]`, etc.) — note any lint rule that encodes an invariant (e.g. a ban on bare `except` that enforces fail-loud)
- Top-level directory structure with one-line purposes, and the main entry-point file
- Build/test/lint/format/run commands, with their exact flags — these become the Commands area
- Git workflow signals — pre-commit hooks, the CI workflow (`.github/workflows/`), staging conventions
- **One representative code-style snippet** — find the house idiom for the thing that matters most (usually error handling) in a representative module. Lift it verbatim; it becomes the single real snippet in the Code style area. One short, real snippet beats three paragraphs.
- **Invariants** — how the code actually behaves at its edges. Read for: fail-open vs. fail-loud on errors, ordering guarantees (e.g. write-then-mark-seen), secret handling (env-only vs. committed config). These become the non-negotiable rules. Pull them from behavior, not aspiration.
- **Boundaries** — what an agent must always do, ask first about, and never do. These become the three-tier Boundaries area.

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

- **CLAUDE.md found**: This workflow moves the commands, structure, and boundaries that CLAUDE.md used to hold into `standards.md`, then shrinks CLAUDE.md to a thin pointer. **Propose this before overwriting.** Ask: "A CLAUDE.md already exists. The v3 model moves its commands, structure, and boundaries into a new `standards.md` constitution, then shrinks CLAUDE.md to a pointer at `standards.md` and `spec.md`. Would you like to **(a)** do that (I'll carry your content into the right file), or **(b)** leave CLAUDE.md as-is and only add `standards.md`?" If the repo already uses CLAUDE.md (or AGENTS.md) as its constitution, ask whether to keep that as the constitution's filename instead of `standards.md`.
- **standards.md found** (also check `AGENTS.md`): "A `{filename}` already exists. Would you like to **(a)** update it to the v3 constitution format while preserving your content, or **(b)** start fresh?" Use the existing filename as the constitution's canonical form.
- **spec.md found** (also check `SPEC.md`, `PROJECT-SPEC.md`): Before asking the user, compare the Current State section against what discovery found. If they diverge, show the specific drift: "spec.md exists but its Current State appears stale: - Spec says: '[quote from Current State]' - Code shows: '[what discovery found]' Would you like to **(a)** update it (I'll fix the drift and match best-practice format), or **(b)** start fresh?"

Then ask: **"This workflow creates standards.md (the constitution), spec.md (current state), and a thin CLAUDE.md. If you only need the constitution and CLAUDE.md, say so now — otherwise we'll proceed with all three."**

If the user opts out of spec.md, skip Phases 4, 5, and the spec.md portions of Phases 6-7.

**Merge rules when updating existing files:**
- **Existing content wins** for human-judgment sections (Project Identity, motivation, ownership, the invariants and boundaries in `standards.md`)
- **Discovery data wins** for factual sections (versions, commands, current state, testing strategy, deployment, the Commands and Project structure areas in `standards.md`)
- **Blend rule** for sections that mix both (Architecture Decisions, Gotchas, the Code style snippet in `standards.md`): keep the existing *rationale and judgment* (the "why"), but update *factual claims* (paths, versions, what exists) from discovery silently. When discovery contradicts an existing *rationale* (not just a factual claim), flag the conflict to the user rather than overwriting.

### Phase 3: Draft standards.md and a thin CLAUDE.md

Draft the constitution first, then point CLAUDE.md at it. Read [references/quality-guide.md](references/quality-guide.md) for CLAUDE.md principles, and the `create-spec` skill's `reference/standards-template.md` for the constitution's exact structure.

**Step 1 — Draft standards.md from the template.** Fill every section from Phase 1 discovery. Keep the template's seven headings and their order: Invariants, then the six areas (Commands, Testing, Project structure, Code style, Git workflow, Boundaries).

- **Invariants** — the 3-6 non-negotiable rules you pulled from how the code behaves at its edges (fail-open vs. fail-loud, ordering guarantees, secret handling). State each as one rule plus why it exists.
- **Commands** — the exact invocations with flags, copy-pasteable, grouped install/run/test/typecheck/lint/format. End with "the gate": the single command run before every PR. **Never invent a command** — if a category has no command, say so with a placeholder comment.
- **Testing** — framework, where tests live, how to run them, the real test conventions.
- **Project structure** — top-level directories with one-line purposes, and the entry-point file. No deep tree.
- **Code style** — the enforced config, plus the ONE real snippet you lifted verbatim from this repo. Note any lint rule that encodes an invariant.
- **Git workflow** — branch, commit, and PR rules pulled from the real hooks and CI.
- **Boundaries** — the three tiers (✅ always / ⚠️ ask-first / 🚫 never). Always include an ask-first catch-all: "anything not covered by this constitution." If spec.md is being created in this run, add to ✅ always: "after significant implementation changes, update `docs/specs/spec.md` Current State (and the subsystem spec if the change is subsystem-scoped) — stale specs are worse than no specs."

Name the file `standards.md` by default. If Phase 2 found the repo uses `CLAUDE.md` or `AGENTS.md` as its constitution, use that name instead — and use that one exact form everywhere.

**Step 2 — Write CLAUDE.md as a thin pointer.** CLAUDE.md no longer holds the commands, structure, or boundaries — those live in standards.md now. Do not duplicate the six areas here. Use [references/claude-md-format.md](references/claude-md-format.md) for the section skeleton, but keep it short:

- **Project Identity** — leave blank with an HTML comment placeholder; this requires human judgment.
- **Pointers to Deeper Docs** — point at both the constitution and the current state:
  - `` `standards.md` — the constitution: invariants, commands, testing, structure, code style, git workflow, and agent boundaries `` (use the actual filename if you chose `CLAUDE.md`/`AGENTS.md`).
  - If spec.md is being created in this run: `` `docs/specs/spec.md` — project spec, architecture overview, and spec index ``. Omit if the user opted out of spec.md.
- **Genuinely CLAUDE.md-specific quick-reference** — only context an agent needs at a glance that is not already in standards.md or spec.md. If there is none, that is fine — a thin pointer is the goal.

If the chosen constitution filename is `CLAUDE.md` itself, then the constitution IS the CLAUDE.md — skip writing a separate pointer file and add the spec.md pointer to the constitution's own Pointers section.

**Self-review** before proceeding to Phase 4:
- [ ] standards.md fills every template section from discovery — no invented commands; absent categories use a placeholder comment
- [ ] standards.md Code style includes ONE real snippet lifted from this repo
- [ ] standards.md Boundaries has all three tiers and an ask-first catch-all
- [ ] CLAUDE.md is under 200 lines
- [ ] CLAUDE.md does NOT restate the six areas — commands, structure, and boundaries live in standards.md
- [ ] CLAUDE.md Pointers section points at both standards.md and (if created) spec.md
- [ ] Project Identity is either filled with what/why/who or left as a placeholder — not filled with technology descriptions

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

**Boundaries section — point at standards.md, do not restate it.** The project-wide boundaries now live in `standards.md` (the constitution). spec.md's Boundaries section becomes a one-line pointer: "Agent boundaries (✅ always / ⚠️ ask-first / 🚫 never) live in `standards.md` — the constitution." Do not duplicate the three tiers here. (Domain specs in Phase 8 may still add domain-specific boundaries that extend the constitution.)

Do not include tech stack, directory structure, dev commands, or the boundary tiers — those belong in standards.md and CLAUDE.md.

### Phase 5: Self-Review

Before presenting to the user, review the whole spec.md draft against these checks from [references/spec-standards.md](references/spec-standards.md) — apply each check to every section, not just the first:

**Required sections present:**
- [ ] Current State (most critical — must be section #1, must describe what is implemented today)
- [ ] Architecture Overview
- [ ] External Dependencies (shared only, if multi-technical-domain)
- [ ] Testing Strategy (infrastructure only, if multi-technical-domain)
- [ ] Boundaries section points at `standards.md` — it does not restate the three tiers
- [ ] Spec Index section with Subsystems and Features tables

**Content quality:**
- [ ] Current State uses past/present tense only — no "will", "planned", "upcoming"
- [ ] Stubs and incomplete features are in a named "Not yet implemented" list in Current State (not buried in prose)
- [ ] No tech stack, directory structure, or dev commands (those belong in standards.md / CLAUDE.md)
- [ ] No content that restates what the code already shows
- [ ] External dependency table includes "Constraints / Can't Do" column (not just failure behavior)
- [ ] No restated boundary tiers — the Boundaries section points at `standards.md` (which carries the ask-first catch-all)
- [ ] Each line answers "what agent decision does this inform?" — remove lines that can't answer

**Density check:**
- [ ] System Context section is present only if this project has platform boundaries or an origin constraint that prevents a wrong technical assumption — omit for standalone projects
- [ ] Gotchas section is present if Phase 1 surfaced institutional knowledge not in the code
- [ ] No human motivation included unless it prevents a specific wrong technical assumption

**Split check (multi-technical-domain only):**
- [ ] No technical domain-specific external deps in root (they go in technical domain specs)
- [ ] No technical domain-specific known issues or tech debt in root
- [ ] No technical domain-specific boundaries in root (project-wide boundaries live in standards.md; domain-specific ones extend it from domain specs)
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
2. Write `standards.md` (or the chosen constitution filename) to the project root, next to CLAUDE.md.
3. Write CLAUDE.md to the project root. (If the chosen constitution filename is `CLAUDE.md` itself, the constitution is the only file at root — there is no separate pointer file.)
4. Write spec.md to `docs/specs/spec.md`. Create the `docs/specs/` directory if it doesn't exist.
5. Verify the cross-references: CLAUDE.md's Pointers to Deeper Docs section points at both `standards.md` (the constitution) and `docs/specs/spec.md` (current state). Confirm spec.md's Boundaries section points at `standards.md` rather than restating the tiers.
6. Add a `## Spec Index` section at the end of `docs/specs/spec.md` with the header and an empty subsystems table (populated in Phase 8 if applicable) and an empty features table:

```markdown
## Spec Index

### Subsystems
| Spec | Path | Description |
|------|------|-------------|

### Features
| Feature | Path | Status | Updated | Description |
|---------|------|--------|---------|-------------|
```

This index is the discovery mechanism for all specs in the project. The `/spec-monkey:create-spec` skill reads this table to find related features and appends one rollup row per feature when creating one — the Path points at the feature's `_index.md`, and the Status rolls up across that feature's slices.

### Phase 7: Review with User

Tell the user the files are written and ask them to review. Prompt them to check:

**For standards.md (the constitution):**
- Are the invariants right? These are the non-negotiable rules that gate every change — an agent will refuse work that violates one.
- Is every command exact and copy-pasteable, with no invented commands?
- Do the three boundary tiers (✅ always / ⚠️ ask-first / 🚫 never) match how the team actually works?
- Is the code-style snippet the idiom you want agents to copy?

**For CLAUDE.md:**
- Which sections have placeholders they should fill in (Project Identity, or any others left blank)
- Confirm it is a thin pointer at standards.md and spec.md — not a second copy of the commands and boundaries

**For spec.md:**
- Does the Current State section accurately describe what is implemented and working today, with nothing aspirational or future-tense?
- Are all stubs and incomplete features named in the "Not yet implemented" list?
- Does this accurately describe the project?
- Is anything missing that would cause an AI to make wrong assumptions?
- Are the failure behaviors and capability constraints (what the dependency *can't* do) for external dependencies accurate?
- Is anything included that's obvious from reading the code? (remove it if so)
- Are there gotchas — non-obvious traps or institutional knowledge — that aren't captured?

Iterate — applying their feedback as edits to the files. End each round of changes by asking: **"Any other changes, or reply 'approved' to finalise?"**

**When to push back on feedback:** if user feedback would violate a quality principle (CLAUDE.md over 200 lines, adding linter rules, duplicating the six areas across standards.md and CLAUDE.md, duplicating spec.md content, adding future-tense items to Current State), flag the conflict:
> "That would [specific violation]. The quality guide recommends [alternative]. Want to proceed anyway, or adjust?"
When feedback would degrade the file, flag the conflict and ask before applying it — as shown above. Cap revision at 3 rounds; after that, suggest approving and iterating in a future session.

Once the user replies "approved", update the **Status** field in spec.md (and any technical domain specs) from `Draft` to `Active`, and update the **Last verified** date to today. In standards.md, replace the "draft for review" status line with the accepted date — the constitution is now in force.

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

**Do not duplicate the root spec.md or standards.md.** Shared conventions and deployment info stay in the root spec; project-wide boundaries live in standards.md. A domain spec's Domain Boundaries section adds only domain-specific rules that **extend** the constitution — never restate the project-wide tiers. Omit empty sections.

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

- **Don't duplicate the six areas across standards.md and CLAUDE.md** — Commands, structure, and boundaries live in standards.md (the constitution). CLAUDE.md is a thin pointer at standards.md and spec.md. Restating the six areas in both files breaks the DRY-constitution rule and creates two places to go stale.
- **Don't guess commands** — If you can't find evidence of a command in config files, scripts, or docs, use a placeholder comment (`<!-- add test command -->`) instead of inventing one. The commands now live in standards.md's Commands area. Getting the package manager wrong (`npm` vs `pnpm` vs `yarn`) is a common failure.
- **Pick ONE constitution filename and keep it exact** — Default to `standards.md`. Use `CLAUDE.md` or `AGENTS.md` only if the repo already uses one as its constitution. Whatever you pick, use that exact form in every slice's `standards:` front-matter and in every in-prose mention — no `/standards.md`-vs-`standards.md` drift.
- **Leave human-judgment sections as placeholders** — Project Identity (CLAUDE.md) requires human input. Do not fill it with generic advice.
- **Keep CLAUDE.md under 200 lines** — A CLAUDE.md that's too long defeats its purpose as quick-reference context.
- **Don't skip discovery for existing projects** — Even when the user describes the project verbally, explore the codebase first — the code is the source of truth.
- **Don't confuse project spec with change spec** — If the user starts describing a specific feature or bug fix mid-interview, redirect them to `/spec-monkey:create-spec` or `/spec-monkey:bug` for that work.
- **Keep cross-references in sync** — When writing or moving files, verify CLAUDE.md points at both `standards.md` and `docs/specs/spec.md`, that spec.md's Boundaries section points at `standards.md`, and that the Spec Index is up to date.
- **Don't conflate layers with technical domains** — `src/lambda_fn/` and `src/backend/` may look like siblings in a directory listing, but if they deploy separately or have divergent constraints, they are separate technical domains. Conversely, `src/models/`, `src/controllers/`, `src/routes/` share a deployment target, import each other directly, and have no divergent constraints — they are layers within one technical domain. Always apply the litmus test and signals from Phase 1, not directory names.
- **This skill targets the root CLAUDE.md** — For subdirectory CLAUDE.md files in a monorepo, scope content to that package's technical domain.

---
