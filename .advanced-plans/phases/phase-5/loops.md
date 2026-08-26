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
task_name: "Deliver the integration intent through the fenced routing block, and take the fork to mirror"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Back up the fork head and prepare the mirror locally — annotated tag on the pre-port fork head, plus a local branch that matches upstream/main exactly. No remote write of any kind."
    repository: "superpowers"
    base_sha: "origin/main fde9f97 (backup); upstream/main, re-fetched (mirror)"
    allowed_paths: ["local refs in the superpowers checkout only"]
    forbidden_paths: ["any remote ref", "<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git tag -n99 on the backup tag shows the pre-port fork head fde9f97"
      - "git diff upstream/main..<mirror branch> -> completely empty, proving the tree is a mirror"
      - "git log --oneline origin/main..<mirror branch> and the reverse -> recorded, so the operator sees exactly what publishing would change"
    evidence: "Backup tag, mirror branch name and head SHA, both diff outputs, and the exact command that would publish it"
    gate: "none"
    outcome: "The fork can be taken to mirror by one reviewed command, and the old state is recoverable"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-2"
    content: "Author the fenced AAW routing block carrying SP-1, SP-2 (Architectural path only), the SP-4a companion pointer and SP-3, gated on the manifest predicate. Two variants: CLAUDE.md and AGENTS.md."
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-1; manifest merged 2026-08-26"
    allowed_paths: [".claude/skills/setup-with-claude/references/", "docs/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "the block reads .aaw/installed.json .components[advanced-planning].installed — no directory existence test anywhere in it"
      - "grep the block for .claude/ and .cursor/ and .opencode/ -> zero hits"
      - "SP-2 names the Architectural path explicitly and says Spike and Bounded are untouched"
      - "grep the block for plannotator -> zero hits"
      - "the AGENTS.md and CLAUDE.md variants say the same thing about SP-1, SP-2 and SP-3; only host mechanics differ"
    evidence: "Both block texts and every grep output"
    gate: "none"
    outcome: "All four intents are expressed in a file AAW owns, so the fork needs no patch at all"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-3"
    content: "Make the installer merge the block idempotently into an existing instruction file without replacing user-authored content"
    repository: "Advanced-AI-Workflows"
    base_sha: "loop-002-2"
    allowed_paths: [".claude/skills/setup-with-claude/", "tests/packaging/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "install twice into a fixture -> the instruction file is byte-identical after the second run"
      - "install into a fixture whose instruction file already has user content -> that content survives verbatim"
      - "the block is delimited so uninstall can remove exactly it and nothing else"
      - "tests/packaging/run-all.sh still passes"
    evidence: "The fixture diffs, the byte-identical proof, and the suite output"
    gate: "none"
    outcome: "Design section 7.2 idempotency holds in practice, not just on paper"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-4"
    content: "Prove the behaviour with Advanced Planning present: an approved design lands in .advanced-plans/specs/ and the Architectural terminal state routes to phase planning"
    repository: "a temporary fixture project"
    base_sha: "loop-002-3"
    allowed_paths: ["the fixture project"]
    forbidden_paths: ["the live profile", "<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "run the flow end to end; assert the output landed in .advanced-plans/specs/ — ACC-04"
      - "assert the Architectural terminal state invoked phase planning"
      - "run a Spike-classified and a Bounded-classified request; assert NEITHER produced a spec file or invoked phase planning"
    evidence: "The fixture transcript and the resulting file paths, for all three router paths"
    gate: "none"
    outcome: "SP-1 and SP-2 are proven by behaviour, and the router is proven not to have been over-hooked"
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
      - "assert the manifest predicate read false rather than the file being missing entirely — absence must be recorded, not inferred"
    evidence: "The fixture transcript, the resulting paths, the manifest contents, and the grep output"
    gate: "none"
    outcome: "ACC-05 passes — the failure mode where AAW invents a path that does not exist is excluded"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-6"
    content: "Prove the fork is a mirror by diffing the whole tree against upstream, not by asserting it"
    repository: "superpowers (mirror branch)"
    base_sha: "loop-002-5"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git diff upstream/main..<mirror branch> -> empty. Any non-empty result is a failed port, not a partial success"
      - "git show upstream/main:skills/brainstorming/SKILL.md contains the Three Paths router verbatim as quoted in the drift evidence"
    evidence: "Both outputs in full"
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
      - "the reviewer is asked specifically whether the fenced block over-reaches into user instructions"
      - "if a fork patch remains, it is host-neutral, minimal, against current upstream, and justified in writing"
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
  from the diff. Read all three evidence documents before starting:
  - evidence/2026-08-26-superpowers-behaviour-matrix.md    (the spec)
  - evidence/2026-08-26-upstream-superpowers-drift.md      (what upstream now does)
  - evidence/2026-08-26-superpowers-matrix-gate-review.md  (what the gate changed and why)

  ## Objective
  Deliver SP-1, SP-2, SP-3 and the SP-4a companion pointer through the fenced AAW routing
  block in AGENTS.md / CLAUDE.md, so the Superpowers fork needs no patch and can become a
  mirror. The fork patch target is ZERO. A remaining patch is a failure to be justified, not
  a planned outcome.

  ## What changed from the first draft of this loop
  This loop was written before the matrix existed and contradicted it in two places. Both are
  now corrected above. Do not resurrect either:
  - SP-4a is NOT ported into Superpowers. The fenced block is read earlier and AAW owns it.
  - SP-3 is NOT left in the fork "pending upstream". It goes in the fenced block too.

  ## Entry criteria — settled, do not re-litigate
  1. Manifest predicate: Advanced Planning is present iff
     .aaw/installed.json .components["advanced-planning"].installed is true. A .advanced-plans/
     directory is data and does not count. Merged into this branch 2026-08-26.
  2. Precedence: the block is additive and idempotent. It must never assert authority over
     user-authored instructions, and re-running the installer must leave the file
     byte-identical.
  3. Acceptance: loop-002-4 and loop-002-5 are the with-AP and without-AP tests. File
     inspection is not proof.

  ## Hard rules
  - Never copy the stale fork files forward. Nothing is written into Superpowers at all.
  - No .claude/, .cursor/ or .opencode/ probe in the routing. Read the manifest.
  - SP-2 attaches to the Architectural path ONLY. Spike and Bounded must behave exactly as
    upstream has them, and loop-002-4 tests that.
  - Do not port the Plannotator half of SP-4. It is dropped.
  - No remote write in this loop. Publishing the mirror is a separate authorisation.

  ## Success criteria
  - [ ] backup tag and mirror branch exist locally, with the publish command written down
  - [ ] the fenced block carries SP-1, SP-2, SP-3 and SP-4a with host-neutral detection
  - [ ] the installer merges it idempotently without touching user content
  - [ ] ACC-04 proven with Advanced Planning, including that Spike and Bounded are untouched
  - [ ] ACC-05 proven without it, with zero .advanced-plans references in the output
  - [ ] git diff upstream/main..<mirror branch> is empty
  - [ ] a different provider reviewed it; mirror-or-patch outcome recorded
---
```
