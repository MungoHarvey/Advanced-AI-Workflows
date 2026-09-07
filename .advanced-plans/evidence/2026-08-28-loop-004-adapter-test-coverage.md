# Adapter lifecycle test coverage — unplanned todo, loop-004

- **Date:** 2026-08-28
- **Repository:** `advanced-planning` (LOCAL ONLY — no push has ever been approved)
- **Branch:** `loop-004-codex`
- **Commits:** `a564e11` (suite, opencode/Qwen worker `codextest`), `31b7667` (controller fix)
- **Status:** complete
- **Planned?** No. Unplanned, taken on the user's decision "Coverage first, then 004-3"
  (2026-08-28). It does **not** consume one of phase 6's 30 todos and `todos_total`
  is unchanged, following the precedent of the earlier unplanned loop.

## Why this exists

loop-004-2 closed with a carried finding larger than the bug it was about:

> the Codex adapter has NO behavioural test coverage — `test_uninstall.py` binds only
> to `setup/claude-code/` and no test anywhere asserts a residual tree after a
> complete uninstall, so nothing in CI could have failed on any defect in this todo.

Stage D took four rounds on `skill-ownership.json`. Every one of those defects was
found by a controller-side shell harness that lives in a session scratchpad and will
not survive this machine. This todo converts that harness into tracked tests, and
— the durable part — parametrises them over adapters so the OpenCode adapter
inherits the coverage instead of repeating the four rounds.

## What was built

`platforms/python/tests/test_adapter_lifecycle.py`, 771 lines, 21 properties in six
groups, each parametrised over `sh` and `ps1` where both languages implement it:
37 test cases.

- **A (1–4)** install merges: existing entry preserved, foreign entry untouched,
  owned skill reads `["codex"]`, reinstall does not duplicate.
- **B (5–11)** uninstall phase 1: shared skill survives, owned skill removed,
  registry *rewritten* not deleted, state sentinel intact, `bin/ap.py` gone,
  `AGENTS.md` fences gone with the user line intact.
- **C (12–13)** phase 2a: a second run removes nothing, registry unchanged.
- **D (14–16)** phase 2b: last owner removed, empty registry deleted, state intact.
- **E (17–18)** differential: the two languages agree on counts and registry.
- **F (19–21)** complete uninstall: residual trees identical, **no `.agents` left
  behind**, state sentinel survives both.

Group F is the group that did not exist before. Twenty-six controller checks had
passed over the round-4 defect because no fixture had ever emptied the tree.

Adapters are a module-level list of tuples; adding OpenCode is one tuple, which is
the point of the exercise.

## The suite passes — which is the weak half

`37 passed in 113.85s` on the controller, which has both `sh` and `pwsh`. The
worker's PATH has neither, so its own claim of a passing run was not accepted as
evidence and was not asked for.

## Mutation sweep — the real test

Seven mutations were **registered before the tests were read**
(`004-tests-mutation-plan.md`), each reintroducing a defect that actually occurred
during stages C and D, each naming in advance which property numbers must fail.
Applied in a disposable detached worktree at `a564e11`, never in the worker's
checkout. Every mutation printed its substitution count — three probes earlier in
this phase silently matched nothing and passed vacuously.

| # | Reintroduces | Predicted | Actually failed | Verdict |
|---|---|---|---|---|
| M1 | shared skill never recorded as codex-owned | 1, 4 (8 by knock-on) | 1, 4 | met exactly; the knock-on did not occur |
| M2 | D1, the original registry clobber | 1, 2 | 1 | **partial — see below** |
| M3 | round-2: decision computed, announced, discarded | 5, 8, 12, 13 | 5, 7, 8, 12, 13, 18 | met, superset |
| M4 | inverse of D4: registry never deleted when empty | 15 | 15, 19 | met, superset |
| M5 | **D4** — converts "shared" into "sole" | 7, 8, 12, 13 | 7, 8, 12, 13, 18 | met, superset |
| M6 | **round-4** — wrong prune path, empty `.agents` left | 19, 20 | 19, 20 | **met exactly, and only those** |
| M7 | D3 in PowerShell: sharedness never computed | 5, 8, 17, 18 | 5, 7, 8, 12, 13, 18 | **partial — see below** |

**No mutation left the suite green.** Nor did any turn it uniformly red: the
smallest kill was one property, the largest six, and each named a set related to
what it broke. That was a stated acceptance criterion — an all-red result would
have suggested one over-broad fixture assertion rather than named properties.

**M6 is the result that mattered**, and it is the cleanest in the table. It
reintroduces the defect that survived 26 passing controller checks and it fails
exactly F.19 and F.20 and nothing else. Group F was built, not merely written.

**M5, the worst-consequence defect** — the one that makes a Codex uninstall delete
OpenCode's skill on the following run — fails four named properties plus the
differential.

### M2: the prediction was wrong, not the suite

M2 replaces the merge with an unconditional write of `["codex"]`. That line runs
only inside the loop over *approved* skills, and the fixture's foreign entry
`opencode-only-skill` is not approved, so M2 never visits it. Property 2 asserts
precisely that non-approved entries survive — a property this mutation cannot
reach. M2 still turned the suite red on property 1, so it is not a silent pass, but
**property 2 remains unmutated: nothing in this sweep shows it is load-bearing.**
Recorded as a gap rather than tidied away.

### M7: the prediction was right, and it found a test that could not fail

M7 makes `uninstall.ps1` treat every skill as sole-owned, so `ps1` removes strictly
more paths than `sh`. E.17 — "the two uninstallers print the same removed/kept
counts" — is the property for exactly that, and it did not fire.

`extract_count` finds the token `removed,` at index `i` and returns `parts[i-1]`.
On a real output line the tokens are `Done.` / `11` / `path(s)` / `removed,` / `0`
/ `kept.`, so `removed,` sits at index 3 and `parts[2]` is the literal string
`path(s)`, not the number, which is at `parts[1]`.

It returned `path(s)` for every run, so the assertion compared that string with
itself and was always true. A second vacuous path existed: on no match it returned
`None` for both sides, which also passes.

Fixed at `31b7667` (index `i-2`, guard `i > 1`) and **proven load-bearing rather
than merely changed**:

- M7 applied, broken parse — `1 passed`
- M7 applied, parse fixed — `1 failed`, diff `- 11 / + 10`, naming the real counts
- M7 reverted, parse fixed — `1 passed`
- full suite with the fix — `37 passed in 102.08s`

This matters beyond one test. The `2 kept` / `3 kept` discrepancy was the *only*
visible symptom of the round-4 defect, and was nearly written off as cosmetic. The
test written to catch that class of regression could not catch it.

It is the **seventh** check in this phase found reporting green over ground it does
not examine, and the second inside a test file. The recurring shape now has a
sharper edge than "check your checks": this instance and its predecessors assert on
a **derived or parsed** value rather than a filesystem fact. The other twenty
properties in this suite read the disk or compare parsed JSON against a literal,
and none of them collapsed. The vacuity risk lives where a test parses text.

## What this sweep does not show

Ten of the twenty-one properties were never killed: 2, 3, 6, 9, 10, 11, 14, 16, 21,
and 17 before its repair. For all but 2 and 17 that is because no mutation was aimed
at them — the seven were chosen to reproduce defects that actually happened, not to
cover the suite. Absence of a kill is therefore not evidence those properties are
vacuous; it is an absence of evidence either way, and it is written down as such.

## Carried

- **The install-side and state-preservation properties have no mutation coverage.**
  A second sweep aimed at properties 2, 3, 6, 9, 10, 11, 14, 16 and 21 would close it.
- `test_self_heal_integration.py:567` still asserts sandbox safety against the
  hard-coded absolute path `C:/Users/mharvey2/Documents/Coding/advanced-planning`,
  which is not where this repository lives. Pre-existing; fails on its own literal.
- The suite is not yet wired into CI as an adapter-parametrised gate; it runs with
  the rest of `platforms/python/tests/`.

## Verification performed by the controller

- Ran the suite: 37 passed, both interpreters present.
- Ran all seven mutations with printed substitution counts; adjudicated each against
  the pre-registered prediction table above.
- Chased the one predicted-but-unfired property to its cause rather than accepting
  the result.
- Both probe worktrees removed with `git worktree remove`, no `--force`; the
  worker's checkout was never modified by a probe and is clean at `31b7667`.
