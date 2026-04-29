# Common Anti-Patterns in Bug Reports

When you notice any of these during the conversation, name the anti-pattern
explicitly and help the user fix it:

| Anti-Pattern | Signal | Response |
|---|---|---|
| Diagnosis as title | "Race condition in save handler" | Reframe as observable symptom |
| Vague reproduction | "It just breaks sometimes" | Ask for specific steps and conditions |
| Missing environment | No OS/version/build info | Ask which environment they observed it in |
| Expected = "it works" | "Expected: it should work correctly" | Ask what "correctly" looks like specifically |
| Actual = "it's broken" | "Actual: it doesn't work" | Ask what specifically they see/experience |
| Solution in symptom | "Fix: invalidate the cache after save" | Remove — solutions belong in the plan |
| Multiple bugs in one | "Also, there's another issue..." | Split into separate bug investigations |
| Inflated severity | Cosmetic issue rated as Critical | Calibrate using the severity table |
| No evidence | No screenshots, logs, or error messages | Ask if they can reproduce and capture evidence |
