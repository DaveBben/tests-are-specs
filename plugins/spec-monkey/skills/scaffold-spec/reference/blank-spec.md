---
schema_version: 1                # spec format version
id: SPEC-NNN                      # a stable id, e.g. SPEC-014
title: <short imperative title>
status: draft                    # leave as draft until it's reviewed
created: <YYYY-MM-DD>
standards: standards.md          # the repo constitution: standards.md | CLAUDE.md | AGENTS.md
---

# Spec: <title>

> **In one line:** <what you're building or changing, in a single sentence>

## 1. Goal
<!-- ONE measurable sentence. State the delta — "X moves from A to B", not "improve X". -->

## 2. Context & Background
<!-- What exists today, and why this is needed now. Ground the reader before the requirements. -->
- **Today:**
- **Why now:**

## 3. Requirements
<!-- What the system must do. One FR per behavior, each with testable acceptance criteria. -->

### FR-001: <name>
The system SHALL <required behavior>.

**Acceptance criteria**
<!-- AC:BEGIN -->
- [ ] #1 WHEN <event> THE SYSTEM SHALL <observable response>
<!-- AC:END -->

### Edge Cases
<!-- The boundaries and failures the requirements must cover — the stuff that's easy to forget. -->
-

## 4. Scope
**In scope**
-

**Out of scope**
- <item> — <why it's excluded>

## 5. Approach
<!-- The non-obvious path only — what an experienced engineer wouldn't already know. -->
- **Mirror:** <existing pattern / file to copy>
- **Ordering:** <what must happen before what>
- **Gotchas:** <the trap that will bite>

## 6. Files / Change Manifest
<!-- Every file you'll touch. mode: new | modify | delete | context (read-only). -->
| id | path | mode | symbol | why |
|----|------|------|--------|-----|
| F1 |  |  |  |  |

## 7. Verification
<!-- How you'll prove it works: the exact commands, and one concrete worked example. -->
**Commands**
```
<e.g. pytest tests/test_x.py -q>
```

**Worked case**
- **Given:** <real input / starting state>
- **When:** <action>
- **Then:** <exact expected output, with literal values>

<!--
Need more? This is the lean core. If your change has a data model, non-functional
requirements (performance/security), or measurable success metrics, pull those sections
from the `handling-specs` skill and add them here.
-->
