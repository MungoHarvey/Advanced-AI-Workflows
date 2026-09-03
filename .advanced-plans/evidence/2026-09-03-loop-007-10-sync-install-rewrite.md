# loop-007-10 — the install path the audit cannot see, and a citation nobody opened

Date: 2026-09-03
Repository: `advanced-planning`, worktree `loop-008-gate`
Commits: `3949abd` (opencode/Qwen worker `syncinstall-fix`), `97ebd0b` (controller)
Discharges: a finding recorded in loop-007-8 and deliberately left open

## The defect

`setup/claude-code/install.sh` defines `ap_rewrite_call_sites` at line 224 and calls it
on each file copied to the **global** layer (`:293-307`), turning the two literal
launcher call-site forms from a project-relative path into an absolute one.

`platforms/claude-code/commands/sync-install.md` Step 4 (`:124`) said only:

```bash
cp <source_path> <installed_path>
```

So refreshing a stale file installs the un-rewritten relative form, and a refreshed
global install stops being what a fresh one produces.

## Why nothing caught it, measured rather than assumed

`install_audit._file_hash` applies `LAUNCHER_PATH_RE.sub(LAUNCHER_CANONICAL, ...)` before
hashing (`install_audit.py:159`), deliberately, so that install.sh's own rewrite does not
show as drift. Driving the real function over the two forms of the same file:

```
call sites in sync-install.md: 4
bytes differ on disk : True
plain     hash: f2b40fa3193def779e7b222dbb68f722a0584c36
rewritten hash: f2b40fa3193def779e7b222dbb68f722a0584c36
AUDIT SEES THEM AS IDENTICAL: True
```

The audit can never report this, and must not be changed to try — the normalisation is
what stops every correctly-installed global file reading as drift. The added test is
therefore the only guard there will be, which is why the loop demanded a mutation result
rather than a passing run.

## The fix

Step 4 now carries a **Global layer only** paragraph instructing the same rewrite, naming
`ap_rewrite_call_sites` and its file, and stating that the project layer keeps the
relative form as a plain `cp`. Mutation-checked by the controller: remove the paragraph
and `test_sync_install_step_4_rewrites_global_call_sites` fails; restore it and it passes.

## The guard had the defect it was written to catch

The worker's test asserted `"line 224" in step4_section` — that the prose *contains* the
string. It never opened `install.sh`. So the test's subject was a string the test itself
supplied, which is this programme's central defect class, arriving one level down from
where it was being fixed.

Demonstrated before changing anything. Inserting a single line near the top of
`install.sh` moves the function:

```
ap_rewrite_call_sites is now at line: 225
doc still says line 224
51 passed
```

The doc's citation is now false and every test passes.

The assertion now extracts the cited number and checks it against `install.sh` itself:

| mutation | result |
|---|---|
| move `ap_rewrite_call_sites` to 225, doc still cites 224 | `test_sync_install_step_4_rewrites_global_call_sites` **FAILED** |
| restore `install.sh` | 51 passed |

Both halves of the earlier mutation (removing the Step 4 paragraph) were re-run by the
controller rather than taken from the worker's report, and both reproduced.

## The suite

```
1099 passed, 1 skipped in 419.06s (0:06:59)
```

1098 before this loop plus its one new test, so nothing was dropped to reach it.

## Attribution

`3949abd` carries `Co-Authored-By: opencode (Qwen) via herdr worker syncinstall-fix` and
`Loop: loop-007-10`. It is the first worker commit in this programme to do so, and it
carried them because the envelope stated them verbatim — the enforcement point named in
`docs/agents/worker-attribution.md`, working first time.
