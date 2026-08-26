# Install: advanced-planning

Source: https://github.com/MungoHarvey/advanced-planning (README.md — "How To Use / 1. Install" section)

Current release: **v0.11.0**

## macOS / Linux

```bash
git clone https://github.com/MungoHarvey/advanced-planning
cd advanced-planning
sh setup/claude-code/install.sh --project /path/to/your/project
```

For global installation (commands available in all projects):

```bash
sh setup/claude-code/install.sh --global
```

Dry-run preview (recommended before first install):

```bash
sh setup/claude-code/install.sh --dry-run --project /path/to/your/project
```

## Windows (PowerShell)

```powershell
git clone https://github.com/MungoHarvey/advanced-planning
cd advanced-planning
.\setup\claude-code\install.ps1 -Project C:\path\to\your\project
```

For global installation:

```powershell
.\setup\claude-code\install.ps1 -Global
```

## Specific tagged release

```bash
git clone https://github.com/MungoHarvey/advanced-planning
cd advanced-planning
git checkout v0.11.0
sh setup/claude-code/install.sh --project /path/to/your/project
```

## What gets installed

Copies commands, skills, agents, schemas, and hooks into your project's `.claude/` directory.
See `setup/claude-code/README.md` for all options (`--global`, `--symlink`, `--dry-run`).

## Detection (used by setup-with-claude)

advanced-planning is installed if `.claude/skills/phase-plan-creator/SKILL.md` exists in the project,
OR if `.advanced-plans/` exists at the project root.

## Notes

- The meta-project uses `.advanced-plans/` as the runtime root (v0.11.0 canonical path).
- After install, grant Claude read/edit/write permissions on `.advanced-plans/` via `.claude/settings.json`
  (the `setup-with-claude` skill handles this step automatically).
- advanced-planning's `/plan-and-phase` auto-detects superpowers — no extra wiring needed.
- Plannotator was deprecated on 2026-08-26; do not install or detect it.
