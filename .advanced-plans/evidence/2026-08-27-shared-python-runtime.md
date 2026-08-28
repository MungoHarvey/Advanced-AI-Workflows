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

---

## Post-gate: the cross-vendor panel, and mechanism B′ (2026-08-28)

The loop-001-5 human gate was answered **"Pass, but re-ask the three questions"**. Before
re-asking, the controller sent the mechanism itself to an independent panel, because the
question the codex reviewer had left unanswered — what happens on a *global* install — turned
out to be the one the mechanism got wrong.

### The panel

Three reviewers, three vendors, one envelope, run as real Herdr worker panes via
`multi-model-review`. Artefacts:
`~/.herdr/reviews/advanced-planning-20260827-180113/` (`COMPILED.md`, plus one file per
reviewer).

| Reviewer | Critical findings | Verdict |
|---|---|---|
| agy (`gemini-3.7-flash-high`) | 3 | Yes |
| cursor (`cursor-grok-4.6-medium`) | 3 | No |
| opencode (Qwen3.5 397B) | 4 | No |

**Cursor's review was the one that mattered**, and it reshaped the implementation:

1. `ProjectWithoutManifest` was raised *before* any global fallback could be consulted, so the
   boundary stop and the fallback were mutually exclusive — the fallback could never fire in
   the case it existed for.
2. A **nested git repository** inherited the enclosing checkout's runtime, silently.
3. `HOME` and `USERPROFILE` disagree under Git Bash on Windows, so an install and a lookup
   could resolve different homes.

All three were real and all three are now closed. This is the argument for rotating reviewers
across vendors rather than asking the same one twice: the two reviewers who returned "Yes" and
"No" respectively did not find any of them.

### The panel contradicted the recorded decision

The controller's own recommendation at the gate was `~/.claude/bin/ap.py`. That contradicts
**contract 6**, which the controller had itself written three commits earlier: the runtime
record is host-neutral and belongs in `.advanced-plans/`, never in an adapter's own directory.
A `~/.claude/` location would have made the next adapter write a second record — the exact
failure contract 6 exists to prevent. Separately, a literal `~` in
`runpy.run_path('~/...')` was verified to crash: `run_path` does no tilde expansion.

Both were reported to the user, and the gate was re-put as a choice. The user selected:

> **B′ — host-neutral, global installer only.** `~/.advanced-plans`, not `~/.claude`; project
> installer unchanged; `cmd.exe` still excluded; silent fallback blocked in-project by
> b6989c0's boundary stop.

### Where the implementation departs from the sketch, and why

The option preview said *"runpy … `os.path.expanduser()` at the 6 inline sites"* and *"13 call
sites change once"*. **Neither is what was built**, and the departure is deliberate:

- `os.path.expanduser()` follows `$HOME`. On this machine `$HOME` under Git Bash is routinely
  a mapped network drive while native Python reads `USERPROFILE` — the two disagree, so
  `expanduser` resolves to a directory the installer never wrote to. Finding 3 above is exactly
  this hazard.
- No single literal works across bash, PowerShell and native Python, so "change the call sites
  once" has no correct value to change them *to*.

Instead the **installers rewrite the launcher path** in the commands they copy, to one absolute
forward-slash path. Source call sites keep the project-relative form and are unchanged in
meaning. This satisfies every property B′ was chosen for — host-neutral location, project
installer untouched, no silent fallback — without depending on a home-directory notion that
differs between the shell and the interpreter.

The cost is a new coupling: the rewrite must be a **pure path substitution**, because
`install_audit` normalises exactly one canonical launcher path back out before hashing. The
first pass rewrote *bare* call sites into *quoted* ones, so source and installed could never
converge and the audit reported **6 files permanently stale** on a clean install — drift no
`/sync-install` could settle. The repair was to quote the source, and the convention is now
pinned by `test_every_source_call_site_is_in_the_substitutable_form` rather than living
implicitly inside three `sed` scripts.

### Two defects the panel missed, found by running it

Neither of these is visible by reading. Three reviewers read this code and none reported them.

1. **The record was read from the caller's profile.** An install-time home and a run-time home
   could therefore disagree, which is the same class of fault as finding 3 and survived the fix
   for it. The installed launcher now prefers the manifest **beside itself**, which cannot
   disagree with the install that wrote it. It refuses that when the launcher's own project
   *encloses* the directory being resolved — that is precisely the borrowing the boundary stop
   exists to refuse, and the first fix re-opened the hole (three boundary tests caught it). The
   residual case is stated in the docstring rather than hidden.
2. **The six in-line `runpy` call sites raised a raw traceback**, not the guard — i.e. the
   exact failure the guard had been written to replace, still occurring at half the call sites.
   `bootstrap()` now catches `Unreachable`, reports, and exits 2.

### Live proof

- A full `install.ps1 -Global` redirected via `$env:USERPROFILE` to a scratch profile: the real
  profile's `.claude/commands` fingerprint and file count were byte-identical before and after.
  (The real `~/.advanced-plans/` does already exist — `specs/` only, dating from June and July,
  unrelated to this work and not written by it.)
- From a **scaffolded-but-never-installed** project: the shell call site exits 0 and names the
  manifest it used; the in-line `runpy` call site returns the checkout root; a real module runs
  from it.
- `install_audit --layers source,global` against that install: **0 stale** (was 6).
- All four new behaviours revert-proven — each removal breaks its own test.

### Correction to the earlier record

The loop-001-4 and loop-001-5 events both state that advanced-planning has
`core.autocrlf=true` and that this is the cause of *"the 6 pre-existing test failures"*.
**Both halves are wrong.** Measured 2026-08-28: `core.autocrlf` is **false**, and `main` fails
**1** test, not 6 — `test_sandbox_leaves_real_working_tree_untouched`, which points at an
unrelated checkout path under `Documents/Coding/`.

The five `install_idempotency` failures were **introduced by this controller's own edits**: the
editing tools silently convert LF files to CRLF, which rewrote whole files (5306 insertions for
an 861-line change), broke those five tests, and would have committed three `#!/bin/sh`
installers that no POSIX shell could execute. Every file was normalised back to LF and the
commit amended before anything left the branch; the four earlier commits on the branch were
audited and are clean.

The underlying hazard is real and remains open: advanced-planning has **no `.gitattributes`**,
so nothing catches this. That is the item to carry — not the autocrlf claim, which was never
true.

The claim's origin is worth naming, because it is the kind of error that repeats. Two repos
were conflated:

| | `core.autocrlf` | `.gitattributes` |
|---|---|---|
| Advanced-AI-Workflows (the controller checkout) | `true` | present |
| advanced-planning (the repo being changed) | `false` | **absent** |

`autocrlf=true` is AAW's setting, and AAW also has a `.gitattributes`, so AAW is safe on both
counts. advanced-planning has neither protection. The original note took the setting from the
repo the controller was standing in rather than the repo it was editing.
