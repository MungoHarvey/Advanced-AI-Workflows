---
phase: 4
title: "gstack Sync and AAW Packaging Repair"
status: passed
gate: attempt-2 PASS (codex 93, code-review-agent 95, phase-goals-agent 87; 0 critical)
commits: 060dc27..HEAD (controller) + e508203..3b19a49 (feat/aaw-packaging-repair)
generated: 2026-08-26
note: written by hand — platforms/python/handoff_digest.py does not exist in the installed Advanced Planning source
---

## What this phase did
Brought the gstack fork current with upstream as a pure sync, and repaired the AAW packaging
defect that made the documented Quick Start unverifiable. 3 loops, 15 todos. A fresh clone of
`feat/aaw-packaging-repair` now contains every install source the docs name, and installation
state is machine-readable rather than guessed from a directory's existence.

## State now
- **Phase 4 CLOSED**, gate passed on attempt 2. Programme pointer advanced to **phase 5**
  (Superpowers Behavioural Port, 2 loops decomposed, not started).
- Controller branch `docs/herdr-v0.2-import` — pushed.
- `feat/aaw-packaging-repair` @ `3b19a49` — pushed, **not merged, no PR opened**. Both are
  separate authorisations and neither has been given.
- `sync/upstream-2026-08-26` and tag `pre-upstream-sync-2026-08-26` — local only.
- `main` @ `3422a8c`, tag `v0.1.0`.
- Packaging suite green: 13/13, 24/24, 21/21, 43/43, 4/4.

## Key decisions / context
- **The gstack upstream-suite criterion is waived**, not met. 7 failures, all attributed away
  from the sync (3 × missing `jq`, 2 × Developer Mode off, 1 Git Bash flake, 1 upstream bug). No
  retry can close it; environment remediation and an upstream fix can.
- **The installer's global paths were fixed, not waived** (`3b19a49`). Everything the skill
  resolves for itself now comes from `%USERPROFILE%`; raw `~` survives only inside the fenced
  commands Step R2 hands the user to paste into their own shell.
- The defect was inherited from before the phase, not introduced by it — `e508203` has both
  sites. Phase 4 added the rule; the gate finished applying it.

## Errors & issues encountered
- **Attempt 1 failed**, and two of three reviewers missed the installer defect entirely because
  they checked `.aaw/detect.py` and stopped. Cross-model agreement is only evidence when the
  models looked in different places — name the file next time.
- **`git add -A` swept an unrelated doc edit into the gate commit.** Split back out into
  `306d15c` and `fc4e8a8` before anything was pushed.
- **`/run-gate` calls three Advanced Planning modules that do not exist** in the installed source
  (`codex_gate`, `install_audit`, `handoff_digest`). Aggregation, the drift preflight and this
  digest were all done by hand. The command's own "do not hand-derive the pass/fail result" could
  not be followed.

## Open threads (not blocking phase 5)
- Install `jq`, enable Windows Developer Mode, re-run the gstack suite — then the waiver can be
  retired rather than carried.
- Report `browse/test/build.test.ts:16` upstream to `garrytan/gstack`.
- A PR and a merge for `feat/aaw-packaging-repair`; a GitHub Release from `v0.1.0`.
- Remove the `feat/aaw-packaging-repair` Herdr worktree (workspace `wA`) — try
  `herdr worktree remove` first, per F5.
- Operator manual steps still outstanding: ACC-10 (`Ctrl+B`, `Q`, reattach) and the post-logon
  `tools/herdr-env.sh --assert`.

## Resume seed
Phase 4 is closed and compacted. Phase 5 is the Superpowers behavioural port — port the Advanced
Planning half of `dfd7ff5` from current `upstream/main` and drop the Plannotator half. Its loops
are decomposed but no todos are populated; `/next-loop` is the natural next command. Nothing is
mid-flight.
