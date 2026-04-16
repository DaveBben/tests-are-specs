# Investigation Agent Questions

## Agent 1 — Blast radius
1. Which files contain the entry point and immediate consumers of this
   change? Follow imports one level deep from the entry point.
2. Which test files import, mock, or call into any of those files?
   Return: file path, test symbol (describe/it/test block name).
3. What is the import chain from the app entry point to the target
   symbol? Return the ordered list of file paths (3-5 hops max).

## Agent 2 — Existing patterns
1. Does anything structurally similar already exist in the codebase
   that this change could extend rather than duplicate?
   Return: file:line and one sentence on what it does.
2. Are there any TODOs, FIXMEs, or comments in the target area that
   mention relevant constraints or known issues?
   Return: file:line and the comment text verbatim.
3. What is the closest analogous change already made in this codebase?
   Return: file:line of the reference implementation.

## Agent 3 — Data shapes and contracts
1. What type definitions, interfaces, or schemas describe data flowing
   through the target area? Return: file:line for each type/interface.
2. What external callers consume the output of the target — routes, API
   handlers, queue consumers, other services? These are what break
   silently when a shape changes. Return: file:line for each caller.
3. Are there serialization boundaries near the target — places where
   data is written to a database, cache, queue, or sent over the wire
   in a format that encodes the current shape?
   Return: file:line and the storage mechanism (e.g. "postgres column",
   "redis key", "JSON response body").

## Agent output format

Cap each agent's return to **3 lines per question**:
```
Q: [question]
A: file:line — [finding]
Note: [one sentence max]
```

If any question lacks a `file:line` answer, note "not found" — do not
invent answers. Unverified context is worse than no context.
