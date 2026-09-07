# The launcher is installed by the installer and audited by nothing

Date: 2026-09-03
Repository: `advanced-planning`, worktree `loop-008-gate` at `97ebd0b`
Status: **finding, not fixed.** Recorded before the phase 6 gate rather than fixed
during it, because the fix changes `install_audit` and the gate should see the
programme as it stands.

## What was measured

Found while checking whether the global install was fit to run the gate through.

`setup/claude-code/install.sh` copies the launcher into place twice:

```
275:    do_cp "$REPO_ROOT/platforms/python/ap_launcher.py" "$_ap_dir/bin/ap.py"   # global
478:    do_cp "$REPO_ROOT/platforms/python/ap_launcher.py" "$AP_DIR/bin/ap.py"    # project
```

`platforms/python/install_audit.py` compares two destination roots and no others:

```
475:        project_claude = repo_root / ".claude"
487:        global_claude = global_home / ".claude"
```

`.advanced-plans/bin/ap.py` is under neither. The audit's own header says so out
loud every time it runs:

```
=== source -> global (C:\Users\mharvey2\.claude) [DRIFT DETECTED] ===
  Summary: 41 current, 2 stale, 0 missing, 0 source-missing, 13 extra  (total: 56)
```

Fifty-six files, and the launcher is not one of them.

## It is not a theoretical gap. The installed launcher is stale right now.

`~/.advanced-plans/runtime.json` records `source_root` as this worktree and
`version` 0.20.0, written by `install.sh --global` at 12:48 today. `0f138de`
landed after that. Diffing the installed copy against the source it claims to be:

```
--- global/ap.py
+++ worktree/ap_launcher.py
@@ -230,5 +236,16 @@
     here = os.path.abspath(start or os.getcwd())
+    profile = os.path.abspath(global_home())
     while True:
+        if os.path.normcase(here) == os.path.normcase(profile):
+            return None
+        if _is_ancestor(here, profile):
+            return None
         candidate = os.path.join(here, MANIFEST_RELPATH)
```

Thirty diff lines. The installed launcher is the pre-loop-007-9 one, without the
profile boundary — the exact product defect that loop closed. Driving the real
`install_audit._file_hash` over both, rather than a reimplementation of its
normalisation:

```
real _file_hash global  : c92924da2dc2010a989356cc6cba0c69edd199e1
real _file_hash worktree: 41c8b71ac87fa7c0650dd5dd965a8ae734fec222
```

The audit reported `0 missing` in the same run.

## Why this is the same defect, one level up

The audit answers a question about a file set it assembled itself. Walk two
`.claude` trees, compare what you find, report a summary. Every file it was given
really was current, and the number is true of that set. The set is the thing
nobody checked, and the file it omits is the one every command in the product
invokes — `run-gate.md:40`, `:349`, `:410` all go through it.

This is the programme's central defect class arriving in the instrument rather
than the subject. Check your instrument before your subject: the audit has been
the instrument for three loops now, and this is the first time anyone asked what
it does not look at.

## What the fix is not

Not "add `bin/ap.py` to the `.claude` walk" — it is in a different tree, and the
layer pair is named for `.claude` throughout. It needs a third comparison, of
`<ap_dir>/bin/ap.py` against `platforms/python/ap_launcher.py`, with the same
`LAUNCHER_PATH_RE` normalisation the file hash already applies, since the global
copy is rewritten in exactly the way that normalisation exists to forgive.

Two consequences worth stating before anyone writes that:

- The audit currently has no notion of a destination outside `.claude`, so this
  is a structural addition, not a line.
- `--layers source,project` would need the project `.advanced-plans/bin/ap.py`,
  which only exists in a project-layer install. A missing one there is normal and
  must not read as drift.

## Also observed in the same run

`commands/sync-install.md` now reads STALE against the global layer. That is
loop-007-10 working as intended: the source changed, the install did not. It is
the second stale file alongside `commands/run-gate.md`, which was already known.
Neither was refreshed — refreshing writes to `~/.claude/`, and the operator had
chosen the route that avoids that.
