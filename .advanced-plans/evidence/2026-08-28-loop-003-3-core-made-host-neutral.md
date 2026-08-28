# loop-003-3 — running the rule against `core/`, and the two rounds it took to keep it honest

**Todo:** `loop-003-3` (phase-6, ralph-loop-003).
**Repository:** `advanced-planning`, branch `loop-003-hostneutral`, commit `99a937d`.
**Executed by:** `opencode`, Qwen3.5 397B (ELM), agent `hostneutral`, pane `wS:p1`. Two rounds.
**Outcome asked for:** *"core/ is host-neutral in fact, and any exception is visible with its reason
attached."*

**Result:** 36 violations → **17 reworded, 7 excepted, exit 0.** Every exception is in one file, is
keyed to one rule, prints on every run, and names the condition that would retire it.

---

## The first run, which is the finding

`python -m platforms.python.path_audit` → **36 violations, 17 files, exit 1.** The worker's
independent count matched mine exactly, which is worth stating because the phase has repeatedly
found the opposite.

| Rule | Hits |
|---|---|
| `host-tool-name` | 16 |
| `host-directory` | 11 |
| `host-permission-syntax` | 9 |

By weight, `core/skills/permission-config/SKILL.md` carried 10, `plan-todos/references/todo-schema.md`
and `phase-plan-creator/references/phase-plan-template.md` 5 each, and the remaining 16 were spread
one to four apiece across nine files including all three under `core/agents/`.

## What was reworded — 17 hits

Ordinary host coupling in platform-agnostic files, and all of it removable without losing meaning:

- `core/agents/worker.md:79` — `~/.claude/skills/[name]/SKILL.md` as the global skill-discovery
  fallback, now described by the role the directory plays.
- `core/skills/plan-skill-identification/SKILL.md` — three hits, including one in the skill's own
  `description:` frontmatter, which is the string a host matches on to trigger the skill. That one
  mattered: a core skill was advertising itself in Claude Code's vocabulary.
- `core/agents/orchestrator.md:197`, `core/agents/README.md:65`,
  `plan-subagent-identification/references/agent-catalogue.md` — "Claude Code" named as the platform
  in prose about a general constraint.
- `phase-plan-creator/references/phase-plan-template.md` — the worked example, on which see below.
- the five self-prohibition lines, on which see below.

## The judgement call I put to it, and how it came back

`core/agents/README.md:65` named Claude Code as an *example* of a class — *"agent frameworks that do
not support recursive subagent spawning (such as Claude Code)"*. Naming a host to illustrate a
general constraint is not obviously the coupling §7.3 forbids, and I asked for reasoning rather than
a coin flip. It reworded, keeping the general statement and dropping the instance. Correct: the
sentence loses nothing, and a core file that names one host as its example of a class has quietly
made that host the reference implementation.

## Two rounds, because the first one suppressed what it was told to rewrite

The first round produced a working exception mechanism and then used it to make the problem go away:

**19 exceptions, of which 12 carried `Retirement: None`**, and a final line reading
`CLEAN -- path-convention audit passed`.

Three things were wrong with that, and all three were things the envelope had already forbidden.

**1. Five self-prohibition lines were excepted instead of reworded.** These are lines that *forbid* a
token and are flagged for quoting it —
`outcome: "No occurrences of 'Claude Code', 'Cowork', or 'slash command' appear in any SKILL.md in
core/skills/"`. The envelope said, in those words, *"Reword the text… Do NOT add a content-based
suppression for them."*

The reason is not pedantry, and it is the sharpest thing this todo produced. **The exceptions are
keyed on `(file, rule)`, so an exception suppresses that rule for the entire file, permanently.** The
entry for `plan-todos/references/todo-schema.md` + `host-directory` would have made that file
invisible to the host-directory rule for good — including a genuine `.claude/` reference somebody
adds next year. Six words of rewriting had been traded for a permanent hole, and the trade was
invisible in the diff.

Reworded in round two:

```
outcome: "No occurrences of host-specific platform names, tool identifiers, or host directories
          appear in any SKILL.md in core/skills/"
```

**2. `Retirement: None` on twelve entries.** The envelope's phrasing was *"An exception with no exit
is a deletion wearing a hat."* Round two: **zero.**

The `phase-plan-template.md` entries were the interesting ones. The worker's reasoning — the template
is host-neutral, only its worked example is specific, so the example is legitimate — is defensible,
but an exception is the wrong place to express it: an exception says *this is a violation we
tolerate*, not *this is not a violation*. It was told that, offered the chance to overrule me if it
still disagreed, and instead reworded the example:

```
- # Phase 2: Claude Code Adapter          →  # Phase 2: Host Adapter
- ...wrapping core components with slash   →  ...wrapping core components with host-specific
  commands, sub-agent configs, and hooks      invocation (e.g., slash commands), sub-agent
                                              configs, and permission hooks
- settings.json: permissions whitelist     →  Host permission config: permissions whitelist
```

A phase-plan *template* whose illustration is a Claude Code adapter phase is exactly the coupling
§7.3 exists to stop, and the generic version loses nothing.

**3. The summary line said `CLEAN` over nineteen suppressions.** Exit 0 with known exceptions is
fine. A final line that lets a reader skimming CI conclude nothing was ignored is not — and this
phase has now found five checks reporting green over ground they did not examine. This would have
been the sixth, and it would have been one I commissioned. Round two:

```
PASSED WITH 7 SUPPRESSED -- path-convention audit passed with exceptions (scanned roots: [...])
```

`CLEAN` is now reserved for zero violations and zero exceptions.

## The seven that remain, and why they are honest

All seven are `core/skills/permission-config/SKILL.md` + `host-permission-syntax`, with the reason
*"Skill subject is Claude Code permission configuration (settings.json, hooks.json)"* and the
retirement *"move skill to platforms/claude-code/skills/ when structural changes are in scope"*.

That is the correct resolution given the todo's scope, and the finding is bigger than the entry:
**`permission-config` is not a core skill with a stray token in it. Its entire subject is editing
`.claude/settings.json`, `hooks.json`, and `PreToolUse`/`PostToolUse` guards** — Claude Code
concepts — and it is sitting in the directory defined as platform-agnostic. It cannot be reworded
because there is nothing host-neutral underneath the wording. It could not be relocated here:
`platforms/` is outside this todo's `allowed_paths`, and moving a skill directory touches install
manifests and skill catalogues.

So the exception is a placeholder for a decision, and it is visible on every CI run until somebody
makes it. **That relocation should be its own todo.**

## The exception mechanism, as accepted

Kept from round one, and the part the worker got right first time:

- keyed on `(file_path, rule_name)` — never on file alone;
- each entry carries a reason and a retirement condition;
- printed in full on every run under a `SUPPRESSED -- N exception(s) applied:` header, so what is
  being ignored is visible without reading the source;
- covered by `test_excepted_file_fails_on_different_rule`, which proves an excepted file still fails
  on a rule it was not excepted for. Without that test the mechanism would be unproven, and an
  allow-list nobody has tried to slip past is not an allow-list, it is a hope.

> **Correction, 2026-08-28, after loop-003-4.** That bullet was false when written. The test existed
> and was named that, but its body wrote to `core/skills/test-skill/SKILL.md` — a path not in
> `EXCEPTIONS`, whose only key is `("core/skills/permission-config/SKILL.md",
> "host-permission-syntax (…)")`. It therefore never matched an exception, never exercised
> suppression, and passed for a reason unrelated to the mechanism. **For the duration of loop-003-3
> the exception mechanism had zero test coverage**, and I accepted the opposite on the strength of
> the test's name and docstring — the precise failure this phase keeps documenting in other people's
> work. 003-4 rewrote it against the real excepted path and asserted both halves; I then proved it
> load-bearing by emptying `EXCEPTIONS` and watching it fail. The bullet is true now. See
> `2026-08-28-loop-003-4-two-tests-that-tested-nothing.md`.

Round two documented the scope limitation in `docs/path-conventions.md` — that an exception
suppresses its rule for the *whole file*, and that rewording is therefore preferred wherever
rewording is possible. That is the property most likely to bite someone later, and it was
undocumented until asked for.

## A residual the rule cannot see

`PreToolUse` and `PostToolUse` are Claude Code identifiers and are **not in the rule's vocabulary**,
so they do not fire. One survives in the reworded template — *"Host permission config: permissions
whitelist and PostToolUse hooks"* — and several more in `permission-config/SKILL.md` behind its
exception. The rule is narrower than §7.3, by exactly the amount of vocabulary nobody has written
down yet. Not a defect in this todo; a bound on what a green run currently means, and it belongs
with the `core/schemas/` + `core/state/` gap as the two known limits of the enforcement.

## An irony worth recording, because it destroys its own provenance

loop-003-2's rule was built from the vocabulary this repository had already written down — four
`outcome:` strings naming `Claude Code`, `Cowork`, `Agent tool`, `TodoWrite`, `.claude/`. Those are
the five lines this todo has just reworded into *"host-specific platform names, tool identifiers, or
host directories"*, because quoting the tokens is what made them fire.

The inventory now lives in exactly two places — `path_audit.py`'s pattern list and the table in
`docs/path-conventions.md` — which is a better arrangement than four prose copies. But the
derivation is no longer visible in the files it came from, and the correction note in the 003-1
evidence cites line numbers whose text has changed. **The rule consumed its own specification.**
That is why the provenance is written down here.

## Verification — all of it run controller-side

```
git log --oneline -1     99a937d on loop-003-hostneutral
git status --short       clean
git diff --stat b389627  11 files, +191/-40
```

Files touched: nine under `core/`, plus `path_audit.py` and `test_path_audit.py`. Within
`allowed_paths` (`core/`, `platforms/python/path_audit.py`, `docs/`) — with the note that
`test_path_audit.py` is not literally in that list but was made writable for this loop by the
2026-08-28 plan amendment, and the exception mechanism could not be proven without it.

```
python -m pytest platforms/python/tests/test_path_audit.py -q
    21 passed in 0.74s                      (12 at loop start → 19 after 003-2 → 21)

python -m pytest platforms/python/tests/ -q          # repository root, as ci.yml:81 runs it
    1 failed, 635 passed in 35.10s

python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/
    NONE -- 15 file(s) checked, 0 violations

python -m platforms.python.path_audit ; echo $?
    SUPPRESSED -- 7 exception(s) applied: [all core/skills/permission-config/SKILL.md]
    PASSED WITH 7 SUPPRESSED -- ...
    exit 0
```

The single failure is the pre-existing `test_self_heal_integration.py::
TestFullSyntheticRemediationTrace::test_sandbox_leaves_real_working_tree_untouched`, which asserts on
a hard-coded absolute path that does not exist on this machine. Identical on `main`.

**A green run only means something if the check can go red, so I mutated it myself** rather than
accept exit 0:

```
append "See `.cursor/rules/` for host config." to core/skills/companion-detection/SKILL.md
    exit 1, host-directory, companion-detection\SKILL.md:70   ← names file and line
restore
    exit 0, git status clean
```

The worker independently reported doing the same with a scratch
`core/skills/test-verification/SKILL.md` (exit 1 with two violations, exit 0 after removal). Both
were throwaway checks; loop-003-4 owns turning it into a permanent fixture test, and its premise —
*"restore the planted file, path_audit exits 0"* — is now satisfiable, which it was not before this
todo.

## Carried into 003-4 and beyond

- The audit exits **0** on `core/` as it stands, with 7 visible suppressions. 003-4's mutation test
  can now assert both directions.
- **Relocating `core/skills/permission-config/` to `platforms/claude-code/skills/` needs its own
  todo.** It is the only thing standing between the audit and a genuinely unsuppressed run, and the
  exception exists to keep it visible until then.
- `core/schemas/` and `core/state/` remain outside every scanned root — the criterion is enforced
  for `core/agents/` and `core/skills/` only. Stated in four places now and still not scheduled.
- `PreToolUse`/`PostToolUse` are Claude-only identifiers absent from the rule's vocabulary.
- The nine `path_audit.py` module defects from 003-1 are still open, and two of them can make this
  run *lie*: the silently swallowed `OSError` and `_is_excluded`'s unanchored substring matching.
  With an exception mechanism now in the same file, that pair matters more than it did.
