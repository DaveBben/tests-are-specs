# CLAUDE.md Quality Guide

## Core Principles

**Context, not configuration.** CLAUDE.md provides context that helps Claude make better decisions. It
does not replace deterministic tools. If a rule can be enforced by a linter, formatter, type checker,
or CI step, enforce it there — not in CLAUDE.md. Deterministic tools catch violations perfectly;
CLAUDE.md instructions are probabilistic and waste context budget on things tools handle better.

**Brevity is load-bearing.** The root CLAUDE.md should stay under 200 lines. Claude's context window
is shared with the system prompt (~50 instructions already consumed) and the actual conversation. Every
line in CLAUDE.md competes with the task at hand. Aim for the shortest file that changes Claude's
behavior — if a line does not change how Claude works in this repo, remove it.

**Specific and verifiable.** Instructions must be concrete enough that compliance is binary. "Use
2-space indentation" is verifiable. "Format code properly" is not. "Run `uv run pytest` before
committing" is actionable. "Make sure tests pass" is not. Every instruction should complete the
sentence: "I can verify this by checking that..."

**Universally applicable only.** The root CLAUDE.md should contain instructions that apply to every
task in the repo. Task-specific, path-specific, or feature-specific instructions belong in
`.claude/rules/` files (with `paths` frontmatter) or subdirectory CLAUDE.md files. The root file is
not a dumping ground for everything Claude should know.

**Pointers over copies.** Reference files by path rather than copying content into CLAUDE.md. "See
`docs/architecture.md` for system design" is better than pasting the architecture inline. Copied
content goes stale instantly and consumes disproportionate context. Avoid `@path/to/import` syntax
unless the content must be loaded into every single session — this is rare. Prefer file path pointers
in the Pointers to Deeper Docs section.

**Progressive disclosure through file hierarchy.** Use the CLAUDE.md cascade for depth: root CLAUDE.md
for project-wide context, subdirectory CLAUDE.md files for component-specific context, `.claude/rules/`
for modular path-scoped rules. Claude loads subdirectory files on demand when it reads files in those
directories — no need to cram everything into the root.

**Keep it current.** CLAUDE.md must be maintained as the project evolves. Stale commands, outdated
directory layouts, or deprecated constraints are worse than no instructions — they actively mislead
Claude. Update Tech Stack and Operational Commands whenever tooling changes. If a section is no longer
accurate, fix it or remove it.

---

## Anti-Patterns

**Using CLAUDE.md as a linter.** "Always use single quotes," "never use var," and "prefer const over
let" belong in ESLint/Ruff/Clippy config, not CLAUDE.md. Deterministic tools catch these perfectly.
CLAUDE.md instructions for style rules waste context and produce inconsistent results. Instead, use
CLAUDE.md for judgment calls tools can't enforce: "Prefer composition over inheritance for new services."

**Wall of text with no structure.** A CLAUDE.md with no headers, no bullets, and no visual hierarchy
is hard for both humans and LLMs to parse. Instead, use markdown headers to group sections and bullets
for lists. Structure sections consistently so Claude can scan them efficiently.

**Conflicting instructions.** "Always write comprehensive tests" combined with "Keep changes minimal"
creates an unresolvable tension. Audit instructions for contradictions across your CLAUDE.md files,
subdirectory files, and `.claude/rules/`. When trade-offs exist, state the priority explicitly.

**Task-specific instructions in the root file.** "When working on the auth module, always check token
expiry" belongs in `src/auth/CLAUDE.md` or `.claude/rules/auth.md` with a `paths` frontmatter scoped
to `src/auth/**`. Instead, root-level instructions should apply to every task — keep them general.

**Pasting code snippets as examples.** Code snippets become stale instantly and consume
disproportionate context. Instead, point to real files: *"Follow the pattern in
`src/services/user-service.ts:15-40`."* The source file is always current; a pasted copy is frozen.

**Instruction overload.** Dumping 300+ lines of instructions degrades overall compliance. LLMs show
diminishing attention to instructions beyond ~150-200 total (including the system prompt). Instead,
prioritize ruthlessly — move specialized content to `.claude/rules/` files or subdirectory CLAUDE.md
files.
