# Pipeline Overview

The full backlog-driven development pipeline from raw idea to shipped code.

```
                    PLANNING                                                     EXECUTION
 ___________      ________      _______________      _________      ______________      _________
|           |    |        |    |               |    |         |    |              |    |         |
| /initiative|--->| /epic  |--->| /architecture |--->| /refine |--->| /task-decomp |--->| /execute|
|___________|    |________|    |___(optional)__|    |_________|    |______________|    |_________|
     |                |              |                  |              |     |            |
     v                v              v                  v              v     v            v
  init-rev        epic-rev       arch-rev          story-rev      plan-rev  test-rev   /check (per task)
  (READY?)        (READY?)       (READY?)          (READY?)       (APPROVE?) (SOUND?)  /deep-review (per repo)
                                                                                          |
                                                                                       code-writer
                                                                                       PR + push
```

## Stage Details

| # | Skill | Input | Output | Gate | Notes |
|---|-------|-------|--------|------|-------|
| 1 | `/initiative` | Raw idea or opportunity description | Initiative document (problem, alignment, metrics, scope, risks, milestones) | `initiative-reviewer` | Gap-driven questioning |
| 2 | `/epic` | Initiative (batch creates all) or standalone description | Epic documents (goal, success metric, ordering rationale, scope, DoD) | `epic-reviewer` | No story maps — decomposition happens in /refine |
| 3 | `/architecture` | Initiative + all epics | Architecture document (system overview + per-epic detail with unknowns/spikes) | `architecture-reviewer` | **Optional.** Narrative format, prose decisions |
| 4 | `/refine` | Epic + architecture + initiative | Stories (spike + feature) with GIVEN/WHEN/THEN ACs | Per-story `story-reviewer` | Drafts all stories itself, architecture-driven decomposition |
| 5 | `/task-decomposition` | Story + upstream artifacts | Task files with parallel-optimized TDD structure | `plan-reviewer` + `test-reviewer` | JSON task artifacts in ~/.claude/backlog-driven-development/artifacts/ |
| 6 | `/execute` | Story + task files | Implemented code — one branch per repo | `/check` per task, `/deep-review` per repo | Multi-repo in one invocation, PR + push |

## Data Flow

```
/initiative → initiative.md (Problem, Alignment, Metrics, Scope)
  └── /epic → epic documents (Goal, Success Metric, Ordering, Scope, DoD)
          └── /architecture → architecture.md (System Overview + Per-Epic Detail)
          └── /refine (reads epic + architecture)
                  └── stories (spike + feature, with ACs)
                          └── /task-decomposition → tasks (with Verification, Do NOT, Repository)
                                  └── /execute (groups by repo, branch per repo)
                                          └── /check per task → /deep-review per repo → PR + push
```

## Key Principles

- **Gap-driven questioning:** Skills analyze upstream context and only ask about what's missing
- **JSON artifacts:** All artifacts stored as flat JSON files in `~/.claude/backlog-driven-development/artifacts/` with an `index.json` for discovery
- **Multi-repo aware:** Tasks are tagged per repo, `/execute` groups by repo and creates one branch + PR per repo
- **Two-tier review:** `/check` per task (fast), `/deep-review` per repo (thorough)
- **Architecture drives decomposition:** Per-epic component detail → spike stories + feature stories
- **Quality gates block forward progress:** Every stage has a reviewer agent
- **Backflow via NEEDS_REFINEMENT:** Downstream skills flag upstream issues with dedicated status check phases
