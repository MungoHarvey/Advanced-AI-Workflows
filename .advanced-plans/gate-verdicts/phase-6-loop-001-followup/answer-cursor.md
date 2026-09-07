The code answers all four. One correction up front: the launcher does **not** distinguish exit 2 vs 3 the way the background described. Every guard failure is exit **3**. Exit **2** is CPython’s own “can’t open file”, which means the launcher never ran.

---

## Q1 — Uninstall

**There is no uninstall path.** Nothing in `setup/claude-code/`, `platforms/claude-code/`, or the docs removes what was installed. `setup/claude-code/README.md` documents install, dry-run, and symlink only.

### What is left behind

**Project install** writes two trees and never takes them back:

- `.claude/` — commands, agents, skills, schemas, `settings.json`
- `.advanced-plans/` — planning data **and** the mechanism files `runtime.json` + `bin/ap.py`

Re-running the installer skip-guards the planning scaffold, not those two trees. Deleting the source checkout does not touch either.

**Global install** writes two more, also never removed:

- `<home>/.claude/` — copied commands (with the launcher path rewritten to an absolute path), plus agents/skills/schemas depending on which installer ran
- `<home>/.advanced-plans/runtime.json` and `<home>/.advanced-plans/bin/ap.py`

`<home>` is `USERPROFILE` then `HOME` (`install.sh` 129–137, `install.ps1` 92–95).

A user who “removes the system” by deleting the checkout therefore still has slash commands on disk, a recorded absolute `source_root`, and (for global) rewritten command files pointing at `<home>/.advanced-plans/bin/ap.py`.

### What breaks, and is it diagnosable?

**Stale record, launcher still present** (the case you asked about): diagnosable. The launcher runs, reads `runtime.json`, looks for `platforms/python/__init__.py` under `source_root`, and fails with exit 3. The message names the manifest, the key, that the checkout was “moved, renamed or deleted”, and the repair (re-run the installer, `/sync-install`, or edit the file):

```331:339:platforms/python/ap_launcher.py
        if not os.path.isfile(os.path.join(root, PACKAGE_MARKER)):
            raise Unreachable(
                "%s records %s = %r, but there is no %s under it - the "
                "checkout has most likely been moved, renamed or deleted"
                % (manifest, MANIFEST_KEY, root, PACKAGE_MARKER),
                "re-run the installer from the checkout's new location "
                "(setup/claude-code/install.ps1 or install.sh), or run "
                "/sync-install, or edit %s so %r points at it."
                % (manifest, MANIFEST_KEY))
```

That is pinned by `test_moved_checkout_is_named_not_a_module_error`. A project with a stale `runtime.json` does **not** fall through to a still-valid global record: a present project manifest wins (`resolve()` uses the first manifest it finds). The operator has to fix or remove that file.

**Launcher file gone, commands still there**: not diagnosable by this system. The interpreter dies with “can’t open file” before `ap.py` runs. The global installer’s own comment states that case (`install.sh` 196–198). `/sync-install` step 1b knows this as a distinct failure (`sync-install.md` 67–68) and tells the *agent* to copy the launcher; a human staring at a shell error does not get the product name or the repair.

**Planning data** in `.advanced-plans/phases/`, `PLANNING.md`, `state/` is untouched either way. The mechanism files sit in the same directory as user data, and the code is silent on how to separate them.

**Verdict.** Fine for the stale-checkout case the guard was built for. Wrong as an uninstall story: there isn’t one, mechanism files are mixed into the data home, and “delete the launcher but leave the commands” is the same pre-guard failure this work was meant to replace. An uninstall that removed `.claude/` plus `.advanced-plans/{runtime.json,bin/}` (project and profile) and left planning artefacts would close that; a page of docs plus a small script. Cheap. Not doing it is a product gap, not a launcher bug.

---

## Q2 — Upgrade in place

**The skip guard does not skip the runtime.** Both project installers write `runtime.json` and overwrite `bin/ap.py` **after** the “planning data already exists, skip scaffold” branch, and they say so in comments:

```357:371:setup/claude-code/install.sh
# ---------------------------------------------------------------------------
# Shared Python runtime: launcher + recorded source path
#
# ...
# Deliberately OUTSIDE the scaffold guard above: that guard skips everything
# when .advanced-plans/ already exists, and an upgrade-in-place is exactly the
# case where the recorded path most needs refreshing.
# ---------------------------------------------------------------------------
say "Recording the shared Python runtime..."
do_mkdir "$AP_DIR/bin"
do_cp "$REPO_ROOT/platforms/python/ap_launcher.py" "$AP_DIR/bin/ap.py"
```

Same structure in `install.ps1` 273–305 (`Copy-Item -Force`, then `WriteAllText` over `runtime.json`). A second install from a moved checkout **does** repair `source_root` and refresh the launcher copy. Planning data is left alone. Commands/agents/skills/schemas are copied again.

That property is pinned by `test_installer_records_the_runtime_outside_the_scaffold_guard` (`test_ap_launcher.py` 743–772), which asserts the last `runtime.json` write sits after the last “skipping scaffold” line in both `install.sh` and `install.ps1`.

**Global has the same repair property, by a simpler route.** There is no scaffold skip. `--global` / `-Global` always:

1. copies commands and rewrites the launcher path
2. copies `ap_launcher.py` → `<home>/.advanced-plans/bin/ap.py`
3. overwrites `<home>/.advanced-plans/runtime.json` with the current checkout

(`install.sh` 184–241, `install.ps1` 113–202.) Re-running from a new location repairs the stale path.

**They are consistent on the question you asked.** Project and global both refresh the record on re-run. Global is not “the same code path”; it never had a skip to get wrong.

One caveat, since you named `platforms/claude-code/install.sh`: that file’s **project** path (`install_project`, lines 60–129) still does not write `runtime.json` or copy the launcher at all. Only its `--global` branch does. Re-running *that* installer over an existing project does not repair a stale record. The setup/ scripts are the ones that have the upgrade property; the adapter copy is not equivalent.

**Verdict.** The setup/ design is fine. I would not change it. I would either delete or relegate `platforms/claude-code/install.sh`’s project path so it cannot be used as a silent no-op upgrade — cheap, and it is the one installer that actually has the bug this section was written to prevent.

---

## Q3 — Python not on PATH

**The user never reaches the launcher.** Call sites are the bare word `python`:

```
python ".advanced-plans/bin/ap.py" <module> [args]
```

and inline `python -c "... runpy.run_path(...)['bootstrap']()"`.

If `python` is missing, the shell fails immediately (`command not found` / `'python' is not recognized`). If it is the Windows Store stub, that stub prints its own “Python was not found…” and exits. If it is Python 2, the file is opened; `except ValueError as exc` may parse on 2.6+, then `import pathlib` dies with a raw traceback. In all three cases **the guard does not run**. `Unreachable.report()` only exists after the interpreter has started this file.

The design already treats interpreter-level failure as a different class of bug. The relative-path-from-subdirectory test is explicit: “The interpreter, not the guard: exit 3 here would mean the launcher ran” (`test_ap_launcher.py` 526–529). `docs/adapting-to-new-platforms.md` 137–141 says the same for cwd: CPython exits 2 before the guard can speak. The code is **silent** on PATH, the Store stub, and Python 2. There is no `command -v python`, no `py -3`, no `python3` fallback in the installers or the launcher. (`next-phase.md` 366 and 558 even use `python3 -c` for hashlib, which is a worse Windows default, but those snippets do not go through `ap.py` anyway.)

**Is this outside the boundary?** Mostly yes. This mechanism solves “the runtime tree is not on `sys.path`”, not “which binary is Python”. Wrapping every call site in a finder (`py -3` / `python3` / `python`) would be a different product, would have to live in Markdown that Claude Code executes as shell, and would still fail if nothing named Python exists. The one cheap thing inside the boundary is a one-line prerequisite in `setup/claude-code/README.md` (it currently lists only Claude Code and a clone of this repo — lines 11–14). I would do that and stop. Inventing an interpreter shim here would cost more than it is worth.

---

## Q4 — Does the mechanism duplicate code that can drift?

Yes, and more than the two Python functions.

`ap_launcher.global_home()` (96–111) and `install_audit.resolve_global_home()` (87–113) both walk `USERPROFILE` then `HOME`. The stated reason is sound **in one direction**: the installed `ap.py` is a standalone stdlib file that must run before `platforms` is importable, so it cannot import `install_audit`. That is real, not a rationalisation.

It does not justify keeping a second Python copy. `install_audit` *can* import `ap_launcher` (it already lives in the checkout and is invoked *after* bootstrap). One function in the launcher, a thin wrapper or a direct call in `install_audit`, and the Python pair cannot drift. Cost: a few lines.

The test (`test_global_home_agrees_with_install_audit`, 261–284) is an adequate control **for the cases it pins**: both vars set, only `HOME`, only `USERPROFILE`. It is not a complete pin:

- Last-resort differs and is untested: `os.path.expanduser("~")` vs `pathlib.Path.home()`.
- It compares two in-checkout modules. It does not compare the **installed copy** of `ap.py` against `install_audit`.
- The same rule exists a third and fourth time in the installers (`ap_home_fs` / `Get-ApGlobalHome`) and again in `platforms/claude-code/install.sh`. Those are not covered by the Python test.

So: launcher-must-stay-standalone is a good reason not to import `install_audit` from `ap.py`. It is a weak reason to duplicate the function in `install_audit`. The test is a decent alarm for the two Python bodies, not an adequate control for the whole USERPROFILE-before-HOME rule. The real drift risk is the shell/PowerShell copies, which is how this class of bug actually ships. I would have `install_audit` call `ap_launcher.global_home` (cheap) and leave the installer copies — they cannot import Python — documented as independently maintained, or add a small installer test that the written global path matches `global_home()`. That last piece is the one I would actually worry about.
