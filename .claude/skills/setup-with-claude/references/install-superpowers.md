# Install: superpowers

Source: https://github.com/obra/superpowers (README.md — "Installation / Claude Code" section)

## Claude Code — Official Marketplace (recommended)

```
/plugin install superpowers@claude-plugins-official
```

## Claude Code — Superpowers Marketplace

Register the marketplace first, then install:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

## Manual install (project-local)

Clone and copy skills into your project's `.claude/` directory:

```bash
git clone https://github.com/obra/superpowers
cd superpowers
cp -r skills/* /path/to/your/project/.claude/skills/
```

## Manual install (global)

Clone and copy skills into `~/.claude/skills/`:

```bash
git clone https://github.com/obra/superpowers
cd superpowers
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

## Windows (PowerShell — manual install, project-local)

```powershell
git clone https://github.com/obra/superpowers
cd superpowers
Copy-Item -Recurse skills\* C:\path\to\your\project\.claude\skills\
```

## Detection (used by setup-with-claude)

Superpowers is installed if `.claude/skills/brainstorming/SKILL.md` exists (project-local)
or `~/.claude/skills/brainstorming/SKILL.md` exists (global install).

## Notes for Advanced AI Workflows

The meta-project's `setup-with-claude` skill installs a CLAUDE.md routing block that overrides
superpowers' default save paths:

- `brainstorming` skill: saves to `.advanced-plans/specs/` (overrides default `.claude/plans/`)
- `writing-plans` skill: saves to `.advanced-plans/specs/` (overrides default `docs/superpowers/plans/`)

Both skills honour user-stated preferences — no patch to superpowers is required.
The routing block is added automatically during `setup-with-claude` and removed cleanly by
`setup-with-claude --uninstall`.
