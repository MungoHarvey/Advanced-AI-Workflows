# Superpowers port — phase 5 / ralph-loop-002 evidence

**Loop**: `phase-5` / `ralph-loop-002`
**Specification**: `.advanced-plans/evidence/2026-08-26-superpowers-behaviour-matrix.md`
(gate PASSED 2026-08-26; see `...-superpowers-matrix-gate-review.md`)
**Amended phase criteria**: `.advanced-plans/phases/phase-5/plan.md` § *Amendment — 2026-08-26*

This file accumulates as the loop's todos complete. Each section is written by the
controller after re-running the checks itself; a worker's own summary is never the
evidence.

---

## loop-002-1 — backup tag and local mirror branch

**Provider**: controller (`claude`/Opus 5), in `C:/Users/mharvey2/Coding/superpowers`.
**Date**: 2026-08-26. **Remote writes: none.**

### Checkout identity

Two clones of `MungoHarvey/superpowers` exist on this machine and they are **not** at the
same commit. The one used by this programme, and by loop-001's drift evidence, is:

```
C:/Users/mharvey2/Coding/superpowers
  branch  main            fde9f97
  origin  https://github.com/MungoHarvey/superpowers.git   main -> fde9f97
  upstream https://github.com/obra/superpowers.git         main -> b36e082
  working tree clean
```

The other, `M:/Coding/planning/superpowers`, is on `main` at `f2d65a6`, has **no `upstream`
remote**, and is two commits behind the fork's own head. It is stale and must not be used
for this port. Recorded as an open item.

`git fetch upstream --tags` returned no new refs — `upstream/main` is still `b36e082`
(v6.3.0), unchanged since loop-001 measured the drift. The matrix is therefore still
measured against current upstream.

### Refs created — local only

```
git tag -a pre-aaw-port-2026-08-26 fde9f97 -m "Pre-port fork head, 2026-08-26. ..."
git branch mirror/upstream-2026-08-26 upstream/main
```

```
$ git tag -n1 pre-aaw-port-2026-08-26
pre-aaw-port-2026-08-26 Pre-port fork head, 2026-08-26.

$ git log --oneline -1 mirror/upstream-2026-08-26
b36e082 Release v6.3.0: Devin CLI and Hermes Agent support, brainstorming three-path router,
        SDD/Codex efficiency fixes (#2125)

$ git log --oneline -1 HEAD
fde9f97 fix(brainstorming): update AP-detected default from .claude/plans/ to .advanced-plans/specs/
```

`main` was not moved and nothing was checked out. Recovery from the tag is
`git reset --hard pre-aaw-port-2026-08-26`.

### Check 1 — the mirror is a mirror

```
$ git diff --stat upstream/main..mirror/upstream-2026-08-26
(no output)
```

Empty. The branch is byte-identical to current upstream, which is the whole point: it was
created by pointing at `upstream/main`, not by copying files forward. This is the same
assertion loop-002-6 re-runs at the end of the loop, after the AAW-side work, to prove
nothing crept in.

### Check 2 — exactly what publishing would change

```
$ git log --oneline origin/main..mirror/upstream-2026-08-26 | wc -l
241

$ git log --oneline mirror/upstream-2026-08-26..origin/main
fde9f97 fix(brainstorming): update AP-detected default from .claude/plans/ to .advanced-plans/specs/
b874847 Merge pull request #1 from obra/main
f2d65a6 feat: use AskUserQuestion tool for brainstorming questions
dfd7ff5 feat: conditional integration with Advanced Planning and Plannotator

$ git diff --stat origin/main..mirror/upstream-2026-08-26 | tail -1
164 files changed, 20679 insertions(+), 3481 deletions(-)
```

The fork gains 241 upstream commits and drops **four** — and those four are precisely the
four intents the matrix analysed, with nothing else hiding among them:

| Dropped commit | Carries | Matrix verdict |
|---|---|---|
| `dfd7ff5` | SP-1 (design-doc location), SP-2 (terminal-state routing), SP-4 (companion tools) | SP-1 and SP-2 PORT to the fenced block; SP-4a superseded; SP-4b dropped |
| `f2d65a6` | SP-3 (`AskUserQuestion` for clarifying questions) | goes to the fenced block, per the gate's F4 resolution |
| `b874847` | merge of upstream into the fork | no intent |
| `fde9f97` | SP-1 follow-up — `.claude/plans/` → `.advanced-plans/specs/` | folded into SP-1 |

This is the independent confirmation that the matrix's coverage was complete: had a fifth
intent existed, it would appear in this list. It does not.

### What publishing would take — NOT RUN, NOT AUTHORISED

```
git push origin mirror/upstream-2026-08-26:main --force-with-lease
```

`docs/herdr-kickoff-prompt.md` places force-push and default-branch writes outside the
controller's authority. The command is written down here so the operator can run it after
the loop-002-7 gate, with the backup tag as the undo. **It has not been run, and the tag
has not been pushed either.**

### Verdict

`loop-002-1` satisfied. The fork can be taken to a mirror by one reviewed command, the old
state is recoverable from a local annotated tag, and the publish delta is measured rather
than assumed.

---

## loop-002-2 — the fenced routing block

**Provider**: controller (`claude`/Opus 5). **Date**: 2026-08-26.
**File**: `.claude/skills/setup-with-claude/references/claude-md-routing.md` (rewritten in
place, markers unchanged).

### One file, not two variants

The todo asked for two variants, CLAUDE.md and AGENTS.md, with a check that they say the
same thing. That check is unnecessary if there is only one text, so the block was made
fully host-neutral instead and a single file now serves both hosts. Two host references
were removed to get there:

- rule 4 said "read `.claude/skills/brainstorming/SKILL.md`" and now says to load the skill
  from wherever the harness keeps its skills;
- the closing instruction named `.claude/settings.json` and now says "where this harness
  supports write hooks".

Neither carried meaning that a Claude-only path was supplying. Design §7.3's rule — no
`.claude/`, `.cursor/`, `.opencode/`, Claude-only tool name, or host-specific permission
syntax — is therefore satisfied by the block itself, not only by the core files.

The one Claude-only tool name that remains is `AskUserQuestion`, and it is named as an
example inside a harness-conditional sentence ("the harness's structured question tool
(`AskUserQuestion` in Claude Code) ... where the harness has no such tool, ask in prose as
usual"). That is a capability fallback, not a host dependency.

### What the block now carries

| Intent | Section | Conditional on Advanced Planning? |
|---|---|---|
| Detection | *How to Tell What Is Installed* | defines the predicate |
| **SP-1** — approved spec location | *Brainstorming* item 2, *Where Plans and Specs Are Written* | yes |
| **SP-2** — terminal state routes to phase planning | *Brainstorming* item 3 | yes, **and Architectural path only** |
| **SP-3** — structured clarifying questions | *Brainstorming* item 1 | no — all three paths, harness-conditional |
| **SP-4a** — companion recommendation | *Companion Tools* | yes, and in both directions |
| SP-4b — Plannotator | *Companion Tools*, final paragraph | dropped, with an explicit do-not-use |

Three things the block did not say before and now does:

1. **A precedence disclaimer.** "Everything outside these two markers belongs to whoever
   wrote this file... Where it conflicts with the rest of this file, the rest of this file
   wins." This is entry criterion 2 written into the artefact rather than left as a
   property of the installer.
2. **The failure mode is spelled out.** "If `.aaw/installed.json` is missing, unreadable, or
   malformed, treat every component as NOT installed... do not write to a path that this
   project has given you no evidence exists." This is what ACC-05 tests.
3. **The over-process warning.** "Do not upgrade a request into phase planning because this
   project has Advanced Planning installed — that would drag every feasibility probe and
   one-file fix into a full decomposition, which is the exact over-process the three-path
   router exists to prevent." An agent that reads only the positive rule can get SP-2 wrong
   in exactly this direction, which is why the negative is stated too.

### Checks

```
$ grep -n 'installed.json\|\["installed"\]' claude-md-routing.md
15:  installation manifest at `.aaw/installed.json` to find out.**
19:  .components["<component>"]["installed"] == true
32:  - **If `.aaw/installed.json` is missing, unreadable, or malformed, ...

$ grep -n '\.claude/\|\.cursor/\|\.opencode/\|\.agents/' claude-md-routing.md
(no output)

$ grep -c 'aaw-routing:begin\|aaw-routing:end' claude-md-routing.md
2

$ grep -n -i 'Architectural' claude-md-routing.md
86, 87, 90-92 (Spike and Bounded explicitly excluded), 106, 112

$ grep -n 'AskUserQuestion' claude-md-routing.md
100:  ... the harness's structured question tool (`AskUserQuestion` in Claude Code) ...

$ bash tests/packaging/run-all.sh | tail -4
idempotency: PASS - 43/43 checks
packaging:   PASS - 4/4 checks
```

### One check was amended mid-loop, not silently passed

The todo's original check read `grep the block for plannotator -> zero hits`. The block
mentions Plannotator twice and both are deliberate: rule 7 says "do not route to it or
detect it", and *Companion Tools* says it is deprecated and that any companion list still
naming it is out of date. Silence would have been the weaker outcome, because upstream
Advanced Planning still ships `core/skills/companion-detection/SKILL.md` naming Plannotator
— an agent reading both files needs to be told which one is current. The check was rewritten
to require that every mention is a do-not-use instruction rather than that no mention
exists. The amendment is recorded in `loops.md` next to the check itself.

### A second stale copy was removed

`SETUP.md` carried a hand-abridged copy of the block for manual installation, and it had
already drifted: different heading case, no phase-boundary rule, no companion section, and
an unconditional `.advanced-plans/specs/` override with no manifest gate — precisely the
ACC-05 failure the block now guards against. Reproducing the corrected block there would
recreate the same drift, so the copy was replaced with a pointer to the canonical file.
There is now exactly one routing block text in the repository.

### Verdict

`loop-002-2` satisfied. All four intents are expressed in a file AAW owns and installs, so
nothing needs to live inside the Superpowers fork.

---

## loop-002-3 — the installer merges the block idempotently, into both instruction files

**Provider**: controller (`claude`/Opus 5). **Date**: 2026-08-26.
**Files**: `.claude/skills/setup-with-claude/SKILL.md` (the specification),
`tests/packaging/project_ops.py` (the executable form of what it documents),
`tests/packaging/test-idempotency.sh` (stage 10, new).

### What was already true, and what was missing

Idempotency itself was already built and passing at 43/43 before this todo: install
replaces the fenced block rather than appending a second one, uninstall restores the
project to its starting bytes, and a half-fence exits 3 rather than guessing where the
block ends. None of that needed rebuilding.

What was missing was **`AGENTS.md`**. The design spec has `aaw init` merging the block into
"existing `AGENTS.md` and/or `CLAUDE.md`", and the installer only ever knew about
`CLAUDE.md`. On a harness that reads `AGENTS.md`, every rule in the block would simply not
be read — which would have made ACC-04 and ACC-05 pass on Claude Code and mean nothing
anywhere else. The block having just been made host-neutral is what made this worth
fixing rather than deferring: there is one text, so serving two files costs nothing.

### The rule chosen, and why

```python
INSTRUCTION_FILES = ("CLAUDE.md", "AGENTS.md")

def instruction_targets(project):
    present = [n for n in INSTRUCTION_FILES if os.path.isfile(os.path.join(project, n))]
    return present or ["CLAUDE.md"]
```

Install into every instruction file the project already has; create `CLAUDE.md` only when
it has neither. A project with an `AGENTS.md` has one because something reads it. A project
with neither should not acquire two files it never asked for — that is an installer leaving
litter, and it is also how an uninstall ends up deleting a file the user thinks is theirs.

### The ordering bug, fixed before it existed

Uninstall now checks **every** file for a broken fence before writing **any** of them. The
naive shape — check and write in the same pass — cleans `CLAUDE.md`, then hits a half-fence
in `AGENTS.md`, and prints "Nothing was changed." That message would be false, and the
project would be left half-uninstalled. `uninstall_routing()` does the marker scan in a
first pass and the writes in a second, and the docstring says why.

### Checks

```
$ bash tests/packaging/run-all.sh | tail -4
idempotency: PASS - 56/56 checks
packaging:   PASS - 4/4 checks
```

43 → 56: thirteen new checks, all in stage 10.

| Check | What it excludes |
|---|---|
| AGENTS.md-only project: the block lands in AGENTS.md | the block being invisible on a non-Claude harness |
| and no CLAUDE.md is invented alongside it | the installer leaving litter |
| and the user's own AGENTS.md content survives verbatim | clobbering someone's house rules |
| and a second install is byte-identical | ACC-16, on the new path |
| and uninstall returns AGENTS.md to the bytes it started with | a one-way install |
| both-file project: each file gets the block exactly once | duplicate blocks, "which one wins" |
| and installing again changes neither file | ACC-16, both files at once |
| and the two files carry byte-identical block text | silent divergence between hosts |
| and uninstall clears the block from both | a residue that reactivates on the next harness |
| a half fence in AGENTS.md exits 3 | guessing where a hand-edited block ends |
| and names AGENTS.md as the file it refused | an error the user cannot act on |
| and CLAUDE.md is byte-identical — checked before anything was written | **the half-uninstall above** |
| a project with neither file gets CLAUDE.md only | the same litter, from the other direction |

### Mutation-verified, because thirteen new checks passing first time proves nothing

Two mutants were applied to the implementation and the suite re-run:

| Mutant | Change | Result |
|---|---|---|
| 1 | `instruction_targets` always returns `["CLAUDE.md"]` — i.e. the old behaviour | **6 of the 13 fail**, including the three headline AGENTS.md checks |
| 2 | check-and-write in one pass instead of scan-then-write | **exactly 1 fails** — "CLAUDE.md is byte-identical — checked before anything was written" |

Mutant 2 is the useful one: it kills precisely the check written for it and nothing else,
which is what says that check is measuring the ordering and not something incidental. Both
mutants were reverted and the suite re-run clean before committing; `grep -c MUTANT
project_ops.py` returns 0.

### The specification was updated too, not just the test

`project_ops.py`'s own docstring says: *"If it and the skill disagree, that is a finding
about one of them, and the skill is the specification."* So `SKILL.md` was updated to match
rather than left behind:

- **Step 4** is now "Wire the routing block into the project's instruction file(s)", states
  the which-files rule, and applies Cases A/B/C per file. It also now says the block's own
  precedence disclaimer is only true if this step honours it.
- **Step U1** reads every instruction file and says, in bold, to check all of them before
  writing any of them — with the half-uninstall spelled out as the reason.
- **Steps U2 and U3** name both files, and U3's delete-if-empty guard now carries the
  reason: deleting a file the user wrote, because our block happened to be the rest of it,
  is the worst thing the uninstall can do.
- Four further single-line mentions (the reference list, the report table, the removal
  inventory, the uninstall summary) were updated in the same pass.

### Verdict

`loop-002-3` satisfied. Idempotency and content preservation hold on both instruction
files, the delimitation is proven by an uninstall that restores starting bytes, and the
skill and its executable form agree.

---

## loop-002-4 and loop-002-5 — the behaviour proofs (ACC-04, ACC-05)

**Provider**: `opencode` (Qwen3.5 397B via the ELM proxy), six rounds, each in its own
fresh pane and process. **Controller**: `claude`/Opus 5. **Date**: 2026-08-26.
**Verification**: filesystem only — every claim below is a hash-diff of the fixture
against a baseline taken immediately before the run. A worker's own account of what it did
is corroboration, never evidence.

### The two fixtures

Two throwaway projects, identical in every respect except the one thing under test.

|  | `with-ap` | `without-ap` |
|---|---|---|
| `.aaw/installed.json` → `advanced-planning.installed` | `true` | **`false`**, with `scope: none` |
| The framework itself | `.claude/skills/phase-plan-creator/SKILL.md` present | absent |
| `.advanced-plans/` on disk | none | **`specs/borrowed.md`** — plans copied in from elsewhere |
| `AGENTS.md` | the routing block, byte-identical between the two | same |
| `skills/brainstorming`, `skills/writing-plans` | copied from `mirror/upstream-2026-08-26` | same |
| `src/cli.py`, `README.md` | a small real CLI with a flag-parsing flow | same |

The `.advanced-plans/specs/borrowed.md` in `without-ap` is the whole point of the
discriminator: a project can hold plans without holding the framework. A rule that tests
for the directory passes there and is wrong. A rule that reads the manifest predicate
fails there and is right. `without-ap` also records the component as `installed: false`
rather than omitting it, so the check is "absence was recorded", not "absence was
inferred".

`src/cli.py` exists because the Bounded path *requires* it: the skill says "bounded means
the flow you are changing is already here to read. If there is no existing flow to change,
the task is not bounded." Without real code, a Bounded classification could not be earned
and the negative check would have proved nothing.

### The envelope

One envelope, byte-identical in both projects (`cmp` checked before every round), naming
three requests to be handled one at a time and independently:

1. a plugin system for the formatters, with a discovery mechanism, a registration
   interface the existing formatters must move onto, and interface versioning — stated as
   not existing in the codebase today (**Architectural** by the skill's own definition);
2. add a `--quiet` flag suppressing the per-row progress lines (**Bounded** — the flow is
   in `src/cli.py`);
3. can Parquet be read with the standard library alone, quick and dirty, no dependency
   (**Spike**).

The envelope never names the expected classifications, never names `.advanced-plans`,
`docs/superpowers`, phase planning or `writing-plans`, and never says which file carries
the project's instructions — only "read the project's instruction file or files". It ends
by asking for `ACC-RESULT.md`: classification, spec path written, other files, terminal
step, and one line of why, per request.

Four envelope revisions were made across the six rounds. Every one of them was about
unblocking an approval or question gate so an unattended run could reach a terminal state;
none touched routing, paths, or tools. They are listed in the round table so the reader can
see which text each round ran under.

### The six rounds

Each row is a hash-diff against a baseline taken immediately before that round, in a fresh
pane and a fresh process. "blocked" means the worker put a clarifying question to a human
through the harness's interactive question tool and waited; no controller answered it.

| # | envelope | block | fixture | spec written to | terminal step | verdict |
|---|---|---|---|---|---|---|
| 1 | v1 | as authored | with-ap | `.advanced-plans/specs/` OK | `writing-plans` WRONG | **FAIL** — found F1 |
| 1 | v1 | as authored | without-ap | `docs/superpowers/specs/` OK | `writing-plans` OK | PASS |
| 2 | v2 | + F1 fix | with-ap | named, not written | `/new-phase` OK | partial |
| 2 | v2 | + F1 fix | without-ap | `docs/superpowers/specs/` OK | `writing-plans` OK | PASS |
| 3 | v3 | + F1 fix | with-ap | — | — | blocked |
| 3 | v3 | + F1 fix | without-ap | `docs/superpowers/specs/` OK | `writing-plans` OK | PASS |
| 4 | v3 | + F1 fix | with-ap | `.advanced-plans/specs/` OK | `/new-phase` OK | **PASS** |
| 4 | v3 | + F1 fix | without-ap | — | — | blocked |
| 5 | v4 | + F1 fix | with-ap | `docs/superpowers/specs/` WRONG | `writing-plans` WRONG | **FAIL** — found F2 |
| 5 | v4 | + F1 fix | without-ap | `docs/superpowers/specs/` OK | `writing-plans` OK | PASS |
| 6 | v4 | + F1 + F2 fix | with-ap | `.advanced-plans/specs/` OK | `/new-phase` OK | **PASS** |
| 6 | v4 | + F1 + F2 fix | without-ap | `docs/superpowers/specs/` OK | `writing-plans` OK | PASS |

Envelope revisions, all of them about letting an unattended run reach a terminal state and
none about routing: **v2** — approval is granted *at the moment the design is presented*,
so a write is not deferred to a future approval that never comes; **v3** — ask clarifying
questions, then answer them yourself with the option you would have recommended; **v4** —
ask them *in the transcript*, because a question put through the harness's interactive tool
waits forever when nobody is at the keyboard.

`without-ap` returned the same answer in every round that produced one — five for five,
under three different envelopes and two versions of the block.

### Finding F1 — the block told two different stories, and the worker believed the wrong one

Round 1 wrote the spec to the right place and then handed over to the wrong skill. The
worker's stated reason named the culprit: front-door **rule 5**, which read

> Need a structured implementation plan from a spec -> Use the `writing-plans` skill

with no condition on it at all, while addition 3 under *Brainstorming* said that with
Advanced Planning installed the step after an approved architectural spec is phase
planning. *Where Plans and Specs Are Written* made it worse by discussing where
`writing-plans` output goes, which reads as a third endorsement of running it.

Rule 5 is now gated on the same manifest predicate as addition 3, and the plans section
says outright that it governs where `writing-plans` writes *if it runs* and is not an
instruction to run it. Fixed in `12af179`; rounds 2, 4 and 6 all took `/new-phase`
afterwards and cited rule 5 by name for it.

This is the finding the proof existed to catch. The contradiction was invisible on
inspection — I wrote both halves — and only a run that had to *act* on the block exposed
which half won.

### Finding F2 — the block was in context and was ignored anyway

Round 5's `with-ap` worker wrote the spec to the upstream default and handed to
`writing-plans`, citing only the brainstorming skill and never mentioning the project's
instructions at all.

The obvious explanation — that `AGENTS.md` was never delivered — is wrong, and a direct
probe settles it. A fresh `opencode` agent in the same fixture, told to answer from context
and to run no tool of any kind, replied:

> Yes — two files were supplied automatically as context: `~/.claude/CLAUDE.md`
> (machine-level instructions), `AGENTS.md` (project-level instructions in the current
> working directory)

and then quoted addition 2 back verbatim, matching the file character for character. **The
fenced block reaches a non-Claude harness automatically, before the first user message,
with no tool call and no host-specific path.** That is the premise the whole zero-patch
design rests on, and it is now demonstrated rather than assumed.

So round 5 was the model declining to apply an instruction it had been given. The block
had no sentence anywhere asserting that its additions outrank a skill's built-in defaults —
it disclaimed precedence over the *file* it sits in, which is right, but said nothing about
the *skills*, which is what it exists to steer. That sentence now exists, at the top of the
*Brainstorming* section, along with an explicit statement that everything the section does
not mention stays exactly as the skill has it. Round 6 then passed on both fixtures.

Two rounds are not a measurement, and this is recorded as a mitigation, not a cure: on this
runtime the block was applied in four of the five `with-ap` rounds that produced a result.
An instruction file is advisory by construction — no wording makes a model read it — which
is a fact about instruction files and not a defect in this one, and it is why the phase
gate wants a second model's eyes on this in `loop-002-7`.

### The checks

**loop-002-4 — ACC-04, Advanced Planning present** (round 6, `with-ap`):

| check | result |
|---|---|
| the output landed in `.advanced-plans/specs/` — **ACC-04** | PASS — `2026-08-26-formatter-plugin-system-design.md`, by hash-diff |
| the Architectural terminal state invoked phase planning | PASS — `/new-phase`, and `/plan-and-phase` correctly *not* chosen: the parenthetical in addition 3 says `/new-phase` for a codebase already explored, and the worker gave that as its reason |
| `writing-plans` did not run | PASS — no plan document exists anywhere in the fixture; the only new files are the spec and the report |
| a Spike-classified request produced no spec file and no phase planning | PASS — request 3, classified Spike, `spec_file: NONE`, `terminal_step: NONE` |
| a Bounded-classified request produced no spec file and no phase planning | PASS — request 2, classified Bounded, `spec_file: NONE`, ends at implementation |
| no fixture input was modified | PASS — all ten baseline files unchanged, `skills/brainstorming/SKILL.md` included |

**loop-002-5 — ACC-05, Advanced Planning absent** (round 6, `without-ap`):

| check | result |
|---|---|
| the output landed in the upstream default location — **ACC-05** | PASS — `docs/superpowers/specs/2026-08-26-plugin-system-design.md`, the path at `skills/brainstorming/SKILL.md:100` and `:206` |
| every file the worker produced, grepped for `.advanced-plans` | PASS — **0 hits** in both files |
| the manifest predicate read `false` rather than the file being missing | PASS — the transcript reads `installed.json`, then reasons "Since Advanced Planning is NOT installed, the spec goes to `docs/superpowers/specs/`". Absence recorded, not inferred |
| the `.advanced-plans/specs/borrowed.md` decoy did not read as an installation | PASS — untouched, never cited, and the routing went the other way |
| Spike and Bounded produced no spec file and no phase planning | PASS — both `NONE` |
| no fixture input was modified | PASS — all ten baseline files unchanged |

One thing the round-6 `without-ap` report got wrong is worth keeping: it recorded
`spec_file: docs/superpowers/specs/plugin-system-design.md` while the file on disk is
`2026-08-26-plugin-system-design.md`. Nothing turns on it — but it is a clean small example
of why the hash-diff is the evidence and the worker's report is not.

### loop-002-6 — the fork patch, measured

```
$ git rev-parse mirror/upstream-2026-08-26              b36e0829c6d0...
$ git rev-parse upstream/main                           b36e0829c6d0...
$ git diff --quiet upstream/main..mirror/upstream-...   -> exit 0
$ git rev-list --count mirror..upstream/main            0
$ git rev-list --count upstream/main..mirror            0
```

Same commit, both directions, empty tree diff. **The patch against upstream is zero**, and
it stayed zero through all six rounds — `skills/brainstorming/SKILL.md` and
`skills/writing-plans/SKILL.md` are byte-identical in both fixtures to the copies taken
from the mirror, before and after every run. Everything ACC-04 and ACC-05 demonstrate was
carried by the instruction file, not by an edit to a skill.

`loop-002-6` is satisfied locally. Publishing the mirror still requires
`git push origin mirror/upstream-2026-08-26:main --force-with-lease`, which the kickoff
prompt places outside this session's authority — it stops at the `loop-002-7` human gate.

### Verdict

`loop-002-4` and `loop-002-5` satisfied, on the sixth round, after the proof caught two
real defects in the deliverable — one a contradiction between two halves of the block, the
other a missing precedence claim over the skills the block steers. Both are fixed and both
fixes are re-proven, not asserted.

---

## loop-002-7 — the cross-model gate

**Date**: 2026-08-26. **Status**: reviews complete, **findings awaiting human resolution**.
This todo's gate is `human`, so nothing below is closed by the controller.

### Who reviewed, and who could not

`loop-002-7` asks for "a provider different from the implementer". The implementer of the
artefact under review — the fenced routing block — is **`claude`/Opus 5**, the controller.
`opencode`/Qwen3.5-397B ran the ACC-04/ACC-05 behaviour rounds but wrote none of the block.

The intended rotation was away from `codex`, which had already served as the gate reviewer
for phase 4 twice (`phase-4-attempt-1-codex.json`, `-attempt-2-codex.json`). **Both fresh
kinds refused to start unattended**, in an ordinary long-used checkout rather than the fresh
worktree the known hazard describes:

| kind | dialog | herdr's report |
|---|---|---|
| `gemini` | "Please enter your Gemini API key" — no stored credential on this machine | `idle`, `interactive_ready: true` |
| `cursor` | full-screen "Workspace Trust Required" for `~/Coding/Advanced-AI-Workflows` | `idle`, `interactive_ready: true` |

Neither dialog was answered — a `blocked` agent is the user's to clear, and a trust
decision is not the controller's to make. Both are recorded as **B11** in
`~/Coding/herdr-ops/FINDINGS.md`, together with the fact that gemini now shows the same
state mis-detection already logged for cursor in B2. The practical consequence is worth
stating plainly: of five kinds, **only `opencode` and `codex` can be dispatched without a
human at the keyboard**, so "rotate the reviewer across kinds" has a real fleet of two.

So the gate ran on both of them, in parallel, from one envelope, byte-identical:

| | reviewer 1 | reviewer 2 |
|---|---|---|
| kind | `codex` | `opencode` |
| model **claimed** | `gpt-5.6-sol` | `Qwen/Qwen3.5-397B-A17B-FP8` |
| model **actual** | `gpt-5.6-terra`, effort `medium` | `Qwen3.5-397B` via the Edinburgh ELM proxy |
| verdict | PASS WITH FINDINGS | PASS WITH FINDINGS |

**codex misreported its own model.** `argv` was `["codex"]` with no `-m`, the pane banner
read `model: gpt-5.6-terra medium`, and `~/.codex/config.toml` pins
`model = "gpt-5.6-terra"` / `model_reasoning_effort = "medium"`. Three independent
out-of-band sources against one self-report; the self-report loses. This is the argument
for reading `argv` rather than asking a worker what it is, demonstrated rather than
asserted.

The envelope asked five questions and forbade writing any file. It asked Q1 in the exact
terms the loop requires — *whether the fenced block over-reaches into user instructions* —
and Q5 in the terms the loop requires: *mirror, or a justified patch*.

### Where they agree

**Q3, host-neutrality — no change needed, unanimously.** No `.claude/`, `.cursor/` or
`.opencode/` path; no host-specific permission syntax; and `AskUserQuestion` is correctly
presented as *an example with a stated fallback* rather than a requirement. Qwen's verdict
was "What should change: Nothing." That is the direct vindication of the SP-3 decision to
put the structured-question preference in the block instead of patching the fork.

**Q5, mirror or patch — publish as a pure mirror, retain nothing, unanimously.** codex
independently re-ran the mirror comparison in the superpowers checkout and confirmed zero
commits in either direction and an empty tree diff. Qwen made the sharper argument: the
patch was never about code, it was about routing authority, and an instruction file read
before any skill loads is exactly the right place for that — so a patch inside the fork
would be redundant rather than merely burdensome. Neither could name an intent that could
not be expressed as an instruction.

**Q4, the proofs — sound method, one shared reservation.** Both credited the pre-run hash
baselines over worker self-reporting, the two fixtures differing only in the manifest, the
decoy that distinguishes data from an installation, and six rounds that found two genuine
defects and were rerun after the fixes. Both then refused to believe the same thing, from
different angles:

- codex: the evidence covers **the opencode harness only**, so run the same fixtures under
  Claude Code.
- Qwen: the fixtures' `AGENTS.md` was **placed by the controller**, so what is proven is
  that the block works when present — not that `aaw init` puts it there and that it
  survives to a fresh session. Its demanded check is a fresh project initialised *by the
  installer*, then a fresh agent given the same envelope with no controller intervention.

Qwen's is the stronger check and it subsumes codex's: it tests the delivery mechanism
end-to-end rather than the block's readability. Both corroborate the limitation already
recorded as an open item after `loop-002-5`, which was reached independently here.

### Where they disagree — and the disagreement is the finding

On **Q2, the installed-or-not test**, the two reviewers contradict each other.

- **codex**: front-door rules **1, 2, 3, 4, 6 and 7** invoke a companion tool's command with
  no manifest gate at all, and can therefore fire where the manifest says absent, missing or
  malformed. Only rule 5 is gated, and only because F1 forced it.
- **Qwen**: "The Front-Door Rules (1-7) all either explicitly gate on *When Advanced
  Planning is installed* (rules 2, 3, 5, 7) or are unconditional by design (rules 1, 4, 6)."

They cannot both be right, so the controller read the lines rather than choosing a
reviewer. **codex is correct and Qwen's sentence is false.** At
`claude-md-routing.md:42-86`, rules 2, 3 and 7 invoke `/plan-and-phase`, `/new-phase` and
`/run-gate` with no gate of any kind; rule 5 alone carries the predicate. Qwen's claim is
recorded in its verdict file under `disputed_claims` with the check that refutes it.

That is what a second and third pair of eyes is for, and it is also why one reviewer is not
enough: taken alone, Qwen's Q2 would have closed this gate with a clean bill on the very
thing that is wrong.

Qwen was not merely wrong, though — it found a real instance **codex missed**: the
**Companion Tools** section at `:152-159` reasons about "a project where Advanced Planning
is installed and `superpowers` is not" without restating the manifest-read discipline, and
ties it precisely to the `borrowed.md` decoy. It is a near-variant of the phrase line 36
binds, so it is weaker than Qwen rates it, but it is real.

**A third instance neither reviewer named**, found while checking theirs: the **Closing
Instruction** at `:164-171` says "AFTER any gstack planning skill writes a design doc,
invoke `/gstack-to-plans`" and points at `~/.gstack/projects/{slug}/` — unconditional, in a
project that may have no gstack.

So the finding is bigger than either reviewer stated, and it has a name: **F1 was fixed as
an instance when it was really a class.** The block's own lines 32-34 say that a missing or
malformed manifest means treat every component as not installed and follow plain upstream
behaviour — and then eight separate routes never consult it.

### The findings, consolidated

| # | severity | location | finding | raised by | controller check |
|---|---|---|---|---|---|
| R1 | **major** | `:42, :47, :53, :59, :73, :79`, `:152-159`, `:164-171` | eight routes name a companion command with no manifest gate; F1 fixed the class's one known instance | codex (6 sites), Qwen (1 further site), controller (1 further site) | **CONFIRMED by reading the lines** |
| R2 | minor / major | `:94-99` | the precedence claim over skill defaults is broader than the three additions it exists to protect | **both**, independently | real; the saving clause at `:95-99` already limits it, so the practical risk is low and the fix is one clause. codex rates minor, Qwen major |
| R3 | minor | `:111` | cosmetic: name the harness-neutral equivalent alongside `AskUserQuestion` | Qwen (codex: leave as is) | optional; both agree the current shape is already host-neutral |
| R4 | minor | evidence, method | the proofs cover one harness, and the fixture's instruction file was placed by hand rather than by `aaw init` | **both**, from different angles | already an open item; the reviewers reached it independently and Qwen sharpened it |

R1 is the one that matters. It is the same defect class as F1, in eight more places, and it
was invisible to the six ACC rounds because every fixture had all three components either
installed or explicitly absent in a well-formed manifest — the malformed and missing-file
cases the block legislates for were never exercised.

### Verdict

`loop-002-7` is **not closed**. Two providers different from the implementer are named and
recorded, both returned PASS WITH FINDINGS, both answered the over-reach question the loop
requires, and both answered the mirror-or-patch question the same way: **the fork ends as a
pure mirror, retaining no patch, and the measured patch is zero**.

What remains is the part the loop assigns to the human: the resolution or waiver of each
finding, and the authorisation to publish the mirror — which needs
`git push origin mirror/upstream-2026-08-26:main --force-with-lease` in the superpowers
repository, outside this session's authorised set.
