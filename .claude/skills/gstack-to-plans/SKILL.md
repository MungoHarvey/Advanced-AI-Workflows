---
name: gstack-to-plans
description: Copy the latest gstack design doc into the current project's .advanced-plans/specs/ directory, bridging gstack strategy/design output into the advanced-planning execution pipeline. Use when the user says "gstack to plans", "copy the gstack design doc into plans", "bring the design doc into advanced-planning", or runs /gstack-to-plans. Also fires automatically via the PostToolUse hook when gstack writes a design doc under ~/.gstack/projects/.
---

# gstack → advanced-planning glue

Bridges the two halves of the Advanced AI Workflows stack: it takes the design
document gstack produces (from `/office-hours`, `/design-consultation`, the plan
reviews, etc.) and copies it into the active project's
`.advanced-plans/specs/` directory, where advanced-planning's `/plan-and-phase`
and `/new-phase` commands look for input specs.

## When to use

- Manually, after a gstack planning/design session, to feed the resulting design
  doc into advanced-planning.
- Automatically, via the `PostToolUse` / `Write` hook scoped to
  `~/.gstack/projects/` — gstack writes a design doc there, the hook invokes this
  skill, and the doc lands in `.advanced-plans/specs/` without manual steps.

## Where gstack writes design docs

gstack stores per-project artefacts under:

```
~/.gstack/projects/<project-slug>/
    <name>-design-<YYYYMMDD>-<HHMMSS>.md   ← design docs (timestamped)
    learnings.jsonl
    timeline.jsonl
```

`<project-slug>` is gstack's slug for the project (git `owner-repo` when a remote
exists, otherwise a slugified path). Design-doc filenames always contain
`-design-` and a timestamp, so the newest by modification time is the most recent
design output.

## Process

1. **Resolve the target.** The current working directory is the project root.
   The destination is `<cwd>/.advanced-plans/specs/`. Create it if it does not
   exist.

2. **Find the source design doc.**
   - If invoked by the hook with a specific written file path, use that file.
   - Otherwise, locate the most-recently-modified `*-design-*.md` under
     `~/.gstack/projects/`. Prefer a project whose slug matches the current
     directory (its folder name or `owner-repo`); if no confident match, fall
     back to the globally newest design doc and say so in the report.

   PowerShell (Windows):
   ```powershell
   $proj = Join-Path $env:USERPROFILE ".gstack\projects"
   $doc = Get-ChildItem $proj -Recurse -Filter "*-design-*.md" -ErrorAction SilentlyContinue |
          Sort-Object LastWriteTime -Descending | Select-Object -First 1
   ```

   bash (macOS/Linux/git-bash):
   ```bash
   doc=$(ls -t "$HOME"/.gstack/projects/*/*-design-*.md 2>/dev/null | head -n1)
   ```

3. **Copy** the design doc into `.advanced-plans/specs/`, preserving its
   filename. Do not overwrite an existing identical file silently — if a file
   with the same name already exists, note it and skip or suffix as appropriate.

4. **Report** to the user: the source path, the destination path, and a one-line
   pointer that `/plan-and-phase` or `/new-phase` can now consume the spec.

## Output format

```
Copied gstack design doc → advanced-planning spec:
  source: ~/.gstack/projects/<slug>/<name>-design-<ts>.md
  dest:   .advanced-plans/specs/<name>-design-<ts>.md

Next: run /plan-and-phase (explore + plan) or /new-phase (plan directly) to turn
this spec into a phase plan.
```

## Notes

- This is a glue skill of the Advanced AI Workflows meta-project. It moves a file;
  it does not modify gstack or advanced-planning internals.
- If `~/.gstack/projects/` has no design docs, report that nothing was found and
  suggest running a gstack planning skill (e.g. `/office-hours`,
  `/design-consultation`) first.
- The auto-trigger requires the `PostToolUse` / `Write` hook (scoped to
  `~/.gstack/projects/`) in `.claude/settings.json`; without it, invoke
  `/gstack-to-plans` manually.
