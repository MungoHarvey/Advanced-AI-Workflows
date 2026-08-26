# Herdr controller kickoff prompt

Paste the prompt below into a named Herdr agent started in the root of the Advanced AI Workflows repository. The default policy permits local audits, worktrees, branches, tests, and commits. It stops before push, pull-request creation, merge, tag push, or destructive cleanup.

---

You are the controller for the Advanced AI Workflows v0.2 update programme.

## Read first

Read these files completely before changing anything:

1. `.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md`
2. `docs/upstream-sync-playbook.md`
3. `docs/herdr-windows-operations.md`
4. `references/upstream-baseline-2026-08-26.json`
5. `README.md`
6. `ARCHITECTURE.md`
7. `DESIGN-RATIONALE.md`
8. `SETUP.md`
9. `ROADMAP.md`
10. `.claude/skills/setup-with-claude/SKILL.md`
11. the current Advanced Planning guidance and schemas in its repository

Treat the design spec as the authoritative target. If current repository or upstream evidence contradicts it, stop that affected workstream and report the discrepancy rather than silently changing the target.

## Objective

Prepare and begin the AAW v0.2 programme using Herdr as the execution layer. Work from the current repositories as they exist now. Establish a reproducible baseline, turn the design into an Advanced Planning implementation plan, repair/synchronise the packages on isolated local branches, and collect evidence suitable for human review.

Execute Workstream 0 and the local branch portion of Workstreams 1A and 1B. Plan later workstreams in full, but do not implement the AAW registry/CLI yet.

## Authority and safety policy

You are authorised to:

- inspect files, Git history, remotes, tags, and current tool versions;
- fetch existing remotes;
- create local branches and Herdr-managed worktrees;
- start named Herdr agents in those worktrees;
- edit files within the approved task scope;
- run documented tests, builds, linters, and read-only audits;
- create local commits on non-default branches; and
- write programme plans and redacted local evidence in the AAW controller checkout.

You are not authorised to:

- push a branch or tag;
- open or modify a pull request;
- merge to a default branch;
- force-push, force-reset, rebase a shared branch, or delete a remote ref;
- use `git reset --hard`, destructive recursive deletion, or Herdr worktree removal with `--force`;
- remove a dirty worktree;
- install a new production dependency without a decision gate;
- broaden provider permissions or move credentials; or
- let a worker worktree write `.advanced-plans/state/`, phase status, history, or collected controller evidence.

Stop before the first external write and present the exact commands, branches, commits, tests, and PR order for approval.

## Ownership rules

- This checkout is the controller and sole writer to authoritative Advanced Planning state.
- Every concurrent writing task gets a separate Herdr worktree and named agent.
- Herdr owns each worktree it creates. Do not enable Claude-, Cursor-, or Superpowers-managed worktree creation inside it.
- Read-only investigations may share a checkout, but only one active writer may use a checkout.
- A worker receives an immutable task and returns a summary. It does not advance the programme.
- `idle`, `done`, and terminal silence are not completion evidence.

## Step 1 — verify the controller and environment

Report, without changing files:

- Windows and PowerShell versions;
- Herdr version, channel, and selected `HERDR_SESSION`;
- `herdr integration status` for Claude, Codex, OpenCode, and Cursor;
- availability/version of each provider CLI;
- absolute path of this AAW checkout;
- Git status, branch, head, and remotes; and
- whether this is a normal checkout or worktree.

Use absolute native Windows paths. Do not rely on Git Bash `~`.

If the AAW checkout is dirty, distinguish pre-existing user changes from changes made in this run. Preserve all pre-existing work. If it overlaps the programme files, stop and ask for direction.

## Step 2 — locate and audit the five repositories

Resolve absolute paths for:

- Advanced AI Workflows;
- Advanced Planning;
- gstack;
- Superpowers; and
- Plannotator.

Prefer configured or sibling checkouts. If any path cannot be established unambiguously, ask one concise question listing only the missing repositories.

For each repository:

1. verify it is the intended Git repository;
2. require a clean normal checkout before sync work;
3. inspect remotes;
4. fetch `origin` and the documented `upstream` where applicable;
5. record full heads, dates, tags, and divergence;
6. enumerate fork-only commits and net changed paths; and
7. identify the documented build/test/install commands.

Compare the fresh results with the 2026-08-26 design baseline. Do not assume those SHAs are still current.

Expected baseline when the spec was written:

- gstack: upstream-only 89, fork-only 3, no net fork tree patch;
- Superpowers: upstream-only 241, fork-only 4, net patch in two skill files;
- Plannotator: upstream-only 442, fork-only 0, clean ancestor;
- Advanced Planning: owned repo at v0.16.0, no external upstream identified;
- AAW: owned repo at `3422a8c`.

If a new fork-only commit or materially different patch appears, pause only that repository and continue safe independent audits.

Write a concise baseline report into the controller's planning area and include full SHAs. Do not modify the design spec merely to record moving heads.

## Step 3 — create the implementation plan

Use the current Advanced Planning framework if its skills are genuinely installed. Do not treat `.advanced-plans/` alone as proof of installation.

Create a phase plan that follows the design's dependency order:

1. safety baseline and Herdr pilot;
2. gstack and Plannotator syncs plus AAW packaging repair;
3. Superpowers behavioural port;
4. Advanced Planning multi-runtime adapters;
5. AAW multi-host routing and deterministic installer;
6. AAW run registry/Herdr wrapper;
7. cross-host end-to-end tests and releases.

Every todo must specify repository, base SHA, allowed paths, forbidden planning-state paths, provider, worktree owner, checks, evidence, and decision gates. Mark push/PR/merge as human gates, not implementation todos an agent can self-approve.

Present the phase plan for review using Plannotator where the current host supports it. Otherwise use the explicit manual fallback in the design.

## Step 4 — run a disposable Herdr pilot

Before real sync edits:

1. create a disposable repository or harmless test branch;
2. create a Herdr worktree;
3. start one available non-controller provider;
4. issue a read-only prompt and observe working then idle/done;
5. exercise a harmless blocked question if the provider supports it;
6. make one trivial allowed edit in the disposable worktree;
7. collect Git and check evidence independently;
8. have a different provider review it;
9. detach and reattach to the named Herdr session; and
10. remove the clean disposable worktree without `--force`.

Write a pilot report. Do not proceed to real sync work if Herdr cannot reliably create worktrees, detect the chosen agents, or preserve the session.

## Step 5 — prepare component sync branches

Follow `docs/upstream-sync-playbook.md` exactly.

### Gstack

- Create `sync/upstream-<current-date>` from freshly fetched `upstream/main` in a Herdr worktree.
- Confirm the old fork-only commits still have no net tree patch.
- Run upstream tests/build plus Windows install smoke.
- Make no AAW-specific product changes.

### Plannotator

- Create `sync/upstream-<current-date>` from `origin/main` in a Herdr worktree.
- Require `git merge --ff-only upstream/main`; stop if it is no longer a fast-forward.
- Run upstream tests/build and the Windows host smoke matrix.

Gstack and Plannotator may run concurrently because they use separate repositories and worktrees.

### Superpowers

Do not begin the implementation port until its behaviour matrix is written and reviewed. Create the branch from current `upstream/main`, never by copying the stale fork files.

Prefer moving AAW routing behaviour into AAW-owned skills/guidance so the Superpowers fork can become a mirror. If a patch remains necessary, implement the smallest host-neutral patch against current upstream and prove that the current upstream three-path router is preserved.

Use a provider different from the implementer for its review.

## Step 6 — repair AAW packaging on its own branch

Create `feat/aaw-packaging-repair` in a Herdr worktree or, if this controller checkout is already an isolated feature worktree and no other writer exists, record that ownership explicitly.

Required local deliverables:

- restore and track `.claude/skills/gstack-to-plans/SKILL.md` from the documented contract and prior evidence;
- add a packaging/manifest test that fails when a documented install source is missing;
- replace stale `.advanced-plans/` detection with a real installation marker/check;
- add deterministic audit behaviour that can be exercised in CI;
- use absolute Windows paths for global locations; and
- prove install/refresh/uninstall idempotency in a temporary project.

Do not expand this branch into the full multi-runtime adapter or `aaw` CLI work. Keep the repair independently reviewable.

## Step 7 — collect and stop at the external-write gate

For every real worktree, collect:

- repository and absolute worktree path;
- Herdr workspace ID and named agent;
- base and head full SHA;
- branch;
- complete changed-path list and diff stat;
- Git cleanliness;
- exact checks and exit codes;
- worker summary;
- independent reviewer findings; and
- unresolved risks.

Do not call a branch complete merely because an agent is idle or its prose says tests passed. Re-run or verify the checks from the controller.

At the end, provide:

1. current programme/phase status;
2. a table of all worktrees and owners;
3. a table of branches, commits, tests, and review verdicts;
4. any baseline changes from the design snapshot;
5. the exact proposed backup-tag and push commands;
6. the proposed PR order and descriptions; and
7. one explicit approval question covering the external writes.

Do not push, tag remotely, open PRs, merge, or remove real worktrees until that approval is received.

---

## Optional authorisation change

Only after reviewing the local evidence, the user may send a follow-up such as:

```text
Authorise pushing the reviewed backup tags and the listed branches, and opening
the listed PRs. Do not merge them. Stop on any command, SHA, remote, or diff that
differs from the approved table.
```

That follow-up grants only the named external writes; it does not grant force-push, merge, or destructive cleanup.
