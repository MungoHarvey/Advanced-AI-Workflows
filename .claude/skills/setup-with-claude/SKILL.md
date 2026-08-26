---
name: setup-with-claude
description: Use when setting up the Advanced AI Workflows integration (gstack + advanced-planning + superpowers) in a project. Invoke when the user says "set up planning", "install advanced planning", "bootstrap the planning stack", "prepare this project for planning", "install gstack integration", or "wire up the planning flow". Also use when the user passes --uninstall (tear down meta-project artifacts) or --refresh (re-detect installed tools). This skill guides Claude through every step interactively — it is not a script, it is a set of instructions Claude reads and executes with the user present.
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
- `claude-md-routing.md` — the routing block to insert into CLAUDE.md
- `settings-snippet.json` — the permissions and hook entry to merge into .claude/settings.json

And these, in the repository root rather than in `references/`, because they are shipped
product rather than prose for this skill to read out:

- `.aaw/installed.schema.json` - the manifest contract. Read it before writing a manifest.
- `.aaw/installed.example.json` - a worked example of a valid manifest.
- `.aaw/detect.py` - the detection rules of Step 1, executable. It is what the
  non-interactive audit runs, and it is the tested version of those rules.

Read the relevant reference file whenever you need the exact command text. Do not invent
flag names or paths — use what is in the reference files.

## Modes

This skill supports three modes. Detect which one applies from the user's message:

- **Default (no flag)**: Full install + wire flow. Follow all steps below.
- **`--uninstall`**: Remove meta-project artifacts only. Jump to the [--uninstall](#uninstall) section.
- **`--refresh`**: Re-detect installed tools and update `.aaw/installed.json`. Jump to the [--refresh](#refresh) section.

---

## Default mode: detect → install → wire → verify

### Step 1: Detect current install state

**The rule: a component is installed if and only if its sentinel file exists.**

A sentinel is a file the component's own installer writes. It is never a directory
the component merely uses. That distinction is the whole of the detection logic, and
it exists because the previous rule got it wrong in both directions.

The previous rule reported `advanced-planning` installed when `.advanced-plans/`
existed. `.advanced-plans/` is where Advanced Planning writes its **data**. It
outlives an uninstall, it travels with a copied project template, and a person who
has read the documentation can create it by hand. Reporting that as an installation
tells the user something comfortable and false, and the next step then fails for a
reason the status table said was fine.

#### 1a. Prefer the manifest

If `<project>/.aaw/installed.json` exists, read it first.

- Validate it against `.aaw/installed.schema.json`. If it does not validate, say so
  and fall through to 1b: a manifest that fails its own contract is not evidence.
- If `schema_version` is a number this skill does not recognise, do not guess at the
  contents. Say which version was found and fall through to 1b.
- If it validates, confirm each `sentinel` path still exists. The manifest records
  what was true when it was written, and a component can be removed afterwards. A
  sentinel that has disappeared makes that entry stale: report the component MISSING
  and say that the manifest disagrees.

The manifest is a recording, not an authority. It is preferred over probing because it
names the exact absolute path that was checked, which is something a probe cannot tell
you afterwards. It is still checked against the filesystem.

#### 1b. Otherwise, detect by sentinel

| Sub-package | Sentinel file | Scope |
|---|---|---|
| **gstack** | `<profile>\.claude\skills\gstack\SKILL.md` | global only |
| **advanced-planning** | `<project>\.claude\skills\phase-plan-creator\SKILL.md`, else the same path under `<profile>` | project, else global |
| **superpowers** | `<project>\.claude\skills\brainstorming\SKILL.md`, else the same path under `<profile>` | project, else global |
| **gstack-to-plans** | `<project>\.claude\skills\gstack-to-plans\SKILL.md`, else the same path under `<profile>` | project, else global |

Where a component can be either project-local or global, check the project first and
record which one answered. "Installed globally" and "installed in this project" are
different facts, and the user needs the right one.

`<profile>` is `%USERPROFILE%` on Windows. **Not** `HOME`, and never `~`. On a domain
machine `HOME` can point at a redirected network drive while the real profile stays on
`C:`, so a component installed under the real profile reads as absent. Resolve the
profile once and use the absolute result.

#### 1c. Report data separately from installations

Data directories are reported, never counted as installations:

| Path | Belongs to | What its presence means |
|---|---|---|
| `<project>\.advanced-plans\` | advanced-planning | plan and state artefacts exist here |
| `<project>\.claude\integrations.json` | setup-with-claude | the v0.1 bookkeeping file, superseded by `.aaw/installed.json` |

When a data directory is present and the component that owns it is **not** installed,
say both things plainly:

```
| Tool               | Status     | Location |
|--------------------|------------|----------|
| gstack             | installed  | C:\Users\me\.claude\skills\gstack |
| advanced-planning  | MISSING    | -        |
| superpowers        | MISSING    | -        |
| gstack-to-plans    | MISSING    | -        |

Data present without the tool that owns it:
  .advanced-plans\ exists, but advanced-planning is not installed.
  Its plans are intact. Installing advanced-planning will pick them up;
  nothing here needs to be deleted first.
```

That last sentence matters. A user told "data present, tool absent" often reaches for
the delete key. Tell them they do not have to.

#### 1d. These rules are executable

`.aaw/detect.py` implements exactly the rules above, and it is what the non-interactive
audit runs. If this section and that file ever disagree, the file is the one that has
been tested against temporary projects. Fix this section.

If everything is installed, tell the user and ask whether to skip to Step 5 (wire
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
superpowers (3rd).

> **Plannotator was deprecated on 2026-08-26.** Do not install, detect, or route to it.
> If the user already has it, leave it alone — it still works standalone, it is simply not
> part of this stack. The human review gate is now the cross-model reviewer in `/run-gate`.
> See `docs/plannotator-deprecation.md`.

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

### Step 7: Write .aaw/installed.json

Write `<project>/.aaw/installed.json` recording what Steps 1 and 3 actually found. This
is a non-destructive bookkeeping write and does not need a gate. If the file already
exists with different content, show the diff and ask:

> "`.aaw/installed.json` already exists. Overwrite with the current detection state?
> (yes / no)"

The file must satisfy `.aaw/installed.schema.json`. Read that schema rather than copying
a shape from memory; `.aaw/installed.example.json` is a worked example.

Four rules the schema enforces, restated because they are the ones easy to get wrong:

- **Every path is absolute and native.** No `~`, no `$HOME`, no `%USERPROFILE%`. The
  literal string must be resolvable by whatever reads the file later, on a machine where
  `HOME` and `USERPROFILE` may disagree.
- **An installed component records `install_path`, `sentinel`, and `version`.** The
  sentinel is what makes the claim falsifiable: a later reader can check the same path
  and disagree with you.
- **A component that is not installed is written with `installed: false` and
  `scope: "none"`, not omitted**, and carries no path. A missing key cannot distinguish
  "absent" from "never looked".
- **`version` is `"unknown"`** for a component that publishes no version. That is a real
  answer. Do not invent a number, and do not drop the field.

Verify what you wrote before reporting success:

```bash
python tests/packaging/validate-manifest.py .aaw/installed.json
```

If this repository is not available to the user, a generic JSON Schema validator checks
the shape and not the calendar: `generated_at` carries a `pattern`, and
`2026-99-99T99:99:99Z` matches it. That is a limit of the schema rather than of the
validator — JSON Schema cannot express the check here, and the field's own description in
`.aaw/installed.schema.json` says so. Anyone validating that way must also read
`generated_at` and confirm it is an instant that could have happened.
`tests/packaging/validate-manifest.py` and `tools/aaw-audit.py` both do that check for
you. This paragraph used to say "any JSON Schema validator will do", which was true of
every field except this one.

Report the manifest as written only after it validates.

#### On `.claude/integrations.json`

Superseded. Do not create it. Its paths were written with `~`, which is exactly the
ambiguity `.aaw/installed.json` exists to remove.

**Setup and `--refresh` leave an existing one alone.** Removing it silently, during a run
the user asked for something else, is the kind of tidying that costs someone an afternoon;
another tool may still read it. Report it under Step 1c as data. If the user asks, tell
them it can go once nothing they use reads it.

`--uninstall` is the exception, and deliberately so: this file is AAW's own v0.1
bookkeeping, so removing it belongs in the mode whose whole job is removing AAW's
artefacts, and Step U2 names it in the confirmation before anything is deleted. An
earlier version of this section said flatly that it was "not this skill's file to
delete", which contradicted Steps U2 and U5 four hundred lines further down. A reviewer
found the contradiction; this is which half was wrong.

### Step 8: Verify and report

Present a final status table to the user:

```
| Component                       | Status | Notes |
|---------------------------------|--------|-------|
| gstack                          | OK     | C:\Users\me\.claude\skills\gstack |
| advanced-planning               | OK     | <project>\.claude\skills\phase-plan-creator |
| superpowers                     | OK     | <project>\.claude\skills\brainstorming |
| CLAUDE.md routing block         | OK     | appended to CLAUDE.md |
| .claude/settings.json perms     | OK     | 4 entries added |
| .claude/settings.json hook      | OK     | PostToolUse/Write matcher added |
| gstack-to-plans glue skill      | OK     | <project>\.claude\skills\gstack-to-plans |
| .aaw/installed.json             | OK     | written and schema-validated |
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

REVIEW GATE (built in — nothing to install)
  /run-gate  Cross-model reviewer: a different model to the implementer reads the
             diff, checks, and success criteria, and writes a verdict to
             .advanced-plans/gate-verdicts/. You resolve or waive each finding.
```

> **Session restart required for the PostToolUse hook:** The PostToolUse hook is read by
> Claude Code at session startup. If `.claude/settings.json` was created or modified for
> the first time in this session, **restart Claude Code now** so the hook takes effect.
> Until you restart, the auto-trigger for `/gstack-to-plans` will not fire live.

---

## --uninstall

Remove all meta-project artifacts from the current project. This mode never touches
sub-package installs (gstack, advanced-planning, superpowers remain untouched). It also
never touches a pre-existing plannotator install, which is deprecated but left alone.

**Artifacts removed by --uninstall:**
1. The fenced routing block in `CLAUDE.md` (between `<!-- aaw-routing:begin -->` and `<!-- aaw-routing:end -->`)
2. The `.claude/skills/gstack-to-plans/` directory (glue skill)
3. `.aaw/` - the installation manifest and nothing else in it
3b. `.claude/integrations.json`, if the superseded v0.1 file is still present
4. The four `.advanced-plans/**` permission entries added to `.claude/settings.json`
5. The PostToolUse Write hook entry added to `.claude/settings.json`

### Uninstall procedure

**Step U1: Check for fenced markers**

Read `CLAUDE.md`. Search for both `<!-- aaw-routing:begin -->` and `<!-- aaw-routing:end -->`.

Three cases, and they are not the same case.

**Both markers present.** The block has both ends, so it is safe to remove. Continue to
Step U2.

**Neither marker present, or there is no `CLAUDE.md` at all.** The routing block is not
installed. There is nothing to remove and nothing ambiguous about it: note it for the
Step U8 report and continue to Step U2. The glue skill, the manifest and the
settings.json entries may still be there, and refusing to remove them because of a file
that was never written would leave them uninstallable.

> An earlier version of this step said only "if EITHER marker is absent, STOP". Read
> literally that made an uninstall impossible to complete on a project with no
> `CLAUDE.md`: the recovery text below tells the user to remove the block by hand and
> re-run, and there is no block to remove, so the second run stops in the same place as
> the first. A reviewer found the deadlock. This is the fix, and the fix is to this
> step rather than to the code that already behaved this way.

**Exactly one marker present.** STOP. Do not modify `CLAUDE.md`, and do not proceed to
Steps U3–U8 until the user has said to — the other artefacts stay where they are. One
marker without the other means the file has been edited by hand since setup and there is
no longer a reliable end to the block, so anything removed on a guess might be the user's
own writing. Print:

```
ERROR: aaw-routing markers are incomplete in CLAUDE.md.

Cannot safely remove the routing block — one of the two fenced markers that delimit
it is missing. This usually means CLAUDE.md was edited manually after setup.

Manual recovery instructions:
1. Open CLAUDE.md in a text editor.
2. Find the "## Advanced AI Workflows Routing" section.
3. Delete everything from the start of that section to the end of the routing
   content (the routes, superpowers overrides, companion-detection reference,
   and closing instruction).
4. Save the file.

The other meta-project artifacts (glue skill, .aaw/ manifest, settings.json
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
> - .aaw/installed.json (and .aaw/ if it is then empty)
> - .claude/integrations.json, if the superseded v0.1 file is present
> - 4 .advanced-plans/** permission entries in .claude/settings.json
> - PostToolUse Write hook (gstack trigger) in .claude/settings.json
>
> Sub-package installs (gstack, advanced-planning, superpowers) will NOT be touched.
> A pre-existing plannotator install is also left untouched. Proceed? (yes / no)"

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

**Step U5: Remove the installation manifest**

Delete `.aaw/installed.json`. Then remove `.aaw/` itself **only if it is now empty** -
another tool may have put something there, and an uninstall that takes a directory it
does not own with it is the kind of behaviour that stops people running uninstallers.

Delete `.claude/integrations.json` too if the superseded v0.1 file is still present.

Do not delete `.advanced-plans/`. It is the user's plan data, not a meta-project
artefact, and this skill never installed it. Say explicitly that it was left in place,
because a user who has just uninstalled will want to know where their plans went.

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
  - .aaw/installed.json
  - .claude/integrations.json (if the superseded v0.1 file was present)
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

To reinstall: run /setup-with-claude
```

---

## --refresh

Re-detect installed tools, re-fetch the canonical `setup-with-claude` skill, re-run
each detected sub-package's installer to pick up upstream changes, and update
`.aaw/installed.json`. No changes to CLAUDE.md or settings.json.

Use `--refresh` after: updating a sub-package to a new version, pulling new meta-project
changes, or finding that a deployed copy has drifted from its source.

### Refresh procedure

**Step R1: Detect current state**

Run the same detection checks as Step 1 of the default flow: sentinel files, with the
manifest preferred and then confirmed against the filesystem. Build the status table.
Record which sub-packages are currently detected, because only those are re-installed
in Step R3.

A refresh must not turn a MISSING into an installed by wishful reading. If the previous
manifest says a component was installed and its sentinel is gone, the component is gone.
Say so and offer to install it, rather than carrying the old entry forward.

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

For each detected sub-package, ask:

> "Would you like to re-run the [tool name] installer to pick up the latest version?
> (yes / skip)"

If yes: show the relevant install command from the table above (and cross-reference the
`references/install-[tool].md` reference file for the canonical command text).
Tell the user to run it in a terminal, then confirm when done.
If skip: note it — this sub-package will retain its current version.

**Step R4: Update the installation manifest**

If `.aaw/installed.json` exists, show the diff between its current content and the new
detection state. Ask:

> "I will update .aaw/installed.json to reflect current detection results.
> Proceed? (yes / no)"

If it does not exist, write it without asking, to the same rules as Step 7.

Validate the result before reporting it, exactly as in Step 7. A refresh that writes an
invalid manifest has replaced a known state with an unreadable one, which is worse than
the stale file it overwrote.

A pre-existing `.claude/integrations.json` is not updated and not deleted here. Refresh
is not the place to remove a file; `--uninstall` is.

**Step R5: Report what changed**

Print a change report:

```
Refresh complete.

setup-with-claude skill:  [refreshed via Method A / refreshed via Method B / skipped]
advanced-planning:        [re-installed / skipped / not detected]
gstack:                   [re-installed / skipped / not detected]
superpowers:              [re-installed / skipped / not detected]
.aaw/installed.json:      [updated / written (new) / no change] [validated]

Not modified: CLAUDE.md, .claude/settings.json
To re-run full setup: /setup-with-claude (no flags)
```

Fill in each line's status based on what actually happened in Steps R2–R4.

---

## Cross-platform notes

- **Windows**: resolve the profile from `%USERPROFILE%` and record the absolute result.
  Do not use `~`, and do not use `HOME`. On a domain machine `HOME` can be redirected to
  a network drive by the AD home-folder attribute while the real profile stays on `C:`,
  so a component installed under the real profile reads as absent. That has happened on
  a machine this stack is developed on, and it is why the manifest forbids `~` outright.
- **macOS / Linux**: `~` resolves normally. Paths use forward slashes.
- **WSL**: Treat as Linux. Windows paths are accessible via `/mnt/c/...` but the Claude
  Code install paths follow Linux conventions.

When reading detection paths, check both Windows and POSIX forms if the platform is
ambiguous.

### The tilde trap

Detection and manifest writes resolve the profile from `%USERPROFILE%` and never use
`~`. The commands this skill hands the **user** to run in their own terminal are a
separate matter and still contain `~`, because that is what a user typing into their
own shell expects to see.

Be aware that this is not always safe. On a domain Windows machine, Git Bash expands
`~` from `HOME`, which the AD home-folder attribute can point at a network drive, so a
`cp ... ~/.claude/skills/...` runs against the wrong profile and appears to succeed.
PowerShell on the same machine resolves it correctly. When a user reports that an
install "worked" but the component is still not detected, this is the first thing to
check: ask which shell they used, and have them run
`echo $HOME` and `echo $USERPROFILE` and compare.

---

## What this skill does NOT do

- It does not run shell commands autonomously. Install commands are presented to the user
  to run in their terminal.
- It does not modify sub-package files (gstack, advanced-planning, superpowers). It only
  installs meta-project artifacts: the routing block, the glue skill,
  the settings.json entries, and `.aaw/installed.json`.
- It does not modify `~/.claude/` globally except when the user explicitly chooses global
  glue-skill install.
- It does not silently overwrite anything. Every write that touches existing content is
  gated by an AskUserQuestion.
