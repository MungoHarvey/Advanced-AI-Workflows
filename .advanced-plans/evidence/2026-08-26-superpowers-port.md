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
