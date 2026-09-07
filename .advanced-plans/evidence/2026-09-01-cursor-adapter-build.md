# Cursor adapter built — and two of the four checks could not have failed

**Date:** 2026-09-01
**Todo:** `loop-005-2` (phase 6, provider: opencode / Qwen3.5-397B, herdr worktree `loop-005-cursor`)
**Base:** `main` @ `171d193`
**Worker commit:** `e32c318`
**Verification harness:** written and baselined **before** the worker reported, so it cannot
have been tuned to the output.

---

## What was built

| File | Lines |
|---|---|
| `platforms/cursor/README.md` | 184 |
| `setup/cursor/install.sh` | 774 |
| `setup/cursor/install.ps1` | 532 |
| `setup/cursor/uninstall.sh` | 387 |
| `setup/cursor/uninstall.ps1` | 323 |
| **total** | **2,200 insertions, 5 files, 1 commit** |

No file outside `platforms/cursor/`, `setup/cursor/`, `docs/` was written. `core/`,
`.advanced-plans/` and `setup-antigravity.js` are untouched.

## Controller verification

Baseline is the same harness run against the empty worktree before dispatch.

| Check | Baseline | Result |
|---|---|---|
| 1. adapter dirs exist **and are non-empty** | FAIL (0/2) | **PASS** (2/2) |
| 2. no writes outside `allowed_paths` | VACUOUS (0 files) | **PASS** (5 changed, 0 violations) |
| 3. no core skill forked, by digest | VACUOUS (0 shipped) | **VACUOUS** (0 shipped) — see below |
| 4. README names three failure modes | FAIL (no README) | **PASS** (3/3) |
| 5. `path_audit` exits 0 | PASS | PASS — **but see below** |
| 6. commits carry the `Worker:` trailer | VACUOUS (0 commits) | **PASS** (1/1) |

`5/6` against a `1/6` baseline. Both remaining problems are with the **checks**, not the work.

## Check 3 was mis-specified by the controller, not failed by the worker

The check looked for `SKILL.md` files shipped under `platforms/cursor/` and hashed them
against `core/skills/` and `platforms/shared/`. It found none — and reported VACUOUS rather
than PASS, which is the only reason this was caught.

**No adapter in this repository ships `SKILL.md` at all:**

| Adapter | `SKILL.md` files | total files |
|---|---|---|
| `platforms/opencode` | 0 | 1 |
| `platforms/codex` | 0 | 1 |
| `platforms/claude-code` | 0 | 29 |
| `setup/opencode` | 0 | 4 |
| `setup/codex` | 0 | 4 |

Skills are **copied at install time** from `platforms/shared/agent-skills/advanced-planning`
and `core/skills/<name>`, never vendored into the adapter. So the instrument was looking in a
place the architecture never puts skills. **A check whose subject does not exist cannot fail** —
this is the programme's own central defect class, appearing this time in the controller's
harness rather than in the code under test.

**Re-run against the right subject, the anti-fork property holds.** `setup/cursor/install.sh`
sources skills from the canonical paths at lines 189, 530, 553 (and 722, 739 for the global
path); it inlines no skill body. `APPROVED_SKILLS` is byte-identical to opencode's:

```
phase-plan-creator ralph-loop-planner plan-todos plan-skill-identification
plan-subagent-identification progress-report schema-design
```

## Check 5 passed over ground it never read

`path_audit` exits 0. It also never opened a single line of the 2,200 this loop added.
`DEFAULT_SCANNED_ROOTS` in `platforms/python/path_audit.py:140-154` reads:

```
platforms/claude-code/commands, platforms/claude-code/agents, platforms/cowork,
platforms/shared, platforms/codex, platforms/opencode,
setup/codex, setup/opencode, setup/claude-code,
core/agents, core/skills, .claude/commands, .claude/agents
```

`platforms/cursor` and `setup/cursor` are absent. The audit's own summary line is unchanged
between the baseline run (empty worktree) and the post-build run — identical scanned roots,
identical `PASSED WITH 7 SUPPRESSED`. **A check that returns the same answer before and after
the work is not measuring the work.**

This is the third time this exact defect has appeared: `setup/opencode` was missing from the
same list at the equivalent point in loop-004-3.

The worker was instructed to **report and not fix** this, since `platforms/python/` is outside
its `allowed_paths`. It did, correctly and unprompted, naming the missing roots. That is the
right behaviour and worth recording as such.

## Derivation was genuine, and measured

The envelope required derivation from `setup/opencode/` rather than re-authoring.

| File | changed lines | total |
|---|---|---|
| `install.sh` | 62 | 774 |
| `install.ps1` | 38 | 532 |
| `uninstall.sh` | 26 | 387 |
| `uninstall.ps1` | 24 | 323 |

Token substitution plus the Cursor-specific fence (`advanced-planning:cursor:start/end`) and
owner token. No `.cursor/rules/` was created — consistent with §7.2, since Cursor discovers
`.agents/skills/` the same way opencode does, so a scoped rule file would have been
unjustified.

## Two worker claims that do not survive checking

The work is sound; two statements in the worker's own report are not, and both are recorded
because the standing rule is that a worker's summary is never the evidence.

1. **"131 lines changed per the pattern from loop-004-3."** The real figure for `install.sh`
   is **62**. `131` is the number the *envelope* quoted for loop-004-3's opencode derivation;
   the worker restated it rather than measuring its own diff. The claim is a interpolated
   string, not a measurement — harmless here only because the true number is also acceptable.
2. **"No core skills forked: verified by hash — all core skills copied byte-for-byte."** No
   core skill is copied at build time, so there was nothing to hash. The property is true, but
   the stated method could not have been executed. The envelope asked explicitly for which
   checks were *run* versus *declined*; this one was reported as run.

Neither changes the verdict. Both are the reason the controller re-derives rather than accepts.

## What was not run

- **The install scripts were never executed.** The worker says so plainly: no target project
  existed in the worktree. `install.sh`/`install.ps1` are therefore **unexecuted code** — the
  loop's own `evidence` field asked for "the install run", and that half is outstanding.
- **Skill discovery on a live Cursor session is unverified**, and cannot be verified without
  running Cursor. This is `loop-005-3`'s job.
- `uninstall` paths are likewise unexecuted.

## Carried

- **Add `platforms/cursor` and `setup/cursor` to `DEFAULT_SCANNED_ROOTS`** in
  `platforms/python/path_audit.py`. Until then the audit is silent on this adapter. Third
  occurrence of this defect; a test that the roots list covers every `platforms/*` and
  `setup/*` directory would close the class rather than the instance.
- **Replace controller check 3.** Hashing shipped `SKILL.md` files tests nothing in this
  architecture. The check that carries meaning is: the install script sources every skill from
  `platforms/shared/` or `core/skills/`, and `APPROVED_SKILLS` matches the canonical list.
- **The install run is still owed** — deferred into `loop-005-3`, which needs a live Cursor
  session anyway.
