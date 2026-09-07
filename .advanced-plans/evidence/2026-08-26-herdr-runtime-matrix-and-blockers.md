# Herdr runtime matrix and configuration blockers

**Collected:** 2026-08-26 · **Herdr:** 0.8.2 · **Controller:** Claude Opus 5
**Scope note:** this was *not* run as an AAW loop. It is a controller-side
configuration test of the Herdr execution layer, collected outside the loop
machinery, and is filed here because its findings are inputs to phase 6.
**Companion:** [herdr pilot](2026-08-26-phase-3-loop-002-herdr-pilot.md), whose
findings F1–F4 this extends rather than repeats.

**Paid inference: ~zero turns.** claude and cursor never completed a turn before
being blocked at startup; every completed turn ran on free opencode/Qwen. Three
independent subagent critiques of the original test plan are the reason — they
identified that codex + opencode behaviour was already established by the pilot,
and that `gemini`/`agy` are not in the target set (`tools/herdr-env.sh:39`,
`TARGETS="claude codex opencode cursor"`), which removed most of the intended spend.

---

## Runtime adapter matrix — Contracts 4 and 5

Probe: read a canary phrase from an injected `SKILL.md` (Contract 4, skills
directory), then `git add` + `git commit` from inside the linked worktree
(Contract 5, checkpoints). **Every commit was re-derived controller-side with
`git log` / `git status` / `git diff`; no worker claim was accepted as evidence.**

| Runtime | C4 skill load | C5 commit in linked worktree | `blocked` detection | Unattended-capable |
|---|---|---|---|---|
| **opencode** (Qwen3.5 397B) | ✅ canary correct | ✅ `c6f99d5`, tree clean | n/a — never blocks | ✅ **the only one** |
| **claude** | ✅ canary correct | ✅ `18d7013` | ✅ correct, two channels | ❌ trust dialog per new worktree |
| **cursor** (`--model auto`) | ✅ canary correct | ✅ `2b92522` | ⚠️ selective and laggy | ❌ trust modal undetected, then approval per shell command |
| **codex** | not retested | ❌ **fails** — pilot F1 | ✅ per pilot | ❌ cannot commit from a worktree |

**Contract 5 is a per-runtime sandbox property, not a worktree limitation.**
Three of four runtimes commit from a linked worktree without difficulty. Codex
cannot, because a linked worktree's git metadata lives in the parent repo's
`.git/worktrees/`, outside its sandbox (pilot F1). **AAW's checkpoint contract
therefore cannot assume a codex worker self-checkpoints** — codex needs either a
sandbox exception or a controller-side commit step.

**Attribution is inconsistent.** Cursor self-attributes with a
`Co-authored-by: Cursor <cursoragent@cursor.com>` trailer; the pilot found codex
commits inherit the human's identity with no agent marking. `docs/programme-git-policy.md`
should normalise this rather than leave it per-runtime.

---

## Blockers

### B1 — `agent start` reporting ready does not mean promptable
`agent start` returned `agent_started`, `agent_status: "idle"`,
`interactive_ready: true` for opencode; the immediately following prompt was
rejected with `agent_prompt_stalled` ("no observed state change within 5000 ms").
The same agent prompted later worked first time.

Initially misdiagnosed as a multi-line/bracketed-paste fault. **Controlling for it
disproved that** — a multi-line prompt to the now-warm agent succeeded. Readiness
is the variable; the TUI was still painting its splash screen.

*Action:* the `start → prompt` step needs a readiness gate. Retry on
`agent_prompt_stalled` is sufficient (attempt 1 stalled, attempt 2 succeeded).

### B2 — cursor's `blocked` detection is selective and laggy
| Situation | Detected |
|---|---|
| Startup "Workspace Trust Required" modal | ❌ reported `idle`, `interactive_ready: true`; `state_change_seq` stayed **86 across the whole modal→cleared transition** |
| Mid-turn shell-approval dialog | ✅ `blocked` (seq 111, 117) |
| Immediately after that dialog was answered | ❌ still `blocked` at seq 111 while the screen showed "Running" |

*Action:* a cursor state is unproven — read the pane before dispatching. This is
the false-negative direction, where a controller dispatches into a dialog box.

### B3 — every fresh worktree triggers a first-run trust dialog
claude and cursor both block on workspace trust in a new worktree; opencode does
not. Since AAW creates **a worktree per loop**, this fires on every claude/cursor
worker start. Clearing it needs `agent send-keys`, i.e. a human.

### B4 — the state bus cannot support concurrent workers *(by inspection)*
`.advanced-plans/state/loop-ready.json` and `loop-complete.json` are single-slot
and carry **no `run_id`, `worker_id`, `repository`, or `branch`** — only
`loop_name`. Concurrent workers overwrite each other and are unattributable,
*regardless of git worktree isolation*. This contradicts `.aaw/project.toml`'s
`max_parallel_writers = 3`, and matches `next-loop.md:389` ("sequentially — never
concurrently").

**Git isolation was never the constraint on AAW parallelism; the state bus is.**
Run-scoped state (`runs/<run-id>/`, spec §9.1) belongs in Workstream 2, not 4.

### B5 — permission rules covered only one tool
Every rule in the controller's `settings.json` targeted `Bash` or `Read`;
`PowerShell` appeared in none, so destructive herdr denies were bypassable by tool
choice. Confirmed fixable: the CLI's own settings schema refers to *"every
Bash/PowerShell allow rule"*, so `PowerShell(...)` rules are a supported mechanism.

### B6 — a controller cannot clean up after itself
`herdr worktree remove` and `herdr workspace close` denied outright leaves
workspaces accumulating, and **contradicts this programme's own teardown order**
in `docs/worktree-ownership.md:100-121`. Note pilot F2: `worktree_remove_failed`
is reported *after* the destructive part completes, so `--force` is the wrong
reflex on that error.

### B7 — under auto mode the `ask` tier does not ask
Two different `ask`-tier rules, four invocations, zero prompts, all executed.
Cause established from the CLI's settings schema: **`defaultMode: "auto"`** routes
decisions to a classifier that silently approves what it judges safe instead of
surfacing the `ask` rule. (`skipAutoPermissionPrompt` is unrelated — it records
*"whether the user has accepted the auto mode opt-in dialog"*.)

*Consequence:* in an auto-mode controller only `deny` is load-bearing. Any AAW
safety control expressed as `ask` is decorative there. Controls that must hold
belong in `deny`, or the controller must run outside auto mode.

---

## Method note

Three predictions made during this session were wrong and were caught only by
controlling the variable: multi-line prompts (B1), cursor's detection being absent
rather than selective (B2), and the cause of B7. Each was corrected by isolating
one factor, not by reasoning further. This is the same discipline pilot F3 records
for agent output, applied to the orchestration layer itself.
