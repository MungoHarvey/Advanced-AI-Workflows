# v0.2 controller baseline audit

**Collected:** 2026-08-26
**Controller checkout:** `C:\Users\mharvey2\Coding\Advanced-AI-Workflows`
**Checkout type:** normal checkout (not a worktree)
**Branch:** `docs/herdr-v0.2-import` @ `bdfaa29cdf78cec1eb94f91b9927caab0f2824c7`
**origin/main:** `3422a8c2da1764344c5992612c4c572ba61d7945` (branch is 1 commit ahead, unpushed)
**Working tree:** dirty — one untracked file, `find-files.js` (pre-existing user scratch, preserved, unrelated to programme files)

Supersedes the assumptions in `references/upstream-baseline-2026-08-26.json` where noted.
Written per Step 2 of `docs/herdr-kickoff-prompt.md`. No repository was modified to produce it.

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

### 2.3 gstack — DISCREPANCY, Workstream 1A gstack is BLOCKED

| Field | Baseline expected | Actually observed |
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

Per the kickoff prompt discrepancy rule, gstack is **paused**. It cannot be synced, and the
"89 upstream-only / 3 fork-only / no net tree patch" claim cannot be re-verified from here.
Note also that the working gstack install used day-to-day is `~/.claude/skills/gstack`
(v1.60.1.0 per the global CLAUDE.md), which matches neither this checkout nor the baseline.

### 2.4 Superpowers — DISCREPANCY, not present

There is **no Superpowers checkout on this machine**. Neither `C:\Users\mharvey2\Coding\superpowers`
nor any sibling path exists, and there is no `superpowers` plugin installed.

What *is* installed are the individual skills, deployed loose into `C:\Users\mharvey2\.claude\skills\`:
`brainstorming`, `using-superpowers`, `writing-plans` — i.e. exactly the two patched files from the
fork (`skills/brainstorming/SKILL.md`, `skills/using-superpowers/SKILL.md`) plus `writing-plans`,
copied out of their repository.

Workstream 1A Superpowers is **paused**: the fork must be cloned before the behaviour matrix can be
written, and the deployed loose skills must be diffed against fork and current upstream to recover
the real AAW behavioural intent.

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
| gstack | fork `a5dc03b` / upstream `ad84005` | **DISCREPANCY — paused.** Local checkout is upstream, shallow, dirty, at older `v1.58.4.0`; fork not present |
| Superpowers | fork `fde9f97` / upstream `b36e082` | **DISCREPANCY — paused.** No checkout exists; only loose deployed skills |
| Plannotator | fork `4db7fcc` / upstream `b381ecb` | **match** — clean ancestor, ff still available |

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
