# Install: plannotator

Source: https://github.com/backnotprop/plannotator (README.md — "Install for Claude Code" section)

## Step 1: Install the plannotator command

### macOS / Linux / WSL

```bash
curl -fsSL https://plannotator.ai/install.sh | bash
```

### Windows PowerShell

```powershell
irm https://plannotator.ai/install.ps1 | iex
```

## Step 2: Register the plugin in Claude Code

```
/plugin marketplace add backnotprop/plannotator
/plugin install plannotator@plannotator
```

## IMPORTANT: Restart Claude Code after plugin install

The plugin hooks (`EnterPlanMode` / `ExitPlanMode`) only take effect after restart.

## What plannotator provides

- `EnterPlanMode` hook: runs `plannotator improve-context` (5s timeout) when Claude Code enters plan mode
- `ExitPlanMode` hook: runs `plannotator` (visual review, 96-hour timeout) when Claude Code exits plan mode
- `/plannotator-annotate <file>` — annotate any markdown file and send feedback back to the agent
- `/plannotator-review` — visual code review of git diffs or remote PRs
- `/plannotator-last` — annotate the agent's last response
- `/plannotator-archive` — archive a plan

## Detection (used by setup-with-claude)

Plannotator is installed if `.claude/commands/plannotator-annotate.md` exists in the project.
This is the same detection check used by advanced-planning's `/plan-and-phase` Step 5b.

## Integration with advanced-planning

Once plannotator is installed, integration is **automatic**:

- advanced-planning's `/plan-and-phase` detects plannotator and invokes `/plannotator-annotate`
  on the phase plan in Step 5b — no meta-project glue required.
- Plannotator's `EnterPlanMode`/`ExitPlanMode` hooks fire automatically whenever Claude Code
  enters or exits plan mode — applies to any planning session.

The meta-project treats plannotator as **optional**. Install it if you want visual plan review;
skip it if you prefer a text-only workflow.

## Notes

- Requires [Bun](https://bun.sh/) v1.0+ on macOS/Linux
- On Windows, the install script handles the Bun dependency
- The `ExitPlanMode` popup is a known UX friction point: plannotator opens a browser window
  for every plan-mode exit, including brief ones. This is plannotator's own behaviour —
  the meta-project does not suppress it.
