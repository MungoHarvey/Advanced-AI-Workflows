# loop-007-7 — the fixture programme on all four hosts, pre-authorised rather than answered

Date: 2026-09-03
Fixtures: `scratchpad/l0077/fx-codex`, `fx-cursor`, `fx-claude` — three throwaway git projects outside every checkout
Adapters under test: `setup/{codex,cursor,claude-code}/install.sh` from herdr worktree `loop-008-gate` @ `a74f1a3`
Discharges: criterion 2 — *a fixture programme can create one phase, one loop, and one external task on every target host*

## The result, first

| host | phase | loop | external task | validator | mode | verdict |
|---|---|---|---|---|---|---|
| opencode | ✓ | ✓ | ✓ | exit 0 | write | complete (loop-004-4, unchanged) |
| **codex** | ✓ | ✓ 5 loops / 27 todos | ✓ | exit 0 | write, `-s workspace-write` | **complete — new** |
| **cursor** | ✓ | ✓ 3 loops | ✓ | exit 0 | write, `--trust --auto-review` | **complete — new** |
| claude | ✓ | ✓ | authored, but the path was the host's own choice | host could not run it | write, `acceptEdits`; Bash refused | **incomplete, and the adapter says so itself** |

Two of the four were incomplete going in. Both are now complete, and neither was
completed by answering a dialog. The fourth turns out to be incomplete for a reason
that was written down in the shipped adapter all along.

## Instrument before subject

Every fixture was snapshotted by sha256 before its run and diffed after. loop-004-4
recorded a controller defect exactly here — a diff joining a sha256 snapshot against an
md5 listing, reporting "0 modified over 0 rows" — so `snap.py` prints the row count on
every comparison and refuses an empty baseline as VACUOUS.

The comparison was proven able to fail before it was trusted: a planted line in the
codex fixture's `README.md` moved it from `0 modified` to `1 modified`, and back to `0`
on restore.

The envelope validator was proven able to fail too, on the real artefact: removing
`base_sha` from codex's envelope gives `Validation error at root: Missing required
property: 'base_sha'`, exit 1; restoring it gives exit 0. Every host's exit 0 below was
re-run by the controller, not taken from the host's report.

## codex — the quota decision reversed, and the run finished

loop-004-4 stopped codex after phase creation because the account stood at 98% of its
weekly window with five days to reset. Read from the most recent rollout today:
`used_percent: 9.0`, `window_minutes: 10080`. It reset, so the skipped half was simply
run.

**Stage 1** (`codex exec -s workspace-write`, prompt on stdin): exactly **one** file
added, `.advanced-plans/phases/phase-1/plan.md` (5812 B), zero modified, `state/` empty,
27 rows compared. The gate held and printed verbatim:

```
REVIEW .advanced-plans/phases/phase-1/plan.md
Reply with exactly one:
APPROVE phase-1 / REVISE phase-1: <instructions> / STOP phase-1
```

**Stage 2** (`APPROVE phase-1` delivered inline): 4 added, 1 modified over 31 rows —
`loops.md` (34 627 B, 27 todos across 5 loops), `state/external-task-envelope.json`,
`state/history.jsonl`, `PLANS-INDEX.md`, and `plan.md` updated.

The history event it appended uses the `timestamp` key, replicating loop-004-4's
observation on a second run:

```json
{"event":"phase_approved","phase":"phase-1","timestamp":"2026-09-03T10:25:04Z"}
```

**The envelope is semantically true, which is new.** loop-004-4 found opencode's envelope
validating at exit 0 while declaring a non-repository, `base_ref: main` and a `base_sha`
of forty zeros — the finding that the schema checks format and not semantics. codex's
`base_sha` is `7e90a820f7903e07eeabec3466957c9f252f67ab`, which **is** the fixture's HEAD,
and `base_ref: master` **is** its branch. The schema gap is unchanged and still real; what
changes is that it is no longer the only thing standing between the envelope and the
truth. Two hosts have now populated it correctly unprompted.

## cursor — the blocker was the shell it was launched from

loop-005-3 stopped cursor at step 4: it could not run **any** shell command, because
`cursor-agent` wraps command hooks in PowerShell unconditionally and then evaluates the
wrapper with the agent's own shell. The `2026-09-01-cursor-hook-wrapper.md` investigation
found the cause in the shipped bundle and recorded the one thing that changes the outcome:
**launched from PowerShell the hook runs; launched from Git Bash it dies at the `&`.**

That is a launch-shell choice, not a permission. It needs no `--force`, no `--yolo`, and
no new trust entry.

Instrument check first, from PowerShell, in the fixture:

```
prompt: "Run the shell command: git rev-parse HEAD"
-> SHA=f28584332c7c64b60af887f3ea2b835ebca06c6a
git rev-parse HEAD -> f28584332c7c64b60af887f3ea2b835ebca06c6a
```

The SHA matches the fixture's real HEAD, so a command genuinely executed. A host that
prints a plausible sha it invented would have failed this.

**The full run then completed all four steps**: 5 files added, 1 modified over 31 rows —
`plan.md`, `loops.md` (3 loops), `state/external-task-envelope.json`,
`state/history.jsonl`, `PLANS-INDEX.md`, with `PLANNING.md` updated. No `BLOCKED.md` was
written, and its absence was checked rather than assumed. Envelope: `base_sha`
`f28584332c7c64b60af887f3ea2b835ebca06c6a` = real HEAD, `base_ref: master` = real branch.
Controller re-ran the validator: exit 0.

Invocation: `cursor-agent -p --trust --auto-review --model cursor-grok-4.6-medium`, prompt
on stdin, launched from PowerShell.

## claude — the one that cannot, and the adapter has said so since before this loop

The claude fixture was pre-authorised with `herdr-trust.py --any --apply`, the operator
having authorised that write. It reports a **second gate** the trust write does not clear:
the adapter's own `.claude/settings.json` pre-approves four `.advanced-plans/**`
permissions, and claude consents to those separately.

**First run was not a fair test and is recorded as such.** The prompt named
`.agents/skills/advanced-planning/SKILL.md`, which is the *codex and cursor* path. claude
correctly refused to substitute a differently-named skill set, wrote `BLOCKED.md`, and
reported its refusals verbatim. That was my prompt's defect, not the host's. Re-run
host-neutrally — *discover what this installation provides for THIS host yourself.*

Second run: 6 files added over 60 rows — `plan.md`, `loops.md`,
`state/external-task-envelope.json`, `PLANS-INDEX.md`, `.claude/logs/model-audit.log`, and
`BLOCKED.md`. No `history.jsonl`.

Two blockers, both named by the host and both verified here:

**1. The validator could not be run.** Under `acceptEdits`, every attempt was refused
before a process started — `This command requires approval` on Bash, and on PowerShell
`This PowerShell command contains multiple operations. The following part requires
approval`. The session is non-interactive, so no approval could arrive. The host reported
**no exit code rather than inventing one**, which is the behaviour this programme keeps
asking for and rarely gets.

I attempted to pre-authorise this the way the todo asks, with a scoped
`--allowedTools "Bash(python:*)"` on the nested invocation. **The auto-mode classifier
refused the whole call.** That is the self-widening guard working correctly, and it is not
something to route around, so it is recorded as a limit on what a controller can
pre-authorise here: folder trust can be written ahead of time; tool permission cannot.

**2. The adapter does not emit envelopes, and says so.** Verified by opening the cited
line rather than repeating the claim — `.claude/commands/next-loop.md:355-359`:

> *"The external task envelope described in `core/agents/orchestrator.md` would be the
> better source and is not available: nothing in this adapter writes one, and
> `loop-ready.json` has no path fields and a schema that forbids extras. **Migrating the
> adapter to emit an envelope is a Phase 7 item**; until then this is the scope the running
> system can actually produce."*

So the envelope claude wrote validates at exit 0 and names the real repository and the real
HEAD (`7b6d5639d1a37b5ce28c08fe00d268c2a5f20090`) — but the host chose the *path* itself,
from the state bus `PLANNING.md` declares, because the installation names none. It flagged
that in `BLOCKED.md` rather than leaving it implicit. Scored honestly, that is not step 3
completed; it is step 3 improvised, and disclosed.

### The structural finding underneath it

The claude-code adapter installs a **different set** from the other three. codex, cursor and
opencode each get 8 skills including the shared `advanced-planning` router. claude-code gets
9 skills with **no router**, plus `.claude/commands/` and `.claude/agents/`, and the envelope
concept lives only in the agent prompts. The four hosts do not have the same entry point,
and that is the real reason criterion 2 cannot close on claude — not trust, and not
permissions, which merely stopped step 4 on top of it.

## A shipping defect found on the way

Every claude run in a trusted workspace printed:

```
Permission allow rule (.claude\settings.json): Write(.advanced-plans/**) is not matched by
file permission checks — only Edit(path) rules are. Use Edit(.advanced-plans/**) instead.
Permission allow rule (.claude\settings.json): MultiEdit(.advanced-plans/**) is not matched
by file permission checks — only Edit(path) rules are.
```

Two of the four permissions the claude-code adapter installs **do nothing**. This was
invisible before today because an untrusted workspace discards all four with a different
message — the very warning that confounded F21. The same four entries appear in
`setup-with-claude`'s `references/settings-snippet.json`, so the AAW installer ships them
too. Not fixed here: it is outside this loop's `allowed_paths` and belongs to whoever owns
the adapter's settings template.

## F21, settled as a by-product

loop-007-6 recorded F21 as un-discriminated: claude answered from the global
`~/.claude/skills` copy, but an untrusted workspace was an un-eliminated alternative cause.
The trust write the operator authorised removes that alternative. Re-running the same canary
probe in the now-trusted `l0076/fixture`:

- the *"this workspace has not been trusted"* warning is **gone**
- `DESC=Generate structured, verifiabl` — still **token-free**, neither `CANARYCLAUDE7Q4Z`
  (project `.claude/skills`) nor `CANARYAGENTS3M8X` (project `.agents/skills`)

**claude prefers the global copy on a name collision. It is precedence, not trust** — the
same answer as opencode, now measured rather than left open. Criterion 1's rewrite stands
unchanged; this closes the one question it had to leave open.

## Mode per host, so a withheld permission is never read as an adapter defect

| host | invocation | mode |
|---|---|---|
| codex | `codex exec -s workspace-write --skip-git-repo-check`, stdin | write |
| cursor | `cursor-agent -p --trust --auto-review --model cursor-grok-4.6-medium`, stdin, **from PowerShell** | write |
| claude | `claude -p --permission-mode acceptEdits` | write for edits, **Bash refused** |

Versions: codex-cli 0.153.0 (`gpt-5.6-sol`), claude 2.1.259, cursor-agent 2026.08.31-4057e58.

No `--dangerously-bypass-approvals-and-sandbox`, no `--force`, no `--yolo`, and no dialog
was answered by anyone. Nothing was written to either repository checkout.

## Profile writes made, and how to undo them

Two folder-trust entries were added to `~/.claude.json`, both for throwaway scratch
fixtures, under the operator's authorisation:

- `.../scratchpad/l0077/fx-claude`
- `.../scratchpad/l0076/fixture`

A backup of the file as it stood before is at `scratchpad/l0077/claude.json.bak`
(145 395 B). Removing the two entries is deleting two lines; nothing else in the profile was
touched, and no tool permission was granted anywhere.

## Criterion 2, scored

Three of four hosts complete it end to end. The fourth cannot, for a documented reason the
adapter states in its own shipped text, with the migration already assigned to Phase 7.

Per this loop's check 4 — *"where a host still cannot complete unattended, that is recorded
as the result with its blocker named, not as a deferral"* — that is the result. Criterion 2
is **met on codex, cursor and opencode, and failed on claude-code**, and the failure has a
named cause, a shipped citation, and an existing owner.
