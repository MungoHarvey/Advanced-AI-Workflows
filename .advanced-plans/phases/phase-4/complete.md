---
phase: 4
title: "gstack Sync and AAW Packaging Repair"
status: passed
gate_verdict_ref: .advanced-plans/gate-verdicts/phase-4-attempt-2-*.json
gate: attempt-2 PASS — codex 93, code-review-agent 95, phase-goals-agent 87; zero critical findings
gate_attempt_1: FAIL — two criteria; one fixed (3b19a49), one waived by human decision
anchor_sha: 060dc27
end_sha: (this commit)
loop_count: 3
todos: 15/15
created: 2026-08-26T10:40:00Z
---

## Goals met

- **gstack is current with upstream and carries no product change.** `sync/upstream-2026-08-26`
  was cut from a freshly fetched `upstream/main`, and the empty-net-patch claim was re-verified
  the correct way — `git diff <merge-base> origin/main` rather than `git diff upstream/main
  origin/main`, the comparison that produced a false alarm during the baseline audit. Evidence:
  `.advanced-plans/evidence/2026-08-26-phase-4-loop-001-gstack-sync.md`.
- **The glue skill is tracked, not merely present.** `.gitignore:12` was the sole cause and the
  file had never been tracked at all. The whitelist was widened by explicit skill directory
  rather than by removing the `.claude/skills/*` exclusion.
- **A fresh clone now contains every documented install source.** `tests/packaging/`
  test-fresh-clone.sh clones the branch into a temporary directory and checks every source the
  README, SETUP and the setup skill name. It was proven to have teeth twice: it fails at
  `--ref e508203` (exit 1, 6 missing sources) and passes at HEAD.
- **Installation state is knowable by a machine.** `.aaw/installed.schema.json` with a 24-fixture
  corpus and a two-validator test; `.aaw/detect.py`, which stops a stale `.advanced-plans/`
  reading as an installed component (ACC-02); `tools/aaw-audit.py`, non-interactive with
  meaningful exit codes and both environmental inputs passed as arguments.
- **Install, refresh and uninstall are safe to repeat.** A 43-check idempotency test over a
  temporary project and a fake profile — install ×3, uninstall, reinstall, a hand-edited
  CLAUDE.md, an existing glue skill, a would-be-emptied array, and a settings file holding
  nothing of ours. ACC-16 holds; the live profile is never read.
- **Every path the installer resolves for itself comes from `%USERPROFILE%`.** Closed at the gate
  — see below.

Suite at the end of the phase: fresh-clone 13/13, manifest-schema 24/24, audit 21/21,
idempotency 43/43, overall 4/4, exit 0. Re-run independently by the gate's code reviewer rather
than taken from the loop record.

## Exit gate

**PASS on attempt 2**, unanimous across two model families, zero critical findings, no
criterion-level disagreement beyond codex's read-only sandbox deferring what the in-house agents
could execute.

**Attempt 1 FAILED**, and the failure was worth having. Two distinct criteria were unmet:

1. **"The upstream suite passes."** Found by all three reviewers. `bun run test:windows` exits 1
   with 7 failing tests. **Waived by human decision on 2026-08-26**, recorded inline in `plan.md`
   beside the criterion it waives. Every failure was re-run in isolation and attributed: 3 need
   `jq` on PATH, 2 need Windows Developer Mode (symlink privilege), 1 is a Git Bash `fork()`
   flake, 1 is a genuine upstream defect at `browse/test/build.test.ts:16` that predates the sync.
   None is attributable to the sync, and the branch carries no net patch, so re-running loop 001
   in this environment reproduces the same result — which is why every reviewer independently left
   `loops_to_revert` empty. On attempt 2 all three were told to evaluate the criterion honestly
   regardless of the waiver, and all three did: two recorded it `failed`, one `waived`. None
   recorded it met.

2. **"No global path in the installer resolves through `~` or `HOME`."** Found by
   `code-review-agent` alone. The other two checked `.aaw/detect.py`, which is clean, and never
   opened the installer. `setup-with-claude/SKILL.md` Step 1 defines `<profile>` as
   `%USERPROFILE%` and says *"Not `HOME`, and never `~`"*, and Steps 6 and U7 then resolved global
   paths through a raw `~` — a copy and a *delete*. **Fixed rather than waived**, in `3b19a49`.

   The reviewer's attribution was wrong and the controller corrected it: `git show
   e508203:` has both sites already, with 23 raw `~/.claude` occurrences at the phase base
   against 19 before the fix. Phase 4 inherited the defect; what it added was the rule that names
   it. That changed the remedy from "revert a regression" to "finish the rule you wrote".

## Findings carried forward

- **Two reviewers agreeing is not two reviewers checking.** codex and `phase-goals-agent` both
  marked the global-path criterion met on attempt 1, from the same partial evidence — they read
  the detector and not the installer. Convergence between models is only worth something when
  they looked in different places. Attempt 2 named the file to check, and both then found what
  the third had found.
- **A waiver has to be visible to the reviewer without being an instruction to it.** The waiver
  is recorded in the plan, which reviewers treat as untrusted data, *and* restated in the
  invocation prompt, which is the trusted channel — with an explicit direction to evaluate the
  criterion honestly anyway. What the waiver governs is what the controller does with a finding,
  not what the finding is.
- **The `<profile>` rule now lives where it can be broken.** The carve-out for user-pasted
  commands is marked in place at Step R2, and "The tilde trap" names which steps resolve for
  themselves. A rule stated four hundred lines from the step that violates it is a rule that gets
  violated.

## Reconciliation with the plan

The `## Key Deliverables` table names two evidence files that were produced under different
names: `<date>-gstack-sync.md` and `<date>-packaging-repair.md`, against the actual
`2026-08-26-phase-4-loop-001-gstack-sync.md` and — for the idempotency work, which loop 002
explicitly deferred — `2026-08-26-phase-4-loop-003-installation-state.md`. Both gate attempts
flagged it at info level. The substance exists; only the filenames the plan predicted are wrong.
`plan.md` was left exactly as the reviewers saw it rather than edited after the fact, and the
reconciliation is recorded here, which is what this artefact is for.

The plan's `## Explicitly NOT included` says *"Pushing anything. Every branch in this phase stays
local until the external-write gate."* Both branches were pushed during the phase under an
explicit human gate. `code-review-agent` flagged the literal scope deviation at info level and
was right to; the gate existed and was used, and the deviation is disclosed rather than quiet.
**No pull request has been opened and nothing has been merged. Both remain separate
authorisations that have not been given.**

## Opened

- **The gstack suite still does not pass**, and the waiver does not make it pass. Closing it needs
  `jq` installed, Windows Developer Mode enabled, and an upstream fix for
  `browse/test/build.test.ts:16` (unquoted `execSync` interpolation — breaks on any checkout path
  containing a space, worth reporting to `garrytan/gstack`).
- **`references/install-gstack.md:16`** gives only a `~`-based install command with no Windows
  PowerShell variant, unlike its sibling reference files. Pre-existing, non-blocking, and outside
  the criterion's letter because it is a user-run command.
- **`feat/aaw-packaging-repair` is pushed but not merged.** Until it lands, `main` still ships an
  incomplete install set, and `README:7` and `SETUP.md:9` each need one further edit when it does.
- **`sync/upstream-2026-08-26`** and the tag `pre-upstream-sync-2026-08-26` are local only.
- **The Advanced Planning source does not have the modules `/run-gate` calls.**
  `platforms.python.codex_gate`, `platforms.python.install_audit` and
  `platforms/python/handoff_digest.py` are absent from `~/Coding/planning/advanced-planning`, so
  verdict aggregation, the install-drift preflight and the handoff digest were all done by hand
  this gate. Worth closing before the next one, since "do not hand-derive the pass/fail result"
  is the command's own instruction and it could not be followed.
- **The glue skill still has zero AskUserQuestion callouts** although phase 1 accepted it on
  having them at three ambiguous branches. Committed verbatim to preserve provenance; the
  packaging test checks presence, not correctness, so it cannot catch this.
