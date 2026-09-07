# v0.2 controller baseline audit

**Collected:** 2026-08-26
**Controller checkout:** `C:\Users\mharvey2\Coding\Advanced-AI-Workflows`
**Checkout type:** normal checkout (not a worktree)
**Branch:** `docs/herdr-v0.2-import` @ `bdfaa29cdf78cec1eb94f91b9927caab0f2824c7`
**origin/main:** `3422a8c2da1764344c5992612c4c572ba61d7945` (branch is 1 commit ahead, unpushed)
**Working tree:** dirty — one untracked file, `find-files.js` (pre-existing user scratch, preserved, unrelated to programme files)

Supersedes the assumptions in `references/upstream-baseline-2026-08-26.json` where noted.
Written per Step 2 of `docs/herdr-kickoff-prompt.md`. No repository was modified to produce it.

> **Correction, 2026-08-26 (later the same day).** Sections 1.1 and 7 below state that Herdr
> reports every integration as `not installed` because `HOME`/`HOMEDRIVE` resolve to `M:\`. That is
> true but imprecise. Herdr honours `HOME` when it is set and falls back to `USERPROFILE` when it is
> not, so the failure is **shell-specific**: Windows PowerShell (`HOME` unset) was never affected;
> Git Bash (`HOME=/m/`) always was. The readings recorded below came from Git Bash. The findings
> and the fix still stand — see
> [`2026-08-26-phase-3-loop-001-environment-pin.md`](2026-08-26-phase-3-loop-001-environment-pin.md)
> §2. The text below is left as collected; evidence records are not rewritten after the fact.

---

## 1. Environment

| Item | Observed |
|---|---|
| OS | Microsoft Windows NT 10.0.26100.0 (Windows 11 Education) |
| PowerShell | 5.1.26100.8875 (**Windows PowerShell, not PowerShell 7**) |
| Herdr | 0.8.2, channel `stable`, server running |
| Herdr socket | `C:\Users\mharvey2\AppData\Roaming\herdr\herdr.sock` |
| `HERDR_SESSION` | not set (no named session selected) |
| Claude Code | 2.1.246 |
| Codex CLI | 0.146.0 |
| OpenCode | 1.18.23 |
| Cursor Agent CLI | **not installed** (`cursor-agent` not on PATH) |
| GitHub CLI | 2.96.0 |
| Node | v22.15.0 |
| Python | 3.12.10 |

### 1.1 Herdr integration status — a false negative, root-caused and fixable

As invoked normally, `herdr integration status` reports **every** integration as `not installed`:

```
claude:   not installed (M:\.claude\hooks\herdr-agent-state.ps1)
codex:    not installed (M:\.codex\herdr-agent-state.ps1)
opencode: not installed (M:\.config/opencode\plugins\herdr-agent-state.js)
cursor:   not installed (M:\.cursor\herdr-agent-state.ps1)
```

The reported paths are the cause, not the symptom. Re-running the identical command with
`HOME` / `HOMEDRIVE` / `HOMEPATH` pointed at the real profile gives the opposite result:

```powershell
$env:HOME="C:\Users\mharvey2"; $env:HOMEDRIVE="C:"; $env:HOMEPATH="\Users\mharvey2"
herdr integration status
```

```
claude:   current (v8)  (C:\Users\mharvey2\.claude\hooks\herdr-agent-state.ps1)
codex:    current (v8)  (C:\Users\mharvey2\.codex\herdr-agent-state.ps1)
opencode: current (v10) (C:\Users\mharvey2\.config/opencode\plugins\herdr-agent-state.js)
cursor:   current (v1)  (C:\Users\mharvey2\.cursor\herdr-agent-state.ps1)
```

**All four required integrations are already installed and current.** Nothing needs installing.
Workstream 0's integration criterion is an *environment resolution* problem, not a setup problem —
and the fix is confirmed to work. This is the single highest-value finding of the audit.

### 1.2 Split-brain home directory (BLOCKER, Workstream 0)

| Variable | Value |
|---|---|
| `USERPROFILE` | `C:\Users\mharvey2` |
| `HOMEDRIVE` / `HOMEPATH` | `M:` / `\` |
| `$HOME` (PowerShell) | `M:\` |
| `$HOME` (Git Bash) | `/m/` |

`M:\` is a **real redirected roaming profile**, not a phantom. Two parallel homes exist:

| Path | Contents | Used by |
|---|---|---|
| `C:\Users\mharvey2\.claude` | full install — 200+ skills, 19 commands, `settings.json`, plugins | Claude Code (authoritative) |
| `M:\.claude` | `skills\gstack` only — a stray misdeploy | nothing |
| `C:\Users\mharvey2\.gstack` | full — config, projects, analytics, profiles | gstack (authoritative) |
| `M:\.gstack` | `projects`, `sessions`, `slug-cache` | stray |

This is the same defect class the phase-2 gate caught (`3557bfa`, "wrong-HOME global deploy").
It is now confirmed to affect **Herdr itself**: Herdr resolves integrations against `HOMEDRIVE`/`HOMEPATH`
(`M:\`), so it cannot see the real Claude/Codex/OpenCode installs on `C:`.

**Consequence:** Workstream 0 cannot exit *as currently invoked*. Herdr cannot see any provider
integration, so `working` / `idle` / `blocked` detection is unverifiable from a default shell.
With the corrected environment (§1.1) all four integrations resolve and report `current`.

This validates design principle 8 and defect 4.1#5 — but the defect is broader than documented:
it is not only Git Bash `~`, it is the Windows profile itself, and it affects third-party tools
(Herdr), not just AAW's own installers. §4.1#5's remedy ("resolve to absolute native paths")
should therefore be restated as: **resolve global locations from `USERPROFILE`, never from
`HOME` / `HOMEDRIVE` / `HOMEPATH` / `~`** — and AAW's `doctor` should assert this and report the
`M:` / `C:` split explicitly rather than silently picking one.

### 1.3 Cursor runtime

Cursor IDE is installed (`C:\Users\mharvey2\AppData\Local\Programs\cursor`, `cursor.cmd` on PATH)
and `C:\Users\mharvey2\.cursor\` contains `herdr-agent-state.ps1`, `hooks.json`, `agents`, `plans`.
The **Cursor Agent CLI (`cursor-agent`) is not installed** — the Herdr hook exists but has no
runtime to drive. Cursor is the only one of the four target runtimes that is genuinely missing.

---

## 2. Repository audit

Fetched fresh. Full SHAs. Compared against `references/upstream-baseline-2026-08-26.json`.

### 2.1 Advanced AI Workflows — owned, MATCHES baseline

| Field | Value |
|---|---|
| Path | `C:\Users\mharvey2\Coding\Advanced-AI-Workflows` |
| origin | `https://github.com/MungoHarvey/Advanced-AI-Workflows.git` |
| origin/main | `3422a8c2da1764344c5992612c4c572ba61d7945` |
| Local branch | `docs/herdr-v0.2-import` @ `bdfaa29cdf78cec1eb94f91b9927caab0f2824c7` (+1, unpushed) |
| Tags | **none** |
| Clean | no (`find-files.js` untracked, pre-existing) |

Baseline recorded `3422a8c`; that is still `origin/main`. The extra local commit `bdfaa29`
("docs: organise v0.2 Herdr documentation set + refresh ROADMAP") is the v0.2 doc import and is
not yet pushed.

**No tags exist on this repository.** There has never been a released version. `v0.1` and `v0.2`
exist only as ROADMAP prose.

### 2.2 Advanced Planning — owned, MATCHES baseline

| Field | Value |
|---|---|
| Path | `C:\Users\mharvey2\Coding\advanced-planning` |
| origin | `https://github.com/MungoHarvey/advanced-planning.git` |
| Branch / head | `main` @ `02b4b86e020bcaccc843228603bf6911450fc2d2` |
| Tag at head | `v0.16.0` (tags v0.12.0–v0.16.0 present) |
| VERSION file | `0.16.0` |
| Upstream | none |
| Clean | no — untracked `setup-antigravity.js` (pre-existing, preserved) |
| Depth | full (171 commits) |

**Correction to the design's Workstream 2 premise.** The design (§7.1) proposes creating a
`core/` + `platforms/` portable layout. That layout **already exists**:

```
core/       agents  constraints.json  schemas  skills  state
platforms/  claude-code  cowork  python
setup/      claude-code  cowork
```

`core/skills/` holds 9 host-neutral skills. `platforms/claude-code/` holds 8 agents, 14 commands,
hooks, settings, and an installer. So Workstream 2 is **not** a from-scratch restructure — it is
"add `codex`, `opencode`, `cursor` alongside the existing `claude-code` and `cowork` platforms,
and add the CI path audit". `docs/adapting-to-new-platforms.md` already exists as the contract.

### 2.3 gstack — local checkout wrong; **fork re-cloned and baseline CONFIRMED**

#### 2.3.1 Resolution

The fork was cloned fresh, full depth, to `C:\Users\mharvey2\Coding\gstack-fork` (2026-08-26).
The pre-existing dirty `Coding\gstack` checkout was left untouched. Against the fresh clone every
baseline claim verifies **exactly**:

| Claim | Baseline | Verified |
|---|---|---|
| Fork head | `a5dc03b…` | `a5dc03bdd64124b302cb56927f0866edc0c11879` ✓ |
| Upstream head | `ad84005…` | `ad8400543cd9ce8d07641362db48d44a95417e33` ✓ |
| Divergence (upstream-only / fork-only) | 89 / 3 | `89  3` ✓ |
| Fork-only commits are merges only | yes | `a5dc03bd`, `973fedc8`, `58479465` — all merge commits ✓ |
| No net fork tree patch | yes | `git diff <merge-base> origin/main` is **empty** ✓ |

Merge base is `029356e1f0693f22cb1fa4524c9b0f28ceab5a1b` and **is an ancestor of `upstream/main`**,
so the fork is cleanly fast-forwardable to current upstream. The fork carries nothing worth keeping;
the design's "replace the fork tree with current upstream" strategy holds without qualification.

**Workstream 1A gstack is unpaused.** Base the sync branch on `gstack-fork`, not `Coding\gstack`.

#### 2.3.2 The misleading local checkout (unchanged, for the record)

| Field | Baseline expected | `Coding\gstack` as found |
|---|---|---|
| origin | `MungoHarvey/gstack.git` (fork) | **`garrytan/gstack.git` (upstream)** |
| upstream remote | `garrytan/gstack.git` | **absent** |
| Head | fork `a5dc03b…` | **`9fd03fae9e74f5daa7a138366aca8f86c7367c5c`** |
| Head version | — | `v1.58.4.0` |
| Upstream head | `ad84005…` (`v1.69.0.0`) | not fetchable from this checkout |
| Depth | full | **shallow, depth 1 (1 commit)** |
| Clean | required | **no** — ` M gstack/llms.txt`, `?? scripts/build-windows.js` |

`C:\Users\mharvey2\Coding\gstack` is **not the fork**. It is a shallow, depth-1, dirty clone of
public upstream at `v1.58.4.0` — which is also *older* than the `v1.69.0.0` the baseline recorded
as upstream. The `MungoHarvey/gstack` fork is not checked out anywhere on this machine.

`C:\Users\mharvey2\Coding\gstack` must not be used for sync work: it is a shallow, depth-1, dirty
clone of *public upstream* at `v1.58.4.0` — older than the `v1.69.0.0` upstream the baseline
recorded, and with no fork remote at all. It appears to be a scratch/build checkout (it carries
uncommitted `gstack/llms.txt` edits and an untracked `scripts/build-windows.js`). Left as found.

Note also that the working gstack install used day-to-day is `~/.claude/skills/gstack`
(v1.60.1.0 per the global CLAUDE.md), which matches neither checkout nor the baseline. Three
different gstack versions are in play on this machine.

### 2.4 Superpowers — not present locally; **fork re-cloned and baseline CONFIRMED**

There was **no Superpowers checkout on this machine**, and no `superpowers` plugin installed. Only
the individual skills were present, deployed loose into `C:\Users\mharvey2\.claude\skills\`:
`brainstorming`, `using-superpowers`, `writing-plans` — the two patched files plus one sibling,
copied out of their repository.

The fork was cloned fresh, full depth, to `C:\Users\mharvey2\Coding\superpowers` (2026-08-26).
Every baseline claim verifies **exactly**:

| Claim | Baseline | Verified |
|---|---|---|
| Fork head | `fde9f97…` | `fde9f972a2a49fcaa116f53d59444f002589c34a` ✓ |
| Upstream head | `b36e082…`, v6.3.0 | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`, `git describe` → `v6.3.0` ✓ |
| Divergence | 241 / 4 | `241  4` ✓ |
| Net patch paths | 2 skill files | `skills/brainstorming/SKILL.md` (+61/−10), `skills/using-superpowers/SKILL.md` (+22/−0) ✓ |

Merge base `f2cbfbefebbfef77321e4c9abc9e949826bea9d7`. **Workstream 1A Superpowers is unpaused.**

#### 2.4.1 Behaviour matrix — the four intents in the fork patch

Recovered from `git diff <merge-base> origin/main`. These are what a re-port must preserve:

| # | Intent | Where | Detection used | Verdict |
|---|---|---|---|---|
| SP-1 | Design doc saves to `.advanced-plans/specs/` when AP present, else upstream `docs/superpowers/specs/` | `brainstorming` step 6 + Documentation | `.claude/skills/phase-plan-creator/SKILL.md` exists | **port** — core AAW routing |
| SP-2 | Terminal state invokes `phase-plan-creator` when AP present, else `writing-plans` | `brainstorming` flow graph + Implementation | same | **port** — core AAW routing |
| SP-3 | Use `AskUserQuestion` for every clarifying question | `brainstorming` process | none | **do not port** — host-generic UX, not AAW-specific; propose upstream instead |
| SP-4 | "Companion Tools" section recommending Advanced Planning **and Plannotator** | `using-superpowers` | `.claude/commands/plannotator-annotate.md` | **port AP half only** — Plannotator half is deprecated (§6.1) |

Two problems block a naive replay of these files:

1. **Detection is Claude-only.** All three probes are `.claude/…` paths, which design §7.3 forbids in
   host-neutral core. A re-port needs host-neutral detection (an installation manifest, per §4.1#3).
2. **Upstream has moved underneath the patch.** Current upstream `brainstorming/SKILL.md` now has a
   "Three Paths" section (line 22) that did not exist at the merge base, and its flow graph and
   Implementation section have been rewritten. Confirmed by inspection: upstream contains **zero**
   occurrences of `advanced-planning` or `plannotator` anywhere under `skills/`.

This is exactly the case the design anticipated — replaying the stale files would silently destroy
the upstream three-path router. It also strengthens the design's stated preference: SP-1, SP-2 and
the AP half of SP-4 should move into **AAW-owned routing**, letting the Superpowers fork become a
pure mirror with zero patch.

### 2.5 Plannotator — MATCHES baseline exactly

| Field | Value |
|---|---|
| Path | `C:\Users\mharvey2\Coding\plannotator` |
| origin | `https://github.com/MungoHarvey/plannotator.git` |
| Branch / head | `main` @ `4db7fcc5dabb3136da45afb301e0d354a213f555` (v0.19.21) |
| Local vs origin/main | `0 0` — identical |
| Upstream `backnotprop/plannotator` HEAD | `b381ecbe1200b07db8c050715c0f2c035a44b73a` = tag `v0.27.8` |
| Fork-only commits | 0 (clean ancestor) |
| Clean | yes |
| Depth | full (632 commits) |

Also installed: Claude plugin `plannotator@plannotator` v0.15.5 (user scope), CLI at
`C:\Users\mharvey2\AppData\Local\plannotator\plannotator`, and three commands in
`~/.claude/commands/` (`plannotator-annotate`, `plannotator-last`, `plannotator-review`).

Note the three-way version spread: fork `0.19.21`, installed plugin `0.15.5`, upstream `0.27.8`.

---

## 3. AAW packaging defects — root cause confirmed

Design §4.1 defect 1 (`gstack-to-plans/SKILL.md` documented but untracked) is confirmed, and the
root cause is now identified precisely. `.gitignore` contains:

```
.claude/*
!.claude/skills/
.claude/skills/*
!.claude/skills/setup-with-claude/
```

The whitelist admits **only** `setup-with-claude/`. Every other skill under `.claude/skills/` is
excluded by construction, so `gstack-to-plans/` could never be tracked.

**The source is recoverable.** A deployed copy exists at
`C:\Users\mharvey2\.claude\skills\gstack-to-plans\SKILL.md` — 90 lines, 3912 bytes, mtime
2026-06-16, frontmatter and body intact, matching the contract described in README/SETUP/ROADMAP.
Workstream 1B can restore from this rather than rewriting from the contract.

Defect 4.1#3 also confirmed: this checkout has a populated `.advanced-plans/` (state, phases 1–2,
specs, gate-verdicts, closeout) which under the current detection rule reads as "Advanced Planning
installed" regardless of whether an adapter is present.

---

## 4. Baseline deltas summary

| Repository | Baseline status | Verdict |
|---|---|---|
| Advanced AI Workflows | `3422a8c` | **match** (+1 unpushed local commit `bdfaa29`) |
| Advanced Planning | `02b4b86`, v0.16.0 | **match** — but `core/`+`platforms/` already exist, reducing WS2 scope |
| gstack | fork `a5dc03b` / upstream `ad84005` | **match, after re-cloning the fork.** 89/3, no net patch, ff-able. Local `Coding\gstack` was the wrong repository |
| Superpowers | fork `fde9f97` / upstream `b36e082` | **match, after cloning the fork.** 241/4, patch = the two named skill files |
| Plannotator | fork `4db7fcc` / upstream `b381ecb` | **match** — clean ancestor, ff still available |

**Net verdict: the recorded baseline was accurate in every particular.** Nothing upstream or in the
forks had moved. The two apparent discrepancies were entirely artefacts of the *local working copies* —
one wrong repository, one absent — and both are resolved by the fresh clones. No design target
needed changing, and no workstream remains paused on baseline grounds.

### 4.1 Checkouts to use for Workstream 1A

| Repository | Use this path | Do not use |
|---|---|---|
| gstack | `C:\Users\mharvey2\Coding\gstack-fork` (fork + `upstream` remote, full depth) | `Coding\gstack` — upstream, shallow, dirty |
| Superpowers | `C:\Users\mharvey2\Coding\superpowers` (fork + `upstream` remote, full depth) | — |
| Plannotator | *deprecated — see §6.1* | — |

## 5. Workstream 0 exit-gate status: NOT MET, but closer than expected

| Gate criterion | Status |
|---|---|
| Herdr stable installed natively on Windows | met (0.8.2, server running) |
| Integrations for claude/codex/opencode/cursor | **installed and current** — but invisible unless `HOME` is corrected (§1.1) |
| Cursor runtime available | **not met** — `cursor-agent` CLI not installed (IDE and hook are) |
| `working` / `idle` / `blocked` reported correctly | **untested** — the Step 4 pilot has not been run |
| Recorded repository heads | met (this document) |
| Branch/tag/push policy | **not set** — repository has no tags and no release process |

Only three things stand between here and a Workstream 0 exit: pin the environment fix, install
`cursor-agent` (or drop Cursor from the v0.2 runtime set), and run the Step 4 disposable pilot.

---

## 6. Impact of the two requested scope changes

Both requested by the user on 2026-08-26; neither is in the authoritative design spec. Recorded
here as pending amendments, not yet applied.

### 6.1 Deprecate Plannotator from this project

Plannotator is referenced **183 times across 21 tracked files**. The heaviest are `SETUP.md` (25),
the design spec (23), `install-plannotator.md` (21), `ARCHITECTURE.md` (17), and
`setup-with-claude/SKILL.md` (15).

It is not merely documented — it is **load-bearing** in the v0.2 design:

- design §7.4 makes Plannotator the per-host **human review gate**, with a fallback table for all
  four runtimes;
- ROADMAP Workstream 2 exit gate requires "per-host human-review fallback text";
- ROADMAP Workstream 3 requires "runtime-specific Plannotator fallbacks";
- design §3 non-goals explicitly forbid *claiming* a review path that upstream does not provide.

Removing Plannotator therefore removes the mechanism that satisfies design principle 9 ("human
review at irreversible boundaries"). **A replacement gate must be named before the deprecation can
be specified**, otherwise v0.2 ships with an unenforced review boundary. Note that ACC-18 already
requires a cross-model gate reviewer, which is a candidate replacement independent of Plannotator.

Deprecation also simplifies the programme: Workstream 1A drops from three fork syncs to two, and
the paused gstack + Superpowers discrepancies become the only 1A blockers.

### 6.2 Start versioning on GitHub

The repository has **no tags and no release history**. Advanced Planning, by contrast, already tags
(`v0.12.0`–`v0.16.0`) and carries a `VERSION` file and `CHANGELOG.md`.

To start versioning, AAW needs the artefacts it currently lacks: a `VERSION` file, a `CHANGELOG.md`,
a tag for the already-shipped v0.1 state, and a documented release procedure. The design's
Workstream 5 already calls for "release tags plus the compatibility manifest point at the exact
tested commits" — so this is bringing forward and formalising an existing v0.2 requirement rather
than adding new scope.

The open decision is whether the v0.1 tag is applied retrospectively to `3422a8c` (the closeout
commit that completed v0.1) or whether versioning starts fresh at v0.2.0.

---

## 7. HOME split — blast-radius investigation

Requested before deciding how far to take the fix. Read-only; nothing was changed.

### 7.1 Which resolver each tool follows

| Follows `HOME`/`HOMEDRIVE` (→ `M:\`) | Follows `USERPROFILE` (→ `C:\Users\mharvey2`) |
|---|---|
| Git (config), OpenSSH, Git Bash, R, zsh, vim, pnpm, uv | Claude Code, Codex, Cursor, Herdr *config*, gstack |

Herdr straddles the two: its socket and config live under `AppData\Roaming` on `C:`, but its
**integration probes resolve from `HOME`** — which is why it looked uninstalled (§1.1).

### 7.2 Per-item impact of repointing `HOME` to `C:\Users\mharvey2`

| Item | On `M:` | On `C:` | Impact of the move |
|---|---|---|---|
| `.gitconfig` | yes | yes | **none — byte-identical** (`diff` clean) |
| `.ssh/` keys | `id_ed25519` | `id_ed25519` (same fingerprint `SHA256:FseJy7…`) **plus** `github_ed25519`, `authorized_keys`, `sockets`, `ssh_key_priv/pub` | **none — C: is a strict superset** |
| `.ssh/config` | github.com, eddie, qwasar | same three **plus** `git.ecdf.ed.ac.uk`, `ServerAliveInterval` | **improvement — C: is more complete**; both reference identities by absolute `C:` paths already |
| `.claude/` | `skills\gstack` stray only | full install | **improvement** |
| `.gstack/` | `projects`, `sessions`, `slug-cache` | full incl. config, analytics, profiles | **improvement**, but M-side `projects`/`sessions` would need merging |
| `.uv-venvs/` | `cell_state_characterisation` | same name present | none apparent |
| `.Rprofile` | yes | **no** | orphaned — but it already hardcodes `C:/Users/mharvey2/R/library`, so copying it across is trivial |
| `.Rhistory`, `.profile`, `.viminfo` | yes | no | orphaned — cosmetic, copy across |
| `.pnpm-store/` | yes | no | orphaned — pnpm rebuilds it automatically |

**Total real breakage: none.** Five orphaned items, all trivially copied or self-rebuilding.

### 7.3 Evidence this has already bitten

`M:\.ssh\config` carries a hand-written comment:

> ```
> # Git-Bash here runs with HOME=/m/, so it reads THIS file, not
> # C:/Users/mharvey2/.ssh/config. Without this block ssh offers the Eddie key to
> # GitHub and the push fails with "Permission denied (publickey)".
> ```

The split has already cost a debugging session and been papered over by duplicating config into
`M:`. It is a standing tax, not a hypothetical one. The phase-2 gate finding (`3557bfa`) was the
second instance; Herdr's invisible integrations are the third.

### 7.4 The argument against a machine-wide change

`M:` is a mapped network home drive on a `@ed.ac.uk` managed Windows machine. That mapping and the
`HOMEDRIVE`/`HOMEPATH` pair are almost certainly set by Group Policy at logon. A local change would
likely be **silently reverted at the next logon or policy refresh**, producing intermittent
breakage that is far worse than the current stable split — the programme would then have runs that
pass and runs that fail with no code change between them.

This is not a claim that it is impossible, only that it cannot be verified from inside the session
and would need to be confirmed against IT policy before being relied upon.

### 7.5 Recommendation

**Scoped fix, plus make the split visible.** Three parts:

1. Pin `HOME` / `HOMEDRIVE` / `HOMEPATH` to `USERPROFILE` in the launcher that starts Herdr sessions
   and any AAW-dispatched agent. Verified working (§1.1) — all four integrations report `current`.
2. Add a `doctor` assertion: resolve every global path from `USERPROFILE`, never `HOME`/`~`, and
   **report the split explicitly** rather than silently choosing. This generalises design §4.1#5
   from "Git Bash `~`" to "any HOME-following resolver, including third-party tools".
3. As a one-off convenience, copy the five orphan items to `C:` so both roots stay usable.

This is durable against GPO, reversible, and turns the defect into something the tooling detects
instead of something a gate has to catch after the fact. It leaves the machine-wide question open
for you to raise with IT separately, without blocking the programme either way.
