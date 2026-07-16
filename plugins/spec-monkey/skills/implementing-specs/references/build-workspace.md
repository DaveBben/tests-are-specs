# Build workspace: isolate the branch, name the finish

The spec is WHAT/WHEN plus a high-level approach; the detailed build is HOW. This file covers what the single-agent workflow (SKILL step 2 and step 6) leans on it for: **where** the build happens — an isolated branch, not the live checkout — and how it finishes. Both are portable: plain git, no hook, no subagent.

## Start on an isolated branch

Before the first slice, isolate the work:

- **Baseline must be clean.** If the working tree has uncommitted changes, stop and ask; don't build on top of someone else's half-done edit.
- **Cut a branch named for the slug** (`spec/<slug>`). Never build straight on the mainline. A multi-slice build that commits into the live checkout is how a half-built change reaches `main` by accident, and how two work items' commits get tangled.
- **A worktree is the upgrade where your setup supports it.** An isolated git worktree keeps the mainline checkout usable while the build runs, and a discarded build becomes a removed directory rather than a `reset`. The plain branch is the portable default; the worktree is strictly better where available. superpowers' `using-git-worktrees` is the deep version if you run it (see `docs/interop.md`).
- **One work item per branch.** `running-lifecycle` builds one item at a time; never stack a second item's commits on the first item's branch.

The spec's *Approach* (in `detail/design.md`) carries the high-level design intent across a session death; the slice ledger (`.spec-monkey/progress.md`) records which slice is done. Between them a resume recovers where it was and what shape it was building, without a separate build-plan file to maintain. Work the detailed HOW out from the *Approach*, the contract, and the real code each session.

## Finishing the build

The build stops before the branch merges; finishing is the human's step, the same discipline as the approval gate.

- Set `status: implemented` and commit with a message that points back to the spec (SKILL step 6). Then **name the finish and hand it over**: open a PR, or merge, or discard the branch/worktree — and let the human take that step. Don't merge to the mainline on your own read, and don't leave a half-built branch sitting unnamed.
- **Discard is a first-class outcome.** A spike that didn't pan out is a removed worktree or a deleted branch, and the mainline never saw it. Say so plainly rather than leaving dead commits behind.
- After a merge, `running-lifecycle`'s close-out (the human sets `status: shipped`) is the last step. A superseded or abandoned item goes `archived`.
