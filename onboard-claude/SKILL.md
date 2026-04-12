---
name: onboard-claude
description: Use when creating, updating, or improving a CLAUDE.md file for a repository, including repo onboarding. Do NOT use for reviewing existing CLAUDE.md quality without changes, or for creating .claude/rules/ files.
disable-model-invocation: true
argument-hint: "[output-path]"
---

# Create CLAUDE.md

A CLAUDE.md file is the primary context document that Claude reads at the start of every session in a
repository. It tells Claude what the project is, how it is built, what commands to run, and what
constraints to respect. It is context for decision-making, not enforced configuration — it does not
replace linters, formatters, or CI.

---

## Workflow

Infer as much as possible from the codebase; leave placeholders for what cannot be inferred.

### Phase 1: Explore the Codebase

Focus on the project root and first-level subdirectories. Read package manager configs and build system files but do not recurse deeply into source directories. Gather:

- Primary language(s), frameworks, and their versions
- Package manager and build system
- Linter/formatter configs (`.eslintrc*`, `ruff.toml`, `pyproject.toml [tool.ruff]`, etc.)
- Top-level directory structure with one-line purposes
- Build/test/lint/format/run commands
- Existing files: `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, `spec.md`, `docs/architecture.md`, `README.md`, `CONTRIBUTING.md`, or other documentation

### Phase 2: Check for Existing CLAUDE.md

If the exploration found an existing `CLAUDE.md` or `.claude/CLAUDE.md`:

1. Read the existing file
2. Ask the user: "A CLAUDE.md already exists. Would you like to **(a)** update it to match best-practice format while preserving your content, or **(b)** start fresh?"
3. If the user chooses (a), preserve existing content and map it into the new format in Phase 3
4. If the user chooses (b), proceed as if no file exists

If no existing CLAUDE.md was found, skip directly to Phase 3.

### Phase 3: Draft the CLAUDE.md

Read [references/quality-guide.md](references/quality-guide.md) for the principles to follow. Use
[references/claude-md-format.md](references/claude-md-format.md) for the exact section structure.

Using the exploration summary from Phase 1, draft each section per the format reference:

- **Fill from exploration data**: Tech Stack and Codebase Map, Operational Commands, Pointers to Deeper Docs. If a command category was not found, include a placeholder comment like `<!-- add test command -->`.
- **Leave blank with HTML comment placeholder**: Project Identity and Critical Constraints — these require human judgment and cannot be reliably inferred.
- **If a `spec.md` was found in Phase 1**, always include a pointer to it in the Pointers to Deeper Docs section: `` `spec.md` — current project state, architecture overview, and working constraints ``

**If updating an existing file (Phase 2, option a):**
- Preserve any existing Project Identity content
- Merge existing tech stack info with exploration findings (exploration data wins for factual data like versions)
- Merge existing commands with discovered commands (keep both, deduplicate)
- Preserve any existing Critical Constraints verbatim
- Merge existing doc pointers with discovered docs

### Gotchas

- **Don't guess commands** — If you can't find evidence of a command in config files, scripts, or docs, use a placeholder comment (`<!-- add test command -->`) instead of inventing one. Getting the package manager wrong (`npm` vs `pnpm` vs `yarn`) is a common failure.
- **Leave human-judgment sections as placeholders** — Project Identity and Critical Constraints require human input. Do not fill these with generic advice.
- **Keep it under 200 lines** — See the quality guide. A CLAUDE.md that's too long defeats its purpose as quick-reference context.
- **This skill targets the root CLAUDE.md** — For subdirectory CLAUDE.md files in a monorepo, scope content to that package's domain. See the quality guide's progressive disclosure principle.
- **spec.md pointer only if it exists** — Only add `spec.md` to Pointers to Deeper Docs if the file actually exists (found in Phase 1) or will be created in Phase 5. Never add a pointer to a non-existent file — this actively misleads Claude in future sessions.

### Phase 4: Write

1. If `$ARGUMENTS` provides an output path, verify the directory exists before writing
2. Write the drafted CLAUDE.md to the project root (or to `$ARGUMENTS` if a path was provided)
3. Tell the user which sections have placeholders they should fill in (Project Identity, Critical Constraints, or any others left blank)

### Phase 5: Offer spec.md Creation

After writing CLAUDE.md, ask the user:

"CLAUDE.md is written. Would you also like to create a spec.md — a living document capturing this project's current state, architecture, ownership, and constraints? It gives any developer or AI a deeper picture beyond what CLAUDE.md covers. (Say yes to proceed with `/capture`, or no to finish here.)"

If the user says yes, invoke the `capture` skill.

If the user says no, finish here.
