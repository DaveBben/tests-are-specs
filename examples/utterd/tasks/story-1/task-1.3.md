# Task 1.3: Implement sync completion detection before emitting files

**Status**: Not Started
**Implementer**: AI
**Repository**: utterd
**Blocked By**: Task 1.2, Spike Task 0 (need the confirmed sync detection method)
**Covers**: AC: watcher waits until file is fully synced before emitting

**Relevant Files:**
- `Sources/Utterd/Watcher/FSEventsWatcher.swift` <- modify
- `Sources/Utterd/Watcher/SyncCompletionChecker.swift` <- create
- `Tests/UtterdTests/Watcher/SyncCompletionCheckerTests.swift` <- create

**Context to Read First:**
- Architecture doc Section 2.2, specifically the sync detection method confirmed during the spike. The implementation below assumes the spike recommended file-size-stability polling. If the spike identified a better method (extended attributes, NSFileCoordinator), adapt accordingly.
- `Sources/Utterd/Watcher/FSEventsWatcher.swift` — current implementation from Task 1.2

**Steps:**
1. [ ] Write failing tests based on acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**
- GIVEN a temp file that is being appended to every 0.5 seconds for 3 seconds then stops, WHEN `waitForSyncCompletion` is called, THEN it returns true only after the file stops growing (not before)
- GIVEN a temp file that is not being modified, WHEN `waitForSyncCompletion` is called, THEN it returns true within `pollInterval * stableReadings` seconds
- GIVEN a temp file that is continuously being appended to, WHEN `waitForSyncCompletion` is called with `timeout: 3.0`, THEN it throws `SyncError.timeout`

**Tests:**
- `test_waitsForFileToStabilize`: Create a temp file, append data every 0.5s for 3s then stop. Assert `waitForSyncCompletion` returns true only after the file stops growing.
- `test_returnsImmediatelyForStableFile`: Create a temp file, don't modify it. Assert returns true within `pollInterval * stableReadings` seconds.
- `test_timeoutWhenFileNeverStabilizes`: Create a temp file, continuously append data. Call with `timeout: 3.0`. Assert throws `SyncError.timeout`.

**Verification:** The watcher holds back files that are still growing and only emits them once stable. Timeout behavior is tested. Integration with the watcher from Task 1.2 is verified — a file copied into the temp directory is only emitted after it stops being modified.

**Verification Command:** `swift test --filter SyncCompletionCheckerTests`

**Do NOT:**
- Hardcode the poll interval or stability threshold — make them configurable via init parameters so they can be tuned later without code changes
- Block the FSEvents callback while waiting for sync — each file's sync wait must be independent

**Scope Boundaries:**
- This task implements sync completion detection and integrates it with the watcher
- Pre-existing file filtering belongs to Task 1.4
- Sleep/wake handling belongs to Task 1.5

**Execution Notes:**
