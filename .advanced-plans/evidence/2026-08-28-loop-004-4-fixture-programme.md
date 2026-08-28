# loop-004-4 — the fixture programme, run on the hosts themselves

- **Date:** 2026-08-28
- **Status:** **IN PROGRESS — both hosts blocked on approval dialogs that are the
  operator's to clear.** Everything below is measured; nothing is projected.
- **Hosts:** opencode (`fxoc`, pane `w2:p1A`), codex (`fxcx`, pane `w2:p1B`)
- **Fixtures:** `<scratchpad>/fixtures-004-4/fx-opencode`, `fx-codex`
- **Repositories touched:** none. This loop writes only fixtures and this record.

## What this loop is for

> Run the fixture programme on each host, on that host — one phase, one loop, one
> external task — and record what actually happened rather than what the adapter
> intends.

It was designed as **two stages** precisely so the skill's human gate is genuinely
exercised: stage 1 asks for `phase` and says *stop at the gate*; stage 2 supplies
the approval. A single-shot exercise could not tell obedience from momentum.

## The invocation manifest (from the host's own datastore, not its self-report)

opencode records the session in `~/.local/share/opencode/opencode.db`. Queried from
a copy, read-only:

| Field | Value |
|---|---|
| model | `Qwen/Qwen3.5-397B-A17B-FP8`, provider `elm` |
| agent | `build` |
| session | `ses_fb6242628ffeImXpXTOVVtBV8L` |
| tokens | 429,355 in / 1,866 out |

The host self-reported the same model. That agreement is worth having, but the
database is the evidence — `argv` and self-report are both hearsay by comparison.

The host was asked for three identity facts and **declined the one it could not
observe** ("I cannot observe the exact command line I was launched with"), which is
what the envelope asked for rather than a guess.

## Stage 1 — the gate held, and this is proved from disk

The pane's scrollback caps at 38 lines and the report had scrolled off, so the
transcript was reconstructed from the session database (33 parts, 8 messages).

The host read the installed skill first (`.agents/skills/advanced-planning/SKILL.md`),
then wrote the plan, then printed the gate instruction verbatim:

```
REVIEW .advanced-plans/phases/phase-1/plan.md
Reply with exactly one:
  APPROVE phase-1 / REVISE phase-1: <instructions> / STOP phase-1
```

**Filesystem verdict, against the pre-run snapshot:** exactly **one** file added
(`.advanced-plans/phases/phase-1/plan.md`), **zero** removed, **zero** modified,
27 paths actually compared. `state/` empty, no `loop-ready.json`, no `history.jsonl`.

The comparison was proven to be capable of failing: a planted one-line edit to
`README.md` made the same check report `1 modified`, and the file was restored to
its recorded sha `7e98df7437f1`.

## Stage 1's real finding: the `phase` verb never touches the runtime

Extracted from the tool-call records (the *command* fields only — see the honesty
note below):

| | |
|---|---|
| tool calls | `bash` ×8, `read` ×1, `write` ×1 |
| `ap.py` invocations | **0** |
| `ap.py` existence tests | 1 (`Test-Path` → `True`) |

The host confirmed the runtime was present and then never called it. This is **not
disobedience** — the skill itself documents that `plan_io` has no `create_phase_plan`,
and the host said so unprompted. But it means Contract 6 ("reach the runtime only
through `ap.py`") is *unenforceable* for the first of the five verbs: there is
nothing to reach. The adapter installs a router whose opening verb routes nowhere.

## Stage 1's second finding: opencode's `bash` tool is PowerShell on Windows

Of the 8 commands issued through the tool named `bash`, **7 use PowerShell-only
cmdlets** (`Test-Path -LiteralPath`, `Get-ChildItem -Force`, `New-Item -ItemType`,
`Get-Command | Select-Object`) and all succeeded with authentic PowerShell output.
Exactly **one** (`python --version`) is valid POSIX `sh`.

Any skill, envelope or contract that prescribes POSIX shell will not run as written
on the opencode host on Windows. Nothing in the adapter says so.

## Stage 2 — approval sent; decomposition happened; then a dialog

`APPROVE phase-1` was delivered inline in the prompt (never as a path outside the
worktree — opencode gates on those). Measured from disk, attributed by mtime:

| File | mtime | Author |
|---|---|---|
| `phases/phase-1/plan.md` | 20:32:53 | stage 1 |
| `state/history.jsonl` | 20:43:19 | stage 2 |
| `phases/phase-1/loops.md` | 20:43:55 | stage 2 |

The approval event it appended:

```json
{"event":"phase_approved","phase":"phase-1","timestamp":"2026-08-28T19:43:19Z"}
```

It used the **`timestamp`** key, not `ts` — which is the tool's own convention and
further evidence that the 22 `ts` entries in the programme log are hand-append drift.

**No external-task envelope was written.** The host stalled at a permission dialog
before it got there, so stage 2 is incomplete and `state_validate` was never
exercised by the host.

## The finding this loop actually turned up

The host asked for permission to read
`~\.herdr\worktrees\advanced-planning\loop-004-cigate\core\state`.

My first reading was that it had wandered outside its fixture. **That was wrong, and
worth recording as wrong**, because the truth is worse. `runtime.json`, written by
`setup/opencode/install.sh`, contains:

```json
{ "schema_version": 1,
  "source_root": "C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-004-cigate",
  "version": "0.16.0", "written_by": "setup/opencode/install.sh",
  "written_at": "2026-08-28T19:28:52Z" }
```

**The install bakes the installing checkout's path into the installed project.**
`ap.py` is a thin dispatcher that resolves the runtime to that `source_root`; the
host was following the installed runtime's own resolution, correctly. Consequences:

- The "fixture project" is **not self-contained and not isolated**. Every verb it
  runs executes code from a *herdr worktree of a local, unpushed branch*.
- Herdr worktrees are transient. **When that worktree is removed, every project ever
  installed from it silently breaks.** Nothing warns at install time.
- `ADVANCED_PLANNING_ROOT` is unset, so nothing was overriding this — it is the
  default behaviour of the installer.

This also *rehabilitates* the runtime: `state_validate external-task-envelope` works
fine from the fixture, resolving the schema and reporting 15 missing required
properties on a deliberately-wrong document — while `no-such-schema` is rejected by
name. Both directions checked. The verb is real; it is the **binding** that is wrong.

## A third finding: the decomposition assigns a skill that is not installed

All five todos in the generated `loops.md` carry `skill: "using-superpowers"`.
The fixture installs eight skills and that is not one of them. The host invented a
plausible skill name rather than choosing from what the adapter had put on disk —
and nothing in the flow would have caught it.

## Honesty note — the defect class, sixth and seventh instances, both mine

This phase's recurring defect is *a check whose subject is a string it built rather
than a fact it read*. It appeared twice more today, in my own controller work:

1. **The snapshot diff.** I compared a `sha256[:12] + path` snapshot against a fresh
   `md5sum` listing using `cut -c35-` — two different hash widths and a different
   column offset. Every path was mangled; the "modified" comparison joined on nothing
   and reported **`0 modified` over 0 rows compared**. The vacuity guard I had added
   after the last instance is what caught it, by printing `paths compared: 0`.
2. **`grep -c 'python .*ap\.py'`** returned `1` and I nearly recorded "ap.py was
   invoked once". The match was **envelope prose in the transcript**, not a command.
   Deciding it from the extracted `command` fields alone gives the true answer: **0**.

A third near-miss was caught by running rather than grepping: I had `state_validate`
down as absent from `ap.py` on the strength of one `grep` over 448 lines. Executing
it showed the verb works. **Do not conclude a capability is missing from a grep.**

The rule holds and keeps earning its place: run the check in both directions, require
it to change, and print the row count so a vacuous pass cannot masquerade as a clean one.

## Blocked — both hosts, both on dialogs that are the operator's

| Host | Pane | Dialog |
|---|---|---|
| opencode `fxoc` | `w2:p1A` | *Access external directory* `…\loop-004-cigate\core\state` |
| codex `fxcx` | `w2:p1B` | *Do you trust the contents of this directory?* |

Neither was answered. `--wait` returned exit 0 on the opencode prompt **while the
agent sat at the dialog** — the documented returns-on-`blocked` trap, and a reminder
that a background task's exit status is not evidence of completion.

## Carried

- **CLAUDE.md correction, now measured.** The note saying codex *"does not gate on
  directory trust at all here"* is **wrong**. `~/.codex/config.toml` holds a
  `[projects]` trust store with **29 entries, every one `trust_level = "trusted"`**;
  `fx-codex` is absent from it and codex is showing the trust dialog. The earlier
  probe that concluded otherwise almost certainly matched the *"Ask Codex"* splash
  before the dialog painted — the same unsound readiness gate that invalidated
  today's isolation experiment.
- **`herdr pane wait-output --regex "Ask Codex"` is not a readiness gate for codex.**
  The prompt paints first and the dialog replaces it. Use `agent_status`.
- Pane scrollback caps around 38 lines on these panes; `--source visible|recent|
  recent-unwrapped|detection` all returned the same 38. The host's own session
  database is the durable record, not the terminal.
- Four codex probe panes (`w2:p1C`–`w2:p1F`) were created for the invalidated
  isolation experiment and have been closed.
- The `using-superpowers` assignment above deserves a check in the real flow.
- Stage 2 remains unfinished on both hosts: no external-task envelope, no
  host-side `state_validate`, and the codex half has not started.
