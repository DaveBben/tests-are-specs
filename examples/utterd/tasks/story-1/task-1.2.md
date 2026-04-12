# Task 1.2: Implement FSEvents-based directory monitoring

**Status**: Not Started
**Implementer**: AI
**Repository**: utterd
**Blocked By**: Task 1.1
**Covers**: AC: new .m4a file detected, AC: non-.m4a files ignored, AC: multiple files in succession

**Relevant Files:**
- `Sources/Utterd/Watcher/FSEventsWatcher.swift` <- modify
- `Tests/UtterdTests/Watcher/FSEventsWatcherTests.swift` <- create

**Context to Read First:**
- `Sources/Utterd/Watcher/FileSystemWatcher.swift` — protocol from Task 1.1
- `Sources/Utterd/Watcher/WatcherEvent.swift` — event struct from Task 1.1
- Architecture doc Section 2.2 — FSEvents design considerations

**Steps:**
1. [ ] Write failing tests based on acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**
- GIVEN a temp directory with the watcher started on it, WHEN a .m4a file is copied in, THEN `onFileDetected` fires within 5 seconds with the correct path
- GIVEN a temp directory with the watcher started, WHEN a .txt file is copied in, THEN `onFileDetected` does not fire within 2 seconds
- GIVEN a temp directory with the watcher started, WHEN two .m4a files are copied in rapid succession, THEN `onFileDetected` fires twice with both paths

**Tests:**
- `test_detectsNewM4AFile`: Create a temp directory, start the watcher on it, copy a .m4a file in, assert `onFileDetected` fires within 5 seconds with the correct path
- `test_ignoresNonM4AFiles`: Copy a .txt file into the watched directory, assert `onFileDetected` does not fire within 2 seconds
- `test_detectsMultipleFiles`: Copy two .m4a files in rapid succession, assert `onFileDetected` fires twice with both paths

**Verification:** Watcher detects new .m4a files in a temp directory and emits their paths. Non-.m4a files are ignored. Tests pass.

**Verification Command:** `swift test --filter WatcherTests`

**Do NOT:**
- Implement sync completion detection yet — that's Task 1.3. For now, emit immediately on detection.
- Filter out pre-existing files yet — that's Task 1.4
- Handle sleep/wake — that's Task 1.5

**Scope Boundaries:**
- This task implements basic FSEvents monitoring with .m4a filtering
- Sync completion detection belongs to Task 1.3
- Pre-existing file filtering belongs to Task 1.4
- Sleep/wake handling belongs to Task 1.5

**Execution Notes:**
