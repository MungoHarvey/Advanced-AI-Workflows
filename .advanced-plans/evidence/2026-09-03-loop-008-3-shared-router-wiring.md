# loop-008-3 - wiring the evidence gate into the shared router

Date: 2026-09-03
Repository: advanced-planning, branch `loop-008-gate` (unpushed)
Worker: opencode/Qwen `gate-wire`, herdr pane `w2:p2E`, opencode 1.18.26
Discharges: criterion 4, on the three hosts that route through the shared skill

## What the todo asked

Wire `evidence_gate` into `platforms/shared/agent-skills/advanced-planning/SKILL.md`
at both sites 008-1 found, in the right order relative to the advancement event,
and then EXECUTE the shipped block in a throwaway installed project rather than
reading it.

## Pre-dispatch derivation

Before the brief was written, the controller established by reading - not by
recall - that the shared router has nowhere to get a baseline from. Zero grep
hits for `checkpoint|base_ref|base_sha|git tag|rev-parse` across the whole file,
and neither `loop-complete.schema.json` nor `loop-ready.schema.json` carries a
git field. Site 2 has no such gap: `<envelope-path>` and `<evidence-path>` are
already named in that block and are exactly the gate's two positional arguments.
The brief therefore asked the worker to answer where site 1's baseline comes
from before editing anything, and warned that a bare placeholder would be the
weaker answer.

## What the worker delivered

One commit, `107d9b0`, 18 insertions and 4 deletions, `SKILL.md` only, working
tree clean, correct worker trailers. `.advanced-plans/` in the worktree was
untouched (no `bin/` present, directory still dated Sep 2 14:35), so the
FORBIDDEN boundary held. Site 2 is genuinely good: correct positional
arguments, both verdict forms shown with a line saying which applies, exit
codes documented, and the gate placed before the advancement event at both
sites.

Site 1 shipped `--baseline HEAD~1` with prose claiming it "measures what the
loop changed". The worker's own commit message conceded "HEAD~1 used as proxy".

## Controller verification

The command was never retyped. `extract_008_3.py` reads fenced blocks out of the
SKILL.md the installer shipped into a throwaway project and prints those that
mention `evidence_gate`, with line ranges; it exits 1 with a VACUOUS message if
none do. Against the installed copy: 24 fenced blocks, 3 containing
`evidence_gate`. The wiring genuinely ships and is genuinely reachable through
the installed launcher.

`make_throwaway_008_3.py` builds the project the block needs, because the
framework repo has no `.advanced-plans/bin/ap.py` at all - that path exists only
after an install, and running the gate any other way would prove a route the
shipped markdown does not use.

### The A/B that decided it

Interventional, not observational: same tree, same forbidden write, only the
baseline moves.

```
(a) positive control, one in-scope commit        rc=0  as expected
(b) forbidden write, and it is the LAST commit   rc=1  names .claude/settings.json
(d) THE SAME forbidden write, one more commit    rc=0  *** should have been 1 ***
    committed after it
    same tree, baseline = where the loop began   rc=1  names .claude/settings.json
```

`HEAD~1` measures the final commit only. Every loop in this programme makes more
than one commit - 008-2 made six - so the shipped gate would have inspected the
last one and reported a pass it never earned. The fix had reintroduced the exact
defect class criterion 4 exists to close: a check whose subject is narrower than
the message it prints.

## The controller correction, `f209e54`

- **D1** `--baseline HEAD~1` replaced by `<loop-base-ref>`, with step 6 now
  instructing the operator to capture it with `git rev-parse HEAD` before the
  worker is spawned, and an explicit line saying not to substitute `HEAD~1` and
  why. The baseline is now produced by the block's own recipe rather than
  assumed.
- **D2** the schema check was deleted rather than preceded. The gate does
  validate schema, but its CLI prints only `schema: N validation error(s)` and
  never the errors. `state_validate` restored ahead of the gate, with a line
  saying why it is not redundant.
- **D3** the prose named "the Claude Code adapter" inside the SHARED router,
  which is the router for codex, cursor and opencode and explicitly not Claude
  Code.
- **D4** the gate takes its allow-list from the process cwd via
  `default_worker_scope(".")` while git reports repository-relative paths.
  Measured: rc=0 from the project root, rc=1 from `src/` naming `src/app.py`
  as `not_allowed` - the same in-scope change. The defect is in
  `evidence_gate.py`, which this loop may not touch; the block now states the
  working directory it must be run from.

Site 2 left unchanged: its scope comes from the envelope rather than the cwd,
both verdict forms were already documented, and the ordering was right.

CRLF preserved through the edit: 316 to 332 CRLF, 0 bare LF before and after.

## Re-proof on the corrected block

`run_008_3_scenarios_v2.py` re-extracts both commands from a freshly installed
copy of the corrected commit, checks the instrument before the subject (it
refuses to run if the shipped gate still hardcodes `HEAD~1`, or carries no
operator baseline), and makes the only substitution the shipped prose itself
instructs. Each scenario runs on its own branch cut from the baseline, so no
history is rewritten and the scenarios cannot contaminate one another.

```
(c) VACUOUS, loop made no commits                    rc=1  as expected
(a) positive control, single in-scope commit         rc=0  as expected
(b) forbidden path in the LAST commit                rc=1  names the path
(d) REGRESSION, forbidden path in the FIRST of two   rc=1  names the path
contrast, same tree under the old --baseline HEAD~1  rc=0  invisible to it
schema check, valid document                         rc=0
schema check, invalid document                       rc=1  names /todos_done
```

6 of 6. The contrast line is what makes the correction load-bearing rather than
cosmetic: the same tree passes the old form and fails the new one. The schema
pair is what makes D2 a live check rather than a comment - the restored command
names `/todos_done: Expected type 'integer', got 'string'`, which the gate alone
would have reduced to a count.

Scenario (c) is now reachable at all. Under the hardcoded `HEAD~1` a VACUOUS
result was essentially unproducible, which is why the worker ran that scenario
with `--baseline HEAD` - substituting a different baseline, so the shipped block
was not what executed.

The extractor's own guard fired once and was right to: two shipped blocks
contain `state_validate loop-complete`, the second belonging to `resume`.
Picking the wrong one would have tested a command the operator never runs at
this site.

## Suite

Controller-run, from the worktree: **1094 passed, 1 skipped in 553.98s**, exit 0
captured without a pipe. The worker reported `6 failed, 979 passed, 96 skipped`
from its own pane, which has no Git Bash; a worker's suite number is not
comparable to the controller's and is not accepted in place of one.

An earlier attempt at the same run reported `[exited with code 0]` while pytest
had died with `FileNotFoundError: pytest.ini`. The exit status belonged to the
`tail` at the end of the pipe. Second appearance of that trap this window; the
run above captures the status before any pipe.

## Recorded, not fixed

Four defects in `platforms/python/evidence_gate.py`, all found before the
worker's diff arrived, all outside this todo's allowed paths.

1. The `loop-complete` path-scope arm is blind to **staged and untracked**
   changes. The source comment says "staged + unstaged"; `git diff --name-only`
   with no `--cached` and no ref reads worktree-against-index only. Measured:
   the same forbidden file staged gives rc=0 and silence, committed gives rc=1
   naming it. Creation is the normal case for `loop-ready.json` and
   `history.jsonl` in a fresh project, and the VACUOUS guard tests the union, so
   committed work plus a staged forbidden write passes.
2. The `collected-evidence` arm has **no vacuity guard at all**, and the schema
   permits `changed_paths: []` (no `minItems`). Measured with a positive control
   in the same run: an envelope allowing nothing and forbidding everything
   returned rc=0 on an empty list and rc=1 naming the path on a single-entry
   one. The sibling subcommand refuses exactly this case twelve lines away, with
   a five-line justification.
3. The CLI **swallows schema error text**, printing only the count. D2's
   mitigation covers site 1; the underlying defect stands.
4. The gate silently depends on being run from the project root. D4's mitigation
   is documentation; the fix is to pass the git root rather than `"."`.

And one found during this verification, in the same file this loop edits:

5. `resume` has a third advancement path. Under "`loop-complete.json` matches
   `loop-ready.json`: Finalize without rerunning" it runs `state_validate` on
   both files and nothing else. That is a finalize step with no evidence gate,
   in the same router, and criterion 4 is about exactly that moment. The todo
   named two sites; adding a third mid-loop is scope-widening that wants a
   decision rather than a quiet edit.

## Commits

`107d9b0` (worker) and `f209e54` (controller correction), both on
`loop-008-gate`, both unpushed. No push, tag, PR or merge.
