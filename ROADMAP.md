# Roadmap

## Completed

- **Three-tool integration programme** — Superpowers, Advanced Planning, and Plannotator integrated at boundaries across three phases
- **Superpowers fork** — conditional integration: brainstorming redirects to phase-plan-creator when Advanced Planning detected; AskUserQuestion for brainstorming questions
- **Plannotator programme mode** — renders Advanced Planning's PLANS-INDEX.md hierarchy as navigable UI with breadcrumb navigation and section-level annotation
- **Advanced Planning gate review system** — sequential gate agents (code-review, phase-goals, security, test) with structured verdicts and confidence scoring
- **Advanced Planning autonomous chaining** — `/next-loop --auto` within phases; `/next-phase --auto` across phase boundaries including gate reviews
- **Meta-repository** — this repository: architecture documentation, design rationale, setup guide

## Next

- **Automated install scripts** — `install.sh` for macOS/Linux/WSL and `install.ps1` for Windows
- **Skills catalogue integration** — standard workflow for discovering, evaluating, and pulling skills from [awesome-agent-skills](https://github.com/MungoHarvey/awesome-agent-skills), [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills), and [anthropics/skills](https://github.com/anthropics/skills)
- **GitHub Project board** — cross-repo integration issue tracking with auto-add for integration-labelled issues
- **End-to-end validation** — clean-environment testing on macOS, Linux, and Windows

## Future

- **Template repository** — enable "Use this template" on GitHub
- **OpenCode full-stack validation** — verify complete three-tool integration on OpenCode
- **Community contribution guide** — how to contribute skills, report integration issues, propose architectural changes
- **Headless operation** — thin orchestrating script for pipeline without interactive session (state bus already supports this)
