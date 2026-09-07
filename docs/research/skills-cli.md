# Skills CLI Research

Primary sources: `npx skills@1.5.24 --help`, `npx skills@1.5.24 add --help`, and the `mattpocock/skills` README (https://raw.githubusercontent.com/mattpocock/skills/main/README.md). Measurements performed in `%TEMP%\skills-cli-test`.

---

## 1. Bulk mode for pinning every skill in a source repo

**Answer:** Yes. The `--all` flag installs every skill from a source in one command.

**Source (measured):**
```
npx skills@latest add mattpocock/skills --all --yes
```
Output confirms: "Selected 37 skills" and installs all of them in a single invocation.

**Help text (quoted):**
```
--all                  Shorthand for --skill '*' --agent '*' -y
```

**Usage for `/setup-aaw`:**
```bash
npx skills@latest add mattpocock/skills --all --yes
```

This decides: pinning the spine is **one step**, not twenty.

---

## 2. Exact selector syntax for pinning named skills

**Answer:** Use `--skill <name>` (can be repeated for multiple skills).

**Source (measured):**
```
npx skills@latest add mattpocock/skills --skill "grill-me" --yes
npx skills@latest add mattpocock/skills --skill "grill-me" --skill "triage" --yes
```

**Help text (quoted):**
```
-s, --skill <skills>   Specify skill names to install (use '*' for all skills)
```

**Examples from help (quoted):**
```
$ skills add vercel-labs/agent-skills --skill pr-review commit
```

**Usage for `/setup-aaw`:**
```bash
# Single skill
npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills --yes

# Multiple named skills
npx skills@latest add mattpocock/skills --skill grill-me --skill triage --skill wayfinder --yes
```

---

## 3. Pinning from a repository's own remote

**Answer:** Yes. The CLI accepts a local path as the `<source>` argument and installs skills from it. The lock records the source as a relative path with `sourceType: "local"`.

**Source (measured):**
```
npx skills@latest add C:\Users\mharvey2\.herdr\worktrees\Advanced-AI-Workflows\research-skills-cli --skill "setup-with-claude" --yes
```

Output:
```
Source: C:\Users\mharvey2\.herdr\worktrees\Advanced-AI-Workflows\research-skills-cli
Local path validated
Found 2 skills
```

**Lock file entry (measured):**
```json
{
  "setup-with-claude": {
    "source": "../../../../.herdr/worktrees/Advanced-AI-Workflows/research-skills-cli",
    "sourceType": "local",
    "computedHash": "1c9738bed7df0b806772228de41ec1fcaf9b16abc3a75afd95cf89a25ecf5b74"
  }
}
```

**Inference:** A fresh clone cannot pin `aaw-tools` from its own remote because the local checkout is the only available source. The fresh-clone test must pin `aaw-tools` from the published GitHub remote (`MungoHarvey/Advanced-AI-Workflows`), not from a local path. The CLI does not "short-circuit" to local—it simply requires an explicit source. If the source is the local repo, it works; if the source is the GitHub remote, it also works.

**Usage for `/setup-aaw`:**
```bash
# Pin aaw-tools from the GitHub remote (works in a fresh clone)
npx skills@latest add MungoHarvey/Advanced-AI-Workflows --skill setup-with-claude --skill gstack-to-plans --yes
```

---

## 4. Where the CLI writes: `.agents/skills/` only, or also harness dirs?

**Answer:** The CLI writes to **all detected agent directories** in the project. In the test, skills were installed to `.agents/skills/` and `.claude/skills/` (symlinked). The lock file (`skills-lock.json`) is written at the project root and records only the source metadata (source, sourceType, skillPath, computedHash)—not which agent directories received the skill.

**Source (measured):**
After `npx skills@latest add mattpocock/skills --skill "grill-me" --yes`:
```
Test-Path ".agents\skills\grill-me"     # True
Test-Path ".claude\skills\grill-me"     # True
Test-Path ".cursor\skills\grill-me"     # False (not detected in this test env)
```

**Installation output (quoted):**
```
~\AppData\Local\Temp\skills-cli-test\.agents\skills\grill-me
  universal: Antigravity, Antigravity CLI, Codex, Cursor, Gemini CLI +12 more
  symlink → Claude Code, Hermes Agent, Pi
```

**Lock file location (measured):**
```
skills-lock.json at project root (same level as package.json)
```

**Lock file schema (measured):**
```json
{
  "version": 1,
  "skills": {
    "<skill-name>": {
      "source": "<github-owner/repo or relative-path>",
      "sourceType": "github | local",
      "skillPath": "<path-within-source-repo>/SKILL.md",
      "computedHash": "<sha256-of-skill-file-content>"
    }
  }
}
```

**Inference:** The lock does **not** record which agent directories received the skill. It only records the source provenance and content hash. Agent directory installation is a separate concern (detected at install time).

**Usage for `/setup-aaw`:**
The lock file is already in the correct format. No additional configuration is needed for multi-agent installs—the CLI handles this automatically.

---

## Summary: Exact commands for `/setup-aaw`

```bash
# 1. Pin the entire spine (mattpocock/skills) in one command
npx skills@latest add mattpocock/skills --all --yes

# 2. Or, pin specific spine skills by name
npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills --skill grill-with-docs --skill wayfinder --yes

# 3. Pin aaw-tools from the GitHub remote (works in fresh clone)
npx skills@latest add MungoHarvey/Advanced-AI-Workflows --skill setup-with-claude --skill gstack-to-plans --yes

# 4. Restore from skills-lock.json (if it already exists)
npx skills@latest experimental_install
```
