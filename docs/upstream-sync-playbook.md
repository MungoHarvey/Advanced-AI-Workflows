# Upstream sync playbook

This guide updates the component forks used by Advanced AI Workflows without losing local behaviour or writing directly to a default branch. It is written for native Windows PowerShell and Herdr.

The baseline below was fetched on 2026-08-26. Always fetch again before acting.

The same snapshot is available in machine-readable form at [`references/upstream-baseline-2026-08-26.json`](../references/upstream-baseline-2026-08-26.json). It is an audit input, not a lock file; replace its observations with a freshly generated baseline on the implementation branch.

## Current baseline

| Fork | Upstream | Fork head | Upstream head | Upstream-only | Fork-only | Strategy |
|---|---|---|---|---:|---:|---|
| `MungoHarvey/gstack` | `garrytan/gstack` | `a5dc03b` | `ad84005` | 89 | 3 | replace tree from upstream; fork-only commits are merges with no net patch |
| `MungoHarvey/superpowers` | `obra/superpowers` | `fde9f97` | `b36e082` (`v6.3.0`) | 241 | 4 | re-port behaviour onto current upstream |
| ~~`MungoHarvey/plannotator`~~ | ~~`backnotprop/plannotator`~~ | ~~`4db7fcc`~~ | ~~`b381ecb` (`v0.27.8`)~~ | ~~442~~ | ~~0~~ | **deprecated 2026-08-26 — no longer synced** |
| `MungoHarvey/advanced-planning` | none identified | `02b4b86` (`v0.16.0`) | n/a | n/a | n/a | owned package; normal feature branches |
| `MungoHarvey/Advanced-AI-Workflows` | none | `3422a8c` | n/a | n/a | n/a | owned meta-project; normal feature branches |

In the divergence columns, `git rev-list --left-right --count upstream/main...origin/main` is read as `upstream-only fork-only`.

## Safety rules

1. Fetch before calculating divergence.
2. Begin from a clean normal checkout.
3. Create one annotated backup tag for the fork's current `origin/main`; push it only after the user approves the external write.
4. Perform all changes on a named sync branch in a separate Herdr worktree.
5. Do not merge, reset, or force-push the fork's default branch directly.
6. Do not use `git reset --hard` as a sync mechanism.
7. Do not cherry-pick stale integration commits until their behaviour has been restated as tests.
8. Run the upstream suite first, then AAW compatibility tests.
9. Review the full tree diff and commit graph before opening a PR.
10. Remove a worktree only when Git reports it clean. Do not use Herdr's `--force` cleanup during the normal workflow.

## 1. Preflight audit

Run this in each normal fork checkout. Replace the upstream URL for the repository being audited.

```powershell
$Repo = (Resolve-Path 'C:\Users\mharvey2\Coding\gstack-fork').Path
Set-Location $Repo

git status --short
git remote -v

git remote get-url upstream 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote add upstream https://github.com/garrytan/gstack.git
}

git fetch --prune origin
git fetch --prune --tags upstream

git show -s --format='%H %cI %s' origin/main
git show -s --format='%H %cI %s' upstream/main
git rev-list --left-right --count upstream/main...origin/main
git log --oneline upstream/main..origin/main
git diff --stat upstream/main...origin/main
```

Stop if:

- `git status --short` is non-empty;
- the remote URLs are not the intended repositories;
- the default branch is not `main`;
- the observed divergence materially differs from the strategy below; or
- a new fork-only change has appeared.

Record the full `origin/main` and `upstream/main` SHAs in the sync PR description. Short SHAs are for display only.

## 2. Preserve the pre-sync fork head

After audit and before creating a sync PR:

```powershell
$Stamp = Get-Date -Format 'yyyy-MM-dd'
$Tag = "pre-upstream-sync-$Stamp"

git tag -a $Tag origin/main -m "Fork head before upstream sync $Stamp"
git show --no-patch $Tag
```

Pushing the tag is an external write. Review the resolved tag and commit, then:

```powershell
git push origin "refs/tags/$Tag"
```

If the tag already exists, inspect it. Do not silently move or overwrite it; choose a unique suffix such as `-2`.

## 3. Use Herdr for each sync branch

Run Herdr directly in Windows Terminal rather than nesting the managed agent inside another multiplexer.

Example for a branch based on upstream:

```powershell
$Repo = (Resolve-Path 'C:\Users\mharvey2\Coding\gstack-fork').Path
$Created = herdr worktree create `
    --cwd $Repo `
    --branch 'sync/upstream-2026-08-26' `
    --base upstream/main `
    --label 'gstack upstream sync' `
    --no-focus | ConvertFrom-Json

$WorkspaceId = $Created.result.workspace.workspace_id
$PaneId = $Created.result.root_pane.pane_id

herdr agent start gstack-sync --kind codex --pane $PaneId
```

Keep `$WorkspaceId`; it is required for safe worktree removal after the PR work is complete. Agent names must be unique, lowercase, and no more than 32 characters.

## 4. Gstack procedure

### Why

The three fork-only commits are merge commits:

- `5847946`;
- `973fedc`; and
- `a5dc03b`.

`git diff upstream/main...origin/main` is empty at the audited baseline, so there is no local tree patch to port. The fork can become a current upstream mirror.

### Branch

Create the Herdr worktree from the newly fetched `upstream/main` as shown above. Give the agent this bounded task:

```text
Audit this sync branch against origin/main and upstream/main. Confirm that the
fork-only commits contain no net tree change, run the repository's documented
test and build commands on this upstream tree, and produce a sync report. Do
not alter product behaviour, push, merge, force-reset, or delete anything.
```

### Required evidence

```powershell
git status --short
git log --oneline --decorate --graph --max-count 30
git diff --stat origin/main...HEAD
git diff --check origin/main...HEAD
git diff --exit-code upstream/main..HEAD
```

Run the current upstream-documented install/build/test commands, including the Windows setup path if a native Windows runner is available. Record exact commands and exit codes in the PR.

### PR

Push the sync branch after human review:

```powershell
git push -u origin sync/upstream-2026-08-26
```

Open a PR to `MungoHarvey/gstack:main`. The PR description must state that the prior fork-only commits were merges with no net patch and link the backup tag.

After merge and a fresh fetch, this must be empty:

```powershell
git diff --exit-code upstream/main...origin/main
```

## 5. Plannotator procedure — withdrawn

**Plannotator was deprecated on 2026-08-26.** It is no longer a component of this project, so
there is no sync to perform. The fast-forward procedure that stood here has been withdrawn.

The `MungoHarvey/plannotator` fork is left as it is on GitHub — deprecation is a decision about
this project's dependencies, not a deletion. If it is ever reinstated, re-derive the procedure from
a fresh audit rather than from this document's history: the fork was 442 commits behind upstream at
the last audit and that gap only grows.

See [plannotator-deprecation.md](plannotator-deprecation.md).

## 6. Superpowers procedure

### Why this one is different

The fork has four fork-only commits and a real net patch in:

- `skills/brainstorming/SKILL.md`; and
- `skills/using-superpowers/SKILL.md`.

Current upstream is hundreds of commits ahead and has redesigned brainstorming and multi-host behaviour. Copying the old fork files or blindly cherry-picking the old commits would overwrite upstream improvements.

### Behaviour first

Before editing, turn the local intent into tests/fixtures:

| Case | Expected behaviour |
|---|---|
| Advanced Planning absent | preserve current upstream brainstorming output and next-step router |
| Advanced Planning installed through AAW manifest | save approved design to `.advanced-plans/specs/` and route to Advanced Planning |
| stale `.advanced-plans/` only | treat Advanced Planning as absent |
| Claude Code | use host-appropriate human question/review UI without hard-coding that mechanism into core content |
| Codex/OpenCode/Cursor | detect through the portable manifest/skills, not `.claude/` paths |
| all cases | retain upstream v6.3.0 three-path brainstorming router and session/worktree handling |

### Preferred implementation

First attempt to move all AAW-specific behaviour into an AAW-owned routing skill and fenced project guidance. If the tests pass without modifying upstream Superpowers files, make `MungoHarvey/superpowers` a clean upstream mirror.

Only retain a Superpowers fork patch if a required behaviour cannot be expressed at the AAW boundary. In that event:

- implement the smallest host-neutral patch against current `upstream/main`;
- document why the boundary adapter is insufficient;
- add upstream-compatible tests;
- avoid Claude-only paths and tool names; and
- prepare a candidate upstream contribution separately from the fork sync.

### Branch

Create from current upstream, not from the stale fork head:

```powershell
$Repo = (Resolve-Path 'C:\Users\mharvey2\Coding\superpowers').Path
$Created = herdr worktree create `
    --cwd $Repo `
    --branch 'sync/upstream-2026-08-26' `
    --base upstream/main `
    --label 'superpowers upstream port' `
    --no-focus | ConvertFrom-Json

$WorkspaceId = $Created.result.workspace.workspace_id
$PaneId = $Created.result.root_pane.pane_id

herdr agent start superpowers-sync --kind claude --pane $PaneId
```

Prompt the worker to read the AAW design spec and this guide, implement the behaviour matrix, and stop before push. Explicitly forbid wholesale replacement from `origin/main` and direct modification of default branches.

### Review

Use a different provider from the implementer for review. Require it to compare:

```powershell
git diff --stat upstream/main...HEAD
git diff upstream/main...HEAD
git diff --check upstream/main...HEAD
git log --oneline upstream/main..HEAD
```

The reviewer must answer:

1. Does current upstream behaviour remain intact?
2. Is every surviving fork change required?
3. Is detection host-neutral and resistant to stale directories?
4. Can the behaviour live in AAW instead?
5. Do tests cover the Advanced Planning present/absent matrix?

Push and open the fork PR only after this independent review and the human gate.

## 7. Advanced Planning and AAW

These repositories are owned packages rather than forks of an identified upstream. Do not add an arbitrary `upstream` remote.

Use normal feature branches:

- `feat/multi-runtime-adapters` in Advanced Planning;
- `feat/herdr-multi-runtime-orchestration` in AAW.

Advanced Planning should release its adapter changes first. The AAW integration branch then pins and tests that exact release/commit. AAW documentation may land earlier if every future capability remains explicitly marked as planned.

## 8. PR order

Recommended merge order:

1. gstack sync PR;
2. AAW packaging repair PR;
3. Superpowers upstream sync/boundary-routing PR;
4. Advanced Planning multi-runtime adapter PRs;
5. AAW routing/installer PR;
6. AAW registry/Herdr CLI wrapper PRs;
7. compatibility manifest, end-to-end evidence, and release PR.

Do not pin AAW to a proposed fork SHA. Pin only a reviewed commit that exists on the fork's durable branch/tag.

## 9. PR evidence template

Every sync PR should contain:

```markdown
## Baseline
- Fork before: <full SHA>
- Upstream tested: <tag and full SHA>
- Backup tag: <tag>
- Divergence before: <upstream-only> / <fork-only>

## Local behaviour
- Behaviour retained: <list or none>
- Behaviour moved to AAW: <list or none>
- Behaviour intentionally removed: <list or none, with reason>

## Verification
- <command>: exit <code>
- <command>: exit <code>
- Windows install smoke: <result>
- AAW compatibility matrix: <result>

## Review
- Implementer runtime: <provider>
- Independent reviewer runtime: <different provider>
- Human gate: <pending/approved>
```

## 10. Safe worktree closeout

After the branch is pushed and its evidence is preserved:

```powershell
herdr agent get <agent-name>
herdr workspace get $WorkspaceId
```

Inspect the worktree itself:

```powershell
git status --short
git log --oneline --decorate --max-count 10
```

Only when the worktree is clean and no longer needed:

```powershell
herdr worktree remove --workspace $WorkspaceId
```

This removes the checkout but does not delete the branch. If removal refuses because the checkout is dirty, inspect it and preserve the changes; do not add `--force` simply to finish the runbook.

## 11. Post-merge compatibility update

After each PR merges:

1. fetch `origin` and `upstream` again;
2. record the merged full SHA;
3. rerun the relevant host installation smoke test;
4. update AAW's compatibility manifest on its integration branch;
5. run `aaw doctor` once implemented, or the equivalent manual audit before then; and
6. retain the pre-sync backup tag until at least the next successful AAW release.

The fork is not considered current merely because GitHub shows the PR merged. It is current when the tested merged SHA is recorded in AAW and the integration suite passes.
