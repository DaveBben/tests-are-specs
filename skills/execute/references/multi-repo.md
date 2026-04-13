# Multi-Repository Execution

Multi-repo support works best with monorepos (multiple packages in one
repo) or co-located repos. For truly separate repositories with
independent CI/CD, consider running `/cks:execute` independently per repo.

If plan.json has `repositories` with more than one entry, group tasks by
their `repository` field. Process each repository sequentially:

1. `cd` to the repository path
2. Create branch (`feature/{slug}` or `bugfix/{slug}`)
3. Execute all tasks for this repository (following the per-task loop)
4. Run post-implementation (Phase 2) for this repository
5. Finalize (Phase 3) for this repository
6. Return to next repository

For single-repo features (repository is `"."`), skip this grouping.

## Contract Stubs (multi-repo only)

When repo B depends on changes from repo A (e.g., new API endpoints,
shared types), repo B's tests can't hit repo A's unmerged changes. Use
contract stubs to decouple execution:

1. After completing repo A's tasks, extract the contract surface: type
   definitions, API schemas, or interface files that repo B depends on
2. Place these as stub files in repo B's test fixtures directory (e.g.,
   `tests/fixtures/contracts/repo-a-types.ts`)
3. Repo B's tests run against the stubs, not the live endpoints
4. Include a `TODO: replace stub with real import after repo A merges`
   comment in each stub file

If plan.json has a `contracts` field listing shared specs (OpenAPI,
protobuf, TypeScript interfaces), use those directly as the stubs rather
than extracting them.

This mirrors consumer-driven contract testing: both repos agree on the
contract, implement independently, and validate on merge.
