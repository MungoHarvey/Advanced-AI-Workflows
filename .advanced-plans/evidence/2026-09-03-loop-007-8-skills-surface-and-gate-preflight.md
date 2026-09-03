# loop-007-8 — the audit made to look at the surface the hosts read

Date: 2026-09-03
Repository: `advanced-planning`, worktree `loop-008-gate`
Commits: `05d1e55` (opencode/Qwen worker `instaudit-impl`), `f16ae91` (controller corrections)
Discharges: criterion 1 — the rewritten form

## What was wrong going in

loop-007-6 rewrote criterion 1 around `install_audit` and wrote a regression test with it.
loop-007-7's global install then exposed two defects that the rewrite's own wording already
required and the test could not see:

1. `install_audit.SURFACES` had **no skills surface**. The four hosts were measured reading
   skills, and loop-007-6's digest table found 6 of 7 shared skills drifted in the global
   layer. The instrument criterion 1 names was blind to the exact files criterion 1 is about.
2. The gate preflight called `--layers all`. `install_audit` resolves the project layer as
   `find_repo_root(__file__) / ".claude"` (`install_audit.py:439,449`) — the *framework*
   checkout, never the project the gate runs in. Measured from AAW: it audited the worktree's
   own `.claude`, which holds only `settings.json`, reported 27 MISSING and exited 1. That made
   the gate's WARN unconditional and permanent, so real drift was indistinguishable from it.

## The preflight, accepted as the worker wrote it

`run-gate.md` now calls `--layers source,global`, which resolves from `USERPROFILE` and works
from any project. The reason sits next to the call, cites `install_audit.py:439,449`, and
records the 27-MISSING measurement. The tightened test asserts equality, so `all` can no longer
satisfy it, and `test_every_layer_argument_is_one_the_parser_accepts` — the control that caught
the original `source,project,global` mistake — is untouched.

**Mutation-checked.** Restore `--layers all` in `run-gate.md` and
`test_the_preflight_covers_the_global_layer` fails; restore `source,global` and it passes.

## The skills surface, rebuilt twice

### First rebuild — the worker's, and why it could not stand

The worker added `("core/skills", "skills")` with an `is_dir_per_item` flag and a second walk
that collected only `NAME/SKILL.md`. It works for the check as literally worded, and the worker
demonstrated red-green on a `SKILL.md`.

It is a **false green** on everything else. Driving the real `audit_pair` over temporary layers:

```
RESTORE SKILL.md, PLANT drift in references/catalogue.md:
  after references edit: skills rows seen = 1
     current  skills/demo-skill/SKILL.md
```

The audit affirms `current` for a skill whose installed `references/` file differs. Seven such
files exist:

```
phase-plan-creator/references/phase-plan-template.md
plan-skill-identification/references/skill-catalogue.md
plan-subagent-identification/references/agent-catalogue.md
plan-todos/references/todo-schema.md
progress-report/references/progress-report-template.md
ralph-loop-planner/references/ralph-loop-template.md
ralph-loop-planner/references/todo-schema.md
```

`setup/claude-code/install.sh:331-336` copies the whole skill directory (`do_cp "$skill_dir"`),
and all seven were confirmed present under `~/.claude/skills/`. The planning skills read them at
runtime. An affirmative "current" over a file that differs is the defect class this phase exists
to remove, one level down from where it was found.

The worker's `test_skills_surface_is_defined` asserts the table entry, and was **measured to pass
against the SKILL.md-only walk**. The loop's own check anticipated this: *"a table entry alone
does not prove the walk reaches it."* It is not a guard.

### Second rebuild — and the correction to my own critique

I first replaced the branch with a plain `("core/skills", "skills")` on the existing recursive
walk, which keys on the path relative to the surface root and already handles nested items. That
is correct on the source side and it made the audit **stop completing**.

The installed `skills/` directory is not the framework's alone. Measured on this machine:

```
top-level entries: 261
total files under it: 18404      (17946 of them one unrelated tool's)
```

Walking it wholesale hashes every file and would report 250-odd unrelated skills as `extra` —
noise, not drift. **The worker's branch avoided that blowup**, though by narrowing to `SKILL.md`
rather than by scoping to what we install, and it dropped `references/` to do it. So the surface
did need a distinction; it just is not "directory-per-item". It is that the installed directory
is a shared namespace and the framework owns 9 of its 261 entries.

`SURFACES` entries now carry `shared_namespace`. For such a surface the installed side is
enumerated per source-declared item, so drift inside one of our skill directories — including a
stale extra file — is still visible, and directories the framework never installed are not
policed.

### The controls, run by the controller

```
GREEN baseline (identical copies):
  current  skills/demo-skill/SKILL.md
  current  skills/demo-skill/references/catalogue.md
PLANT drift in installed SKILL.md:
  stale    skills/demo-skill/SKILL.md
  current  skills/demo-skill/references/catalogue.md
RESTORE, PLANT drift in references/catalogue.md:
  current  skills/demo-skill/SKILL.md
  stale    skills/demo-skill/references/catalogue.md
```

Both kinds go red and green independently.

**Three mutation checks, all confirmed:**

| mutation | test that must fail | result |
|---|---|---|
| narrow the skills walk back to `SKILL.md` only | `test_the_skills_walk_reaches_a_nested_reference_file` | FAILED |
| widen the installed walk back to wholesale | `test_the_skills_walk_ignores_directories_the_framework_never_installed` | FAILED |
| restore `--layers all` in `run-gate.md` | `test_the_preflight_covers_the_global_layer` | FAILED |

Two hardcoded lists that broke on the new surface now derive from their source of truth: the
surface count in `test_audit_nonempty_subject.py` from `SURFACES`, and the gitignore fixture in
`test_install_audit.py` from `_AUDITED_SURFACES`, which itself gained `skills`. Both were the
same defect as the count they replaced — a check spelling out what another file declares.

## The live audit

```
=== source -> global (C:\Users\mharvey2\.claude) ===
  STALE     commands/run-gate.md
  Summary: 42 current, 1 stale, 0 missing, 0 source-missing, 13 extra  (total: 56)
```

56 rows, up from 40 — exactly the 9 `SKILL.md` plus 7 `references/` files. One second. The one
stale file is `commands/run-gate.md`, which this loop edited and the global copy has not been
re-synced to, so the audit is reporting real drift rather than a permanent false positive.

## The suite, and the five failures that are not this loop's

```
5 failed, 1092 passed, 1 skipped
```

All five are in `test_ap_launcher.py`, and all five **reproduce identically at `05d1e55^`**, run
from a clean `git archive` of the parent commit. One measured cause:

```
profile record exists: True -> C:\Users\mharvey2\.advanced-plans\runtime.json
tmp dir is under the profile: True
find_manifest(orphan)    -> C:\Users\mharvey2\.advanced-plans\runtime.json
```

`pytest`'s `tmp_path` lives under the user profile, so `ap_launcher`'s upward walk climbs out of
the fixture and adopts the real global record. Those tests isolate `HOME` and `USERPROFILE` but
not filesystem ancestry. They were invisible until loop-007-7's global install created that
record — which is the *supported* installation, so the suite is red on any machine where the
product is installed globally.

One of them is named `test_the_profile_directory_is_never_adopted_as_a_checkout`, and
`test_find_manifest_walks_up_and_stops` carries a comment describing this exact machine-dependence
and handling two outcomes, neither of which is the one that now occurs. So this is either a
test-isolation gap or the product doing the thing those tests exist to forbid. That distinction is
a design call, it is outside this loop's scope, and it is referred up rather than patched.

## Criterion 1, scored

The audit covers the surface the hosts read, the walk is proven to reach nested files and proven
not to wander into other tools' trees, and the preflight reports drift the invoking project can
act on. Every check in the loop is discharged except *"suite green"*, which fails for five
reasons that pre-date the loop and belong to a different defect.
