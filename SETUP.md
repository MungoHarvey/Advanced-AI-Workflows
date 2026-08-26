# Setup Guide

This guide walks you through installing the full Advanced AI Workflows stack: gstack, advanced-planning, and superpowers.

> **Changed 2026-08-26:** plannotator was deprecated and is no longer installed. v0.1 was a four-tool stack; from v0.2 the review gate is a cross-model reviewer built into `/run-gate`. See [docs/plannotator-deprecation.md](docs/plannotator-deprecation.md).

> **Claude Code only in v0.1.** This guide assumes Claude Code. The CLAUDE.md routing, `.claude/skills/` install paths, and `.claude/settings.json` permission grants are Claude Code-specific. Multi-runtime support is a v0.2+ ROADMAP item.
>
> **Current-head notice:** on `main` the documented `gstack-to-plans` source is still missing from the repository, so that head is not a verified fresh-install route. It is fixed on `feat/aaw-packaging-repair`, where the skill is tracked and `tests/packaging/test-fresh-clone.sh` verifies every documented install source against a fresh clone. For the v0.2 pilot see the [Herdr Windows operating guide](docs/herdr-windows-operations.md) and the [orchestration design](.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md).

Each tool can be installed independently — you only need the ones relevant to your workflow. Installing all four gives you the complete think → plan → review → execute → review pipeline.

---

## Version Compatibility Matrix

| Sub-package | Minimum version | Tested against | Notes |
|---|---|---|---|
| advanced-planning | ≥ v0.11.0 | v0.11.0 | v0.11.0 moved the runtime root to `.advanced-plans/`. Earlier versions used `plans/` and are not compatible with this meta-project. |
| gstack | ≥ v1.0.0 | current main | Requires `~/.claude/skills/gstack/` install path and the `~/.gstack/projects/` write convention. |
| superpowers | ≥ v1.0.0 | current main | Requires the `brainstorming` skill to support the user-preference override in CLAUDE.md (free-prose override syntax). |

---

## Prerequisites

| Requirement | Needed For | Install Guide |
|---|---|---|
| git | Cloning repositories | [git-scm.com](https://git-scm.com/) |
| Claude Code | Running the integrated flow | [claude.ai/code](https://claude.ai/code) |
| Node.js (any recent LTS) | PostToolUse hook script | [nodejs.org](https://nodejs.org/) |

---

## Automated Setup (Recommended)

Install the setup skill and tell Claude to walk you through setup:

```bash
mkdir -p ~/.claude/skills/setup-with-claude
curl -fsSL https://raw.githubusercontent.com/MungoHarvey/advanced-ai-workflows/main/.claude/skills/setup-with-claude/SKILL.md \
  -o ~/.claude/skills/setup-with-claude/SKILL.md
```

Then in any Claude Code session: *"Set up advanced AI workflows in this project."*

Claude will detect existing installs, offer to install missing sub-packages, wire the CLAUDE.md routing block, grant `.advanced-plans/` permissions in `.claude/settings.json`, install the `gstack-to-plans` glue skill, and write `.claude/integrations.json`.

For uninstall: *"Run setup-with-claude --uninstall in this project."*
For re-detection only: *"Run setup-with-claude --refresh in this project."*

---

## Manual Setup

### Step 1: Clone This Repository

```bash
git clone https://github.com/MungoHarvey/advanced-ai-workflows.git
cd advanced-ai-workflows
```

---

### Step 2: Install gstack

Follow the gstack install instructions at `~/.claude/skills/gstack/INSTALL.md` (or your distribution's README). After install, confirm you have access to gstack commands in Claude Code:

```
/office-hours
```

Claude should enter a gstack strategy session. The design doc will be written to `~/.gstack/projects/{slug}/{user}-{branch}-design-{datetime}.md`.

---

### Step 3: Install advanced-planning

Advanced Planning copies slash commands, skills, agent definitions, and schemas into your project's `.claude/` directory.

#### macOS / Linux

```bash
cd advanced-planning
sh setup/claude-code/install.sh --project /path/to/your/project
```

#### Windows PowerShell

```powershell
cd advanced-planning
.\setup\claude-code\install.ps1 -Project C:\path\to\your\project
```

#### Install Options

| Option | Description |
|---|---|
| `--global` / `-Global` | Install to `~/.claude/` so commands are available in every project |
| `--symlink` / `-Symlink` | Link to `core/skills/` instead of copying, so updates apply immediately |
| `--dry-run` / `-DryRun` | Preview what would be installed without writing any files |

#### Verify

Open Claude Code in your target project and run:

```
/plan-and-phase test planning system
```

Claude should enter read-only exploration mode, examine the codebase, and present findings before running the planning pipeline.

---

### Step 4: Install superpowers

#### Claude Code (Official Marketplace)

```
/plugin install superpowers@claude-plugins-official
```

#### Claude Code (via Plugin Marketplace)

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

#### Verify

Start a new Claude Code session and describe something you want to build. If superpowers is installed correctly, the brainstorming skill should activate automatically.

---

### Step 5: The review gate (nothing to install)

> **Plannotator was deprecated on 2026-08-26.** v0.1 installed it here as a Claude Code plugin for
> browser-based plan review. It is no longer part of the stack — there is nothing to install at this
> step. See [docs/plannotator-deprecation.md](docs/plannotator-deprecation.md) for the rationale and
> the migration path if you installed it previously.

The human review gate is now a **cross-model gate reviewer**, provided by advanced-planning's
`/run-gate`. It needs no separate install, no plugin, no Bun, and no browser.

What it does at each phase boundary:

1. Spawns a reviewer agent on a **different model from the one that implemented the work**.
2. Gives it the phase's changed paths, diff, check output, and the phase plan's success criteria.
3. Writes a structured verdict to `.advanced-plans/gate-verdicts/`.
4. Requires every finding to be resolved or **explicitly waived by you** before the phase advances.

**Prerequisite:** a second runtime must be configured for the reviewer to run on — Codex, OpenCode,
or Cursor alongside Claude Code. If only one provider is available, the gate falls back to
same-model review, which must be recorded as such in the verdict rather than silently accepted.

---

### Step 6: Grant `.advanced-plans/` Permissions

Advanced-planning and the `gstack-to-plans` glue skill need Claude read/edit/write access to `.advanced-plans/`. Add the following entries to your project's `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Write(.advanced-plans/**)",
      "Edit(.advanced-plans/**)",
      "MultiEdit(.advanced-plans/**)",
      "Read(.advanced-plans/**)"
    ]
  }
}
```

If `.claude/settings.json` already exists, append these four entries to the existing `permissions.allow` array. Do not duplicate entries that are already present.

The `setup-with-claude` skill does this step automatically when invoked — it asks for confirmation before writing.

#### Critical Gap 1: Permission failure mode

If `.advanced-plans/` permission entries are missing, advanced-planning commands will appear to succeed but silently fail to write state files (`loop-ready.json`, `loop-complete.json`, phase plans). The failure mode is confusing: Claude completes the planning dialogue but no files appear on disk.

**Diagnostic:** run `/plan-and-phase test` and check whether `.advanced-plans/phases/` is created. If not, check `.claude/settings.json` for the four permission entries above.

---

### Step 7: Wire CLAUDE.md Routing and Install the Glue Skill

The `setup-with-claude` skill handles both of these steps automatically. To do it manually:

#### CLAUDE.md routing block

Add the following to your project's `CLAUDE.md` (or create it if absent), between the fenced markers:

```markdown
<!-- aaw-routing:begin -->
## Advanced AI Workflows routing

**Ambiguous problem / strategy session:** invoke `/office-hours` (gstack). This is the front door for unclear scope, architecture decisions, or when a second opinion is needed before committing to an approach.

**Known scope, unfamiliar codebase:** invoke `/plan-and-phase` (advanced-planning). Pass the gstack design doc content as the description argument if one has been produced.

**Known scope, known codebase:** invoke `/new-phase` (advanced-planning). Pass the design doc content as the description argument if available.

**Stuck on options mid-execution / need ideation:** invoke the superpowers brainstorming skill.

**Need a plan drafted:** invoke the superpowers writing-plans skill.

**Second opinion on a plan or implementation:** invoke gstack `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, or `/codex`.

**After any gstack planning skill writes a design doc:** invoke `/gstack-to-plans` if it has not already fired. This copies the design doc from `~/.gstack/projects/{slug}/` to `.advanced-plans/specs/` and prints the next-step suggestion.

## Superpowers preference overrides

Save brainstorming output to: `.advanced-plans/specs/`
Save writing-plans output to: `.advanced-plans/specs/`
<!-- aaw-routing:end -->
```

#### Glue skill install

Copy `gstack-to-plans/SKILL.md` from the meta-project into the active project's `.claude/skills/gstack-to-plans/`:

```bash
mkdir -p .claude/skills/gstack-to-plans
cp path/to/advanced-ai-workflows/.claude/skills/gstack-to-plans/SKILL.md \
   .claude/skills/gstack-to-plans/SKILL.md
```

Or for a global install available in all projects:

```bash
mkdir -p ~/.claude/skills/gstack-to-plans
cp path/to/advanced-ai-workflows/.claude/skills/gstack-to-plans/SKILL.md \
   ~/.claude/skills/gstack-to-plans/SKILL.md
```

---

### Step 8: Add the PostToolUse Hook (Auto-trigger)

The auto-trigger hook surfaces `/gstack-to-plans` in Claude's next turn whenever a gstack design doc is written. Add the following to your project's `.claude/settings.json`, in the `hooks.PostToolUse` array:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "node -e \"const p = process.env.CLAUDE_TOOL_INPUT_PATH || ''; const h = require('os').homedir(); const prefix = h + '/.gstack/projects/'; if (p.startsWith(prefix)) { const f = require('path').basename(p); if (/-design-\\d/.test(f)) { console.log('[aaw-hook] gstack design doc written: ' + p); console.log('[aaw-hook] Suggestion: invoke /gstack-to-plans to archive this design doc into .advanced-plans/specs/'); } }\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

**Session restart required:** The PostToolUse hook registers at session startup. If you created or modified `.claude/settings.json` for the first time in this session, **restart Claude Code** before expecting the hook to fire live. Until you restart, the auto-trigger for `/gstack-to-plans` will not activate.

**Scope discipline:** this hook checks `CLAUDE_TOOL_INPUT_PATH` at runtime. It fires only when the written path starts with `~/.gstack/projects/` AND the filename matches the gstack design-doc pattern (`*-design-{datetime}.*`). Writes to any other path produce no output and exit 0 — the hook does not interfere with normal development.

**Windows note:** `~/.gstack/projects/` resolves to `%USERPROFILE%\.gstack\projects\`. The `node -e` command handles this via `os.homedir()`, which is cross-platform.

If the hook misfires or is disabled, the manual fallback still works: run `/gstack-to-plans` directly, or follow the CLAUDE.md closing instruction.

---

## Verify the Full Pipeline

With all three tools installed, the complete workflow chains together:

1. **Strategy session:** run `/office-hours` in Claude Code. Describe the problem. Gstack walks through a structured session and writes a design doc to `~/.gstack/projects/{slug}/`.

2. **Archive:** the auto-trigger hook surfaces `/gstack-to-plans`. Run it. Claude copies the design doc to `.advanced-plans/specs/` and prints the next-step suggestion.

3. **Phase planning:** run `/plan-and-phase` with the design doc as the description argument. Advanced-planning enters exploration mode, then calls `phase-plan-creator` to produce `.advanced-plans/phases/phase-1/plan.md`.

4. **Review:** read the phase plan and approve it, or send it back with changes. At the phase's end, `/run-gate` runs the cross-model reviewer and you resolve or waive each finding.

5. **Loop execution:** run `/next-loop`. The orchestrator prepares the first loop; the worker executes todos with targeted superpowers skill injection. Repeat with `/next-loop` or chain with `/next-loop --auto`.

6. **Gate:** run `/run-gate`. Gate agents evaluate success criteria. Advance with `/next-phase` on pass, or loop back on fail.

---

## Critical Gaps

### Critical Gap 1: Permission failure mode

If the four `.advanced-plans/**` entries are absent from `.claude/settings.json`, advanced-planning silently fails to write state files. The failure mode is confusing — Claude completes the planning dialogue but no files appear on disk.

**Diagnostic:** after running `/plan-and-phase`, check whether `.advanced-plans/phases/` was created. If not, verify the four permission entries in `.claude/settings.json`.

**Workaround:** run `setup-with-claude` to have Claude add the permissions automatically, or add the four entries manually as shown in Step 6 above.

### Critical Gap 2 (resolved): plannotator ExitPlanMode popup noise

**Resolved by deprecation on 2026-08-26.** Plannotator is no longer installed, so the hook no longer fires.

For the record: when plannotator was installed, its `ExitPlanMode` hook fired on every plan-mode exit — including short or incidental planning sequences, not just full phase-plan creation sessions, so the review UI opened more often than users expected. There was no workaround short of disabling the hook, which removed the automatic review integration entirely. The cross-model gate reviewer that replaced it runs once per phase boundary, on demand, and never opens a browser.

---

## Troubleshooting

### The gate reviewer runs on the same model as the implementer

The gate is only as good as its independence. If `/run-gate` reports a same-model review:

- Confirm a second runtime is installed and on `PATH` (`codex --version`, `opencode --version`, `cursor-agent --version`).
- Confirm the phase config names a reviewer distinct from the implementer.
- If only one provider is genuinely available, the verdict must say so. A same-model pass recorded as an independent one is worse than no gate.

### Global paths resolve to the wrong drive

On Windows, `HOME`, `HOMEDRIVE`, and `~` can point somewhere other than `%USERPROFILE%` — a redirected or mapped network home is common on managed machines. Tools then install to one root and look for themselves in another, reporting components as missing when they are present.

- Check for disagreement: compare `$env:USERPROFILE` with `$env:HOME` and `$HOME`.
- Resolve every global path from `USERPROFILE`, never from `HOME`/`HOMEDRIVE`/`~`.
- If they disagree, pin them for the session before launching agents:
  `$env:HOME=$env:USERPROFILE; $env:HOMEDRIVE="C:"; $env:HOMEPATH=$env:USERPROFILE.Substring(2)`

### Superpowers skills don't trigger

- Restart Claude Code after installing the plugin.
- Verify the `using-superpowers` bootstrap skill is present — it loads automatically on every session start.
- Check plugin registration: run `/plugin list` in Claude Code to confirm superpowers appears.

### Advanced Planning commands not found

- Re-run the install script with the correct `--project` path pointing to your project root.
- Check that `.claude/commands/` exists in your project and contains files like `plan-and-phase.md`, `next-loop.md`, etc.
- Verify hooks are registered in `.claude/settings.json`.

### gstack-to-plans not finding the design doc

- Check that `~/.gstack/projects/{slug}/` exists and contains a file matching the pattern `{user}-{branch}-design-{datetime}.md`.
- Confirm the current git branch name matches the branch used during the gstack session.
- On detached HEAD or worktree setups, the skill will ask you which design doc to use via `AskUserQuestion`.

### PostToolUse hook not firing

- Confirm Node.js is installed (`node --version`).
- Check `.claude/settings.json` for the `hooks.PostToolUse` entry with the Write matcher.
- The hook is advisory — if it doesn't fire, run `/gstack-to-plans` manually or follow the CLAUDE.md closing instruction.
