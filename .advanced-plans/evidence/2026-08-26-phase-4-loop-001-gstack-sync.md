# gstack upstream sync — phase 4 loop 001

**Collected:** 2026-08-26
**Covers:** todos loop-001-3 (branch + backup tag) and loop-001-4 (suite + install smoke)
**Repository:** `C:\Users\mharvey2\Coding\gstack-fork`
**Worktree owner:** `herdr`

Read with `.advanced-plans/evidence/2026-08-26-fork-divergence-reaudit.md`, which covers todos
loop-001-1 and loop-001-2 and establishes the empty net patch this sync depends on.

---

## 1. The refs

| | Full SHA |
|---|---|
| pre-sync `origin/main` | `a5dc03bdd64124b302cb56927f0866edc0c11879` |
| `upstream/main` at sync | `ad8400543cd9ce8d07641362db48d44a95417e33` |
| merge base | `029356e1f0693f22cb1fa4524c9b0f28ceab5a1b` |
| `sync/upstream-2026-08-26` head | `ad8400543cd9ce8d07641362db48d44a95417e33` |

The sync branch head is **identical to `upstream/main`**, which is the loop-001-3 check:

```
$ git log -1 --format='%H %s' sync/upstream-2026-08-26
ad8400543cd9ce8d07641362db48d44a95417e33 v1.69.0.0 fix: the silent-failure wave — 6 fixes, 5 community PRs absorbed, tracker closed with receipts (#2666)
$ git diff --stat upstream/main sync/upstream-2026-08-26
(empty)
```

`origin/main` is untouched at `a5dc03bd…`. No AAW-specific change was placed on this branch.

### Backup tag

Annotated, local only. `git tag -n99 pre-upstream-sync-2026-08-26`:

```
pre-upstream-sync-2026-08-26 Fork head before upstream sync 2026-08-26

    Pre-sync origin/main: a5dc03bdd64124b302cb56927f0866edc0c11879
    Upstream at sync:     ad8400543cd9ce8d07641362db48d44a95417e33
    Merge base:           029356e1f0693f22cb1fa4524c9b0f28ceab5a1b
    Divergence:           89 behind, 3 ahead (all three ahead-commits are merges)
    Net tree patch from the merge base: empty

    Created by AAW v0.2 phase 4 loop 001. Local only; pushing a tag is a human gate.
    Retain until at least the next successful AAW release.
```

`git cat-file -t` returns `tag`. `git ls-remote --tags origin 'pre-upstream-sync-*'` returns
nothing; the tag has not been pushed, and pushing it is a human gate.

### Worktrees

```
C:/Users/mharvey2/Coding/gstack-fork                           a5dc03bd [main]
C:/Users/mharvey2/Coding/aaw worktrees/gstack-sync-2026-08-26  ad840054 [sync/upstream-2026-08-26]
C:/Users/mharvey2/Coding/aaw worktrees/gstack-presync-control  a5dc03bd [pilot/gstack-presync-control]
```

The `pilot/` worktree is the control described in section 6 and is deleted at the end of this loop.

---

## 2. Environment for every command below

```bash
export HOME="$USERPROFILE"
export HOMEDRIVE="C:"
export HOMEPATH='\Users\mharvey2'
```

This is the phase-3 HOME pin. Without it Git Bash resolves `HOME` to `M:\` and gstack's tooling
looks in the wrong profile.

---

## 3. The first two runs were invalid, and are recorded as invalid

The suite was first run **without `bun run build`**. `browse/src/cli.ts` hard-fails on Windows when
`browse/dist/server-node.mjs` is missing:

```
error: server-node.mjs not found. Run `bun run build` to generate the Windows server bundle.
```

That message appears 7 times in the first `test:windows` log. The runs in section 4 supersede them.

| Run | Command | Exit | Wall | Result |
|---|---|---|---|---|
| 1 (invalid) | `bun run test` | **124** | 8m04s | all 7 shards fail-or-timeout; shards 4 and 6 killed at 445s / 390s |
| 2 (invalid) | `bun run test:windows` | **1** | 1m03s | 13 failing tests |

Both are superseded because the documented build prerequisite had not been run. They are left in
the record because a suite that was run wrongly is not the same thing as a suite that was not run.

---

## 4. The valid runs

### 4.1 Install

```
$ bun install --frozen-lockfile
exit=0   224 packages   23.4s
```

### 4.2 Build

```
$ bun run build
exit=0   real 0m25.203s
...
Node server bundle ready: .../gstack-sync-2026-08-26/browse/dist/server-node.mjs   (0.86 MB)
```

### 4.3 `bun run test:windows` — the run of record

```
$ bun run test:windows
exit=1   real 1m21.061s
```

```
[test:free] curated 261 Windows-safe tests (218 excluded)
[test:free] full suite: 252 files across 6 shard processes, then 9 tree-mutating file(s) serially
[test:free] shard 5/7: 34 files, 19s, pass   — PASS 269 tests
[test:free] shard 6/7: 37 files, 30s, pass   — PASS 556 tests
[test:free] shard 7/7:  9 files, 12s, pass   — PASS  60 tests
[test:free] shard 1/7: 42 files, 25s, fail   — FAIL 1 failing test in 1 file
[test:free] shard 2/7: 47 files,  9s, fail   — FAIL 1 failing test in 1 file, 1 unhandled error
[test:free] shard 3/7: 39 files, 43s, fail   — FAIL 1 failing test in 1 file
[test:free] shard 4/7: 53 files, 60s, fail   — FAIL 4 failing tests in 2 files
```

**This is a failure and is recorded as a failure: exit code 1, 7 failing tests, 3 of 7 shards
passing.** Building first moved it from 13 failures with timeouts to 7 failures with none, but it
did not make it pass.

### 4.4 Every failure, run again in isolation and attributed

Each failing file was re-run on its own with `bun test <file>`:

| File | Isolated | Failing | Cause |
|---|---|---|---|
| `test/tasks-section-jq.test.ts` | exit 1 | 3 | `error: Executable not found in $PATH: "jq"` |
| `test/hermetic-wiring.test.ts` | exit 1 | 1 | `EPERM: operation not permitted, symlink` |
| `test/hermetic-skills-seeding.test.ts` | exit 1 | 1 | `EPERM: operation not permitted, symlink` |
| `test/setup-alias-name-uniqueness.test.ts` | exit 1 | 1 | `alias install failed: … cygheap read copy failed … Win32 error 299` |
| `browse/test/build.test.ts` | exit 1 | 1 | unquoted path containing a space — see 4.5 |
| `test/codex-web-search-flag.test.ts` | **exit 0** | 0 | passes alone; failed at 38s under shard load |

Attribution, checked rather than assumed:

- **`jq` is not installed.** `command -v jq` returns nothing. Three failures, environmental.
- **Windows symlink privilege is off.** The Developer Mode value
  `HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock\AllowDevelopmentWithoutDevLicense`
  is absent, so `symlink()` returns `EPERM` for an unelevated process. Two failures, environmental.
  gstack's own `CONTRIBUTING.md` line 302 says *"Tests run against the browse binary directly — they
  don't require dev mode"*; for these two hermetic tests that is not true on this machine.
- **`setup-alias-name-uniqueness`** shells out to `./setup` and died on a cygwin `fork()` failure
  (`Win32 error 299`, a partial `ReadProcessMemory`). A Git Bash process-creation flake, not a code
  fault. Note the contrast with section 5: the same `./setup`, run directly, exits 0.
- **`codex-web-search-flag`** passes in isolation in under two seconds and took 38s inside the
  shard. Load-induced flake.

### 4.5 The one genuine upstream defect

`browse/test/build.test.ts:16` builds a shell command by interpolation without quoting:

```js
expect(() => execSync(`node --check ${SERVER_NODE}`, { stdio: 'pipe' })).not.toThrow();
```

Our worktree path is `C:\Users\mharvey2\Coding\aaw worktrees\gstack-sync-2026-08-26`. Node receives
the path split at the space:

```
Error: Cannot find module 'C:\Users\mharvey2\Coding\aaw'
```

`server-node.mjs` is fine; `node --check` never reaches it. This is an upstream bug in gstack,
reproducible on any checkout whose path contains a space, and it is worth reporting upstream. It is
**not** introduced by the sync — the fork carries no net patch, so this code is upstream's on both
sides of the sync.

---

## 5. Windows install smoke — into an isolated target

The todo forbids the live profile skills directory. The install was pointed at a scratch profile:

```bash
SMOKE=…/scratchpad/install-smoke-home
rm -rf "$SMOKE"; mkdir -p "$SMOKE/.claude" "$SMOKE/.codex"
env HOME="$SMOKE" USERPROFILE="$(cygpath -w "$SMOKE")" \
    CLAUDE_CONFIG_DIR="$SMOKE/.claude" CODEX_HOME="$SMOKE/.codex" \
    ./setup --host claude -q
```

```
exit=0   real 4m7.631s
```

Tail:

```
Windows detected — verifying Node.js can load Playwright...
  linked skills: autoplan benchmark-models benchmark browse canary careful codex context-restore
  context-save cso design-consultation design-html design-review design-shotgun devex-review
  diagram document-generate document-release freeze gstack-upgrade guard health investigate
  ios-clean ios-design-review ios-fix ios-qa ios-sync land-and-deploy landing-report learn
  make-pdf office-hours open-gstack-browser pair-agent plan-ceo-review plan-design-review
  plan-devex-review plan-eng-review plan-tune qa-only qa retro review scrape
  setup-browser-cookies setup-deploy setup-gbrain ship skillify spec sync-gbrain unfreeze
  note: Windows install uses file copies (no Developer Mode required). Re-run ./setup after every
  'git pull' to refresh skill files.
  linked root skill alias: gstack
```

Verified afterwards:

- `$SMOKE/.claude/skills` holds **56 entries** including `_gstack-command` and the `gstack` root
  alias. `browse/SKILL.md` is a real 59,203-byte file, not a symlink — the file-copy path the note
  describes.
- **The live profile is untouched.** `~/.claude/skills` had 245 entries and md5
  `1ec91947bb1c25659ad777116a94c7ed` over the sorted `SKILL.md` list before the run, and the
  identical count and hash after. `find ~/.claude/skills -newermt '-20 minutes'` returned nothing.

One thing the redirection did **not** contain: Playwright downloaded Chrome for Testing (191.8 MiB)
and Chrome Headless Shell (114.5 MiB) into the machine-wide cache
`C:\Users\mharvey2\AppData\Local\ms-playwright\`, which is keyed off `LOCALAPPDATA`, not `HOME`.
That is a shared cache, not configuration, and it is not the forbidden path — but the smoke test is
not fully hermetic and should not be described as if it were.

---

## 6. The control run, and why it cannot answer the question it was set

A worktree was created at the **pre-sync fork head** `a5dc03bd…` on branch
`pilot/gstack-presync-control`, to test whether the 7 failures pre-date the sync.

```
$ bun install --frozen-lockfile   exit=0
$ bun run build                   exit=0   real 0m19.100s
$ bun run test:windows            exit=1   real 0m40.632s
```

```
[test:free] curated 103 Windows-safe tests (106 excluded)
[test:free] shard 10/20 (5 files) failed with exit code 1
(fail) spawnSkill: lifecycle > untrusted spawn: GSTACK_SKILL_TOKEN visible, root env scrubbed
error: Executable not found in $PATH: "bun"
```

**The pre-sync head also fails**, on its own environmental cause (a spawned subprocess cannot see
`bun` on `PATH`). But it is not a like-for-like comparison, and saying so matters more than the
result:

- the pre-sync runner shards into **20** and **aborts on the first failing shard**; the post-sync
  runner shards into 7, runs them concurrently, and reports all of them. A fail-fast run cannot
  produce a total.
- the curated Windows-safe set grew from **103 tests to 261** across the 89 upstream commits.
- **five of the six failing files do not exist at the pre-sync head** — `tasks-section-jq`,
  `setup-alias-name-uniqueness`, `hermetic-wiring`, `hermetic-skills-seeding`, and
  `codex-web-search-flag` all arrived with upstream. Only `browse/test/build.test.ts` is present on
  both.

So the control establishes that the fork was already failing this suite on this machine, and
nothing sharper than that. The stronger evidence for "not a sync regression" is structural: the
fork carries an **empty net tree patch**, so the synced tree is upstream's tree exactly, and every
failure above is either upstream's code or this machine's environment. There is no fork-specific
code that the sync could have broken.

---

## 7. Verdict on the sync branch

**Known-bad on the suite, and known-good as a sync.** Both halves are true, and the loop's outcome
field asks for the first, so it is stated first.

- `bun run test:windows` exits **1** with **7 failing tests**. That is the recorded result.
- Of those 7: 3 need `jq`, 2 need Windows symlink privilege, 1 is a Git Bash `fork()` flake, 1 is a
  genuine upstream quoting bug triggered by a space in our path. A further shard failure
  (`codex-web-search-flag`) does not reproduce in isolation.
- **Zero** of the 7 are attributable to the sync, and the empty net patch makes that structural
  rather than a judgement call.
- `bun run build` and the Windows install smoke both exit **0**, and the smoke leaves the live
  profile identical.

### Blockers on a PR, if one is later proposed

1. Install `jq` and enable Windows Developer Mode, then re-run, so the environmental failures stop
   masking real ones. The suite has never been observed green on this machine.
2. Report `browse/test/build.test.ts:16` upstream, or move the worktree off a path with a space.
   Preferring the first: the bug is real for any user with a space in their path.

---

## 8. Residue

- Two untracked fixtures the test run created in the sync worktree, both under
  `browse/test/fixtures/`: `test-cookies.db`, `test-cookies-linux.db`. Test artefacts, not tracked,
  not committed.
- `browse/dist/` build output in both worktrees; gitignored.
- Playwright browsers in `%LOCALAPPDATA%\ms-playwright\` — see section 5.
- Logs, all under the session scratchpad: `bun-install.log`, `gstack-test.log`,
  `gstack-test-windows.log`, `sync-build.log`, `sync-windows-postbuild.log`, `iso-*.log`,
  `install-smoke.log`, `control-install.log`, `control-build.log`, `control-windows-postbuild.log`.

## 9. What this does not establish

- Nothing was pushed. The branch and the tag are local. `git ls-remote` confirms neither exists on
  `origin`.
- The paid tiers (`test:e2e`, `EVALS=1`) were not run. Tier 1 only.
- `bun run test` (the full, non-Windows-filtered suite) has not been re-run post-build. Only
  `test:windows` is claimed.

---

## 10. Independent cross-model review — todo loop-001-5 (ACC-18)

| | |
|---|---|
| Implementer of loop-001-4 | **Claude Opus 5** (`claude-opus-5[1m]`), acting as the programme controller |
| Reviewer | **`Qwen/Qwen3.5-397B-A17B-FP8`** via opencode, ELM Proxy (Edinburgh) |
| Herdr agent | `syncreview`, kind `opencode`, pane `w5:p1`, session `ses_fc3051eb9ffeF1kWOsJo1IAvmO` |
| Duration | 1m 38s |
| Verdict | **PASS** |

The providers differ, which is the ACC-18 check.

**Deviation from the plan, recorded rather than smoothed over.** Todo loop-001-4 names its provider
as *"codex or opencode"*. The controller ran it instead. The reason is that the first two runs were
invalid (section 3) and diagnosing that — a missing build prerequisite, a fail-fast runner on the
control, five test files that do not exist at the pre-sync head — needed the controller's own view
of both trees. ACC-18 is not weakened by this: the reviewer is a different model from the
implementer either way, and a controller-implemented, worker-reviewed loop is the stricter
direction.

### What the reviewer was asked to do

Read the evidence file, then **independently verify five claims by running its own commands**, and
separately check whether any AAW-specific change had leaked onto a branch that is supposed to be a
pure sync.

### The reviewer's findings, and the controller's re-verification of them

| Claim | Reviewer | Controller re-ran it | Agree |
|---|---|---|---|
| C1 sync head = `upstream/main`, empty diff | CONFIRMED | `git diff --stat upstream/main sync/…` empty | yes |
| C2 tag is annotated, targets `a5dc03bd…`, not on origin | CONFIRMED | `cat-file -t` → `tag`; `rev-parse …^{commit}` → `a5dc03bd…`; tag object `7034809e18…` | yes |
| C3 nothing pushed | CONFIRMED | `ls-remote origin 'refs/heads/sync/*'` empty; `ls-remote --tags origin 'pre-upstream-sync-*'` empty | yes |
| C4 `build.test.ts:16` interpolates an unquoted path | CONFIRMED | matches section 4.5 | yes |
| C5 `jq` absent, Developer Mode value absent | CONFIRMED | `where.exe jq` not found; `reg query` → key/value not found | yes |
| No AAW-specific change on the branch | CONFIRMED — only the two untracked fixtures | matches section 8 | yes |

Every factual claim the reviewer made was re-derived by the controller and matched. This is the
phase-3 F3 discipline applied: a reviewer verdict is evidence only once the controller has checked
the claims underneath it.

### One operational note

The reviewer went **`blocked`** partway through, on an opencode permission prompt to read
`…\Advanced-AI-Workflows\.advanced-plans\evidence\*`. Reading programme state is explicitly
permitted — `docs/worktree-ownership.md` §2, *"A worker may read any of these"* — and the todo scopes
the reviewer to read-only, so **Allow once** was granted, not **Allow always**. The block was
detected by `agent wait --until blocked` and the question text was recovered with `agent read`,
exactly as the phase-3 pilot predicted for a `trust_directory` detection.

---

## 11. Control worktree removal, and a new finding

The `pilot/` branch had to be destroyed at the end of the loop that created it
(`docs/programme-git-policy.md` §2). Two things went wrong on the way, both worth recording.

### 11.1 The control worktree was dirty, on a line-ending artefact

```
$ git status --porcelain
 M gstack/llms.txt
```

A dirty worktree is never removed. But the modification was not real:

```
$ git diff --numstat -- gstack/llms.txt     (empty)
$ git ls-files --eol -- gstack/llms.txt
i/lf    w/lf    attr/                      gstack/llms.txt
```

The file has **no `.gitattributes` rule** covering it — the `attr/` column is empty — so under this
machine's `core.autocrlf=true` it is stat-dirty with identical content. The synced tree does not
show this, so upstream has since changed either the file or its attributes.

Restored with a **targeted** `git checkout -- gstack/llms.txt` (exit 0), not `git reset --hard`,
which is forbidden outright. `git status --porcelain` then returned empty.

### 11.2 F5 — closing the last pane of a Herdr workspace orphans the worktree

Phase 3's F2 taught that `herdr worktree remove` can fail on the final `rmdir` when an agent
process still holds the directory as its cwd, and that the cure is to close those panes. That
lesson was applied **too early** here: the pane was closed *before* attempting removal.

`w7:p1` was the only pane in workspace `w7`. Closing it destroyed the workspace, and Herdr then had
no handle on the worktree at all:

```
$ herdr worktree list   --workspace w7   → {"error":{"code":"workspace_not_found", …}}
$ herdr worktree remove --workspace w7   → {"error":{"code":"workspace_not_found", …}}
```

The directory and the Git worktree registration were both still present. Herdr had simply lost the
ability to address them.

Recovered with Git directly, and without any force:

```
$ git worktree remove 'C:/Users/mharvey2/Coding/aaw worktrees/gstack-presync-control'   exit=0
$ git branch -d pilot/gstack-presync-control
Deleted branch pilot/gstack-presync-control (was a5dc03bd).                              exit=0
```

Final state, verified:

```
$ git worktree list
C:/Users/mharvey2/Coding/gstack-fork                           a5dc03bd [main]
C:/Users/mharvey2/Coding/aaw worktrees/gstack-sync-2026-08-26  ad840054 [sync/upstream-2026-08-26]
$ git branch --list
* main
+ sync/upstream-2026-08-26
$ ls .git/worktrees
gstack-sync-2026-08-26
```

The directory is gone, the branch is gone, `-d` was used rather than `-D`, and nothing was forced.

**The rule this yields.** Attempt `herdr worktree remove` **first**, and close panes only if it
reports a failure. Closing the last pane first is not a safe precaution — it costs the Herdr-managed
removal path and forces a fall back to raw Git. Added to `docs/worktree-ownership.md` §4.
