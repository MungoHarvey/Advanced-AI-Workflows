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
