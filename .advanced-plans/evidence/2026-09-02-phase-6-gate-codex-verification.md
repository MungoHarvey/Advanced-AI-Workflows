# Verifying all three gate reviewers against the source

_Written in three passes, one per reviewer, each appended as that reviewer returned.
Part 1 is codex, part 2 `code-review-agent`, part 3 `phase-goals-agent`. The parts are
left in the order they were written rather than tidied into a single verdict, because
part 3 overturns a conclusion I reached in part 1 and the sequence is the point. Read
part 3's final table for the standing result._

## Part 1 of 3: codex

**Date:** 2026-09-02
**Gate:** phase-6, attempt 1
**Subject:** `.advanced-plans/gate-verdicts/phase-6-attempt-1-codex.json`
**Reviewer under verification:** codex `gpt-5.6-sol`, `model_reasoning_effort=xhigh`, `-s read-only`
**Verdict as returned:** `fail`, confidence 99, five criticals, five of six criteria failed

The controller's standing rule is that a citation it did not open is a claim it is
repeating. Codex returned a fail that contradicts several results this phase recorded as
passing, so every cited path and line was opened before the verdict entered aggregation.
Verifying is not overriding: the verdict file is unmodified, and the pass/fail result
still comes from `aggregate_verdicts`, not from this document.

---

## Result

| # | Codex's critical | Verdict |
|---|---|---|
| 1 | Adapters do not install the same core-skill set | **Confirmed as fact. I disputed the criterion failure here and was wrong; see part 3** |
| 2 | The fixture programme did not complete on every host | **Confirmed** — by the programme's own evidence |
| 3 | ACC-08 is not enforced by an independent collector | **Confirmed** |
| 4 | Collected evidence is not wired through the joined decision | **Confirmed** |
| 5 | The CI path audit can pass with host-specific paths in `core/` | **Confirmed** |

Four of five held on this pass, with codex's finding 1 confirmed as fact but disputed as a
criterion failure. Part 3 reverses that dispute: the criterion does fail, on measured
evidence I had not opened, so all five of codex's criticals stand. The overall `fail` is
correct, and it disagrees with this phase's own self-assessment, which is the reason a
cross-model gate exists.

---

## Finding 4 — confirmed, and my first reading of it was wrong

Codex wrote that the joined advancement gate has no production caller. My first check
grepped for both validator names at once, found `platforms/claude-code/commands/next-loop.md:341`
and `:343`, and I judged the headline imprecise. That conflated two different functions.

There are two: `validate_advancement` (collected evidence — schema AND path scope AND
policy gates) and `validate_loop_complete_advancement` (the Claude adapter's
`loop-complete.json` path). Codex distinguished them; I did not.

Searching every `.py`, `.md` and `.yml` in the repository outside `platforms/python/tests/`,
`validate_advancement` resolves to `platforms/python/evidence_gate.py` alone — its
definition, its docstrings, and the internal call from `can_advance_loop` at line 150.

**Zero call sites outside its own module and the tests.** The function that joins the
decision over collected evidence is never invoked in production.

The one production call that does exist is the other function, and it omits the gate half.
At `platforms/claude-code/commands/next-loop.md:343` the call passes only the
`loop-complete.json` path, so `verdict_paths` defaults to `None`, and
`evidence_gate.py:389-391` then takes the else branch — commented in the source as
_"No gate review requested — policy gate passes by default"_ — and sets
`gate_result` to a literal `{"result": "pass", "conflicts": [], "missing": []}`.

Criterion 4 reads: _"Collected evidence advances a loop only after both schema validation
and gate validation pass."_ Neither half of that is wired. The default-pass is documented
in the docstring, so it is a designed default rather than a bug — but a documented default
that no caller ever overrides is exactly a gate that cannot fail. Codex's claim stands as
written. Correcting my own reading here rather than leaving the imprecision on the record.

---

## Finding 3 — confirmed, and it is this phase's defect class exactly

`evidence_gate.py:240-242` is the only path into the path-scope check. It reads
`changed_paths` out of `evidence["git"]["changed_paths"]` and hands it straight to
`validate_path_scope` with the allowed and forbidden lists.

`evidence` is the collected-evidence document. `core/agents/worker.md:235` has the worker
emit that field about itself, and both other worker prompts
(`platforms/claude-code/agents/ralph-loop-worker.md:206`,
`platforms/cowork/agents/worker-prompt.md:188`) say the same.

The sharpest part is the docstring. `scope_policy.py:162` describes the parameter as
_"List of file path strings from git diff --name-only."_ No caller supplies it that way.
Grepping the whole repository for that command outside tests returns only
`platforms/claude-code/commands/next-phase.md:370` and `:551`, which belong to the
remediation flow and never reach the evidence gate.

So the function documents a provenance the call site does not honour, and a worker that
edits `.advanced-plans/state/` and omits the path from its own `changed_paths` passes
collection. Criterion 3 says such a worker _"fails collection — ACC-08"_. It does not.
A check whose subject is a string supplied by the party under review is the failure this
phase was convened to eliminate.

---

## Finding 5 — confirmed, and it subsumes a finding this session already had

`path_audit.py:140-154`, `DEFAULT_SCANNED_ROOTS`, holds thirteen entries. Of `core/` it
scans `core/agents` and `core/skills` only. **`core/schemas` and `core/state` are in no
root**, so a host-specific path written into a schema or a state document is invisible to
the audit. Criterion 5 requires the audit to fail on any host-specific path in `core/`.

The same list also omits `platforms/cursor` and `setup/cursor` — the carried finding from
loop-006-5, recorded in `docs/release-checklist.md` as a known gap. Codex found the more
severe half of the same defect independently, which is worth noting: the release checklist
now warns about the adapter the audit cannot see, and says nothing about the two `core/`
subdirectories it also cannot see.

---

## Finding 2 — confirmed by the programme's own record

Criterion 2: _"A fixture programme can create one phase, one loop, and one external task
on every target host."_ Two hosts did not complete it, and both are written down:

- `.advanced-plans/evidence/2026-08-28-loop-004-4-fixture-programme.md:5` and `:440` —
  _"codex: stage 1 verified; stage 2 deliberately not run"_, blocked by a rate-limit
  dialog on pane `w2:p1B`.
- `.advanced-plans/evidence/2026-09-01-cursor-fixture-run.md:25-26` — cursor's
  `external-task-envelope.json` and `VALIDATION.txt` both **absent, step 4 blocked**.

Neither artefact exists anywhere in the implementation checkout. Codex read the record
correctly and did not overstate it. Both stoppages were operator decisions at a blocked
dialog rather than code defects — which is a reason to waive rather than to revert, but
not a reason to call the criterion met.

---

## Finding 1 — the fact is right, the conclusion is not

Confirmed as fact. `setup/codex/install.sh`, `setup/cursor/install.sh` and
`setup/opencode/install.sh` each carry the same lines 28-31: a comment reading
_"Approved core skills to install (excludes companion-detection, permission-config)"_ and
an `APPROVED_SKILLS` list of seven. `setup/claude-code/install.sh` copies or symlinks the
whole of `core/skills`, which today holds nine directories. So claude-code gets nine and
the other three get seven.

But the exclusion is documented, by name, as intentional:

> `docs/adapting-to-new-platforms.md:77` — _"Two core skills are excluded by name:
> `companion-detection` and `permission-config` do not install."_

Criterion 1 asks that every host discover the same named core **planning** skills, not
host-specific copies that drift. The seven planning skills are identical on all four
hosts; the two excluded are a companion-tool detector and a permissions configurator,
neither of which is a planning skill.

**On that basis I first called criterion 1 met. That was wrong, and the third reviewer
caught it.** See the correction below: I checked what the installers write and never
checked what the hosts resolve, which is what the criterion actually asks.

The finding is still worth keeping as a **warning**, because of the mechanism rather than
today's contents: claude-code enumerates the directory while the others enumerate a
hardcoded list. A tenth core skill lands on claude-code automatically and on nobody else,
silently, with no test asserting the two sets agree. That is drift waiting to happen, and
it is the criterion's actual concern — it simply has not happened yet.

---

## A defect in the gate command itself, found by running it

`~/.claude/commands/run-gate.md` instructs the codex reviewer to mark a criterion it
cannot check as `"not_applicable"`. The schema it must validate against,
`core/state/gate-verdict.schema.json`, defines `criteria_outcomes.status` as an enum of
exactly `["met", "deferred", "failed"]` with `additionalProperties: false`.

A reviewer that follows the command as written produces a verdict that fails
`extract_and_validate`, and step 8a then degrades the gate to its raw-text fallback —
losing the structured verdict entirely, and recording the loss as a `gate_codex_skipped`
event rather than as a defect in the instruction. The envelope for this run substituted
`deferred` and said why, which is the only reason a structured codex verdict exists to
verify.

This is the same defect class one level up: an instruction whose subject is a value the
instruction's author supplied from memory rather than read off the schema. It is not a
phase 6 finding — the command is not a phase 6 artefact — but it was found by running
phase 6's gate, and it will silently degrade every future gate until the word is changed.

---

## What was not verified

Codex's `loops_to_revert` names four loops. Nothing in the five findings supports
reverting them: findings 3, 4 and 5 are gaps in mechanisms those loops built, not
regressions they introduced, and findings 1 and 2 are a documented exclusion and two
operator-blocked dialogs. Reverting is a separate decision and the run-gate procedure
reserves it to the operator; no artefact was reverted here.

---

# Part 2 of 2: code-review-agent

**Subject:** `.advanced-plans/gate-verdicts/phase-6-attempt-1-code-review-agent.json`
**Verdict as returned:** `fail`, confidence 90, 2 critical, 2 warning, 1 info.
Criteria: 3 met, 1 failed, 2 deferred. `loops_to_revert: ["ralph-loop-006"]`.

The agent has no Write tool in its declared set, so the gate command's contingency was
expected to apply. It wrote the file anyway, through Bash. I confirmed the file on disk
rather than trusting the agent's closing summary: 13919 bytes, parses, and carries the
right `agent`, `backend`, `phase` and `attempt` values.

## Where the two reviewers agree

Both returned `fail`. On the central defect they agree, and they reached it separately.

The subagent's second critical says the ACC-08 path-scope machinery has no live caller,
and records the search that proves it: looking for `validate_advancement` or
`can_advance_loop` anywhere outside `evidence_gate.py` and its tests "returns only
CHANGELOG.md". That is the same result my own grep produced in Part 1, run before either
subagent verdict existed. Three independent checks, one answer. The mechanism is built,
unit-tested, and wired to nothing.

## Where they disagree, and who is right

Two criteria split them. On both, I read the source and side with codex.

**Criterion 4, the joined decision.** The subagent marked it met, and its own evidence
line shows why: it argues the two gates inside `validate_loop_complete_advancement` are
"each proven independently in test_evidence_gate.py", then adds that the mechanism "is
sound on its own terms". That is a judgement about whether the mechanism exists. The
criterion asks whether collected evidence advances a loop only after both gates pass, and
no caller passes `verdict_paths`, so the policy gate returns a hardcoded pass every time.
Asking "does this exist" rather than "is this wired to anything" is the exact reading the
gate envelope warned against, and it is how a check that cannot fail survives review.

**Criterion 5, the path audit.** The subagent marked it met on the ground that "no new
host token was introduced under `core/` by any of the 20 reviewed commits". True, and
beside the point. The criterion states a property of the audit, that it fails on any
host-specific path in `core/`, not a property of this diff. An audit blind to
`core/schemas` and `core/state` does not acquire that property by being handed a clean
branch. The subagent scoped the question to the diff; codex scoped it to the system, and
the criterion is written about the system.

Worth saying plainly: neither reviewer is careless. They asked different questions and
answered their own correctly. That is the argument for running both, and it is why the
aggregation treats any fail as decisive rather than taking a vote.

## Three findings codex did not raise, all confirmed

**The negative-assertion tests cannot fail.** The best finding of the gate, and I checked
it line by line. `scope_policy.py:148-151` declares
`validate_path_scope(changed_paths, allowed_paths, forbidden_paths)`, three lists of
strings. It opens no file and writes none. The tests in
`TestNegativeAssertion_StateUnchangedOnFailure` create a state file under `tmp_path`, pass
an unrelated path *string* to the function, then byte-compare the file and assert it is
unchanged. It is unchanged because nothing in the call path can reach it. The assertion is
incapable of failing.

The comment above it insists the property matters: "the error message alone is not enough,
the state file must not have been modified". The code under test has no capability to
modify anything. Loop-006-2 wrote these tests to guard against checks that cannot fail,
and produced three of them.

**The Claude adapter contradicts itself.** `ralph-loop-worker.md:18` and Hard Contract
clause (d) both say the worker does not write `loop-complete.json`, and that the controller
writes it from the collected-evidence document. `next-loop.md:322` still instructs the
worker to "Write `.advanced-plans/state/loop-complete.json`", and Step 7 then reads that
file back.

The diff explains how it happened. Across this branch `ralph-loop-worker.md` gained 68
lines and lost 20, a real rewrite, while `next-loop.md` gained 25 and lost none, the
Step 7a insertion alone. Loop-006-1 moved the boundary in the agent file and added a
validator call to the command file, but never reconciled the command file's own account of
who writes what. The one adapter with a working orchestration flow now holds both stories.

This also sharpens Part 1's finding 4. The command reads back a file that, under the new
contract, nobody is supposed to write.

**Cursor is outside the path audit.** Confirms the carried finding from loop-006-5, already
recorded in `docs/release-checklist.md`. Reached independently here.

The info finding, that `ralph-orchestrator.md` carries pasted boundary text at odds with
its own frontmatter, is consistent with the second critical and I accept it without
separate verification.

## Standing after two reviewers

| Criterion | codex | code-review-agent | My reading |
|---|---|---|---|
| 1 same core planning skills | failed | deferred | **failed** (corrected in part 3; I had this as met) |
| 2 fixture programme every host | failed | deferred | **failed**, on our own evidence |
| 3 ACC-08 blocks a state edit | failed | failed | **failed**, unanimous |
| 4 joined decision | failed | met | **failed**, codex right |
| 5 path audit covers `core/` | failed | met | **failed**, codex right |
| 6 no adapter forks a core skill | met | met | **met**, unanimous |

Four criteria fail on this pass, five once part 3 corrects criterion 1. Neither reviewer
saw the full set alone: codex missed the vacuous tests and the adapter contradiction, the
subagent missed two live criterion failures.

---

# Part 3 of 3: phase-goals-agent, and a correction to my own reading

**Subject:** `.advanced-plans/gate-verdicts/phase-6-attempt-1-phase-goals-agent.json`
**Verdict as returned:** `fail`, confidence 85. Criteria: 3 met, 3 failed.
6 findings (3 critical, 2 warning, 1 info). `loops_to_revert` empty.

## It found a criterion failure I had argued away

I called criterion 1 met in Part 1. It is failed, and the proof was already in this
programme's evidence directory, in a file whose title states the conclusion:
`.advanced-plans/evidence/2026-09-01-four-host-skill-discovery.md`, "Four hosts, one
project: the phase's headline criterion fails, and now with a mechanism".

My error was reading the wrong artefact. I opened the four installers, compared their
skill lists, found the seven planning skills identical, and concluded the hosts agree.
The criterion is about what each host **discovers**, and loop-005 measured exactly that on
four live hosts. What it found:

- opencode resolves `.claude/skills`, claude-code's copy, not its own (F20). In any
  project where claude-code is also installed, opencode serves claude-code's layer.
- On a real profile, claude and cursor serve global copies over the project's (F21).
- cursor never listed one of the skills at all, and the same opencode run produced an
  unstable list, so a host's skill listing is not stable evidence in the first place (F23).

Byte-identical file content, different resolved copies. F20, F21, F22 and F23 are all
recorded as open. So the phase measured its own headline criterion, wrote down that it
fails, and I contradicted that from a weaker artefact without opening the stronger one.

Codex marked criterion 1 failed and reached the right answer by a weaker route: its
argument was the documented `APPROVED_SKILLS` exclusion, which on its own does not fail
the criterion. The conclusion was right, my dispute of it was wrong, and the reason both
of us gave was not the reason that matters.

The rule that would have caught this is one already written down here: read the phase's
own evidence before ruling on the phase's own criterion. I read the code and skipped the
measurement.

## Where it lands on the two contested criteria

It marks criterion 4 met and criterion 5 met, siding with `code-review-agent` against
codex. Neither changes my reading.

On criterion 4 it records the caveat itself, as a critical finding: the collected-evidence
variant used by codex, opencode and cursor "has no confirmed production caller". That is
the failure, stated inside a verdict of met. It judged the Claude `loop-complete.json`
path sound, which it is on its own terms, and then noted separately that the other three
adapters have no wiring at all.

On criterion 5 it confirms `path_audit` is mutation-tested and wired unconditionally into
`.github/workflows/ci.yml`, which I verified: the "Path Convention Audit" job runs
`python -m platforms.python.path_audit` with no condition. That establishes the audit runs.
It does not establish that the audit covers `core/`. I checked whether any other CI job
applies the host-neutrality rule to the two unscanned directories, and none does. Job 2
reads `core/state` only to validate that the JSON parses and its keys match a schema, and
the install-drift job compares `core/schemas` for drift between layers. Neither looks for
host-specific paths. Criterion 5 stays failed.

## Its independent agreements

It reproduced, without access to the other verdicts, both the ACC-08 result ("zero
production callers ... only test files reference it") and the adapter contradiction
(`next-loop.md` Step 6 against `ralph-loop-worker.md:18`). Three reviewers and my own grep
now agree on the first; two reviewers and my own diff on the second.

It also declined to populate `loops_to_revert`, reasoning that the failures are honest
environment limits or a missing wiring step rather than invalid work. That matches my
Part 1 conclusion, reached separately.

## Final standing, all three reviewers

| Criterion | codex | code-review | phase-goals | Verified |
|---|---|---|---|---|
| 1 same core planning skills | failed | deferred | failed | **failed** — F20/F21/F23, measured |
| 2 fixture programme every host | failed | deferred | failed | **failed** |
| 3 ACC-08 blocks a state edit | failed | failed | failed | **failed** — unanimous |
| 4 joined decision | failed | met | met | **failed** — no caller for three adapters |
| 5 path audit covers `core/` | failed | met | met | **failed** — `core/schemas`, `core/state` unscanned |
| 6 no adapter forks a core skill | met | met | met | **met** — unanimous |

Five of six criteria fail. All three reviewers returned `fail` independently.

No reviewer saw everything, and neither did I. Codex alone caught criteria 4 and 5 and
missed the vacuous tests. `code-review-agent` alone caught the vacuous tests and the
adapter contradiction, and marked two live failures met. `phase-goals-agent` alone brought
the measured four-host result that overturns my own finding. I was wrong on criterion 1
and right on 4 and 5 against two reviewers each. The disagreements did the work here;
a single reviewer, or a vote, would have produced a worse answer than any of the parts.
