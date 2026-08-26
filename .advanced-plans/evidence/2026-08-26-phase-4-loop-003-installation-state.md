# Phase 4 loop 003 — making installation state knowable

**Collected:** 2026-08-26
**Branch:** `feat/aaw-packaging-repair`, head `360ab3c`
**Base:** `3b0c621` (end of loop 002), on top of `e508203` on `docs/herdr-v0.2-import`
**Worktree:** `C:\Users\mharvey2\Coding\aaw worktrees\aaw-packaging-repair`, workspace `wA`, owner `herdr`
**Pushed:** no. This branch is local only and has never been sent to a remote.

**Result: installation state is now a thing a machine can read, disagree with, and fail on.**
A manifest records what is installed and where; detection no longer treats a data directory as
an installed component; an audit answers the question without a conversation; and the install
surface is proven to behave the same on the second run as on the first.

The cross-model review of loops 002 and 003 together took four passes. It returned FAIL three
times and PASS on the fourth. Every finding in every pass was re-derived by the controller before
it was accepted, and every fix was proven to fire before it was believed.

---

## 1. The five todos

| Todo | Commit | What it produced |
|---|---|---|
| `loop-003-1` | `11fb8a4` | `.aaw/installed.schema.json`, an example manifest, a validating test and a fixture corpus |
| `loop-003-2` | `6e94cf5` | `.aaw/detect.py`, and the rewrite of the detection half of `setup-with-claude` |
| `loop-003-3` | `3ae6121` | `tools/aaw-audit.py` and `tests/packaging/test-audit.sh` |
| `loop-003-4` | `8f7b008` | `tests/packaging/project_ops.py` and `tests/packaging/test-idempotency.sh` |
| `loop-003-5` | `1307aa4`, `2cf86fe`, `360ab3c` | the four review passes and the three fix packs that answered them |

### The checks each todo was given, and what happened

**`loop-003-1` — "the schema is validated by a test, not merely documented".** It is:
`tests/packaging/validate-manifest.py` runs two validators over a corpus of 24 fixtures and fails
if they disagree. The built-in validator refuses to run rather than silently ignore a schema
keyword it does not implement. **"Every path recorded is absolute and native Windows, with no `~`
and no `HOME`":** four of the fixtures exist to make that fail — `invalid-relative-path.json`,
`invalid-env-var-path.json`, `invalid-absent-with-stale-path.json`, `invalid-scope-none-but-installed.json`.

**`loop-003-2` — ACC-02.** A temporary project containing only a stale `.advanced-plans/` reports
the data present and the component absent, in the same line of output. The audit test asserts it:
`ok  ACC-02: data present and component MISSING, reported together`.

**`loop-003-3` — "the same input produces the same output twice".** The audit takes `--home` and
`--now` so that both of its environmental inputs are arguments. The docstring says plainly that
without `--home` the live profile is read and becomes one of the inputs the determinism is relative
to; the tests always pass it.

**`loop-003-4` — ACC-16, uninstall, and reinstall.** `test-idempotency.sh` is 43 checks over nine
stages against a temporary project and a fake profile. Install is run three times, not twice,
because on a first install "append" and "replace" are the same operation and a two-run test cannot
tell them apart.

---

## 2. The provider deviation, stated rather than glossed

`loop-003-4` specifies `provider: "codex or opencode"`. **Claude implemented it.** That is a
deviation from the plan and it is recorded here rather than in a footnote.

The property the plan was buying with that line is the cross-model one — that the work is not
checked only by the model that wrote it — and that property is preserved, because `loop-003-5`'s
reviewer is codex and it reviewed `project_ops.py` and `test-idempotency.sh` in four passes. It
found three real defects in exactly that file (see §4), which is the outcome the todo's provider
line was trying to make possible. What is lost is independence of *authorship*: had codex written
the idempotency scaffolding, a Claude reviewer would have been reading unfamiliar code rather than
its own.

This is offered as a fact for the human gate to accept or reject, not as a conclusion.

---

## 3. Scoping decision: `project_ops.py` is scaffolding, and the skill is the specification

`setup-with-claude` is a skill — prose a model follows — so there was nothing executable to run an
idempotency test against. `tests/packaging/project_ops.py` performs the file operations the skill
documents so that repeating them can be asserted.

Its module docstring says what that makes it:

> This is test scaffolding. If it and the skill disagree, that is a finding about one of them,
> and the skill is the specification.

The reviewer used that stance to locate three defects in `project_ops.py` rather than in the skill
(C1, C2, C3 below) — and then, in a later pass, one place where the skill itself was the half that
was wrong. Both directions were exercised, which is the argument that the stance was the right one
to declare up front.

---

## 4. The review — four passes, reviewer `gpt-5.6-terra`

**ACC-18 is satisfied on observable evidence.** The reviewer is a codex agent named `pkgreview`
started in workspace `wA` with `--kind codex`; its model reads `gpt-5.6-terra medium fast` from the
pane footer. It was instructed not to state its model name, and none of the four verdicts rests on
a self-report. The implementer is Claude. The two differ.

Scope reviewed: `e508203..HEAD` — loops 002 and 003 together as one packaging change, which is what
the todo asks for.

### Pass 1 — VERDICT: FAIL, 11 findings

Every one was re-derived by the controller before acceptance. **All 11 held.** Closed in `1307aa4`.

| Id | Finding | How it was proven |
|---|---|---|
| F1 | `"components": 1` crashed the audit — exit 2, `'int' object is not iterable` | reproduced, then fixed to exit 1 `[manifest-invalid]` |
| F2 | a manifest naming an unrelated file as advanced-planning reported `HEALTHY`, exit 0 | reproduced; new `manifest-mismatch` finding now exits 1 |
| C1 | `install_glue` rmtree'd an existing glue directory; Step 6 Case B says note it and continue | read against the skill; stage 7 now proves a `NOTES.md` beside the skill survives |
| C2 | uninstall continued after refusing `CLAUDE.md`, under a comment claiming the skill said so | the skill said the opposite; second time in this branch a comment asserted what its cited source did not |
| C3 | `uninstall_settings` deleted emptied arrays unconditionally; U6 says show the diff and ask | now refuses, names both arrays, changes nothing |
| B1 | fresh-clone only checked a curated list | UNDECLARED scan added; proven by removing the glue skill from `required-sources.txt` |
| B2 | every fixture had a boolean `installed` | five type fixtures added; proven by mutating `"boolean": bool` → `object` in the validator |
| B3 | `test-audit.sh` created `gstack-to-plans` and never asserted it | loop over all three components added |
| B4 | (folded into C1) | |
| A1 | `git clone` inherited the user's global config | `GIT_CONFIG_GLOBAL` / `GIT_CONFIG_SYSTEM` now `/dev/null` |
| F3 | fingerprints folded CRLF while the checks were labelled "byte-identical" | normalisation removed; the suite is still green, so the claim is now literal |
| F4 | `generated_at` was regex-only, so month 99 was accepted | `datetime.strptime` check added to the audit |
| F5 | the skill said `.claude/integrations.json` was "not this skill's file to delete" while U2/U5 removed it | contradiction resolved in favour of uninstall, and which half was wrong is written down |

### Pass 2 — VERDICT: FAIL, 3 PARTIAL + 2 new

Closed in `2cf86fe`. The pre-fix code was run from a clone of `1307aa4` and reproduced each defect
before it was fixed.

- **C2 PARTIAL.** A project with no `CLAUDE.md`, or one with neither marker, continued the
  uninstall — contrary to Step U1's "if EITHER marker is absent, STOP". **Resolved by changing the
  skill, not the code.** Read literally, U1 made an uninstall impossible to finish on a project
  with no `CLAUDE.md`: the recovery text tells the user to remove the block by hand and re-run, and
  there is no block to remove, so the second run stops where the first did. U1 now names three
  cases — both markers, neither, exactly one — and only the third stops. The reviewer was asked
  directly whether it agreed that was the half that was wrong; it did.
- **C3 PARTIAL.** The no-rewrite check compared serialised output against the file's bytes, so a
  four-space `settings.json` holding nothing of ours came back two-space. Reproduced against
  `1307aa4`, then fixed by comparing the parsed documents.
- **Adversarial.** An unrelated empty `PostToolUse`/`Write` matcher made `_survivors()` return empty
  and the Step U6 guard refuse an uninstall with nothing to remove — and, had it not refused, it
  would have deleted that stranger's entry. Both halves are one bug. `_survivors()` now keeps what
  is not ours, returns new dicts rather than editing in place, and is the single answer used by both
  the guard and the removal.
- **Adversarial.** The UNDECLARED scan skipped a documented path missing from the clone. That is the
  broken install source the scan exists to catch; it now fails as `MISSING`.
- **F4 PARTIAL.** The shipped schema and `validate-manifest.py` still accepted
  `2026-99-99T99:99:99Z`. JSON Schema cannot express the calendar check here, so `semantic_errors()`
  does it beside the schema — deliberately outside `validate_builtin()`, so `--self-check` keeps
  comparing the two validators on the same question.

### Pass 3 — VERDICT: FAIL, 2 PARTIAL + 1 new

Closed in `360ab3c`. Three of the five were confirmed FIXED.

- **F4 residue.** The skill still told a user without this repository that "any JSON Schema
  validator will do" — true of every field except the one the finding is about. The paragraph now
  says what a generic validator will and will not catch.
- **B1 residue.** The docs scan matched a fixed extension list. It now matches any extension.
- **New.** The `MISSING` branch cannot tell a source this repository ships from a path the docs name
  because an installer *writes* it in the user's project. Nothing in the prose distinguishes them,
  so the distinction is declared instead: `tests/packaging/documented-destinations.txt`.

### Pass 4 — VERDICT: PASS

> fresh clone: 13/13 PASS · manifest schema: 24/24 PASS · audit: 21/21 PASS ·
> idempotency: 43/43 PASS · overall: packaging: PASS - 4/4 checks

Run by the reviewer, in its own words, not quoted from the commit message.

**Two caveats the reviewer recorded rather than blocked on**, and its own words on whether they
should stop a pull request:

1. **B1 remains PARTIAL.** A documented source with **no extension at all** is still not matched.
   *"a small, transparent residual limitation rather than a regression."*
2. **`documented-destinations.txt` is an exception mechanism.** Somebody can add a real missing
   source to it and silence the scan; the required reason is a convention the parser does not
   enforce. *"a dedicated, tracked, initially empty allowlist whose additions are visible in code
   review… I would record this caveat and merge rather than block the PR."*

---

## 5. What was proven rather than asserted

- **The idempotency test was proven capable of failing** before it was trusted: two deliberate
  mutations in a temporary copy broke 7 and 3 checks respectively. One observation from that
  exercise changed the test — "exactly one fenced block" did **not** fire for an append mutation at
  stage 1, because on a first install append and replace are the same operation. That is why the
  install runs three times.
- **Stage 9 was proven to catch its own regression:** restoring the byte comparison in
  `uninstall_settings` makes it fail 1 of 43.
- **The `MISSING` branch was proven by mutation:** a `SETUP.md` naming
  `.claude/skills/nonexistent/SKILL.tmpl` — an extension the pass-2 pattern did not match — makes
  the fresh-clone check FAIL 1 of 14; declaring that path as a destination and changing nothing else
  returns it to PASS 13/13.
- **Pass-2's findings were reproduced against a clone of `1307aa4`,** not read off the source:
  the refusal (`exit=3`), the reformat (a four-space file returned two-space), and the accepted
  non-date (`valid`).
- **The blast radius is measured, not assumed.** Stage 6 fingerprints the fake profile before and
  after install, refresh and uninstall, and asserts every manifest-recorded path lies inside the
  temporary tree. The live profile was verified unchanged after the loop: 245 entries under
  `~/.claude/skills`, no `~/.aaw`, no `~/.claude/integrations.json`.
- **A fresh-clone run of the whole suite** proved `project_ops.py` checks out CRLF on this machine
  (`i/lf w/crlf`) and everything still passes — turning an assumption about Python and CRLF into
  evidence.

---

## 6. State at the end of the loop

| | |
|---|---|
| Branch | `feat/aaw-packaging-repair` at `360ab3c`, clean |
| Commits since base | 11 (`0e145c7` … `360ab3c`) |
| Pushed | **no** — local only, and no push has been authorised for it |
| Suite | `packaging: PASS - 4/4 checks` (13/13, 24/24, 21/21, 43/43) |
| Reviewer | codex `pkgreview`, `gpt-5.6-terra`, workspace `wA`, pane `wA:p1` |
| Verdict | **PASS** on pass 4, with the two caveats in §4 recorded |

**Still open, and outside this loop:** `jq` is not installed and Windows Developer Mode is off, so
the gstack suite cannot be run to completion here; both need the user. Nothing in this loop depends
on either.
