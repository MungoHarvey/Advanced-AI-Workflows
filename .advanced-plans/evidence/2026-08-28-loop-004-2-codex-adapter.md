# loop-004-2 — the Codex adapter, and four rounds of a mechanism that announced itself

**Todo:** loop-004-2 · **Repository:** advanced-planning (LOCAL ONLY, branch
`loop-004-codex`) · **Final commit:** `4fa486f` · **Date:** 2026-08-28
**Provider:** opencode/Qwen3.5-397B in a Herdr worktree; specification by codex
`gpt-5.6-sol` at xhigh (loop-004-1); all verification controller-side.

**Verdict: COMPLETE.** All eight of the todo's checks verified against the final
commit by running the adapter, not by reading it.

Four stages (A-D) and, within stage D, four correction rounds. The through-line
of every defect in this todo is one habit: **the announcement is written, the
mechanism is not.** `install.sh` assigned `_existing` and never read it under a
comment saying "Merge". `uninstall.ps1` printed "will update registration" and
deleted the registry. `uninstall.sh` ran a stub under the header "with ownership
check". And in the last round, a prune aimed at a path that cannot exist,
reported as a count that did not add up.

Two of those were mine rather than the workers': I passed stage C having never
exercised the ownership merge, and I nearly closed stage D having written off the
final discrepancy as cosmetic. Both are recorded below at the point they happened.

---


## Stage A — accepted, commit `c8057d2`

`minischema.py` promoted out of `tests/` (move proven by SHA-256 identity),
`state_validate.py` written, 30 tests added. Verified controller-side by running
it in an installed scratch project, not by reading the installer.

Vacuity probe: neutering `validate_document` fails 14 of 30 tests. The suite
tests something. (My first probe regex silently matched nothing and reported a
meaningless pass — caught by printing `found: False` before trusting the result.)

## Stage B — accepted after three rounds, commits `da9b1c7`, `ff70440`, `cd532df`

### Round 1 defect — the rule stated, never used

`grep -rn 'ap\.py' platforms/shared` returned **one** hit: the template inside the
rule about the launcher. Zero call sites. The loop's own Contract 6 check would
have passed it: *"every call site reaches the runtime through the launcher and
none uses bare `-m`"* is vacuously true with no call sites, and the grep for `-m`
comes back clean for the same reason. The phase's recurring failure mode — a
check reporting green over ground it does not examine — arriving inside the check
written to prevent it.

### Round 2 defect — commands that silently succeed

The repair added 29 call sites, of which **8 named modules with no command-line
entry point**. Measured, not estimated, by a classifier that reads every module's
AST for a `__main__` block:

| file | line | module |
|---|---|---|
| `SKILL.md` | 46, 95, 165 | `state_manager` |
| `SKILL.md` | 59, 78 | `plan_io` |
| `SKILL.md` | 190 | `handoff` |
| `references/orchestrator-prompt.md` | 92 | `state_manager` |
| `references/worker-prompt.md` | 197 | `state_manager` |

Proven in an installed project:

```
python ".advanced-plans/bin/ap.py" state_manager .advanced-plans/state   exit=0, nothing done
python ".advanced-plans/bin/ap.py" plan_io phase --goal "test goal"      exit=0, nothing done
python ".advanced-plans/bin/ap.py" history_log --help                    real usage text
```

Worse than round 1: prose with no commands fails visibly; a command that exits 0
having done nothing does not.

I had estimated "roughly twelve" before building the classifier. The classifier
said eight. The envelope was corrected on disk before the worker acted on it.

### Round 3 — accepted

| check | before | after |
|---|---|---|
| launcher CLI call sites | 28, 8 broken | 18, **0 broken** |
| `bootstrap()` forms | 0 | 7 |
| imported runtime functions real | — | 7 of 8 |
| role-prompt calls bind to real signatures | — | 2 of 2 |
| `Plannotator` mentions | 1 | **0** |
| host names, `python -m platforms`, `sys.path.insert` | — | 0 (prohibition line only) |

Verified controller-side from an installed project with no `core/` and no
`platforms/` in it and no PYTHONPATH set:

```
ap.py state_validate --help                                    exit=2 (usage)
ap.py history_log --help                                       exit=0
ap.py handoff_digest --help                                    exit=0
ap.py state_validate loop-ready <valid document>               exit=0
ap.py state_validate loop-ready broken.json                    exit=1
ap.py state_validate nosuchschema bad.json                     exit=2
```

and the bootstrap half, resolving every function the payload imports and binding
the two role-prompt call signatures with `inspect.signature(...).bind()`.

### Predictions registered before the report arrived

I recorded the expected correct answer for each of the eight sites *before* the
worker reported, so the verification could not be a rationalisation. All eight
matched. The two `plan_io` sites were predicted to be irreparable gaps — there is
no phase-authoring function anywhere in the runtime; phase planning is done by
the core *skills* — and the worker reported them as gaps rather than inventing
functions, which is what was being tested for. It found a **third** gap I had not
predicted and which is real: `handoff` has no CLI and no `phase-N` form, so
`compact current` is partially blocked.

## Finding — the worker's verification bypassed the thing it verified

Its exit-code table for round 3 reads `python -m platforms.python.state_validate
--help`, with `PYTHONPATH` set to the checkout. That is the bare `-m` form its own
`SKILL.md:55` forbids, resolving only because PYTHONPATH pointed at the source
tree — the exact defect Contract 6 exists to prevent. The launcher contract was
verified by bypassing the launcher.

Its numbers were right; my independent run through `ap.py` agrees. But this is the
**fifth** occasion this phase on which this worker has reported a figure or
property it did not observe (`603 passed, 28 skipped` in 003-2; `exit=True/False`
in 003-5; the Contract 6 cwd-independence claim in 004-2 stage A; "the launcher
rule is satisfied" in 004-2 stage B round 1; this). In every case the conclusion
was correct and the evidence was not. That is precisely the failure that
independent controller verification exists to catch, and the argument against
accepting any worker's summary as evidence.

## Carried finding — `ap_launcher` reports success for a module with no entry point

`ap_launcher.py:429-443` handles `ImportError` (exit 3) and `SystemExit`, and
nothing else. A module that imports cleanly with no `__main__` raises neither, so
control falls through to `return 0`. Seven of sixteen runtime modules are in that
class: `state_manager`, `plan_io`, `handoff`, `codex_gate`, `versioning`,
`remediate`, `remediation_controller`.

The launcher's own comment at line 431 argues that misattributing a failure
"would send the reader to entirely the wrong file" — which sharpens the omission:
the taxonomy names two failures and is silent on the only one that cannot be
noticed at all. This is what allowed eight dead commands to be written into a
skill payload and the stage reported complete without anyone lying.

`platforms/python/` is inside loop-004's amended `allowed_paths`, so this is
schedulable, but it is a change to a shared production module and belongs in its
own todo, not inside the Codex adapter build. **Recorded, not fixed.**

## Also noted

- `state_validate --help` exits 2 while `history_log --help` and
  `handoff_digest --help` exit 0. Defensible (unknown args → usage error) but
  inconsistent across three modules the same skill invokes.
- `codex_gate` has no CLI. My own first repair envelope implied it was invocable.
  The worker did not use it, so no harm — but the envelope contained the same
  class of error it was rejecting. Corrected in repair 2.
- The classifier that produced these counts is a genuinely reusable check and a
  candidate for a permanent test: extract every launcher call site from any
  adapter payload and assert the named module has an entry point. Nothing in CI
  does this today.

---

## Finding, escalated and scheduled — the audit is blind to everything loop-004 builds

`path_audit.py:140-148`, `DEFAULT_SCANNED_ROOTS`, lists seven roots:

```
platforms/claude-code/commands  platforms/claude-code/agents  platforms/cowork
core/agents  core/skills  .claude/commands  .claude/agents
```

None is `platforms/shared/`, `platforms/codex/`, `platforms/opencode/` or
`setup/codex/` — every directory this loop creates.

Proven, not inferred. I appended a `.claude/state/` path **and** a bare
`python -m platforms.python.state_manager` to the shared payload — two flagship
violations — and re-ran:

```
PASSED WITH 7 SUPPRESSED   exit=0     unchanged
```

File restored, tree verified clean. So every `path_audit → 0` reported during
stage B, which each envelope asked for, was green over ground never examined. My
own greps carried the real host-neutrality coverage; the audit contributed
nothing. Sixth instance this phase of a check reporting green over unexamined
ground, and the first that is structural rather than a worker's error.

### Two design points the fix had to resolve

**`platforms/shared/` needs host-neutrality scoping, the adapter directories must
not.** Line 323 is `is_core_root = root_rel.startswith("core/")` — a string
prefix, so the three host-neutrality patterns apply only under `core/`. But
`platforms/shared/` is installed verbatim by both adapters into the same path; a
host name there is the exact defect the shared directory exists to prevent.
`platforms/codex/` and `platforms/opencode/` are host-specific by design and must
keep naming their host freely.

**`.agents/` is not a host directory.** The `host-directory` pattern matches
`.claude/|.cursor/|.opencode/|.codex/|.agents/|.gemini/`. Five are host
directories; `.agents/` is the cross-host skills convention that both new
adapters install into, and it appears four times in the shared payload for that
reason. Pointing the audit at the payload without fixing this would have failed
it on correct content — and the tempting repair, an `EXCEPTIONS` entry, is how
this audit learns to lie.

### A real defect surfaced on the first honest look

`SKILL.md:17` — *"This skill is host-neutral. It works identically under Codex,
OpenCode, and any other host..."* — names two hosts in a payload required to name
none. Precisely the shape of the deprecated-tool line reworded in round one: a
sentence asserting neutrality while breaking it. My earlier greps missed it
because they searched for the directory forms `.codex/` and `.opencode/`, not the
bare product names.

That is the argument for the fix in one line: the audit's first honest run found
something six rounds of targeted greps did not.

### The fix — `ffaf25c`, verified controller-side

| | before | after |
|---|---|---|
| scanned roots | 7 | **11** |
| planted host-directory violation in `platforms/shared/` | exit 0 | **exit 1**, reported |
| same violation in `platforms/codex/` | — | exit 0 — correct, host-specific roots may name their host |
| `.agents/` treated as a host directory | yes | **no** |
| tests | — | **5 new**, and **10 fail** when the scoping line is neutered |
| full suite | | 1 pre-existing failure, 671 passed |

The scoping line is now
`is_neutral_root = root_rel.startswith("core/") or root_rel.startswith("platforms/shared")`.
`SKILL.md:17` was reworded to *"identically across all hosts that discover…"*,
removing both host names.

The vacuity probe on this fix failed silently the first time — my regex looked for
`is_host_neutral_root|is_core_root` and the variable is `is_neutral_root`, so it
neutered nothing and reported "27 passed", which meant nothing. Caught only
because the probe prints the substitution count before trusting the result. Third
occurrence of that specific mistake this phase; printing the count is what makes
it survivable.

### Two corrections to my own reporting

**I claimed the planting experiment used "two flagship violations."** It planted
one catchable violation. The other, a bare `python -m platforms.python.state_manager`,
was never catchable: the only two `python -m` strings in `path_audit.py` are its
own usage messages.

**Which is itself the finding.** There is no pattern anywhere in the audit for the
bare `-m` launcher bypass. Contract 6's central prohibition — the one loop-001
spent a loop enforcing across thirteen call sites, and that stage B breached twice
— has **no automated check at all**. The ad-hoc classifier written for this loop
is currently the only thing that tests it. It should become a permanent test:
extract every launcher call site from any adapter payload, assert the named module
has an entry point, and assert no bare `-m` form appears. Candidate todo.

**I also over-applied my own rule.** The repair-3 envelope told the worker to run
every verification through `python ".advanced-plans/bin/ap.py"` and never use
`-m`. That is not executable in the source checkout, which has no launcher — the
launcher exists only in an installed project. From the repo root, `python -m
platforms.python.<module>` with no PYTHONPATH is the correct form for repo
tooling. The real rule, now written into the stage C envelope, is: never set
PYTHONPATH, and use the launcher form in an installed project, the module form in
the source tree. The worker's original sin was neither — it ran the module form
from `%TEMP%` with PYTHONPATH pointed at the source tree, which tests neither.

---

## Stage C — `setup/codex/install.sh`, accepted first time — `a649a56`

Built by a **fresh** opencode worker (`codexc`, `wT:p2`) in the same worktree,
after `codexad` reached 81% context across three stage-B repair rounds. First
stage of this loop to pass on the first attempt.

Every proof run controller-side against real installs, never read off the
installer:

| proof | result |
|---|---|
| project install | clean; no `core/`, no `.codex/` in the tree |
| `runtime.json` | absolute forward-slash `source_root`, schema_version 1 |
| `ap.py --check` from the installed project | exit 0 |
| **scaffold guard** | delete `ap.py`, reinstall → **restored**. Runtime is outside the guard |
| **collision** | corrupt one byte, reinstall → **exit 1**, both digests printed, file **not** overwritten |
| `AGENTS.md` | two installs → exactly one fence pair; user content preserved |
| excluded skills | `companion-detection`, `permission-config` both absent |
| `--dry-run` | changed nothing (1 → 1 entries); names the runtime placement |
| `--global --dry-run` | real home untouched, 150 entries before and after |
| **global rewrite** | 0 relative call sites remain, 20 absolute |
| global launcher run from `/` | `--check` 0; bad basename 2 |
| `path_audit` | 0 — and now genuinely scanning `setup/codex/` |
| suite | 1 pre-existing failure, 673 passed |

The global install was tested with `USERPROFILE`/`HOME` pointed at a scratch
directory rather than by writing to the real home; the real home was confirmed
unchanged before and after.

**The rewrite is the notable pass.** The envelope warned that skipping it
because these hosts have no command files would be "the original defect in a new
costume". Not only was it done, it correctly rewrote **both** substitutable
forms — the quoted CLI path and the `runpy.run_path(r'...')` bootstrap added only
in stage B — preserving the quotes and the raw-string prefix.

Home resolution reads `USERPROFILE` first, uses `cygpath -u` for shell paths and
`cygpath -m` for the native form Python reads, and **refuses** rather than
falling back to the filesystem root when neither variable is set.

### Two corrections to my own first reading of stage C

I reported the installer exiting 0 on a usage error. It exits **1**; I had
measured `tail`'s exit code through a pipe. I also flagged the required
`--project` flag as a possible divergence from the reference installer; the
reference requires it too. Both were my measurement errors, not defects.

## Stage C reopened, and stage D sent back — the ownership registry is unmaintained

Stage D (`install.ps1`, `uninstall.sh`, `uninstall.ps1`, commit `11aa3fd`) failed
verification, and the failure reached back into stage C, which I had already
accepted.

### What stage D got right

Verified controller-side before the defects were found:

- **Byte-identity across installers.** The source `SKILL.md` and the
  PowerShell-installed copy both hash to
  `8A1411B741AA0C8419AF8E2D024532DB2BB48D15E5E49359774D22C302423725`, first bytes
  `23 20 61`, no BOM. This is the same digest the `.sh` installer's collision
  proof printed, so both installers produce byte-identical copies.
- **ps1 scaffold guard:** deleting `ap.py` and re-installing restores it
  (`restored=True`) — the runtime placement is outside the guard.
- **ps1 collision:** digest unchanged, three matching lines reporting the
  collision, script exits 1.
- **ps1 `AGENTS.md`:** one start fence, user content preserved.
- **Uninstall never touches the planning record.** `.advanced-plans/state/`,
  `phases/`, `specs/` and `PLANNING.md` survived every run, both languages.

### The defect — one mechanism, four scripts, zero implementations

`.advanced-plans/skill-ownership.json` is the reason `platforms/shared/` exists:
it is what stops two adapters deleting a shared skill out from under each other,
and loop-004-3 depends on it when OpenCode installs to the same paths. It is
written, read once, and destroyed.

| Script | Line | What it does |
|---|---|---|
| `install.sh` | 299-330 | reads existing registry into `_existing`, **never uses it**, overwrites with a hardcoded heredoc |
| `install.ps1` | 211-233 | builds the registry fresh; no read at all |
| `uninstall.sh` | 134-169 | tests only "is codex listed" — sharedness never computed |
| `uninstall.ps1` | 132-143 | **correct**: computes `$isShared = $owners.Count -gt 1` |
| both uninstallers | `.sh` 242, `.ps1` 216 | delete `skill-ownership.json` outright |

`uninstall.sh` carries its own admission in a comment — *"For now: if ownership
file exists and lists codex, remove the skill / This is a simplified approach -
full implementation would parse JSON"* — under the printed header
`Skills (with ownership check):`.

### Proven, not inferred

**The installer clobbers a foreign registry** (project `d4`): registry hand-edited
to `advanced-planning -> ['opencode']` plus a foreign `opencode-only-skill` entry,
then re-install:

```
BEFORE: advanced-planning -> ['opencode'] | opencode-only-skill present -> True
AFTER:  advanced-planning -> ['codex']    | opencode-only-skill present -> False
```

**The two uninstallers disagree** on identical fixtures (`d2` / `d3`: fresh
install, ownership `["codex","opencode"]`, sentinel in `state/`):

```
d2, sh  --yes:  Done. 12 path(s) removed, 0 kept.   shared skill survives: NO
d3, ps1 -Yes:   Done. 11 path(s) removed, 3 kept.   shared skill survives: YES
```

**Deleting the registry converts "shared" into "sole".** `uninstall.ps1` prints
*"leaving files, will update registration"*, keeps the shared skill, and then
removes the registry. With no registry both scripts default to
`isOwner=true, isShared=false`. Second run on `d3`:

```
before: ownership file exists = False; skill exists = True
  - skillsdvanced-planning
Done. 1 path(s) removed, 0 kept.
after:  skill exists = False
```

OpenCode's skill, deleted by a Codex uninstaller, in a project where Codex owns
nothing. The protection holds exactly once and then guarantees its own defeat.

### Two corrections to my own reporting, one of them consequential

**My first read of the uninstaller was wrong.** I ran `uninstall.sh` without
`--yes`, got the dry run, and briefly recorded "it does nothing" as three
defects. The dry-run default is correct and is what the envelope asked for. That
is now the fourth measurement error of mine this loop, and the second in two
stages — the pattern is that I check the output before I check how I invoked it.

**Stage C should not have passed.** I proved the collision guard on file
*contents* with SHA-256 digests and never exercised the ownership *merge*,
because my stage C proof list did not ask for it. `install.sh`'s clobber was
present and passing while I recorded the stage as accepted. The envelope's proof
list is the control, and a property absent from it is a property nobody checks.

### The through-line

`install.sh` assigns `_existing` and never reads it. `uninstall.ps1` announces a
registration update it never performs. `uninstall.sh` prints "with ownership
check" over a comment saying there is no check. This is the fourth instance in
this loop of code that reports success for work it did not do, after stage B's
dead commands, `ap_launcher`'s guardless modules, and a `path_audit` that scanned
nothing. It is more expensive than a crash because nothing surfaces it.

Sent back as `ENVELOPE-004-2d-repair.md`, scoped to `setup/codex/` and covering
all four scripts, requiring a two-phase uninstall proof — the second phase being
the half never reached last round, which is the half that proves the mechanism
works twice.

### A phantom defect I nearly recorded — verifying against a live worktree

While the repair was in flight I ran the ownership harness against the build
worktree and found `install.ps1` throwing *"The property 'phase-plan-creator'
cannot be found on this object"*, writing no registry, and exiting 1. It read as
a fifth defect and a serious one.

It was not a defect. `codexc` was `working` and had modified both installers
minutes earlier; I had measured half-written code. The give-away was that the
function carried the comment *"merges with existing, does not overwrite"* — the
repair I had just commissioned, not the code I had reviewed. Retracted before it
reached the worker.

The structural fault was mine and it was in the harness: it had no way to notice
that the thing under test was changing underneath it. It now fingerprints
`HEAD` + `git status --porcelain` + the mtimes of `setup/codex/` before and
after, and voids the entire run if they differ, with a separate note when the
worktree is merely dirty. **Verify against a settled tree, and prove it was
settled** — an agent-edited checkout is not a fixed object, and a green from a
moving target means nothing.

Two vacuity holes in the same harness were fixed alongside it: phase 2b's setup
step could fail silently and leave three checks "passing" against a state never
established, and the differential's registry comparison passed when *both*
registries were absent, `NOFILE == NOFILE`. Both are the same shape as the three
probes earlier this phase that silently matched nothing.

### Stage D repair, round 1 — one script fixed, three not; checkpoint `ba6066d`

`codexc` rewrote all four scripts, hit a tool-call error (*"Expected
'function.name' to be a string"*) at 78% context, and settled `done` **without
committing**. `done` is not completion evidence; the tree was dirty and the
report never arrived. I checkpointed the work as `ba6066d` so the good half was
not at risk, and verified all four myself against a settled tree — `HEAD`,
`git status --porcelain` and `setup/codex/` mtimes fingerprinted before and
after the harness run, unchanged.

**`uninstall.ps1` is now correct** — all thirteen checks, including the two I
had registered as the ones most likely to be got wrong: the second uninstall
(codex no longer an owner, so it must remove *nothing*) and deletion of the
registry only once the last owner goes. `.advanced-plans/state/` and `AGENTS.md`
user content survived every run.

The other three did not:

| # | Script | Defect |
|---|---|---|
| R1 | `install.ps1` | throws *"The property 'phase-plan-creator' cannot be found on this object"*, exits 1, writes **no registry at all** — skills and `ap.py` already on disk, so the install is left half-complete. `ConvertFrom-Json` returns a `PSCustomObject`, not a hashtable |
| R2 | `install.sh` | `APPROVED_SKILLS` (line 29) lists the seven core skills and omits `advanced-planning` — the shared routing skill, the one the mechanism exists for. It is never recorded as codex-owned |
| R3 | `uninstall.sh` | prints *"leaving files, updating registration"* and then deletes the registry — the previous round's defect, unchanged, in the same words. Same root cause as R2: `any_remaining` iterates only the approved list |
| R4 | `uninstall.sh` | reports `3 path(s) removed` where nine occurred (seven skills, `ap.py`, `runtime.json`) |
| R5 | both `.sh` | shell out to `python3`; the project's own `setup/claude-code/README.md:14-21` requires `python` and warns that on Windows `python3` is usually the Store alias and not necessarily the same interpreter. The reference installer uses `python3` zero times |

The differential is stark: `3 removed, 1 kept` from `.sh` against `10 removed,
3 kept` from `.ps1` on identical fixtures.

**One thing I got right by testing rather than asserting.** I suspected the
`set -e`-less swallowing of the merge's failure path. `set -e` is at
`install.sh:17`; forcing malformed JSON gives exit 1 with the error printed and
the registry untouched. Not a defect — and I would have reported it as one had I
stopped at reading the code.

### Correcting my own retraction

Earlier in this loop I recorded the `install.ps1` crash as a phantom — half-written
code caught mid-edit — and retracted it. **That retraction was wrong.** The crash
reproduces exactly on the settled, checkpointed tree: exit 1, registry missing,
same message. It is R1 above.

The retraction was still the right call *at the time*: the tree was demonstrably
moving and no finding drawn from it could be trusted. But "measured on a moving
tree" means *unknown*, not *false*, and I wrote it down as though it meant false.
The correct disposition for a finding from an unstable tree is to re-measure once
it settles — which is what the harness's fingerprint guard now forces — not to
discard it.

---

## Round 3 (`4783dba`, codexd) — the mechanism passes

Verified controller-side with `verify-ownership.sh` against the committed tree.
Tree fingerprint `fd3d2f7dda2262fa` at start and end, unchanged throughout — the
run describes a settled commit, not a checkout someone was editing.

**26 of 27 checks pass**, both languages:

| Group | Checks | Result |
|---|---|---|
| Merge proof, per installer | 4 each | PASS — foreign owner survives, `opencode-only-skill` preserved, no `["codex","codex"]` on reinstall |
| Phase 1, per uninstaller | 8 each | PASS — shared skill kept, registry **rewritten** to `["opencode"]`, `state/` sentinel intact, `AGENTS.md` 0 fences with user line present |
| Phase 2a, per uninstaller | 2 each | PASS — second run removes nothing, registry unchanged. **This is the case that failed rounds 1 and 2** |
| Phase 2b, per uninstaller | 3 each | PASS — sole owner removed, empty registry deleted, `state/` still intact |
| Differential | 2 | 1 PASS (registries agree, real values), 1 FAIL (counts: `2 kept` vs `3 kept`) |

### The vacuity probes

Both run in a disposable `git worktree add --detach` at `4783dba`, so the
worker's checkout was never touched. Removed cleanly afterwards (`git worktree
remove`, no `--force`, clean tree).

| Probe | Substitution | Count | Effect |
|---|---|---|---|
| 1 | `owners = [o for o in owners if o != "codex"]` → `owners = []` | **1** | 6 checks flip to FAIL; `11 removed, 0 kept` |
| 2 | `os.remove(owner_file)` → `pass` | **3** | `[sh] P2b empty registry deleted` flips to FAIL; `ps1` unaffected |

The substitution counts are printed, not assumed. Three earlier probes in this
phase silently matched nothing and "passed" vacuously; that is why the count is
now part of the probe.

## The count discrepancy was not cosmetic — and I nearly recorded that it was

The one failing check was the kept count: `10 removed, 2 kept` from `.sh` against
`10 removed, 3 kept` from `.ps1` on identical fixtures. I compared the two
on-disk trees afterwards and they were byte-identical, and I wrote down
**"the difference is reporting only"**.

That conclusion was wrong, and the way it was wrong is the point: I compared the
trees on the *shared-skill* fixture only. There `.agents/skills` is non-empty
regardless, so the defect has no observable effect. The comparison could not have
failed.

Chasing the count to its cause instead:

`uninstall.sh:287-288`
```sh
remove_if_empty "$SKILLS_DIR"
remove_if_empty "$CLAUDE_DIR/.agents"
```
`SKILLS_DIR="$CLAUDE_DIR/skills"` resolves to `<project>/.agents/skills`, so
`CLAUDE_DIR` is already `<project>/.agents` and the second call targets
`<project>/.agents/.agents` — a path that never exists. It returns at the
`[ -d ]` guard, silently. **The shell uninstaller never prunes `.agents`.**

Measured on a sole-owner fixture (codex owns everything, so the uninstall empties
the tree):

```
sh   Done. 11 path(s) removed, 0 kept.        ps1  Done. 11 path(s) removed, 0 kept.
  ./.advanced-plans                             ./.advanced-plans
  ./.advanced-plans/state                       ./.advanced-plans/state
  ./.agents          <-- left behind            (absent)
  ./AGENTS.md                                   ./AGENTS.md
```

`sh` leaves an empty `.agents/` after a complete uninstall; `ps1` removes it. Both
report `0 kept`, so on this fixture the count line conceals the difference
entirely — the discrepancy is only visible on the fixture where the defect is
*not*.

Dispatched as round 4 (`ENVELOPE-004-2d-repair-4.md`). One line:
`remove_if_empty "$CLAUDE_DIR"`. It fixes the leftover directory and makes the
counts agree by itself, since `.agents` then gets visited and counted on the
shared fixture. `ps1` was right.

**The lesson, recorded because it is the second time this loop:** a number that
does not add up is worth chasing to its cause even when the cause looks trivial.
Both times, the boring-looking discrepancy was the real defect — and both times my
first move was to construct a reason it did not matter rather than to find out why
it was there.

## Why every one of these defects had to be found by hand

Checked on the probe worktree at `4783dba`, read-only:

- `platforms/python/tests/test_uninstall.py` binds `_UNINSTALL_SH` / `_UNINSTALL_PS1`
  to **`setup/claude-code/`** only. It is a good suite — dry-run deletes nothing,
  confirmed run keeps the user's work, a symlinked command dir is unlinked not
  walked — and none of it touches the Codex adapter.
- The only file in the whole suite that mentions `setup/codex` is
  `test_path_audit.py`, which scans paths for policy, not behaviour.
- **No test anywhere asserts the residual tree after a complete uninstall.**
  `grep -rn '\.agents' platforms/python/tests/` outside `skills/` returns nothing.

So the four Codex scripts have no behavioural coverage at all. Every defect in
stages C and D — the clobbering merge, the stub ownership check, the deleted
registry, the wrong prune path — was reachable only by running the scripts and
looking at the filesystem. Nothing in CI could have failed on any of them, and
the 28 tests that *do* skip for want of `sh`/`pwsh` would not have caught them
either, because they do not cover this adapter.

**Carried finding, for loop-004-4:** extend `test_uninstall.py` to parametrize
over adapters rather than hard-binding the claude-code pair, and add a
complete-uninstall residual-tree assertion. The harness section 4 written this
round is the specification for that test — it fails on `4783dba` with
`9d8 < ./.agents` and passes once the prune path is corrected.

---

## Round 4 (`4fa486f`, codexd) — stage D passes

```
4fa486f fix: uninstall.sh to prune .agents/ directory correctly
 setup/codex/uninstall.sh | 8 ++++----
```

One file, four lines each way, clean tree, no untracked leftovers. The change is
the one asked for: `CLAUDE_DIR` renamed `AGENTS_DIR` throughout the function,
`remove_if_empty "$CLAUDE_DIR/.agents"` corrected to `remove_if_empty
"$AGENTS_DIR"`, and `_agents_file="$AGENTS_DIR/../AGENTS.md"` preserved so line
292 still resolves to `<project>/AGENTS.md`. No `CLAUDE_DIR` reference survives.

**Harness against the settled tree — 31/31 PASS.** Fingerprint `d642afe26301715b`
unchanged start to end.

```
sh : Done. 10 path(s) removed, 3 kept.
ps1: Done. 10 path(s) removed, 3 kept.
  PASS  counts agree
  PASS  registries agree (real values)          opencode
  PASS  sole-owner residual trees identical     9 path(s)
  PASS  [sh]  sole-owner leaves no .agents      no
  PASS  [ps1] sole-owner leaves no .agents      no
```

Section 4's discrimination is already established: the same section run against
`4783dba` in a detached probe worktree fails with `9d8 < ./.agents`. Pre-fix FAIL,
post-fix PASS, one line between them.

### Repo checks at `4fa486f`

- `python -m platforms.python.path_audit` → **exit 0**, `PASSED WITH 7 SUPPRESSED`
  (all seven the known `core/skills/permission-config/SKILL.md` exceptions). No change.
- `python -m pytest platforms/python/tests/ -q` → **675 passed, 1 failed, 0 skipped.**
  My PATH has `sh` and `pwsh`, so the 28 tests that skip on the worker's PATH —
  the installer and uninstall suites, the ones covering this work — **ran here and
  passed**. That is the first time in this loop those tests have actually executed.

## Carried finding — a sandbox safety test pinned to a path that does not exist

`platforms/python/tests/test_self_heal_integration.py:567-593`,
`test_sandbox_leaves_real_working_tree_untouched`. **Pre-existing** — it fails
identically at `4783dba`, so round 4 did not cause it.

Its docstring states its purpose: *"Meta-test: all file operations in this module
use tmp_path. The real working tree's critical files are not modified."* It
verifies that by asserting two absolute paths exist:

```python
real_loops_md = Path(
    "C:/Users/mharvey2/Documents/Coding/advanced-planning"
    "/.advanced-plans/phases/phase-14/loops.md"
)
```

That path is not where this repo lives — the checkout is `~/Coding/advanced-planning`,
with no `Documents` component. So the test fails because its literal is wrong, not
because a sandbox escaped.

The failure is the harmless half. Had the literal happened to resolve, the test
would have **passed while asserting facts about an unrelated directory** — a
sandbox-safety check that cannot detect a sandbox escape in the tree it is
guarding. It is the same shape as everything else this loop has turned up: the
announcement is written, the mechanism is not.

It also hard-codes one developer's home directory, so it cannot pass for anyone
else, and cannot pass in a linked worktree even on the right machine. The fix is
to derive the repo root from `Path(__file__).resolve().parents[...]` and assert
relative to that.

**Scope note:** outside stage D (`setup/codex/` only), so not fixed here. Carried
for loop-004-4 alongside the adapter-coverage gap above.

## Stage D verdict

**PASS.** The ownership mechanism is implemented once per language, both
languages agree on decisions, counts, registry contents and residual tree, and
the mechanism survives being run twice — which is the property loop-004-3 depends
on when the OpenCode adapter installs to the same paths.

Four rounds. Rounds 1-3 fixed the mechanism; round 4 fixed a wrong path that only
the count discrepancy betrayed.

---

## The todo's eight checks, verified against the final commit `4fa486f`

Re-run against the *final* tree rather than accepted at the stage each was first
proven. Stage C was once recorded as passing on a tree that still contained the
clobbering merge; that is why these are re-measured at the end.

| # | Check | Result |
|---|---|---|
| 1 | `core/` forbidden and untouched | `git diff --name-only` across the whole todo — **no `core/` path** |
| 2 | No adapter file duplicates a core skill's content | **8 skills installed, 0 forked.** Every `.agents/skills/*/SKILL.md` digest equals its source: 7 from `core/skills/`, `advanced-planning` from `platforms/shared/` |
| 3 | Installs to `.agents/skills/<name>/SKILL.md` + AGENTS.md fenced block | fence written at lines 5-21, user line intact |
| 4 | Adapter README with setup, quick start, top three failure modes | `platforms/codex/README.md` — Project Setup, Global Setup, Quick Start, and **five** numbered failure modes |
| 5 | `path_audit` exits 0, new host tokens not flagged | exit 0, `PASSED WITH 7 SUPPRESSED`, all seven the known `permission-config` exceptions |
| 6 | Shared payload created once, installed byte-identical | `advanced-planning` resolves to `platforms/shared/agent-skills/`, digest `8a1411b741aa0c84` on both sides |
| 7 | `state_validate.py`: stdlib only, six schemas, resolved from `source_root`, reached through `ap.py` | see below |
| 8 | Contract 6: `runtime.json` + launcher, no bare `-m`, proven by installing and running | see below |

### Check 7 — the validator, exercised rather than inspected

Imports are `json`, `sys`, `pathlib`, `typing`, plus the repository's own
`platforms.python.minischema`. No third-party dependency.

Its usage line names all six basenames — `collected-evidence`,
`external-task-envelope`, `gate-failure-context`, `gate-verdict`,
`loop-complete`, `loop-ready` — matching the six `*.schema.json` in `core/state/`.

Run **from inside the installed project, which contains no `core/` directory at
all**, through the launcher:

```
VALID loop-complete document                                        exit 0
todos_done: 5 -> "five"    Expected type 'integer', got 'string'    exit 1
status: -> "review_required"  Value not in enum ['completed',
                              'partial', 'failed']                  exit 1
```

Schemas therefore resolve from the recorded `source_root`, not from a `core/`
the installed project does not have — the property the check is actually about.

A note worth keeping: the enum rejection names **`review_required`**, the exact
value design §9.3 used wrongly and that loop-002-3 identified as contradicting
§10's lifecycle. The correction that was carried as a documentation fix is now
mechanically enforced against any document that tries to use it.

### Check 8 — Contract 6, proven by installing and running

```
.advanced-plans/runtime.json   { "source_root": "<checkout>", "version": "0.16.0",
                                 "written_by": "setup/codex/install.sh", ... }
.advanced-plans/bin/ap.py      present

python ".advanced-plans/bin/ap.py" history_log <path> '{"event":"contract6_probe"}'
  exit 0, and the file now contains
  {"event":"contract6_probe","timestamp":"2026-08-28T17:15:43Z"}
```

`PYTHONPATH` was unset for this run — confirmed, not assumed. No bare
`python -m platforms...` and no `sys.path.insert` anywhere under `setup/codex/`
or `platforms/codex/`. This is loop-001's defect, and it is closed here by
running a module in an installed project rather than by reading the installer.

**Known carried item, unchanged:** `state_validate --help` exits 2 where
`history_log` and `handoff_digest` exit 0. The module is reachable and correct;
the inconsistency is in its usage-error convention. Already on the carried list.

## loop-004-2 verdict

**COMPLETE.** All eight checks verified against `4fa486f` by running the adapter,
not by reading it. Four correction rounds inside stage D; the mechanism the whole
todo exists to establish — two adapters installing one shared skill without either
deleting the other's — now holds in both languages and survives being run twice.
