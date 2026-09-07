# gstack Subset Installation — Research Findings

**Ticket:** #11 — Can gstack be installed as a subset (careful, ship, land-and-deploy, retro, investigate, qa, design-review), or only whole?

**Branch:** research/gstack-subset

**Date:** 2026-09-07

**Method:** Primary source examination of `~/.claude/skills/gstack` setup script, skill structure, and `skills-lock.json` pattern.

---

## Summary

**Measured finding:** gstack **cannot** be installed as a subset of individual skills. The setup script installs all skills or none. There is no `--skills` flag, no selective installation mechanism, and no pinning system for individual gstack skills analogous to `skills-lock.json` for Matt Pocock skills.

**Inferred:** A gstack subset would require modifications to the setup script to support selective skill installation, or a manual post-install pruning approach that removes unwanted skill symlinks.

---

## Installation Architecture

### Setup Script Behavior

**Source:** `C:\Users\mharvey2\.claude\skills\gstack\setup` (examined lines 1-1224)

The setup script performs the following installation flow:

1. **Builds browse binary** — single shared runtime dependency for all browser-based skills (`/qa`, `/design-review`, `/browse`, `/canary`, `/benchmark`)
   - Path: `~/.claude/skills/gstack/browse/dist/browse`
   - Requires Bun + Playwright Chromium

2. **Generates host-specific skill docs** — `.agents/skills/gstack-*` for Codex, `.factory/skills/gstack-*` for Factory Droid, `.opencode/skills/gstack-*` for OpenCode

3. **Links ALL skills** — the `link_claude_skill_dirs()` function (lines 540-575) iterates over **every** subdirectory in `gstack/*/` that contains a `SKILL.md`:
   ```bash
   for skill_dir in "$gstack_dir"/*/; do
     if [ -f "$skill_dir/SKILL.md" ]; then
       # ... creates symlink for EVERY skill found
     fi
   done
   ```

4. **No selective installation flag** — the script accepts `--host`, `--local`, `--prefix`, `--no-prefix`, `--team`, `--no-team`, `--plan-tune-hooks`, `--no-plan-tune-hooks`, `-q/--quiet`. **No `--skills` or selective installation option exists.**

### Shared Runtime Dependencies

**Measured paths:**

| Dependency | Path | Used By |
|------------|------|---------|
| Browse binary | `~/.claude/skills/gstack/browse/dist/browse` | `/qa`, `/design-review`, `/browse`, `/canary`, `/benchmark`, `/setup-browser-cookies` |
| Binaries | `~/.claude/skills/gstack/bin/*` | All skills (gstack-config, gstack-slug, gstack-telemetry-log, etc.) |
| Review assets | `~/.claude/skills/gstack/review/*.md` | `/review`, `/ship` |
| QA templates | `~/.claude/skills/gstack/qa/templates/*` | `/qa`, `/qa-only` |
| ETHOS.md | `~/.claude/skills/gstack/ETHOS.md` | All skills (referenced in "Search Before Building" preamble) |

**Inferred:** Even a subset installation would require all shared runtime dependencies. The browse binary alone is ~20-50MB compiled.

---

## Skills-Lock Pattern Comparison

### Matt Pocock Skills (`skills-lock.json`)

**Source:** `C:\Users\mharvey2\.herdr\worktrees\Advanced-AI-Workflows\research-gstack-subset\skills-lock.json`

Structure:
```json
{
  "version": 1,
  "skills": {
    "code-review": {
      "source": "mattpocock/skills",
      "sourceType": "github",
      "skillPath": "skills/engineering/code-review/SKILL.md",
      "computedHash": "b4f17857..."
    },
    "implement": { ... },
    "research": { ... }
  }
}
```

**Measured:** Each skill is pinned individually by:
- GitHub source repo
- Path within repo
- Content hash for verification

**Inferred:** This pattern allows selective installation — the setup mechanism (not examined in this research) could theoretically install only skills listed in `skills-lock.json`.

### Gstack Skills

**Measured:** No equivalent pinning mechanism exists for gstack skills.

- gstack installs from a **single monolithic checkout** (`~/.claude/skills/gstack`)
- All skills share the same version (tracked in `~/.claude/skills/gstack/VERSION`)
- `/gstack-upgrade` updates the **entire** gstack directory via `git pull`

**Inferred:** A gstack subset would require:
1. Either a `skills-lock.json`-style manifest for gstack skills
2. Or a modified setup script that accepts a list of skill names to install
3. Or manual post-install pruning of unwanted skill symlinks

---

## The Seven Selected Skills

**From issue #11:** `careful`, `ship`, `land-and-deploy`, `retro`, `investigate`, `qa`, `design-review`

**Measured dependencies:**

| Skill | Shared Dependencies | Standalone? |
|-------|---------------------|-------------|
| `/careful` | `bin/gstack-config`, `bin/gstack-slug`, `bin/gstack-telemetry-log`, `bin/gstack-timeline-log` | ❌ Requires bin/ |
| `/ship` | bin/, `review/*.md`, `qa/templates/`, browse (for `/qa` handoff), `ETHOS.md` | ❌ Requires multiple shared dirs |
| `/land-and-deploy` | bin/, browse (for canary checks) | ❌ Requires browse |
| `/retro` | bin/, `projects/*/retros/`, `projects/*/timeline.jsonl`, `projects/*/learnings.jsonl` | ❌ Requires global state |
| `/investigate` | bin/, `projects/*/learnings.jsonl`, `~/.gstack/analytics/eureka.jsonl` | ❌ Requires global state |
| `/qa` | bin/, browse binary, `qa/templates/*`, `qa/references/*` | ❌ Requires browse |
| `/design-review` | bin/, browse binary, `design/dist/*` | ❌ Requires browse |

**Inferred:** None of the seven skills can run standalone. All require the `bin/` directory and global state management. Four of seven require the browse binary.

---

## Upgrade Implications

### `/gstack-upgrade` Behavior

**Source:** `C:\Users\mharvey2\.claude\skills\gstack\gstack-upgrade\SKILL.md` (not fully examined, but referenced in setup script)

**Measured from setup script (lines 1203-1224):**

- Migration scripts live in `gstack-upgrade/migrations/v*.sh`
- Each migration is version-gated and idempotent
- Setup runs migrations on every install if version changed

**Inferred:** A subset installation would:
1. Still run all migrations (global state changes)
2. Still require `/gstack-upgrade` to update the entire gstack directory
3. Have no mechanism to pin individual skill versions

---

## Git Remote Structure

**Measured:**
```
fork    https://github.com/MungoHarvey/gstack.git (fetch)
fork    https://github.com/MungoHarvey/gstack.git (push)
origin  https://github.com/garrytan/gstack.git (fetch)
origin  https://github.com/garrytan/gstack.git (push)
```

**Inferred:** This is a personal fork setup. The gstack repo itself is monolithic — all skills live in the same repository, same directory tree. No mechanism for partial checkout exists.

---

## Open Questions (Not Answered by This Research)

1. **Can individual skills be manually symlinked?** — Technically yes, but would break on `/gstack-upgrade` and would not receive shared dependency updates.

2. **Could `skills-lock.json` be extended to support gstack skills?** — Would require a new installation mechanism. Current Matt Pocock skill installer is separate from gstack's setup script.

3. **What breaks if you delete unwanted skill symlinks post-install?** — Unknown without testing. The `/gstack-upgrade` skill might restore them.

4. **Does Claude Code's skill discovery mechanism allow filtering?** — Unknown. gstack registers all skills via `link_claude_skill_dirs()`; Claude's behavior on large skill sets was not examined.

---

## Conclusion

**Measured facts:**

1. gstack setup installs **all skills** or none — no selective installation flag exists
2. All skills share runtime dependencies (`bin/`, `browse/`, `review/`, `qa/`, `ETHOS.md`)
3. No `skills-lock.json`-style pinning exists for gstack skills
4. `/gstack-upgrade` updates the entire gstack directory monolithically
5. None of the seven selected skills can run standalone — all require shared infrastructure

**Inferred:**

- A gstack subset is **not supported** by the current installation architecture
- Implementing subset support would require:
  - Modifying the setup script to accept a `--skills` flag
  - Creating a manifest system for gstack skills (analogous to `skills-lock.json`)
  - Handling upgrade/migration paths for partial installs
  - Testing shared dependency isolation

**Recommendation:** This finding should be socialized with the gstack maintainer (Garry Tan) before proceeding with component design. The routing decision in #1 assumes a subset is installable; this research shows it is not currently possible without modification to gstack itself.

---

**Researcher:** opencode via herdr worker research-gstack-subset

**Sources examined:**
- `~/.claude/skills/gstack/setup` (lines 1-1224)
- `~/.claude/skills/gstack/SKILL.md` (lines 1-200)
- `~/.claude/skills/gstack/README.md` (lines 1-491)
- `~/.claude/skills/gstack/investigate/SKILL.md` (lines 1-897)
- `~/.claude/skills/gstack/careful/SKILL.md` (lines 1-67)
- `~/.claude/skills/gstack/ship/SKILL.md` (lines 1-887)
- `~/.claude/skills/gstack/land-and-deploy/SKILL.md` (lines 1-892)
- `~/.claude/skills/gstack/retro/SKILL.md` (lines 1-883)
- `skills-lock.json` (this repo)
- Git remotes: `garrytan/gstack` (origin), `MungoHarvey/gstack` (fork)
