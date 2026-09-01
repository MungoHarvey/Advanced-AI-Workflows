# Cursor ran the programme — after two failures that were the controller's, not Cursor's

**Date:** 2026-09-01
**Todo:** `loop-005-3` (phase 6, provider: cursor / `cursor-grok-4.6-medium`)
**Fixture:** `scratchpad/loop-005-3/fixture-cursor3`, a scratch project outside both checkouts
**Adapter under test:** `setup/cursor/install.sh` from herdr worktree `loop-005-cursor` @ `e32c318`
**Verification harness:** `harness.py`, baselined before any dispatch (see `loop-005-2` evidence)

---

## The outcome, first

Cursor executed the fixture programme. It wrote a phase plan and a loop decomposition
that follow the installed skills' own templates, it answered the discovery question, and
when it hit a blocked shell command it **stopped and wrote `BLOCKED.md`** instead of
inventing a result — which is exactly what the prompt demanded and what this programme
keeps failing to get from its own checks.

| Artefact | Result |
|---|---|
| `DISCOVERY.md` | 1074 B — eight skill names, the fence text, an honest discovery answer |
| `.advanced-plans/phases/phase-1/plan.md` | 3231 B — Objective / Scope / Deliverables / Success Criteria / Risks |
| `.advanced-plans/phases/phase-1/loops.md` | 3916 B — YAML frontmatter, todos with `skill`/`agent`/`outcome`/`status`/`priority` |
| `BLOCKED.md` | 686 B — the refused command and the verbatim refusal |
| `.advanced-plans/state/external-task-envelope.json` | **absent** — step 4 blocked |
| `VALIDATION.txt` | **absent** — step 4 blocked |

So the loop's outcome field — *"Cursor is exercised or its blocker is recorded honestly;
it does not ship as an untested claim"* — is satisfied on both halves at once. It was
exercised, and the one thing it could not finish is recorded with its cause.

The install itself is sound. Harness against this fixture: **7 ok, 0 FAIL, 0 VACUOUS,
1 finding**, examining 8 skills, 19 byte-compared files, 1 launcher, 2 launcher probes,
1 fence, 8 ownership records and a 34-file tree.

---

## The two failures before it, and why they were mine

The first two attempts produced nothing, and the temptation was to write that up as
"cursor under-performs". That would have been wrong. Both were defects in **how the
controller invoked the CLI**, and the programme's own rule caught it: *exit 0 plus a
fluent summary is not completion — read the artefacts.*

### Attempt 1 — a greeting, no work

`cursor-agent -p "<3 KB multi-line prompt>" --trust --auto-review --model cursor-grok-4.6-medium`
exited **0** in 80 s and printed a readiness greeting listing the planning triggers. Zero
artefacts. Reproduced exactly on a second run, so not a one-off.

The obvious suspect was the AGENTS.md fence, which is written as a command dispatcher
("**Triggers:** …") and could plausibly convert a task prompt into a menu. **Tested and
acquitted:** with the fence deleted from `AGENTS.md` the same prompt produced the same
greeting and the same zero artefacts. The agent simply re-derived the trigger names from
`.advanced-plans/PLANNING.md`, which the installer also writes.

### Attempt 2 — the prompt was being re-parsed as CLI options

Flattening the prompt to a single line gave the diagnosis outright:

```
error: unknown option '--json'
```

`--json` occurs **inside the prompt** — the fixture goal is *"Add a `--json` flag to a
hypothetical CLI tool"* — and the whole prompt was passed as a single quoted `argv`
element. `cursor-agent` re-tokenises its own `-p` value and re-parses the pieces as
options.

That one fact explains every earlier symptom, including one that had looked like a
separate bug. Measured, each in a fresh untrusted directory, all with `--trust` passed:

| Prompt | Bytes | Lines | Exit | Trust marker written |
|---|---|---|---|---|
| `reply with the single word OK` | 29 | 1 | 0 | yes |
| 900 × `a` | 900 | 1 | 0 | yes |
| head of the fixture prompt | 120 | 1 | 0 | yes |
| same words, split over 3 lines | 29 | 3 | **1** | **no** |
| head of the fixture prompt | 300 | 6 | **1** | **no** |
| the full fixture prompt | 3091 | many | **1** | **no** |

It is **newlines, not size**: 900 bytes on one line trusts fine, 29 bytes on three lines
does not. And the failure presents as `⚠ Workspace Trust Required` — a message that names
`--trust` as the fix *while `--trust` is being passed*. An operator reading only stderr
would conclude the flag does not work, and the herdr notes already carry one wrong
conclusion about cursor reached exactly that way.

### The fix, which the record already contained

Deliver the prompt on **stdin**, not as an `argv` value:

```bash
cursor-agent -p --trust --auto-review --model cursor-grok-4.6-medium < prompt.txt
```

Verified on all three failure modes at once — multi-line prompt, a prompt containing
`--json`, and a never-trusted directory: exit 0, correct output, trust marker written, no
warm-up call needed. The run that produced the artefacts above used this form in a
directory with `trusted before: 0`.

`CLAUDE.md` already says these one-shot CLIs *"read a prompt on stdin"*. The documented
form was right; the controller deviated from it. That is the finding, and it is not
cursor's.

---

## The invocation manifest the loop asked for

Recorded so a permission the operator withheld is never mistaken for a routing failure.

| Field | Value |
|---|---|
| CLI | `cursor-agent` 2026.08.25-3e8eec8 |
| Model | `cursor-grok-4.6-medium` (explicit, not `auto`) |
| Mode | **write** — `--trust --auto-review` |
| Prompt delivery | stdin |
| `--sandbox enabled` | **unavailable**: *"Sandbox requires macOS or Linux."* Exit 1 on Windows |
| `--force` / `--yolo` | **not used, deliberately** — Run Everything auto-approves every shell command, which is broadening provider permissions and is the operator's decision, not the controller's |
| Trust | `--trust` on a never-trusted directory, marker written by the run itself |
| Duration | 110 s |

`--sandbox` was the option `loop-005-1` named as *"the right first try"* for a fixture run.
It is measured now and it is not available on this platform, so that recommendation is
closed rather than deferred.

---

## Blocker: Cursor cannot run any shell command on this machine

Step 4 needed one shell command. Every shell call Cursor makes is refused:

```
Hook blocked with message: --: eval: line 1: syntax error near unexpected token `&'
--: eval: line 1: `$OutputEncoding = [System.Text.Encoding]::UTF8; Get-Content -LiteralPath
'…\cursor-hooks-B49VL0\payload.json' -Raw | & { $input | python
"C:\Users\mharvey2\.claude\plugins\cache\chandran-lab-fair-data-prep\fair-data-prep\0.4.1/hooks/block_prune.py" }'
```

Not taken from the worker's summary — reproduced by the controller with a one-line prompt
asking only for `git rev-parse HEAD`, in a fresh hook payload directory (`A21qsi`, versus
`B49VL0` in the worker's run).

The source is `~/.claude/plugins/cache/chandran-lab-fair-data-prep/fair-data-prep/0.4.1/hooks/hooks.json`,
which declares a Claude Code `PreToolUse` hook on `Bash`:

```json
{"matcher": "Bash", "hooks": [{"type": "command",
 "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/block_prune.py\""}]}
```

Cursor executes that hook, wraps it in **PowerShell** syntax (`$OutputEncoding`,
`Get-Content`, the `& { … }` call operator) and then evaluates the wrapper with a **POSIX
shell**, which dies at the `&`. Same shell-resolution class as the WSL/Git-Bash trap
already recorded in the phase-5 evidence: the command text and the interpreter chosen to
run it come from two different assumptions about the platform.

Consequences worth stating plainly:

- The blocker is **machine configuration, not the Cursor adapter**. The adapter installed
  cleanly and its skills were used.
- It is **not specific to advanced-planning** — it blocks every Bash call from
  `cursor-agent` on this machine, in any project.
- It is **the operator's to clear**, since it involves a plugin's hook wiring. The loop's
  own check says a blocked agent is not the worker's to answer, and that holds here.
- Cursor behaved correctly at the block: it stopped, recorded the refusal verbatim, and
  honoured the *"do not work around it"* instruction.

---

## Skill discovery: the adapter ships a claim this run contradicts

The fence the installer writes states:

> **Skills:** Installed to `.agents/skills/` - Cursor discovers them automatically.

`DISCOVERY.md`, answering the question it was asked to answer honestly, says:

> Cursor listed many skills at session start but omitted the names under this project's
> `.agents/skills/`; I read those directory names from disk myself.

**This is a self-report and is marked as such** — what a CLI offers its own model is not
observable from outside the process, so it is the only channel available and it is weaker
evidence than anything else in this document. What *is* independently verified is that the
work got done: `plan.md` and `loops.md` follow the installed skills' templates, so the
skills were read one way or the other. `loop-005-4` is the todo that settles discovery
properly, across four hosts under a fake HOME, and it should treat this as a hypothesis to
test rather than a result to cite.

---

## A shipping defect found on the way: the Cursor fence names commands that do not exist

Not part of the loop's checks; found while chasing the greeting, and it is real.

`setup/cursor/install.sh` builds the fence inside a double-quoted `sh` string, so
`$advanced-planning` is expanded — `$advanced` is unset, and what lands in the operator's
`AGENTS.md` is:

```
- `-planning phase <goal>` - Create a new phase plan
```

Measured by installing each adapter into its own throwaway fixture and reading the file
that resulted, rather than by grepping the scripts:

| Adapter | `install.sh` output | `install.ps1` output |
|---|---|---|
| codex | `` `$advanced-planning phase <goal>` `` | `` ` $advanced-planning phase <goal> ` `` |
| opencode | `` `$advanced-planning phase <goal>` `` | `` ` $advanced-planning phase <goal> ` `` |
| **cursor** | ``  `-planning phase <goal>`  `` ✗ | `` ` $advanced-planning phase <goal> ` `` |

Localised: **`setup/cursor/install.sh` lines 411–415 are missing the backslash that
`setup/codex/install.sh` and `setup/opencode/install.sh` carry at the identical line
numbers.** The cursor adapter was derived from codex's and lost the escape on exactly the
five trigger lines.

Two details that stop this being a one-line story:

- **`PLANNING.md` is unaffected in all three**, because line 681 sits inside a *quoted*
  heredoc (`<<'PLANEEOF'`). So one installer writes the command name correctly to one file
  and incorrectly to another, and a reader comparing the two would reasonably conclude the
  expansion was intentional somewhere.
- **The two hosts of the same adapter disagree.** `install.ps1` escapes correctly (backtick
  inside `@"`), so an operator on PowerShell gets a working trigger name and an operator in
  Git Bash does not — from the same adapter, same version. Neither matches the other
  exactly, since the `.ps1` also renders a padded code span.

A test that installed each adapter and asserted the fence text is identical across hosts
would have caught both. There is no such test.

---

## Carried

- **Fix `setup/cursor/install.sh:411-415`** (escape `\$advanced-planning`), and add a test
  that the fence text an adapter writes is identical from its `.sh` and `.ps1` installers.
  Lives in `advanced-planning`, in the unpushed worktree `loop-005-cursor` @ `e32c318`.
- **The fair-data-prep `PreToolUse`/`Bash` hook blocks every Cursor shell command** on this
  machine. Operator decision — see the handoff.
- **The stdin rule for `cursor-agent -p`** belongs in the herdr notes alongside B11: a
  multi-line or option-shaped `argv` prompt silently defeats `--trust` and misreports as a
  workspace-trust refusal.
- Unchanged from `loop-005-2`: add `platforms/cursor` and `setup/cursor` to
  `DEFAULT_SCANNED_ROOTS`; the `ap_launcher` exit-3 overloading (reproduced again by this
  loop's harness, and still the only FINDING it emits).
- `loop-005-4` should not cite this loop's discovery answer as settled.
