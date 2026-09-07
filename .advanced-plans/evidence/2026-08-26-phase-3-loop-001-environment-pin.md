# Phase 3 loop 001 — environment pin

**Collected:** 2026-08-26
**Loop:** `.advanced-plans/phases/phase-3/loops.md` → `ralph-loop-001`
**Decisions by:** repository owner, 2026-08-26
**Status:** all four todos complete

---

## 1. Decisions recorded (todo loop-001-1 and loop-001-4)

| Decision | Chosen | Reason given |
|---|---|---|
| HOME split fix | **Both** — machine-wide user-level override *and* the scoped launcher plus doctor assertion | Convenience of a single global fix, with the launcher as the guard that catches a silent revert |
| Cursor runtime | **Install `cursor-agent`** | Keeps the four-runtime target set intact; no design amendment needed |

Both were `gate: human` todos. Neither was self-approved.

---

## 2. A correction to the baseline audit's diagnosis

The audit (§1.1, §7) recorded that Herdr reports every integration as `not installed` because
`HOME`/`HOMEDRIVE` resolve to `M:\`. That is true but imprecise, and the imprecision matters
because it changes what the fix has to cover.

**Herdr honours `HOME` when `HOME` is set, and falls back to `USERPROFILE` when it is not.**
So the failure is *shell-specific*, not machine-wide:

| Shell | `HOME` | `herdr integration status` |
|---|---|---|
| Windows PowerShell 5.1 | unset | **correct** — resolves under `C:\Users\mharvey2` |
| Git Bash | `/m/` | **broken** — probes `M:\.claude\`, `M:\.codex\`, … |

Verified both directions in the same session:

```
# Git Bash, ambient (HOME=/m/)
claude:   not installed (M:\.claude\hooks\herdr-agent-state.ps1)
codex:    not installed (M:\.codex\herdr-agent-state.ps1)
opencode: not installed (M:\.config/opencode\plugins\herdr-agent-state.js)
cursor:   not installed (M:\.cursor\herdr-agent-state.ps1)

# Git Bash, through tools/herdr-env.sh
claude:   current (v8)  (C:\Users\mharvey2\.claude\hooks\herdr-agent-state.ps1)
codex:    current (v8)  (C:\Users\mharvey2\.codex\herdr-agent-state.ps1)
opencode: current (v10) (C:\Users\mharvey2\.config/opencode\plugins\herdr-agent-state.js)
cursor:   current (v1)  (C:\Users\mharvey2\.cursor\herdr-agent-state.ps1)
```

The audit's PowerShell reading of `M:\` paths came from a Git Bash invocation. PowerShell was
never affected.

**Consequence:** the Git Bash launcher is the load-bearing half of the fix, because this project's
agents routinely shell out through Bash. The PowerShell launcher is the belt to its braces.

### `HOMEDRIVE` does not come from the registry

Also established, and relevant to how much the machine-wide half can promise:

```
User-level    HOME / HOMEDRIVE / HOMEPATH : all unset before this loop
Machine-level HOME / HOMEDRIVE            : all unset
AD account "Home directory"               : \\cmvm.datastore.ed.ac.uk\cmvm\smgphs\users\mharvey2
```

`HOMEDRIVE=M:` and `HOMEPATH=\` are injected **by the logon process** from the Active Directory
home-folder attribute. They are not a registry setting anyone configured. A user-level override is
therefore competing with something reasserted at every logon, and whether it wins cannot be tested
without a fresh logon — a child process inherits its parent's environment block, not the registry.

This is not a reason the "Both" decision was wrong; it is the reason the launcher half is what
makes the outcome deterministic. **The machine-wide half is unverified until next logon.** The
doctor assertion is what will tell you if it lost.

---

## 3. Orphan items copied (todo loop-001-3)

Copied, never moved. `M:` was not modified.

| Item | Source bytes | Destination bytes | Match | Still on `M:` |
|---|---|---|---|---|
| `.pnpm-store` | 16,370,612 | 16,370,612 | ✓ | ✓ |
| `.Rprofile` | 554 | 554 | ✓ | ✓ |
| `.Rhistory` | 5 | 5 | ✓ | ✓ |
| `.profile` | 26 | 26 | ✓ | ✓ |
| `.viminfo` | 1,241 | 1,241 | ✓ | ✓ |

Nothing is lost when `HOME` stops pointing at `M:`.

---

## 4. The launcher and the doctor assertion (todo loop-001-2)

| Artefact | Purpose |
|---|---|
| `tools/herdr-env.sh` | Git Bash launcher — the one that matters. Pins `HOME`/`HOMEDRIVE`/`HOMEPATH` from `USERPROFILE` for the child process only |
| `tools/herdr-env.ps1` | PowerShell equivalent, for symmetry and for callers that never touch Bash |

Both accept `--assert` / `-Assert`: run the status check, and exit non-zero if any **target**
runtime reports `not installed` or resolves outside the profile.

### The assertion is scoped to the target set, deliberately

The first version failed, correctly, and taught something. Herdr 0.8.2 ships integrations for
**17** runtimes — `pi`, `omp`, `copilot`, `devin`, `droid`, `kimi`, `kilo`, `hermes`, `qodercli`,
`qwen`, `mastracode`, `grok`, `antigravity-cli`, and the four we use. `not installed` is the
*correct* answer for the thirteen we do not use, so an assertion that fails on any occurrence of
that string fails permanently and is worthless. It now checks only
`claude`, `codex`, `opencode`, `cursor`.

Incidental finding: `antigravity-cli: current (v2)` is also installed
(`C:\Users\mharvey2\.gemini\config\hooks\herdr-agent-state.ps1`). Not a v0.2 target; noted only so
it is not mistaken for drift later.

### Proven in both directions

| Test | Expected | Result |
|---|---|---|
| Bash, ambient `HOME=/m/` | all four `not installed` | as expected — the bug reproduces |
| Bash, via `herdr-env.sh` | all four `current` | ✓ |
| Bash, `herdr-env.sh --assert` | exit 0 | ✓ `ASSERTION PASSED` |
| PowerShell, `herdr-env.ps1 -Assert` | exit 0 | ✓ `ASSERTION PASSED` |
| PowerShell, `-Assert` with the profile root deliberately pointed at `M:\` | exit **1** | ✓ `ASSERTION FAILED`, naming all four runtimes |

The negative test is the one that matters: a guard that never fails is not a guard.

---

## 5. Cursor runtime resolved (todo loop-001-4)

**No remote installer was run.** `cursor-agent` was already present on this machine — the Cursor
IDE bundles a complete CLI inside its extension storage and simply does not put it on `PATH`:

```
C:\Users\mharvey2\AppData\Roaming\Cursor\User\globalStorage\
  anysphere.cursor-agent-worker\agent-cli\.local\share\cursor-agent\
  versions\2026.08.11-e8db854\cursor-agent.cmd
```

Verified working before anything was changed: `--version` → `2026.08.11-e8db854`, exit 0.

Made discoverable with a shim at `C:\Users\mharvey2\.local\bin\cursor-agent.cmd`. That directory
was **already** on the user `PATH`, so no `PATH` modification was needed.

The shim resolves the **newest** version directory at run time rather than pinning
`2026.08.11-e8db854`, so a Cursor upgrade cannot silently leave it pointing at a stale build. It
resolves from `USERPROFILE`, not `HOME`.

Verified after: `Get-Command cursor-agent` → the shim; `cursor-agent --version` → exit 0;
`cursor-agent --help` → the real CLI usage text, not just a version string.

**The four-runtime target set stands.** No design amendment is needed and no document claiming
four runtimes has to change.

---

## 6. Workstream 0 exit-gate status after this loop

| Criterion | Before | After |
|---|---|---|
| Herdr installed natively | met | met |
| Integrations for all four runtimes | installed but invisible | **met** — and now assertable |
| Cursor runtime available | not met | **met** — bundled CLI, shimmed onto `PATH` |
| `working` / `idle` / `blocked` reported correctly | untested | **still untested** — loop 002 |
| Recorded repository heads | met | met |
| Branch/tag/push policy | not set | **partly** — `docs/releasing.md` covers tags and push; loop 003 covers branch naming |

Remaining before the Workstream 0 exit gate: **loop 002 (the disposable pilot)** and
**loop 003 (the policy documents)**.

---

## 7. Open item

The machine-wide `HOME`/`HOMEDRIVE`/`HOMEPATH` override is written to the user registry but
**unverified until the next logon**, because it competes with the AD home-folder attribute. After
your next sign-out and sign-in, run:

```bash
tools/herdr-env.sh --assert     # must pass regardless
herdr integration status        # tells you whether the machine-wide half won
```

If the second command still shows `M:\` paths, the AD attribute won and the launcher is doing all
the work — which is the outcome the scoped fix was designed for. Nothing breaks either way.
