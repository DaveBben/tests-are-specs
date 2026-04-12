# Section-by-Section Guidance

Detailed guidance for each plan.md section — why it exists, common mistakes, and good/bad examples.

## Contents

- [What We Are Building](#what-we-are-building)
- [Why This Exists](#why-this-exists)
- [Scope — In](#scope--in)
- [Scope — Out (explicitly)](#scope--out-explicitly)
- [Scope — Constraints](#scope--constraints-what-must-not-change)
- [Downstream Impact](#downstream-impact)
- [Technical Context](#technical-context)
- [Domain-Specific Sections](#domain-specific-sections)
- [Edge Cases](#edge-cases)
- [Success Criteria](#success-criteria)
- [Dependencies & Assumptions](#dependencies--assumptions)
- [Risks & Rollback](#risks--rollback)
- [Open Questions](#open-questions)
- [Key Decisions](#key-decisions)
- [Failed / Rejected Approaches](#failed--rejected-approaches-subsection-of-key-decisions)
- [Verification Command (per task)](#verification-command-per-task)
- [Context to Read First](#context-to-read-first--fileline-references)
- [Covers: (per-task)](#covers-per-task--replaces-the-requirement-traceability-table)
- [Implementer Field (per-task)](#implementer-field-per-task)
- [Scope Boundaries (per-task)](#scope-boundaries-per-task)
- [Verification (per-task)](#verification-per-task)
- [Do NOT (per-task)](#do-not-per-task)
- [Critical Reminders](#critical-reminders-required--last-section-before-appendix)
- [Appendix: Requirements Detail](#appendix-requirements-detail)
- [Task 0: Define Contracts & Interfaces](#task-0-define-contracts--interfaces)
- [Individual Tasks (Task 1+)](#individual-tasks-task-1)

---

## What We Are Building
- 2-4 sentences maximum
- Must plainly spell out what the change delivers — what will exist or be different when done
- Written so a non-technical stakeholder can understand what they are getting
- No jargon, no architecture, no implementation details
- Bad: "Implement a React component tree with Redux state management for notification preferences"
- Good: "Users will get a settings page where they can turn each type of notification on or off
  for each channel (email, push, in-app) independently."
- Test: "Would a product manager who has never seen the codebase understand this?" If yes, it is
  at the right level

## Why This Exists
- 2-4 sentences maximum
- Must state the PROBLEM, not the SOLUTION
- Bad: "Build a notification preferences page with per-channel controls"
- Good: "Users are disengaging because they receive too many irrelevant notifications. Support
  tickets show 'too many emails' as the #1 complaint in Q1."
- If it mentions a technology, framework, or implementation detail, it belongs in Technical
  Context (if factual) or the task sections (if prescriptive)
- Test: "Could this 'why' justify a completely different solution?" If yes, it is properly
  solution-agnostic

## Scope — In
- Bullet list of what will be built or changed
- Each item should be concrete enough to verify ("did we build this?")
- Bad: "Notification management" (too vague — could mean anything)
- Good: "Preference controls for each notification category" (verifiable)

## Scope — Out (explicitly)
- As important as the In section — this prevents AI scope creep
- Include anything a reasonable person might assume is included but is not
- Include a brief reason when the exclusion is not obvious
- This section replaces the old "Out of Scope (Clarification)" section — items that came
  up during the interview and were deferred get an annotation: "[discussed during planning
  — deferred because ...]"
- Bad: (empty or missing — gives the AI infinite scope)
- Good: "Notification scheduling / quiet hours — separate feature planned for Q3"
- Good: "Notification history / inbox [discussed during planning — deferred: separate feature #018]"

## Scope — Constraints (what must NOT change)
- The hardest gate in the plan: things the implementing agent must not touch even if tempted
- Distinct from Out (which says "don't build X") — Constraints says "don't break Y that already exists"
- Include: API contracts other code depends on, database schemas, public interfaces, behavioral contracts
- The executing agent uses this section as a checklist: if a task would violate a constraint, it stops and asks
- Bad: (missing — agent decides for itself what is safe to change)
- Good: "GET /preferences response shape must not change — mobile clients depend on it"
- Good: "The `user_settings` table schema must not change — this is owned by the settings team"

## Downstream Impact
- Captures who is affected by this change beyond the immediate code being modified
- Three categories: internal consumers (code in this repo), external consumers (other services/clients), implicit contracts (assumed behaviors not enforced in types or tests)
- Produced by tracing callers during the interview's codebase exploration — not guessed
- Bad: (missing — the agent has no signal about blast radius)
- Bad: "May affect some callers" (vague — name them specifically)
- Good: "Internal: `src/email/send.py` reads preference data on every send — any schema change breaks this"
- Good: "External: Mobile app v3.2+ caches the preference response for 24h — changes are not immediately visible to cached clients"
- Good: "Implicit: Callers assume `enabled: true` is the default for new categories — this must be preserved"
- If there are no external consumers, say so explicitly: "External: None — this API is internal only"

## Technical Context
- The ONE section in the plan where technology names are allowed
- States what exists (platform, frameworks, relevant systems), not what to build
- Provides constraints that affect scope decisions (version requirements, API boundaries)
- Keep it factual and brief — 3-5 bullet points, not paragraphs
- Bad: "We will implement a SwiftUI view with an @Observable model that calls the REST API"
  (implementation plan — belongs in the task sections)
- Good: "Platform: iOS/SwiftUI. The app already has a settings screen using the NavigationStack
  pattern. The notification API is REST-based and returns JSON."
- Test: "Am I describing what exists, or what to build?" If the latter, it belongs in tasks
- This section is optional for plans where the technology context is obvious from the project

## Domain-Specific Sections
- Optional — only include when the domain has structured data the plan references
- Use tables for categories, types, or enumerations
- Keep it descriptive, not technical (no DDL, no schemas, no column types)
- Bad: SQL CREATE TABLE statements
- Good: "Notification categories: Account, Billing, Marketing, Product Updates. Each category
  has independent on/off controls per channel (email, push, in-app)."

## Edge Cases
- Each entry names the boundary condition and states the expected behavior
- Focus on scenarios the AI would get wrong silently if not told
- Include: empty states, missing data, network failures, duplicate actions, concurrent users,
  unsupported environments, permission boundaries
- Bad: "Handle errors gracefully" (not an edge case, not specific)
- Good: "User with no email set: Preferences page still loads; email column shows disabled
  toggle with tooltip 'Add an email address to enable email notifications'"
- Aim for 5-10 edge cases for a standard feature, fewer for bug fixes

## Success Criteria
- Every criterion must include a measurable number or threshold
- These are OUTCOMES, not OUTPUTS — they measure whether the change solved the problem
- Bad: "Notification preferences page is live" (output, not outcome)
- Good: "Support tickets citing 'too many emails' decrease by >= 30% within 60 days of launch"
- Include at least one criterion
- For bug fixes: "The bug no longer reproduces using the steps above" plus a regression metric

## Dependencies & Assumptions
- Dependencies: things the change needs that it does not control
- Assumptions: things assumed true that change the plan if false
- Making assumptions explicit prevents surprises during implementation
- Bad: (unstated assumption that users are always authenticated)
- Good: "Assumes users are authenticated to reach the preferences page (except the email
  unsubscribe flow, which must work for unauthenticated users)"

## Risks & Rollback
- Two required parts: (1) the riskiest parts of this change, (2) the rollback plan
- Risks: name specific things that could go wrong, not generic warnings
  - Bad: "This change is risky" (not actionable)
  - Good: "**Token replay**: A valid token intercepted from an email could be reused by a third party — Likelihood: Low, Impact: High"
- Rollback Plan: concrete steps, not "we'll figure it out"
  - Bad: "Rollback if needed" (not a plan)
  - Good: "Deploy previous release tag. The JSONB column addition is backwards-compatible — no migration reversal needed. If the email footer change causes deliverability issues, revert `src/email/footer.py` independently."
- For low-risk changes, still state the rollback: "Standard deploy rollback via git revert. No database changes."
- This section is the signal to the implementing agent to pause and raise concerns if they encounter something that matches a named risk

## Open Questions

**This is the most important section.** Open questions are blocking gates — implementation
cannot proceed until every question is resolved.

### Two Types of Open Questions

Open questions serve two purposes in a single plan:

| | Product/Scope Questions | Architecture/Code Questions |
|---|---|---|
| **Test** | "Would a different answer change the ACs or scope?" | "Would a different answer change the tasks or file paths?" |
| **Examples** | "Real-time or batched?", "Which user roles?", "Backwards compatible?" | "Repository pattern or direct queries?", "New table or extend existing?", "Redis or in-memory?" |
| **Surfaced by** | /task-decomposition during interview | /task-decomposition during codebase exploration |
| **Blocks** | Task structuring | Execution |

### Gate Mechanism

Unchecked `- [ ]` items in the Open Questions section are **hard blockers**:
- Unresolved product questions → tasks cannot be structured
- Unresolved architecture questions → execution cannot begin

The gate check is mechanical: any unchecked checkbox in Open Questions = blocked.

### Format

Each question uses this format so the human has space to record their decision:

```markdown
- [ ] [question requiring human decision]
  - Context: [why this matters and what depends on the answer]
  - Options considered: [list viable options if known]
  - Decision needed by: [milestone or date]
  - Decision:
  - Reasoning:
```

### Guidance

- Err on the side of MORE questions, not fewer
- Each question must include context and options so the human can decide without re-reading
  the entire plan
- Leave the Decision and Reasoning fields blank — these are for the human
- An empty Open Questions section usually means not enough thought was given to ambiguities

### Status Values

| Status | Meaning | Gate |
|---|---|---|
| `Draft` | Still being written, not yet reviewed | — |
| `Open Questions` | Content reviewed by user, but questions block next stage | Blocked |
| `Approved` | All questions resolved, user approved | Clear |
| `In Progress` | Actively being implemented | — |
| `Complete` | Change implemented and verified | — |

## Out of Scope (Clarification) — REMOVED
- This section is merged into Scope — Out (explicitly)
- Items that came up during planning and were deferred get an annotation in the Out section:
  "[discussed during planning — deferred because ...]"
- Do not create a separate Out of Scope (Clarification) section

## Key Decisions
- Records architecture and code decisions made during codebase exploration
- These are SETTLED decisions, not open questions — someone has already chosen and documented
  the reasoning
- Bad: "We need to decide whether to use Redis or Memcached" (this is an open question)
- Good: "Caching: Use Redis — the project already has a Redis instance for session storage,
  adding a second cache layer would increase ops burden without benefit"
- Include alternatives considered and why they were rejected — this prevents the implementing
  agent from second-guessing the decision

## Failed / Rejected Approaches (subsection of Key Decisions)
- Lives as `### Failed / Rejected Approaches` under the `## Key Decisions` section in the plan
- Distinct from Key Decisions: Key Decisions records what was chosen; Failed Approaches records what was explored and ruled out
- The primary value: prevents future agents or developers from re-exploring the same dead ends
- Only include if something was genuinely tried or seriously considered and rejected
- Each entry must name the approach, the specific reason it was rejected, and what to try instead
- Bad: (missing — future session explores the same rejected approach and wastes time)
- Bad: "We considered other approaches but this one was better" (not specific enough to prevent re-exploration)
- Good: "**Separate preferences table**: Explored creating a `notification_preferences` table with one row per user/category. Rejected: would require a JOIN on every email send (N+1 query per recipient). Use JSONB column on `user_settings` instead."
- Good: "**JWT tokens in email links**: Evaluated JWT for unsubscribe tokens. Rejected: JWT payload is base64-visible to email recipients — exposes internal user IDs. Use HMAC-signed opaque tokens instead."

## Verification Command (per task)
- A single, runnable command that definitively proves the task is complete
- The task is done when this command passes — not when the agent says it's done
- Must be runnable without modification: specific test file, not just "run tests"
- Bad: "Run the tests" (which tests? how?)
- Bad: "Verify the implementation works" (not a command)
- Good: `pytest tests/models/test_notification_preferences.py -v`
- Good: `tsc --noEmit && jest src/components/Toggle.test.tsx`
- Task 0 (contracts): use the compile/type-check command, not a test command

## Context to Read First — file:line references
- The agent reads these files before starting the task to understand patterns to follow or reuse
- Use `file:line` to point directly to the specific function, class, or pattern — not just the file
- The agent should reuse what exists at that location rather than reimplementing it
- Bad: "`src/services/crypto.py` — crypto utilities" (which part? do what with it?)
- Good: "`src/services/crypto.py:42` — existing `hmac_sign(payload, secret)` function — reuse this for token signing, do not reimplement HMAC"
- Always include the contracts file from Task 0 in every subsequent task's context

## Covers: (per-task — replaces the Requirement Traceability table)
- Each task declares which ACs and edge cases it implements via a `Covers:` line
- Written at the same time as the task — accurate by construction, not fabricated post-hoc
- Format: `**Covers:** AC-01.2, AC-01.4, Edge: expired token`
- Task 0 uses: `**Covers:** Foundational — enables all tasks`
- Bad: Separate traceability table filled after writing tasks (Claude fabricates this post-hoc)
- Good: Inline `Covers:` written with the task, listing every AC it satisfies
- If an AC cannot be mapped to any task's Covers:, create a task for it or explicitly note
  it as deferred in the Appendix Open Questions section

## Implementer Field (per-task)
- Every task includes `**Implementer:** AI | Human` directly after the task heading
- **AI** (default): Claude executes this task via `/execute`
- **Human**: The engineer implements this task manually; `/execute` pauses at this task
  and presents the task requirements, acceptance criteria, and relevant files to the user.
  Execution resumes only after the user confirms the task is complete.
- Existing plans without the Implementer field remain valid — all tasks are treated as AI
- Default to `AI` unless the task requires human judgment, credentials, or manual steps
  that cannot be automated

## Scope Boundaries (per-task)
- Uses positive framing, which LLMs follow more reliably than negative "Do NOT" instructions
- States what this task owns (positive) and where adjacent concerns live (reference)
- Bad: "Do NOT add preference validation logic" (negative instruction, often ignored)
- Good: "This task's scope is limited to CRUD operations on the preference repository.
  Preference validation belongs to Task 3."
- Always name the task that owns the excluded concern — this creates a verifiable scope graph
- Include one boundary per tempting adjacent concern the executor might drift into

## Verification (per-task)
- A prose description of what "done" looks like for this task
- More concrete than acceptance criteria — tells the executor exactly what to check
- The executor reads this AFTER completing the task to self-verify
- Bad: (missing — executor decides for itself when the task is done)
- Bad: "Tests pass" (too generic — which tests? what behavior is observable?)
- Good: "Module compiles. Watcher detects new .m4a files in a temp directory and
  emits their paths. Non-.m4a files are ignored. Tests pass."
- Good: "The orchestrator processes a sequence of 5 memos — 3 succeed, 1 fails
  transiently then succeeds on retry, 1 fails permanently. Four memos have status
  transcribed, one has status failed. No resources leaked."
- Think of it as: "if someone watched a demo of this task's output, what would they see?"

## Do NOT (per-task)
- Explicit anti-scope: what the implementer MUST avoid doing in this task
- Complements Scope Boundaries (which uses positive framing) with direct prohibitions
- Each item should reference which task owns the excluded work
- Bad: (missing — executor drifts into adjacent scope)
- Bad: "Don't do anything extra" (too vague to be actionable)
- Good: "Do NOT implement actual monitoring — that's Task 1.2"
- Good: "Do NOT hardcode the iCloud Voice Memos path — inject it so tests can use
  a temp directory"
- Good: "Do NOT add dependencies on the state tracker or transcription modules"
- Include 2-4 items per task, focused on the most tempting scope drift

## Critical Reminders (required — last section before Appendix)
- The most important section for executor reliability — exploits recency bias
- The executor reads the plan linearly. The last thing it reads should be the most
  critical constraints. Without this, constraints written early in the plan are in the
  "lost middle" by the time tasks are being executed.
- Mandatory content:
  - **Must not change**: restate the 2-3 most important Constraints verbatim (not a reference)
  - **Highest risk**: restate the single most dangerous Risk verbatim
  - **Rollback**: one-line summary of the rollback plan
  - **File boundaries**: standard reminder that each task only touches its Relevant Files
- Bad: (missing — constraints are only in Scope section, which is far from tasks in context)
- Bad: "See Constraints section above" (a reference doesn't help when the Constraints section is outside the context window)
- Good: Explicit verbatim restatements of the 2-3 most critical constraints and risks

## Appendix: Requirements Detail
- All requirements-detail sections live here, AFTER the tasks and Critical Reminders
- Why: the executor needs What/Why/Scope/Downstream/Risks/Tasks/Reminders; it does not
  need Success Criteria during code execution — those belong in the Appendix
- Sections in the Appendix: Technical Context, Domain-Specific, Edge Cases,
  Success Criteria, Dependencies & Assumptions, Key Decisions (+ Failed/Rejected Approaches),
  Open Questions
- Bug Fix and Small plans may abbreviate or skip Appendix sections per the Right-Sizing Guide
- The Appendix is still written — it provides the "why" for planning and review; it's
  just moved after the executor-facing content so it doesn't pollute execution context

## Task 0: Define Contracts & Interfaces
- MANDATORY — every plan's task section must start with Task 0
- Runs before all other tasks
- Defines shared boundaries: API shapes, type definitions, interface contracts, config schemas
- Does NOT follow the TDD cycle — verified by compilation/type checking
- Bad: Task 0 that implements business logic (that belongs in subsequent tasks)
- Bad: No Task 0 — agents invent their own interfaces and produce incompatible code
- Good: Task 0 that defines TypeScript interfaces, API request/response types, and shared
  constants that multiple tasks will import

## Individual Tasks (Task 1+)

### Title
- Should describe a complete, testable unit of work
- Bad: "Implement the feature" (too vague)
- Bad: "Write tests for preferences" (test-only — missing the GREEN half)
- Bad: "Add preference API endpoint and frontend toggle and migration" (too many "ands")
- Good: "Add GET /preferences endpoint returning user preferences as JSON"

### Blocked By
- Optional — only declare when a task genuinely cannot start until another completes
- In a well-ordered sequential plan, most dependencies are implicit (Task 3 runs after Task 2)
- Use Blocked By when a task depends on a non-adjacent earlier task (e.g., Task 5 depends on Task 2)
- **Ordering impact:** Tasks without `Blocked By` and with non-overlapping `Relevant Files`
  can be run in parallel by `/execute`

### Relevant Files
- List EVERY file the task will create or modify, including test files
- Use explicit paths: `src/api/routes/preferences.ts`, not "the preferences route file"
- Bad: "Update the relevant files" (which files?)
- Good: "`src/api/routes/preferences.ts` <- create"

### Context to Read First
- Files the agent should read BEFORE starting the task, with reasons
- Include the contracts from Task 0 in every task's context
- Bad: Just a list of file paths with no explanation
- Good: "`src/api/middleware/auth.ts` — understand the authentication middleware pattern
  this endpoint will use"

### Steps
- Always the same four TDD steps (except Task 0)
- Do not add extra steps — the acceptance criteria define the scope

### Acceptance Criteria
- Every AC uses GIVEN/WHEN/THEN format
- Should be specific enough that two different agents would write the same test
- Include failure-mode ACs, not just happy path
- Bad: "The endpoint returns preferences" (not testable)
- Good: "GIVEN an authenticated user with 3 preferences saved, WHEN GET /preferences is
  called, THEN response status is 200 and body contains a JSON array of 3 preference objects"

### Scope Boundaries
- Uses positive framing, names the owning task for excluded concerns
- Bad: "Do NOT add preference validation logic" (negative, often ignored)
- Good: "This task's scope is limited to CRUD operations on the preference repository.
  Preference validation belongs to Task 3."
