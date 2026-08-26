# Phase 4 — Ralph Loops

Source phase plan: `.advanced-plans/phases/phase-4/plan.md`
Design spec: §14 Workstreams 1A (gstack) and 1B
Procedure: `docs/upstream-sync-playbook.md`
Baseline: `.advanced-plans/evidence/2026-08-26-baseline-audit.md` §2.3, §3

**Standard programme forbidden set.** Forbidden for every worker todo in this programme, without
exception: `.advanced-plans/state/`, `.advanced-plans/PLANNING.md`,
`.advanced-plans/PLANS-INDEX.md`, `.advanced-plans/phases/*/complete.md`,
`.advanced-plans/gate-verdicts/`, `.advanced-plans/evidence/`. Only the controller checkout
writes those.

Loops 001 and 002/003 touch different repositories and may run concurrently in separate Herdr
worktrees with separate owners.

---

```yaml
---
name: "ralph-loop-001"
task_name: "gstack upstream sync"
max_iterations: 2
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-001-1"
    content: "Fetch origin and upstream in the gstack fork and re-record heads, divergence, and merge base at full SHAs, comparing against the baseline"
    repository: "gstack (C:\\Users\\mharvey2\\Coding\\gstack-fork)"
    base_sha: "origin/main a5dc03bdd64124b302cb56927f0866edc0c11879; upstream/main ad8400543cd9ce8d07641362db48d44a95417e33; merge-base 029356e1f0693f22cb1fa4524c9b0f28ceab5a1b"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git rev-list --left-right --count upstream/main...origin/main -> baseline says 89 and 3"
      - "git merge-base upstream/main origin/main"
      - "git merge-base --is-ancestor <merge-base> upstream/main -> must succeed"
    evidence: "Fresh full SHAs and divergence counts, with any delta from the baseline called out explicitly"
    gate: "none"
    outcome: "The sync starts from measured reality rather than from a three-week-old snapshot"
    status: completed
    complexity: low
    priority: high
  - id: "loop-001-2"
    content: "Re-verify that the three fork-only commits still carry no net tree patch, using the merge-base diff and NOT a plain upstream-to-fork diff"
    repository: "gstack (C:\\Users\\mharvey2\\Coding\\gstack-fork)"
    base_sha: "loop-001-1"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git diff --stat $(git merge-base upstream/main origin/main) origin/main -> expect empty"
      - "git log --merges --oneline <merge-base>..origin/main -> expect exactly the three known merge commits"
    evidence: "The empty diff output, and the three commit SHAs listed"
    gate: "none"
    outcome: "The replace-the-fork-tree strategy is re-justified at execution time"
    status: completed
    complexity: low
    priority: high
  - id: "loop-001-3"
    content: "Create sync/upstream-<date> from freshly fetched upstream/main in a Herdr worktree, and create the backup tag for the pre-sync fork head"
    repository: "gstack (C:\\Users\\mharvey2\\Coding\\gstack-fork)"
    base_sha: "upstream/main at loop-001-1"
    allowed_paths: ["the sync worktree only"]
    forbidden_paths: ["origin/main", "<standard programme forbidden set>"]
    provider: "controller"
    worktree_owner: "herdr"
    checks:
      - "git log -1 on the new branch matches upstream/main exactly"
      - "git tag -n99 on the backup tag shows the pre-sync fork head"
    evidence: "Branch name, head SHA, backup tag name and target SHA, worktree absolute path"
    gate: "none"
    outcome: "A recoverable sync branch exists locally; the pre-sync state is tagged and cannot be lost"
    status: pending
    complexity: low
    priority: high
  - id: "loop-001-4"
    content: "Run the upstream test/build suite and the Windows install smoke test from the synced tree, recording exact commands and exit codes"
    repository: "gstack (sync worktree)"
    base_sha: "loop-001-3"
    allowed_paths: ["the sync worktree, plus a temporary install target"]
    forbidden_paths: ["the live profile skills directory", "<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "the documented gstack build/test command, with its exit code"
      - "the documented Windows install path, into a temporary target"
    evidence: "Command, exit code, and the tail of output for each. A failure is recorded as a failure, never summarised as passing"
    gate: "none"
    outcome: "The sync branch is known-good or known-bad, on evidence the controller re-ran"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-001-5"
    content: "Have a provider different from the loop-001-4 implementer review the sync branch and record the verdict with the model named"
    repository: "gstack (sync worktree)"
    base_sha: "loop-001-4"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "a provider different from loop-001-4"
    worktree_owner: "herdr"
    checks:
      - "the reviewing and implementing providers are named and differ — ACC-18"
    evidence: "Reviewer verdict, findings, and the model that produced it"
    gate: "none"
    outcome: "The sync branch carries an independent verdict before it is proposed for a PR"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Objective
  Bring the gstack fork current with upstream. This is a pure sync: no AAW-specific change may
  appear on this branch.

  ## Read first
  - docs/upstream-sync-playbook.md section 1 and the gstack procedure
  - baseline audit section 2.3

  ## The one test that matters and is easy to get wrong
  To ask what the fork ADDS, diff from the merge base:
      git diff <merge-base> origin/main
  Do NOT use git diff upstream/main origin/main. That asks how far BEHIND the fork is, produces
  a thousand-file diff, and proves nothing. This mistake was already made once during the
  baseline audit.

  ## Success criteria
  - [ ] heads, divergence, and merge base re-recorded at full SHAs
  - [ ] empty net patch re-confirmed with the merge-base diff
  - [ ] sync/upstream-<date> created from fresh upstream/main, with a backup tag on the old head
  - [ ] upstream suite and Windows install smoke run, with exact commands and exit codes
  - [ ] a different provider reviewed it and the reviewing model is named

  ## Forbidden
  Do not push. Do not open a PR. Do not merge. Do not modify origin/main. Do not add any
  AAW-specific product change to this branch.
---
```

```yaml
---
name: "ralph-loop-002"
task_name: "AAW packaging — restore the untracked glue skill and add a packaging test"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Confirm the .gitignore whitelist is the sole cause the glue skill is untracked, using git check-ignore -v"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "HEAD of the phase-4 base"
    allowed_paths: ["none — read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "git check-ignore -v .claude/skills/gstack-to-plans/SKILL.md -> names the excluding rule and its line"
    evidence: "The check-ignore output naming the exact rule"
    gate: "none"
    outcome: "The fix targets the actual cause rather than the symptom"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-2"
    content: "Widen the .gitignore whitelist by explicit skill directory so gstack-to-plans becomes trackable, without removing the .claude/skills/* exclusion wholesale"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-002-1"
    allowed_paths: [".gitignore"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "git status --porcelain -> only the intended skill becomes visible, nothing else"
      - "git check-ignore -v on the other local skills -> still ignored"
    evidence: "The gitignore diff and the git status before and after"
    gate: "none"
    outcome: "One skill becomes trackable; the machine local skill collection does not leak into the repository"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-3"
    content: "Restore .claude/skills/gstack-to-plans/SKILL.md from the deployed copy, diff it against the contract described in README, SETUP, and ROADMAP, and record any discrepancy before committing"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-002-2"
    allowed_paths: [".claude/skills/gstack-to-plans/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "git ls-files .claude/skills/gstack-to-plans/SKILL.md -> returns the path"
      - "the frontmatter name and description match what the setup skill installs"
      - "every behaviour the docs promise is present in the file, or the gap is written down"
    evidence: "The restored file, its provenance (the deployed copy path and mtime), and a contract-conformance note"
    gate: "none"
    outcome: "The documented install source exists in the repository and matches what the documentation claims it does"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-4"
    content: "Add a packaging test that enumerates every install source named in the documentation and fails when one is missing from a fresh clone"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-002-3"
    allowed_paths: ["tests/packaging/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "the test passes on the current tree"
      - "the test FAILS when the glue skill is temporarily removed — prove this, do not assume it"
      - "the test runs against a fresh clone in a temporary directory, not against the working tree"
    evidence: "Both runs, passing and deliberately failing, with exit codes"
    gate: "none"
    outcome: "This class of defect cannot recur silently"
    status: pending
    complexity: high
    priority: high
  - id: "loop-002-5"
    content: "Have a provider different from the implementer review the packaging branch, with particular attention to whether the gitignore change over-widens"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-002-4"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "a provider different from the implementer"
    worktree_owner: "herdr"
    checks:
      - "the reviewing and implementing providers are named and differ — ACC-18"
    evidence: "Verdict, findings, reviewer model"
    gate: "none"
    outcome: "An independent reader has checked the change that decides what enters the repository"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Objective
  Make a fresh clone of this repository contain everything the documentation tells a user to
  install. The root cause is a .gitignore whitelist that admits only setup-with-claude.

  ## Read first
  - baseline audit section 3
  - README Quick Start, SETUP.md, and .claude/skills/setup-with-claude/SKILL.md

  ## Hard rules
  - Fix the whitelist by naming the skill directory. Do not delete the .claude/skills/* exclusion.
  - Prove the packaging test fails when a source is missing. An unproven test is not a test.
  - Test against a fresh clone in a temporary directory, never against the live working tree.

  ## Success criteria
  - [ ] git check-ignore names the excluding rule before anything is changed
  - [ ] the glue skill is tracked and matches its documented contract
  - [ ] the packaging test passes clean and fails on a deliberately removed source
  - [ ] a different provider reviewed the change
---
```

```yaml
---
name: "ralph-loop-003"
task_name: "AAW packaging — real installation marker, deterministic audit, idempotency"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-003-1"
    content: "Define and write the installation manifest schema (.aaw/installed.json) recording which components are installed, at which version, and to which absolute path"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-002-5"
    allowed_paths: [".aaw/", "tests/packaging/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "the schema is validated by a test, not merely documented"
      - "every path recorded is absolute and native Windows, with no ~ and no HOME"
    evidence: "Schema, an example manifest, and the validating test"
    gate: "none"
    outcome: "Component detection has a real source of truth to read"
    status: pending
    complexity: high
    priority: high
  - id: "loop-003-2"
    content: "Replace stale .advanced-plans/ probing in setup-with-claude with a manifest plus skill-presence check, so a data directory alone no longer reads as installed"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-003-1"
    allowed_paths: [".claude/skills/setup-with-claude/", ".aaw/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "a temporary project containing only a stale .advanced-plans/ reports data present, Advanced Planning absent — ACC-02"
      - "a genuinely installed project still reports installed"
    evidence: "Both temporary-project runs with their output"
    gate: "none"
    outcome: "ACC-02 passes, and the false-positive that made the v0.1 detection unreliable is gone"
    status: pending
    complexity: high
    priority: high
  - id: "loop-003-3"
    content: "Add a deterministic non-interactive audit mode that can run in CI, keeping the conversational setup skill as the front end"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-003-2"
    allowed_paths: [".claude/skills/setup-with-claude/", "tools/", "tests/packaging/"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "claude"
    worktree_owner: "herdr"
    checks:
      - "the audit runs to completion with no prompt and a meaningful exit code"
      - "the same input produces the same output twice"
    evidence: "Two identical runs, plus the exit codes for a healthy and an unhealthy project"
    gate: "none"
    outcome: "Installation health becomes a check a machine can run, not only a conversation"
    status: pending
    complexity: high
    priority: high
  - id: "loop-003-4"
    content: "Prove install, refresh, and uninstall idempotency in a temporary project with global paths redirected away from the live profile"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-003-3"
    allowed_paths: ["a temporary project directory", "tests/packaging/"]
    forbidden_paths: ["the live profile", "<standard programme forbidden set>"]
    provider: "codex or opencode"
    worktree_owner: "herdr"
    checks:
      - "refresh run twice -> the second run reports and makes no change — ACC-16"
      - "uninstall -> AAW fenced blocks and files gone, user-authored content preserved"
      - "install after uninstall -> returns to the same manifest state"
    evidence: "Full transcript of the temporary-project run, plus before/after file listings"
    gate: "none"
    outcome: "The install surface behaves the same on the second run as on the first"
    status: pending
    complexity: high
    priority: high
  - id: "loop-003-5"
    content: "Have a provider different from the implementer review loops 002 and 003 together as one packaging change and record the verdict"
    repository: "Advanced-AI-Workflows (feat/aaw-packaging-repair)"
    base_sha: "loop-003-4"
    allowed_paths: ["read-only"]
    forbidden_paths: ["<standard programme forbidden set>"]
    provider: "a provider different from the implementer"
    worktree_owner: "herdr"
    checks:
      - "the reviewing and implementing providers are named and differ — ACC-18"
    evidence: "Verdict, findings, reviewer model, and the human resolution or waiver of each finding"
    gate: "human"
    outcome: "The packaging branch is reviewed as a whole before it is proposed for a PR"
    status: pending
    complexity: medium
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]

  ## Objective
  Make installation state knowable. Today detection probes for a path that lies in both
  directions: .advanced-plans/ exists without an adapter, and .claude/ paths are Claude-only.

  ## Hard rules
  - Never test install, refresh, or uninstall against the live profile. Redirect global paths
    to a temporary directory.
  - Absolute native Windows paths only. No ~, no HOME. Global locations resolve from USERPROFILE.
  - Keep this branch to the packaging repair. Do not start the multi-runtime adapter work here.

  ## Success criteria
  - [ ] .aaw/installed.json schema exists and is test-validated
  - [ ] a stale .advanced-plans/ alone reports Advanced Planning absent
  - [ ] audit is non-interactive, deterministic, and returns a meaningful exit code
  - [ ] refresh twice is a no-op; uninstall preserves user content; reinstall restores the manifest
  - [ ] a different provider reviewed the whole packaging change
---
```
