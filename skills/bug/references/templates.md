# Bug Artifact Templates

## plan.json

```json
{
  "date": "YYYY-MM-DD",
  "status": "Approved",
  "type": "bugfix",
  "featureSlug": "{slug}",
  "featureDescription": "{title — describes what the user sees, not the cause}",
  "whatWeAreBuilding": "[what symptom is resolved]",
  "whyThisExists": "[symptom, impact, severity]",
  "rootCause": "[one sentence root cause]",
  "scope": {
    "in": ["reproduction test", "minimal fix"],
    "out": ["..."],
    "constraints": ["..."]
  },
  "severity": "[Critical|High|Medium|Low]",
  "reproductionResult": "[RED|GREEN|ERROR]",
  "knownRisks": ["[from at-risk areas confirmed in Phase 3]"],
  "criticalReminders": ["..."],
  "totalTasks": "N",
  "repositories": ["."],
  "totalSlices": 1,
  "slices": [
    {
      "id": 1,
      "description": "[one-sentence fix description]",
      "files": ["src/path/a.ts", "tests/path/b.ts"]
    }
  ]
}
```

## task_{N}.json

Same schema as feature tasks — no bug-specific fields.

```json
{
  "id": "task_{N}",
  "slice": 1,
  "repository": ".",
  "title": "Task N: [Title]",
  "status": "PENDING",
  "implementer": "AI",
  "intent": "[Why this task exists — one sentence]",
  "files": ["src/path/to/file.ts"],
  "symbol": "functionName()",
  "reference": "src/existing/pattern.ts:42",
  "dependencyChain": ["src/routes/index.ts", "src/controllers/feature.ts"],
  "relevantFiles": [
    {"path": "src/path/to/file.ts", "action": "modify"}
  ],
  "blockedBy": [],
  "atRiskTests": [
    {
      "path": "tests/existing.test.ts",
      "symbol": "describe('existing')",
      "reason": "[why this test could regress from the fix]"
    }
  ],
  "doNot": ["[boundary]"],
  "acceptanceCriteria": [
    "GIVEN [precondition], WHEN [action], THEN [expected outcome]"
  ],
  "verificationCommand": "[single runnable test command]",
  "regressionCheck": "[command to run atRiskTests]",
  "scopeBoundaries": "[what this task owns] / [what others own]",
  "doneWhen": "[mechanically verifiable]"
}
```

**Field notes:**
- Same schema as feature tasks. No `testContext` or `implementationContext`.
- `reference`: single entry only — closest working pattern.
- `atRiskTests`: human-confirmed in Phase 3 of /bug.
- For the reproduction test task: include the draft repro-test path
  in `acceptanceCriteria` so the agent can use it as a starting point.
