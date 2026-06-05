---
name: setup-with-claude
description: Use when setting up the Advanced AI Workflows four-tool integration (gstack + advanced-planning + superpowers + plannotator) in a project. Invoke when the user says "set up planning", "install advanced planning", "bootstrap the planning stack", "prepare this project for planning", "install gstack integration", or "wire up the four-tool flow". Also use when the user passes --uninstall (tear down meta-project artifacts) or --refresh (re-detect installed tools). This skill guides Claude through every step interactively — it is not a script, it is a set of instructions Claude reads and executes with the user present.
---

# Setup Advanced AI Workflows

This skill walks you — Claude — through installing and wiring the Advanced AI Workflows
four-tool integration into the current project. You execute each step interactively.
Before any destructive change (writing files, editing CLAUDE.md, modifying settings.json),
you ask the user for explicit confirmation using AskUserQuestion.

## Reference files

Before starting, be aware of these files in `references/` (relative to this SKILL.md):

- `install-gstack.md` — canonical install commands for gstack
- `install-advanced-planning.md` — canonical install commands for advanced-planning
- `install-superpowers.md` — canonical install commands for superpowers
- `install-plannotator.md` — canonical install commands for plannotator
- `claude-md-routing.md` — the routing block to insert into CLAUDE.md
- `settings-snippet.json` — the permissions and hook entry to merge into .claude/settings.json

Read the relevant reference file whenever you need the exact command text. Do not invent
flag names or paths — use what is in the reference files.

## Modes

This skill supports three modes. Detect which one applies from the user's message:

- **Default (no flag)**: Full install + wire flow. Follow all steps below.
- **`--uninstall`**: Remove meta-project artifacts only. Jump to the [--uninstall](#uninstall) section.
- **`--refresh`**: Re-detect installed tools and update `.claude/integrations.json`. Jump to the [--refresh](#refresh) section.

---

## Default mode: detect → install → wire → verify

### Step 1: Detect current install state

Check the project for each sub-package. Detection is path-based — look for the sentinel
file or directory that each tool installs. Do not run shell commands for this; read the
filesystem directly.

| Sub-package | Installed if... |
|---|---|
| **gstack** | `~/.claude/skills/gstack/` exists (global install — gstack is always global) |
| **advanced-planning** | `.claude/skills/phase-plan-creator/SKILL.md` exists in this project, OR `.advanced-plans/` exists at the project root |
| **superpowers** | `.claude/skills/brainstorming/SKILL.md` exists in this project, OR `~/.claude/skills/brainstorming/SKILL.md` exists globally |
| **plannotator** | `.claude/commands/plannotator-annotate.md` exists in this project |

On Windows, `~` resolves to `%USERPROFILE%` (e.g. `C:\Users\<name>`). Use `os.homedir()` or
the platform-appropriate equivalent when constructing paths. On macOS/Linux, `~` resolves
normally.

Report findings to the user in a table:

```
| Tool               | Status     | Location |
|--------------------|------------|----------|
| gstack             | installed  | ~/.claude/skills/gstack/ |
| advanced-planning  | MISSING    | — |
| superpowers        | installed  | .claude/skills/brainstorming/ |
| plannotator        | MISSING    | — |
```

If everything is installed, tell the user and ask if they want to skip to Step 5 (wire
routing) or Step 7 (verify only).

### Step 2: Install missing sub-packages

For each sub-package marked MISSING, read its install reference file (e.g.
`references/install-gstack.md`) and present the canonical install instructions to the user.

Then ask:

> "Would you like to install [tool name] now, or handle it manually and continue once it
> is installed? (install now / do it manually)"

Wait for the user's response before proceeding.

- If "install now": present the exact commands from the reference file for the user's
  platform (Windows/macOS/Linux). Tell the user to run the commands in a terminal outside
  this Claude Code session, then confirm when done. Do NOT attempt to run the install
  commands yourself — they involve git clone, bun, and plugin marketplace operations that
  may require user interaction.
- If "do it manually": note it and continue. The verification step (Step 7) will catch
  anything still missing.

Repeat for each missing sub-package. Install order: gstack (1st), advanced-planning (2nd),
superpowers (3rd), plannotator (4th, optional). Tell the user plannotator is optional —
the integration works without it.

After presenting install instructions for advanced-planning, note: "After installing
advanced-planning, you may also need to grant Claude permissions on `.advanced-plans/`.
Step 5 covers this."

### Step 3: Re-detect after user confirms installs

Once the user confirms that missing sub-packages have been installed (or skipped), repeat
the detection check from Step 1. Update the status table. If any required package is still
missing after the user chose "do it manually", note it prominently but continue — the
pipeline will still partially work.

### Step 4: Wire CLAUDE.md routing

Read `references/claude-md-routing.md` (the routing block bounded by
`<!-- aaw-routing:begin -->` and `<!-- aaw-routing:end -->` markers).

Check whether the project has a `CLAUDE.md` file.

**Case A — No CLAUDE.md:** Ask the user:

> "This project has no CLAUDE.md. May I create one and add the Advanced AI Workflows
> routing block? (yes / no)"

If yes: write `CLAUDE.md` with the routing block as its content. If no: skip this step.

**Case B — CLAUDE.md exists, no aaw-routing markers:** Check whether a section named
`## Advanced AI Workflows Routing` or the `<!-- aaw-routing:begin -->` marker is already
present. If absent:

> "I will append the Advanced AI Workflows routing block to your existing CLAUDE.md.
> The block will be added between `<!-- aaw-routing:begin -->` and `<!-- aaw-routing:end -->`
> markers so it can be removed cleanly later. Proceed? (yes / no)"

If yes: append the routing block (including both markers) to the end of the file.
If no: skip.

**Case C — CLAUDE.md exists, aaw-routing markers present:** Show the diff between
the current content inside the markers and the reference template. Ask:

> "The routing block is already present. Would you like to refresh it with the current
> template? (yes — replace / no — keep existing)"

If yes: replace only the content between the markers (inclusive of marker lines) with
the fresh template. If no: leave it as-is.

Never overwrite content outside the fenced markers. Never remove or reformat CLAUDE.md
content that belongs to other tools or the user.

### Step 5: Grant .advanced-plans/ permissions in .claude/settings.json

Read `references/settings-snippet.json`. Extract the `permissions.allow` array and the
`hooks.PostToolUse` array.

Check whether `.claude/settings.json` exists in the project.

**Case A — No settings.json:** Ask:

> "I need to create `.claude/settings.json` with permissions granting Claude read/edit/write
> access to `.advanced-plans/` (required for advanced-planning to persist plan artifacts),
> and the gstack auto-trigger hook. Create it now? (yes / no)"

If yes: write `.claude/settings.json` with the permissions and hook entry from the snippet.
If no: remind the user that advanced-planning will fail to write plan files without this.

**Case B — settings.json exists:** Show the user the four permission entries and the hook
entry that need to be added. Ask:

> "I need to merge these entries into your existing `.claude/settings.json`:
>
> Permissions to add (if not already present):
>   Write(.advanced-plans/**)
>   Edit(.advanced-plans/**)
>   MultiEdit(.advanced-plans/**)
>   Read(.advanced-plans/**)
>
> Hook to add (PostToolUse / Write matcher scoped to ~/.gstack/projects/):
>   [show the hook command from settings-snippet.json]
>
> May I merge these into your settings.json? (yes / no)"

If yes: merge following the merge instructions in the snippet:
- For `permissions.allow`: append only the entries not already present (no duplicates).
- For `hooks.PostToolUse`: if no `Write` matcher exists, append the full matcher entry.
  If a `Write` matcher already exists, add the hook to its `hooks` array rather than
  creating a duplicate matcher.

If no: note it and continue. Advanced-planning will prompt for permissions separately.

### Step 6: Install the gstack-to-plans glue skill

This meta-project's glue skill (`gstack-to-plans`) copies gstack design docs into the
project's `.advanced-plans/specs/` directory when invoked.

Check whether `.claude/skills/gstack-to-plans/SKILL.md` already exists in this project.

**Case A — Not installed:** Ask:

> "The gstack-to-plans glue skill is not installed in this project. It connects gstack
> design docs to advanced-planning. Install it now?
> (project-local at .claude/skills/gstack-to-plans/ / global at ~/.claude/skills/gstack-to-plans/ / skip)"

If project-local: copy the meta-project's `gstack-to-plans/SKILL.md` from wherever this
skill is installed (check `.claude/skills/gstack-to-plans/SKILL.md` in the meta-project
repo, or `~/.claude/skills/gstack-to-plans/SKILL.md`) to the active project's
`.claude/skills/gstack-to-plans/SKILL.md`.

If global: copy to `~/.claude/skills/gstack-to-plans/SKILL.md`.

If skip: note it. The user can invoke `/gstack-to-plans` only if the skill is installed.

**Case B — Already installed:** Note it and continue.

### Step 7: Write .claude/integrations.json

Write (or overwrite) `.claude/integrations.json` recording the current detection state.
This is a non-destructive write that the user does not need to gate — it is a bookkeeping
file. However, if the file already exists with different content, show the diff and ask:

> "`.claude/integrations.json` already exists. Overwrite with current detection state?
> (yes / no)"

Write this structure (fill in actual detected values):

```json
{
  "_comment": "Advanced AI Workflows — integration state. Updated by /setup-with-claude.",
  "generated_at": "<ISO timestamp>",
  "platform": "claude-code",
  "tools": {
    "gstack": {
      "installed": true,
      "install_path": "~/.claude/skills/gstack/",
      "notes": "Always global; gstack is not project-local"
    },
    "advanced-planning": {
      "installed": true,
      "install_path": ".claude/skills/phase-plan-creator/",
      "version": "<version from advanced-planning/VERSION file if readable, else 'unknown'>"
    },
    "superpowers": {
      "installed": true,
      "install_path": ".claude/skills/brainstorming/",
      "scope": "project-local"
    },
    "plannotator": {
      "installed": false,
      "notes": "Optional. Install if you want visual plan review."
    }
  },
  "glue": {
    "gstack-to-plans": {
      "installed": true,
      "install_path": ".claude/skills/gstack-to-plans/"
    }
  },
  "routing": {
    "claude_md_routing_block": true,
    "settings_json_permissions": true,
    "settings_json_hook": true
  }
}
```

Adjust each `installed` value to match the actual detection results from Steps 1 and 3.
Set `install_path` values to whichever path was actually found during detection.

### Step 8: Verify and report

Present a final status table to the user:

```
| Component                       | Status | Notes |
|---------------------------------|--------|-------|
| gstack                          | OK     | ~/.claude/skills/gstack/ |
| advanced-planning               | OK     | .claude/skills/phase-plan-creator/ |
| superpowers                     | OK     | .claude/skills/brainstorming/ |
| plannotator                     | SKIP   | optional; not installed |
| CLAUDE.md routing block         | OK     | appended to CLAUDE.md |
| .claude/settings.json perms     | OK     | 4 entries added |
| .claude/settings.json hook      | OK     | PostToolUse/Write matcher added |
| gstack-to-plans glue skill      | OK     | .claude/skills/gstack-to-plans/ |
| .claude/integrations.json       | OK     | written |
```

For any MISSING or SKIP item, print the relevant install command from the reference file
on one line.

Then print the quick-reference guide:

```
Setup complete. Here is what you can do now:

PLANNING (gstack — strategy + review)
  /office-hours        Describe what you are building; get strategic framing
  /plan-ceo-review     CEO-perspective review of a plan or design
  /plan-eng-review     Engineering review of architecture and test plan
  /codex               Independent second opinion on any design or code

ROUTING → EXECUTION (advanced-planning)
  /plan-and-phase      Explore codebase, then create a phase plan
  /new-phase           Create a phase plan directly (familiar codebase)
  /next-loop           Execute one bounded loop
  /next-loop --auto    Chain all loops in the current phase
  /run-gate            Evaluate phase outputs before advancing
  /next-phase          Gate review, then advance to next phase

TACTICAL (superpowers)
  brainstorming skill  Explore options mid-execution or when stuck
  writing-plans skill  Draft a structured implementation plan from a spec

GLUE
  /gstack-to-plans     Copy latest gstack design doc to .advanced-plans/specs/
                       (also fires automatically via the PostToolUse hook)

VISUAL (plannotator — if installed)
  Fires automatically on plan-mode entry/exit via hooks
  /plannotator-annotate  Annotate a plan file and send feedback back
```

> **Session restart required for the PostToolUse hook:** The PostToolUse hook is read by
> Claude Code at session startup. If `.claude/settings.json` was created or modified for
> the first time in this session, **restart Claude Code now** so the hook takes effect.
> Until you restart, the auto-trigger for `/gstack-to-plans` will not fire live.

---

## --uninstall

Remove all meta-project artifacts from the current project. This mode never touches
sub-package installs (gstack, advanced-planning, superpowers, plannotator remain
untouched).

**Artifacts removed by --uninstall:**
1. The fenced routing block in `CLAUDE.md` (between `<!-- aaw-routing:begin -->` and `<!-- aaw-routing:end -->`)
2. The `.claude/skills/gstack-to-plans/` directory (glue skill)
3. `.claude/integrations.json`
4. The four `.advanced-plans/**` permission entries added to `.claude/settings.json`
5. The PostToolUse Write hook entry added to `.claude/settings.json`

### Uninstall procedure

**Step U1: Check for fenced markers**

Read `CLAUDE.md`. Search for both `<!-- aaw-routing:begin -->` and `<!-- aaw-routing:end -->`.

If EITHER marker is absent, STOP. Do not modify `CLAUDE.md`. Print:

```
ERROR: aaw-routing markers not found in CLAUDE.md.

Cannot safely remove the routing block — the fenced markers that delimit it are
missing or incomplete. This usually means CLAUDE.md was edited manually after setup.

Manual recovery instructions:
1. Open CLAUDE.md in a text editor.
2. Find the "## Advanced AI Workflows Routing" section.
3. Delete everything from the start of that section to the end of the routing
   content (the routes, superpowers overrides, companion-detection reference,
   and closing instruction).
4. Save the file.

The other meta-project artifacts (glue skill, integrations.json, settings.json
additions) can still be removed by re-running /setup-with-claude --uninstall
after you have completed the manual CLAUDE.md cleanup.
```

Do not proceed to the remaining uninstall steps until the user has confirmed they have
fixed CLAUDE.md manually (or if they ask to skip the CLAUDE.md step and remove only
the other artifacts).

**Step U2: Confirm destructive removals**

Ask:

> "I will remove the following meta-project artifacts from this project:
>
> - CLAUDE.md routing block (between aaw-routing markers)
> - .claude/skills/gstack-to-plans/ (glue skill)
> - .claude/integrations.json
> - 4 .advanced-plans/** permission entries in .claude/settings.json
> - PostToolUse Write hook (gstack trigger) in .claude/settings.json
>
> Sub-package installs (gstack, advanced-planning, superpowers, plannotator) will NOT
> be touched. Proceed? (yes / no)"

If no: abort.

**Step U3: Remove the routing block from CLAUDE.md**

Delete the lines from `<!-- aaw-routing:begin -->` through `<!-- aaw-routing:end -->` inclusive.
Do not modify any other content in CLAUDE.md.

After removing the block, check whether the remaining content is empty or whitespace-only
(blank lines, spaces, tabs — nothing visible to the user):

- If CLAUDE.md is now **empty or whitespace-only**: delete the file entirely. Print:
  `"CLAUDE.md was empty after block removal — deleted."`
- If CLAUDE.md still has **non-whitespace content**: leave it in place. Print:
  `"CLAUDE.md has remaining content — kept."`

**Guard:** never delete CLAUDE.md unless the only remaining content is whitespace. If
there is any doubt (e.g. the content check is inconclusive), keep the file and inform
the user.

**Step U4: Remove the glue skill**

Delete `.claude/skills/gstack-to-plans/` and all its contents.

**Step U5: Remove integrations.json**

Delete `.claude/integrations.json` if it exists.

**Step U6: Remove settings.json entries**

Read `.claude/settings.json`. Remove:
- The four `.advanced-plans/**` permission entries from `permissions.allow`
- The PostToolUse Write hook entry whose command contains `aaw-hook`

Write the modified settings.json back. If removing these entries would leave the JSON
malformed or would remove the only entry in an array (leaving an empty array that
advanced-planning or another tool also uses), show the diff and ask the user to confirm
rather than writing blindly.

**Step U7: Check for globally-installed glue**

After removing the project-local glue, check whether any Advanced AI Workflows glue
components are installed globally in `~/.claude/`:

- `~/.claude/skills/setup-with-claude/` (the setup skill itself)
- `~/.claude/skills/gstack-to-plans/` (the global glue skill, if installed globally)

If EITHER path exists, ask the user:

> "I found the following globally-installed Advanced AI Workflows components in ~/.claude/:
>
> [list each found path]
>
> These affect ALL projects on this machine. Would you like to remove them?
> (yes — remove global components / no — keep them)"

If yes: delete each found global path and its contents.
If no: leave them in place and note that they remain active for other projects.

If neither path exists: note "No globally-installed glue found in ~/.claude/" and
continue to the report.

**Step U8: Report**

Print a confirmation:

```
Uninstall complete.

Removed (project-local):
  - CLAUDE.md routing block
  - .claude/skills/gstack-to-plans/
  - .claude/integrations.json
  - settings.json: 4 .advanced-plans/** permission entries
  - settings.json: PostToolUse gstack hook

Global components (~/.claude/):
  [removed: ~/.claude/skills/setup-with-claude/  (if removed)]
  [removed: ~/.claude/skills/gstack-to-plans/     (if removed)]
  [kept: no global components found / user chose to keep]

Not touched:
  - gstack (~/.claude/skills/gstack/)
  - advanced-planning (.claude/skills/...)
  - superpowers (.claude/skills/brainstorming/ or ~/.claude/skills/brainstorming/)
  - plannotator (.claude/commands/plannotator-annotate.md)

To reinstall: run /setup-with-claude
```

---

## --refresh

Re-detect installed tools, re-fetch the canonical `setup-with-claude` skill, re-run
each detected sub-package's installer to pick up upstream changes, and update
`.claude/integrations.json`. No changes to CLAUDE.md or settings.json.

Use `--refresh` after: updating a sub-package to a new version, pulling new meta-project
changes, or finding that a deployed copy has drifted from its source.

### Refresh procedure

**Step R1: Detect current state**

Run the same detection checks as Step 1 of the default flow. Build the status table.
Record which sub-packages are currently detected — only detected packages will be
re-installed in Step R3.

**Step R2: Re-fetch the canonical setup-with-claude skill**

This step updates the global `~/.claude/skills/setup-with-claude/SKILL.md` to the
latest version from the meta-project.

Present the following two methods to the user and ask which to use:

> **Method A — Local copy (recommended when the meta-project repo is cloned locally):**
> ```bash
> cp path/to/advanced-ai-workflows/.claude/skills/setup-with-claude/SKILL.md \
>    ~/.claude/skills/setup-with-claude/SKILL.md
> ```
> Replace `path/to/advanced-ai-workflows` with the actual clone path.
>
> **Method B — curl from GitHub (use when you do not have a local clone):**
> ```bash
> curl -fsSL https://raw.githubusercontent.com/MungoHarvey/advanced-ai-workflows/main/.claude/skills/setup-with-claude/SKILL.md \
>   -o ~/.claude/skills/setup-with-claude/SKILL.md
> ```
>
> "Which method would you like to use to refresh setup-with-claude?
> (A — local copy / B — curl / skip)"

Tell the user to run the command in a terminal outside this Claude Code session, then
confirm when done. Do NOT attempt to run the command yourself.

If the user chooses skip: note it and continue — the globally installed skill will remain
at its current version.

**Step R3: Re-run detected sub-package installers**

For each sub-package detected in Step R1, present the re-install command and ask the
user to run it. This picks up any upstream changes (new commands, updated agents, revised
settings snippets) without a full manual setup.

Sub-package re-install commands:

| Sub-package | Re-install command (macOS / Linux) | Re-install command (Windows PowerShell) |
|---|---|---|
| **advanced-planning** | `sh setup/claude-code/install.sh --project /path/to/your/project` | `.\setup\claude-code\install.ps1 -Project C:\path\to\your\project` |
| **gstack** | Follow `~/.claude/skills/gstack/INSTALL.md` for the update procedure | Same — check INSTALL.md |
| **superpowers** | `/plugin install superpowers@claude-plugins-official` (in Claude Code) | Same |
| **plannotator** | `bun install && bun run build` (in the plannotator directory) | Same |

For each detected sub-package, ask:

> "Would you like to re-run the [tool name] installer to pick up the latest version?
> (yes / skip)"

If yes: show the relevant install command from the table above (and cross-reference the
`references/install-[tool].md` reference file for the canonical command text).
Tell the user to run it in a terminal, then confirm when done.
If skip: note it — this sub-package will retain its current version.

**Step R4: Update integrations.json**

If `.claude/integrations.json` exists, show the diff between current content and the
new detection state. Ask:

> "I will update .claude/integrations.json to reflect current detection results.
> Proceed? (yes / no)"

If it does not exist, write it without asking (same structure as Step 7 above).

**Step R5: Report what changed**

Print a change report:

```
Refresh complete.

setup-with-claude skill:  [refreshed via Method A / refreshed via Method B / skipped]
advanced-planning:        [re-installed / skipped / not detected]
gstack:                   [re-installed / skipped / not detected]
superpowers:              [re-installed / skipped / not detected]
plannotator:              [re-installed / skipped / not detected]
integrations.json:        [updated / written (new) / no change]

Not modified: CLAUDE.md, .claude/settings.json
To re-run full setup: /setup-with-claude (no flags)
```

Fill in each line's status based on what actually happened in Steps R2–R4.

---

## Cross-platform notes

- **Windows**: `~` resolves to `%USERPROFILE%`. When constructing home-directory paths
  in detection or file writes, use `os.homedir()` or equivalent — do not assume `/home/`.
- **macOS / Linux**: `~` resolves normally. Paths use forward slashes.
- **WSL**: Treat as Linux. Windows paths are accessible via `/mnt/c/...` but the Claude
  Code install paths follow Linux conventions.

When reading detection paths, check both Windows and POSIX forms if the platform is
ambiguous.

---

## What this skill does NOT do

- It does not run shell commands autonomously. Install commands are presented to the user
  to run in their terminal.
- It does not modify sub-package files (gstack, advanced-planning, superpowers,
  plannotator). It only installs meta-project artifacts: the routing block, the glue skill,
  the settings.json entries, and integrations.json.
- It does not modify `~/.claude/` globally except when the user explicitly chooses global
  glue-skill install.
- It does not silently overwrite anything. Every write that touches existing content is
  gated by an AskUserQuestion.
