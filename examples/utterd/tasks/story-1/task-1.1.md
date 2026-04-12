# Task 1.1: Set up the watcher module with its public interface

**Status**: Not Started
**Implementer**: AI
**Repository**: utterd
**Blocked By**: Story 0 complete
**Covers**: Foundational — enables Tasks 1.2-1.7

**Relevant Files:**
- `Sources/Utterd/Watcher/FileSystemWatcher.swift` <- create
- `Sources/Utterd/Watcher/WatcherEvent.swift` <- create

**Context to Read First:**
- Architecture doc Section 2.2 — File System Watcher detail and design decisions

**Steps:**
1. [ ] Create `WatcherEvent` struct with `filePath: URL`, `detectedAt: Date`, and `fileSize: Int64`
2. [ ] Create `FileSystemWatcher` protocol with `startMonitoring() throws`, `stopMonitoring()`, and `var onFileDetected: ((WatcherEvent) -> Void)? { get set }`
3. [ ] Create `FSEventsWatcher: FileSystemWatcher` — stub implementation, all methods `fatalError("not implemented")`
4. [ ] Verify the module compiles

**Acceptance Criteria:**
- GIVEN the Watcher module, WHEN imported from another module, THEN `FileSystemWatcher`, `FSEventsWatcher`, and `WatcherEvent` are accessible
- GIVEN the `FSEventsWatcher` initializer, WHEN called with `init(directory: URL)`, THEN it accepts an injected directory path (not hardcoded)
- GIVEN the module, WHEN compiled, THEN no errors or warnings

**Verification:** Module compiles. Protocol and event struct are importable from other modules. No runtime behavior.

**Verification Command:** `swift build`

**Do NOT:**
- Implement actual file monitoring — that's Task 1.2
- Hardcode the iCloud Voice Memos path — inject it via init so tests can use a temp directory
- Add dependencies on the state tracker or transcription modules

**Scope Boundaries:**
- This task defines the public interface for the watcher module only
- Monitoring implementation belongs to Task 1.2
- Sync completion detection belongs to Task 1.3

**Execution Notes:**
