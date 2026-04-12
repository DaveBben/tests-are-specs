# Worked Example: Notification Unsubscribe Links

A complete plan for a small feature, showing every section at the right level of detail
and the new template structure (executor-facing content first, requirements appendix last).

## Contents

- [What We Are Building](#what-we-are-building)
- [Why This Exists](#why-this-exists)
- [Scope](#scope) — In, Out, Constraints
- [Downstream Impact](#downstream-impact)
- [Risks & Rollback](#risks--rollback)
- [Implementation Tasks](#implementation-tasks)
  - [Task 0: Define Contracts & Interfaces](#task-0-define-contracts--interfaces)
  - [Task 1: Add Preference Repository and Token Validation](#task-1-add-preference-repository-and-token-validation)
  - [Task 2: Add Preference API Endpoints](#task-2-add-preference-api-endpoints)
  - [Task 3: Add Unsubscribe Landing Page](#task-3-add-unsubscribe-landing-page)
  - [Task 4: Add Unsubscribe Links to Email Footer](#task-4-add-unsubscribe-links-to-email-footer)
- [Critical Reminders](#critical-reminders-for-executor)
- [Appendix: Requirements Detail](#appendix-requirements-detail)
  - [Technical Context](#technical-context)
  - [Edge Cases](#edge-cases)
  - [Success Criteria](#success-criteria)
  - [Dependencies & Assumptions](#dependencies--assumptions)
  - [Key Decisions](#key-decisions)
  - [Open Questions](#open-questions)

---

```markdown
# Notification Unsubscribe Links Plan

**Date**: 2026-03-15
**Status**: Approved
**Plan Size**: Small
**Author**: Dave
**Repository**: notification-service
**Project Spec**: SPEC.md

---

## What We Are Building

Users will get unsubscribe links in their marketing email footers that let them opt out of
specific notification categories. Clicking a link takes them to a landing page where they
can see and toggle their preferences without needing to log in.

---

## Why This Exists

Users who receive marketing emails have no way to unsubscribe from individual notification
categories. Support tickets citing "too many emails" are the #1 complaint in Q1, and 12%
of users mark emails as spam rather than unsubscribing, which hurts email deliverability.

---

## Scope

### In
- Per-category unsubscribe links in email footers
- Landing page that shows the user's current preferences and lets them toggle categories
- Unsubscribe action works without requiring login

### Out (explicitly)
- Notification scheduling / quiet hours — separate feature planned for Q3
- In-app notification preferences UI — already tracked in issue #042
- Email template redesign — only the footer changes, not the full template
- Notification history / inbox [discussed during planning — deferred: separate feature #018]
- Resubscribe flow from the landing page [discussed — V1 only handles unsubscribe; resubscribe requires login via full preferences UI]

### Constraints (what must NOT change)
- `GET /preferences` response shape — mobile app v3.2+ parses this directly; a schema break requires a coordinated mobile release
- Existing `user_settings` table columns — owned by the settings team; we may only add new columns
- Email footer layout and styling — only the unsubscribe link content changes, not the template structure

---

## Downstream Impact

**Internal consumers**
- `src/email/send.py` — reads preference data on every email send; any preference schema change affects filtering logic
- `src/api/routes/settings.py` — shares the `user_settings` model; JSONB column addition is additive and will not break it

**External consumers**
- Mobile app v3.2+ — caches the GET /preferences response for 24h; preference changes will not be immediately visible to cached clients (acceptable, documented in Out)
- Email delivery service — receives dynamic footer content per recipient; already supports this via template variables

**Implicit contracts**
- Callers assume `enabled: true` is the default for any new notification category — must be preserved in `get_preferences()` when a category has no saved record

---

## Risks & Rollback

**Risks**
- **Token replay**: A valid unsubscribe token intercepted from a forwarded email could be used by a third party to change someone else's preferences — Likelihood: Low, Impact: Medium (mitigated by 30-day expiry and user-ID binding)
- **JSONB migration lock**: Adding `notification_preferences` column to `user_settings` on Postgres < 12 requires a table lock — Likelihood: Low (we run Postgres 15), Impact: High if it occurs

**Rollback Plan**
Deploy previous release tag. The JSONB column addition is backwards-compatible with prior code (column is nullable). If email deliverability is affected, revert `src/email/footer.py` independently via cherry-pick — it has no dependencies on the other tasks.

---

## Implementation Tasks

### Task 0: Define Contracts & Interfaces

**Implementer:** AI

**Covers:** Foundational — enables all tasks

**Relevant Files:**
- `src/types/notification_preferences.ts` <- create

**Context to Read First:**
- `src/types/user.ts:1` — existing User type that preferences will extend
- `src/api/middleware/auth.ts:34` — existing token shape pattern to align with

**Steps:**

1. [ ] Define `NotificationCategory` enum: Account, Billing, Marketing, ProductUpdates
2. [ ] Define `PreferenceResponse` type: `{ category: NotificationCategory, enabled: boolean }[]`
3. [ ] Define `UnsubscribeToken` type: `{ userId: string, category: NotificationCategory, expiresAt: Date }`
4. [ ] Define `GET /preferences` response shape and `POST /preferences` request shape
5. [ ] Verify types compile with no errors

**Acceptance Criteria:**

- GIVEN the contracts file, WHEN imported by any task, THEN all shared types are available and compile without errors
- GIVEN the type definitions, WHEN a developer reads them, THEN the API contract between frontend and backend is unambiguous

**Verification:** Types compile with no errors. All shared types are importable. No runtime behavior — contracts only.

**Verification Command:** `tsc --noEmit`

**Do NOT:**
- Implement token signing or validation logic — that belongs to Task 1
- Add database models or ORM code — that belongs to Task 1
- Include any UI or template code — that belongs to Task 3

**Scope Boundaries:**
- This task's scope is limited to defining shared contracts, types, and interfaces
- Token signing and validation logic belongs to Task 1
- Database models belong to Task 1
- UI belongs to Task 3

---

### Task 1: Add Preference Repository and Token Validation

**Implementer:** AI

**Covers:** AC-01.4 (works without login), Edge: expired token, Edge: tampered token

**Relevant Files:**
- `src/models/notification_preferences.py` <- create
- `src/services/unsubscribe_token.py` <- create
- `tests/models/test_notification_preferences.py` <- create
- `tests/services/test_unsubscribe_token.py` <- create

**Context to Read First:**
- `src/types/notification_preferences.ts` — contracts from Task 0
- `src/models/user_settings.py:23` — `UserSettings` model class to extend with JSONB column
- `src/services/crypto.py:42` — existing `hmac_sign(payload, secret)` function — reuse for token signing, do not reimplement HMAC

**Steps:**

1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**

- GIVEN a user with no preferences saved, WHEN `get_preferences(user_id)` is called, THEN all 4 categories are returned with `enabled: true` (default)
- GIVEN a user, WHEN `update_preference(user_id, "Marketing", false)` is called, THEN only the Marketing preference changes; other categories are unchanged
- GIVEN a valid user ID and category, WHEN `generate_token(user_id, category)` is called, THEN an HMAC-signed token is returned that decodes back to the correct user and category
- GIVEN a token older than 30 days, WHEN `validate_token(token)` is called, THEN a `TokenExpiredError` is raised
- GIVEN a tampered token, WHEN `validate_token(token)` is called, THEN an `InvalidTokenError` is raised

**Verification:** All preference CRUD operations work with default and saved preferences. Token generation produces valid HMAC tokens. Expired and tampered tokens are correctly rejected. Tests pass.

**Verification Command:** `pytest tests/models/test_notification_preferences.py tests/services/test_unsubscribe_token.py -v`

**Do NOT:**
- Create API endpoints — that belongs to Task 2
- Modify email templates or footer — that belongs to Task 4
- Reimplement HMAC signing — reuse the existing `hmac_sign` function from `src/services/crypto.py`

**Scope Boundaries:**
- This task's scope is limited to the preference repository and token service
- API endpoints belong to Task 2
- Email template changes belong to Task 4

---

### Task 2: Add Preference API Endpoints

**Implementer:** AI

**Covers:** AC-01.1 (landing page loads), AC-01.2 (toggle and save), Edge: expired token, Edge: invalid token

**Relevant Files:**
- `src/api/routes/preferences.py` <- create
- `tests/api/routes/test_preferences.py` <- create

**Context to Read First:**
- `src/types/notification_preferences.ts` — contracts from Task 0
- `src/api/routes/settings.py:1` — existing route pattern to follow (middleware, error handling)
- `src/services/unsubscribe_token.py` — token validation from Task 1

**Steps:**

1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**

- GIVEN a valid unsubscribe token, WHEN `GET /preferences?token=<valid>` is called, THEN response is 200 with `PreferenceResponse[]` matching the user's saved preferences
- GIVEN an expired token, WHEN `GET /preferences?token=<expired>` is called, THEN response is 401 with `{ error: "token_expired", message: "Please log in to manage preferences" }`
- GIVEN an invalid/tampered token, WHEN called, THEN response is 401 with `{ error: "invalid_token" }`
- GIVEN a valid token, WHEN `POST /preferences` is called with `{ category: "Marketing", enabled: false }`, THEN preference is updated and response is 200 with updated preferences

**Verification:** Valid tokens return 200 with preferences. Expired tokens return 401 with user-friendly message. POST updates preferences and returns updated state. Tests pass.

**Verification Command:** `pytest tests/api/routes/test_preferences.py -v`

**Do NOT:**
- Reimplement preference storage — use the repository from Task 1
- Create landing page HTML — that belongs to Task 3
- Add authenticated preference management — out of scope per plan

**Scope Boundaries:**
- This task's scope is limited to the preference API endpoints
- Preference storage logic belongs to Task 1 (use the repository)
- Landing page HTML belongs to Task 3
- Authenticated (logged-in) preference management is out of scope per plan

---

### Task 3: Add Unsubscribe Landing Page

**Implementer:** AI

**Covers:** AC-01.1 (landing page loads with preferences), AC-01.2 (toggle and save), Edge: double-click, Edge: all categories off

**Relevant Files:**
- `src/templates/preferences/unsubscribe.html` <- create
- `src/static/js/preferences.js` <- create
- `tests/templates/test_unsubscribe_page.py` <- create

**Context to Read First:**
- `src/types/notification_preferences.ts` — contracts from Task 0
- `src/templates/base.html:1` — base template to extend
- `src/static/js/settings.js:88` — existing toggle pattern to follow for consistency

**Steps:**

1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**

- GIVEN a valid token URL, WHEN the landing page loads, THEN all 4 categories are shown with toggles reflecting current state, and the category from the token is highlighted
- GIVEN the landing page, WHEN the user toggles off a category and clicks Save, THEN a POST request is sent to the API and a confirmation message appears without page reload
- GIVEN a save request that fails (network error), WHEN the user clicks Save, THEN the toggle reverts to its previous state and an error toast appears within 3 seconds
- GIVEN a user clicks the same unsubscribe link twice, WHEN the page loads the second time, THEN the category is shown as already toggled off with no error
- GIVEN an expired token, WHEN the landing page loads, THEN a message is shown: "This link has expired. Please log in to manage your preferences." with a login link
- GIVEN all categories toggled off, WHEN the user saves, THEN a warning "You won't receive any emails" is shown but the save proceeds

**Verification:** Landing page loads with correct preference state. Toggling and saving works without page reload. Failed saves revert the toggle and show an error toast. Expired token shows a friendly message with login link. Tests pass.

**Verification Command:** `pytest tests/templates/test_unsubscribe_page.py -v`

**Do NOT:**
- Reimplement API endpoints — use the endpoints from Task 2
- Modify email footer — that belongs to Task 4
- Add resubscribe functionality — out of scope per plan
- Change the base template layout or styling

**Scope Boundaries:**
- This task's scope is limited to the landing page template and client-side JS
- API endpoints belong to Task 2 (use them, don't reimplement)
- Email footer changes belong to Task 4
- Resubscribe functionality is out of scope per plan

---

### Task 4: Add Unsubscribe Links to Email Footer

**Implementer:** AI

**Covers:** AC-01.3 (excluded from next send), AC-01.1 (footer link generates token)

**Relevant Files:**
- `src/email/footer.py` <- modify
- `src/email/send.py` <- modify
- `tests/email/test_footer.py` <- modify
- `tests/email/test_send.py` <- modify

**Context to Read First:**
- `src/types/notification_preferences.ts` — contracts from Task 0
- `src/email/footer.py:1` — current footer generation to extend
- `src/email/send.py:55` — current send logic to add preference filtering
- `src/services/unsubscribe_token.py` — token generation from Task 1

**Steps:**

1. [ ] Write failing tests based on the acceptance criteria below
2. [ ] Run tests to verify they fail (confirm RED state)
3. [ ] Write minimal implementation to make tests pass
4. [ ] Run tests to verify they pass (confirm GREEN state)

**Acceptance Criteria:**

- GIVEN a marketing email being generated, WHEN the footer is rendered, THEN it includes an unsubscribe link with a valid signed token for that user and the email's category
- GIVEN a user who has unsubscribed from "Product Updates", WHEN the next Product Updates email batch runs, THEN that user is excluded from the recipient list
- GIVEN a user subscribed to all categories, WHEN a Marketing email is sent, THEN the footer link says "Unsubscribe from Marketing emails" (not generic "unsubscribe")

**Verification:** Marketing emails include category-specific unsubscribe links with valid tokens. Unsubscribed users are excluded from the next email batch for that category. Tests pass.

**Verification Command:** `pytest tests/email/test_footer.py tests/email/test_send.py -v`

**Do NOT:**
- Change the email template layout or styling — only add the unsubscribe link content
- Modify the email sending infrastructure — only filter recipients and add footer links
- Add batch/digest logic — out of scope per plan

**Scope Boundaries:**
- This task's scope is limited to the email footer generation and recipient filtering
- Email template layout and styling must not change (see Constraints)
- Email sending infrastructure must not change — only filter recipients and add footer links
- Batch/digest logic is out of scope per plan

---

## Critical Reminders (for executor)

**Read this before dispatching any task.**

- **Must not change**: `GET /preferences` response shape (mobile clients depend on it); existing `user_settings` table columns (settings team owns them); email footer layout and styling
- **Highest risk**: JSONB migration column addition — verify Postgres version before running. On Postgres < 12, this requires a table lock.
- **Rollback**: Deploy previous release tag. JSONB column is nullable (backwards-compatible). Footer changes can be reverted independently via cherry-pick.
- **File boundaries**: Each task ONLY touches its declared Relevant Files. If a step requires touching a file not listed, STOP and report.

---

## Appendix: Requirements Detail

### Technical Context

- **Platform**: Python/Flask web app with Jinja2 templating
- **Email delivery**: SendGrid with per-recipient template variables in footers
- **Database**: PostgreSQL 15 with SQLAlchemy ORM; `user_settings` table uses JSONB for extensible config
- **Relevant systems**: Existing `user_settings` model, HMAC signing utility at `src/services/crypto.py`

### Edge Cases

- **User clicks unsubscribe link twice**: Second click loads the page with category already toggled off; no error, no duplicate action
- **Signed token is expired (> 30 days)**: Landing page shows a message asking the user to log in, with a link to the login page
- **User has no email address on file**: Cannot occur — unsubscribe links only appear in emails, which require an email address
- **All categories toggled off**: Allowed. User sees a warning "You won't receive any emails" but can proceed

### Success Criteria

1. Support tickets citing "too many emails" decrease by >= 30% within 60 days of launch
2. Spam report rate decreases from 12% to < 5% within 60 days
3. Zero reported cases of cross-category unsubscription

### Dependencies & Assumptions

**Dependencies**
- Email delivery service supports dynamic footer content per recipient
- Existing preference storage mechanism in the database

**Assumptions**
- Notification categories are stable (Account, Billing, Marketing, Product Updates) — if false: enum must be extensible, not hardcoded
- Unsubscribe links can securely identify the user without requiring login — if false: full auth flow required, landing page scope changes significantly

### Key Decisions

- **Token strategy**: Use HMAC-signed tokens with user ID + category + expiry embedded. JWT rejected because JWT payloads are base64-visible to email recipients — exposes internal user IDs.
- **Preference storage**: Extend `user_settings` with a JSONB `notification_preferences` column. New dedicated table rejected: always read/written alongside other user settings; a JOIN would add latency to every email send.
- **Frontend approach**: Server-rendered landing page (no SPA). The page is accessed by potentially unauthenticated users from email links — a full SPA bundle for a single toggle page is unnecessary.

#### Failed / Rejected Approaches

- **Redis for preference storage**: Explored using Redis as the preference store to reduce DB load. Rejected: preferences are user-settings data, not ephemeral state — they belong in the database alongside other settings. Redis would introduce a second source of truth and complicate consistency guarantees.
- **One-click unsubscribe (no confirmation page)**: Evaluated RFC 8058 style one-click handling. Rejected: users forward emails; a one-click link would unsubscribe the recipient unintentionally. The landing page provides a review step.

### Open Questions

None — all decisions resolved during planning.
```

This example demonstrates: executor-optimized structure (safety-critical sections before tasks),
Critical Reminders as the final pre-Appendix section, `Implementer:` labels per task, inline
`Covers:` per task, `Verification:` prose per task (what "done" looks like), `Do NOT:` anti-scope
per task (explicit prohibitions), `Scope Boundaries` in positive framing, `file:line` references
in Context to Read First, requirements detail moved to an Appendix, merged Out section (no separate
Clarification section), Failed/Rejected Approaches in Key Decisions, and specific measurable
success criteria.
