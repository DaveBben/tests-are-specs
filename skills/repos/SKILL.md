---
name: repos
effort: low
model: sonnet
argument-hint: "[add | list | remove | add <path> | remove <name>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
description: >
  Repository registry — add, list, and remove local repository paths with optional
  tags and descriptions. Stores repo metadata in
  ~/.claude/backlog-driven-development/repos.json so other skills (task-decomposition,
  import) can discover available repos without asking the user to type paths.
  Use /repos add to register a repo, /repos list to see all repos,
  /repos remove to deregister one.
---

# Repository Registry

> Manages a registry of local repository paths at
> `~/.claude/backlog-driven-development/repos.json`.
> Other skills read this registry instead of asking you to type paths.

This skill is intentionally simple — it is a named lookup table, nothing more.
It does not clone repos, sync state, or track branches. It stores the local path
where a repo lives on this machine so other skills can discover it.

---

## Storage Location

```
~/.claude/backlog-driven-development/repos.json
```

### Schema

```json
{
  "version": 1,
  "lastModified": "2026-04-11T14:30:00Z",
  "repos": [
    {
      "name": "utterd",
      "path": "/Users/dave/repos/utterd",
      "description": "macOS voice memo transcription daemon",
      "tags": ["personal", "swift"],
      "addedAt": "2026-04-11"
    }
  ]
}
```

**Fields:**
- `name` — short identifier used by other skills (e.g., `"utterd"`, `"api-server"`)
- `path` — absolute local path to the repo root
- `description` — optional one-line description of what the repo does
- `tags` — optional array of strings for filtering (e.g., `["work", "python"]`)
- `addedAt` — ISO date when the repo was registered

---

## Input Handling

If `$ARGUMENTS` were provided, classify them:

1. **`list`** or no arguments: Enter **List Mode**.
2. **`add`** with a path argument (e.g., `add /Users/dave/repos/myapp`):
   Pre-fill the path and enter **Add Mode**, skipping the path question.
3. **`add`** with no path: Enter **Add Mode** from the beginning.
4. **`remove`** with a name argument (e.g., `remove utterd`):
   Pre-fill the name and enter **Remove Mode**, skipping the selection step.
5. **`remove`** with no name: Enter **Remove Mode** from the beginning.
6. **Unrecognized input**: Show usage and enter **List Mode**.

**Usage hint (shown for unrecognized input):**
```
/repos            — list all registered repos
/repos add        — register a new repo
/repos add <path> — register repo at <path>
/repos remove     — remove a registered repo
```

---

## List Mode

1. Read `~/.claude/backlog-driven-development/repos.json`. If the file does not
   exist, display:
   > "No repos registered yet. Run `/repos add` to register your first repo."
   Stop.

2. If the `repos` array is empty, display the same message.

3. Otherwise, display:

```
## Registered Repositories ({N} total)

| Name | Path | Description | Tags |
|------|------|-------------|------|
| {name} | {path} | {description or "—"} | {tags joined by ", " or "—"} |
...
```

Include a hint at the bottom:
> "Run `/repos add` to register a repo or `/repos remove` to deregister one."

Stop after displaying.

---

## Add Mode

### Step 1: Get the Path

If a path was pre-filled from `$ARGUMENTS`, skip this question.

Otherwise ask:
> "What is the absolute path to the repository? (e.g., `/Users/you/repos/myapp`)"

### Step 2: Validate the Path

Check that the path exists and is a directory:

```bash
ls "{path}"
```

If the directory does not exist:
> "That path doesn't exist on this machine: `{path}`
>
> Check the path and try again, or clone the repo first."
Stop.

Check whether the directory is a git repo:
```bash
ls "{path}/.git"
```

If `.git` is not present, warn but do not block:
> "Note: `{path}` doesn't appear to be a git repository (no `.git` directory found).
> Registering it anyway — you can still use it with this pipeline."

### Step 3: Check for Duplicate Path

Read `repos.json` (if it exists). If any existing entry has the same `path`:
> "This path is already registered as `{existing_name}`.
>
> Would you like to update its metadata instead?"

If yes, enter update flow (skip to Step 6, pre-filling existing values).
If no, stop.

### Step 4: Get the Name

Suggest a name derived from the directory basename (e.g., path `/Users/dave/repos/api-server` → suggested name `api-server`).

Ask:
> "What should this repo be called? (suggested: `{basename}`)"

If the user presses enter or confirms the suggestion, use the basename.

Check for duplicate names in existing repos. If the name is already taken:
> "The name `{name}` is already in use by `{existing_path}`. Choose a different name."
Re-ask.

### Step 5: Get Optional Metadata

Ask for a description in one question (combine description + tags to avoid extra turns):
> "Optional: add a description and/or tags for this repo.
>
> Description (one line, or skip): "

After the description, ask:
> "Tags (comma-separated, e.g., `work, python` — or skip): "

If the user skips either, use `null` for description and `[]` for tags.

### Step 6: Write the Registry

Ensure the directory exists:
```bash
mkdir -p ~/.claude/backlog-driven-development
```

Read `repos.json` (or create it if absent with the empty scaffold):
```json
{
  "version": 1,
  "lastModified": "",
  "repos": []
}
```

Append the new entry:
```json
{
  "name": "{name}",
  "path": "{path}",
  "description": "{description or null}",
  "tags": ["{tag1}", "{tag2}"],
  "addedAt": "{today ISO date}"
}
```

Update `lastModified` to now. Write `repos.json` back.

### Step 7: Confirm

> "Registered `{name}` → `{path}`"
>
> If description was provided: "Description: {description}"
> If tags were provided: "Tags: {tags}"
>
> "This repo is now available to `/task-decomposition` and `/import`."

---

## Remove Mode

### Step 1: Select the Repo

Read `repos.json`. If the file doesn't exist or is empty:
> "No repos registered. Nothing to remove."
Stop.

If a name was pre-filled from `$ARGUMENTS`, verify it exists in the registry:
- If found, skip to Step 2.
- If not found:
  > "No repo named `{name}` found in the registry.
  >
  > Run `/repos list` to see registered repos."
  Stop.

If no name was pre-filled, list the registered repos and ask which to remove:
> "Which repo would you like to remove?
>
> {numbered list of name — path pairs}"

### Step 2: Confirm Removal

Use AskUserQuestion to confirm:
> "Remove `{name}` (`{path}`) from the registry?
>
> This only removes the registration — it does not delete any files on disk.
>
> Type 'confirm' to proceed."

If the user does not confirm, stop without making changes.

### Step 3: Execute Removal

Remove the entry from the `repos` array in `repos.json`.
Update `lastModified`. Write `repos.json` back.

### Step 4: Confirm

> "Removed `{name}` from the registry. The files at `{path}` are untouched."

---

## How Other Skills Use This Registry

Skills that need repo paths read `repos.json` directly:

```
~/.claude/backlog-driven-development/repos.json
```

**`/task-decomposition` Phase 0b** — instead of asking "which repos are involved?",
it reads the registry, presents the registered repos, and asks the user to select
which apply to the current story. Unregistered repos can still be added ad-hoc.

**`/import`** — reads the registry to suggest which repos a Jira story likely
touches, based on the story's content and the repo descriptions/tags.

If the registry is empty, skills fall back to asking the user for paths directly
(same behavior as before this skill existed).
