# Phase 3 — Ralph Loops

Source phase plan: `.advanced-plans/phases/phase-3/plan.md`
Design spec: `.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md` §14 Workstream 0
Baseline: `.advanced-plans/evidence/2026-08-26-baseline-audit.md`

**Todo schema (v0.2).** Every todo carries `repository`, `base_sha`, `allowed_paths`,
`forbidden_paths`, `provider`, `worktree_owner`, `checks`, `evidence`, and `gate`.
`gate: human` means the todo is a decision or an external write that an agent may prepare and
present but **may not self-approve**.

**Standard programme forbidden set.** Forbidden for every worker todo in this programme, without
exception: `.advanced-plans/state/`, `.advanced-plans/PLANNING.md`,
`.advanced-plans/PLANS-INDEX.md`, `.advanced-plans/phases/*/complete.md`,
`.advanced-plans/gate-verdicts/`, `.advanced-plans/evidence/`. Only the controller checkout
writes those.

---

```yaml
---
name: "ralph-loop-001"
task_name: "Environment pin — HOME fix, doctor assertion, Cursor decision"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-001-1"
    content: "Record the HOME fix decision (scoped launcher vs machine-wide) as a written decision entry, with the option chosen and the reason"
    repository: "Advanced-AI-Workflows"
    base_sha: "HEAD of phase/v0.2-baseline"
    allowed_paths: [".advanced-plans/evidence/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks: []
    evidence: "Decision recorded with the option chosen and the reason; baseline audit section 7.5 cited"
    gate: "human"
    outcome: "The HOME fix approach is chosen in writing before any implementation"
    status: pending
    complexity: low
    priority: high
  - id: "loop-001-2"
    content: "Implement the chosen HOME fix as tools/herdr-env.ps1 — a launcher that pins HOME/HOMEDRIVE/HOMEPATH from USERPROFILE and then runs herdr with the caller arguments"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-001-1"
    allowed_paths: ["tools/", "docs/herdr-windows-operations.md"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "tools/herdr-env.ps1 integration status  -> expect four current, zero M: paths"
      - "same command from a shell where HOME was deliberately set to M:\\  -> must still be correct"
    evidence: "Both check outputs pasted verbatim into the pilot report"
    gate: "none"
    outcome: "herdr integration status reports current for every target runtime even when the ambient HOME is M:\\"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-001-3"
    content: "Copy the five orphan items from M:\\ to the real profile (.pnpm-store, .Rprofile, .Rhistory, .profile, .viminfo) — copy, never move; leave M:\\ untouched"
    repository: "n/a (user profile)"
    base_sha: "n/a"
    allowed_paths: ["the five named items under the real profile only"]
    forbidden_paths: ["M:\\ is read-only in this todo", "<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "per-item comparison of source and destination; source still present on M:\\"
    evidence: "Per-item before/after listing with sizes"
    gate: "none"
    outcome: "Nothing on M:\\ is lost when HOME stops pointing there, and M:\\ itself is unmodified"
    status: pending
    complexity: low
    priority: medium
  - id: "loop-001-4"
    content: "Close the Cursor runtime question: either install cursor-agent and record its version, or amend the design to a three-runtime target set and update every document naming four runtimes"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-001-2"
    allowed_paths: [".advanced-plans/evidence/", "README.md", "ROADMAP.md", "SETUP.md", "ARCHITECTURE.md", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "cursor-agent --version, if the install option is chosen"
      - "grep for four runtimes / all four hosts across README, ROADMAP, SETUP, ARCHITECTURE, docs -> must agree with the decision"
    evidence: "Either a version string, or a diff showing the runtime count changed consistently everywhere"
    gate: "human"
    outcome: "The v0.2 target runtime set is a fact rather than an assumption, and the documents agree with it"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Objective
  Make the environment honest before anything depends on it. Two open questions block the
  programme: which HOME fix to apply, and whether Cursor is a v0.2 target runtime.

  ## Read first
  - .advanced-plans/evidence/2026-08-26-baseline-audit.md sections 1.1, 1.2, 1.3, 5, and 7

  ## Success criteria
  - [ ] HOME fix decision recorded in writing with its reason
  - [ ] tools/herdr-env.ps1 makes integration status correct even from a shell where HOME is M:\
  - [ ] The five orphan items exist on the real profile and still exist on M:\
  - [ ] The Cursor question is closed and every document agrees with the answer

  ## Forbidden
  Do not write the standard programme forbidden set. Do not modify anything on M:\. Do not
  change machine-wide environment variables unless loop-001-1 explicitly chose that option.
---
```

```yaml
---
name: "ralph-loop-002"
task_name: "Disposable Herdr pilot (kickoff Step 4, ten steps)"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Create the disposable branch pilot/herdr-smoke from AAW HEAD and a Herdr worktree for it at a path containing a space"
    repository: "Advanced-AI-Workflows"
    base_sha: "HEAD of phase/v0.2-baseline"
    allowed_paths: ["the disposable worktree only"]
    forbidden_paths: ["main", "<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "herdr worktree list -> the new worktree appears with its absolute path"
      - "git status in the worktree -> clean"
    evidence: "Herdr workspace ID, agent name, absolute worktree path, branch, base SHA"
    gate: "none"
    outcome: "A throwaway worktree exists on a path containing a space, owned by Herdr, on a branch nothing depends on"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-2"
    content: "Start one non-controller provider in the worktree, issue a read-only prompt, and record the state transitions Herdr reports"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-1"
    allowed_paths: ["the disposable worktree, read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "codex or opencode — NOT claude, which is the controller"
    worktree_owner: "herdr"
    checks:
      - "herdr agent list sampled before, during, and after the prompt"
    evidence: "Timestamped state samples showing working then idle/done, taken from Herdr output and not from agent prose"
    gate: "none"
    outcome: "The working to idle/done transition is observed and evidenced, or its absence is recorded as an exit-gate failure"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-3"
    content: "Provoke a harmless blocked question on a provider that supports it, and record whether Herdr surfaces blocked and preserves the question text"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-2"
    allowed_paths: ["the disposable worktree, read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "herdr agent list -> expect blocked"
    evidence: "The blocked state and the preserved question text, or an explicit note of which providers cannot produce it and why"
    gate: "none"
    outcome: "The ACC-09 mechanism is understood before the programme relies on it"
    status: pending
    complexity: medium
    priority: medium
  - id: "loop-002-4"
    content: "Make one trivial allowed edit in the disposable worktree, commit it, and collect Git evidence from the controller independently of what the agent said"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-3"
    allowed_paths: ["one throwaway file in the disposable worktree"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "git log -1 in the worktree"
      - "git diff --stat base..HEAD in the worktree"
      - "git status --porcelain in the worktree -> clean after commit"
    evidence: "Base and head full SHAs, changed-path list, diff stat, and cleanliness — all re-run by the controller"
    gate: "none"
    outcome: "The controller can verify a worker result without trusting the worker report"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-5"
    content: "Have a different provider review the trivial edit and record its verdict, proving the cross-model review mechanism works before it becomes the gate"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-4"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "a provider different from the loop-002-4 implementer"
    worktree_owner: "herdr"
    checks:
      - "the reviewing provider and the implementing provider are named and differ"
    evidence: "Reviewer verdict text with the reviewer model and provider recorded — ACC-18"
    gate: "none"
    outcome: "The cross-model gate that replaced Plannotator is demonstrated on real output"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-6"
    content: "Detach from the named Herdr session and reattach; confirm the pane and the agent survived"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-5"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "herdr session list, detach, herdr session attach, herdr agent list"
    evidence: "Agent identity and state before and after, showing continuity — ACC-10"
    gate: "none"
    outcome: "Session restore is proven rather than assumed"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-7"
    content: "Remove the clean disposable worktree WITHOUT --force, then delete the disposable branch"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-6"
    allowed_paths: ["the disposable worktree and branch only"]
    forbidden_paths: ["main", "any real branch", "<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "herdr worktree remove with no --force; if it refuses, STOP and report"
      - "git worktree list -> gone"
    evidence: "Exact command and exit code. If --force proved necessary, that is an exit-gate FAILURE and must be reported as one"
    gate: "none"
    outcome: "The ACC-17 safety property holds, or the phase stops here"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-8"
    content: "Write the pilot report into the controller evidence area"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-7"
    allowed_paths: [".advanced-plans/evidence/"]
    forbidden_paths: ["<standard programme forbidden set, except evidence/ which the controller owns>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "every one of the ten kickoff Step 4 items appears with a result or an explicit not-applicable"
    evidence: "The report itself"
    gate: "none"
    outcome: "A written verdict on whether Herdr is fit to be the execution layer"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Find out what Herdr agent states actually mean, on this machine, before the programme depends
  on them. This is an investigation, not a build. A negative result is a valid and valuable
  outcome.

  ## Hard rules
  - idle, done, and terminal silence are NOT completion evidence. Verify with git, from the
    controller, every time.
  - Never pass --force to a worktree removal. If removal refuses, that refusal is the finding.
  - The disposable branch must never be merged and must never be pushed.

  ## Success criteria
  - [ ] working to idle/done observed from Herdr output
  - [ ] blocked observed, or its unavailability recorded per provider
  - [ ] a trivial edit made, committed, and independently verified by the controller
  - [ ] a different provider reviewed it and its verdict is recorded with the model named
  - [ ] detach and reattach preserved the session
  - [ ] the clean worktree was removed without --force
  - [ ] the pilot report covers all ten Step 4 items
---
```

```yaml
---
name: "ralph-loop-003"
task_name: "Programme Git policy and worktree ownership policy"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-003-1"
    content: "Write docs/programme-git-policy.md — branch naming per repository, backup-tag naming, the exact check command for each repository, and the statement that push, PR, merge, and tag-push are human gates"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-8"
    allowed_paths: ["docs/programme-git-policy.md", "README.md", "ROADMAP.md"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "every branch name used later in phases 4 and 5 appears in this document first"
    evidence: "The document, linked from the ROADMAP operating guides list"
    gate: "none"
    outcome: "Branch and tag names are decided once, in writing, rather than improvised per worktree"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-2"
    content: "Write docs/worktree-ownership.md — one owner per checkout, the owner values (herdr, claude, cursor, aaw, none), the no-nesting rule, and the controller-sole-writer rule with the exact forbidden path list"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-003-1"
    allowed_paths: ["docs/worktree-ownership.md", "ROADMAP.md"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "the forbidden path list here is byte-identical to the one in every loops.md header"
    evidence: "The document"
    gate: "none"
    outcome: "ACC-07 and ACC-08 have a written contract to be tested against in Phase 8"
    status: pending
    complexity: low
    priority: high
  - id: "loop-003-3"
    content: "Update the CHANGELOG Unreleased section with the Phase 3 outcomes and record the phase-3 exit-gate result"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-003-2"
    allowed_paths: ["CHANGELOG.md"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "the CHANGELOG entry names the pilot report and both policy documents"
    evidence: "Changelog diff"
    gate: "none"
    outcome: "The release record stays current as the programme runs rather than being reconstructed at the end"
    status: pending
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Turn what the pilot proved into written policy, so phases 4 and 5 execute against a contract
  rather than against a memory of this session.

  ## Success criteria
  - [ ] docs/programme-git-policy.md exists and names every branch and tag phases 4 and 5 will use
  - [ ] docs/worktree-ownership.md exists with the forbidden-path list matching the loops.md header
  - [ ] CHANGELOG Unreleased records phase 3
---
```
