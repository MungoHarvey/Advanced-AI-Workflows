---
phase: 3
title: "Safety Baseline and Herdr Pilot"
status: passed_with_open_item
gate_verdict_ref: (none — cross-model gate reviewer not yet run; see Opened)
anchor_sha: 5944375
end_sha: (this commit)
loop_count: 3
created: 2026-08-26T07:00:00Z
---

## Goals met

- **HOME split fixed, and diagnosed correctly.** `tools/herdr-env.sh` and `tools/herdr-env.ps1` pin
  `HOME`/`HOMEDRIVE`/`HOMEPATH` from `USERPROFILE` for the child process. `--assert` / `-Assert` is
  a doctor check scoped to the four target runtimes, proven passing and proven failing on
  deliberate drift. The baseline audit's diagnosis was corrected: Herdr prefers `HOME` when set and
  falls back to `USERPROFILE`, so the failure was shell-specific (Git Bash broken, PowerShell never
  affected) — `.advanced-plans/evidence/2026-08-26-phase-3-loop-001-environment-pin.md` §2.
- **Machine-wide override written** to the user registry as the second half of the "Both" decision.
  Unverified until next logon — see Opened.
- **Five orphan items copied** from `M:` byte-identically, sources intact.
- **Cursor runtime available.** `cursor-agent` was already bundled by the Cursor IDE; no remote
  installer was run. Shimmed for Windows shells (`.cmd`) and, after loop 002 found the gap, for Git
  Bash (extensionless POSIX wrapper). The four-runtime target set stands; no design amendment.
- **Herdr pilot: all ten kickoff Step 4 items exercised** —
  `.advanced-plans/evidence/2026-08-26-phase-3-loop-002-herdr-pilot.md`. Worktree on a path
  containing a space; codex and opencode both detected; `working` / `idle` / `done` / `blocked`
  observed and timestamped; blocking question text preserved; trivial edit committed and
  independently re-verified from the controller; clean worktree removed without `--force`; branch
  never merged and never pushed, then deleted.
- **Cross-model review demonstrated on real output (ACC-18).** codex `gpt-5.6-terra medium`
  implemented; opencode `Qwen/Qwen3.5-397B-A17B-FP8` reviewed; verdict PASS; both of the reviewer's
  factual claims matched the controller's independent verification. This is the mechanism that
  replaced Plannotator.
- **Policy written.** `docs/programme-git-policy.md` names every branch and tag phases 4 to 7 will
  use, the per-repository check command, commit authorship, and the three human gates.
  `docs/worktree-ownership.md` states one owner per checkout, the controller-sole-writer rule, and
  the removal procedure. The forbidden-path list is now byte-identical across all three `loops.md`
  headers and the ownership document, verified programmatically.
- **Versioning live on GitHub.** `VERSION`, `CHANGELOG.md`, `docs/releasing.md`; `v0.1.0` annotated
  at `3422a8c` and pushed with `docs/herdr-v0.2-import`, both under explicit authorisation.

## Exit gate

**PASS with one open item.** Step 4's stop condition — *do not proceed to real sync work if Herdr
cannot reliably create worktrees, detect the chosen agents, or preserve the session* — is satisfied
outright on worktrees and detection. Session preservation is evidenced but not proven (ACC-10, see
Opened). Phase 4 may proceed.

## Findings carried into phase 4 and beyond

- **F1 — a linked worktree is not an isolation boundary.** codex's trust prompt said in terms that
  trusting the worktree applies to the repository root, and its sandbox could not commit because a
  linked worktree's Git metadata lives in the parent repo. The controller/worker split is enforced
  by policy and review, not by the worktree mechanism. Recorded in `docs/worktree-ownership.md` §3.
- **F2 — `herdr worktree remove` reports failure after completing the destructive part.** It
  returned `worktree_remove_failed` having already deleted every file and deregistered the Git
  worktree, failing only on the final `rmdir` of the empty directory that two agent processes held
  as their cwd. Never answer that error with `--force`. Recorded in `docs/worktree-ownership.md` §4.
- **F3 — the case that earns the central rule.** Asked how many lines `ROADMAP.md` has, the agent
  ran `Get-Content | Measure-Object -Line`, got 98, and answered "98 lines" with no caveat. Ground
  truth is 139; that pipeline silently drops the 41 blank lines. The agent went cleanly to `done`.
  Only controller-side re-derivation caught it.
- **F4 — ACC-10 is not exercisable from the CLI.** See Opened.
- **Commit authorship.** Worker agents inherit the human's Git identity with no agent marking.
  `docs/programme-git-policy.md` §5 now requires the model/session trailer.

## Deferred

- Phase 6 to 9 remain planned at phase level only, deliberately not decomposed. The AAW registry
  and CLI (phase 8) are explicitly not to be started early.

## Opened

- **ACC-10 unproven.** Herdr 0.8.2's session verbs are `list`, `attach`, `stop`, `delete` — no CLI
  detach. `stop` would have killed the controller's own Claude agent; `attach` would have seized
  its stdin. Closes with one manual `Ctrl+B`, `Q` and reattach by the operator, confirming this
  pane and its session id survive.
- **Machine-wide HOME override unverified.** `HOMEDRIVE=M:` is injected at logon from the AD
  home-folder attribute, not from any registry setting, so the user-level override competes with
  something reasserted every sign-in. After the next logon, `tools/herdr-env.sh --assert` must pass
  regardless; bare `herdr integration status` reveals which half won. Nothing breaks either way.
- **No gate verdict recorded for this phase.** The cross-model gate reviewer was demonstrated
  inside loop 002 but has not been run as the phase-3 boundary gate. Phase 4's boundary is the
  first place `/run-gate` runs for real.
- **Prompt delivery is not perfectly reliable.** One `agent prompt` to a codex agent resting in
  `done` landed as keystrokes and opened its `/hooks` screen; two `esc` presses recovered it.
  Automation should read the pane back and confirm the prompt reached the composer.
