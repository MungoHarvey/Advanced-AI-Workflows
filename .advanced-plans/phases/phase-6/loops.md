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
    status: in_progress
    result: "OPTIONS DRAFTED 2026-08-27, DECISION OPEN. Four mechanisms costed against five axes in evidence/2026-08-27-shared-python-runtime.md. Controller recommends (c) resolve a recorded source path, with (d) detect-and-degrade as a non-optional guard under whichever is chosen. Against (a) copy-into-install-tree: it puts an Nth copy of executable code in every project, and install_audit - the machinery that would police it - compares by mtime, a limitation already on the carried-items list. Against (b) console-script shim: the only option that adds a packaging system and mutates PATH. For (c): zero duplication, no new subsystem, and the only one already demonstrated to work here. AWAITING the human gate; loop-004-1 writes its adapter specification against whatever is chosen."
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
    complexity: low
    priority: high
  - id: "loop-003-2"
    content: "Add a core/-scoped host-neutrality rule covering host directories, host-only tool names and host permission syntax"
    repository: "advanced-planning"
    base_sha: "loop-003-1"
    allowed_paths: ["platforms/python/path_audit.py", "docs/path-conventions.md"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "host directories flagged under core/: .claude/, .cursor/, .opencode/, .codex/, .agents/, .gemini/"
      - "host-only tool and agent names flagged under core/: the Claude Agent/Task tool, subagent_type, and slash-command syntax only one host has"
      - "host permission syntax flagged under core/: settings.json permission rules, opencode.json, .cursor/rules"
      - "the rule fires ONLY under core/ — platforms/claude-code/ must still be allowed to say .claude/, which is the entire point of an adapter"
      - "docs/path-conventions.md is the stated source of truth for canonical paths and gains the new rule"
    evidence: "The diff and the rule list"
    gate: "none"
    outcome: "The success criterion — the CI path audit fails on any host-specific path in core/ — has an implementation"
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
task_name: "Codex and OpenCode adapters — the five contracts, each proven on its own host, neither forking a core skill"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-004-1"
    content: "Write the adapter specification for both hosts before either is built: for Codex and for OpenCode, fill in all five contracts from docs/adapting-to-new-platforms.md and the four extra requirements in design §7.3"
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
      - "§7.3 additions: discovery, invocation, delegation, state I/O, and the human gate. §7.4 gives the per-host Plannotator fallback text; Plannotator is DEPRECATED in AAW, so state the host-neutral manual review command instead and do not carry the Plannotator wording forward"
    evidence: "One specification document covering both adapters, contract by contract, with the codex commit constraint called out"
    gate: "none"
    outcome: "Two adapters are specified against the published contract before code exists, so neither is reverse-engineered from the Claude Code one"
    status: pending
    complexity: high
    priority: high
  - id: "loop-004-2"
    content: "Build the Codex adapter: platforms/codex/ and setup/codex/, installing and registering the core skills without forking any of them"
    repository: "advanced-planning"
    base_sha: "loop-004-1"
    allowed_paths: ["platforms/codex/", "setup/codex/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "core/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "core/ is in the forbidden set for this todo on purpose: an adapter that needs to change a core skill has found a core defect, which is reported and fixed as its own todo, not absorbed"
      - "no file under platforms/codex/ duplicates the CONTENT of a core skill — prove it by hashing every installed skill against its core original and showing they are the same file or the same digest"
      - "the adapter installs skills to .agents/skills/<name>/SKILL.md and guidance to the AGENTS.md fenced block, per §7.2"
      - "an adapter README exists covering setup, quick start, and the top three failure modes — the checklist in docs/adapting-to-new-platforms.md requires it"
      - "path_audit still exits 0, and the new host tokens under platforms/codex/ are correctly NOT flagged"
    evidence: "The tree, the install run, and the hash comparison proving no core skill was forked"
    gate: "none"
    outcome: "Codex installs and registers the same named core skills Claude Code does"
    status: pending
    complexity: high
    priority: high
  - id: "loop-004-3"
    content: "Build the OpenCode adapter: platforms/opencode/ and setup/opencode/, on the same terms"
    repository: "advanced-planning"
    base_sha: "loop-004-2"
    allowed_paths: ["platforms/opencode/", "setup/opencode/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "core/", "setup-antigravity.js"]
    provider: "opencode"
    worktree_owner: "herdr"
    checks:
      - "same no-fork hash proof as loop-004-2"
      - "skills to .agents/skills/, guidance to the AGENTS.md fenced block; opencode.json is touched ONLY for plugins, permissions or extra instructions, per §7.2"
      - "adapter README with the top three failure modes"
      - "path_audit exits 0"
    evidence: "The tree, the install run, and the hash comparison"
    gate: "none"
    outcome: "OpenCode installs and registers the same named core skills"
    status: pending
    complexity: high
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
      - "the envelope is validated by the loop-002-4 validator, not by eye"
      - "idle, done and terminal silence are not completion evidence — read the produced files and check them"
      - "record the invocation and model for each run, the way tests/adherence/MANIFEST.json does, so a re-run is reproducible"
    evidence: "The two fixture runs with their produced artefacts, the validator output, and the invocation manifest"
    gate: "none"
    outcome: "Neither adapter ships unexercised — the risk register names 'an adapter is written but never exercised on its host' as high impact, and this is its mitigation"
    status: pending
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
    evidence: "The verdict at .advanced-plans/gate-verdicts/phase-6-loop-004-<provider>.json and the controller's resolution or waiver of each finding"
    gate: "human"
    outcome: "Two of the four hosts are independently verified before the third is built on the same pattern"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Add the Codex and OpenCode adapters beside the Claude Code and Cowork ones, per the five
  contracts in `docs/adapting-to-new-platforms.md` and the five requirements in design §7.3.
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    status: pending
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
    checks:
      - "python -m pytest platforms/python/tests/ -v — green, with the new tests visible in the count"
      - "python -m platforms.python.path_audit — exit 0"
      - "python -m platforms.python.install_audit --layers source,project — exit 0. NOTE the recorded limitation that this audit compares by mtime; if a drift it should have caught is invisible, that is a finding for the compatibility-manifest work, not something to wave through"
      - "python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/ — still dependency-free"
      - "CI job 2's inline python over the schema directories — passes"
      - "git status clean apart from the two named untracked files"
    evidence: "Every command with its exit code and output"
    gate: "none"
    outcome: "The phase's own suites are green before the gate is asked to judge it, and by a provider that implemented none of it"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-006-5"
    content: "Stage the v0.17.0 release locally: VERSION, CHANGELOG, and the release checklist. Do not publish"
    repository: "advanced-planning"
    base_sha: "loop-006-4"
    allowed_paths: ["VERSION", "CHANGELOG.md", "docs/release-checklist.md"]
    forbidden_paths: ["<standard programme forbidden set>", "advanced-planning/.advanced-plans/", "setup-antigravity.js"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout drives; the commit is made in advanced-planning)"
    checks:
      - "VERSION 0.16.0 -> 0.17.0"
      - "CHANGELOG names all three new adapters, both schemas, the host-neutrality rule and the shared-runtime fix, with the loop each came from"
      - "docs/release-checklist.md is FOLLOWED, and each item is recorded as done or explicitly not applicable"
      - "NO tag is pushed, NO release is created, NO PR is opened. The programme's external-write rule stands and covers this repository too"
      - "the controller appends a release_staged event to history.jsonl with event, phase and version, per the programme's release-staging convention"
    evidence: "The diff, the completed checklist, and the history event"
    gate: "human"
    outcome: "v0.17.0 is ready to publish on one command, and publishing it remains the user's decision"
    status: pending
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

## Loop order and why

| Loop | Delivers | Why here |
|---|---|---|
| 001 | shared Python runtime reachable from an installed project | Every adapter shells out the same way; three more adapters over an unreachable runtime is one defect times three |
| 002 | task-envelope and collected-evidence schemas | Loops 004–006 all validate against them; they must exist first |
| 003 | host-neutrality enforced in `core/` | Cheap, and it must be armed *before* three adapters start adding host tokens, not after |
| 004 | Codex + OpenCode adapters | The two hosts with the strongest evidence base — opencode is the only unattended runtime in the fleet |
| 005 | Cursor adapter + the four-host discovery proof | Cursor is the most constrained host, so it goes last of the three; the four-host table needs all of them |
| 006 | ACC-08, evidence-gated advancement, v0.17.0 staged | Edits `core/` prompts, so it runs after the audit is armed and the schemas exist |

## Exit criteria for the phase gate

Taken verbatim from `plan.md`, with the loop that discharges each:

| Criterion | Discharged by |
|---|---|
| Every target host discovers the same named core planning skills | loop-005-4 |
| A fixture programme creates one phase, one loop and one external task on every host | loop-004-4, loop-005-3 |
| Only the control checkout updates programme state — ACC-08 | loop-006-1, loop-006-2 |
| Collected evidence advances a loop only after schema and gate validation | loop-006-3 |
| The CI path audit fails on any host-specific path in `core/` | loop-003-2, loop-003-4 |
| No adapter duplicates a core skill's content | loop-004-2, loop-004-3, loop-005-2, loop-005-4 |

Not a plan criterion but a phase-6 finding in its own right: the shared Python runtime is
unreachable from any installed project (loop-001). It is not in the plan's deliverable table
because the defect was found on 2026-08-27, after the plan was written. It is carried as loop 001
rather than deferred, because every other loop in this phase invokes that runtime.
