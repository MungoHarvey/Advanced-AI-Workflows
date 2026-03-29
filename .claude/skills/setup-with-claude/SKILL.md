---
name: setup-with-claude
description: Use when setting up the Advanced AI Workflows planning stack in a project, when user asks to install advanced planning, bootstrap planning tools, or prepare a project for structured planning
---

# Setup Advanced AI Workflows

Bootstrap the full planning-review-execution stack into the current project. Clones tool repositories to a local cache and installs commands, skills, agents, and hooks into the project's `.claude/` directory.

## Overview

Three tools integrate at boundaries to form a complete pipeline:

| Tool | What It Does | Repo |
|------|-------------|------|
| **Superpowers** | Composable dev methodology skills (brainstorming, TDD, code review) | `MungoHarvey/superpowers` |
| **Advanced Planning** | Hierarchical planning: Phases → Ralph Loops → Todos | `MungoHarvey/advanced-planning` |
| **Plannotator** | Visual plan review and annotation in the browser | `MungoHarvey/plannotator` |

Install order matters: **Superpowers (1st) → Advanced Planning (2nd) → Plannotator (3rd)**.

## When to Use

- User says "set up planning", "install advanced planning", "prepare this project for planning"
- Starting a new project that needs structured, multi-phase planning
- User wants the brainstorm → plan → review → execute → review pipeline

## When NOT to Use

- Project already has all three tools installed (verify with Step 1 first)
- User only wants one tool — direct them to that tool's own README instead

## Process

### Step 1: Detect Current State

Check what is already installed before doing anything:

```bash
echo "=== Commands ==="
[ -f .claude/commands/plan-and-phase.md ] && echo "FOUND: plan-and-phase" || echo "MISSING: plan-and-phase"
[ -f .claude/commands/next-loop.md ] && echo "FOUND: next-loop" || echo "MISSING: next-loop"
[ -f .claude/commands/run-gate.md ] && echo "FOUND: run-gate" || echo "MISSING: run-gate"
[ -f .claude/commands/next-phase.md ] && echo "FOUND: next-phase" || echo "MISSING: next-phase"

echo "=== Skills ==="
[ -d .claude/skills/brainstorming ] && echo "FOUND: brainstorming (Superpowers)" || echo "MISSING: brainstorming"
[ -f .claude/skills/phase-plan-creator/SKILL.md ] && echo "FOUND: phase-plan-creator (Adv. Planning)" || echo "MISSING: phase-plan-creator"
[ -f .claude/skills/ralph-loop-planner/SKILL.md ] && echo "FOUND: ralph-loop-planner (Adv. Planning)" || echo "MISSING: ralph-loop-planner"

echo "=== Agents ==="
[ -f .claude/agents/ralph-orchestrator.md ] && echo "FOUND: ralph-orchestrator" || echo "MISSING: ralph-orchestrator"
[ -f .claude/agents/ralph-loop-worker.md ] && echo "FOUND: ralph-loop-worker" || echo "MISSING: ralph-loop-worker"

echo "=== Cache ==="
[ -d ~/.cache/advanced-ai-workflows/advanced-planning ] && echo "CACHED: advanced-planning" || echo "NOT CACHED: advanced-planning"
[ -d ~/.cache/advanced-ai-workflows/plannotator ] && echo "CACHED: plannotator" || echo "NOT CACHED: plannotator"
[ -d ~/.cache/advanced-ai-workflows/superpowers ] && echo "CACHED: superpowers" || echo "NOT CACHED: superpowers"
```

Tell the user what was found. Skip steps for components already installed. If everything is present, jump to Step 6 (verify).

### Step 2: Clone Repositories to Cache

Repos are cached at `~/.cache/advanced-ai-workflows/` — they do not live in the project directory.

```bash
mkdir -p ~/.cache/advanced-ai-workflows
cd ~/.cache/advanced-ai-workflows

# Clone only what is missing:
[ -d advanced-planning ] || git clone https://github.com/MungoHarvey/advanced-planning.git
[ -d plannotator ] || git clone https://github.com/MungoHarvey/plannotator.git
[ -d superpowers ] || git clone https://github.com/MungoHarvey/superpowers.git

# Update if already cached:
[ -d advanced-planning ] && (cd advanced-planning && git pull --ff-only 2>/dev/null || true)
[ -d plannotator ] && (cd plannotator && git pull --ff-only 2>/dev/null || true)
[ -d superpowers ] && (cd superpowers && git pull --ff-only 2>/dev/null || true)
```

### Step 3: Install Superpowers (first)

Superpowers loads the skills framework on session start. No build step required.

**Ask the user: project-local or global install?**

**Project-local install** (skills available in this project only):
```bash
CACHE=~/.cache/advanced-ai-workflows/superpowers
mkdir -p .claude/skills .claude/hooks .claude/agents

# Skills
cp -r "$CACHE/skills/"* .claude/skills/

# Hooks (session start)
cp "$CACHE/hooks/"* .claude/hooks/ 2>/dev/null || true

# Agents
cp "$CACHE/agents/"* .claude/agents/ 2>/dev/null || true
```

**Global install** (skills available in all projects):
```bash
CACHE=~/.cache/advanced-ai-workflows/superpowers
mkdir -p ~/.claude/skills ~/.claude/hooks ~/.claude/agents

cp -r "$CACHE/skills/"* ~/.claude/skills/
cp "$CACHE/hooks/"* ~/.claude/hooks/ 2>/dev/null || true
cp "$CACHE/agents/"* ~/.claude/agents/ 2>/dev/null || true
```

**Plugin marketplace** (alternative — installs as a managed plugin):
```
/plugin install superpowers@claude-plugins-official
```

### Step 4: Install Advanced Planning (second)

Installs slash commands, planning skills, agent definitions, and schemas.

**Ask the user: project-local or global?**

**Project-local install (recommended):**

macOS / Linux / WSL:
```bash
cd ~/.cache/advanced-ai-workflows/advanced-planning
sh setup/claude-code/install.sh --project "PROJECT_PATH"
```

Windows PowerShell:
```powershell
cd "$env:USERPROFILE\.cache\advanced-ai-workflows\advanced-planning"
.\setup\claude-code\install.ps1 -Project "PROJECT_PATH"
```

Replace `PROJECT_PATH` with the actual project root.

**Global install:**
```bash
cd ~/.cache/advanced-ai-workflows/advanced-planning
sh setup/claude-code/install.sh --global
```

**Dry-run first** (preview what will be copied):
```bash
sh setup/claude-code/install.sh --dry-run --project "PROJECT_PATH"
```

After install, confirm key files exist:
```bash
ls .claude/commands/plan-and-phase.md .claude/commands/next-loop.md .claude/commands/run-gate.md
```

### Step 5: Install Plannotator (third)

Plannotator hooks into ExitPlanMode to provide visual plan review in the browser.

**Requires Bun.** Check with `bun --version`. If not installed, tell the user:
> "Plannotator requires Bun. Install it from https://bun.sh/ then re-run this step."

**Build from cache:**
```bash
cd ~/.cache/advanced-ai-workflows/plannotator
bun install
bun run build
```

**Install as plugin. Ask the user which method:**

Marketplace:
```
/plugin marketplace add backnotprop/plannotator
/plugin install plannotator@plannotator
```

Local plugin (from cache):
```bash
claude --plugin-dir ~/.cache/advanced-ai-workflows/plannotator/apps/hook
```

**Tell the user: Restart Claude Code after installing Plannotator.** The hook registration only takes effect after restart.

### Step 6: Verify Setup

Run the full verification and present results:

```bash
echo "=== Verification ==="

# Commands
CMDS_OK=true
for cmd in plan-and-phase next-loop run-gate next-phase new-phase loop-status progress-report check-execution; do
  [ -f ".claude/commands/$cmd.md" ] && echo "OK: /$cmd" || { echo "MISSING: /$cmd"; CMDS_OK=false; }
done

# Core skills
SKILLS_OK=true
for skill in phase-plan-creator ralph-loop-planner plan-todos plan-skill-identification plan-subagent-identification progress-report; do
  [ -f ".claude/skills/$skill/SKILL.md" ] && echo "OK: $skill" || { echo "MISSING: $skill"; SKILLS_OK=false; }
done

# Superpowers skills
SP_OK=true
for skill in brainstorming writing-plans subagent-driven-development test-driven-development; do
  [ -d ".claude/skills/$skill" ] && echo "OK: $skill" || { echo "MISSING: $skill"; SP_OK=false; }
done

# Agents
AGENTS_OK=true
for agent in ralph-orchestrator ralph-loop-worker; do
  [ -f ".claude/agents/$agent.md" ] && echo "OK: $agent" || { echo "MISSING: $agent"; AGENTS_OK=false; }
done

# Infrastructure
mkdir -p .claude/state .claude/plans
echo "OK: state and plans directories"
```

Present the summary:

```
| Component                 | Status |
|---------------------------|--------|
| Advanced Planning commands | OK / MISSING |
| Planning skills            | OK / MISSING |
| Superpowers skills         | OK / MISSING |
| Agent definitions          | OK / MISSING |
| State + plans directories  | OK |
| Plannotator plugin         | Requires restart to verify |
```

If anything is MISSING, offer to re-run the relevant install step.

### Step 7: Post-Setup Quick Reference

Show the user what is now available:

```
Setup complete. Here is what you can do:

PLANNING
  /plan-and-phase [desc]   Explore codebase, then create a structured plan
  /new-phase [desc]        Create a plan directly (when you know the codebase)

EXECUTION
  /next-loop               Execute one bounded loop
  /next-loop --auto        Chain all loops in the current phase

REVIEW
  /run-gate                Evaluate phase outputs with review agents
  /next-phase              Gate review, then advance to next phase
  /next-phase --auto       Fully autonomous multi-phase execution

MONITORING
  /loop-status             Current phase progress
  /progress-report         Detailed status from plans and git history
  /check-execution         Diagnostic if something seems wrong

TIP: Just describe what you want to build. Superpowers brainstorming
     activates automatically and feeds into the planning pipeline.
```

## Common Mistakes

| Problem | Fix |
|---------|-----|
| Installed Plannotator before Superpowers | Skills framework not loaded. Install Superpowers first, restart. |
| Commands not found after install | Check `.claude/commands/` has `.md` files. Re-run install script. |
| Plannotator doesn't open in browser | Restart Claude Code. Check Bun is installed. Check port access. |
| Skills don't trigger automatically | Ensure `using-superpowers` hook ran on session start. Restart. |
| Install script copies to wrong directory | Use `--dry-run` first. Confirm `PROJECT_PATH` is correct. |

## Install This Skill

**Global** (available in all projects — recommended):
```bash
mkdir -p ~/.claude/skills/setup-with-claude
curl -fsSL https://raw.githubusercontent.com/MungoHarvey/advanced-ai-workflows/main/.claude/skills/setup-with-claude/SKILL.md \
  -o ~/.claude/skills/setup-with-claude/SKILL.md
```

**Project-local:**
```bash
mkdir -p .claude/skills/setup-with-claude
curl -fsSL https://raw.githubusercontent.com/MungoHarvey/advanced-ai-workflows/main/.claude/skills/setup-with-claude/SKILL.md \
  -o .claude/skills/setup-with-claude/SKILL.md
```
