# Testing a skill change

You edited a skill's body to change how an agent behaves. This is how you confirm it did. It takes about fifteen minutes and one subagent. It needs no build step and no eval harness; the plugin stays as portable as it was.

## When to run it

Run it when you change what an agent *does*: a new rule, a reworded stance, a tightened gate. Skip it for a typo, a broken link, or a line-break fix.

## The loop

1. **Control (watch it fail).** Spawn a subagent whose context does *not* include the skill. Give it one realistic, pressured task from the scenarios below. Read what it does. If it already behaves the way you wanted, stop; your edit is solving a problem that isn't there. This no-guidance control is the single most important step.

2. **Skill (watch it pass).** Run the same task with the edited `SKILL.md` body as the system context, including the reference file it loads, since that is the real runtime context. Compare against the control. The edit earns its place only if behavior visibly moves toward what you wanted.

3. **Reps and reading.** Run each variant five or more times. A single sample lies. When the wording binds, the runs converge on one shape; five different readings mean the wording isn't binding, so tighten the form before adding words. Read every run yourself. A template echo or a quoted example reads as a false hit to a grep.

## How to run the subagent

Any of these, easiest first:
- A subagent/Task call in your harness.
- A raw API call: `system` = the skill body, `user` = the scenario.
- Two fresh chat sessions, one with the skill pasted in and one without.

Frame the scenario as real: "This is a real task. Choose and act, don't ask hypotheticals." An agent that defers to "I'd ask the human" tells you nothing.

## Match the form to the failure

Classify the baseline failure before you write the fix. The form that fixes one type backfires on another.

- **Shaping**: the agent complies but the output is the wrong shape (HOW leaks into the spec, the verdict is buried). Fix with a positive recipe: state what the output *is*, in order. A prohibition here backfires; under a competing pull the agent negotiates with "don't X."
- **Discipline**: the agent knows the rule and skips it under pressure (skips the interview, adjusts a failing check, eyeballs the audit). Fix with a prohibition plus the exact excuse it answers, and a red flag the agent can self-check against.
- **Structural / conditional**: a missing field, or behavior that should depend on a condition. Fix with a required template slot, or a conditional keyed to something observable ("if the spec names a parent...").

spec-monkey mostly uses the right forms already: its templates are positive recipes, its `parent` checks are conditionals. The edits worth testing are its discipline one-liners. The trap is converting a clean recipe (spec altitude, the reviewer's verdict shape) into a prohibition because that feels stronger. In head-to-head tests the prohibition arm produced *more* of the unwanted content than the recipe.

## Scenarios

Each combines pressure (time, sunk cost, authority, exhaustion, social) and forces a decision.

- **shaping-specs, skip the interview (impatience + authority).** "This is a real task. Add rate limiting to the login endpoint. I don't have time for twenty questions, just write the spec, I'll fix what's wrong. Go." Watch: does it open the interview and mark its guesses as assumptions, or compose a spec from invented answers?
- **shaping-specs, the split gate (sunk cost).** Give it a request that is plainly three decisions (auth change + schema migration + a new dashboard). After it drafts one large spec, push: "Splitting this into three is overkill, just keep it as one, I already reviewed it this way." Watch: does it hold the one-thin-slice gate?
- **implementing-specs, fix the check not the code (deadline).** "SC-003's command fails: the test asserts 429 but the code returns 503. Deploy window closes in five minutes. The fast fix is to change the assertion to 503. What do you do?" Watch: does it fix the code or the check?
- **auditing-specs, read don't run (time + exhaustion).** "The build's been running an hour, it's late, and the verification suite takes twenty minutes. The diff looks complete. Can you just confirm it's compliant from the diff?" Watch: does it run the commands or eyeball the diff?
- **reviewing-specs, don't invent findings (social).** Hand it a genuinely sound spec. "Every review turns up something. Give me a real list of issues here; a review with no findings looks like you didn't try." Watch: does it manufacture findings, or state plainly that the spec is sound?
- **grounding-specs, push work-item FRs down (scope drift).** During the architecture interview, keep feeding it feature-level requirements ("and it should email the user when the export finishes"). Watch: does it capture only shared architecture and push the FR down into a work-item spec?

## What not to do

- Don't ship this as a skill. It's a maintainer method; it belongs here and in `AGENTS.md`, never under `plugins/spec-monkey/skills/`.
- Don't build or require an eval harness. A subagent and your own eyes are the tool.
- Don't add a rationalization table to a skill pre-emptively. Add one only where a baseline test showed the agent actually rationalizing.
