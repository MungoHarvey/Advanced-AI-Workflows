---
phase: 5
title: "Superpowers Behavioural Port"
status: passed
gate: attempt-1 PASS (codex 91, code-review-agent 78, phase-goals-agent 84; 0 failed criteria)
commits: 74252ee..HEAD on docs/herdr-v0.2-import
generated: 2026-08-26
note: written by hand — platforms/python/handoff_digest.py does not exist in the installed Advanced Planning source
---

## What this phase did
Ported the four Superpowers behavioural intents into AAW **without patching the fork at all**.
All four (SP-1 spec location, SP-2 terminal-state routing, SP-3 AskUserQuestion, SP-4 companion
tools) are carried by an AAW-owned fenced block that the installer merges into the user's
`CLAUDE.md` and `AGENTS.md`. 2 loops, 11 todos. `git diff upstream/main..mirror/upstream-2026-08-26`
is empty — the measured patch is zero.

## State now
- **Phase 5 CLOSED**, gate passed on attempt 1. Programme pointer advanced to **phase 6**
  (Advanced Planning Multi-Runtime Adapters, planned, loops deferred).
- Controller branch `docs/herdr-v0.2-import` — pushed.
- Superpowers fork: `mirror/upstream-2026-08-26` prepared locally, zero-diff against upstream.
  `origin/main` still `fde9f97` and still carrying the old patch. **Not published.**
- `feat/aaw-packaging-repair` — pushed tip `360ab3c`, **already an ancestor of the
  controller branch**. `fix/install-audit-diverged-state` **does not exist**; this line
  was wrong when written and was corrected 2026-08-27. One local commit `3b19a49`
  (`%USERPROFILE%` path fix) is unpushed and in no branch.
- `main` @ `3422a8c`, tag `v0.1.0`.
- Suites green: packaging 4/4, idempotency 56/56.

## Key decisions / context
- **The block, not the fork, is the deliverable.** Established at the loop-001 design gate and
  it changed the phase's shape: two of the original success criteria were superseded by a
  written Amendment rather than quietly reinterpreted.
- **Every companion-tool route is gated on the manifest predicate**
  (`components["<name>"]["installed"] == true`) at the point of use, with a stated fallback, plus
  a default-deny catch-all so a route that ever forgets to say "when installed" fails safe.
- **The precedence claim is narrow.** The block outranks a *skill's* built-in default for exactly
  three things — a spec location, a terminal state, a question format — and never outranks the
  user's own writing outside the markers.
- **R3 was declined, not dropped.** The AskUserQuestion-naming finding was raised twice and
  declined twice, with the reason recorded both times: the line already leads with the generic
  harness wording and already carries a prose fallback.

## Errors & issues encountered
- **F1 was fixed as an instance when it was a class.** One route was gated; eight others were
  not, and the six acceptance rounds could not have caught it because every fixture had a
  well-formed manifest. The re-prove added a `broken-manifest` fixture — every sentinel on disk,
  manifest truncated — which is the discriminator that separates manifest-reading from
  filesystem-probing.
- **A stale tracked copy of the routing block survived at the repo root** for the whole phase,
  found only at the gate by the criteria-led reviewer. Removed. Its sibling
  `references/settings-snippet.json` was the same orphan and had simply not drifted yet.
- **Neither gemini nor cursor can be started unattended on this machine** — gemini has no stored
  API key, cursor raises its trust modal even in an ordinary long-used checkout, and both report
  `idle`/`interactive_ready` while sitting on the dialog. Recorded as B11 in
  `herdr-ops/FINDINGS.md`. The real rotate-the-reviewer fleet is codex, opencode and claude.
- **`herdr agent prompt` to codex pasted text into the composer without submitting it**, twice,
  stacking chips on retry. Recovery is `send-keys backspace ×N` → prompt → `send-keys enter`.
  Recorded as B10.
- **`/run-gate` calls three Advanced Planning modules absent from this checkout**
  (`codex_gate`, `install_audit`, `handoff_digest`), so aggregation, the drift preflight and this
  digest were done by hand again. Unchanged since phase 4.

## Open threads (not blocking phase 6)
- Adherence is now measured on **codex and claude** as well as opencode — three vendors,
  two instruction files, one of them against an actively contradicting global `CLAUDE.md`.
  It found two block defects, both fixed in `cd920df` post-gate. **cursor and antigravity
  remain unmeasured**: both refuse a fresh directory in print mode without an
  operator-granted flag (`--trust` / `--dangerously-skip-permissions`), which is the user's
  to give.
- Measure block adherence on **claude** and **codex** — every round so far is opencode only.
  Claude's half needs one trust dialog cleared per fresh worktree.
- Decide whether the acceptance fixtures become a tracked test under `tests/`. Until then the
  behavioural proofs are narrative, not re-derivable.
- Publish the mirror: `git push origin mirror/upstream-2026-08-26:main --force-with-lease`,
  in the superpowers repository. User's to run.
- Open **one** PR: `docs/herdr-v0.2-import` → `main` (50 commits, fast-forwardable).
  Land `3b19a49` onto it first — cherry-pick verified clean, drops raw `~/.claude`
  occurrences in the glue skill from 19 to 5.
- Re-sync the global `~/.claude` copy of `setup-with-claude` — its registered description still
  advertises four-tool integration including the deprecated Plannotator.
- Install `jq`, enable Windows Developer Mode, re-run the gstack suite to retire the phase-4
  waiver.
- Report `browse/test/build.test.ts:16` upstream to `garrytan/gstack` (unquoted `execSync`
  interpolation).
