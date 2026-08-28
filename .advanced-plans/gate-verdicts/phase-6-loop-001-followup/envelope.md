# Review request — three specific questions about an installer mechanism

You are reviewing a change in the repository at `C:/Users/mharvey2/Coding/advanced-planning`,
on branch `fix/shared-runtime-reachability`, HEAD commit `38f5d00`. Read the code. Do not
change anything — this is read-only.

## Background, so the questions make sense

The project is a planning system whose slash commands are Markdown files containing shell and
Python call sites. Those call sites need a shared Python runtime that lives in the source
checkout (`platforms/python/`). Until this branch, no installer ever shipped that runtime into
an installed project, so every command died with the interpreter's own "can't open file".

The mechanism now is:

- `.advanced-plans/runtime.json` records `source_root`, an absolute path to the source
  checkout. `.advanced-plans/bin/ap.py` is a copy of `platforms/python/ap_launcher.py`. The
  launcher reads the record, puts `source_root` on `sys.path`, and dispatches.
- Call sites are `python ".advanced-plans/bin/ap.py" <module> [args]` for shell, and
  `runpy.run_path(r'.advanced-plans/bin/ap.py')['bootstrap']()` for in-line Python.
- A **project** install (`--project`) writes those two files into the project.
- A **global** install (`--global` / `-Global`) copies commands into `<home>/.claude/commands/`
  and additionally writes `<home>/.advanced-plans/runtime.json` and
  `<home>/.advanced-plans/bin/ap.py`, then **rewrites the launcher path** inside each copied
  command to one absolute forward-slash path. `<home>` resolves from `USERPROFILE` before
  `HOME` (they disagree under Git Bash on Windows).
- Resolution order at run time: `$ADVANCED_PLANNING_ROOT` env override → walk up from cwd for
  `.advanced-plans/runtime.json`, stopping at a boundary (a `.advanced-plans/` or a `.git`
  without a manifest) → the manifest sitting beside the launcher itself → the profile-level
  record at `<home>/.advanced-plans/runtime.json`.
- On failure the launcher prints a guard naming the manifest, the key and the repair, and
  exits 2 (unreachable) or 3 (stale record).

The files to read: `platforms/python/ap_launcher.py`, `platforms/python/install_audit.py`,
`setup/claude-code/install.sh`, `setup/claude-code/install.ps1`,
`platforms/claude-code/install.sh`, and `platforms/claude-code/commands/*.md`.

## The three questions

Answer each **in your own words**, from the code, not from the description above. If the code
does not answer a question, say that it does not — "the code is silent on this" is a valid and
useful answer, and is more useful than a guess.

**Q1 — Uninstall.** If a user wants to remove this system, what exactly is left behind, and
what breaks? Consider both the project install and the global install. Is there an uninstall
path at all? What happens to a project that still has `.advanced-plans/runtime.json` pointing
at a source checkout that has been deleted? Is the resulting failure diagnosable by the person
who sees it?

**Q2 — Upgrade in place.** A user re-runs the installer over a project that already has
planning data. What happens to `runtime.json` and to the launcher copy? Specifically: if the
source checkout moved between the first install and the second, does the second install repair
the stale path, or does the "planning data already exists, skip" guard skip past it? Check
whether the *global* installer has the same property as the project installer. Are the two
consistent?

**Q3 — Python not on PATH.** The shell call sites invoke the bare word `python`. On a machine
where `python` is not on PATH — or where it resolves to the Windows Store stub, or to Python 2
— what does the user see? How far does execution get before it fails? Does any part of the
guard machinery run? If not, is there anything the design could reasonably do about it, or is
it genuinely outside the boundary of this system?

## What I want back

For each question: a direct answer, the file and line that justifies it, and — if you think
the behaviour is wrong — what you would change and how much it would cost. Be concrete and be
willing to say the design is fine where it is fine. I am specifically not asking for a general
code review; three answers is the whole task.

Also answer this fourth, briefly: **does the mechanism duplicate code that can drift?**
`ap_launcher.global_home()` and `install_audit.resolve_global_home()` implement the same
USERPROFILE-before-HOME rule in two places. Is the stated reason (the launcher is copied
standalone and must stay stdlib-only) sound, and is a test pinning the duplication an adequate
control, or is this a real drift risk?
