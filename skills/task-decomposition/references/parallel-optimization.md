# Parallel Optimization Guide

Reference for Phase 4 Steps 2-4 of the task-decomposition skill: building the dependency
DAG, computing parallel batches, and identifying the critical path.

---

## Step 2: Build the Dependency DAG

Model tasks as a directed acyclic graph:

- Each task is a node
- A directed edge from A to B means "B is Blocked By A"
- Task 0 (if present) is the root — all other tasks depend on it

**Dependency rules** — add an edge from Task N to Task M when:
- Task N creates a type or interface that Task M imports
- Task N creates a file that Task M modifies
- Task N creates test infrastructure that Task M uses
- Task N produces data or state that Task M reads

**Minimize edges.** Prefer independent tasks. If two tasks could share a file, consider
whether the shared concern should be extracted into a third task (or into Task 0).

---

## Step 3: Compute Parallel Batches

Apply Kahn's algorithm to produce execution batches:

```
completed = {0}  // Task 0 already done
batches = []
while unscheduled tasks remain:
  candidates = tasks where all Blocked By deps ∈ completed
  batch = [], batchFiles = {}
  for candidate in candidates (task order):
    if candidate.relevantFiles ∩ batchFiles == ∅:
      batch.add(candidate), batchFiles ∪= candidate.relevantFiles
  batches.add(batch)
  completed ∪= batch
```

If the algorithm cannot complete (cycle detected), the DAG has a circular dependency —
fix it before proceeding.

---

## Step 4: Identify Critical Path

The critical path is the longest chain of dependent tasks through the DAG. It determines
the minimum number of batches `/execute` will need.

Present the execution schedule prominently in the plan:

```
## Parallel Execution Schedule

Critical path: Task 0 → Task 1 → Task 4 (3 batches minimum)

Batch 1 (parallel): Task 1, Task 2, Task 3
Batch 2 (parallel): Task 4 (blocked by Task 1), Task 5 (blocked by Task 2)
Batch 3: Task 6 (blocked by Task 4, Task 5)

Total: 6 tasks, 3 batches (plus Task 0)
```
