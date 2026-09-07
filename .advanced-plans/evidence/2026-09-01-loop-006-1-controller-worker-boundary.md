# The boundary reaches the prompts, and five checks fail on the way

**Date:** 2026-09-01
**Todo:** `loop-006-1` (phase 6, teach the roles to emit an envelope rather than mutate programme state)
**Repository:** advanced-planning, herdr worktree `loop-005-cursor`, branch `loop-005-cursor`
**Worker:** `env061`, opencode / Qwen3.5-397B, pane `w2:p2B`
**Commits:** `8f7294d` (batch 1, worker), `94fd785` (controller), `b0c04da` (batch 2, worker),
`071d005` (batch 3, worker), `68b6902` (controller)
**Schemas under test:** `core/state/external-task-envelope.schema.json`, `core/state/collected-evidence.schema.json`

---

## The outcome, first

Eight role prompts across four hosts said the worker writes `loop-complete.json`. The
design has said since loop-002 that it does not: the worker emits a **collected-evidence**
document and the controller writes programme state from it. That gap was in the documents
the workers actually read, which is the only place it counts.

It is now closed in the shared and core role definitions, and the two documents are
distinguished everywhere by direction of travel:

| Document | Direction | Written by |
|---|---|---|
| `external-task-envelope` | the ASSIGNMENT | controller to worker |
| `collected-evidence` | the RESULT | worker to controller |

The work was split into three batches. What that split cost, and five checks that failed
while doing it, are the substance below.

---

## Findings

**F25 — a piped background command reports the pipe's exit code, not the command's.**
The full suite was run as `pytest -q 2>&1 | tail -3` in the background. The completion
notification read **"completed (exit code 0)"**. pytest had finished **2 failed, 948
passed, 1 skipped**: `tail` exited 0, and `tail` is what the shell reported. This is the
phase's central defect class occurring in the controller's own instrumentation, and it is
the worst instance so far because the subject was not an interpolated string but a
*process* substituted for the one being measured. The pipe also destroyed the evidence —
the log held five lines, so the assertion text was gone and both tests had to be re-run to
learn what they said. **Never pipe a check whose exit code is the result**: redirect to a
file, or capture the first element of PIPESTATUS. Caught only because the notification's
own summary contradicted the text directly beneath it.

**F26 — a check pinned by position cannot tell drift from insertion.**
`TestWorkerCommitContract` extracts clause (a) of each worker Hard Contract by letter and
asserts the three shipped copies state it identically. Batch 1 inserted a new clause at the
top, relettering the commit clause to (b). The test fired and was right to fire — there was
a real contradiction underneath — but its message said the contracts *"state 2 different
commit policies"* when the policies were byte-identical and merely sitting at different
letters. A correct alarm with a wrong diagnosis, and the first thing written about it here
was that a user decision had been overwritten, which was false and needed correcting. The
test's subject is a position standing in for a topic. **Not changed in the same breath as
the work it flagged**, deliberately: loosening a check to make a change pass is the move
this phase exists to prevent.

**F27 — a schema summary that reads only top-level `properties` cannot see an item-level enum.**
The todo requires an emitted envelope and its validation, so the controller built a real
one. It failed on all four items of `required_evidence` — a controlled vocabulary of six
values (`git_diff`, `tests`, `agent_summary`, `review`, `screenshots`, `logs`) into which
prose had been written. The cause was the controller's own dump of the schema, which
printed enums found on each top-level property; `required_evidence` carries none, because
its constraint lives one level down on `items`. The dump reported "array of string" — true
of the container, useless about the contents — and that description went into the batch-1
envelope. **The workers were right where the controller was wrong**: both
`orchestrator-prompt.md` and `core/agents/orchestrator.md` document the correct six values,
because they were told to read the schema rather than trust a summary. An argument for that
instruction, and against pre-digesting a spec for an agent that can read it.

**F28 — a positional pin over one clause cannot see the surrounding contract drift.**
The three worker contracts the test treats as one document carry **4, 3 and 5 Hard Contract
clauses** respectively (`core/agents/worker.md`, `ralph-loop-worker.md`,
`shared/.../worker-prompt.md`). Clause (a) is pinned byte-identical; nothing pins (b)
onward, so the shared copy acquired a "Do not plan or restructure" clause the other two
never got. On inspection it is not a policy gap — `core/agents/worker.md` states the same
rule in prose twice — so the contracts agree on substance and differ in structure. Recorded
rather than fixed, for the same reason as F26. The consequence landed immediately: the
boundary clause added by this loop is (d) in two copies and (e) in the third, purely
because of a clause only one of them has.

**F29 — the controller verified a commit in the worktree a writer was editing.**
The full suite was started against `b0c04da`, then batch 3 was dispatched to a worker in
the *same* worktree while it ran. From that moment the suite was reading files being
rewritten underneath it, so whatever it printed would have described no commit that ever
existed. Killed rather than reported. The rule it breaks — one worktree per concurrent
writer — was already written down and was being applied to workers while the controller
exempted itself. **A reader needs a stable tree exactly as much as a writer needs an
exclusive one.** The two measurements taken before the dispatch survive; the suite was
re-run afterwards on a quiet tree and covers all three batches at once.

**F30 — a substring test for negation is satisfied by any word that contains it.**
The controller's check for *"does a worker prompt still tell the worker to write
`loop-complete.json`?"* excluded a line if `"not" in line.lower()`. That check made two
opposite errors at once, and each hid the other. It **false-positived** on two rows sitting
under a `## What the Worker Does NOT Do` heading, because the negation there is structural —
it is in the heading, not in the row. And it **false-negatived** on
`ralph-loop-worker.md:3`, whose YAML `description:` still read *"and writes
`loop-complete.json` on finish"* — flatly contradicting line 18 of its own file, which batch
3 had already corrected — because the phrase *"**Can**not spawn subagents"* later in the same
string contains the letters `n-o-t`. Two spurious failures made the check look strict while
it was silently passing the one file that was actually wrong.

The defect that escaped is the more serious kind: `description:` is the field a host
surfaces when routing work to an agent, so it is read in more places than the body is. Fixed
by matching `\bnot\b` and tracking the enclosing heading, and the repaired matcher now
**self-tests before it runs** — it asserts it still fires on a positive imperative and stays
silent on the same sentence under a negative heading, so a future edit cannot quietly
neuter it. The correction landed in `68b6902`.

The rule: **a negation is a property of a proposition, not of the characters in a line.**
A check that looks for meaning by substring is testing a string it interpolated, which is
this phase's central defect class arriving for the sixth time — and the fifth of the six is
the controller's own instrument rather than a worker's output.

---

## Two rules the batching produced

**A pinned invariant defines the unit of change; the file layout does not.**
Underneath batch 1's re-lettering was a real defect: the commit clause told a git-less
runtime to list its changed paths in `loop-complete.json` — the exact file the new boundary
forbids it to write. The clause had to change, and because the three copies are pinned
byte-identical it had to change in all three at once. The three-batch split was scoped by
file, so it necessarily left the suite red until the last batch landed. Fixed by pulling
that one clause forward into all three copies in `94fd785`. Before batching by file, ask
what the tests pin across files.

**Schema validity is not currency.**
The batch-3 envelope was emitted against `94fd785` and validated. Batch 2 then committed
`b0c04da`, and the envelope kept validating — `base_sha` only has to be forty hex
characters, and the old one still is. A document correct in every field the schema can see,
and wrong about the only thing that mattered: the commit the worker would actually start
from. Re-derived from `git rev-parse HEAD` immediately before dispatch. A document that
pins a fact about the machine must be re-derived when it is used, not when it was
convenient to build.

---

## A rule about call sites, from a failure that was not one

Batch 1 added three `python ".advanced-plans/bin/ap.py"` call sites to the two shared role
prompts. Batches 2 and 3 were told to use prose instead, after measuring that installers copy
and symlink without rewriting — so the repo looked inconsistent, and the controller's check
*"no `ap.py` call site in any agent file"* failed on exactly those three lines. It read as a
real defect caused by the controller's own reversed instruction.

It is not. `setup/{codex,cursor,opencode}/install.sh` copy
`platforms/shared/agent-skills/advanced-planning` to the host's skills directory and then run
`ap_rewrite_call_sites` over `find … -name '*.md'`, which reaches `references/`. That function
substitutes the **exact literal** `python ".advanced-plans/bin/ap.py"` for the host launcher.
So in that one directory the call site is the *source form the installer expects*, and it
predates this loop by **17 occurrences** in `SKILL.md` and `gate-reviewer-prompt.md`. The six
files under `core/agents`, `platforms/claude-code/agents` and `platforms/cowork/agents` are
copied by no rewriting installer, so a call site in *those* would ship a path that cannot
resolve — `.advanced-plans/bin/ap.py` does not exist in the repository.

Both instructions were right for their own files. The check was wrong: it applied one rule to
eight files governed by two. **Whether a literal path is a defect depends on whether something
rewrites it at install time, so a check over shipped text has to know the install topology.**
Split into two halves that pin the whole contract rather than one side of it: prose-only where
nothing rewrites, and *exact* source form where something does — the second half being the
stronger of the two, because a drifted quote style there would survive install unrewritten and
fail silently on a user's machine. Nothing pins those files today; the existing call-site tests
glob the commands directory only, which is a real gap and is recorded as one.

---

## Amendment to the todo's own check 1

The todo's first check reads *"the worker-role prompt writes an envelope validating against
the loop-002-2 schema"*. **The worker does not write an envelope.** Per the table at the
top, the envelope is the assignment and travels controller-to-worker; a worker writing its
own envelope would be assigning work to itself, which is precisely the boundary this loop
exists to establish. Satisfying the check as written would have undone the todo's outcome.

What was implemented is the correct reading: the worker emits collected evidence, the
orchestrator emits the envelope, and both halves validate. The envelope half of the
evidence requirement is met by the assignment actually issued for batch 3 — emitted against
the live HEAD, validating exit 0, with a malformed `run_id` rejected exit 1 to prove the
check discriminates.

Recorded as an amendment rather than silently satisfied or silently ignored. A check
phrased in terms of a schema is still prose, and prose can be wrong about the artefact it
names.

---

## What the shipped templates are, and how they are now checked

The prompts ship their examples as **fill-in-the-blanks templates**, not literal JSON: the
boolean fields are written as an unquoted alternation and every leaf is a placeholder in
angle brackets. A first controller-side check that parsed fenced blocks as JSON therefore
skipped the one example that mattered and reported **VACUOUS** — correctly refusing to call
zero validated examples a pass, and thereby catching its own blind spot rather than
papering over it.

The replacement normalises each template by taking every placeholder value **from the
schema entry for that same key**, then validates the result. Key names, nesting and enum
membership are all genuinely tested; the substitution is schema-driven rather than
hand-mapped, because a hand-map is the F27 mistake repeated. Any pattern the generator does
not recognise raises rather than guessing.

Both shipped evidence templates pass, and the check is proven to discriminate: reinstating
the exact value batch 1 shipped, `status: "partial"`, is rejected with
*"Value 'partial' not in enum"*. `partial` was never in the collected-evidence enum — a
defect batch 2 independently found and resolved to `interrupted`, the status meaning
execution stopped at the iteration limit and needs a controller decision.
