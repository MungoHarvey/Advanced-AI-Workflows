# Install: gstack

Source: https://github.com/garrytan/gstack (README.md — "Install — 30 seconds" section)

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Git](https://git-scm.com/)
- [Bun](https://bun.sh/) v1.0+
- [Node.js](https://nodejs.org/) (Windows only)

## Step 1: Install on your machine

Open Claude Code and paste this prompt. Claude does the rest:

> Install gstack: run **`git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`** then add a "gstack" section to CLAUDE.md that says to use the /browse skill from gstack for all web browsing, never use mcp__claude-in-chrome__* tools, and lists the available skills: /office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review, /design-consultation, /design-shotgun, /design-html, /review, /ship, /land-and-deploy, /canary, /benchmark, /browse, /connect-chrome, /qa, /qa-only, /design-review, /setup-browser-cookies, /setup-deploy, /retro, /investigate, /document-release, /codex, /cso, /autoplan, /plan-devex-review, /devex-review, /careful, /freeze, /guard, /unfreeze, /gstack-upgrade, /learn. Then ask the user if they also want to add gstack to the current project so teammates get it.

## Step 2 (optional): Team mode

From inside your repo, paste this. Switches to team mode, bootstraps the repo so teammates get gstack automatically, and commits the change:

```bash
(cd ~/.claude/skills/gstack && ./setup --team) && ~/.claude/skills/gstack/bin/gstack-team-init required && git add .claude/ CLAUDE.md && git commit -m "require gstack for AI-assisted work"
```

Swap `required` for `optional` if you'd rather nudge teammates than block them.

## Detection (used by setup-with-claude)

gstack is installed if `~/.claude/skills/gstack/` exists and contains `SKILL.md` or `README.md`.

## Uninstall

Remove the `~/.claude/skills/gstack/` directory. The meta-project's `--uninstall` does NOT do this — it only removes meta-project artifacts.
