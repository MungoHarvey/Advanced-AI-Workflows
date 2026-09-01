# Phase 5's gate verified the repository. The machine still runs the patch.

**Date:** 2026-09-01
**Found by:** a routine post-fetch re-verification of the superpowers mirror publish
**Status:** measured, not acted on — the remedy is a decision, not a cleanup

---

## What Phase 5 claimed

Phase 5 passed its gate on 2026-08-26 on this claim, restated in the publish record:

> *"MungoHarvey/superpowers is now a clean mirror of obra/superpowers. It carries no patch on
> any branch, and the behaviour the patch used to provide is delivered by the AAW fenced
> block, which this push does not touch."*

The first sentence is true. The second is not true on this machine.

## What is actually installed

Digest comparison of the two files the port touched:

| File | live `~/.claude/skills/` | fork head `fde9f97` | clean mirror `b36e082` | official plugin 6.1.1 |
|---|---|---|---|---|
| `brainstorming/SKILL.md` | `307a023e6f1000c4` | **`307a023e6f1000c4`** | `74edf03ea6d24ef5` | `e14914605f640e08` |
| `using-superpowers/SKILL.md` | `c80ce1ff9188e391` | **`c80ce1ff9188e391`** | `30f2ab78e20ddc27` | — |

Both live files are **byte-identical to `fde9f97`** — the pre-port patched fork head, the exact
commit the 2026-09-01 force-push overwrote on the remote. They carry no AAW fence markers.
This is a raw fork patch installed at the user level, not an overlay.

The patch body is still visible at `~/.claude/skills/brainstorming/SKILL.md:30,123`, routing
design docs to `.advanced-plans/specs/` when `.claude/skills/phase-plan-creator/SKILL.md`
exists — itself a Claude-only sentinel, the same hardcoding class as `.aaw/detect.py`.

## What is not installed

| Thing Phase 5 relies on | State |
|---|---|
| the `aaw-routing` fenced block in any `CLAUDE.md` / `AGENTS.md` | **installed nowhere** — checked the global file and every project checkout on this machine |
| `.aaw/installed.json`, the Phase 5 consumption predicate | **does not exist** — `.aaw/` holds only `detect.py`, `installed.example.json`, `installed.schema.json` |
| AAW's own `CLAUDE.md` / `AGENTS.md` | **do not exist** |

The fenced block exists only as a template, at
`.claude/skills/setup-with-claude/references/claude-md-routing.md`. It has never been applied.

## The defect

Phase 5's gate evidence is a set of `git` measurements taken **inside the repository** —
`rev-list`, `diff --stat`, digest equality between `mirror/upstream-2026-08-26` and
`upstream/main`. Every one of them is correct. None of them is about the machine.

**The claim was about what is delivered; the check was about what is committed.** This is the
programme's central defect class — a check whose subject is a string or a tree rather than the
running system — at the largest scale it has so far appeared, because it is the premise the
whole dependency-not-forks direction rests on.

Two corollaries worth stating:

- The publish's own post-verification recorded *"AAW packaging suite PASS 4/4, idempotency
  suite PASS 56/56."* Both suites passed on a machine where the patched skill was live. They
  therefore **cannot distinguish patched from unpatched**, which is what a suite guarding this
  boundary would have to do.
- The local checkout at `C:/Users/mharvey2/Coding/superpowers` is still on `main` at `fde9f97`,
  diverged `4 / 241` from the published `origin/main`, working tree clean. Recoverable in both
  directions — the backup tag is on the remote — but it is the patched tree, and the record
  says the fork carries no patch on any branch.

## What is *not* wrong

- The mirror publish itself is sound. `origin/main` = `upstream/main` = `b36e082`, re-verified
  after a fresh fetch today; the backup tag `pre-aaw-port-2026-08-26` (`071000c` -> `fde9f97`)
  is intact on the remote, so the pre-port head is recoverable without this machine.
- Nothing is broken right now. The behaviour works — it is simply being delivered by the
  mechanism Phase 5 said had been retired, not the one it said had replaced it.

## The live risk

The patched skills and the clean plugin copy (`superpowers 6.1.1`) both exist on disk. Any
reinstall from the now-clean mirror, or any resolution that prefers the plugin copy, removes
the AP-detection behaviour **with nothing installed to replace it**, because the fenced block
that was supposed to replace it has never been applied anywhere.

## Options

1. **Install the fenced block, then clean the skills** — makes Phase 5's claim true, in that
   order so behaviour never lapses.
2. **Keep the patch, amend the record** — accept the fork patch as the delivery mechanism and
   correct Phase 5's gate evidence and the publish record to say so.
3. **Record only** — leave both as they are, with this note as the correction.

## Carried

- Whichever option is taken, **Phase 5's gate evidence needs a machine-state check**, not only
  repository measurements. A gate that cannot fail when the machine contradicts the repo is not
  guarding this boundary.
- `.aaw/installed.json` does not exist, so the Phase 5 predicate
  `components["<name>"]["installed"] == true` currently reads a missing file. Whether that is
  by design (produced at install time) or a gap should be settled before Phase 7 builds
  manifest-driven detection on top of it.

---

## Resolved: there is no contest. The plugin is switched off.

Measured after the question above was raised.

`superpowers@claude-plugins-official` version 6.1.1 is present in
`~/.claude/plugins/installed_plugins.json` and **absent from `enabledPlugins` in
`~/.claude/settings.json`** — installed, not enabled. The clean plugin copy is inert.

So nothing shadows anything. **The patched user-level skills are the sole live copy of
superpowers on this machine**, and the patch is not a latent risk — it is what runs.

### And they are unmanaged, and stale

The live copies are a real directory, not a symlink to the checkout and not a plugin
install. Nothing updates them. Last written **2026-06-16** — two and a half months ago.

| | live (`fde9f97`) | current upstream (`b36e082`) | differing lines |
|---|---|---|---|
| `brainstorming/SKILL.md` | 207 lines | 250 lines | **197** |
| `using-superpowers/SKILL.md` | 137 lines | 63 lines | **110** |

The live skills predate **241** upstream commits, **43** of which touch these two files.
`using-superpowers` was cut from 137 lines to 63 upstream — a rewrite, not a drift.

### Why this matters beyond Phase 5

This is the concrete instance of the problem that opened the programme:

> *"editing forks and the packaged dependencies requires constant updating to the specific
> tools inside those but that can be clunky and could require heavy adjustment each update"*

A hand-copied, hand-patched skill directory with no provenance marker, no version pin, and no
update path is exactly the failure mode the dependency-not-forks direction exists to end. It
went stale silently for two and a half months, and no check in the programme noticed — because
every check looks at repositories.

### What this does to the options

Option 3 ("record only") is weaker than it looked: the cost is not a hypothetical future
reinstall, it is 43 commits of upstream work already missed and accruing.

Option 1 ("install the block, then clean") is correspondingly stronger, and it now has a
second half worth naming: once the fenced block delivers the routing, the skills themselves
should come from a **managed** source — the enabled plugin, or a pinned checkout recorded in
the compatibility manifest of section 13.2 — rather than a hand-copy.

---

## Executing "managed source + fenced block": what the work found

### The manifest is not produced by `detect.py`

`.aaw/detect.py` is a library — no `main`, no `__main__`, no argparse, no output. It is driven
by `tools/aaw-audit.py` (`load_detect()` -> `detect.detect(project, home=home)`). The manifest
is written by the `setup-with-claude` skill **at install time**, which the dependency plan
already records at `specs/2026-09-01-dependencies-not-forks-plan.md:50`. So the fenced block
cannot simply be pasted into a `CLAUDE.md`: the designed path is to run the installer skill,
which writes `.aaw/installed.json` and installs the block together.

Live audit of the controller checkout, `python tools/aaw-audit.py`, exit 1:

```
advanced-planning  installed   global   ...\.claude\skills\phase-plan-creator
gstack             installed   global   ...\.claude\skills\gstack
gstack-to-plans    installed   project  ...\.claude\skills\gstack-to-plans
plannotator        deprecated  none     -
superpowers        installed   global   ...\.claude\skills\brainstorming

FINDINGS (1)
  [manifest-absent] .aaw\installed.json does not exist. Detection fell back to
  sentinel probing, which is correct but records nothing for the next reader.
```

### The blocker: removing the hand-copy turns the routing off

`detect.py:116-122` recognises superpowers at exactly two paths:

```
("project", <project>/.claude/skills/brainstorming, .../SKILL.md)
("global",  <home>/.claude/skills/brainstorming,    .../SKILL.md)
```

**The sentinel for superpowers is the hand-copy itself.** A plugin install lives at
`~/.claude/plugins/cache/claude-plugins-official/superpowers/<version>/skills/brainstorming/`
and is not probed at all.

So the chosen sequence does not survive its own last step. Remove the hand-copy and
`detect.py` reports superpowers **MISSING**; the manifest then says not-installed; and the
fenced block — which is explicit that a missing or negative manifest means *treat every
component as not installed* (`claude-md-routing.md:32`) — declines the routing. That is exactly
the lapse the block-first ordering was chosen to prevent, arriving one step later than expected.

**Detection must learn the plugin location before the hand-copy can go.**

There is a design question inside that, and it is this programme's own defect class again: an
installed-but-**disabled** plugin still has a directory on disk. `superpowers@claude-plugins-official`
is in `installed_plugins.json` and absent from `enabledPlugins` right now — present as a path,
absent as a capability. A sentinel that probes only the path would report a disabled plugin as
installed, which is a check that cannot fail. Correct detection has to read `enabledPlugins`.

### Reversibility, proven before proposing any removal

Every file in both live skill directories was compared against `fde9f97`:

| Directory | live files | in `fde9f97` | digest result |
|---|---|---|---|
| `brainstorming` | 8 | 8 | 6 identical; `scripts/frame-template.html` and `scripts/server.cjs` differ **by line endings only** (CRLF locally, LF in git) |
| `using-superpowers` | 4 | 4 | all identical |

Normalising line endings, both directories are byte-for-byte recoverable from `fde9f97`, and
that commit is preserved by the annotated tag `pre-aaw-port-2026-08-26` **on the remote**. No
local backup is needed; removal would be reversible without this machine.

### Remaining sequence

1. Teach detection to recognise a plugin-scoped superpowers — reading `enabledPlugins`, not
   just probing the cache path. **Blocks everything after it.**
2. Enable `superpowers@claude-plugins-official` in `~/.claude/settings.json`. Only the operator
   can do this; the classifier correctly refuses agent edits to that file.
3. Run `setup-with-claude` to write `.aaw/installed.json` and install the fenced block.
4. Remove the hand-copy at `~/.claude/skills/{brainstorming,using-superpowers}`.

---

## Step 1 done: detection now reads the switch, not the cache path

Commit `12de222` on `docs/herdr-v0.2-import`. Local only.

`.aaw/detect.py` gained a **plugin scope**, general across components rather than special-
cased for superpowers. A location may now be `{"scope": "plugin", "plugin": <key>,
"sentinel": (<parts>,)}`, and it counts only when the plugin is **enabled**. Rule 5 states
why: a plugin's files sit in the cache whether it is switched on or off, so a path probe
reports a disabled plugin as installed on every machine where it was ever installed. That is
the programme's own defect class, and it would have been introduced by the obvious fix.

Two readers were added, both read-only: `enabled_plugins(home)` over
`~/.claude/settings.json`, where only an explicit `true` counts, and
`plugin_install_paths(home)` over `~/.claude/plugins/installed_plugins.json`. The install
path is read from the harness's own registry rather than reconstructed from the cache
layout, because that path carries a version segment (`.../superpowers/6.1.1/`) that changes
on every upgrade; a guessed path would go stale silently.

Path locations still outrank plugin ones, so a hand-copy is reported as the thing in force —
which is what the harness actually loads. A component whose plugin files are present but
switched off reads MISSING, correctly, and now carries the reason, which `aaw-audit.py`
surfaces as `[plugin-present-not-enabled]`.

### The test can fail, and was made to

`tests/packaging/plugin_detection.py`, wired into `run-all.sh` as
`test-plugin-detection.sh`. Eight fixture cases against fake homes, plus the audit CLI end
to end. Fixtures mirror the real registry's shape, including the `"scope": "project"` and
`projectPath` the live superpowers entry carries, so a case cannot pass on a shape reality
does not use.

The last case is the one that matters. It reads `detect.py`, asserts the enabled gate
appears exactly once, removes it, loads the mutant, and re-runs the disabled-plugin case
against it. **If the mutant still reported MISSING, the gate would not be what produced the
earlier answer and every case above it would be decorative** — the file says so in those
terms. The mutant does flip to installed.

Proven both directions before the commit:

| Probe | Result |
|---|---|
| `test-plugin-detection.sh` | PASS 10/10, exit 0 |
| a deliberately broken expectation in a throwaway copy | **FAIL 9/10, exit 1** — the runner reports, it does not pass quietly |
| `run-all.sh` | PASS 5/5 (was 4/4) |
| `python tools/aaw-audit.py` on this checkout | **byte-for-byte the output recorded above** — the hand-copy is still found first |

### What the real machine says now

Run against the live profile, not a fixture:

```
enabled plugins read from settings: 13
superpowers enabled?                False
superpowers install paths:          ...\.claude\plugins\cache\claude-plugins-official\superpowers\6.1.1
  sentinel exists:                  True
resolve ->                          (None, 'superpowers@claude-plugins-official')
```

Present as a path, absent as a capability — exactly the state rule 5 was written for. The
moment the plugin is enabled, that resolve returns the 6.1.1 path and detection reports
superpowers `installed`, `scope: plugin`, with no hand-copy needed.

### Where the sequence stands

1. ~~Teach detection to recognise a plugin-scoped superpowers.~~ **Done, `12de222`.**
2. **Enable `superpowers@claude-plugins-official`.** Blocked on the operator: the classifier
   correctly refuses agent edits to `~/.claude/settings.json`.
3. Run `setup-with-claude` to write `.aaw/installed.json` and install the fenced block.
4. Remove the hand-copy at `~/.claude/skills/{brainstorming,using-superpowers}`.

### Limit recorded rather than papered over

Only `<home>/.claude/settings.json` is read. A plugin can also be enabled in a project's own
settings, and the live superpowers registry entry is `"scope": "project"` against
`Coding/microglia-cadino`. Detection ignores both, so a plugin enabled only for some other
project reads as not enabled here. That is the conservative direction and it is the one the
routing block needs — but it is a limit, not a proof of correctness, and it is stated in the
test's own docstring so the next reader finds it there too.
