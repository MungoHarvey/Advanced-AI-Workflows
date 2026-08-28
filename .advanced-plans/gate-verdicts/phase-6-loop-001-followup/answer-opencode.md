I'll read the specified files to answer these questions.
Now let me read a few of the command files to see the call sites:
Now I have all the information needed to answer the four questions. Let me provide the answers:

---

## Q1 — Uninstall

**What is left behind after uninstall:**

**Project install:**
- `.advanced-plans/` directory with all planning data (phases/, specs/, state/, logs/)
- `.advanced-plans/runtime.json` pointing to the source checkout
- `.advanced-plans/bin/ap.py` (the launcher copy)
- `.claude/` directory with commands/, agents/, skills/, schemas/, settings.json

**Global install:**
- `<home>/.advanced-plans/runtime.json` and `<home>/.advanced-plans/bin/ap.py`
- `<home>/.claude/commands/`, `<home>/.claude/agents/`, `<home>/.claude/schemas/`, `<home>/.claude/skills/`

**There is no uninstall path** — neither `install.sh` nor `install.ps1` provides an `--uninstall` option, and no uninstall script exists.

**What breaks:** A project with `runtime.json` pointing to a deleted checkout will fail when any command invokes the launcher. The launcher's guard at lines 337–346 (`ap_launcher.py`) detects this and exits 3 with:
```
advanced-planning: <manifest> records source_root = <path>, but there is no platforms/python/__init__.py under it...
advanced-planning: fix: re-run the installer from the checkout's new location...
```

**Is it diagnosable?** Yes — the guard is explicit. It names the manifest file, the key, and the repair command. However, there is no guidance for "I want to uninstall" — the repair assumes the checkout still exists.

---

## Q2 — Upgrade in place

**Project installer (`setup/claude-code/install.sh` lines 369–389):**

The runtime record is written **outside** the scaffold guard (lines 287–354). The comment at lines 365–367 states:
> "Deliberately OUTSIDE the scaffold guard above: that guard skips everything when .advanced-plans/ already exists, and an upgrade-in-place is exactly the case where the recorded path most needs refreshing."

So re-running the installer **does update** `runtime.json` and `ap.py` even if `.advanced-plans/` already exists. The path is always refreshed to the current `$REPO_ROOT`.

**Global installer (`setup/claude-code/install.sh` lines 163–180 and `install.ps1` lines 89–198):**

The global installer has **no existence guard at all** — it unconditionally writes `runtime.json` and copies `ap.py` every time. Lines 172–177 (sh) / 186–194 (ps1) always execute.

**Consistency:** Both installers repair stale paths on re-run. The project installer's explicit comment confirms this is intentional. They are consistent.

---

## Q3 — Python not on PATH

**What the user sees:**

The shell call sites (e.g., `next-loop.md` lines 70, 96, 184, 208) invoke `python ".advanced-plans/bin/ap.py" ...`. If `python` is not on PATH, or resolves to the Windows Store stub, or to Python 2:

**The shell fails immediately** with the interpreter's own error:
- "python: command not found" (Unix)
- "'python' is not recognized..." (Windows PowerShell)
- Windows Store prompt (Windows 10/11 default behavior)

**Nothing in the guard machinery runs** — `ap_launcher.py` is never invoked, so lines 337–365 (the guard) never execute. The failure is at the shell level, before Python starts.

**Is this outside the boundary?** Yes — this is the OS shell failing to find an interpreter, not the planning system failing. The launcher can only guard against failures that occur *after* Python starts (stale manifest, missing module, invalid JSON).

**What could reasonably be done:** A wrapper script could check for Python availability and emit a diagnostic, but that wrapper would itself need to be invoked by `python` or be on PATH — the same problem. The design cannot structurally solve "python is not on PATH" without becoming a different product (e.g., a standalone executable).

---

## Q4 — Does the mechanism duplicate code that can drift?

**The duplication:**
- `ap_launcher.py:global_home()` (lines 96–111)
- `install_audit.py:resolve_global_home()` (lines 87–105)

Both implement USERPROFILE-before-HOME resolution identically.

**The stated reason (launcher comment, lines 98–104):**
> "Deliberately duplicates `install_audit.resolve_global_home`. This file is copied out of the checkout and run before the runtime is reachable, so it cannot import the module it agrees with."

**Is this sound?** Yes — the launcher is stdlib-only by design (line 80: "Standard library only, and it must not import the package it is resolving"). It cannot import `install_audit` because `install_audit` is in `platforms.python`, which is precisely what the launcher is trying to *reach*.

**Is a test pinning the duplication adequate?** The comment references `test_global_home_agrees_with_install_audit` — a test that would fail if either implementation diverges. This is the standard control for unavoidable duplication: make divergence a test failure.

**Is this a real drift risk?** No — the logic is trivial (iterate two env keys, return first present, fallback to `expanduser`). The test is an adequate control. The duplication is a necessary consequence of the bootstrap problem: the launcher must work before the runtime is reachable, so it cannot depend on anything in the runtime.

---

**Summary:** The mechanism is sound. Q1 has no uninstall but good diagnostics; Q2 upgrades correctly; Q3 fails outside the boundary (unavoidable); Q4's duplication is justified and pinned by test.
