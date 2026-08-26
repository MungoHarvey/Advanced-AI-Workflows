# Phase 4 loop 002 — AAW packaging repair

**Collected:** 2026-08-26
**Branch:** `feat/aaw-packaging-repair`, head `3b0c6214ba7025e91c5cd4834c3770e9022b8713`
**Base:** `e5082037e4d5a007c1a8ccd0a3753ab5239ae667` on `docs/herdr-v0.2-import`
**Worktree:** `C:\Users\mharvey2\Coding\aaw worktrees\aaw-packaging-repair`, workspace `wA`, owner `herdr`
**Pushed:** no. This branch is local only and has never been sent to a remote.

**Result: the documented install set is now complete in a fresh clone, and a test now fails if it
stops being complete.** The `.gitignore` change admits exactly one directory and nothing else.

---

## 1. The defect

`README.md` and `SETUP.md` tell a user to install two skills. Only one of them was in the
repository. A fresh clone therefore could not deliver what the documentation promised, and nothing
in the project noticed.

`git check-ignore -v` named the cause without ambiguity:

```
.gitignore:12:.claude/skills/*    .claude/skills/gstack-to-plans/SKILL.md
```

Line 11 re-included `.claude/skills/`, line 12 excluded its contents again, and line 13 whitelisted
`setup-with-claude/` alone. The glue skill was never named, so it was never trackable.

**It was never tracked, as opposed to deleted.** `git log --all -- .claude/skills/gstack-to-plans/*`
returns nothing: the path is absent from the entire history on every ref. There was no earlier good
version to restore from, which is why the only available source was the deployed copy at
`~/.claude/skills/gstack-to-plans/SKILL.md`.

---

## 2. The four commits

| SHA | Subject |
|---|---|
| `0e145c7` | `fix(packaging): track the gstack-to-plans glue skill` |
| `692b7be` | `test(packaging): fail the build when a documented install source is missing from a fresh clone` |
| `67ae688` | `chore(packaging): pin the manifest to LF, and retire the notices the fix made false` |
| `3b0c621` | `docs(packaging): stop the LF pin claiming a failure mode that was disproved` |

`git status --porcelain` in the worktree is empty at `3b0c621`.

---

## 3. The whitelist widening, and the proof it does not over-widen

The exclusion was kept and one directory was added beside the existing one:

```
.claude/*
!.claude/skills/
.claude/skills/*
!.claude/skills/setup-with-claude/
!.claude/skills/gstack-to-plans/
```

The comment above it states the rule this loop is defending: never relax `.claude/skills/*`
wholesale, because this machine's local skill collection lives in the same tree. Adding a skill to
the product means adding one line, deliberately.

Probed at `3b0c621`, from the controller, after the fix:

| Path | `check-ignore` exit | Rule |
|---|---|---|
| `.claude/skills/gstack-to-plans/SKILL.md` | 1 — **not ignored** | — |
| `.claude/skills/some-local-skill/SKILL.md` | 0 — still ignored | `.gitignore:15:.claude/skills/*` |
| `.claude/settings.json` | 0 — still ignored | `.gitignore:13:.claude/*` |

`git status --porcelain` after the `.gitignore` edit alone showed only `.gitignore` itself as
modified. **No other file became visible.** The full tracked set under `.claude/` is seven files:
the six `setup-with-claude` files and the one new glue skill.

The independent reviewer reached the same answer by its own probes — see §7.

---

## 4. Provenance of the restored skill

Copied from the deployed installation, not reconstructed:

| | |
|---|---|
| Source | `C:\Users\mharvey2\.claude\skills\gstack-to-plans\SKILL.md` |
| Size | 3912 bytes |
| mtime | `2026-06-16 23:28:28.888666200 +0100` |
| md5 | `3fc4d9cca4f5d93296fde2febe914292` |
| Byte comparison | `cmp` reports IDENTICAL |
| Directory contents | pure markdown; zero non-`.md` files |
| Frontmatter | `name: gstack-to-plans` |

A note on method: `md5sum` was initially read as reporting two different hashes for the two copies.
It was not — `md5sum` escapes a Windows path with a leading backslash on one of its output lines, so
`awk '{print $1}' | sort -u` saw two distinct strings for one hash. `cmp` and `md5sum < file` settle
it.

### Contract gap, recorded rather than repaired

Phase 1 accepted this skill on the basis that it carried **explicit `AskUserQuestion` callouts at
all three ambiguous branches**. The deployed file contains **zero** occurrences of the string
`AskUserQuestion`. Two of the three branches (source-selection, destination-exists) exist as prose
only; the third (unexpected-pattern) is absent entirely.

The file was committed **verbatim** anyway. Rewriting it while importing it would have destroyed the
provenance this loop exists to establish, and would have made the gap invisible. The gap is a
separate piece of work, on the record, not folded into a packaging fix. The reviewer independently
confirmed the gap statement is accurate.

---

## 5. The packaging test

`tests/packaging/test-fresh-clone.sh` with `tests/packaging/required-sources.txt`.

It clones the repository into a `mktemp -d` directory with `git clone --quiet --no-hardlinks
--no-local`, checks out the requested ref, reads `git ls-files` from that clone, and checks each
manifest path for MISSING / EMPTY / UNTRACKED. It reports **every** failure rather than stopping at
the first. Exit 0 = all present, 1 = at least one failure, 2 = fatal. `--repo`, `--ref` and `--keep`
are supported.

Nine paths are required: the six `setup-with-claude` files, the glue skill, `README.md`, `SETUP.md`.
The manifest header explicitly warns *not* to list `.claude/skills/gstack/`, `brainstorming/` or
`phase-plan-creator/`, because those belong to the user's project after installing third-party
tools and are not this repository's to ship.

### Proven in four directions, not assumed

| Case | Result |
|---|---|
| HEAD | **exit 0**, 9/9 present |
| `--ref e508203` — the real commit immediately before the fix | **exit 1**, `MISSING .claude/skills/gstack-to-plans/SKILL.md` |
| scratch clone with the skill `git rm`'d | **exit 1** |
| scratch clone with `SETUP.md` truncated to zero bytes | **exit 1**, EMPTY |

The second case is the strongest of the four because nothing is fabricated: it is the repository's
own history, one commit earlier, failing for the real reason. Both scratch clones were made in
temporary directories and deleted. **No deliberately broken commit was ever made on a real branch.**

---

## 6. Line endings, and a guard that was removed after being tested

`core.autocrlf=true` on this machine. `.gitattributes` gained `tests/packaging/*.txt text eol=lf`.
`git ls-files --eol` reports `i/lf w/lf` for both files under `tests/packaging/`.

A CR-stripping guard was added to the manifest reader first, on the assumption that a CRLF manifest
would break it. That assumption was **tested and disproved**: an unguarded copy of the script passed
cleanly against a deliberately CRLF'd manifest, because the reader's existing
`sed 's/[[:space:]]*$//'` already strips a carriage return. Worse, the guard's own source had
written a raw CR byte into a `.sh` file that `.gitattributes` pins to LF — exactly what the pin
exists to prevent. The guard was removed. The pin was kept, with its justification corrected to the
true one.

`3b0c621` exists because that correction was made in two places and not the third — see §7.

---

## 7. Independent cross-model review (ACC-18)

| | |
|---|---|
| Implementer | Claude Opus 5, `claude-opus-5[1m]` — the controller |
| Reviewer | codex, pane footer `gpt-5.6-terra medium`, agent `pkgreview` in workspace `wA` |
| Differ? | **Yes** |
| Pass 1 | **FAIL**, `OVER-WIDENS: no`, 2m 11s |
| Pass 2, after the fix | **PASS**, no findings |

The reviewer ran its own checks rather than reading the implementer's claims. It located Git for
Windows itself after the sandboxed `bash` resolved to a blocked WSL shim, and it escalated twice for
permission to run the packaging test outside the sandbox because the test needs shared memory to
create its temporary clone. Both escalations were granted **one-shot**; the offered
"don't ask again" option was refused both times, because that broadens permissions and this
programme does not broaden permissions to save a round-trip.

Its independent results: `HEAD_EXIT=0`, `PREFIX_EXIT=1`, ignore probes matching §3 exactly,
md5 and byte comparison matching §4, the clone-into-`mktemp` mechanism confirmed by reading the
script, and the `AskUserQuestion` gap confirmed as accurately stated.

### The finding, and why it was accepted

> `.gitattributes` falsely claims CRLF manifest paths could fail the test; the script's
> trailing-whitespace sed removes CR, contradicting `67ae688`'s claim that the comment is accurate.

**Re-derived by the controller before acceptance**, per phase 3's F3 rule that a reviewer's verdict
is evidence only after the claims underneath it are checked. The comment above the pin read
*"which could turn a passing packaging test into a stream of MISSING for files that are present"*.
`printf 'foo/bar.md\r' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | od -c` emits no CR. The claim
is false, and `67ae688` had corrected the same claim in its commit message and in the comment at the
reader while leaving the `.gitattributes` comment carrying the pre-correction wording. Two comments
about one fact disagreed, and the one a reader meets first was the wrong one.

Fixed in `3b0c621`: the pin is kept, its justification restated as making the LF requirement
explicit so the next parser added here need not depend on a side effect of a sed. The packaging test
was re-run after the edit — exit 0, 9/9 — and the reviewer re-ran it itself from the committed tree.

### A correction the reviewer made to its own report

Pass 1 reported `MODEL: gpt-5.6-sol`, which conflicts with the pane footer `gpt-5.6-terra medium`.
Asked directly, it answered *"unknown — I cannot determine the exact runtime model id"* and named
the conflict rather than defending its first answer.

**Consequence for ACC-18, stated plainly: an agent's self-reported model id is not evidence.** The
observable identity is the runtime the controller started (`--kind codex`) and the pane footer the
controller can read. Both are recorded above; the self-report is not. This does not weaken the
review — the reviewer is demonstrably not the implementer either way — but any future ACC-18 check
that relies on an agent naming its own model would be relying on something this loop just watched
fail.

---

## 8. What this does not establish

- **The branch is unmerged and unpushed.** `main` still ships an incomplete install set. `README.md:7`
  and `SETUP.md:9` currently say the blocker is fixed on this branch and stands on `main`; both need
  one further edit when it lands.
- **The `AskUserQuestion` contract gap is open**, not closed. §4.
- **The test checks presence, not correctness.** A file that exists, is tracked, and is non-empty
  passes. It does not check that the skill does what the documentation says it does — the gap in §4
  is exactly the kind of thing this test cannot see, and would not have caught.
- **`.aaw/installed.json` does not exist yet.** Detecting an installation still probes
  `.advanced-plans/`, so a stale data directory alone still reads as installed (ACC-02). That is
  loop 003.
