# Cursor adapter: the decision, and what the CLI's real behaviour costs it

**Date:** 2026-09-01
**Todo:** `loop-005-1` (phase 6, provider: controller, read-only + evidence)
**Base:** `loop-004-5`
**cursor-agent version measured:** `2026.08.25-3e8eec8`

Written before `loop-005-2` builds the adapter, so it is designed for the CLI as it
behaves rather than as its documentation implies. The programme has already been caught
out by cursor's state reporting once.

---

## Check 1 — the phase-3 decision is live

`.advanced-plans/PLANNING.md:25`, under `resolved_decisions`:

> `"Cursor runtime: install cursor-agent — already bundled by the Cursor IDE, shimmed onto PATH (2026-08-26)"`

Confirmed by reading it, not assumed. The phase plan's *Blocked-by* is discharged.
`cursor-agent --version` answers `2026.08.25-3e8eec8`, so the runtime is present as the
decision describes.

**But the same file carries an open item that qualifies it**, at `PLANNING.md:40-46`:

> *"Neither gemini nor cursor can be started unattended on this machine — ... cursor
> raises its workspace-trust modal even in an ordinary long-used checkout, not just in a
> fresh worktree. Both report idle/interactive_ready while sitting on the dialog.
> Recorded as B11 in herdr-ops/FINDINGS.md. Consequence for the programme:
> rotate-the-reviewer has a real fleet of two, codex and opencode, until a human clears
> those dialogs once."*

**Half of that open item is now obsolete and half of it still stands**, and separating
the two is the point of this note.

- **Obsolete:** *"until a human clears those dialogs once"*. A later measurement
  (2026-08-28, recorded in the user's global `CLAUDE.md`) established that `--trust`
  clears the workspace gate from the command line in an untrusted worktree, bringing the
  agent up `idle` with no modal. The gate is cleared by a **flag**, not by a human. So
  cursor is available to `loop-005-3` and to rotate-the-reviewer, and B11's stated
  consequence — a reviewer fleet of two — no longer follows.
- **Still stands, and unfixed by any flag:** *"Both report idle/interactive_ready while
  sitting on the dialog."* No flag repairs state reporting. This is the constraint the
  adapter and its fixture run must actually be designed around.

## Check 2 — what unreliable state reporting costs an unattended run

Two measured behaviours, both from the programme's own record:

1. **`blocked` detection is selective.** cursor sat at a full-screen *"Workspace Trust
   Required"* modal while herdr reported `idle`, `interactive_ready: true`, with
   `state_change_seq` unchanged across the whole modal → cleared transition.
2. **When it does report `blocked`, it lags** — still `blocked` after a shell-approval
   dialog had been answered and the screen showed "Running".

**The consequence for `loop-005-3` is specific: `agent_status` is not a completion
signal for a cursor pane, in either direction.** A run that gates on `idle` can collect
from an agent that has done nothing, and a run that waits for `blocked` to clear can
wait past the point the work finished. Both failure modes are silent.

This is the programme's central defect class in a new coat — a check whose subject is a
**reported state** rather than a fact read off the machine. The fixture run must
therefore take its completion signal from **artefacts on disk** (the phase directory,
the loop file, the emitted envelope) and read the pane, not from the lifecycle state.
`herdr pane read` before dispatching or collecting, per the standing rule.

## Check 3 — `--trust` grants no tools; a write needs more

Confirmed against `cursor-agent --help` at the version above. These are four separate
flags, and conflating them is what would break the fixture run:

| Flag | What it actually does |
|---|---|
| `--trust` | *"Trust the current workspace without prompting"* — clears the **workspace** gate only |
| `-f, --force` | *"Force allow commands unless explicitly denied"* |
| `--yolo` | *"Alias for `--force` (Run Everything)"* |
| `--sandbox <mode>` | *"Explicitly enable or disable sandbox mode (overrides config)"*, choices `enabled` / `disabled` |

So the todo's premise is correct as stated: `--trust` clears directory trust and grants
**no** tool permission. A run that only passes `--trust` will clear the modal and then
stall on the first non-allowlisted command, which under `approvalMode="allowlist"`
permits little more than `Shell(ls)`.

**Two things this check did not anticipate, both found by reading the help rather than
the note:**

- **`--mode` has no write value.** Its only choices are `plan` (*"read-only/planning
  (analyze, propose plans, no edits)"*) and `ask` (*"Q&A style ... (read-only)"*). There
  is no `--mode write`. A **writing** run cannot be constrained by mode at all, which is
  why the permission question lands on `--force` rather than on mode selection.
- **`--sandbox enabled` is a third option the todo's checks omit.** It sits between
  read-only and Run Everything, and is the narrower instrument for a fixture run that
  must write inside a scratch directory. It is **not yet measured on this machine** —
  the flag's existence is established, its behaviour is not.

### What `loop-005-3` needs, and why

`loop-005-3` runs the fixture programme *on Cursor*: one phase, one loop, one validated
external task. Creating a phase directory and a loop file are **writes**, so a read-only
mode cannot satisfy it.

**Recommended invocation, narrowest first:**

```
cursor-agent --trust --sandbox enabled --model cursor-grok-4.6-medium ...
```

falling back to `--trust -f` only if `--sandbox enabled` is measured to block the writes
the fixture legitimately needs. `-f`/`--yolo` is *Run Everything* and should not be the
first choice for a run that has a scratch directory as its entire legitimate blast
radius. Whichever is used, **the fixture must run in a scratch fixture project outside
both checkouts**, which `loop-005-3`'s `allowed_paths` already requires.

Per the standing speed-tier rule, the model must not carry a `-fast` suffix.

---

## What this costs the adapter

Three design constraints for `loop-005-2`, each traceable to a measurement above:

1. **The installer must not depend on cursor's lifecycle state**, because that state is
   unreliable in both directions. Any readiness or completion check reads the filesystem.
2. **Trust and permission are separate concerns and need separate handling** — `--trust`
   for the workspace, `--sandbox`/`--force` for tools. An adapter that treats "trusted"
   as "can act" will stall.
3. **`--mode` cannot be used to make the adapter safe**, since neither of its two values
   permits writes. Safety comes from the sandbox flag and the scratch directory, not from
   mode.

## What was NOT verified here

- **`--sandbox enabled` has not been run.** Its existence and its two choices are read
  off `--help`; its actual effect on a writing fixture run is unmeasured, and
  `loop-005-3` should measure it rather than assume the recommendation above holds.
- **The `--trust` result is inherited, not re-run today.** It was measured 2026-08-28 in
  an untrusted worktree and recorded in the global `CLAUDE.md`. This note relies on that
  record; it did not reproduce it.
- **B11 in `herdr-ops/FINDINGS.md` has not been amended.** This note establishes that
  half of it is obsolete; updating that file is outside this todo's `allowed_paths` and
  is carried.

## Carried

- Amend B11 in `herdr-ops/FINDINGS.md`: the human-clears-the-dialog consequence is
  superseded by `--trust`; the state-reporting half stands.
- `PLANNING.md:40-46`'s open item says the reviewer fleet is two. With `--trust` it is
  three. The `open_items` entry should be corrected when a controller-owned write to
  `PLANNING.md` next happens.
