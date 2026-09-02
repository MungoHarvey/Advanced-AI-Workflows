# loop-008-1 — independent audit of the criterion-4 gap

**Date:** 2026-09-02
**Provider:** codex, `gpt-5.6-sol`, `model_reasoning_effort=high`
**Shape:** `codex exec -s read-only`, prompt on stdin, non-interactive. One-shot read-only
work does not need an interactive agent, and this way there is no pane to retire and no
directory-trust gate to clear.
**Subject:** `advanced-planning`, worktree `loop-007-acc08`, branch `loop-007-integration`,
commit `9fd6796`.
**Envelope:** four checks, reproduced in the loop-008 todo. It was told the controller's
measurement explicitly and told to reproduce or refute it, not to reconcile a disagreement
quietly.

## What the controller verified before believing any of it

**The read-only claim was checked, not accepted.** The report's closing line says *"No files
or git state were changed."* Independently: `git status --short` in the worktree returned
empty and `HEAD` was still `9fd6796` after the run. That is the check, not the sentence.

**Check 1 was re-run by the controller in parallel**, dispatching both modules through
`runpy.run_module(..., run_name="__main__")` the way `ap_launcher.py:428` does, so the
comparison is against a transcript rather than a recollection:

| dispatch | controller | 008-1 |
|---|---|---|
| `platforms.python.state_validate` | `SystemExit(2)`, prints usage listing six schemas | exit `2`, prints usage |
| `platforms.python.evidence_gate` | returned normally, no `SystemExit` | exit `0`, printed nothing |

Agreement, from two independent runs by two models. The gate is callable on the three
non-Claude hosts and silently green there.

**Both disagreements were opened and checked at the cited lines.** Both are right, and both
were wrong in the controller's favour, which is the direction worth catching:

- `validate_advancement` is called at `evidence_gate.py:150`, inside `can_advance_loop`
  (defined at 113). The controller's "ZERO anywhere" was zero *outside the module*, stated
  as zero everywhere. The consequence is not cosmetic: the dead export is
  **`can_advance_loop`**, and there are **two** unreachable functions in `__all__`, not one.
  `evidence_gate.py:148` is the detail that settles it — the wrapper's own docstring tells
  callers to use `validate_advancement` instead.
- The router validates at **ten** points, not four: `loop next` at SKILL.md 120, 138, 146;
  `gate current` at 166, 190, 196; `resume` at 216, 217, 223, 230. The controller had the
  loop verb right, undercounted the gate verb three-to-one, and missed `resume` entirely.

**Its citation convention was checked before being trusted.** Every cited line is about
three lower than the command it describes — 117 against 120, 163 against 166, 187 against
190, 193 against 196. Each was opened. They land on the step *heading*, with the command in
the fence below. A consistent convention, not invented line numbers; worth confirming,
because a review earlier in this programme produced fabricated line numbers that survived
because two models agreed on the conclusion they supported.

## The finding nobody else had

The gate reviewers said the gate is not wired into three adapters. The controller narrowed
that to one site, loop step 7. Both were short.

`SKILL.md:193-196` validates collected evidence **schema-only**, in the external-dispatch
block — the Herdr/AAW fallback path. That is the path this programme runs its own workers
through. So criterion 4 fails at two sites, and the one nobody had named is the one
actually exercised here.

Its ordering point also stands, though not in the form it proposed. It suggested gating
before `loop-complete.json` is written; in this router the **worker** writes that file, so
the controller cannot gate ahead of it. What survives is the part that matters: the gate
must run after the schema check and **before the `history_log` advancement event at
SKILL.md:152**. A gate that runs after the loop has been logged complete is decorative.
And its second warning is squarely right — a CLI added while `ap_launcher` still runs any
importable module with `run_name="__main__"` closes this instance and leaves the mechanism
open for the next one.

## What changed in loop-008 as a result

Thirteen edits, all inside the loop-008 block and its handoff summary:

- 008-1 marked `completed`, carrying a `result:` field recording the above.
- The handoff's (d) and (e) corrected — the router's ten validation points, and the real
  caller counts.
- 008-2 gains a check requiring `ap_launcher`'s dispatch path to be closed in the same
  change, and to prove it by dispatching a CLI-less module and seeing non-zero.
- 008-3 gains the second site and an explicit ordering requirement.
- 008-5 now covers both functions and names `can_advance_loop` as the weaker case.
- Two success criteria widened to match.

The loop was re-parsed after the amendment: five pending todos, correct phase and task name.

## The report, verbatim

---

The controller’s main diagnosis is right: the shared-host loop path performs schema validation but never invokes the joined evidence gate. Two literal counts need correction, however:

- `validate_advancement` has one direct non-test caller, not zero, although that caller is itself unwired.
- The `gate current` section contains three `state_validate` invocation points, not one, when its conditional external-dispatch path is included.

## Claim table

| Basis | Claim | Result and evidence |
|---|---|---|
| measured | Repository under audit | Branch `loop-007-integration`, commit `9fd6796`. |
| measured | `state_validate` launcher dispatch | Printed its usage and schema list; launcher exit code `2`. This reproduces the controller’s result. |
| measured | `evidence_gate` launcher dispatch | Printed nothing; launcher exit code `0`. This reproduces the silently-green behavior. |
| read | `evidence_gate` CLI | The complete 451-line module contains no `main`, `sys.argv`, `sys.exit`, or `__main__` guard. Its last function simply returns at [evidence_gate.py:445](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:445). |
| read | Why the dispatch is green | The launcher returns `0` when `runpy.run_module` returns normally at [ap_launcher.py:428](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/ap_launcher.py:428) and [ap_launcher.py:444](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/ap_launcher.py:444). |
| read | Launcher allow-list | There is none. It rejects a leading `-`, prefixes bare names with `platforms.python.`, then dispatches the resulting module at [ap_launcher.py:417](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/ap_launcher.py:417), [ap_launcher.py:421](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/ap_launcher.py:421), and [ap_launcher.py:430](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/ap_launcher.py:430). Thus any importable module under that namespace can be attempted. |
| read | Direct production callers of `validate_advancement` | **1**, at [evidence_gate.py:150](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:150), inside `can_advance_loop`. |
| read | Adapter-wired callers of `validate_advancement` | **0**. `can_advance_loop` has no non-test production caller; its other appearances are its definition, export, and docstring examples. |
| read | Production callers of `validate_loop_complete_advancement` | **1**, imported at [next-loop.md:366](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/claude-code/commands/next-loop.md:366) and called at [next-loop.md:400](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/claude-code/commands/next-loop.md:400). |
| read | Shared router gate calls | No `evidence_gate`, `validate_advancement`, `validate_loop_complete_advancement`, or `can_advance_loop` reference appears in `SKILL.md` or any `references/*.md`. |

### Explicit document-validation invocations in the shared router

| Basis | Router point | Validation invoked |
|---|---|---|
| read | `loop next`, step 3 | Validates an existing `loop-ready.json` with `state_validate` at [SKILL.md:117](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:117). |
| read | `loop next`, step 5 | Validates the orchestrator’s new `loop-ready.json` at [SKILL.md:135](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:135). |
| read | `loop next`, step 7 | Validates `loop-complete.json` at [SKILL.md:143](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:143). |
| read | `gate current`, step 3 | Validates each `gate-verdict` at [SKILL.md:163](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:163). |
| read | `gate current`, external dispatch before worker | Conditionally validates the external-task envelope at [SKILL.md:187](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:187). |
| read | `gate current`, external dispatch after worker | Conditionally validates collected evidence before state advances at [SKILL.md:193](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:193). This is schema-only validation. |
| read | `resume`, matching ready/completion branch | Validates both `loop-ready` and `loop-complete` at [SKILL.md:213](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:213). |
| read | `resume`, incomplete-loop branch | Validates `loop-ready` at [SKILL.md:220](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:220). |
| read | `resume`, invalid-JSON branch | Invokes `state_validate` for a specific error at [SKILL.md:227](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:227). |
| read | Orchestrator reference, step 4 | Validates the external-task envelope before handoff at [orchestrator-prompt.md:119](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/orchestrator-prompt.md:119). |
| read | Worker reference, startup step 1 | Revalidates the external-task envelope before doing work at [worker-prompt.md:31](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/worker-prompt.md:31). |
| read | Worker reference, completion step 3 | Validates collected evidence before returning at [worker-prompt.md:243](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/worker-prompt.md:243). Again, schema-only. |
| read | Gate-reviewer reference, step 6 | Validates the verdict document at [gate-reviewer-prompt.md:82](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/gate-reviewer-prompt.md:82). |

Other checks described as validation or verification are:

- Process step 2 checks or creates the state directory at [SKILL.md:39](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:39).
- `gate current` steps 2–4 run independent phase review and require all verdicts to pass at [SKILL.md:161](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:161). This is a phase gate, not the loop-advancement evidence gate.
- `resume` step 1 calls `get_status`; despite the “validate existing state” wording, this is a status read, not schema validation, at [SKILL.md:201](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:201).
- Worker per-todo step 5 verifies the requested observable outcome at [worker-prompt.md:97](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/worker-prompt.md:97).
- Worker completion step 1 verifies loop success criteria at [worker-prompt.md:181](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/worker-prompt.md:181).
- Gate-reviewer steps 3–4 evaluate criteria and determine the verdict at [gate-reviewer-prompt.md:47](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/gate-reviewer-prompt.md:47).
- The manual-review reference blocks phase planning until explicit human approval at [manual-review.md:28](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/references/manual-review.md:28).
- `compact current` step 1 says “generate and validate,” but supplies no explicit validator or pass/fail command at [SKILL.md:235](/C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:235).

## Disagreements with the controller

1. **Caller count disagreement.** The controller’s “ZERO anywhere” count for `validate_advancement` is literally wrong. There is one direct production-code call at `evidence_gate.py:150`. However, it sits inside `can_advance_loop`, which itself has no production caller, so the adapter-wiring count remains zero.

2. **Gate-section count disagreement.** The shared router contains three `state_validate` invocation points under `gate current`, not one: verdict validation plus the conditional external-envelope and collected-evidence validations. None invokes the joined evidence gate, so this does not change the criterion-4 failure.

There is no disagreement on the dispatch measurement, missing CLI, missing launcher allow-list, the three `loop next` schema checks, or the single Claude `validate_loop_complete_advancement` call.

## Criterion-4 gap

On shared-skill hosts, the router schema-validates state and evidence, but no reachable loop-advancement path calls the joined evidence gate; meanwhile, dispatching the CLI-less `evidence_gate` module returns a false-success exit `0`.

## Correct wiring point

Loop step 7 is the right control point, but the gate must run **before** the controller turns collected evidence into `loop-complete.json` or logs/advances the loop.

The correct order is:

1. Receive the worker’s collected evidence.
2. Invoke `validate_advancement(evidence_path, envelope_path, verdict_paths)` through the library-bootstrap form.
3. Stop if `result.ok` is false.
4. Only then write `loop-complete.json`.
5. Schema-validate `loop-complete.json`, then log and advance.

Simply adding `python ... ap.py evidence_gate` beside the existing step-7 schema check would preserve the current silent-green defect. If a CLI is added, the launcher also needs an explicit module allow-list.

## Commands run

I used `-B` to prevent bytecode writes and set `ADVANCED_PLANNING_ROOT` process-locally so the launcher used this worktree without consulting `.advanced-plans` manifests.

```powershell
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD

$n=0; Get-Content 'platforms/python/ap_launcher.py' | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ }

$env:ADVANCED_PLANNING_ROOT=(Get-Location).Path; python -B platforms/python/ap_launcher.py platforms.python.state_validate; exit $LASTEXITCODE

$env:ADVANCED_PLANNING_ROOT=(Get-Location).Path; python -B platforms/python/ap_launcher.py platforms.python.evidence_gate; exit $LASTEXITCODE

$files = @('platforms/python/state_validate.py','platforms/python/evidence_gate.py'); foreach ($file in $files) { Write-Output ('FILE ' + $file); $n=0; Get-Content $file | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ } }

rg -n "__main__|def main|argparse|sys\.argv|sys\.exit" platforms/python/evidence_gate.py

rg -n "module = argv\[0\]|module\.startswith|runpy\.run_module|unknown option" platforms/python/ap_launcher.py

rg -n --hidden --glob '!.git/**' --glob '!.advanced-plans/**' --glob '!**/.advanced-plans/**' "validate_loop_complete_advancement|validate_advancement" .

rg -n --hidden --glob '!.git/**' --glob '!.advanced-plans/**' --glob '!**/.advanced-plans/**' "can_advance_loop" .

rg --files 'platforms/shared/agent-skills/advanced-planning/references'

$n=0; Get-Content 'platforms/shared/agent-skills/advanced-planning/SKILL.md' | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ }

$n=0; Get-Content 'platforms/shared/agent-skills/advanced-planning/references/orchestrator-prompt.md' | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ }

$n=0; Get-Content 'platforms/shared/agent-skills/advanced-planning/references/worker-prompt.md' | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ }

$n=0; Get-Content 'platforms/shared/agent-skills/advanced-planning/references/gate-reviewer-prompt.md' | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ }

$n=0; Get-Content 'platforms/shared/agent-skills/advanced-planning/references/manual-review.md' | ForEach-Object { $n++; '{0,4}: {1}' -f $n, $_ }

rg -n "evidence_gate|validate_advancement|validate_loop_complete_advancement|can_advance_loop" platforms/shared/agent-skills/advanced-planning/SKILL.md platforms/shared/agent-skills/advanced-planning/references
```

No files or git state were changed.
