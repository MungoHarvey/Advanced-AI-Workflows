# The shared Python runtime is unreachable from an installed project

Phase 6, ralph-loop-001, todos 1–3. Recorded 2026-08-27.

Advanced Planning's slash commands shell out to a shared Python runtime —
`python -m platforms.python.<module>` — for state preparation, history, gates, audits and
versioning. Neither installer ships `platforms/python/`. Every one of those invocations therefore
fails in any project that is not the source checkout.

**Provider note.** loop-001-1 assigns codex and loop-001-2 assigns opencode, both in Herdr
worktrees. Neither was used: the controller derived both directly. For a grep and a reproduction
that is a defensible substitution — independence buys nothing on a mechanical inventory — but it
is a substitution, and loop-001-5's independent review is now the only cross-model check in this
loop. Do not let it be skipped.

---

## loop-001-1 — the call-site inventory, derived from source

Scope: `platforms/claude-code/commands/`, `platforms/claude-code/agents/`, `core/agents/`,
`core/skills/`, and `platforms/cowork/` (added to the scope; the loop named four directories and
the fifth turned out to be the informative one).

Repository `advanced-planning` at `02b4b86e020bcaccc843228603bf6911450fc2d2`, `main`, v0.16.0.

| File | Line | Module |
|---|---|---|
| `platforms/claude-code/commands/new-phase.md` | 125 | `history_log` |
| `platforms/claude-code/commands/next-loop.md` | 77 | `state_manager` |
| `platforms/claude-code/commands/next-loop.md` | 207 | `state_manager` |
| `platforms/claude-code/commands/next-loop.md` | 341 | `history_log` |
| `platforms/claude-code/commands/next-phase.md` | 376 | `remediate` |
| `platforms/claude-code/commands/next-phase.md` | 419 | `versioning` |
| `platforms/claude-code/commands/plan-and-phase.md` | 139 | `history_log` |
| `platforms/claude-code/commands/run-gate.md` | 39 | `install_audit` |
| `platforms/claude-code/commands/run-gate.md` | 326 | `codex_gate` |
| `platforms/claude-code/commands/run-gate.md` | 386 | `codex_gate` |
| `platforms/claude-code/commands/sync-install.md` | 46 | `install_audit` |
| `platforms/claude-code/commands/sync-install.md` | 113 | `install_audit` |
| `platforms/claude-code/commands/sync-install.md` | 151 | `install_audit` |

**13 call sites across 6 commands**, using 6 modules: `install_audit` ×4, `history_log` ×3,
`state_manager` ×2, `codex_gate` ×2, `versioning` ×1, `remediate` ×1.

This matches the controller's independent count over the *installed* copies in `~/.claude/commands/`
exactly — 13 sites, the same 6 commands. The loop asked for a discrepancy to be reported as a
finding rather than smoothed over; there is none.

**Every module named exists** under `platforms/python/`. The second defect the todo was watching
for — a call site naming a module that was never written — is not present.

### The three zero rows are the finding

| Directory | Call sites |
|---|---|
| `platforms/claude-code/commands/` | 13 |
| `platforms/claude-code/agents/` | 0 |
| `core/agents/` | 0 |
| `core/skills/` | 0 |
| `platforms/cowork/` | 0 |

The shared runtime is an **adapter-layer dependency of the Claude Code adapter**, not a core
dependency. `core/` does not invoke it at all, and the one adapter that is not Claude Code does
not either — Cowork solves the same checkpoint problem with a POSIX `platforms/cowork/checkpoint.sh`
that snapshots `.advanced-plans/` and needs no Python.

That changes the decision in loop-001-3 in two ways. It is a smaller blast radius than the phrase
"shared runtime" suggests, and there is already a precedent in this repository for an adapter
shipping its own executable helper rather than reaching for a common one.

It also cuts the other way, and this is the part not to lose: the three adapters phase 6 is about
to add have to choose a side. Follow the Claude Code pattern and each inherits this defect; follow
the Cowork pattern and the framework grows a second, third and fourth reimplementation of state
handling. Neither is free.

---

## loop-001-2 — reproduced from a clean install

`setup/claude-code/install.ps1 -Project <scratch>` into an empty scratch directory. Exit 0.

**What landed:** `.claude/{commands,agents,schemas,skills,settings.json}` — 14 commands, 13
agents, 9 core skills, 5 schemas — plus a `.advanced-plans/{phases,specs,state,logs}` scaffold.

**What did not:** anything under `platforms/`. Confirmed by reading `install.ps1`'s copy calls
rather than only by listing the result: it copies commands, agents, core skills and schemas, and
creates the scaffold. `platforms/python/` is never referenced as a copy source in either
`install.ps1` or `install.sh`.

### A — from the installed project, which is what a user gets

The installer's own closing instructions are *"cd into your project folder → claude → `/new-phase`"*,
and `/new-phase` line 125 is a `history_log` call. So the first command a new user is told to run
is one of the thirteen.

```
python -m platforms.python.history_log .advanced-plans/state/history.jsonl '{"event":"probe"}'
  -> Error while finding module specification for 'platforms.python.history_log'
     (ModuleNotFoundError: No module named 'platforms')                          exit 1

python -c "from platforms.python.state_manager import prepare_loop_ready"        # /next-loop fast path
  -> ModuleNotFoundError: No module named 'platforms'                            exit 1

python -m platforms.python.install_audit --layers source,project                 # /run-gate step
  -> ModuleNotFoundError: No module named 'platforms'                            exit 1
```

### B — the same line from the source repo, as a control

```
cd advanced-planning && python -c "from platforms.python.state_manager import prepare_loop_ready"
  -> state_manager imports fine here                                             exit 0
```

The control is the point. The modules are fine; they are not *reachable*. A fix has to change
where the interpreter looks, not what it finds.

### Interim workaround, verified

`PYTHONPATH=C:/Users/mharvey2/Coding/advanced-planning` makes all three succeed from any cwd. With
it set, `prepare_loop_ready` reads this programme's new `phase-6/loops.md` and returns
`ok / ralph-loop-001 / 5 todos`, so `/next-loop`'s fast path works in the AAW controller checkout
today. That is a workaround for the controller, not the fix — it depends on one absolute path
being right on one machine.

---

## loop-001-3 — the four mechanisms, costed

| | (a) copy into the install tree | (b) console-script shim on PATH | (c) resolve a recorded source path | (d) detect and degrade |
|---|---|---|---|---|
| **Works for a non-Claude host** | yes — each adapter copies, or one shared `.advanced-plans/lib/` | yes — everything shells out | yes — `PYTHONPATH` or an absolute path is host-agnostic | n/a — not a mechanism |
| **Survives the source repo moving** | yes | only if reinstalled | **no** — breaks until `sync-install`/`--refresh` is re-run | n/a |
| **Duplicates code that can drift** | **yes — one copy per project** | no | no | n/a |
| **Uninstall has to undo** | remove the copied tree | remove the shim; a PATH mutation is the risk | nothing | nothing |
| **New machinery required** | extend `install_audit` to a fourth layer | Python packaging + entry points + PATH | record one path in the manifest | an existence check per call site |
| **Proven to work here** | not tried | not tried | **yes, today** | n/a |

### Recommendation: (c) as the mechanism, (d) as the guard

**Against (a).** It creates an N-th copy of *executable* code in every project, and this programme
has been burned by exactly that twice — the phase-5 gate found an orphaned second copy of the
routing block still shipping at the repository root, and `install_audit` exists at all because
install-layer drift is a known failure mode here. Worse, `install_audit` compares by **mtime**,
a limitation already on the programme's carried-items list, so its drift detection is currently
the weakest part of the machinery being asked to carry the most.

**Against (b).** It is the only option that adds a packaging system and mutates PATH, for a
problem that is really "the interpreter is looking in the wrong place". It also makes uninstall
the most intrusive of the four.

**For (c).** Zero duplication, single source of truth, no new subsystem, and it is the one option
already demonstrated to work. Its real weakness — a moved or renamed source checkout breaks it
silently — is precisely what `sync-install` and AAW's `--refresh` already exist to repair, and (d)
turns "silently" into "with a message naming the manifest key to fix".

**(d) is not optional under any of the three.** Today the failure is a raw `ModuleNotFoundError`
in the middle of a slash command, with no indication of which manifest entry is wrong or what the
user should do. Whichever mechanism is chosen, a call site that cannot reach the runtime should
say so in one line and name the fix.

### What this decision binds

Loops 004 and 005 add three adapters that will each need the same runtime by the same route. The
mechanism chosen here is the one all three inherit, and loop-004-1's adapter specification is
written against it. That is why this is a human gate and why it sits in loop 001 rather than
wherever the plan's deliverable table would have put it.
