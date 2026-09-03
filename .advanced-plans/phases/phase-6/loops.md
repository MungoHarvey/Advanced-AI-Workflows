# Phase 6 — Ralph Loops

Source phase plan: `.advanced-plans/phases/phase-6/plan.md`
Design spec: §7.2 host contract, §7.3 adapter requirements, §9.2 task envelope, §9.3 collected
result, §14 Workstream 2, §15 ACC-08, §16.1
Baseline: `.advanced-plans/evidence/2026-08-26-baseline-audit.md`

**This phase works in a different repository from every phase before it.** Phases 1–5 changed
`Advanced-AI-Workflows` and `superpowers`. Phase 6 changes `MungoHarvey/advanced-planning` at
`C:\Users\mharvey2\Coding\advanced-planning`, base
`02b4b86e020bcaccc843228603bf6911450fc2d2` on `main`, tagged `v0.16.0`. AAW is the controller
checkout and holds the programme state; it is not the work tree for this phase.

**Standard programme forbidden set.** Forbidden for every worker todo in this programme, without
exception: `.advanced-plans/state/`, `.advanced-plans/PLANNING.md`,
`.advanced-plans/PLANS-INDEX.md`, `.advanced-plans/phases/*/complete.md`,
`.advanced-plans/gate-verdicts/`, `.advanced-plans/evidence/`. Only the controller checkout
writes those.

**Phase-6 addition to the forbidden set.** `advanced-planning` self-hosts: it carries its own
`.advanced-plans/` tree recording its own 16-phase programme. That tree is a *second* programme's
state and is equally out of bounds — a phase-6 worker never writes
`advanced-planning/.advanced-plans/` either. It may read it.

**Untracked files that must never be staged.** `find-files.js` in the AAW checkout and
`setup-antigravity.js` in the advanced-planning checkout are both pre-existing and untracked.
Every `git add` in this phase is
`git add -A -- . ':!find-files.js' ':!setup-antigravity.js'`.

**CORRECTION 2026-09-01 - this header describes a repository that no longer exists in
that state.** Everything above about the base and about remote writes was true when
phase 6 opened and is now false. Measured today, controller-side:

- `fix/shared-runtime-reachability` is **fully merged into `main`**.
  `git rev-list --left-right --count main...fix/shared-runtime-reachability` returns
  `73  0` and the merge-base IS the branch head (`b3f1b8f`) - zero commits sit only on
  the phase branch. Loops 001-004 are shipped, not local.
- `main` is `171d193`, `VERSION` is **0.19.0**, and `v0.17.0`, `v0.18.0` and `v0.19.0`
  are all tagged (CHANGELOG entries dated 2026-08-31, 2026-08-31 and 2026-09-01). The
  base for any remaining loop is `171d193`/v0.19.0, **not** `02b4b86`/v0.16.0.
- The remaining todos carry a *relative* `base_sha` chained to the previous todo, so
  they need no per-todo edit - but a worker dispatched against the header as written
  would have branched three releases behind. That is why this correction precedes the
  next dispatch rather than following it.

**`loop-006-5` is superseded by events.** It stages `v0.17.0` locally and leaves
publishing to the user. v0.17.0 shipped on 2026-08-31, and two further releases have
shipped since. The todo cannot be executed as written; what it should become is the
user's call and is not decided here.

**What is genuinely outstanding**, verified by probing `main` for each deliverable:
`platforms/cursor/` and `setup/cursor/` are ABSENT, so loop-005 is real work; no skill
emits a task envelope, there is no ACC-08 test, and there is no gate-validation module,
so 006-1, 006-2 and 006-3 are real work. Loop-002's schemas and validator, loop-004's
two adapters and `test_adapter_lifecycle.py` are all PRESENT on `main`.

**No remote writes.** No push, no tag push, no PR and no release in any loop of this phase without
a separate authorisation. Loop 006 stages `v0.17.0` locally; publishing it is the user's to run.

**codex cannot commit from a Herdr worktree.** A linked worktree's git metadata lives in the
parent repo's `.git/worktrees/`, outside codex's sandbox. Where a todo names codex as the
provider it is a reader or a reviewer; the controller or an opencode worker does the writing.

**Scope correction that already holds.** The design (§7.1) proposes creating `core/` +
`platforms/`. It exists: `core/` holds 9 host-neutral skills plus `agents/`, `schemas/`, `state/`
and `constraints.json`; `platforms/` holds `claude-code`, `cowork` and `python`;
`docs/adapting-to-new-platforms.md` is already the five-contract adapter guide, and CI already
runs a path audit and an install-drift audit. This phase adds three platforms beside the two that
exist, adds the two run-contract schemas, and hardens the audit. It is not a restructure.

---

```yaml
---
name: "ralph-loop-001"
task_name: "The shared Python runtime — prove it is unreachable from an installed project, then fix it before three more adapters inherit it"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-001-1"
    content: "Re-derive the call-site inventory from the source repository: every `python -m platforms.python.<module>` invocation in platforms/claude-code/commands/, platforms/claude-code/agents/, core/agents/ and core/skills/, with file and line"
    repository: "advanced-planning (C:\\Users\\mharvey2\\Coding\\advanced-planning)"
    base_sha: "02b4b86e020bcaccc843228603bf6911450fc2d2 (main, v0.16.0)"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/"]
    provider: "codex"
    worktree_owner: "herdr"
    checks:
      - "grep -rno for platforms.python.<module> across the four scoped directories, producing a table of module, file, line"
      - "for each module named, confirm the file exists under platforms/python/ — a call site naming a module that does not exist is a second, different defect and is reported separately"
    evidence: "The call-site table and the count. The controller's own count over the INSTALLED copies was 13 sites across 6 commands (next-loop, new-phase, plan-and-phase, next-phase, run-gate, sync-install); a different number from source is a finding, not a discrepancy to smooth over"
    gate: "none"
    outcome: "The blast radius is a number derived from the repository, not from the controller's recollection"
    status: completed
    result: "DONE 2026-08-27. 13 call sites across 6 commands, using 6 modules - matching the controller's independent count over the installed copies exactly, so there is no discrepancy to report. All 6 modules exist; the second defect this todo watched for is not present. THE FINDING IS THE ZERO ROWS: platforms/claude-code/agents/, core/agents/, core/skills/ and platforms/cowork/ contain none. The runtime is an ADAPTER-LAYER dependency of the Claude Code adapter, not a core one, and the one non-Claude adapter that exists solves the same problem with a POSIX checkpoint.sh needing no Python. Full table in evidence/2026-08-27-shared-python-runtime.md. PROVIDER SUBSTITUTION: derived by the controller, not by the assigned codex worker."
    complexity: low
    priority: high
  - id: "loop-001-2"
    content: "Prove the failure from a clean install rather than asserting it: install Advanced Planning into a scratch directory with setup/claude-code/install.ps1 -Project, then run one of the inventoried python lines from that project root"
    repository: "advanced-planning (read) plus a scratch project outside both checkouts"
    base_sha: "loop-001-1"
    allowed_paths: ["a scratch directory under the session scratchpad only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "any path inside either repository checkout"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "install.ps1 -Project <scratch> exits 0"
      - "list <scratch> for a platforms directory — expect absence; the installers copy commands, agents, skills and schemas, and nothing under platforms/python/"
      - "from <scratch>, run python -m platforms.python.history_log and record the exact error text"
      - "run the same line from the advanced-planning repo root and expect success — that is what proves the fault is reachability, not the module"
    evidence: "The install transcript, the directory listing, and both invocations with exit codes and stderr"
    gate: "none"
    outcome: "The defect is reproduced from a clean install, so the fix has a failing case to close and the loop cannot end on a claim"
    status: completed
    result: "DONE 2026-08-27. install.ps1 -Project into an empty scratch dir exits 0 and lands .claude/{commands,agents,schemas,skills,settings.json} plus a .advanced-plans/ scaffold; platforms/ is absent, confirmed by reading the installer's copy calls and not only by listing the result. All three probes fail from the installed project with ModuleNotFoundError (history_log, state_manager, install_audit) and the same import succeeds from the source repo - the control that proves this is reachability, not the module. The installer's own closing instructions send a new user to /new-phase, whose line 125 is one of the thirteen. PROVIDER SUBSTITUTION: run by the controller, not by the assigned opencode worker."
    complexity: medium
    priority: high
  - id: "loop-001-3"
    content: "Decide the delivery mechanism for the shared Python runtime and record the decision with its reason, having first written down what each option costs"
    repository: "Advanced-AI-Workflows (controller)"
    base_sha: "loop-001-2"
    allowed_paths: [".advanced-plans/evidence/"]
    forbidden_paths: ["<standard programme forbidden set, except evidence/ which the controller owns>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "at least four options are costed, including: (a) the installers copy platforms/python/ into the install tree; (b) a console-script shim on PATH; (c) the commands resolve an absolute source path recorded in the installation manifest; (d) the commands detect absence and degrade to a stated manual step"
      - "each option is scored against: does it work for a NON-Claude host, since codex, opencode and cursor all shell out the same way; does it survive the source repository being moved; does it duplicate code that then drifts; what does uninstall have to undo"
      - "the chosen option is written into PLANNING.md resolved_decisions by the CONTROLLER, never by a worker"
    evidence: "The costed options table and the recorded decision"
    gate: "human"
    outcome: "The mechanism is chosen once, on stated grounds, before three adapters are built on top of it — this is the fork the rest of the phase inherits"
    status: completed
    result: "DECIDED 2026-08-27 by the human gate: (c) resolve a recorded source path, with (d) detect-and-degrade as a non-optional guard. Recorded in PLANNING.md resolved_decisions by the controller. Options were drafted as: Four mechanisms costed against five axes in evidence/2026-08-27-shared-python-runtime.md. Controller recommends (c) resolve a recorded source path, with (d) detect-and-degrade as a non-optional guard under whichever is chosen. Against (a) copy-into-install-tree: it puts an Nth copy of executable code in every project, and install_audit - the machinery that would police it - compares by mtime, a limitation already on the carried-items list. Against (b) console-script shim: the only option that adds a packaging system and mutates PATH. For (c): zero duplication, no new subsystem, and the only one already demonstrated to work here. AWAITING the human gate; loop-004-1 writes its adapter specification against whatever is chosen."
    complexity: medium
    priority: high
  - id: "loop-001-4"
    content: "Implement the chosen mechanism, and add a test that fails without it"
    repository: "advanced-planning"
    base_sha: "loop-001-3"
    allowed_paths: ["setup/", "platforms/", "core/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "python -m pytest platforms/python/tests/ is green and the new test is in the count"
      - "the new test FAILS when the mechanism is reverted — demonstrate by reverting, running, and restoring. A test that passes both ways is not a test"
      - "install into a fresh scratch project again and re-run the loop-001-2 invocation — now exits 0"
      - "python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/ still reports no external dependencies"
    evidence: "The diff, the pytest output before and after the revert, and the re-run of the loop-001-2 reproduction"
    gate: "none"
    outcome: "Every command that shells out to the shared runtime works from an installed project, on every host, not only inside the source repository"
    status: completed
    result: "IMPLEMENTED 2026-08-27 on advanced-planning branch fix/shared-runtime-reachability, commits 54a0a73 + 8cd3705 (LOCAL ONLY, not pushed - programme policy authorises local commits on non-default branches only). MECHANISM: .advanced-plans/runtime.json holds source_root; .advanced-plans/bin/ap.py (copied from platforms/python/ap_launcher.py) reads it; all 13 call sites rewritten - 7 module invocations to `ap.py <module>`, 6 in-line imports to a runpy bootstrap. Both installers write the manifest OUTSIDE the scaffold-exists guard, so an upgrade-in-place refreshes a stale path - verified live: install.ps1 re-run over a project whose manifest pointed at C:/nowhere preserved the planning data and repaired the path. GUARD (d) in the same file: every failure names the manifest, the key and the repair, and exits 3. TESTS: 20 new in platforms/python/tests/test_ap_launcher.py, REVERT-PROVEN three ways - reverting the call sites fails 3, reverting the installers fails 3, removing the guard fails 5; restored green each time. Suite 418 passed (baseline 397 on main), the same 6 failures before and after. ast_check CLEAN as CI runs it; path_audit CLEAN. ACCEPTANCE: fresh scratch install, then the exact loop-001-2 invocations - history_log exit 0, state_manager import exit 0, install_audit reached (its exit 1 is its own audit verdict, no ModuleNotFoundError anywhere). Proven for BOTH installers. TWO DEFECTS FOUND BY RUNNING IT, NOT BY READING IT: (1) install.sh under Git Bash recorded a POSIX /c/Users path that native Python cannot open - a fresh, correct install tripped my own guard, and the repair the guard suggested reproduced the same bad path; fixed with cygpath -m and pinned by test_install_sh_records_a_path_the_interpreter_can_open. (2) three call sites already carried sys.path.insert(0, '.'), the same defect wearing a hat - it reaches the runtime only when cwd is the checkout. ALLOW-SET WIDENED DELIBERATELY: runpy added to core/constraints.json with the reasoning in its notes, and the pinned set in test_ast_check.py updated in the same commit so the constraint stays a constraint. Rejected __import__, which would have passed ast_check by hiding from it. DOCS: contract 6 in docs/adapting-to-new-platforms.md plus two checklist items, so loops 004-005 inherit the mechanism rather than each inventing one. CARRIED, NOT FIXED: advanced-planning has no .gitattributes and core.autocrlf=true, so install.sh is checked out CRLF and cannot execute under bash on Windows. That is what the 6 pre-existing test failures are. Real defect, outside this loop's allowed_paths, recorded for the phase gate. PROVIDER SUBSTITUTION: assigned to an opencode Herdr worker; run by the controller. HERDR_ENV=1, so a worker WAS available - the reason not to use one was the envelope, not the absence of a pane: 13 call sites across 6 files plus a launcher plus 20 tests exceeds Qwen's 8k output cap, which CLAUDE.md says to keep to focused diffs. This is the THIRD substitution in loop 001. loop-001-5 MUST be a real cross-model worker. SELF-FOUND DEFECT, fixed in 8cd3705 before the reviewer saw it: the guard told the reader to run /sync-install, which refreshes .claude/ surfaces from install_audit's file lists and is blind to .advanced-plans/runtime.json - it would have reported CLEAN and changed nothing. A guard naming a no-op repair is worse than a raw traceback. Both halves fixed: the diagnostic now leads with re-running the installer, and /sync-install gained step 4b which checks and rewrites the record through the launcher. test_the_guard_only_names_repairs_that_exist pins the two together. Suite now 419 passed. CORRECTION 2026-08-28: the CARRIED-NOT-FIXED claim above is wrong on both halves. Measured: advanced-planning has core.autocrlf=FALSE, and main fails 1 test, not 6. The 5 install_idempotency failures were introduced by the CONTROLLER'S OWN EDITS - the editing tools silently convert LF files to CRLF, which rewrote whole files, broke those tests, and would have committed three #!/bin/sh installers no POSIX shell could execute. Caught at commit time (5306 insertions for an 861-line change), normalised back to LF, commit amended before anything left the branch; the four earlier branch commits were audited and are clean. What remains true and open is that advanced-planning has NO .gitattributes, so nothing catches such a conversion."
    complexity: high
    priority: high
  - id: "loop-001-5"
    content: "Have a provider that did not implement it review the mechanism, specifically for what it does to uninstall, to upgrade in place, and to a project whose Python is not on PATH"
    repository: "advanced-planning (read-only)"
    base_sha: "loop-001-4"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/"]
    provider: "codex gpt-5.6-sol effort high — must differ from the loop-001-4 implementer"
    worktree_owner: "herdr"
    checks:
      - "the reviewer states in its own words what happens on uninstall and on upgrade in place"
      - "the reviewer is asked directly whether the mechanism duplicates code that can drift, and answers"
    evidence: "The verdict at .advanced-plans/gate-verdicts/phase-6-loop-001-<provider>.json, and the controller's resolution or waiver of each finding"
    gate: "human"
    outcome: "The foundational choice of the phase carries an independent verdict before four loops are built on it"
    result: "REVIEWED 2026-08-27 by codex gpt-5.6-sol effort high, a genuine cross-model check and the FIRST in loop 001 - the three earlier todos were controller substitutions. Verdict: CHANGES REQUESTED, reviewed through 8cd3705. Full verdict at .advanced-plans/gate-verdicts/phase-6-loop-001-codex.json with the raw transcript beside it. FOUR FINDINGS, and every one was independently reproduced by the controller before being acted on, per the standing rule never to take a worker's summary as evidence. THREE FIXED in fdc2ab9, each revert-proven: (2, P1) /sync-install could not repair the runtime it depends on - step 2 invoked install_audit THROUGH the launcher, so a stale manifest made the audit itself exit 3 and a missing launcher made it exit 2, while the repair sat at step 4b behind both; it was unreachable in exactly the two cases it existed for. The repair is now step 1b, ahead of the first launcher call, and the test asserts offset ordering rather than string presence - the weakness the reviewer named. (4, P1-adjacent, filed P2) valid JSON of the wrong shape bypassed the guard: [] raised AttributeError on data.get and {'source_root': 1} on .strip(), raw tracebacks naming a launcher internal, which is the failure the guard exists to replace; all four wrong shapes now exit 3 naming the shape found. (3, P2) a test overclaimed subdirectory coverage by passing an ABSOLUTE launcher path, while the shipped call sites are project-root-relative and exit 2 from a subdirectory before find_manifest runs; fixed by correcting the claim rather than the code - the test is renamed to what it proves, the real limit has its own test, a second test forbids any command changing directory before invoking the launcher, and contract 6 records that commands run from the project root. The walk-up is RETAINED, not removed: it is the route an out-of-project launcher takes, which finding 1's decision may require. ONE ESCALATED: (1, P1) both setup installers exit 0 from the --global branch before the runtime block, AND platforms/claude-code/install.sh - a THIRD installer neither the implementer nor loop-001-1's inventory knew existed - copies the commands and never writes runtime.json or bin/ap.py. Globally-installed commands therefore fail in any project that was never project-installed. Not fixed: the repair requires choosing where a globally-installed command finds its launcher, which changes the shape of all 13 call sites and is inherited by the three adapters in loops 004-005 - the same class of decision the loop-001-3 gate took. Escalated to this todo's human gate rather than taken unilaterally. BOTH OF THIS TODO'S CHECKS ARE UNSATISFIED and that is recorded, not smoothed over: the reviewer answered none of the three required-coverage questions - uninstall, upgrade-in-place, python-not-on-PATH - in its own words, and did not answer the drift question it was asked directly. The controller's own answers to all three are in the verdict file, labelled as the controller's, including the plain admission that python-not-on-PATH is entirely outside the guard because the failure happens in the shell before any Advanced Planning code runs. The reviewer also could not run pytest - no writable temp directory in its sandbox - so its 22-test collection is the limit of what it verified by execution. Suite after the fixes: 425 passed / 6 failed, the same 6 CRLF failures carried from main; ast_check clean as CI runs it. POST-GATE 2026-08-28, commit 38f5d00 (still LOCAL ONLY): the gate was answered 'pass, but re-ask the three questions'. Before re-asking, the MECHANISM went to a cross-vendor panel via multi-model-review in real Herdr panes - agy 3 critical/Yes, cursor 3 critical/No, opencode 4 critical/No, artefacts at ~/.herdr/reviews/advanced-planning-20260827-180113/. Cursor was decisive and found three real defects the other two missed: the boundary stop was raised BEFORE the global fallback could be consulted so the fallback could never fire in the case it existed for; a nested git repository silently inherited the enclosing checkout; and HOME vs USERPROFILE disagree under Git Bash on Windows. That is the argument for rotating vendors rather than asking the same one twice. THE PANEL CONTRADICTED THE CONTROLLER: my own recommendation of ~/.claude/bin/ap.py violates contract 6 - text I had written three commits earlier - and a literal ~ in runpy.run_path was verified to crash, since run_path does no tilde expansion. Both reported to the user and the gate re-put; the user chose B' (host-neutral ~/.advanced-plans, global installer only, project installer unchanged). IMPLEMENTATION DEPARTS FROM THE OPTION PREVIEW and this was reported: the preview said os.path.expanduser() at the 6 inline sites and '13 call sites change once', but expanduser follows $HOME, which here is a mapped network drive while native Python reads USERPROFILE, and no single literal is correct across bash, PowerShell and native Python. The installers instead REWRITE the launcher path in the commands they copy; source call sites are unchanged in meaning. Cost: the rewrite must be a pure path swap or install_audit reports permanent drift - the first pass rewrote bare call sites into quoted ones and the audit reported 6 files stale on a clean install, which no /sync-install could settle. Fixed by quoting the SOURCE, pinned by test_every_source_call_site_is_in_the_substitutable_form. TWO MORE DEFECTS FOUND BY RUNNING IT, MISSED BY ALL THREE REVIEWERS: (1) the global record was read from the CALLER's profile, so install-time and run-time homes could disagree - the installed launcher now prefers the manifest beside itself, refusing it when its own project encloses the directory being resolved, because that is the borrowing the boundary stop exists to refuse (the first fix re-opened the hole and three boundary tests caught it). (2) the six in-line runpy call sites raised a RAW TRACEBACK, not the guard - the exact failure the guard was written to replace, still present at half the call sites. LIVE PROOF: -Global install redirected to a scratch profile left the real profile byte-identical; from a scaffolded-but-never-installed project the shell call site exits 0 naming the manifest, the in-line call site returns the root, and a real module runs; install_audit source,global reports 0 stale. All four new behaviours revert-proven. Suite 444 passed / 1 failed, and that 1 fails identically on main. ast_check NONE. STILL UNSATISFIED - the two checks above remain unanswered by anyone but the controller; the follow-up envelope on uninstall, upgrade-in-place and python-not-on-PATH is the outstanding gate requirement, and B' changed what the uninstall answer is, which is why it was sequenced after the mechanism settled. GATE REQUIREMENT NOW SATISFIED 2026-08-28: the follow-up envelope was sent one-shot and read-only to three providers; opencode and cursor answered, agy produced nothing because headless mode auto-denied the tool permission it needed to read files. Both checks are answered by providers other than the controller. It cost two more defects: cursor found that platforms/claude-code/install.sh's PROJECT path shipped no runtime at all - the original defect intact in the one code path nobody re-read - and the controller found by running that the same file's --global block read an undefined $REPO_ROOT and half-installed under set -e. Fixed in 686aee2 and f9c8bd6. Cursor also corrected me: the guard exits 3, not 2; there is no exit 2 from the guard at all. Carried open: no uninstall path exists and a deleted launcher is undiagnosable; the USERPROFILE-before-HOME rule has at least five copies of which the test pins two, the shell and PowerShell ones being unpinned; next-phase.md uses python3 in two places. Artefacts at .advanced-plans/gate-verdicts/phase-6-loop-001-followup/."
    status: completed
    complexity: medium
    priority: high

prompt: |
  ## Objective
  Advanced Planning's commands shell out to a shared Python runtime — `python -m
  platforms.python.<module>` — for state preparation, history, gates, audits and versioning.
  Neither installer ships `platforms/python/`. The controller hit this directly on 2026-08-27:
  `python -m platforms.python.history_log` in the AAW checkout returns
  `ModuleNotFoundError: No module named 'platforms'`, and the same gap is already recorded for
  `codex_gate`, `install_audit` and `handoff_digest`.

  Fix this FIRST. Every adapter in this phase invokes the same runtime the same way, so shipping
  three more adapters over an unreachable runtime triples one defect instead of finding it.

  ## Hard rules
  - Reproduce before you fix. loop-001-2 exists so the fix has a failing case, not a claim.
  - The mechanism must work for a host that is not Claude Code. Codex, OpenCode and Cursor all
    shell out; a fix that only lands in `.claude/` is not a fix for this phase.
  - Do not vendor a second copy of the modules that can drift from `platforms/python/` unless the
    costed decision explicitly accepts that cost and says how drift is detected.
  - No remote writes.

  ## Success criteria
  - [ ] the call-site inventory is derived from the repository, with file and line
  - [ ] the failure is reproduced from a clean `install.ps1 -Project` into a scratch directory
  - [ ] four or more mechanisms are costed and one is chosen, with the reason recorded
  - [ ] a test fails without the fix and passes with it, demonstrated by reverting
  - [ ] a different provider has reviewed uninstall, upgrade and no-Python-on-PATH
---
```

---

```yaml
---
name: "ralph-loop-002"
task_name: "The two run-contract schemas — in the convention this repository already has, with invalid fixtures that actually fail"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Settle where the two new schemas live and in what form, against the split the repository already has, and write the reason down"
    repository: "advanced-planning (read-only)"
    base_sha: "loop-001-4"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/"]
    provider: "codex"
    worktree_owner: "herdr"
    checks:
      - "core/schemas/ holds four *.schema.md files — prose specifications. core/state/ holds four *.schema.json files — machine-validatable JSON Schema. Confirm this split from the files rather than assuming it"
      - "CI job 2 (schema-validation) globs core/state/*.json ONLY. Whichever location is chosen, name what has to change in ci.yml for the new files to be validated"
      - "docs/ also holds three *.schema.md files (phase-complete, phase-handoff, phase-manifest-entry). Establish whether that is a third convention or an accident, because the answer decides where a new prose companion would go"
    evidence: "A short note stating the chosen location and form for each of the two schemas, the reason, and the ci.yml change required"
    gate: "none"
    outcome: "The two schemas join an existing convention instead of founding a third one"
    status: completed
    complexity: low
    priority: high
  - id: "loop-002-2"
    content: "Write the immutable external-task envelope schema from design §9.2, with every required field, and every one of the six validation rules either expressed in the schema or documented beside it as a rule the validator enforces"
    repository: "advanced-planning"
    base_sha: "loop-002-1"
    allowed_paths: ["core/schemas/", "core/state/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "every field of the §9.2 example is present, with types"
      - "rule: an implementation or sync task must use isolation=worktree unless an explicit shared-write override is recorded — expressed conditionally, not as prose alone"
      - "rule: allowed_paths cannot be absent for a sync or release task"
      - "rule: forbidden_paths always contains the controller's mutable planning state for a worker task"
      - "rule: no credential or secret field is permitted — additionalProperties false, or the exclusion is explicit and tested"
      - "rule: base_ref is recorded as a full commit SHA alongside its human-readable ref"
      - "the envelope is IMMUTABLE: amendments create a new envelope with supersedes_run_id, and that field is in the schema"
    evidence: "The schema file and a field-by-field mapping to §9.2"
    gate: "none"
    outcome: "A dispatched task has a contract that can be validated before it is sent, not after it has gone wrong"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-002-3"
    content: "Write the collected-evidence schema from design §9.3, with the collector/worker trust boundary stated inside the schema description rather than only in the design document"
    repository: "advanced-planning"
    base_sha: "loop-002-2"
    allowed_paths: ["core/schemas/", "core/state/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "the nested git, checks, policy and agent objects match §9.3"
      - "agent_summary carries a description saying it is ONE evidence item and is not trusted: the collector independently computes changed_paths, diff summary, commit identity and check exit codes"
      - "status is an enumeration drawn from the §10 lifecycle and it includes interrupted — ACC-11 turns on a run never being silently reported as completed"
      - "policy.path_scope_passed, tests_passed and independent_review_passed are all required, so a result cannot be silent about a gate it did not run"
    evidence: "The schema file and a field-by-field mapping to §9.3"
    gate: "none"
    outcome: "Evidence has a shape the controller can check, and the schema itself says the worker's prose is not the evidence"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-002-4"
    content: "Add valid AND invalid fixtures per §16.1 and a pytest that runs both directions"
    repository: "advanced-planning"
    base_sha: "loop-002-3"
    allowed_paths: ["platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "at least five INVALID fixtures, each failing for a different named reason: allowed_paths missing on a sync task; isolation not worktree on an implementation task; a credential-shaped extra field; base_ref given as a branch name with no SHA; a result whose policy block omits a gate"
      - "each invalid fixture asserts the SPECIFIC validation error, not merely that validation failed — an invalid fixture that would also fail for a typo is not testing what it claims"
      - "python -m pytest platforms/python/tests/ is green"
      - "ast_check still reports dependency-free. If JSON Schema validation wants a library, that is a new production dependency and needs a decision gate — prefer a hand-written validator, or raise the dependency rather than adding it"
    evidence: "The fixture files, the test file, and the pytest output naming each invalid case"
    gate: "none"
    outcome: "The schemas are enforced rather than published, and each rule has a case that proves it fires"
    status: completed
    complexity: high
    priority: high
  - id: "loop-002-5"
    content: "Wire the new schemas into CI job 2 so they are validated wherever loop-002-1 put them"
    repository: "advanced-planning"
    base_sha: "loop-002-4"
    allowed_paths: [".github/workflows/ci.yml"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "job 2 currently globs core/state/*.json only — after the change it covers the new files"
      - "prove the job fails on a malformed schema by corrupting one, running the job's python inline, and restoring it"
    evidence: "The ci.yml diff and the deliberate-corruption run"
    gate: "none"
    outcome: "A malformed schema stops the build instead of shipping"
    status: completed
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Add the two run contracts from design §9.2 (immutable task envelope) and §9.3 (collected
  result). These are what make a worker's output checkable: the envelope is validated before
  dispatch, the result is validated before it advances anything.

  ## The convention question comes first
  This repository has two schema conventions already — prose `*.schema.md` in `core/schemas/`,
  machine-validatable `*.schema.json` in `core/state/` — and a third-looking set of `*.schema.md`
  in `docs/`. The phase plan's deliverable table says "JSON Schema, `core/schemas/`", which would
  put a JSON file in the prose directory. Settle that in loop-002-1 before writing anything.

  ## Hard rules
  - The worker's prose is one evidence item, never the evidence. Say so in the schema.
  - `interrupted` must be a reachable status. A run that lost its server is not `completed`.
  - No new production dependency without a decision gate.
  - An invalid fixture must assert WHICH rule rejected it.
  - No remote writes.

  ## Success criteria
  - [ ] location and form settled against the existing convention, with the reason written down
  - [ ] both schemas written, every §9.2 rule and §9.3 field accounted for
  - [ ] five or more invalid fixtures, each asserting its specific error
  - [ ] pytest green, ast_check still dependency-free
  - [ ] CI validates the new files, proven by a deliberate corruption
---
```

---

```yaml
---
name: "ralph-loop-003"
task_name: "Host-neutrality enforced, not asserted — extend the path audit until it fails on a host token in core/"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-003-1"
    content: "Read platforms/python/path_audit.py and state precisely what it checks today, and what the phase-6 criterion asks for that it does not"
    repository: "advanced-planning (read-only)"
    base_sha: "loop-002-5"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/"]
    provider: "codex"
    worktree_owner: "herdr"
    checks:
      - "it currently treats exactly three signatures as violations: a doubled .advanced- prefix, .advanced-plans nested under .claude, and the deprecated .claude/plans/ token. Confirm from the source"
      - "its docstring states that a bare .claude/commands/ or .claude/skills/ reference is LEGITIMATE. That is true for the INSTALLED runtime surface and false for core/. Name that tension explicitly; it is the whole of this loop"
      - "core/skills/ and core/agents/ are already in the scanned scope, so the change is a scope-dependent RULE, not a new directory"
    evidence: "A statement of the current three rules, the scoped directories, and the exact gap against design §7.3 — core files must contain no host directory, no host-only tool name and no host-specific permission syntax"
    gate: "none"
    outcome: "The change is understood as adding a rule that applies only under core/, not as widening a rule that would then fire on legitimate installed-runtime paths"
    status: completed
    complexity: low
    priority: high
  - id: "loop-003-2"
    content: "Add a core/-scoped host-neutrality rule covering host directories, host-only tool names and host permission syntax"
    repository: "advanced-planning"
    base_sha: "loop-003-1"
    allowed_paths: ["platforms/python/path_audit.py", "docs/path-conventions.md", "platforms/python/tests/test_path_audit.py"]  # widened 2026-08-28 after loop-003-1 - see plan.md amendment
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "host directories flagged under core/: .claude/, .cursor/, .opencode/, .codex/, .agents/, .gemini/"
      - "host-only tool and agent names flagged under core/: the Claude Agent/Task tool, subagent_type, and slash-command syntax only one host has"
      - "host permission syntax flagged under core/: settings.json permission rules, opencode.json, .cursor/rules"
      - "the rule fires ONLY under core/ — platforms/claude-code/ must still be allowed to say .claude/, which is the entire point of an adapter"
      - "test_path_audit.py::TestFalsePositiveGuard::test_claude_skills_ref_is_not_flagged currently asserts the OPPOSITE of this rule, on core/agents/worker.md. INVERT and RENAME it - do not delete it. A guard that asserted the old wrong behaviour must become one that asserts the new right behaviour"
      - "docs/path-conventions.md is the stated source of truth for canonical paths and gains the new rule"
    evidence: "The diff and the rule list"
    correction: "2026-09-02, from gate attempt 2. The FIRST check above enumerates six host directories and the implementation shipped five: the regex read (claude|cursor|opencode|codex|gemini) and .agents/ was absent, so a core/ file naming the shared skills root passed the audit in silence for five days. docs/path-conventions.md had it right in both places all along, and the check above had it right too - the evidence field asked for the rule list, and nobody read the rule list against the check. That is this phase defect class inside the loop that was building the check for it. It also survived loop-007-4, which added four new roots and four new red-green tests, because every one of those tests planted a token the regex already matched: widening a checks ROOTS does not widen its TOKENS. Fixed in the loop-007 integration branch - token added, three named EXCEPTIONS for the platforms/shared/ files that legitimately name the cross-host discovery root, a mutation test that plants .agents/ under core/ through the DEFAULT root list, and a drift test that DERIVES the forbidden tokens from the Host directories row of docs/path-conventions.md so the documentation and the regex cannot diverge again. Both new tests mutation-proved: with the token removed they fail and name .agents/, with it present they pass, and the clean-tree positive control stays green throughout."
    gate: "none"
    outcome: "The success criterion — the CI path audit fails on any host-specific path in core/ — has an implementation"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-003-3"
    content: "Run it against core/ as it stands and deal with what it finds honestly — fix the file, or record a named exception with a reason. Do not weaken the rule to make the run green"
    repository: "advanced-planning"
    base_sha: "loop-003-2"
    allowed_paths: ["core/", "platforms/python/path_audit.py", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "record the FULL first-run output before any fix; that list is the finding"
      - "each violation is either fixed in core/ or added to a named allow-list entry carrying a one-line reason — a silent exclusion is not acceptable"
      - "if the count is zero on the first run, treat that as suspicious rather than good: plant a violation and confirm the rule fires before believing it"
    evidence: "The first-run output, the resolution of each hit, and the final run"
    gate: "none"
    outcome: "core/ is host-neutral in fact, and any exception is visible with its reason attached"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-003-4"
    content: "Mutation-test the audit: plant one host token in a core/ skill, prove exit 1, remove it, prove exit 0, and leave the case behind as a permanent fixture test"
    repository: "advanced-planning"
    base_sha: "loop-003-3"
    allowed_paths: ["platforms/python/tests/", "core/skills/ (temporarily, reverted inside this todo)"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "plant a .cursor/rules/ reference in one core/skills SKILL.md — path_audit exits 1 and names the file and line"
      - "restore the planted file — path_audit exits 0"
      - "git status is clean afterwards; the mutation leaves nothing behind"
      - "the same mutation is added as a permanent case in test_path_audit.py against a FIXTURE, not a live file"
    evidence: "Both runs with exit codes, the clean git status, and the new test"
    gate: "none"
    outcome: "The audit is proven to fail, which is what makes a green run mean anything — a check that never fails is not a check"
    status: completed
    complexity: low
    priority: high
  - id: "loop-003-5"
    content: "Confirm CI job 4 picks the new rule up without a workflow change, or make the minimal change it needs"
    repository: "advanced-planning"
    base_sha: "loop-003-4"
    allowed_paths: [".github/workflows/ci.yml"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "job 4 runs path_audit bare, so a rule added inside the module needs no workflow edit — verify that rather than assume it"
      - "the inline comment in ci.yml lists the three old signatures and is now incomplete; update it or it will mislead the next reader"
    evidence: "The verification, and the ci.yml diff if one was needed"
    gate: "none"
    outcome: "The enforcement is in CI, and CI's own description of it is true"
    status: completed
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Design §7.3 requires that core files contain no host directory, no host-only tool name and no
  host-specific permission syntax, and says a CI path audit enforces it. The audit exists and runs
  in CI job 4, but it checks three *corruption* signatures — it does not check host-neutrality at
  all. Close that.

  ## The trap this loop must not fall into
  `path_audit.py`'s docstring says a bare `.claude/commands/` reference is legitimate, and for the
  installed-runtime surface it IS. The new rule is scoped to `core/` only. Widening the existing
  rule instead of adding a scoped one would flag `platforms/claude-code/`, which is exactly where
  `.claude/` belongs — and the fix would then be to weaken the rule, arriving back where it
  started with more code.

  ## Hard rules
  - Never weaken the rule to make the tree pass. Fix the file, or record a named exception.
  - A zero-violation first run is a reason to distrust the rule, not to celebrate. Plant one.
  - The mutation test is permanent, as a fixture. A live-file mutation that is reverted proves it
    once; a fixture proves it every run.
  - No remote writes.

  ## Success criteria
  - [ ] the current three rules and the gap are stated from source
  - [ ] a core/-scoped rule covers host directories, host-only tool names and host permission syntax
  - [ ] the first-run output is recorded in full and every hit is resolved or named
  - [ ] the audit is proven to exit 1 on a planted token, and that case is a permanent test
  - [ ] CI enforces it, and ci.yml's own comment describes it correctly
---
```

---

```yaml
---
name: "ralph-loop-004"
task_name: "Codex and OpenCode adapters — the six contracts, each proven on its own host, neither forking a core skill"  # five -> six, 2026-08-28: see plan.md amendment
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-004-1"
    content: "Write the adapter specification for both hosts before either is built: for Codex and for OpenCode, fill in all SIX contracts from docs/adapting-to-new-platforms.md and the five requirements in design §7.3"  # amended 2026-08-28: the doc has six contracts, not five, and §7.3 lists five requirements, not four
    repository: "advanced-planning (read) + Advanced-AI-Workflows evidence/"
    base_sha: "loop-003-5"
    allowed_paths: [".advanced-plans/evidence/"]
    forbidden_paths: ["<standard programme forbidden set, except evidence/ which the controller owns>"]
    provider: "codex gpt-5.6-sol effort xhigh"
    worktree_owner: "herdr"
    checks:
      - "Contract 1 entry point: Codex has no custom prompt files, so the entry point is a skill under .agents/skills/ — say exactly how a user triggers a phase, a loop, a gate, a resume and a compact"
      - "Contract 2 agent spawning: neither host has Claude Code's subagent model. State whether the orchestrator/worker roles are native, or an external Herdr/AAW task, and how the prompt reaches them"
      - "Contract 3 state directory: .advanced-plans/state/ for both, and the reason it is NOT a host-private directory"
      - "Contract 4 skills directory: .agents/skills/<name>/SKILL.md per design §7.2 for both hosts"
      - "Contract 5 checkpoints: git for both — but codex CANNOT commit from a linked worktree, so the codex adapter must say who commits instead. That is a real constraint, not a footnote"
      - "Contract 6 shared Python runtime: state that the installer writes .advanced-plans/runtime.json and copies platforms/python/ap_launcher.py to .advanced-plans/bin/ap.py, and that it does BOTH OUTSIDE any scaffold guard. A --global install carries the three extra obligations in the same section. This contract was added to the doc on 2026-08-27 by loop-001 and is the one an adapter is most likely to omit, because omitting it produces a tree that looks complete and fails only when installed"
      - "§7.3 additions: discovery, invocation, delegation, state I/O, and the human gate. §7.4 gives the per-host Plannotator fallback text; Plannotator is DEPRECATED in AAW, so state the host-neutral manual review command instead and do not carry the Plannotator wording forward"
    evidence: "One specification document covering both adapters, contract by contract, with the codex commit constraint called out"
    gate: "none"
    outcome: "Two adapters are specified against the published contract before code exists, so neither is reverse-engineered from the Claude Code one"
    status: completed
    complexity: high
    priority: high
  - id: "loop-004-2"
    content: "Build the Codex adapter: platforms/codex/ and setup/codex/, installing and registering the core skills without forking any of them"
    repository: "advanced-planning"
    base_sha: "loop-004-1"
    allowed_paths: ["platforms/codex/", "setup/codex/", "platforms/shared/", "platforms/python/", "docs/"]  # widened 2026-08-28: loop-004-1 put the shared skill payload at platforms/shared/ (the collision decision) and found that no production code validates state against the core schemas, so platforms/python/state_validate.py is a prerequisite. core/ stays forbidden
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "core/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "core/ is in the forbidden set for this todo on purpose: an adapter that needs to change a core skill has found a core defect, which is reported and fixed as its own todo, not absorbed"
      - "no file under platforms/codex/ duplicates the CONTENT of a core skill — prove it by hashing every installed skill against its core original and showing they are the same file or the same digest"
      - "the adapter installs skills to .agents/skills/<name>/SKILL.md and guidance to the AGENTS.md fenced block, per §7.2"
      - "an adapter README exists covering setup, quick start, and the top three failure modes — the checklist in docs/adapting-to-new-platforms.md requires it"
      - "path_audit still exits 0, and the new host tokens under platforms/codex/ are correctly NOT flagged"
      - "the shared skill payload is created ONCE at platforms/shared/agent-skills/advanced-planning/ and installed byte-identical to .agents/skills/advanced-planning/SKILL.md. A destination that differs is an install CONFLICT reported with both digests, never an overwrite"  # added 2026-08-28 from loop-004-1
      - "§7.3 State I/O is a prerequisite, not a claim: platforms/python/state_validate.py exists, uses only the standard library, validates all SIX core/state schemas, resolves them from the recorded source_root rather than expecting core/ in the installed project, and is reached through ap.py. state_manager.py does NOT validate - loop-004-1 checked"  # added 2026-08-28
      - "Contract 6: setup/codex/ writes .advanced-plans/runtime.json and copies the launcher, both OUTSIDE the scaffold guard; every call site reaches the runtime through the launcher and none uses bare -m or sys.path.insert. Prove it by INSTALLING into a scratch project and running a module there — this is loop-001's defect, and reading the installer is how it survived thirteen call sites the first time"  # added 2026-08-28
    evidence: ".advanced-plans/evidence/2026-08-28-loop-004-2-codex-adapter.md — final commit 4fa486f on loop-004-codex (LOCAL ONLY). All eight checks re-verified against the final tree by running the adapter: 8 skills installed, 0 forked (7 from core/skills/, advanced-planning from platforms/shared/, digests equal); Contract 6 proven by running history_log through .advanced-plans/bin/ap.py in an installed project with PYTHONPATH unset; state_validate resolves all six core/state schemas from the recorded source_root in a project containing no core/, accepting a valid loop-complete document and rejecting a type error and an enum violation. Stage D took four rounds on the skill-ownership.json mechanism, which was written, read once and destroyed. Controller harness 31/31 with two vacuity probes at printed substitution counts. CARRIED: the Codex adapter has no behavioural test coverage in platforms/python/tests/ — test_uninstall.py binds only to setup/claude-code/ and no test anywhere asserts a residual tree after a complete uninstall, which is why every defect here was found by hand"
    gate: "none"
    outcome: "Codex installs and registers the same named core skills Claude Code does"
    status: completed
    complexity: high
    priority: high
  - id: "loop-004-3"
    content: "Build the OpenCode adapter: platforms/opencode/ and setup/opencode/, on the same terms"
    repository: "advanced-planning"
    base_sha: "loop-004-2"
    allowed_paths: ["platforms/opencode/", "setup/opencode/", "docs/", "platforms/python/tests/"]  # platforms/shared/ is READ for this todo, not written: 004-2 creates the payload, 004-3 consumes it unchanged. platforms/python/tests/ ADDED 2026-08-28: the unplanned coverage todo parametrised test_adapter_lifecycle.py over adapters so that adding OpenCode is one tuple, but 004-3 could not reach the file to add it, and the suite would have stayed single-adapter. The widening is APPEND-ONLY: 004-3 may add one tuple to _ADAPTERS and may not alter any existing test logic, fixture or assertion. Same shape as 004-1's platforms/shared/ finding - a shared location the build loop was forbidden to touch. CORRECTION 2026-08-28: the APPEND-ONLY constraint above was WRONG and forbade the only correct fix. The suite was only nominally parametrised - THREE assertions still hardcoded 'codex', so the tuple could not be added without de-hardcoding them, and FIVE further sites hardcoded the fixture SEEDS and merged expectations, seeding a sibling adapter as the 'foreign' owner. That was true while Codex was the only adapter and became false the moment OpenCode became the adapter under test. The worker de-hardcoded the three (no assertion weakened) and could not reach the five; the controller fixed those. The instruction should have read: parametrise whatever is still adapter-coupled, and change no assertion's MEANING. The earlier 'adding OpenCode is one tuple' claim is withdrawn - it was 17 sites.
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "core/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "same no-fork hash proof as loop-004-2"
      - "skills to .agents/skills/, guidance to the AGENTS.md fenced block; opencode.json is touched ONLY for plugins, permissions or extra instructions, per §7.2"
      - "adapter README with the top three failure modes"
      - "path_audit exits 0"
      - "Contract 6, same terms and same proof as loop-004-2: install into a scratch project and run a module there"  # added 2026-08-28
      - "NO divergent copy of the shared payload: this todo consumes platforms/shared/ as 004-2 created it and reuses state_validate.py rather than writing a second validator. Installing codex-then-opencode and opencode-then-codex must leave ONE identical skill tree"  # added 2026-08-28 from loop-004-1
    evidence: ".advanced-plans/evidence/2026-08-28-loop-004-3-opencode-adapter.md — worker commit 3a95f1e, final commit b458a51 on loop-004-opencode (LOCAL ONLY). DERIVED not re-authored: 131 differing lines out of 1,752, every one host-naming except four in install.ps1, of which one was a real defect (the header comment said it was the PowerShell equivalent of ITSELF) - so four rounds of stage-D ownership fixes were inherited rather than re-earned. The worker ran NONE of the nine requested proofs and SAID SO rather than claiming a pass it could not produce; its PATH has no sh or pwsh. All evidence is therefore controller-side: ownership harness 41/41 in BOTH orientations (codex-as-adapter and opencode-as-adapter, same tree); collision harness 20/20, which exercises loop-004-1 collision decision for the first time - both install orders give ONE identical tree (35 paths, 8 SKILL.md digest-equal), advanced-planning owned by both, both fences coexisting, and uninstalling one leaves the other wholly intact with a SECOND uninstall a no-op; no-fork proof 8/8 digest-equal; Contract 6 exit 0 with PYTHONPATH unset against a real document; no opencode.json created, which is correct per 7.2. THE LOOP REAL FINDING IS THAT THREE CHECKING INSTRUMENTS WERE REPORTING GREEN OVER GROUND THEY DID NOT EXAMINE. (1) The controller harness opened with 6 FAILs, all of them its own: two sites still meant the-other-owner but said the literal opencode, the planted foreign entry stopped being foreign once OpenCode was the adapter, and the AGENTS.md fence check read grep -c in SINGLE quotes so $ADAPTER never expanded - it searched a literal that cannot occur, returned 0, and had passed unconditionally through all four Codex rounds. Proven by discrimination: old form reads 0 with both fences present, repaired form reads 2. (2) The tracked suite came back 11 failed / 743 passed, ten of them [opencode] - and those were TEST defects, the identical bug class, found in the same hour: five fixtures seeded a sibling adapter as the foreign owner and hardcoded the merged expectation. Repaired with a foreign owner that is deliberately never an adapter name; 74 passed (37 cases x 2 adapters) and the full suite 753 passed / 1 failed, up from 743 - exactly the ten recovered cases, the one remaining failure being the pre-existing hard-coded-path test that fails on main too - and proven load-bearing rather than merely green by reintroducing the D1 registry clobber - 1 failed with it, 8 passed without. That probe FIRST attempt printed 0 substitutions (the block is at four spaces, not eight) and was caught only because it prints its count, the fourth time this phase that has saved a mutation from being vacuous. (3) path_audit DEFAULT_SCANNED_ROOTS named setup/codex and NOT setup/opencode, so its PASSED WITH 7 SUPPRESSED was a statement about 1,755 lines it had never read. Root added; still 7 suppressions, so the adapter is clean - but now clean BECAUSE CHECKED, proven by planting a doubled-prefix violation (exit 1 naming the file, exit 0 on revert). CARRIED: property 2 still has no mutation coverage for the same unchanged reason; the suite is still not a CI gate; setup/claude-code/ is still outside every scanned root, the same gap setup/opencode/ had."
    gate: "none"
    outcome: "OpenCode installs and registers the same named core skills"
    status: completed
    complexity: high
    priority: high
  - id: "loop-004-cigate"
    content: "UNPLANNED: make the adapter-parametrised suite a CI gate that is unable to pass silently, and close the setup/claude-code/ scanned-root gap"
    repository: "advanced-planning"
    base_sha: "loop-004-3"
    allowed_paths: [".github/workflows/ci.yml", "platforms/python/path_audit.py", "platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "core/", "setup/", "platforms/codex/", "platforms/opencode/", "platforms/shared/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "wiring the suite into CI is NOT the task: making it unable to pass silently is. pytest.skip means an absent interpreter turns 74 cases into green silence, measured at 32 passed / 42 skipped / exit 0"
      - "the skip guards escalate to FAILURE under AP_REQUIRE_ADAPTER_INTERPRETERS=1 and still SKIP when it is unset - the second half is the developer-laptop regression"
      - "ci.yml asserts both interpreters exist AND sets the env var; both are needed, the assertion for a legible fast failure and the variable as the backstop if the assertion is ever edited away"
      - "skips must NOT be detected by parsing pytest output - a parsed string is the precise defect class this phase found three times; the env var is a fact about the process, not a sentence about it"
      - "ci.yml is validated with a real YAML parser, not by eye: a worker previously left it invalid, breaking every job, having run its Python four times without once parsing the file it edited"
      - "every proof is paired with a pre-change baseline, so a green is only ever reported alongside the red from the same check"
    evidence: ".advanced-plans/evidence/2026-08-28-loop-004-cigate-ci-gate.md - worker commit 05918a5, controller tidy c6f7a53 on loop-004-cigate (LOCAL ONLY). UNPLANNED, inserted by human decision 'CI gate first, then 004-4' after loop-004-3 found three instruments green over ground they never examined and none of them could have been caught by CI. The premise was measured BEFORE any change, on the pre-change tree, so no baseline could be tuned to the worker output: BASELINE A - a .advanced-.advanced- violation planted under setup/claude-code/ gave path_audit exit 0, NOT CAUGHT; BASELINE B - the adapter suite with pwsh stripped from PATH gave 32 passed, 42 SKIPPED, exit 0. Baseline B is the finding: 42 of 74 cases evaporate and the job still reports success, so 'wire the suite into CI' would have installed a fourth instance of the same defect INSIDE the remedy. The worker changed three files in scope (setup/claude-code into DEFAULT_SCANNED_ROOTS; an AP_REQUIRE_ADAPTER_INTERPRETERS escalation in both skip helpers; a command -v assertion step plus the env var on the pytest step in ci.yml) and reported that proofs 3 and 4 were BEYOND IT - it could not strip pwsh from its own PATH - rather than claiming them. Second consecutive worker on this branch to decline a proof it could not run. All escalation proofs are therefore controller-side, six groups, each paired with its baseline: (1) ci.yml asserted against the object returned by yaml.safe_load and never against raw text - 4 jobs parse, the assert step PRECEDES pytest, the env var is on the same command line, no other job runs the suite unguarded; (2) planted violation now exit 1 naming setup\\claude-code\\install.sh:543 [doubled-prefix], exit 0 on revert, against baseline A exit 0; (3) var=1 with pwsh stripped gives 8 failed + 34 errors + 32 passed, exit 1, message naming the missing interpreter 84 times - and 8+34 = exactly the 42 that baseline B had silently skipped, so nothing was lost or invented in the conversion; (4) var UNSET with pwsh stripped still gives 32 passed / 42 skipped / exit 0, byte-identical to baseline B, so the developer without PowerShell is not regressed; (5) both helpers proven symmetric by driving shutil.which directly, since /usr/bin cannot be stripped from PATH without destroying the shell; (6) both interpreters present and var set gives 74 passed, 0 SKIPPED - the skip count is now zero rather than 42. A FIFTH INSTANCE OF THIS PHASE DEFECT CLASS WAS FOUND, AND IT WAS THE CONTROLLER OWN: proof 2 first reported 'audit output names the offending file: NOT NAMED' against an audit that had named it perfectly, because path_audit prints an ABSOLUTE path with the platform separator and the check grepped a forward-slash literal that cannot occur on Windows. Repaired and proven by two-way discrimination - repaired check reads 0 clean / 1 planted, original reads 0 BOTH WAYS. Four rounds of stating the rule did not stop it being written a fifth time; it was caught only by running the check in both directions. Controller tidy: the escalation had imported os twice at two nesting depths, consolidated to one module-level import. WITHDRAWN: the two trailing-whitespace lines were first flagged as a worker defect - the file carried 118 such lines before and 120 after, so that is its own norm and no CI job lints style. CARRIED: the one premise NOT measured is that ubuntu-latest actually ships pwsh - if it does not, the assert step turns CI permanently red, which is the intended direction of failure but rests on documentation rather than a measurement, and is settled for free by the first CI run this branch gets. Also carried: the python-tests job is a 3-way matrix so the assertion runs three times per push; property 2 still has no mutation coverage; test_self_heal_integration.py:586 still fails on its own hard-coded absolute path, as it does on main."
    gate: "none"
    outcome: "the adapter suite can no longer report success while its cases vanish, and setup/claude-code/ is audited"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-004-4"
    content: "Run the fixture programme on each host, on that host — one phase, one loop, one external task — and record what actually happened rather than what the adapter intends"
    repository: "a scratch fixture project outside both checkouts"
    base_sha: "loop-004-3"
    allowed_paths: ["a scratch fixture project under the session scratchpad only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "any path inside either repository checkout"]
    provider: "codex for the codex fixture, opencode for the opencode fixture — each adapter is exercised by its own host, which is the entire point"
    worktree_owner: "herdr"
    checks:
      - "on each host: create one phase, decompose one loop, and emit one external task envelope that validates against the loop-002-2 schema"
      - "install BOTH adapters into one fixture project, in both orders, and show one identical .agents/skills/ tree. This is the only place loop-004-1's collision decision is exercised on a real host rather than asserted"  # added 2026-08-28
      - "the envelope is validated by the loop-002-4 validator, not by eye"
      - "idle, done and terminal silence are not completion evidence — read the produced files and check them"
      - "record the invocation and model for each run, the way tests/adherence/MANIFEST.json does, so a re-run is reproducible"
    evidence: ".advanced-plans/evidence/2026-08-28-loop-004-4-fixture-programme.md (AAW commits 22a77a9, 1971cd1). Both adapters were exercised on their own host, in two fixtures under the session scratchpad, and NOTHING was written to either repository checkout. CHECK STATUS, stated honestly: check 2 SATISFIED - both adapters installed into one project in BOTH orders gives a byte-identical .agents/skills/ tree, 19 files across 8 skills, and the comparison was proven able to discriminate by mutating one hash. Check 4 SATISFIED throughout - every host claim was re-derived from disk or from the host's own datastore, never from its summary. Check 5 SATISFIED - opencode ran Qwen3.5-397B-A17B-FP8 via elm, agent build, session ses_fb6242628ffeImXpXTOVVtBV8L, 429355 in / 1866 out, read from opencode.db; codex ran gpt-5.6-terra at effort medium, cli 0.150.1, sandbox workspace-write with network_access false, 248215 in / 4314 out, read from its session rollout. Check 3 SATISFIED on opencode - envelope-001.json validates at exit 0 under state_validate external-task-envelope, and the SAME invocation form was proven able to fail by deleting base_sha (exit 1, Missing required property). CHECK 1 IS SATISFIED ON OPENCODE ONLY. codex created the phase and stopped correctly at the gate; it did not decompose a loop or emit an envelope, because the codex account stood at 98 percent of its weekly quota with five days to reset and the pane was parked on a rate-limit modal. Skipping codex stage 2 was a HUMAN DECISION taken on that evidence, not an omission - and its marginal yield was low, because codex stage 1 had already replicated both host findings. FINDINGS. (1) The phase verb never touches the runtime, on EITHER host - ap.py invocations are 0 on opencode and 0 on codex, against 1 Test-Path existence check each. It is a property of the skill, not of a host: plan_io has no create_phase_plan, which the skill itself documents. Contract 6 is unenforceable for the opening verb because there is nothing to reach. Stage 2 on opencode used ap.py SEVEN times, which scopes the finding rather than widening it - the runtime is reachable and is used wherever a function exists. (2) Neither host runs POSIX sh on Windows. All 7 codex shell commands are PowerShell, as were 7 of 8 opencode ones; in both transcripts exactly one fragment (python --version) is valid POSIX and it sits inside a semicolon-joined PowerShell line. Any skill, envelope or contract prescribing POSIX shell will not run as written on either host, and nothing in either adapter says so. (3) The installer binds the project to the installing checkout - AP_SOURCE_ROOT=REPO_ROOT across six installer files - so the fixture executed code from a herdr worktree of a local unpushed branch, and that binding is what raised opencode's permission dialog. LATENT, NOT LIVE: a bounded sweep found runtime.json in no real project, and the control found all 4 fixture copies, so the negative is real. A correction was recorded against my own first statement of this: a removed checkout does NOT break silently - it exits 3 naming the file, the key and three fixes. (4) The decomposition assigned skill using-superpowers to all five todos; the fixture installs eight skills and that is not one of them. (5) The envelope schema validates FORMAT, NOT SEMANTICS - envelope-001.json passes at exit 0 while declaring a repository that is not a git repository, base_ref main and a base_sha of forty zeros. The HOST found and disclosed this itself, unprompted, after tabulating three git probes at exit 128. (6) NEW - codex misreported its own model, saying GPT-5.6 Sol while its own turn_context, the launch command and the pane status line all read gpt-5.6-terra. It correctly declined the two facts it could not observe and then asserted the third wrongly, which is this phase's defect class appearing where there is no filesystem to check against. (7) NEW - codex DOES expose quota: every token_count event in its rollout carries rate_limits.primary with used_percent, window_minutes 10080 and resets_at, monotone across the last eight sessions at 85/86/94/95/95/97/98/98 percent. CLAUDE.md's blanket 'no CLI in this fleet exposes usage or quota' needs narrowing to exclude codex; a draft is prepared. (8) NEW - herdr reported that codex pane as agent_status done while a system-initiated modal awaited a keypress, so a follow-up prompt would have been consumed by the menu. The task HAD completed, so done is not a lie, but the pane-read rule CLAUDE.md states for cursor applies to codex too. CONTROLLER DEFECTS, both mine, instances 6 and 7 of this phase's class: a snapshot diff joining a sha256 snapshot against an md5 listing that reported 0 modified over 0 rows, caught only by the vacuity guard printing the row count; and a grep -c that scored envelope PROSE as a command invocation. A third near-miss was caught by running rather than grepping - state_validate looked absent from a 448-line ap.py and works. A RETRACTION is recorded in the evidence file: I was drafting the claim that the host invented git metadata when it had in fact reported the impossibility and disclosed its placeholders. ENVIRONMENT: the Bash tool's quoted heredoc collapses doubled backslashes before Python sees them, which produced two identical re.error failures, so both invocation counts were taken with no regex at all."
    gate: "none"
    outcome: "Neither adapter ships unexercised — the risk register names 'an adapter is written but never exercised on its host' as high impact, and this is its mitigation"
    status: completed
    complexity: high
    priority: high
  - id: "loop-004-5"
    content: "Cross-model review of both adapters by a provider that built neither"
    repository: "advanced-planning (read-only)"
    base_sha: "loop-004-4"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/"]
    provider: "claude or cursor — must differ from the implementer and from the loop-001-5 reviewer, per the rotate-reviewers rule"
    worktree_owner: "herdr"
    checks:
      - "the reviewer is asked specifically whether either adapter has forked a core skill, and answers with evidence"
      - "the reviewer is asked whether the human gate is real on each host, or whether an absent automatic hook silently skips it — §7.4 forbids the silent skip"
    evidence: "Three review rounds under ~/.herdr/reviews/loop-004-cigate-20260829-{080458,080613,082722}, reviewing fbc559b..c6f7a53 (19 commits, 24 files). Verdict at .advanced-plans/gate-verdicts/phase-6-loop-004-5-multimodel.json with 9 findings and 4 fleet findings, every one independently reproduced from disk by the controller before recording. Round 1 (cursor-grok-4.6-medium) hit a 200000-of-261036-byte envelope truncation that dropped setup/opencode/install.sh entirely - one half of the comparison Q1 asks for - though it was flagged in the envelope, not silent, and cursor demonstrably read past it from the worktree. Round 2 was scoped to exactly those bytes and found the loop's most severe defect, which round 1 had missed for that reason. Round 3 put Qwen on the same questions after agy was found permission-blocked. Both checks in this todo are satisfied: the fork question was asked and answered with file-level evidence, and the human-gate question was asked and answered NO on both hosts."
    gate: "human"
    outcome: "Two of the four hosts are independently verified before the third is built on the same pattern"
    status: completed
    complexity: medium
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Add the Codex and OpenCode adapters beside the Claude Code and Cowork ones, per the SIX
  contracts in `docs/adapting-to-new-platforms.md` and the five requirements in design §7.3.
  The sixth contract — shared Python runtime — was added to that doc on 2026-08-27 by this
  phase's own loop-001, after the design paragraph that says "five" was written. An adapter
  that omits it reproduces loop-001's defect on a new host: thirteen call sites that resolve
  only when the working directory happens to be the source checkout.
  Both install to `.agents/skills/` and merge guidance into `AGENTS.md`, per §7.2.

  ## Specify before building
  loop-004-1 writes both adapter specifications first, using a different provider from the one
  that builds them. Phase 5 established that pattern for a reason: the behaviour matrix caught two
  places where the loop as first written contradicted the intent, before any code existed.

  ## Hard rules
  - Adapters install and register. They do NOT fork a core skill. `core/` is forbidden to the
    build todos so that "I had to change a core file" surfaces as a finding instead of a diff.
  - codex cannot `git commit` from a linked worktree. The codex adapter's checkpoint contract must
    say who commits instead, rather than describing a commit that will not happen.
  - Plannotator is deprecated in AAW. Give the host-neutral manual review command; do not carry
    §7.4's Plannotator wording forward. An absent automatic hook must never silently skip the gate.
  - Every adapter is exercised on its own host, by that host. A fixture run by Claude proves
    nothing about Codex.
  - No remote writes.

  ## Success criteria
  - [ ] both adapters specified contract by contract before either is built
  - [ ] `platforms/codex/` + `setup/codex/` and `platforms/opencode/` + `setup/opencode/` exist
  - [ ] no core skill is forked, proven by digest
  - [ ] each installer writes `.advanced-plans/runtime.json` and the launcher outside the
        scaffold guard, proven by installing into a scratch project and running a module there
  - [ ] one phase, one loop and one validated external task on each host, run by that host
  - [ ] a third provider has reviewed both, and the human gate is confirmed real on each host
---
```

---

```yaml
---
name: "ralph-loop-005"
task_name: "Cursor adapter, and the four-host discovery proof that is the phase's first exit criterion"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-005-1"
    content: "Confirm the phase-3 Cursor decision still holds, and record what cursor-agent's known behaviour costs this adapter before writing it"
    repository: "Advanced-AI-Workflows (read) + advanced-planning (read)"
    base_sha: "loop-004-5"
    allowed_paths: [".advanced-plans/evidence/"]
    forbidden_paths: ["<standard programme forbidden set, except evidence/ which the controller owns>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "PLANNING.md resolved_decisions records 'Cursor runtime: install cursor-agent'. The phase plan's Blocked-by is therefore discharged — confirm that rather than assume it"
      - "cursor-agent demands approval for every non-allowlisted shell command, and its blocked detection is selective and laggy: it sat at a full-screen Workspace Trust modal while reporting idle and interactive_ready. Say what that means for an unattended fixture run"
      - "--trust clears the directory-trust gate under -p but grants NO tools; a write needs -f/--yolo. State which the fixture run needs and why"
    evidence: "A short note recording the decision as live, and the two constraints the adapter and its fixture run must be designed around"
    gate: "none"
    outcome: "The adapter is designed for the CLI as it behaves, not as its documentation implies — the programme has already been caught out by cursor's state reporting once"
    status: completed
    result: "DONE 2026-09-01. All three checks discharged; two returned more than the check asked. Check 1: the decision is live at PLANNING.md:25 - but the open item qualifying it (PLANNING.md:40-46, B11) is now HALF OBSOLETE, and separating the halves is this todo's real output. Obsolete: 'until a human clears those dialogs once' - --trust clears the workspace gate from the command line, so the reviewer fleet is three, not two. Still standing and unfixed by any flag: cursor reports idle/interactive_ready while sitting on a modal. Check 2: the consequence is specific - agent_status is not a completion signal for a cursor pane IN EITHER DIRECTION, so loop-005-3 must take completion from artefacts on disk, not lifecycle state. That is this programme's central defect class again: a check whose subject is a REPORTED STATE rather than a fact read off the machine. Check 3: the premise is correct - --trust grants no tools - and cursor-agent 2026.08.25-3e8eec8 shows four distinct flags (--trust, -f/--force, --yolo as its alias, --sandbox). TWO THINGS THE CHECK DID NOT ANTICIPATE: --mode has NO write value (only plan and ask, both read-only), so mode cannot make the adapter safe; and --sandbox enabled is a third option the checks omit, narrower than Run Everything and the right first try for a fixture run whose blast radius is one scratch directory. --sandbox is NOT YET MEASURED - its existence is read off --help, its behaviour is not, and loop-005-3 must measure rather than assume it. The --trust result is INHERITED from the 2026-08-28 measurement, not re-run today. Evidence: evidence/2026-09-01-cursor-adapter-preconditions.md. Carried: B11 in herdr-ops/FINDINGS.md needs amending, and PLANNING.md's open_items still says the reviewer fleet is two."
    complexity: low
    priority: high
  - id: "loop-005-2"
    content: "Build the Cursor adapter: platforms/cursor/ and setup/cursor/, on the same no-fork terms as loop-004"
    repository: "advanced-planning"
    base_sha: "loop-005-1"
    allowed_paths: ["platforms/cursor/", "setup/cursor/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "core/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "skills to .agents/skills/, guidance to the AGENTS.md fenced block; .cursor/rules/ is used ONLY where a scoped Cursor rule is genuinely necessary, per §7.2"
      - "no core skill forked, proven by digest"
      - "adapter README with the top three failure modes — the trust modal and the per-command approval are two of them"
      - "path_audit exits 0"
    evidence: "The tree, the install run, and the hash comparison"
    gate: "none"
    outcome: "The third and last new adapter exists on the same terms as the other two"
    result: "DONE. Worker commit e32c318 in herdr worktree loop-005-cursor (opencode/Qwen3.5-397B). 5 files, 2200 insertions: platforms/cursor/README.md (184) and setup/cursor/{install,uninstall}.{sh,ps1} (774/532/387/323). Nothing written outside allowed_paths. Derivation from setup/opencode/ is genuine and measured: 62 of 774 changed lines in install.sh, 38/532, 26/387, 24/323; APPROVED_SKILLS byte-identical; skills sourced from platforms/shared/agent-skills and core/skills, never inlined; no .cursor/rules created. Controller harness, baselined before dispatch, went 1/6 to 5/6. TWO OF THE FOUR CHECKS COULD NOT HAVE FAILED. (a) The digest check looked for SKILL.md under platforms/cursor, but NO adapter in this repo ships SKILL.md - skills are copied at install time - so the check had no subject; it reported VACUOUS rather than PASS, which is the only reason this was caught. Re-run against the install script the anti-fork property holds. (b) path_audit exits 0 while never reading a line of the 2200 added: DEFAULT_SCANNED_ROOTS at platforms/python/path_audit.py:140-154 omits platforms/cursor and setup/cursor, and its summary line is IDENTICAL before and after the build. Third occurrence of this defect (setup/opencode was missing at the same point in loop-004-3). The worker reported it unprompted rather than fixing it, correctly, as path_audit is outside its write scope. NOT RUN: the install scripts were never executed (no target project in the worktree), so the loop evidence field half - the install run - is outstanding and deferred to loop-005-3. Two worker claims do not survive checking: it cited 131 changed lines (the envelope number for loop-004-3, not its own; true value 62) and claimed to have verified no-fork by hash when nothing is copied at build time to hash. Evidence: evidence/2026-09-01-cursor-adapter-build.md. Carried: add platforms/cursor and setup/cursor to DEFAULT_SCANNED_ROOTS; replace controller check 3 with one that tests the install script sources rather than shipped files."
    status: completed
    complexity: high
    priority: high
  - id: "loop-005-3"
    content: "Run the fixture programme on Cursor, on Cursor — one phase, one loop, one validated external task"
    repository: "a scratch fixture project outside both checkouts"
    base_sha: "loop-005-2"
    allowed_paths: ["a scratch fixture project under the session scratchpad only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "any path inside either repository checkout"]
    provider: "cursor"
    worktree_owner: "herdr"
    checks:
      - "the envelope validates against the loop-002-2 schema, checked by the validator"
      - "if the run blocks on a trust or approval dialog, that is REPORTED to the controller and left for the user to clear — a blocked agent is not the worker's to answer"
      - "record the invocation, model and mode (write or read-only), so a permission the operator withheld is never confused with a routing failure. tests/adherence/MANIFEST.json is the precedent"
    evidence: "The fixture run, its artefacts, the validator output, and the invocation manifest"
    gate: "none"
    outcome: "Cursor is exercised or its blocker is recorded honestly; it does not ship as an untested claim"
    result: "DONE 2026-09-01. Cursor ran the programme: DISCOVERY.md (1074B), phase-1/plan.md (3231B) and phase-1/loops.md (3916B), all following the installed skills' own templates, in fixture-cursor3 with the install harness at 7 ok / 0 FAIL / 0 VACUOUS (examining 8 skills, 19 byte-compared files, 34-file tree). Steps 1-3 done; step 4 BLOCKED and recorded as BLOCKED.md rather than faked - the prompt forbade working around a block and Cursor obeyed. THE FIRST TWO ATTEMPTS PRODUCED NOTHING AND BOTH FAULTS WERE THE CONTROLLER'S, NOT CURSOR'S. Attempt 1 exited 0 with a fluent greeting and zero artefacts, twice. The AGENTS.md fence was the obvious suspect and was TESTED AND ACQUITTED: with the fence deleted the same prompt gave the same greeting, because the agent re-derives the trigger names from PLANNING.md. Attempt 2, flattened to one line, named the real cause outright - error: unknown option '--json' - where --json occurs INSIDE the prompt (the fixture goal is to add a --json flag). cursor-agent re-tokenises its own -p value and re-parses the pieces as options. That single fact also explains a symptom that had looked separate: a MULTI-LINE prompt silently defeats --trust and reports 'Workspace Trust Required' - a message naming --trust as the fix while --trust is being passed. Measured in fresh untrusted directories: 900 bytes on ONE line trusts fine, 29 bytes on THREE lines does not, so it is newlines and not size. FIX: deliver the prompt on STDIN, which CLAUDE.md already documented and the controller had deviated from; verified against all three failure modes at once, in a directory with trusted-before=0. INVOCATION MANIFEST: cursor-agent 2026.08.25-3e8eec8, model cursor-grok-4.6-medium, mode WRITE via --trust --auto-review, prompt on stdin, 110s. --sandbox enabled is MEASURED AND UNAVAILABLE (requires macOS or Linux), which closes loop-005-1's recommendation that it was the right first try. --force/--yolo deliberately NOT used: auto-approving every shell command is broadening provider permissions and is the operator's call. BLOCKER, verified by the controller rather than taken from the worker: cursor-agent cannot run ANY shell command on this machine. The fair-data-prep plugin declares a Claude Code PreToolUse hook on Bash; Cursor executes it, wraps it in PowerShell and evaluates the wrapper with a POSIX shell, dying at the & of the call operator. Reproduced with a one-line git rev-parse prompt in a fresh hook payload dir. Machine configuration, not the adapter, not specific to advanced-planning, and the operator's to clear. SHIPPING DEFECT FOUND EN ROUTE: setup/cursor/install.sh lines 411-415 lack the backslash that codex and opencode carry at the IDENTICAL line numbers, so the fence ships `-planning phase <goal>` - a command name that does not exist. Measured from installed output, not grep. PLANNING.md escapes it in all three because line 681 sits in a quoted heredoc, and install.ps1 escapes it correctly, so the same adapter writes the name correctly to one file and one host and incorrectly to another. A test asserting the fence text is identical across an adapter's .sh and .ps1 would catch both; none exists. Skill discovery is answered but only by SELF-REPORT (Cursor said it read .agents/skills/ off disk rather than being offered them) and is marked as weaker evidence - loop-005-4 must settle it, not cite it. Evidence: evidence/2026-09-01-cursor-fixture-run.md."
    status: completed
    complexity: high
    priority: high
  - id: "loop-005-4"
    content: "Prove the phase's first exit criterion across all four hosts at once: every target host discovers the SAME named core planning skills, not host-specific copies that have drifted"
    repository: "a scratch fixture project outside both checkouts"
    base_sha: "loop-005-3"
    allowed_paths: ["a scratch fixture project under the session scratchpad only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "any path inside either repository checkout"]
    provider: "controller collects; each host reports for itself"
    worktree_owner: "herdr"
    checks:
      - "install all four adapters into ONE fixture project and list the skills each host discovers"
      - "the NAME SET is identical across all four — a host missing one, or carrying an extra, is a failure"
      - "the CONTENT is identical too: digest every discovered SKILL.md and compare across hosts. Same names with drifted bodies is precisely the failure this criterion exists to catch"
      - "run under a FAKE HOME so a globally installed copy cannot supply the answer — the adherence fixtures established that discipline and it applies here"
    evidence: "The four skill listings, the name-set comparison, and the digest table"
    gate: "none"
    outcome: "The phase's headline criterion has a table behind it rather than four separate assertions"
    result: "DONE 2026-09-01. THE CRITERION FAILS, and not the way the todo anticipated: the files are identical and the RESOLUTION differs. One host of four reads the copy its own adapter installed. By per-surface canary token, each host naming the directory it actually read: codex quoted the .agents/skills token (its own target, correct); opencode quoted the .claude/skills token, i.e. claude-code's copy and not its own; claude quoted the GLOBAL profile description verbatim; cursor never listed phase-plan-creator at all. CHECK 3 PASS over 7 shared names, byte-identical (phase-plan-creator 6c04c90fdc8fa82e, plan-skill-identification c9c5fb19f121bc64, plan-subagent-identification 790f2d9afe37f686, plan-todos 71989ea0178bd73e, progress-report c4a13a7b68c1ebcc, ralph-loop-planner c1609b8140e11d85, schema-design 21e77ab42da375e6); the shared-name count is printed so a zero would report VACUOUS rather than a clean sweep. CHECK 2 FAIL in both directions, but recorded as a CHECK defect rather than a product defect: it demands an identical name set while the phase asks only about core planning skills, and the extra names (companion-detection and permission-config on claude-code; advanced-planning on the other three) are host-scoped BY DESIGN via APPROVED_SKILLS and the two routing designs. Three of four hosts share .agents/skills, so those pairs CANNOT FAIL and compare.py reports them as such rather than counting them as passes. CHECK 4 CANNOT BE HONOURED, and that is itself a measurement: claude under a fake HOME exits 1 (Not logged in), cursor exits 127 (no bundled CLI found under the fake profile), and codex starts but IGNORES the fake HOME for skill discovery - its own stderr names the real profile's .agents/skills while HOME and USERPROFILE both point elsewhere. Only opencode is isolated by it. The per-surface canary is the substitute and is strictly stronger, because it does not care where a host looks: only one file on disk holds the string it must quote. THE INSTRUMENT WAS WRONG TWICE AND THE HOSTS CAUGHT IT BOTH TIMES. v1 appended the token after a quoted YAML scalar's closing quote - codex named it as invalid YAML at line 2 column 427 - so two hosts correctly refused a skill I had corrupted, and the run read as a discovery failure when it was an instrument failure. v2 put the token at the END of a long description, and codex truncated it away under its documented skill-context budget, answering TOKEN=ABSENT for a skill it had just listed. Fixed by injecting inside the scalar at the front, with the injector re-parsing the frontmatter via PyYAML and confirming the token survives into the parsed description before it writes. A third, smaller one: a grep against a probe file that did not exist returned 0 and was nearly recorded as proof codex stayed inside the fake HOME - caught before it entered the record. FINDINGS. F19: platforms/shared/agent-skills/advanced-planning/SKILL.md ships with ZERO frontmatter delimiters, the only one of eleven shipped SKILL.md files, and it is the routing skill for three of five platforms; codex refuses it outright, opencode silently omits it, and NO test anywhere asserts frontmatter on a shipped skill, which is why it shipped. F20: opencode reads .claude/skills and it wins, so the APPROVED_SKILLS exclusion of companion-detection and permission-config is not enforced at the discovery layer wherever claude-code is installed alongside. F21: on a real profile, claude and cursor serve global copies over the project's; claude also warned the workspace is untrusted, which is a live alternative cause and is NOT discriminated here, though either way the project copy did not win. F22: setup/cowork/create-zip.sh exits 127 because zip is not installed, and no test references it, so the fifth platform's content identity was derived source-level from the script's own file list - cowork's 9 equal claude-code's 9 and the 7 cross-host skills are identical across all five platforms. F23: a host's skill LIST is unstable evidence - the same opencode invocation on the same fixture listed 10 names and then 7 - while the token is verbatim and can only have come from one file, which is a second reason check 2's FAIL is a defect in the check. Corroboration: codex is 0.152.0, not the 0.150.1 recorded in CLAUDE.md; all three non-Claude fences coexist in one AGENTS.md, the first three-way proof of loop-004-1's collision decision, where loop-004-4 proved two. Both canary tokens were verified absent from the entire repo checkout before every probe. Evidence: evidence/2026-09-01-four-host-skill-discovery.md."
    status: completed
    complexity: high
    priority: high
  - id: "loop-005-5"
    content: "Update docs/adapting-to-new-platforms.md so the contract tables include all five adapters, and the guide describes the system as it now is"
    repository: "advanced-planning"
    base_sha: "loop-005-4"
    allowed_paths: ["docs/", "STRUCTURE.md", "README.md"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "each of the five contract tables gains a Codex, an OpenCode and a Cursor row"
      - "the Minimum Adapter Checklist item 'No .claude/ paths in a non-Claude Code adapter' is now machine-enforced for core/ by loop-003 — say so, and say what is still only checklist"
      - "STRUCTURE.md and README.md describe five platforms, not three"
    evidence: "The docs diff"
    gate: "none"
    outcome: "The guide the next adapter author reads is true — a doc that describes three platforms while five ship is how the sixth adapter gets built wrong"
    result: "DONE 2026-09-01. All three checks PASS, but it took THREE review rounds, and the two rounds that failed failed in exactly the way this phase exists to catch: a fluent sentence whose subject was never checked. ROUND 1 (advanced-planning ce620ce) got the structure right - all five contract tables gained a Codex, an OpenCode and a Cursor row, and Contract 5 carried the codex exception correctly - and got three claims wrong. (a) 'the Claude Code, Codex, OpenCode and Cursor adapters share a common implementation pattern': claude-code's install.sh is 674 lines against the others' 774, and greps ZERO for .agents/skills or AGENTS.md, so it shares none of the mechanism; the group is three, not four, and pointing the next adapter author at claude-code as a reference sends them to the wrong file. (b) 'the one genuine behavioural difference among the five adapters' - it is the one difference among the THREE that are otherwise the same adapter; Claude Code and Cowork differ from them in several ways already visible in the same tables. (c) A 'Machine enforcement status' paragraph listing six checklist items as NOT machine-enforced, of which THREE have named tests in the same checkout: test_every_source_call_site_is_in_the_substitutable_form (test_ap_launcher.py:713 - which the guide ITSELF cites sixty lines above the edit), test_installer_records_the_runtime_outside_the_scaffold_guard (test_ap_launcher.py:859), and test_home_resolution_agreement.py's seven. It asserted a negative it had not searched for, which would have told an adapter author that three enforced rules were optional. ROUND 2 (3e08de3) fixed all three, and adopted 'no test found' in place of 'not machine-enforced' - an honest statement about the search rather than an unestablished claim about the repository. ROUND 3 (0cbb206) caught the worst one, which both earlier rounds carried: INVENTED FILE PATHS IN THE TWO FILES WHOSE ONLY JOB IS TO DESCRIBE THE FILE TREE. STRUCTURE.md gave codex, cursor and opencode an install.sh and a SKILL.md each; ls shows README.md and nothing else in all three, and find -name SKILL.md over those directories returns zero. The installers live in setup/HOST/, and the routing skill is ONE file at platforms/shared/agent-skills/advanced-planning/SKILL.md - which is precisely WHY the three installers are identical, so the invented layout also destroyed the explanation. Round 3 removed the six invented entries and added platforms/shared/ to the tree, where the shared skill and the three reference prompts actually live. MY OWN FIRST CHECK WAS VACUOUS, and it is the same lesson as loop-005-4's canary. A regex for slash-separated paths across both documents found 14, all of which existed - a clean sweep over the wrong subject, because a tree draws bare filenames under box-drawing and almost never spells a full path. The check that works reconstructs each entry's path from its indentation and asserts it exists: 71 entries, and it found the six invented ones immediately. A vacuity guard on the entry count is what stopped 14 being recorded as a pass. CONTROLLER COMMIT a2f8fbc, three stale counts the tree walk surfaced, all counted off disk rather than incremented: STRUCTURE.md listed new-loop.md which does not exist (the command is next-loop.md, listed beside it) and listed 8 of the 14 command files, omitting run-gate among six others - the gate reviewer this programme turns on; README.md said 11 slash commands against 14, and 70 tests against 951, which matches the full run's 950 passed / 1 skipped exactly. The command block is now generated from the directory listing and states its own count, so it cannot drift silently again. None of the three was introduced by this loop. CHECKS. 1 PASS: all five contract tables carry Claude Code, Codex, OpenCode, Cursor, Cowork and Generic, parsed from the markdown rather than eyeballed, with an assert that exactly five tables were found so a regex that matched nothing would fail rather than sweep. 2 PASS: the checklist item now says path_audit.py enforces it for core/ and for four of the five adapters and names the four, says platforms/cursor and setup/cursor are absent from DEFAULT_SCANNED_ROOTS so for Cursor it is checklist-only, and separates what IS enforced with test names from what has no test found. 3 PASS: both STRUCTURE.md and README.md name all five adapters, and 71 of 71 tree entries under platforms/ and setup/ resolve to files that exist. F24: STRUCTURE.md's command tree had drifted six entries behind the directory for long enough that nobody noticed run-gate was missing from it - the failure mode of any hand-maintained tree, and the reason that block is now generated. The four advanced-planning commits and this controller one all remain UNPUSHED, per the standing decision; advanced-planning is now at 8 unpushed commits and has still never had a push approved."
    status: completed
    complexity: medium
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Add the Cursor adapter, then prove the phase's first exit criterion across all four hosts:
  every target host discovers the same named core planning skills, not host-specific copies that
  drift.

  ## What the four-host proof has to be
  Four separate "yes it works" reports are not the proof. Install all four adapters into ONE
  fixture project, under a fake HOME, and produce a table: skill name set per host, and a digest
  per discovered `SKILL.md`. Identical names with drifted bodies is exactly the failure the
  criterion names, and only the digest column catches it.

  ## Hard rules
  - A blocked cursor agent is the user's to clear. Report it; do not answer the dialog.
  - Record mode (write or read-only) per run. A permission the operator withheld is not a defect
    in the adapter, and conflating the two corrupts the evidence.
  - Fake HOME, always. A globally installed skill answering for the adapter would make the whole
    table meaningless.
  - No remote writes.

  ## Success criteria
  - [ ] the phase-3 Cursor decision is confirmed live and its two CLI constraints are recorded
  - [ ] `platforms/cursor/` + `setup/cursor/` exist, no core skill forked
  - [ ] a fixture programme run on Cursor, or its blocker recorded honestly
  - [ ] one table, four hosts, identical name sets AND identical digests, under a fake HOME
  - [ ] the adapter guide, STRUCTURE.md and README.md describe five platforms
---
```

---

```yaml
---
name: "ralph-loop-006"
task_name: "The boundary made executable — ACC-08, evidence-gated advancement, and v0.17.0 staged"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-006-1"
    content: "Teach the orchestration skills to EMIT an external task envelope rather than mutate programme state from a worker worktree"
    repository: "advanced-planning"
    base_sha: "loop-005-5"
    allowed_paths: ["core/skills/", "core/agents/", "platforms/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "the worker-role prompt writes an envelope validating against the loop-002-2 schema; it does not write loop-ready.json, loop-complete.json, PLANNING.md or history.jsonl itself"
      - "the controller role is the only writer of programme state, and the skills say so in the imperative rather than as background"
      - "any change under core/ must still pass the loop-003 host-neutrality rule — this is the todo most likely to reintroduce a host token, since it is editing prompts"
      - "python -m pytest platforms/python/tests/ green"
    evidence: "The diff, an emitted envelope, and its validation"
    gate: "none"
    outcome: "The controller/worker boundary is in the instructions the worker actually reads, not only in the design document"
    status: completed
    complexity: high
    priority: high
  - id: "loop-006-2"
    content: "Make ACC-08 an executed test: a worker that attempts a planning-state edit fails collection, and programme state does not advance"
    repository: "advanced-planning"
    base_sha: "loop-006-1"
    allowed_paths: ["platforms/python/", "platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "the test constructs a result whose changed_paths include a forbidden planning-state path, and asserts collection FAILS and names the offending path"
      - "ACC-13 is the same machinery for a path merely outside allowed_paths — add it in the same test module while the fixture is there"
      - "assert the negative too: programme state is unchanged after the failed collection. A test that only checks the error message would pass while state advanced anyway"
      - "the risk register says 'the worker/controller boundary is documented but not enforced' and that ACC-08 must be an executed test, not a policy statement. Satisfy that literally"
    evidence: "The test, its output, and the state-unchanged assertion"
    gate: "none"
    outcome: "The boundary is enforced by something that runs, and it is proven to fail when crossed"
    status: completed
    complexity: high
    priority: high
  - id: "loop-006-3"
    content: "Make collected evidence advance a loop only after BOTH schema validation and gate validation pass, and prove each half independently"
    repository: "advanced-planning"
    base_sha: "loop-006-2"
    allowed_paths: ["platforms/python/", "platforms/python/tests/", "core/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "case A: schema-invalid evidence with all gates passing does NOT advance"
      - "case B: schema-valid evidence with a failing gate does NOT advance"
      - "case C: both pass, and it advances"
      - "ACC-12 belongs here: an idle agent with a failing test is marked review or failed. Idle is not success — the programme has recorded that idle, done and terminal silence are not completion evidence, and this is where it becomes code"
    evidence: "The three cases with their outcomes, and the ACC-12 case"
    gate: "none"
    outcome: "Both halves of the advancement gate are load-bearing, demonstrated by removing each in turn"
    status: completed
    complexity: high
    priority: high
  - id: "loop-006-4"
    content: "Full-suite verification across everything phase 6 added, run from a clean checkout state"
    repository: "advanced-planning"
    base_sha: "loop-006-3"
    allowed_paths: ["none — verification only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "codex gpt-5.6-sol effort high — verification, not implementation"
    worktree_owner: "herdr"
    rewritten: "2026-09-02, on the user's decision, AFTER the checks were run — the measurements are what forced it. Check 3 named --layers source,project, which cannot pass in this repository by its own documented design: two independent verifiers measured 0 current, 0 stale, 27 missing, and .github/workflows/ci.yml lines 181-186 already record that exact failure as the reason CI replaced the pair with source,global, with TestCIAuditsALayerItCanActuallyHave failing the build if anyone re-adds it. A check that cannot pass is the mirror of a check that cannot fail, and had it been 'fixed' in the code rather than in the plan it would have broken something real. Its caveat that the audit compares by MTIME was also false: install_audit contains zero mtime references and compares EOL-normalised SHA-256 digests, which is strictly stronger. Both verifiers reached that independently; the claim traces to docs/adapting-to-new-platforms.md:182 and is carried, not fixed here. Check 6 assumed the main checkout's untracked set. Recorded against the outcome line: the declared provider no longer satisfies its 'implemented none of it' clause, because codex gpt-5.6-luna authored 14da314 in this phase after this todo was written. The operator accepted that on 2026-09-01 on the ground that the controller had already verified that commit independently, so codex judged only the 18 commits it did not touch."
    checks:
      - "python -m pytest platforms/python/tests/ -v — green, with the new tests visible in the count"
      - "python -m platforms.python.path_audit — exit 0"
      - "python -m platforms.python.install_audit --layers source,global — the pair CI actually runs, and the only one with a real subject here. NOT source,project: .claude/settings.json is tracked, so .claude/ always exists, install_audit's 'not found — skipped' guard never fires, and all 27 source files read as missing. Drift against the global layer is EXPECTED while commits sit unpushed; what is checked is that the audit had a subject and said so, not that the number is zero"
      - "python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/ — still dependency-free"
      - "CI job 2's inline python — passes, AND its scope is reported rather than assumed: it globs core/state/*.json only, not core/schemas/, and validate({}, schema) reaches nested type values only for properties present in the instance. Say what it did not examine"
      - "git status clean. In a LINKED WORKTREE that means fully clean: untracked files are per-working-directory, and setup-antigravity.js is untracked in the main checkout, not here"
    evidence: "Every command with its exit code and output"
    gate: "none"
    outcome: "The phase's own suites are green before the gate is asked to judge it, and by a provider that implemented none of it"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-006-5"
    content: "Stage the v0.20.0 release locally: VERSION, CHANGELOG, and the release checklist. Do not publish"
    repository: "advanced-planning"
    base_sha: "loop-006-4"
    allowed_paths: ["VERSION", "CHANGELOG.md", "docs/release-checklist.md"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout drives; the commit is made in advanced-planning)"
    rewritten: "2026-09-01, on the user's decision. The original said VERSION 0.16.0 -> 0.17.0 and hand-listed the CHANGELOG contents. Measured at rewrite time: origin/main is at 0.19.0, with 0.17.0 and 0.18.0 both shipped on 2026-08-31 and 0.19.0 on 2026-09-01, so every check in the original was unsatisfiable. The intent - a release staged locally and publishable on one command, nothing pushed - is unchanged. Check 2 is the substantive repair: the old one named the contents the author expected, which is a check whose subject is a string the plan typed; the new one derives them from the unreleased commit range, so work landing between this rewrite and the todo running cannot be silently omitted."
    checks:
      - "VERSION 0.19.0 -> 0.20.0. A minor bump, not a patch: the range contains a new adapter"
      - "the CHANGELOG's [Unreleased] section currently reads '_Nothing yet._' while eight commits sit unreleased - it is emptied into a 0.20.0 section"
      - "the 0.20.0 entries are DERIVED from `git log --oneline origin/main..HEAD`, not from a list written in this todo. Every commit in that range is either named in the CHANGELOG or recorded, in the loop result, as deliberately not user-visible with the reason. A count is taken both sides and they must agree"
      - "each entry names the loop it came from, as the CHANGELOG's existing sections do"
      - "docs/release-checklist.md is FOLLOWED, and each item is recorded as done or explicitly not applicable"
      - "NO tag is pushed, NO release is created, NO PR is opened. The programme's external-write rule stands and covers this repository too. At rewrite time advanced-planning holds 8 unpushed commits and has never had a push approved; staging a release does not change that"
      - "the controller appends a release_staged event to history.jsonl with event, phase and version, per the programme's release-staging convention"
    evidence: "The diff, the commit-range count on both sides, the completed checklist, and the history event"
    gate: "human"
    outcome: "v0.20.0 is ready to publish on one command, its CHANGELOG accounts for every unreleased commit rather than the ones the plan happened to remember, and publishing it remains the user's decision"
    status: completed
    complexity: medium
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Close the two exit criteria that are about behaviour rather than files — only the control
  checkout updates programme state (ACC-08), and collected evidence advances a loop only after
  both schema and gate validation pass — then stage v0.17.0.

  ## Why this loop is last
  It edits `core/` prompts, which is the one place the loop-003 host-neutrality rule is most
  likely to be tripped, and it depends on the schemas from loop-002 and the adapters from
  loops 004–005. Running it earlier would mean writing the boundary against contracts that do
  not exist yet.

  ## Hard rules
  - ACC-08 must be an EXECUTED test. The risk register names "documented but not enforced" as the
    failure mode and this todo as the mitigation.
  - Assert the negative. A collection test that checks only the error message would pass while
    programme state advanced anyway.
  - Idle is not success. ACC-12 is code in this loop, not a note.
  - Verification is done by a provider that implemented none of it.
  - v0.17.0 is STAGED. No tag push, no release, no PR.

  ## Success criteria
  - [ ] the worker role emits a validated envelope and writes no programme state
  - [ ] ACC-08 and ACC-13 are executed tests that fail when crossed, with state proven unchanged
  - [ ] schema-invalid and gate-failing evidence each independently block advancement
  - [ ] every suite green, run by a non-implementing provider
  - [ ] v0.17.0 staged locally with the checklist followed and a release_staged event recorded
---
```

---

```yaml
---
name: "ralph-loop-007"
task_name: "Gate remediation - wire what was built, and make the checks able to fail"
max_iterations: 3
on_max_iterations: escalate

opened: "2026-09-02, by the phase-6 gate returning fail on attempt 1. Three reviewers reached fail independently and agreed on only two of six criteria; the disagreements are what produced the finding list below, and each todo names the criterion it discharges. No loop was reverted: nothing built in loops 001-006 was found wrong. What was found is machinery that was built, unit-tested, and never called, plus assertions that cannot fail. Reverting the loops that built it would remove the work and leave the gap."

handoff_summary:
  done: "007-1 through 007-4 landed in full, and 007-5 in half, across three branches off 171d193; all six commits were merged conflict-free onto the local branch loop-007-integration so the gate had one tree to read. No branch was pushed and main is untouched at 171d193."
  failed: ""
  needed: "007-6 (host discovery) and 007-7 (the fixture programme on every host) are gate: human and remain open. They carry criteria 1 and 2, so a second fail on those two is the expected result of attempt 2 rather than a surprise. Attempt 2 asked the reviewers to judge the phase with those two declared open, and returned fail from all three. It also produced two findings loop 007 did not anticipate: path_audit's host-directory regex omits .agents/, so criterion 5 is not met despite 007-4's four new roots and four new tests (widening a check's roots does not widen its tokens); and 007-5's first check was never done, corrected above. Criterion 4 remains failed on two of three reviewers plus controller measurement. CRITERION 5 IS NOW DISCHARGED (2026-09-02, operator decision to fix it inside this loop rather than open loop-008): the token, the three named exceptions, and two tests are in the integration branch, and the real-repo audit runs green at 24 suppressed against 20 before - exactly the four declared occurrences across three platforms/shared/ files. The reviewer split on this criterion is worth keeping: two of three marked it MET and both had checked the ROOTS, while the single reviewer who marked it failed had checked the TOKENS. A majority vote would have passed a criterion a controlled mutation shows was not met, which is why consensus is a prompt to verify rather than a substitute for it. The origin is recorded against loop-003-2, where the check that named the token and the implementation that dropped it sat in the same todo."

todos:
  - id: "loop-007-1"
    content: "Give ACC-08 a production caller: the collection path must run the path-scope check against real git output, not only in tests"
    repository: "advanced-planning"
    base_sha: "loop-006-5"
    allowed_paths: ["platforms/python/", "platforms/python/tests/", "core/skills/", "platforms/claude-code/", "platforms/codex/", "platforms/cursor/", "platforms/opencode/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 3 - only the control checkout updates programme state (ACC-08). Failed by all three gate reviewers, and independently reproduced a fourth time by the controller."
    checks:
      - "grep proves at least one caller of the path-scope check OUTSIDE platforms/python/tests/. Today there is none: validate_path_scope is a pure function over three lists of strings and every caller is a test. That is the finding, so the grep is the check"
      - "the caller supplies changed_paths from `git diff --name-only`, as scope_policy.py's own docstring says it should, rather than from a literal the caller typed"
      - "an END-TO-END test drives the production entry point - not the pure function - with a worker result whose changed paths include .advanced-plans/state/, and asserts collection fails and names the offending path"
      - "positive control, F33: the same production entry point with clean paths must PASS. A guard that rejects everything is as useless as one that rejects nothing, and only the pair distinguishes an instrument fault from a subject fault"
      - "python -m pytest platforms/python/tests/ green"
    evidence: "The grep before and after, the diff, and both halves of the control pair with their output"
    gate: "none"
    outcome: "The boundary the phase claims to enforce is enforced by something production actually runs"
    landed: "3f98cbd on loop-007-acc08. evidence_gate.py now calls validate_path_scope at two production sites (lines 242, 437); every caller before this was a test."
    status: completed
    complexity: high
    priority: high
  - id: "loop-007-2"
    content: "Replace the negative-assertion tests that cannot fail, and prove the replacements can"
    repository: "advanced-planning"
    base_sha: "loop-007-1"
    allowed_paths: ["platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 3, evidence half. Found by code-review-agent alone; neither other reviewer saw it."
    checks:
      - "TestNegativeAssertion_StateUnchangedOnFailure in test_scope_policy.py writes a state file under tmp_path, passes an unrelated path STRING to validate_path_scope, then byte-compares the file. validate_path_scope opens no file and can modify nothing, so the assertion cannot fail. Rewrite it against the production caller from loop-007-1"
      - "the replacement is proven non-vacuous by MUTATION: disable the guard, run the test, show it goes red, restore the guard, show it goes green. A negative assertion that was never observed to fail is a claim, not a test"
      - "the mutation run is recorded with its output. 'I checked and it passes' is what the original test also said"
      - "python -m pytest platforms/python/tests/test_scope_policy.py -v green after restoration"
    evidence: "The old test, the new test, and the red-green mutation pair"
    gate: "none"
    outcome: "The test that proves ACC-08 holds is itself proven able to fail"
    landed: "6cca55c on loop-007-acc08. The old assertion byte-compared a file the pure function never opened. Replaced against the production caller and mutation-proved red-green."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-007-3"
    content: "Make gate validation load-bearing at every production call site, not only where a caller opts in"
    repository: "advanced-planning"
    base_sha: "loop-007-2"
    allowed_paths: ["platforms/python/", "platforms/python/tests/", "platforms/claude-code/", "platforms/codex/", "platforms/cursor/", "platforms/opencode/", "core/skills/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4 - collected evidence advances a loop only after BOTH schema and gate validation pass. codex failed it; the other two marked it met by asking whether the mechanism exists rather than whether anything calls it."
    checks:
      - "next-loop.md step 7a is the only production call of validate_loop_complete_advancement and it passes no verdict_paths. evidence_gate.py then takes the else branch and gate 2 passes by default with a hardcoded result. Fix the call site, not the default"
      - "the other three adapters do not call it at all. Either they call it, or the docs say plainly which adapters gate advancement and which do not - an undocumented gap is the defect, a documented one is a scope decision"
      - "a test drives each adapter's own call shape with a FAILING verdict and asserts advancement is blocked. Per adapter, not once generically"
      - "the default-pass branch keeps a test that pins it as deliberate, so a future reader cannot mistake it for an oversight"
      - "python -m pytest platforms/python/tests/ green"
    evidence: "The call sites before and after, and one blocked-advancement case per adapter"
    gate: "none"
    outcome: "A failing gate verdict stops a loop advancing on every host, or the hosts where it does not are named in writing"
    landed: "e49506d on loop-007-acc08. Step 7a read an envelope nothing writes, so its first real run would have raised FileNotFoundError; it now derives scope from default_worker_scope and was EXECUTED in three scenarios before commit. Adapter coverage was scoped down: claude-code gates advancement, the other three are README-only and cannot, which is recorded rather than claimed fixed."
    status: completed
    complexity: high
    priority: high
  - id: "loop-007-4"
    content: "Extend the path audit to the roots it never scanned, and prove each new root can go red"
    repository: "advanced-planning"
    base_sha: "loop-007-3"
    allowed_paths: ["platforms/python/", "platforms/python/tests/", "docs/", ".github/workflows/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 5 - the CI path audit fails on any host-specific path in core/. codex failed it; the other two read the criterion as being about this diff rather than about coverage."
    checks:
      - "DEFAULT_SCANNED_ROOTS has 13 entries and reaches only core/agents and core/skills. core/schemas and core/state are core/ directories the criterion names and the audit has never looked at. Add them"
      - "platforms/cursor and setup/cursor are also unscanned - carried from loop-006-5 as a known gap and recorded in the release checklist rather than fixed. Fix it here"
      - "POSITIVE CONTROL PER ROOT: plant a host-specific path in each newly added root, show the audit goes red naming that root, remove it, show green. Four roots, four red-green pairs. An audit that reports PASSED WITH N SUPPRESSED over a root it cannot see is the exact defect this phase exists to eliminate"
      - "path_audit.py's argparse description is stale and describes something the module no longer does - correct it while here"
      - "python -m platforms.python.path_audit exit 0 on a clean tree, and the per-root list is read rather than the verdict alone"
    evidence: "The root list before and after, and four red-green control pairs"
    gate: "none"
    outcome: "The audit's pass covers the directories the criterion actually names"
    landed: "9603fca + d09c440 on loop-007-audit. Four roots added; test_path_audit.py holds a per-root red-green test for each of core/schemas, core/state, platforms/cursor, setup/cursor."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-007-5"
    content: "Resolve the two instruction defects that make an adapter contradict itself and a compliant reviewer fail validation"
    repository: "advanced-planning"
    base_sha: "loop-007-4"
    allowed_paths: ["platforms/claude-code/", "core/skills/", "core/agents/", "platforms/python/tests/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 3 supporting, plus a defect in the gate machinery itself, found while running the gate."
    checks:
      - "next-loop.md tells the worker to write loop-complete.json at step 6 and names step 7 'Read loop-complete.json', while loop-006-1 rewrote the worker contract to say the worker writes no programme state. Both instructions are live in the same file. Reconcile them and say which is the contract"
      - "run-gate.md instructs reviewers to emit criteria_outcomes.status 'not_applicable'. The gate-verdict schema enum is exactly [met, deferred, failed] with additionalProperties false, so a reviewer that OBEYS the instruction produces a verdict that fails extract_and_validate and is logged as a skipped reviewer rather than as an instruction defect. Measured 2026-09-02 while gating this phase"
      - "a test pins the instruction text against the schema enum, so the two cannot drift apart again silently. This is the second time a phase-6 instruction and its schema disagreed"
      - "python -m pytest platforms/python/tests/ green"
    evidence: "Both diffs and the pinning test"
    gate: "none"
    outcome: "The adapter states one contract, and a reviewer that follows run-gate.md produces a verdict the gate can read"
    landed: "06434b7 on loop-005-cursor discharged the SECOND check only. run-gate.md now instructs 'deferred', the only value in the schema enum that means 'I could not check this', with a test pinning the instruction text against the enum, and that fix was proven live in gate attempt 2: codex emitted deferred and its verdict validated. NOTE the INSTALLED copy at ~/.claude/commands/run-gate.md is stale and still instructs not_applicable."
    not_landed: "The FIRST check was never done, found by code-review-agent in gate attempt 2 and confirmed against the file: next-loop.md Steps 6 and 7 still tell the worker to write and then read loop-complete.json, while core/agents/worker.md says the worker writes no programme state. Both instructions are still live in the same adapter. The controller marked this todo completed on the strength of the commit message rather than the checks, which is the defect class this phase exists to remove. Reconciling the two is Phase 7 work, tracked with the loop-complete.json carve-out."
    status: in_progress
    complexity: medium
    priority: high
  - id: "loop-007-6"
    content: "Host discovery: separate what the adapters control from what the hosts control, fix the first and make the second falsifiable"
    repository: "advanced-planning"
    base_sha: "loop-007-5"
    allowed_paths: ["setup/", "platforms/", "core/skills/", "docs/", "platforms/python/", "platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode for the adapter work; controller for the live four-host measurement"
    worktree_owner: "herdr"
    discharges: "criterion 1 - every target host discovers the same named core planning skills. Failed by phase-goals-agent on measured evidence, which overturned the controller's own ruling that it was met. The controller had compared installer skill lists; the criterion is about what each host DISCOVERS."
    rewritten_scope: "Opened on the operator's decision of 2026-09-02 to remediate everything including host discovery, having been offered the narrower option of waiving this criterion as a recorded host limit."
    checks:
      - "F20: opencode resolves .claude/skills - claude-code's copy - rather than its own adapter's. Determine whether opencode can be pointed at its own directory by configuration we install, or whether it is fixed host behaviour. The answer decides whether this is a defect or a documented constraint, and it must be MEASURED, not reasoned about"
      - "F21: claude and cursor serve global profile copies over the project's. Same question, same standard of proof: an A/B under a fake HOME with the project copy differing from the global one, so which one answered is visible in the content and not inferred"
      - "F23: cursor never listed one skill, so its list is not stable evidence. Establish whether the omission reproduces; an intermittent list cannot support a criterion either way"
      - "the four-host table is re-run under a fake HOME with the DIGEST column, not just names. Identical names with drifted bodies is the failure the criterion actually names"
      - "where a finding is genuinely host behaviour we cannot change, the criterion is rewritten to something falsifiable about the adapter - and the rewrite is recorded with its reason, in the plan, not quietly in a check. Do not mark a criterion met by narrowing it until it fits"
    evidence: "The A/B measurements per host, the four-host digest table, and a written verdict per finding: adapter defect, or host constraint"
    gate: "human"
    outcome: "Criterion 1 is either satisfied or replaced by one that can be tested, with the difference between the two stated rather than blurred"
    status: pending
    complexity: high
    priority: high
  - id: "loop-007-7"
    content: "Complete the fixture programme on the two hosts where it stopped at a dialog, by pre-authorising rather than by answering"
    repository: "advanced-planning"
    base_sha: "loop-007-6"
    allowed_paths: ["docs/", "platforms/", "setup/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "controller drives the hosts; opencode for any adapter change the runs expose"
    worktree_owner: "herdr"
    discharges: "criterion 2 - a fixture programme can create one phase, one loop and one external task on every target host."
    checks:
      - "the two incomplete hosts stopped at trust and approval dialogs that the operator cleared or declined. Pre-authorise instead: herdr-trust.py for claude, --trust --auto-review for cursor. A dialog answered by sending keys is not a passing run and must not be recorded as one"
      - "each host creates one phase, one loop and one external task, and the ARTEFACTS are read back - a host that printed a success banner and wrote nothing has told you about its banner"
      - "record mode per host: write or read-only. A permission the operator withheld is not an adapter defect, and conflating the two corrupts the evidence"
      - "where a host still cannot complete unattended, that is recorded as the result with its blocker named, not as a deferral. A criterion deferred twice is failing"
    evidence: "Per host: the commands, the artefacts read back, and the mode"
    gate: "human"
    outcome: "The criterion has a measured answer on all four hosts, including the answer 'this host cannot, and here is why'"
    status: pending
    complexity: medium
    priority: medium

  ## What this loop is for

  The gate did not find the phase's work wrong. It found three things built and never
  connected, two assertions that cannot fail, and two instructions that contradict
  themselves. Every one of those is the phase's own declared defect class turned on the
  phase: a check that cannot fail, and its mirror, a mechanism whose existence was
  mistaken for its use.

  ## Hard rules
  - A mechanism with no production caller discharges no criterion. Asking "does this exist"
    instead of "is anything calling it" is how two of three reviewers marked criterion 4 met
    over code that never runs.
  - Every guard added here ships with a positive control. Red and green, both observed, both
    recorded. F33.
  - Mutation is the only proof a negative assertion works. Disable the guard, watch the test
    fail, restore it. A test never seen to fail is a claim.
  - Do not narrow a criterion to fit the result. Rewriting one is allowed and sometimes right;
    doing it without recording the reason is how a phase passes its own gate.
  - No remote writes. advanced-planning has never had a push approved and this loop does not
    change that.

  ## Success criteria
  - [ ] the path-scope check has a production caller, driven by real git output, with a red-green pair
  - [ ] the negative-assertion tests are proven able to fail by mutation
  - [ ] a failing gate verdict blocks advancement on every adapter, or the exceptions are documented
  - [ ] the path audit scans `core/schemas`, `core/state`, `platforms/cursor` and `setup/cursor`, each proven able to go red
  - [ ] `next-loop.md` states one worker contract, and `run-gate.md` instructs a status value its schema accepts
  - [ ] every criterion-1 finding has a verdict: adapter defect or host constraint, measured either way
  - [ ] the fixture programme has a measured outcome on all four hosts
---
```

---

```yaml
---
name: "ralph-loop-008"
task_name: "Criterion 4 - make the evidence gate reachable, and unable to pass silently"
max_iterations: 3
on_max_iterations: escalate

opened: "2026-09-02, by operator decision after gate attempt 2. Criteria 3 and 5 were closed inside loop 007; 1 and 2 are the human-gated todos 007-6 and 007-7. That leaves criterion 4 as the only open criterion not gated on manual host work. The gap is NOT what the phrase 'the gate is not wired into three adapters' suggests, and the loop is scoped on the measurement rather than the phrase - see 008-1."

handoff_summary:
  done: ""
  failed: ""
  needed: "Measured by the controller on 2026-09-02, before this loop was written, so the todos below are scoped on facts rather than on the gate reviewers' phrasing. (a) evidence_gate.py has NO __main__ and no CLI; eight modules under platforms/python/ have one and it is not among them. (b) ap_launcher dispatches with runpy.run_module(module, run_name='__main__') and NO allow-list, so any module name the router writes will be run. (c) Consequently the gate is not merely absent from the three non-Claude hosts, it is CALLABLE AND SILENTLY GREEN there: dispatched with the same argument shape that makes state_validate print usage and raise SystemExit(2), evidence_gate returns normally, which the launcher reports as exit 0. A router that called it today would read 'gate passed' from a module that never looked at anything. (d) The shared router is not unvalidated - it runs state_validate at TEN points across three verbs: three in `loop next` (SKILL.md 120, 138, 146), three in `gate current` (166, 190, 196) and four in `resume` (216, 217, 223, 230). The controller first counted four and 008-1 corrected it. What the router never runs is the GATE half, which is the other half of criterion 4's wording: schema AND gate validation. (e) platforms/claude-code/commands/next-loop.md lines 366 and 400 are the only production callers of validate_loop_complete_advancement. The controller then claimed validate_advancement has ZERO callers anywhere; 008-1 corrected that. It has exactly one, at evidence_gate.py:150, inside can_advance_loop - and can_advance_loop itself has none. So there are TWO dead exports in __all__, not one, and can_advance_loop is the dead one."

# Execution order is DOCUMENT order, and the ids are deliberately out of sequence.
# loop-008-5 was moved ahead of loop-008-2 on 2026-09-02, by operator decision: it decides
# what the gate's public API is, and 008-2 builds a CLI on that API, so deciding after
# building is the wrong way round. The ids were NOT renumbered, because "loop-008-2" is
# already cited in commit b3a436d and in the loop-008-1 evidence file, and a renumber would
# leave two meanings of the same identifier - the drift this phase keeps finding.
todos:
  - id: "loop-008-1"
    content: "State the criterion-4 gap as it actually is, and prove the silent pass rather than inferring it"
    repository: "advanced-planning (read-only)"
    base_sha: "loop-007-integration"
    allowed_paths: ["none - read-only"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "codex"
    worktree_owner: "herdr"
    discharges: "criterion 4 - collected evidence advances a loop only after schema AND gate validation. Failed by codex and phase-goals-agent in attempt 2, and independently measured by the controller."
    checks:
      - "run it, do not read it: dispatch platforms.python.evidence_gate through runpy exactly as ap_launcher.py does, and record what happens against platforms.python.state_validate as the control. The controller measured SystemExit(2) for the control and a normal return for the gate; reproduce or refute that, and say which"
      - "confirm from source that evidence_gate.py has no __main__ and that ap_launcher applies no module allow-list. Both are the mechanism; a fix that adds a CLI without closing the silent-dispatch path leaves the hole open for the next module"
      - "count production callers of BOTH gate functions with tests excluded, and give the file and line of each. The controller found one for validate_loop_complete_advancement and zero for validate_advancement. CORRECTED by this todo: validate_advancement has one, at evidence_gate.py:150 inside can_advance_loop, and can_advance_loop has none - so the dead export is can_advance_loop and 008-5 must decide about both"
      - "state what the shared router DOES validate. It runs state_validate at ten points across loop next, gate current and resume, so 'the router does no validation' is false, and a loop written on that phrasing would fix the wrong thing. The controller counted four; the true figure is this todo's, not the controller's"
    evidence: "A table with one row per claim, each marked measured or read, and the exact commands. Any disagreement with the controller's measurement above is the finding, not an error to reconcile quietly"
    gate: "none"
    outcome: "The gap is stated as callable-and-silently-green rather than unwired, so 008-2 and 008-3 fix the mechanism instead of the symptom"
    result: "Run 2026-09-02 as a read-only `codex exec -s read-only -m gpt-5.6-sol` probe on loop-007-integration at 9fd6796; the worktree was verified clean and HEAD unchanged afterwards, so the read-only claim was checked rather than accepted. It CONFIRMED the dispatch measurement independently - state_validate SystemExit(2), evidence_gate returns normally - and confirmed no CLI, no launcher allow-list, and no gate reference anywhere in the shared skill or its four reference prompts. It CORRECTED the controller twice, and both corrections are in this loop: the caller count for validate_advancement, and the router's validation count. It added one finding neither the controller nor the gate reviewers had: the external-dispatch path at SKILL.md 193-196 validates collected evidence SCHEMA-ONLY, and that is the very path this programme uses for its own Herdr workers - so there are two sites needing the gate, not one. Its cited line numbers point at each step's heading rather than the command inside the fence; every one was opened and lands on the right step."
    status: completed
    complexity: low
    priority: high
  - id: "loop-008-5"
    content: "Decide what validate_advancement and can_advance_loop are: the API the CLI should expose, or dead code"
    repository: "advanced-planning (read-only for the decision; the edit lands in 008-2's worktree)"
    base_sha: "loop-008-1"
    allowed_paths: ["none for the decision - the edit is carried out under 008-2"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "codex"
    worktree_owner: "herdr"
    discharges: "criterion 4 - two public functions in __all__ with no reachable caller are either the interface or a liability, and the criterion cannot be assessed while that is undecided. 008-1 established the shape: validate_advancement has exactly one caller, can_advance_loop, and can_advance_loop has none, so the whole pair is unreachable from production"
    checks:
      - "validate_advancement takes evidence, envelope and verdict paths, a wider contract than the loop-complete wrapper the one live caller uses. Say whether the router needs that width; if it does, the CLI exposes it and 008-2's entry point is built on it rather than beside it"
      - "can_advance_loop is decided separately and is the weaker case: it is a boolean thinning of validate_advancement, it discards the reasons an operator needs, and its own docstring at evidence_gate.py:148 tells callers to use validate_advancement instead. A wrapper whose documentation advises against itself and which nothing calls is dead code"
      - "if it does not, DELETE it with its tests rather than leaving it in __all__. Machinery that is implemented, tested and never called is the finding this phase was opened to remove, and keeping it because it might be wanted is how it survived this long"
      - "either way the decision goes into the module docstring, so the next reader does not have to re-derive it"
      - "this todo DECIDES; it does not edit. codex cannot git-commit from a linked worktree - the worktree's git metadata lives in the parent repo's .git/worktrees, outside its sandbox - so the deletion or the docstring is written by the opencode worker carrying 008-2, against this decision. Handing the decision to the implementer is also the right split: the model that decides is not the model that then has to justify what it wrote"
    evidence: "The decision, its reasoning, and the exact change 008-2 is to make"
    gate: "none"
    outcome: "Neither implemented-but-uncalled gate function remains undecided in the module"
    result: "Run 2026-09-02 as a read-only `codex exec -s read-only -m gpt-5.6-sol` probe on the same worktree as 008-1; clean tree and unchanged HEAD verified afterwards. DECISION 1, the interface: neither Python signature is exposed unchanged, because the two router sites cannot supply the same arguments. `loop next` never names an envelope - the token does not occur anywhere in SKILL.md 100-160 - while the external-dispatch block has both an envelope (validated at 190) and an evidence path (196), and NEITHER site has verdict paths. So the CLI takes two subcommands: `collected-evidence EVIDENCE ENVELOPE` routing to validate_advancement, and `loop-complete LOOP_COMPLETE --baseline GIT_REF` which measures changed paths from the baseline, takes scope from default_worker_scope('.') and routes to validate_loop_complete_advancement. That second shape is not invented: it is what the claude-code adapter already does at next-loop.md:397, and test_evidence_gate.py:734 records in its own name why - `does_not_read_the_envelope_that_nobody_writes`. DECISION 2: delete can_advance_loop. DECISION 3: a derived reachability test, not an enumerated one. The controller reached the same three answers independently before reading the probe, which is agreement rather than confirmation; the probe was better on two points the controller had left vague - where changed_paths comes from, and that an absent verdict list must be an explicit assertion rather than a default."
    status: completed
    complexity: low
    priority: medium
  - id: "loop-008-7"
    content: "Make the gate read the policy block it is handed, so evidence that says review FAILED cannot advance a loop"
    repository: "advanced-planning"
    base_sha: "loop-008-5"
    allowed_paths: ["platforms/python/evidence_gate.py", "platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4 - schema AND gate validation. Found by 008-5 and REPRODUCED by the controller, not inferred: a collected-evidence document carrying policy.independent_review_passed=false is schema-valid, ships in the repository as a fixture under tests/fixtures/run-contracts/VALID/, and validate_advancement returns ok=True with zero reasons against it. Measured 2026-09-02 by calling the function on evidence-review-complete.json and envelope-implementation-complete.json unmodified"
    checks:
      - "the mechanism is an omission, not a bug in a branch: grep evidence_gate.py for independent_review_passed, tests_passed and path_scope_passed and every hit is a docstring. Every `policy` reference in the module is about VERDICT FILES; the evidence document's own policy block is never read. So a worker reporting its own review as failed is advanced by the gate that exists to stop it"
      - "the schema is not the place to fix it and must not be changed here. core/state/collected-evidence.schema.json:113 already REQUIRES all three booleans to be present, and its own description says a missing gate must fail validation rather than default to true. It guards against absent, which is correct; false is a legitimate value a worker must be able to report honestly. The gate is what must act on it"
      - "this lands BEFORE 008-2 so the CLI is built on the fixed semantics. A CLI shipped first would expose a gate that passes evidence saying it failed, and 008-4's tests would then pin the wrong behaviour as correct"
      - "red-green using the fixture already in the tree: evidence-review-complete.json currently advances and must stop advancing. Restore any mutated source byte-exact, and carry a positive control - an all-true policy block must still advance, or the new check is simply refusing everything"
      - "say what happens to the existing fixture. It lives in valid/ because it is SCHEMA-valid, which stays true; if a test elsewhere relies on it advancing, that test encoded the defect and is changed with a note saying so"
    evidence: "The grep showing the omission, the before/after run of validate_advancement on the unmodified fixture pair, the diff, and the positive control"
    gate: "none"
    outcome: "Evidence that reports its own policy failure is blocked, and the gate's decision includes the document it was handed"
    result: "Run 2026-09-02 by opencode/Qwen worker `gate-impl` in herdr worktree `loop-008-gate`, commit e0f7104 on top of 9fd6796. Verified by the controller independently - the diff was read, the fixture probed directly, and the suite run here, not taken from the worker report. A new Gate 2b in validate_advancement reads the evidence document's own policy block and appends a `policy_self_review` reason, deliberately named apart from `policy_gates`, which means verdict FILES. Measured: the shipped fixture evidence-review-complete.json now gives ok=False with reasons [(policy_self_review, Worker self-review failed: independent_review_passed=false)] where it gave ok=True and zero reasons before; the positive control with all three booleans true still gives ok=True and reasons=[], so the check is not simply refusing everything; a policy block with a key ABSENT is caught earlier by the schema gate with `/policy: Missing required property`, so the two failure modes stay tellable apart. loop-complete.schema.json was checked and carries no policy block, so scoping the change to validate_advancement alone was correct rather than an omission. ok = len(reasons) == 0 at line 288, so a new reason genuinely blocks. Eight tests added in TestPolicySelfReview, none vacuous; the whole test directory is green at 1073 passed, 1 skipped in 387s (RC=0), run by the controller. One honest limitation recorded rather than papered over: the worker also added a missing-policy-block branch as defence in depth, and that branch is UNREACHABLE in production - validate_document is called unconditionally at evidence_gate.py:207 and there is no flag to skip it, so the schema gate always fires first. Its own test asserts `schema` rather than forcing the branch, which is the honest result; it is left in place because it becomes live if the schema is ever relaxed, but it is an unreachable branch inside the loop about unreachable code, and saying so here is cheaper than rediscovering it."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-008-2"
    content: "Give evidence_gate a CLI whose three failure modes an operator can tell apart"
    repository: "advanced-planning"
    base_sha: "loop-008-7"
    allowed_paths: ["platforms/python/evidence_gate.py", "platforms/python/ap_launcher.py", "platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4"
    checks:
      - "invoked with no arguments it exits NON-ZERO with a usage line naming the module, the way state_validate does. An entry point that exits 0 on no arguments is the defect this todo exists to remove"
      - "the three failure modes 007-3 established for the claude-code caller stay distinguishable here: a path-scope violation, a VACUOUS measurement, and a schema failure. The operator acts differently on each - revert the worker, distrust the baseline, distrust the report - so one undifferentiated non-zero exit is not sufficient"
      - "a VACUOUS measurement must NOT exit 0. loop-007-2 established that a path-scope gate over zero paths must fail rather than pass; the CLI inherits that and a test pins it"
      - "the violating paths are PRINTED, not merely counted. A gate that says '3 violations' sends an operator back to the diff to work out which"
      - "the SHAPE is decided by 008-5 and is not the implementer's to redesign: two subcommands, `collected-evidence EVIDENCE ENVELOPE` and `loop-complete LOOP_COMPLETE --baseline GIT_REF`, each taking `--verdict PATH` repeatably OR a required `--no-verdicts-requested`. The mutually-exclusive verdict flag is the point, not decoration: both validators today turn an omitted verdict list into a fabricated pass (the `else:` branch under the `# Gate 2: Policy gates` comment in BOTH validators - cited without line numbers on purpose, because 008-7 has already moved the second one once), so a router that simply failed to find the verdict files would read as `no review was requested`. Exit 0 advance, 1 blocked, 2 usage; 3 stays the launcher's"
      - "a bare `loop-complete LOOP_COMPLETE` with neither verdicts nor a baseline is REFUSED, not accepted. Step 7 has already schema-validated that file, and with gates 2 and 3 both skipped the call would be a second schema check presented as a joined gate - present and inert, which is the failure mode this whole loop exists to remove"
      - "close the dispatch path in the same change: `ap_launcher` accepts any importable module under platforms.python and runs it with run_name='__main__', which is what made a CLI-less module report success. Give it an explicit allow-list, or make an absent __main__ a non-zero error rather than a silent normal return. A CLI added without this leaves the hole open for the next module, which is 008-1's point and the reason this check is here rather than in a test"
      - "red-green: each new assertion is proved able to fail by mutation, with the source restored byte-exact afterwards and a positive control showing the instrument is not simply broken"
    evidence: "The diff, the mutation log, the CLI output for all four cases including the clean pass, and a dispatch of a CLI-less module through the launcher showing it is now non-zero"
    gate: "none"
    outcome: "The gate can be invoked from a shell by any host, and cannot report a pass it did not establish"
    result: "Run 2026-09-02 by opencode/Qwen worker `gate-impl` in herdr worktree `loop-008-gate`, commits 794059b (CLI), 512a409 (launcher), f1cf589 and b9e00cd (defect fixes), 1ddda86 (regression tests), plus e7b04ed by the controller. Every check in this todo is met and was verified here rather than taken from the worker's report. Shape as 008-5 decided it: two subcommands, exit 0 advance / 1 blocked / 2 usage, 3 left to the launcher. Measured on the final tree - both verdict flags together exit 2 naming both flags; neither flag exits 2 with usage; `--baseline nosuchref_xyz` exits 1 with `BAD BASELINE: git diff failed with exit code 128` carrying git's own stderr; `--baseline HEAD` exits 1 with a distinct VACUOUS line; a real baseline exits 0 silently. The three modes an operator acts differently on stay tellable apart, and violating paths are printed rather than counted. Part B closed the dispatch path: against a fake runtime root, `scope_policy` and `minischema` went from exit 0 and silence at the base to exit 3 with a diagnostic, with an absent module and a real CLI as unchanged controls. FIVE production defects were found by controller verification and fixed - the mutually-exclusive verdict flags were an OR not a XOR; a failing `git diff` became an empty measurement indistinguishable from a legitimately empty one; Part B had deleted the ImportError handler, so a module whose OWN import fails broke the exit-code contract in the one case that handler existed for; the __main__ detection matched only a double-quoted string, so a single-quoted module would have been rejected as CLI-less; and `default_worker_scope` was called but never imported, making every loop-complete run that got past the VACUOUS early return raise NameError while the suite stayed green. That fifth one is the loop's own defect class caught in the loop's own code: nothing invoked the path, and the only mention of the name in the tests asserted it appears as a STRING in a markdown step. It was reachable only because defect 2 had been fixed - both earlier probes returned at VACUOUS and never reached the call, so the controller's instrument had been masking it. Red-green: all four regression tests proved able to fail by mutation, each run carrying TestPolicySelfReview as a positive control and restoring the source byte-exact with a sha256 comparison rather than by eye (evidence_gate.py 6f58914f, ap_launcher.py acb8b1c7, identical before and after every case). The harness asserts the expected number of pattern sites and refused to run when the count disagreed, which is what caught the verdict-flag guard existing at TWO call sites - a harness demanding exactly one would have reported `not pinned` wrongly. Two of the worker's four tests could not fail as written and were rebuilt in e7b04ed: one ended on a disjunction whose right-hand side had been established by the assertion on the line above, and one ran in a bare tmp_path, which is not a git repository, so BOTH git calls failed and the assertion was satisfied by the wrong branch - measured, mutating away the check it claimed to pin left it GREEN. Controller-run suite: 1076 passed, 1 skipped at 1ddda86 and again at e7b04ed. The worker reported 975 passed / 6 failed / 96 skipped from its own pane, which has no Git Bash; a worker's suite number is not comparable to the controller's and is not accepted in place of one. Evidence: .advanced-plans/evidence/2026-09-02-loop-008-2-cli-and-dispatch.md. Recorded and not fixed: test_evidence_gate.py:713 still asserts default_worker_scope as a string in a document rather than executing it, which is what let defect 5 survive; and both new launcher tests assert on `is not in the runtime`, which ap_launcher emits from two different branches, so the assertion cannot say which fired. Commits are unpushed on loop-008-gate - no push, tag, PR or merge."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-008-3"
    content: "Wire the gate into the shared router so the three non-Claude hosts run it, and EXECUTE the block rather than reading it"
    repository: "advanced-planning"
    base_sha: "loop-008-2"
    allowed_paths: ["platforms/shared/agent-skills/advanced-planning/", "platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4"
    checks:
      - "TWO sites, both found by 008-1. First, loop step 7 (SKILL.md 143-153), where the router already schema-validates loop-complete.json. Second, the external-dispatch block at SKILL.md 193-196, which validates collected evidence SCHEMA-ONLY - and that is the path this programme uses for its own Herdr workers, so leaving it is leaving the criterion failed where it is actually exercised"
      - "ORDER is load-bearing at both sites. In this router the WORKER writes loop-complete.json, so the gate cannot precede the write the way it would if the controller wrote it. It must run after the schema check and BEFORE the history_log advancement event at SKILL.md:152 - a gate that runs after the loop is logged as complete is decorative. State the order explicitly in the block rather than relying on where the lines happen to sit"
      - "EXECUTE the shipped block. Extract the command from the markdown that ships and run it in a throwaway project; do not retype it. loop-007-3 found a gate that had passed every reviewer because they had read it rather than run it, and its first real invocation would have raised FileNotFoundError"
      - "three scenarios, and the first is the positive control: an in-scope change PASSES, a write to a forbidden path FAILS naming the path, and an empty measurement FAILS as VACUOUS. Without the pass, a router that refused everything would score two out of three"
      - "every artefact the block reads must be one this adapter actually writes. 007-3's defect was a bare open() on a file nothing in the adapter produces, and the schema forbade it ever appearing"
    evidence: "The diff, the extracted command, and the three runs with their exit codes and messages"
    gate: "none"
    outcome: "Criterion 4 holds on the three hosts that route through the shared skill, not only on Claude Code"
    result: "Run 2026-09-03 by opencode/Qwen worker `gate-wire` in herdr worktree `loop-008-gate` (pane w2:p2E, opencode 1.18.26), commit 107d9b0, plus the controller correction f209e54. Every check verified here rather than taken from the worker's report. Site 2 the worker got right - correct positional arguments, both verdict forms shown with a line saying which applies, exit codes documented, gate before the advancement event at both sites, one clean commit touching only SKILL.md, correct trailers, and `.advanced-plans/` in the worktree untouched. Site 1 shipped `--baseline HEAD~1` with prose claiming it measures what the loop changed. It does not, and the interventional A/B is what settled it: same tree, same forbidden write to `.claude/settings.json`, only the baseline moving - rc=1 naming the path when the write happened to be the LAST commit, rc=0 and silence when one more commit followed it, rc=1 again against the commit the loop actually started from. Every loop in this programme makes more than one commit (008-2 made six), so the shipped gate would have inspected the last one and reported a pass it never earned. The fix had reintroduced the very defect class criterion 4 exists to close, and the worker's own commit message conceded `HEAD~1 used as proxy` while the shipped text asserted a measurement. Corrected in f209e54: D1 the baseline is now `<loop-base-ref>`, captured at step 6 by the block's own `git rev-parse HEAD` recipe before the worker is spawned, with an explicit line saying not to substitute `HEAD~1` and why; D2 `state_validate` restored ahead of the gate, which the worker had deleted rather than preceded - the gate does check schema but its CLI prints only a count, so diagnosability had regressed; D3 the shipped prose named `the Claude Code adapter` inside the SHARED router, which is the router for codex, cursor and opencode and explicitly not Claude Code; D4 the block now states the working directory, because the gate takes its allow-list from the process cwd via `default_worker_scope('.')` while git reports repository-relative paths - measured, the same in-scope change reads rc=0 from the project root and rc=1 from `src/` naming `src/app.py` as not_allowed. Site 2 left unchanged; its scope comes from the envelope rather than the cwd. CRLF preserved, 316 to 332, 0 bare LF throughout. Check 3 met by execution, not by reading: commands are extracted from the SKILL.md the installer shipped into a throwaway installed project (24 fenced blocks, 3 containing evidence_gate) and never retyped, in a project built for the purpose because the framework repo has no `.advanced-plans/bin/ap.py` at all. On the corrected block, 6 of 6 - VACUOUS with no commits since the baseline exits 1; the positive control exits 0; a forbidden path in the LAST commit exits 1 naming it; a forbidden path in the FIRST of two commits now also exits 1 naming it, where the old form returned 0 on the identical tree; and the restored schema check exits 0 on a valid document and 1 on an invalid one naming `/todos_done: Expected type 'integer', got 'string'`. That contrast line is what makes the correction load-bearing rather than cosmetic. Scenario (c) is only reachable at all now - under the hardcoded HEAD~1 a VACUOUS result was essentially unproducible, which is why the worker ran that scenario with `--baseline HEAD`, substituting a different baseline so the shipped block was not what executed. Each scenario runs on its own branch cut from the baseline, so no history is rewritten and the scenarios cannot contaminate one another; the runner checks its instrument before its subject and refuses to run if the shipped gate still hardcodes HEAD~1. The extractor's uniqueness guard fired once and was right to - two shipped blocks contain `state_validate loop-complete`, the second belonging to `resume`, and picking the wrong one would have tested a command the operator never runs at this site. Check 5 holds: every artefact the block reads is one this adapter writes, and the baseline is now produced by the block's own recipe rather than assumed. Controller-run suite from the worktree: 1094 passed, 1 skipped in 553.98s, exit status captured without a pipe. The worker reported 979 passed / 6 failed / 96 skipped from its own pane, which has no Git Bash; a worker's suite number is not comparable to the controller's. Evidence: .advanced-plans/evidence/2026-09-03-loop-008-3-shared-router-wiring.md. Recorded and not fixed, all in `platforms/python/evidence_gate.py` and outside this todo's allowed paths: the loop-complete path-scope arm is blind to staged and untracked changes despite a source comment claiming otherwise, and the VACUOUS guard tests the union, so committed work plus a staged forbidden write passes; the collected-evidence arm has no vacuity guard at all and the schema permits an empty changed_paths, so an envelope permitting nothing returned rc=0 while a single path returned rc=1 in the same run; the CLI swallows schema error text and prints only a count; and the gate silently depends on being run from the project root. Found during this verification and new: `resume` has a THIRD advancement path - finalize-without-rerunning validates both state files and runs no gate - which is the same moment criterion 4 is about, in the same router, and wants a decision rather than a quiet mid-loop edit. Commits are unpushed on loop-008-gate - no push, tag, PR or merge."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-008-4"
    content: "Make the silent-dispatch class impossible to reintroduce: a test derived from the shipped commands, not from a list"
    repository: "advanced-planning"
    base_sha: "loop-008-2"
    allowed_paths: ["platforms/python/tests/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4, and the defect class underneath it"
    checks:
      - "the module names are DERIVED by parsing the shipped command and skill files for ap.py invocations, never enumerated in the test. An enumerated list is a second copy of a list that can be forgotten, which is exactly how .agents/ was lost from the path audit for five days"
      - "the test asserts that every module a shipped file names has a __main__, so a module wired into a command but inert fails here"
      - "a vacuity guard on the number of invocations found. Zero parsed invocations must FAIL as VACUOUS rather than sweep - a regex that matches nothing otherwise reports a clean pass over nothing"
      - "mutation-proved by pointing a shipped file at a module with no __main__ and watching it go red, restored byte-exact"
      - "this lands BEFORE 008-3 rather than after, by operator decision on 2026-09-02, and the base_sha was moved from loop-008-3 to loop-008-2 to say so. That ordering is deliberate and not a shortcut: the test DERIVES its module list from the shipped files, so at the moment 008-3 adds the gate invocation the test starts covering it with no further edit. Landing the guard after the thing it guards would need someone to remember to come back, which is the failure mode this todo exists to remove. It also means the derived list will NOT contain evidence_gate when this todo runs - that is expected, and the vacuity guard is what keeps the test honest in the meantime"
    evidence: "The test, the parsed invocation list with its count, and the mutation log"
    gate: "none"
    outcome: "The next module wired into a shipped command cannot be silently inert"
    result: "Run 2026-09-03 by opencode/Qwen worker `gate-impl` in herdr worktree `loop-008-gate`, commit ff44883, corrected by the controller in ed38f33. All five checks met. The test derives its module list by regex over shipped files and never enumerates it, `evidence_gate` is correctly ABSENT because 008-3 has not run, and the worker did not add it by hand to look covered. The controller derived its own expectation BEFORE dispatch so the answer could be checked against something the worker did not supply: 26 invocations naming 4 modules (state_validate 14, history_log 7, install_audit 4, handoff_digest 1). Reproduced exactly. Three defects were found and fixed here. First, the walk read a FILENAME where it needed a directory - it opened SKILL.md directly and never reached references/, which ships three prompt files carrying four state_validate dispatches, and which all three installers copy as part of the whole skill directory. That gap is invisible in the totals: a walk reading only SKILL.md still finds 22 invocations and clears the floor while covering none of those files, so it now has its OWN test. Second, the vacuity floor measured a different quantity from the one its message named - find_ap_invocations returned a deduplicated SET, so the guard floored unique modules (4) while the failure text read `only found N ap.py invocations`; those differ by a factor of six here, so three quarters of the corpus could vanish with the count still clear. Third, the floor said three things at once: docstring FLOOR = 10 with `~15 unique modules` measured nowhere, comment 4, constant 3 - and 3 sits BELOW the 4 the walk found, so losing an entire module was tolerated on the day it was written. There is now one measured figure (26, dated) and one floor derived from it (22), interpolated into the message so the two cannot drift. Also split named-but-absent from present-but-inert, which has_main_block had collapsed, and added a NEGATIVE control: nothing in the original proved that function could ever return False, so every assertion in the file was satisfied by a detector returning True unconditionally. Red-green by five mutations, controller-run, each asserting the expected number of pattern sites first, restoring byte-exact with a sha256 comparison, and carrying a positive control in the same run: an inert module dispatched, an absent module dispatched, the corpus dropped below the floor, the walk stopped recursing, and the detector forced to always say yes - all five RED on the named test, control green, restored rc=0. The site-count guard earned itself again, refusing to run when SKILL.md turned out to hold 10 state_validate sites rather than the 11 a cross-file grep suggested. The mutation worth keeping is the rglob-to-glob one: under a non-recursive walk the main assertion stays GREEN at exactly 22, the floor, and only the references test goes red - a single combined test would have passed straight through the defect. One controller error corrected in the record rather than quietly dropped: the pre-dispatch expectation claimed FIVE roots and called a two-root answer the finding, on the strength of ap.py MENTIONS per directory. Reading the nine lines under platforms/codex, /cursor and /opencode shows every one is prose with no module following, so excluding those roots is right; next-phase.md calls the launcher's bootstrap helper and install.sh copies the launcher rather than using it. Counting mentions to predict dispatches is the same substitute-the-easy-measurement error this programme keeps finding in its own instruments. Controller-run suite at ed38f33: 1080 passed, 1 skipped in 437s - 1076 plus exactly the four tests added here. The worker reported 977 passed / 6 failed / 96 skipped from its own pane, correctly attributed the six to the absence of Git Bash there, and reported the line verbatim without interpreting it, which is what the brief asked for after 008-2. Evidence: .advanced-plans/evidence/2026-09-03-loop-008-4-derived-dispatch-guard.md. platforms/shared/ and platforms/claude-code/ are clean in git after the proof; commits are unpushed on loop-008-gate."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-008-8"
    content: "Close the five gate defects criterion 4 depends on: two silent passes, one unreadable failure, one cwd dependency, and a third advancement path that gates nothing"
    repository: "advanced-planning"
    base_sha: "loop-008-3"
    allowed_paths: ["platforms/python/evidence_gate.py", "platforms/python/tests/", "platforms/shared/agent-skills/advanced-planning/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4"
    checks:
      - "F1 - the loop-complete path-scope arm is blind to STAGED and UNTRACKED changes. evidence_gate.py:632 runs `git diff --name-only` with no --cached and no ref, which reads worktree-against-index only, while the comment directly above it claims `staged + unstaged`. Measured: the same forbidden file staged gives rc=0 and silence, committed gives rc=1 naming it. The VACUOUS guard does not cover the gap because it tests the UNION, so real committed work plus a staged forbidden write passes. `git diff --name-only HEAD` covers tracked staged and unstaged in one call, `git ls-files --others --exclude-standard` covers untracked. The proof must be the MIXED case - a genuine committed in-scope change alongside a staged forbidden write must FAIL naming the path. A test that stages a forbidden write on an otherwise empty tree passes for the wrong reason, because VACUOUS would have caught that one anyway"
      - "F2 - the collected-evidence arm has no vacuity guard at all, and this is the site the programme's own Herdr workers route through. `validate_advancement` Gate 3 (evidence_gate.py:245-262) takes changed_paths straight from the worker's own report and calls validate_path_scope, which returns ok=True on an empty list; the schema permits it, declaring changed_paths a required array of non-empty strings with no minItems. Measured with a positive control in the same run: an envelope allowing NOTHING and forbidding everything returned rc=0 on an empty list and rc=1 naming the path on a single entry. Mirror the guard its sibling already carries 200 lines above, gate-side rather than schema-side, and state in the commit why the schema was left alone rather than leaving the reader to guess"
      - "F3 - both arms collect schema_errors and print only the count. Measured: `schema: 1 validation error(s)` and nothing else, with the cause recoverable only by calling validate_document directly, which named it at once. An operator following the shipped block gets a failure they cannot act on. The proof is an invalid document whose stderr NAMES the offending pointer, not a test that merely asserts a non-zero exit"
      - "F4 - the gate takes its allow-list from the process cwd. evidence_gate.py:664 calls `default_worker_scope('.')`, which derives the allow-list from that directory's own top-level entries, while git returns repository-relative paths. Measured, same commit and same baseline: rc=0 from the project root, rc=1 from `src/` naming `src/app.py` as not_allowed - the same in-scope change. Resolve the repository root and pass that. The proof needs BOTH arms: the same in-scope change must give the same verdict from the root and from a subdirectory, AND a genuinely forbidden path must still fail from the subdirectory. Without that second arm the check is satisfied by a gate that has stopped refusing anything"
      - "F5 - the shared router has a THIRD advancement path and it gates nothing. Under `resume`, the branch `loop-complete.json matches loop-ready.json: Finalize without rerunning` runs state_validate on both files and stops. That is a finalize step, which is the exact moment criterion 4 is about. Decide it and say so in the block: either resume runs the evidence gate with an operator-supplied baseline, or it refuses to finalize and sends the operator to step 7. Do not leave a finalize step that gates nothing, and do not paper over the real difficulty - a resume after a crash may no longer know the baseline the loop started from - whichever way it goes, the block must say why"
      - "Red-green on every fix, by mutation and not by assertion. Each new test must be shown able to FAIL by mutating away the fix it pins, with the source restored byte-exact and compared by sha256 rather than by eye, and every run must carry a positive control so a detector that has started failing everything is distinguishable from one that is working. Four of the five defects above were found by exactly this discipline before any diff existed"
      - "Execute, do not read. Every before/after pair must be produced by running the shipped CLI in a throwaway installed project, because the framework repo has no `.advanced-plans/bin/ap.py` and any other route proves a path the operator does not use. Report the exit code and the stderr text for each, not a summary of them"
    evidence: "The diff, and for each of F1-F4 a before/after pair carrying the exit code and the stderr text, each with its positive control; the mutation result for every new test; the decision taken on F5 and the words it is stated in; and a controller-run suite"
    gate: "none"
    outcome: "The gate cannot report a pass it never earned, and no advancement path in the shared router is left ungated"
    result: "Run 2026-09-03 by opencode/Qwen worker `gate-fix` in herdr worktree `loop-008-gate`, commits 6497c87 (F1-F5) and 8cf17b5 (the residual), both unpushed. All seven checks met. Verified interventionally rather than by reading the diff: two throwaway INSTALLED projects built by git archive from f209e54 and from the fix, and one 13-scenario script byte-identical between runs whose pre|post argument changes only the expected column, never what executes. 12/13 after round one, 13/13 after round two. Every loop-complete scenario carries a real committed in-scope change and prints its committed set, so the VACUOUS guard cannot fire and be mistaken for the fix, and six of the thirteen rows are positive controls - a gate that had simply started refusing everything would fail seven and pass six. F1: the MIXED case, untracked and staged forbidden writes alongside committed in-scope work, went rc=0 and silent to rc=1 naming loop-ready.json and history.jsonl, with the one shape the old code did catch still failing. F2: an empty changed_paths against an envelope permitting nothing went rc=0 to rc=1, fixed gate-side in validate_advancement as asked with the schema left alone. F3: both arms went from a bare count to naming run_id and todos_done. F4: the same in-scope change now gives the same verdict from the project root and from src/. A SIXTH defect was found by the controller and is the finding of this loop: F1 and F4, each correct alone, combined into a gate blind to an untracked forbidden file whenever it ran from a subdirectory - precisely the case F4 existed to make safe - because git diff reports repository-relative paths whatever the cwd while git ls-files --others is scoped to the cwd subtree and prints relative to it. The pre-fix column reads rc=1 on that row and is NOT a pass: it named src/app.py (not_allowed), the F4 bug, while the forbidden file was invisible, so only a run that reads stderr rather than the exit code can tell the two apart. It was isolated rather than guessed - a COMMITTED forbidden write was still caught from src/ in the same post-fix run, which is what proves git diff is repo-wide and pins git ls-files as the cwd-dependent call. 8cf17b5 moves the git rev-parse --show-toplevel resolution above all three git subprocesses and runs each with cwd=repo_root, so no input the gate collects depends on where the operator stood; no os.chdir in the library. Mutation was done controller-side by REVERTING the whole production file rather than mutating one line: all six round-one tests fail on the f209e54 gate, and the round-two class run against 6497c87 fails its defect assertion while its positive control stays GREEN, which is the asymmetry a control exists to show. Round one had declined mutation, reporting it not performed because the tests were written green-first - but green-first says the test passes now, not that it would fail if the fix were removed, which is the only property that protects a fix from a future edit. The worker did perform its own narrower mutation in round two, reverting cwd=repo_root from the ls-files call with a matching sha256 pair either side of the restore. Two existing tests were edited to replace an empty changed_paths with a real path; both are legitimate consequences of F2 rather than weakenings, since neither test subject - schema load-bearingness, policy self-review - depends on the list being empty. F5 was decided the harder way: resume now REFUSES to finalize and sends the operator to run the gate with a supplied baseline, and the block says why - after a crash the step-6 baseline SHA is gone because it lived in the session and was never persisted, so running the gate is impossible and a guessed baseline would make it meaningless. One consequence carried forward: that branch no longer validates loop-ready.json at all. The verification harness caught its own contamination before it could produce a wrong verdict about the worker - git checkout -b drops neither untracked nor staged files, so with git add -A one scenario committed the previous scenario's forbidden file and would have reported a refusal for the wrong reason; fixed by committing only named paths, unlinking an enumerated scratch list, and asserting a clean tree at the start of each scenario, with no git clean and no git reset --hard anywhere. The 008-3 harness needed adapting because F5 added a second shipped block running the loop-complete gate: it now selects site 1 by STRUCTURE - the gate whose own state_validate sits within 12 lines above it, which the resume site does not have - rather than by position, prints the count so a third site would be visible rather than absorbed, and was confirmed discriminating on both installs before use; it then re-ran 6/6 unchanged in substance, with the invalid-document scenario now naming /todos_done rather than a bare count, which is F3 visible through the shipped operator path. Dispatch itself failed twice, silently, in this programme's own defect class, and is recorded because of that: a multi-paragraph brief was submitted only as far as its first blank line, so the worker answered a question nobody asked - Confirmed, all five defects are fixed - in 17.9s and settled done; the retry broke on PowerShell native-argument quoting and delivered nothing. Both returned agent_prompted and exit 0, and --wait returned instantly on the worker's pre-existing idle, so the controller was shown success for a prompt that was never delivered - a check whose subject is a string it supplied itself, which is exactly the defect this loop closed in the gate. Delivery was established instead from agent_status reaching working on a moved state_change_seq and from the TAIL of the prompt appearing on screen. Controller-run suite at 8cf17b5: 1102 passed, 1 skipped in 407.33s, exit 0, against 1080 passed 1 skipped at loop-008-4. Evidence: .advanced-plans/evidence/2026-09-03-loop-008-8-gate-defects-closed.md."
    status: completed
    complexity: medium
    priority: high
  - id: "loop-008-6"
    content: "Prove criterion 4 on a real non-Claude host, against the installed copy"
    repository: "advanced-planning (read-only for the host; the fixture lives outside both checkouts)"
    base_sha: "loop-008-4"
    allowed_paths: ["none - the fixture lives in the session scratchpad"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    discharges: "criterion 4, on a host rather than in a test"
    checks:
      - "opencode, because it is the only unattended runtime in the fleet and needs no trust dialog. One host is enough for this todo; the four-host question is 007-6 and is not reopened here"
      - "the host runs the INSTALLED copy, from a fixture install, not the source checkout. loop-004-4 established that the installer binds a project to its installing checkout, so a run against the repo proves nothing about a consuming project"
      - "the host must be made to FAIL the gate as well as pass it. A run that only passes cannot distinguish a working gate from an absent one"
      - "read the host's own datastore for the invocation manifest - model, session id, token counts - rather than accepting its summary. Its report of what it did is not evidence that it did it"
    evidence: "The fixture path, both runs with exit codes, and the invocation manifest read off disk"
    gate: "none"
    outcome: "Criterion 4 has a measured verdict on a host, which is what the criterion asks for"
    result: "Run 2026-09-03 on opencode 1.18.27 driving Qwen3.5 397B via the ELM proxy, herdr agent host-006, in a throwaway consuming project in the session scratchpad - outside both checkouts, as the loop requires. The fixture was INSTALLED rather than run in place: a git archive export of 8cf17b5 was used as the installing checkout and setup/opencode/install.sh --project put .agents/skills/ and .advanced-plans/bin/ap.py into the fixture, which matters because loop-004-4 established that the installer binds a project to its installing checkout, so a run against the repo would prove nothing about a consumer. Baseline dd05323, taken after the install was committed. Criterion 4 now has a measured PASS and a measured FAIL on a non-Claude host: the host executed the command read out of the INSTALLED SKILL.md with only the literal <loop-base-ref> placeholder substituted, and got exit 0 with empty stderr on a branch carrying one in-scope commit, and exit 1 naming .claude/settings.json (forbidden) on a branch carrying two commits with the forbidden write second - so the multi-commit baseline is exercised rather than assumed. The host's own report does NOT support the host's own conclusion, and that is worth more than the pass: it concluded the gate gives the same verdict from a subdirectory, which is true, but its subdirectory run was cd src issued in a shell already in src, so the cd failed with Set-Location: Cannot find path ...fixture-006/src/src and the command ran from the repository root. Its SUBDIR RUN is a second root run; the error is printed directly above the conclusion in its own transcript and it dismissed it as cosmetic, and it also silently rewrote the launcher path instead of running the shipped command as instructed. Second time in two loops that a worker reached a correct conclusion on evidence that does not reach it. The controller measured it properly in three runs reading the same shipped command out of the same installed SKILL.md: A, shipped verbatim from src/, exit 2 with python unable to open src/.advanced-plans/bin/ap.py; B, the same gate from src/ with launcher and document resolved to the repo root, exit 1 naming the forbidden path; C, the identical resolved form from the root, byte-identical to B. B equal to C is the proof the worker needed and lacked - the gate itself is cwd-independent, which is precisely the property 8cf17b5 added and the loop-008-8 round-two class pins. A is a different failure one layer up: the shipped command names the launcher by a repository-root-relative path, so from a subdirectory python dies before the gate is entered. That is loud rather than silent and therefore safe, but it is not what the shipped prose says. THE FINDING is that the F4 fix moved the reason out from under the documentation. SKILL.md step 7 does state the precondition - a first reading called it undocumented and that was wrong - but every clause of the reason it gives is now false: it says the allow-list is derived from the working directory's own top-level entries and that the same in-scope change reports as a violation one directory down, while default_worker_scope takes repo_root as a parameter, the F4 fix passes the resolved value, and run B shows the in-scope change is not flagged. The precondition outlived its own justification. The adjacent exit-code table is wrong the same way, saying exit 2 should not happen with the shipped command, which is exactly what run A is. Recorded, not fixed, alongside the stale module docstring found under loop-008-8. The invocation manifest was read off opencode's own datastore rather than accepted from the worker: ~/.local/share/opencode/opencode.db opened read-only, session row ses_f99b87b61ffeMX60gBwF7sb2GI, giving model Qwen/Qwen3.5-397B-A17B-FP8 on provider elm, version 1.18.27, agent build, 1350759 input and 2878 output tokens, cost 0.0, 25 messages, and a directory field naming the fixture - that last one is what makes against the installed copy a measured claim rather than a stated one. The version also corrects CLAUDE.md, which still records opencode 1.18.25. Fixture closed with a clean tree, run-pass at 1c96fbe and run-fail at 704546f, and git log --name-only confirms nothing under .agents/ or .advanced-plans/ was touched by any commit on either branch - the load-bearing half of the FORBIDDEN list, verified rather than trusted. Pane w2:p2G retired. Evidence: .advanced-plans/evidence/2026-09-03-loop-008-6-criterion-4-on-a-host.md."
    status: completed
    complexity: high
    priority: high

  ## Non-negotiables
  - The gap is callable-and-silently-green, not unwired. A fix that adds a CLI and leaves
    runpy dispatching arbitrary module names has closed the symptom and left the mechanism.
  - Execute the shipped block. Reading it is what let 007-3's defect through three reviewers.
  - Derive, do not enumerate. Every list in this loop that could drift is parsed from the
    artefact it describes, for the reason .agents/ went missing.
  - A VACUOUS result is a failure, never a pass. Established by loop-007-2 and inherited here.
  - Criteria 1 and 2 are NOT in scope. They are 007-6 and 007-7, gate: human, and still open.

  ## Success criteria
  - [x] dispatching the gate module through the launcher can no longer exit 0 having checked nothing
  - [ ] the shared router runs the gate as well as the schema validation, at BOTH sites, before the advancement is logged, proven by executing the shipped block in three scenarios
  - [ ] the three failure modes are distinguishable by exit code and message, with the violating paths printed
  - [x] a module named in a shipped command but lacking a __main__ fails a test derived from those commands
  - [ ] validate_advancement and can_advance_loop are each exposed or deleted, and the decisions are recorded in the module
  - [x] the gate reads the policy block of the evidence it is handed, proven by a schema-valid document that reports its own review as failed and is blocked
  - [x] criterion 4 has a measured pass AND a measured fail on one non-Claude host, on an installed copy
---
```

---

## Loop order and why

| Loop | Delivers | Why here |
|---|---|---|
| 001 | shared Python runtime reachable from an installed project | Every adapter shells out the same way; three more adapters over an unreachable runtime is one defect times three |
| 002 | task-envelope and collected-evidence schemas | Loops 004–006 all validate against them; they must exist first |
| 003 | host-neutrality enforced in `core/` | Cheap, and it must be armed *before* three adapters start adding host tokens, not after |
| 004 | Codex + OpenCode adapters | The two hosts with the strongest evidence base — opencode is the only unattended runtime in the fleet |
| 005 | Cursor adapter + the four-host discovery proof | Cursor is the most constrained host, so it goes last of the three; the four-host table needs all of them |
| 006 | ACC-08, evidence-gated advancement, v0.17.0 staged | Edits `core/` prompts, so it runs after the audit is armed and the schemas exist |
| 007 | gate remediation - the wiring, the controls, the host-discovery verdicts | Opened by the attempt-1 gate returning fail; every todo names the criterion it discharges |
| 008 | criterion 4 - the evidence gate made reachable, and unable to pass silently | Opened by the attempt-2 gate. The gate is not merely unwired on the three non-Claude hosts: dispatched through the launcher it returns normally where `state_validate` raises `SystemExit(2)`, so it is callable and silently green |

## Exit criteria for the phase gate

Taken verbatim from `plan.md`, with the loop that discharges each:

| Criterion | Discharged by |
|---|---|
| Every target host discovers the same named core planning skills | loop-005-4, **loop-007-6** |
| A fixture programme creates one phase, one loop and one external task on every host | loop-004-4, loop-005-3, **loop-007-7** |
| Only the control checkout updates programme state — ACC-08 | loop-006-1, loop-006-2, **loop-007-1, loop-007-2** |
| Collected evidence advances a loop only after schema and gate validation | loop-006-3, loop-007-3, **loop-008-1 .. loop-008-6** |
| The CI path audit fails on any host-specific path in `core/` | loop-003-2, loop-003-4, **loop-007-4** |
| No adapter duplicates a core skill's content | loop-004-2, loop-004-3, loop-005-2, loop-005-4 |

**Attempt 1 of this gate returned fail on 2026-09-02**, on five of these six criteria. The
bolded loop-007 todos are what was added in response; the unbolded ones are the work already
done, which the gate did not find wrong. Only criterion 6, no adapter duplicating a core
skill, passed unanimously and needed nothing.

**Attempt 2 returned fail on 2026-09-02**, on three. The operator resolved two of them the
same day. Criterion 3 was ruled **met** on the declared carve-out: `loop-complete.json` is
writable by the worker by design, the divergence is recorded in the loop-007 evidence and
carried as a Phase 7 finding, and a criterion cannot be failed for a deviation the phase
declared. Criterion 5 was **fixed inside loop 007** rather than deferred - `.agents/` was
absent from the host-neutrality regex, and adding it moved the audit from 20 suppressed
matches to 24, with two new tests each proven able to fail by mutation. That left criterion
4, which is why loop 008 exists, and criteria 1 and 2, which are the human-gated todos
007-6 and 007-7 and are not in loop 008's scope.

The state after those rulings is **three met, three failed**: 3, 5 and 6 met; 1, 2 and 4
open. Criterion 5's failure is the one worth naming, because two of the three reviewers
marked it met. They checked that the audit's **roots** had been widened and did not check
its **tokens**, and widening a check's roots does not widen what it looks for. A majority
vote would have passed a criterion a one-line mutation shows was not met.

Not a plan criterion but a phase-6 finding in its own right: the shared Python runtime is
unreachable from any installed project (loop-001). It is not in the plan's deliverable table
because the defect was found on 2026-08-27, after the plan was written. It is carried as loop 001
rather than deferred, because every other loop in this phase invokes that runtime.
