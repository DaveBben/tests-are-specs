# Common Failure Patterns

Known failure modes in the `/feature` workflow and how to avoid them.

---

- **Skimming instead of reading** — Phase 0 exists because the AI reads at
  signature level and moves on. Force deep reading with specific instructions:
  "read the full function body", "trace every caller", "understand the intricacies."
- **Planning before researching** — The research artifact must be written and
  reviewed BEFORE any plan. Without it, plans are structurally incorrect.
- **Pseudocode in the plan** — The plan must contain actual code snippets.
  Pseudocode leads to implementations that diverge from intent.
- **Accepting vague annotations** — If the user annotates "make this better",
  push back: "Better how? Faster? More readable? Different API shape?"
- **Skipping the impact map review** — The impact map catches wrong-module
  errors. Skipping it means discovering structural problems after tasks are
  written.
- **Tasks with multiple concerns** — Each task must target one logical
  concern (typically 1-3 files). Tasks that mix unrelated concerns produce
  significantly worse AI results.
- **"Should" instead of "must"** — "Should" reduces AI adherence. Use "must"
  for all task constraints.
- **Missing "Do NOT" boundaries** — Without explicit boundaries, tasks expand
  into adjacent work. Every task needs a "Do NOT" field.
- **Feature too large** — More than ~50 tasks means the feature needs to be
  split. Plan at the right altitude.
- **Horizontal layering** — Grouping tasks by layer (all DB changes, then
  all service changes, then all endpoint changes) means nothing works until
  everything is done. Each slice must be a vertical cut: DB + service +
  endpoint + test for one capability.
