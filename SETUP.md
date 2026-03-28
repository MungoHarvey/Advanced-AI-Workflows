# Setup Guide

This guide walks you through installing the full Advanced AI Workflows stack. Each tool can be installed independently -- you only need the ones relevant to your workflow. Installing all three gives you the complete planning-review-execution pipeline.

---

## Prerequisites

| Requirement | Needed For | Install Guide |
|-------------|-----------|---------------|
| git | Cloning repositories | [git-scm.com](https://git-scm.com/) |
| Claude Code or OpenCode | Running the agent CLI | [claude.ai/code](https://claude.ai/code) or [opencode.ai](https://opencode.ai) |
| Bun | Plannotator build and runtime | [bun.sh](https://bun.sh/) |
| Python 3.10+ | Advanced Planning tests (optional) | [python.org](https://www.python.org/) |

Not all prerequisites are needed for all tools. If you only want Superpowers, you need git and an agent CLI. If you only want Advanced Planning commands, you need git, an agent CLI, and optionally Python for running tests. Plannotator is the only tool that requires Bun.

---

## Step 1: Clone This Repository

```bash
git clone https://github.com/MungoHarvey/advanced-ai-workflows.git
cd advanced-ai-workflows
```

---

## Step 2: Clone the Tool Repositories

Clone each tool into its expected subdirectory inside the workspace:

```bash
git clone https://github.com/MungoHarvey/advanced-planning.git
git clone https://github.com/MungoHarvey/plannotator.git
git clone https://github.com/MungoHarvey/superpowers.git
```

After cloning, your directory structure should look like this:

```
advanced-ai-workflows/
├── advanced-planning/      # Hierarchical multi-agent planning framework
├── plannotator/            # Browser-based visual plan review UI
├── superpowers/            # Development methodology skills
├── ARCHITECTURE.md
├── DESIGN-RATIONALE.md
├── README.md
├── ROADMAP.md
├── SETUP.md                # (this file)
└── CLAUDE.md
```

---

## Step 3: Install Superpowers

No build step needed -- Superpowers skills are markdown files loaded directly by your coding agent.

### Claude Code (Official Marketplace)

```
/plugin install superpowers@claude-plugins-official
```

### Claude Code (via Plugin Marketplace)

Register the marketplace first, then install:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### OpenCode

Tell OpenCode to fetch and follow instructions from the raw install file:

```
Fetch and follow instructions from https://raw.githubusercontent.com/obra/superpowers/refs/heads/main/.opencode/INSTALL.md
```

### Local Development

Run Claude Code with the plugin directory pointed at your local clone:

```bash
claude --plugin-dir ./superpowers
```

### Verify

Start a new Claude Code session and describe something you want to build. If Superpowers is installed correctly, the brainstorming skill should activate automatically -- the agent will ask clarifying questions about your intent before jumping into code.

---

## Step 4: Install Plannotator

Plannotator requires Bun. Install it from [bun.sh](https://bun.sh/) if you haven't already.

### Build from Source

```bash
cd plannotator
bun install
bun run build
```

**Build order note:** If you modify review UI code (in `packages/ui/`, `packages/editor/`, or `packages/review-editor/`), you must rebuild the review app before the hook:

```bash
bun run --cwd apps/review build && bun run build:hook
```

Running only `bun run build:hook` after review-editor changes will copy stale HTML files.

### Claude Code (Plugin Marketplace)

First, install the `plannotator` command:

**macOS / Linux / WSL:**

```bash
curl -fsSL https://plannotator.ai/install.sh | bash
```

**Windows PowerShell:**

```powershell
irm https://plannotator.ai/install.ps1 | iex
```

Then in Claude Code, register the marketplace and install the plugin:

```
/plugin marketplace add backnotprop/plannotator
/plugin install plannotator@plannotator
```

**Important:** Restart Claude Code after plugin install for the hooks to take effect.

### Local Development

Run Claude Code with the plugin directory pointed at the hook app:

```bash
claude --plugin-dir ./plannotator/apps/hook
```

### OpenCode

Add to your `opencode.json`:

```json
{
  "plugin": ["@plannotator/opencode@latest"]
}
```

Then run the install script to get the slash commands (`/plannotator-review`, `/plannotator-annotate`, `/plannotator-last`):

```bash
curl -fsSL https://plannotator.ai/install.sh | bash
```

Restart OpenCode after installation.

### Verify

Enter plan mode in Claude Code (start planning something) or run `/plannotator-annotate` on a markdown file. The Plannotator UI should open in your browser. If you installed via the plugin marketplace, the `ExitPlanMode` hook intercepts automatically when a plan is ready for review.

---

## Step 5: Install Advanced Planning

Advanced Planning copies slash commands, skills, agent definitions, and schemas into your project's `.claude/` directory.

### macOS / Linux

```bash
cd advanced-planning
sh setup/claude-code/install.sh --project /path/to/your/project
```

### Windows PowerShell

```powershell
cd advanced-planning
.\setup\claude-code\install.ps1 -Project C:\path\to\your\project
```

### Install Options

| Option | Description |
|--------|-------------|
| `--global` / `-Global` | Install to `~/.claude/` so commands are available in every project |
| `--symlink` / `-Symlink` | Link to `core/skills/` instead of copying, so updates apply immediately |
| `--dry-run` / `-DryRun` | Preview what would be installed without writing any files |

These flags can be combined. For example, `--global --symlink` installs globally with symlinked skills. See `setup/claude-code/README.md` in the Advanced Planning repository for the full reference.

### Verify

Open Claude Code in your target project and run:

```
/plan-and-phase test planning system
```

Claude should enter read-only exploration mode, examine the codebase, and then present findings for review before running the planning pipeline. If the command is not found, check that `.claude/commands/` in your project contains the installed `.md` files.

---

## Step 6: Verify the Full Pipeline

With all three tools installed, the complete workflow should chain together:

1. **Start a Claude Code session** in a project where Advanced Planning is installed.

2. **Describe something you want to build.** Superpowers brainstorming should activate, asking clarifying questions and refining your intent into a design document.

3. **Approve the design.** The brainstorming skill hands off to Advanced Planning's phase-plan-creator, which generates a hierarchical phase plan with success criteria.

4. **Review the phase plan.** Plannotator opens in your browser, showing the plan with annotation tools. Approve to proceed, or add annotations and request changes.

5. **Approve the plan.** Advanced Planning proceeds to ralph loop decomposition, populating todos with skill and agent assignments.

6. **Run `/next-loop`.** The orchestrator agent prepares the first loop, then the worker agent executes it with targeted skill injection. Repeat with `/next-loop` or chain with `/next-loop --auto`.

### If Something Goes Wrong

- **Check plugin install order.** The recommended order is Superpowers first, then Advanced Planning, then Plannotator. This avoids hook conflicts where multiple plugins intercept the same events.

- **Check hook entries.** Look at `~/.claude/settings.json` (or your project's `.claude/settings.json`) to confirm hooks are registered. Plannotator should have a `PermissionRequest` hook matching `ExitPlanMode`. Advanced Planning should have `PreToolUse` hooks for planning-mode and gate-review-mode sentinels.

- **Check that Plannotator's server starts.** If the browser doesn't open, verify Bun is installed (`bun --version`) and that `bun run build` completed without errors in the `plannotator/` directory.

---

## Troubleshooting

### Plannotator doesn't open in the browser

- Verify Bun is installed: `bun --version`
- Rebuild: `cd plannotator && bun install && bun run build`
- Check for port conflicts -- Plannotator uses random ports by default. Set `PLANNOTATOR_PORT` to a specific port if needed.
- In remote/SSH environments, set `PLANNOTATOR_REMOTE=1` and forward the port manually.

### Superpowers skills don't trigger

- Restart Claude Code after installing the plugin.
- Verify the `using-superpowers` bootstrap skill is present -- it should load automatically on every session start.
- Check plugin registration: run `/plugin list` in Claude Code to confirm Superpowers appears.

### Advanced Planning commands not found

- Re-run the install script with the correct `--project` path pointing to your project root.
- Check that `.claude/commands/` exists in your project and contains files like `plan-and-phase.md`, `next-loop.md`, etc.
- Verify hooks are registered in `.claude/settings.json` (the install script writes this automatically).

### Hook conflicts between tools

- Install in the recommended order: Superpowers, then Advanced Planning, then Plannotator.
- If Superpowers intercepts `EnterPlanMode` and prevents Advanced Planning from activating, this is a known conflict. The integration strategy routes brainstorming output into Advanced Planning's phase-plan-creator rather than Superpowers' own writing-plans skill.
- Check `~/.claude/settings.json` for duplicate or conflicting hook entries.

---

## Future: Automated Install Scripts

Unified `install.sh` and `install.ps1` scripts that install all three tools in the correct order are planned. These will handle dependency checks, build steps, and hook registration in a single command.

See [ROADMAP.md](ROADMAP.md) for details and timeline.
