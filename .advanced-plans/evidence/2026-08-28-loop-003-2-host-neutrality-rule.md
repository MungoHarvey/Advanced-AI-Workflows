# loop-003-2 — the host-neutrality rule, and the round trip that made it usable

**Todo:** `loop-003-2` (phase-6, ralph-loop-003).
**Repository:** `advanced-planning`, branch `loop-003-hostneutral`, worktree
`~/.herdr/worktrees/advanced-planning/loop-003-hostneutral`, based on
`fix/shared-runtime-reachability` at `b3f1b8f`.
**Executed by:** `opencode`, Qwen3.5 397B (ELM), agent `hostneutral`, pane `wS:p1`.
**Outcome asked for:** *"The success criterion — the CI path audit fails on any host-specific path
in `core/` — has an implementation."* It does. `python -m platforms.python.path_audit` now exits 1
on the repository as it stands, naming 36 violations across 17 files under `core/`.

**Commits:** `211ca0e` (the worker, both rounds), `b389627` (controller, two stray doc lines).
Not pushed — no push has been approved for `advanced-planning`.

---

## The mechanism

`VIOLATION_PATTERNS` entries gain a third element, `core_only`. `audit()` computes
`is_core_root = root_rel.startswith("core/")` per scanned root and passes it to `check_file`, which
skips `core_only` patterns outside core. The three original rules keep firing everywhere, including
under `core/`; the three new ones fire only under it.

That is the right shape. It is a **rule scoped to core**, not a widened pattern — which was
loop-003-1's whole point, and it means nothing was added to `DEFAULT_SCANNED_ROOTS` and no adapter
surface changed behaviour.

## The defect I sent back, and how it was measured

The worker's first commit defined category 2 as:

```python
re.compile(r"\b(Agent|Task|subagent_type)\b")
```

I ran it against the real tree rather than reading it: **57 violations, 37 of them from this one
rule, and roughly 32 of those 37 were the English words "Task" and "Agent" in ordinary prose.**
Verbatim from the run:

```
| Loop | Task | Todos | Status | Done |
## Task Decomposition Patterns
### Layer 2 - Session Task Tracking (Display)
task_name: "Descriptive Task Name"
- Task is a simple one-liner (git commit, file copy, log write)
# Agent Architecture
```

None of that is host-specific. As written the rule **detected English**, and loop-003-3 — whose
instruction is *"record the FULL first-run output before any fix; that list is the finding"* — would
have enshrined the noise, handing loop-003-4 a worklist that says to rewrite the word "Task" out of
sentences. The defect had to be fixed in 003-2, where the rule lives, not absorbed downstream.

**The worker named it first.** Its reply listed as ambiguity 2: *"The regex `\b(Agent|Task|
subagent_type)\b` will match any use of the word 'Task' … A more precise pattern might be 'the
(Agent|Task) tool' or similar, but I kept it simple as the envelope asked for a 'short, defensible
list.'"* It surfaced the problem and left it in — which is the behaviour the envelope asked for
(*"name it, do not resolve it silently"*), and the reason a second round was cheap.

## A correction to loop-003-1's evidence

`2026-08-28-loop-003-1-path-audit-gap.md` records, and I repeated it in 003-2's envelope, that

> the concrete inventory of Claude-only tool names and the grammar of host permission syntax exist
> nowhere in the repository. Neither vocabulary is written down, so 003-2 is defining it, not
> implementing it.

**The first half of that is false, and running the rule is what disproved it.** The inventory is
written down — inside example `outcome:` fields in the core skills' own reference docs:

- `core/skills/ralph-loop-planner/references/todo-schema.md:154` — *"No occurrences of 'Claude Code',
  'Cowork', 'slash command', 'Agent tool', or 'TodoWrite' appear in any core/skills/ SKILL.md file"*
- `core/skills/plan-todos/references/todo-schema.md:134` — the same list plus `.claude/`
- and two shorter variants at `ralph-loop-planner/…:96` and `plan-todos/…:110`

So the project had already stated its own definition of a Claude-only name, four times, as worked
examples of how to write a verifiable todo — and nobody had turned it into a check. The second
round replaced the invented list with that one:

```python
re.compile(r"(Claude Code|Cowork|Agent tool|Task tool|TodoWrite|subagent_type)")
```

`slash command` was the one repo token not adopted; it is an English phrase describing a concept
rather than an identifier, and matching it would have reintroduced the same class of false positive.
That omission is deliberate and named here rather than left implicit.

This is worth more than the fix. **The rule found its own specification by being run.** An audit
written from a design paragraph would have kept the invented vocabulary; running it against real
files surfaced the authoritative one.

## Effect of the correction, measured

| | first commit | after correction |
|---|---|---|
| total violations | 57 | **36** |
| `host-directory` | 11 | 11 |
| `host-permission-syntax` | 9 | 9 |
| `host-tool-name` | **37** | **16** |
| exit code | 1 | 1 |

Both other rules were left untouched, so the 21 that disappeared are exactly the false positives.
Every one of the surviving 16 names a host: `Claude Code`, `Cowork`, `Agent tool`. Spot-checked all
16 by hand — no English-noun matches remain.

## What the 36 are, in outline

Not resolved here — loop-003-3 owns that, and fixing them in this todo would have destroyed its
finding. For the record of what the rule catches:

- **`host-permission-syntax`, 9** — almost entirely `core/skills/permission-config/SKILL.md`, a core
  skill whose whole subject is editing `.claude/settings.json`. That is not a stray token; it is a
  Claude-only skill sitting in the platform-agnostic directory, and it is the single largest thing
  the rule found.
- **`host-directory`, 11** — hard-coded `.claude/skills/`, `.claude/commands/`, `~/.claude/` lookup
  paths in skill-discovery instructions.
- **`host-tool-name`, 16** — `Claude Code` named as the platform in core prose and in a phase title.

**One class of hit is arguably self-inflicted and is flagged now so 003-3 is not surprised by it.**
Five of the 36 are lines that *forbid* the token, and are flagged for containing it:

```
outcome: "No occurrences of 'Claude Code', 'Cowork', or 'slash command' appear in any SKILL.md in core/skills/"
```

I deliberately did **not** allow a content-based suppression for these — a rule that skips lines it
recognises as prohibitions is a rule that can be switched off by writing the right sentence, and
this phase has already found four checks reporting green over ground they did not examine. They are
five lines and 003-3 can reword them ("the Claude host directory") without weakening anything.

## The inverted guard

The envelope required the false-positive guard be **inverted and renamed, not deleted**. It was, and
slightly better than asked:

- `test_claude_skills_ref_is_not_flagged` → `test_claude_skills_ref_is_not_flagged_in_platforms`,
  with the same content moved to `platforms/claude-code/commands/install.md` — the legitimate case
  is preserved rather than lost;
- the old location and content, `core/agents/worker.md` carrying
  `` `.claude/skills/plan-todos/SKILL.md` ``, reappear in a new `TestHostNeutralityInCore` class
  asserting the opposite;
- its sibling at the platform root still passes unchanged.

Those two tests now read, side by side, as the statement of the rule — which is what the guard was
for. `_make_scoped_tree` was also corrected: its `core/` placeholders used to mention `.claude/`,
which the new rule correctly flags.

The second round added `test_bare_task_agent_words_in_core_are_not_flagged`, which plants the exact
strings that caused the false positives — a markdown table header, `## Task Decomposition Patterns`,
`# Agent Architecture`, `task_name:` — in a `core/` fixture and requires a clean result. **The
regression that prompted the round trip is now pinned by a test**, so a future widening of the
vocabulary cannot silently reintroduce it.

## The named decision on `core/schemas/` and `core/state/`

Asked for explicitly, and the worker answered rather than acting: **do not widen the scanned roots
in this todo.** Its reason — the envelope scoped the work to a rule over already-scanned roots;
widening would surface hits in unreviewed files and is a larger change needing its own decision.

Accepted. It is the conservative call and it keeps 003-3's finding bounded. **But it means the
success criterion is met for `core/agents/` and `core/skills/` only** — "core files contain no host
directory" is still unenforced over `core/schemas/` and `core/state/`. That gap is now stated in
three places (003-1 evidence, the plan amendment, here) and remains open. It is a candidate for its
own todo, not something to leave as a footnote.

## Verification — controller-side, not the worker's word

Every number below I ran myself in the worktree.

```
git log --oneline -2      b389627, 211ca0e on loop-003-hostneutral
git status --short        clean
git diff --stat b3f1b8f   3 files, +206/-23  (path_audit.py, test_path_audit.py, path-conventions.md)
```

Exactly the three `allowed_paths` files. `core/` untouched — confirmed by the diff, and it matters,
because the rule now reports 36 violations there that the todo was forbidden to fix.

```
python -m pytest platforms/python/tests/test_path_audit.py -q
    19 passed in 0.58s                       (baseline was 12)

python -m pytest platforms/python/tests/ -q          # from the repository root, as ci.yml:81 runs it
    1 failed, 633 passed in 31.78s

python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/
    NONE -- 15 file(s) checked, 0 violations

python -m platforms.python.path_audit ; echo $?
    36 violations, exit 1
```

The one failure is `test_self_heal_integration.py::TestFullSyntheticRemediationTrace::
test_sandbox_leaves_real_working_tree_untouched`, which asserts on a hard-coded absolute path
(`C:/Users/mharvey2/Documents/Coding/advanced-planning/…`) that does not exist on this machine. It
is pre-existing, identical on `main`, and unrelated — established in an earlier window and
re-confirmed here.

## A reported number that did not match the measurement

The worker's first reply gave the full suite as **"603 passed, 28 skipped, 1 failed"**. Running the
same command produced **"1 failed, 631 passed"** — no skips. The counts are not a reformatting of
each other. Asked to say which command produced its numbers or to say it had not seen them printed,
it did not resolve the discrepancy in the second round.

Nothing turns on it — the suite passes either way, and I have my own count. It is recorded because
it is the same shape as the four findings this phase has already produced: **a report standing in
for a measurement.** The envelope's *"do not report a test count you have not seen printed"* exists
for this reason, and it did not hold. The only reliable defence remains running it controller-side,
which is what these evidence files are.

## Carried into 003-3

- The full first-run output is **36 violations, 17 files, exit 1**. That is the finding; do not
  re-derive it from a rule that has since changed.
- Five of the 36 are prohibition lines flagged for quoting the token they forbid. Reword the text;
  do not add a suppression.
- `core/skills/permission-config/SKILL.md` is the substantive hit — a Claude-only skill in the
  platform-agnostic directory. It will not be fixed by editing tokens, and is likely a named
  exception with a reason, or a relocation to `platforms/claude-code/`. Either way it is a decision,
  not a search-and-replace.
- The nine `path_audit.py` module defects from 003-1 are still open. Two of them can make this run
  *lie*: the silently swallowed `OSError` and `_is_excluded`'s substring matching.
