# Phase 5 — Ralph Loops

Source phase plan: `.advanced-plans/phases/phase-5/plan.md`
Design spec: §14 Workstream 1A (Superpowers), §13.3
Baseline: `.advanced-plans/evidence/2026-08-26-baseline-audit.md` §2.4, §2.4.1

**Standard programme forbidden set.** Forbidden for every worker todo in this programme, without
exception: `.advanced-plans/state/`, `.advanced-plans/PLANNING.md`,
`.advanced-plans/PLANS-INDEX.md`, `.advanced-plans/phases/*/complete.md`,
`.advanced-plans/gate-verdicts/`, `.advanced-plans/evidence/`. Only the controller checkout
writes those.

---

```yaml
---
name: "ralph-loop-001"
task_name: "Superpowers behaviour matrix — write it and get it reviewed before touching anything"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-001-1"
    content: "Re-derive the fork net patch from the merge base and confirm it is still exactly the two named skill files"
    repository: "superpowers (C:\\Users\\mharvey2\\Coding\\superpowers)"
    base_sha: "origin/main fde9f972a2a49fcaa116f53d59444f002589c34a; upstream/main b36e0829c6d0140e93cfef2ca599b1b07d4a7797; merge-base f2cbfbefebbfef77321e4c9abc9e949826bea9d7"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git diff --stat <merge-base> origin/main -> expect skills/brainstorming/SKILL.md and skills/using-superpowers/SKILL.md only"
      - "git rev-list --left-right --count upstream/main...origin/main -> baseline says 241 and 4"
    evidence: "Fresh SHAs, divergence, and the net-patch path list, with any delta from the baseline called out"
    gate: "none"
    outcome: "The matrix describes the patch as it is now, not as it was three weeks ago"
    status: completed
    complexity: low
    priority: high
  - id: "loop-001-2"
    content: "Document each of the four intents (SP-1 to SP-4): what it does, where it lives, what detection it uses, and an explicit port or do-not-port verdict with the reason"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-001-1"
    allowed_paths: [".advanced-plans/evidence/"]
    forbidden_paths: ["<standard programme forbidden set, except evidence/ which the controller owns>"]
    provider: "controller"
    worktree_owner: "aaw (controller checkout)"
    checks:
      - "all four intents present with a verdict each"
      - "each do-not-port verdict states where that behaviour goes instead"
    evidence: "The behaviour matrix document"
    gate: "none"
    outcome: "The port has a specification, so nobody has to infer intent from a diff mid-implementation"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-3"
    content: "Record what current upstream does that the merge-base version did not, especially the Three Paths router, so the port knows what it must not break"
    repository: "superpowers"
    base_sha: "loop-001-2"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "git diff <merge-base> upstream/main -- skills/brainstorming/SKILL.md -> read it, do not skim it"
      - "grep upstream skills/ for advanced-planning and plannotator -> expect zero hits"
    evidence: "A summary of what upstream changed in the two patched files, with the router section quoted"
    gate: "none"
    outcome: "The reason a file copy would be destructive is written down, with the evidence attached"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-4"
    content: "Have a provider different from the matrix author review the matrix before implementation is allowed to start"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-001-3"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "a provider different from the matrix author"
    worktree_owner: "herdr"
    checks:
      - "the reviewing and authoring providers are named and differ — ACC-18"
    evidence: "Verdict, findings, reviewer model, and the human resolution or waiver of each finding"
    gate: "human"
    outcome: "The design gate the spec requires before the port begins is actually observed"
    status: completed
    complexity: medium
    priority: high

prompt: |
  ## Objective
  Write down what the Superpowers fork patch MEANS before anyone tries to move it. The design is
  explicit that implementation may not start until this matrix is written and reviewed.

  ## Read first
  - baseline audit section 2.4 and 2.4.1
  - design spec section 13.3

  ## Why this loop exists
  The fork patch is two files. Upstream has since rewritten both, adding a Three Paths router
  that did not exist at the merge base. Copying the fork files forward would silently delete it.
  The matrix is what stops that happening.

  ## Success criteria
  - [ ] net patch re-derived from the merge base and confirmed
  - [ ] all four intents documented with a port / do-not-port verdict and a reason
  - [ ] what upstream changed underneath the patch is recorded, router section quoted
  - [ ] a different provider reviewed the matrix and its findings are closed

  ## Forbidden
  Do not create the port branch in this loop. Do not edit any Superpowers file.
---
```

```yaml
---
name: "ralph-loop-002"
task_name: "Reimplement the integration intent as AAW-owned routing"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Create port/aaw-routing-<date> from current upstream/main in a Herdr worktree, and tag the pre-port fork head as a backup"
    repository: "superpowers"
    base_sha: "upstream/main, re-fetched"
    allowed_paths: ["the port worktree only"]
    forbidden_paths: ["origin/main", "<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git log -1 on the new branch matches upstream/main exactly — prove the branch point"
      - "git tag -n99 on the backup tag shows the pre-port fork head fde9f97..."
    evidence: "Branch name, head SHA, backup tag, worktree absolute path"
    gate: "none"
    outcome: "The port starts from current upstream, and the old fork state is recoverable"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-2"
    content: "Implement SP-1 and SP-2 as AAW-owned routing that reads the Phase 4 installation manifest, with no .claude/ path probe anywhere"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-1; depends on phase-4 loop-003 manifest"
    allowed_paths: [".claude/skills/", ".agents/skills/", "references/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "grep for .claude/ in the ported routing logic -> expect zero host-specific probes"
      - "the routing reads the installation manifest, not a directory existence test"
    evidence: "The routing source and the grep output"
    gate: "none"
    outcome: "The integration behaviour lives in AAW and works on any host, rather than in a Claude-only fork patch"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-3"
    content: "Port the Advanced Planning half of SP-4 (companion-tools recommendation) and confirm the Plannotator half is absent"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-2"
    allowed_paths: [".claude/skills/", ".agents/skills/", "references/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "the companion recommendation names Advanced Planning"
      - "grep for plannotator in the ported routing -> zero hits"
    evidence: "The recommendation text and both grep results"
    gate: "none"
    outcome: "The useful half of SP-4 survives the deprecation and the deprecated half does not come back"
    status: pending
    complexity: low
    priority: medium
  - id: "loop-002-4"
    content: "Prove the behaviour with Advanced Planning present: an approved design lands in .advanced-plans/specs/ and the terminal state routes to phase planning"
    repository: "a temporary fixture project"
    base_sha: "loop-002-3"
    allowed_paths: ["the fixture project"]
    forbidden_paths: ["the live profile", "<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "run the flow end to end; assert the output landed in .advanced-plans/specs/ — ACC-04"
      - "assert the terminal state invoked phase planning"
    evidence: "The fixture transcript and the resulting file paths"
    gate: "none"
    outcome: "SP-1 and SP-2 are proven by behaviour rather than by file inspection"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-5"
    content: "Prove the behaviour with Advanced Planning ABSENT: the upstream default path is used and no AAW path is fabricated"
    repository: "a second temporary fixture project, without Advanced Planning"
    base_sha: "loop-002-4"
    allowed_paths: ["the fixture project"]
    forbidden_paths: ["the live profile", "<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "run the same flow; assert the output landed in the upstream default location — ACC-05"
      - "grep the whole output for .advanced-plans -> zero hits"
    evidence: "The fixture transcript, the resulting paths, and the grep output"
    gate: "none"
    outcome: "ACC-05 passes — the failure mode where AAW invents a path that does not exist is excluded"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-6"
    content: "Prove the current upstream Three Paths router is intact on the port branch by diffing the section, not by asserting it"
    repository: "superpowers (port worktree)"
    base_sha: "loop-002-5"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git diff upstream/main..port/aaw-routing-<date> -- skills/brainstorming/SKILL.md -> the router section is unchanged, or every change to it is justified in writing"
    evidence: "The diff, with the router section shown"
    gate: "none"
    outcome: "The exact regression this phase exists to prevent is checked for, not hoped against"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-7"
    content: "Have a provider different from the implementer review the port, and record whether the fork ended as a mirror or retains a justified patch"
    repository: "superpowers + Advanced-AI-Workflows"
    base_sha: "loop-002-6"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "a provider different from the implementer"
    worktree_owner: "herdr"
    checks:
      - "the reviewing and implementing providers are named and differ — ACC-18"
      - "if a fork patch remains, it is host-neutral, minimal, and against current upstream"
    evidence: "Verdict, findings, reviewer model, the human resolution or waiver of each finding, and the mirror-or-patch outcome"
    gate: "human"
    outcome: "The higher-risk lane carries an independent verdict and an explicit statement of what the fork now is"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  The behaviour matrix is the specification for this loop. Follow it; do not re-derive intent
  from the diff.

  ## Objective
  Move SP-1, SP-2, and the AP half of SP-4 into AAW-owned routing so the Superpowers fork can
  become a mirror. A minimal host-neutral patch against current upstream is an acceptable
  fallback if it is justified in writing.

  ## Hard rules
  - Branch from current upstream/main. Never copy the stale fork files forward.
  - No .claude/ path probes in ported logic. Read the installation manifest.
  - Prove behaviour with AND without Advanced Planning. File inspection is not proof.
  - Do not port SP-3. Do not port the Plannotator half of SP-4.

  ## Success criteria
  - [ ] port branch provably starts at current upstream/main, with a backup tag on the old head
  - [ ] SP-1, SP-2, SP-4-AP reimplemented with host-neutral detection
  - [ ] ACC-04 proven in a fixture with Advanced Planning
  - [ ] ACC-05 proven in a fixture without it, with zero .advanced-plans references in the output
  - [ ] the upstream Three Paths router is diffed and shown intact
  - [ ] a different provider reviewed it; mirror-or-patch outcome recorded
---
```
