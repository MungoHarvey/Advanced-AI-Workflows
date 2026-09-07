# loop-008-4 — the guard lands before the thing it guards

Date: 2026-09-03
Repository: advanced-planning
Branch: `loop-008-gate` (base `loop-007-integration` at `9fd6796`)
Worktree: `~/.herdr/worktrees/advanced-planning/loop-008-gate`
Provider: opencode / Qwen3.5 397B, herdr worker `gate-impl` in `w23:p1`
Discharges: criterion 4, and the defect class underneath it

## What landed

| commit | author | change |
|---|---|---|
| `ff44883` | worker | `platforms/python/tests/test_dispatchable_modules.py`, 130 lines, 2 tests |
| `ed38f33` | controller | the walk missed a shipped root, and the floor measured a different number from the one it named |

Test-only, as the todo requires. No production code changed by either commit.

## The controller's expectation, derived before dispatch

Written to the scratchpad at `e7b04ed`, before the brief was sent, so the
worker's answer could be checked against something it did not supply: **26
invocations naming 4 modules** — `state_validate` 14, `history_log` 7,
`install_audit` 4, `handoff_digest` 1. That figure was reproduced exactly by the
corrected walk. The expectation also predicted the worker would report only the
two roots the brief names, and it did.

One part of that expectation was **wrong and is corrected here**. It listed five
roots on the strength of `ap.py` *mentions* per directory —
`platforms/codex/` 3, `platforms/cursor/` 3, `platforms/opencode/` 3 — and
called a two-root answer "the finding". Reading those nine lines shows every one
is prose: *"all Python calls go through `.advanced-plans/bin/ap.py`"*, with no
module following. There is nothing there to dispatch, and excluding those roots
is correct. A mention is not an invocation, and counting the former to predict
the latter was the same substitute-the-easy-measurement error this programme
keeps finding in its own instruments.

Two more near-misses, both checked rather than assumed:
`platforms/claude-code/commands/next-phase.md` calls
`runpy.run_path(...)['bootstrap']()` — the launcher's bootstrap helper, not a
module dispatch — and `platforms/claude-code/install.sh` copies
`ap_launcher.py` into place rather than using it.

## What the worker got right

The list is genuinely derived by regex over shipped files, never enumerated. The
`__main__` detection accepts both quote styles, carrying forward the latent
defect found in 008-2. `evidence_gate` is correctly **absent** from the derived
list, with a comment saying why — 008-3 has not run, and adding it by hand to
look covered would have reintroduced the enumerated list the todo exists to
prevent.

## Three defects in it

**The walk read a filename where it needed a directory.** It opened
`platforms/shared/agent-skills/advanced-planning/SKILL.md` directly, so it never
reached `references/`, which ships three prompt files — `worker-prompt.md`,
`orchestrator-prompt.md`, `gate-reviewer-prompt.md` — carrying four
`state_validate` dispatches between them. The todo said in terms that a root the
shipped files use and the walk misses is the finding rather than a detail. Both
roots are now `rglob`'d.

That gap has its own test, because it is invisible in the totals: a walk reading
only `SKILL.md` still finds **22** invocations and clears the vacuity floor while
covering none of those three files. No assertion in the file would have noticed.

Those three files really do ship, checked rather than assumed: all three
installers (`setup/{codex,cursor,opencode}/install.sh`) copy the whole
`platforms/shared/agent-skills/advanced-planning` directory as `_src` into the
host's skills root, `references/` included.

**The floor measured a different quantity from the one its message named.**
`find_ap_invocations()` returned a deduplicated set, so the guard floored *unique
modules* (4) while its failure text read `only found N ap.py invocations`. Those
differ by a factor of six here — 26 against 4 — so three quarters of the corpus
could disappear with the count still comfortably clear. It now returns one entry
per invocation with file and line, and the floor is on that.

**The floor said three different things at once.** The docstring: `FLOOR = 10
(as of 2026-09-03, found ~15 unique modules)`. The constant's comment: `found 4
unique modules`. The constant: `VACUITY_FLOOR = 3`. The `~15` is not measured
anywhere. And 3 sits *below* the 4 the walk found, so losing an entire module was
already tolerated on the day it was written. There is now one measured figure
(26, dated) and one floor derived from it (22), interpolated into the failure
message so the two cannot drift apart.

Two smaller repairs: **named-but-absent** and **present-but-inert** were
collapsed into one assertion by `has_main_block` returning False for both —
different defects, different fixes, now different messages. And a **negative
control** was added, because nothing in the original proved `has_main_block`
could ever return False: every assertion in the file was satisfied by a detector
returning True unconditionally, so the suite would have stayed green through
exactly the defect it is written to catch. `scope_policy` and `codex_gate` are
real CLI-less modules in this runtime and now pin that without needing a
mutation to show it.

## Final measurement

    invocations: 26   floor: 22
    dirs reached: ['advanced-planning', 'commands', 'references']

| module | invocations | in runtime | has `__main__` |
|---|---|---|---|
| `state_validate` | 14 | yes | yes |
| `history_log` | 7 | yes | yes |
| `install_audit` | 4 | yes | yes |
| `handoff_digest` | 1 | yes | yes |

All four pass today, which is expected and is the point: the guard lands before
the thing it guards, so when 008-3 wires `evidence_gate` into the shared router
this test starts covering it with no further edit and nobody has to remember to
come back.

## Mutation proof — controller-run, five cases

Each asserts the expected number of pattern sites before touching anything,
restores byte-exact with a sha256 comparison, and carries
`test_detector_can_return_true` as a positive control in the same run.

| mutation | subject | test that went red | control |
|---|---|---|---|
| M1 an inert module is dispatched | `SKILL.md` | `test_every_dispatched_module_is_dispatchable` | green |
| M2 an absent module is dispatched | `SKILL.md` | same | green |
| M3 corpus drops below the floor (5 of 10 sites) | `SKILL.md` | same | green |
| M4 the walk stops recursing (`rglob`→`glob`) | the test | `test_the_walk_reaches_the_references_subdirectory` | green |
| M5 the detector always says yes | the test | `test_detector_can_return_false` | green |

Every case: mutated rc=1, restored sha matches, re-run rc=0.

The site-count guard earned itself again. `SKILL.md` holds **10**
`state_validate` dispatches, not the 11 a cross-file grep suggested, and the
harness refused to run M3 rather than silently mutating a different five — the
same guard that caught the two-site verdict-flag pattern in 008-2.

**M4 is the case worth keeping.** Under a non-recursive walk the main assertion
stays **green** at exactly 22 invocations — the floor — and only the references
test goes red. A single combined test would have passed through the defect.

`platforms/shared/` and `platforms/claude-code/` are clean in `git status` after
the proof.

## Suite

Controller-run, whole directory, at `ed38f33`:

    1080 passed, 1 skipped in 437.19s

That is 1076 + the four tests added here, with nothing else moved.

The worker reported `977 passed, 6 failed, 96 skipped` from its own pane and
correctly attributed the six to `test_fence_byte_identity.py` and the absence of
Git Bash there. It reported the line verbatim and did not interpret it, which is
what the brief asked for after 008-2.

## What did not happen

No push, no tag, no PR, no merge. The eight commits sit unpushed on
`loop-008-gate` in the worktree.
