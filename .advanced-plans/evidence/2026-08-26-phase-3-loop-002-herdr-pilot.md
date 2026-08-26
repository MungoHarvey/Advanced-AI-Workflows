# Phase 3 loop 002 — disposable Herdr pilot

**Collected:** 2026-08-26
**Loop:** `.advanced-plans/phases/phase-3/loops.md` → `ralph-loop-002`
**Covers:** all ten items of `docs/herdr-kickoff-prompt.md` Step 4
**Herdr:** 0.8.2, server PIDs 60672 / 63176, started 2026-08-26 05:45:41
**Everything below was invoked through `tools/herdr-env.sh`,** never bare `herdr` — see
[loop 001](2026-08-26-phase-3-loop-001-environment-pin.md).

---

## Verdict

**Herdr is fit to be the execution layer for this programme.** It created a worktree on a path
containing a space, detected two different agent runtimes, reported `working` / `idle` / `done` /
`blocked` accurately and with sub-second latency, preserved blocking question text, and removed a
clean worktree without `--force`.

Four findings qualify that verdict. None of them blocks Step 5; two change how the programme must
be operated, and are inputs to loop 003.

| # | Finding | Severity | Consequence |
|---|---|---|---|
| F1 | A linked worktree is **not** an isolation boundary — trust and sandbox escalation both reach the parent repo | medium | Worktree-ownership policy must say so; a worker in a worktree is not contained |
| F2 | `herdr worktree remove` reports `worktree_remove_failed` **after** completing the destructive part | medium | An operator who reaches for `--force` on that error would be forcing an already-done removal |
| F3 | The agent gave a confident, wrong-by-omission answer that only controller-side verification caught | high (validates the rule) | The "verify with git, from the controller, every time" rule earns its place |
| F4 | ACC-10 detach/reattach cannot be exercised from the CLI at all | low | One manual step for the operator; recorded as a testability gap, not a failure |

---

## Step 4, item by item

| # | Kickoff item | Result |
|---|---|---|
| 1 | Disposable branch | ✅ `pilot/herdr-smoke` from `386de0a6c5b484119758bf66889f0fd408e93c7e` |
| 2 | Herdr worktree | ✅ workspace `w3` at `C:\Users\mharvey2\Coding\herdr pilot\aaw-smoke` — path contains a space |
| 3 | Non-controller provider started | ✅ `pilot-codex` (codex 0.146.0, `gpt-5.6-terra medium`) in pane `w3:p1` |
| 4 | Read-only prompt, `working` → `idle`/`done` | ✅ observed twice, timestamped |
| 5 | Harmless `blocked` question | ✅ observed **twice, by two different detection rules** |
| 6 | Trivial allowed edit | ✅ `PILOT-NOTE.md`, committed as `17327c69…` |
| 7 | Independent Git evidence | ✅ every claim re-derived by the controller; one claim disproved (F3) |
| 8 | Different provider reviews it | ✅ `pilot-opencode` — Qwen3.5-397B via ELM Proxy — verdict PASS |
| 9 | Detach and reattach | ⚠️ **not exercisable from the CLI** — see F4 |
| 10 | Remove clean worktree without `--force` | ✅ removed; `--force` never passed. See F2 for the misleading error |

---

## 1. Worktree creation on a path containing a space

```
herdr worktree create --branch pilot/herdr-smoke --base 386de0a6… \
  --path 'C:\Users\mharvey2\Coding\herdr pilot\aaw-smoke' --label aaw-herdr-pilot --no-focus
```

| Field | Value |
|---|---|
| Workspace | `w3` |
| Root pane | `w3:p1` (terminal `term_659ed58674b5d4`) |
| Path | `C:\Users\mharvey2\Coding\herdr pilot\aaw-smoke` |
| Branch | `pilot/herdr-smoke` |
| Base | `386de0a6c5b484119758bf66889f0fd408e93c7e` |

Controller-side confirmation:

```
$ git worktree list
C:/Users/mharvey2/Coding/Advanced-AI-Workflows  386de0a [docs/herdr-v0.2-import]
C:/Users/mharvey2/Coding/herdr pilot/aaw-smoke  386de0a [pilot/herdr-smoke]

$ git -C '…/herdr pilot/aaw-smoke' status --porcelain
(empty — clean)
```

The space in the path caused no problem at any point in the pilot, including removal.

---

## 2. Agent state transitions — `working`, `idle`, `done`

Sampled by polling `herdr agent list` in a loop and printing only the transitions.

**Read-only prompt** ("report how many lines ROADMAP.md has"):

```
06:34:14.947  done     seq=27      <- steady state before the prompt
06:34:16.561  working  seq=28      <- 1.6 s after submission
06:34:25.988  done     seq=29      <- turn complete, 9.4 s of work
```

`herdr agent prompt … --wait` returned exactly at the `done` edge. `state_change_seq` is monotonic
and is a better completion signal than the state name, because `done` is a resting state that also
precedes the next turn.

**Startup trust prompt** (`blocked` → `idle`), sampled the same way:

```
06:31:44Z  blocked  seq=24
06:31:46Z  idle     seq=25
```

Herdr distinguishes `idle` (never prompted / returned to rest) from `done` (a turn just ended).
Both are resting states and, per the programme rule, neither is completion evidence.

---

## 3. `blocked` — observed twice, by two different rules

This is the ACC-09 mechanism, and it works. `herdr agent explain` names the detection rule and
quotes its evidence.

**Rule 1 — screen-region match, at startup:**

```
agent: codex
state: blocked
manifest: remote:…\agent-detection\remote\codex.toml 2026.08.09.1
rule: trust_directory (region=top_non_empty_lines(20) priority=950)
evidence: "> You are in C:\\Users\\mharvey2\\Coding\\herdr pilot\\aaw-smoke\n\n
  Note: You're in a subdirectory of a Git project. Trusting will apply to the repository root:\n
  C:\\Users\\mharvey2\\Coding\\Advanced-AI-Workflows\n\n  Do you trust the contents of thi..."
```

**Rule 2 — OSC terminal-title match, mid-turn approval:**

```
agent: codex
state: blocked
rule: osc_title_blocked (region=osc_title priority=1100)
evidence: "[ . ] Action Required | aaw-smoke"
```

**Where the question text lives.** Rule 1 preserves the full question in `explain`'s `evidence`
field, because the rule matched on the screen text itself. Rule 2 does not — its evidence is only
the OSC title. In that case the question must be recovered with `herdr agent read`, which returned
the complete approval prompt including the exact command and all three options. **An automated
handler must therefore call `agent read`, not `agent explain`, to learn what it is being asked.**

`opencode` produced no trust prompt at all and went straight to `idle`. Blocking behaviour is a
per-provider property, not a Herdr one.

### F1 — a linked worktree is not an isolation boundary

Two independent escalations in this pilot both reached outside the worktree:

- codex's trust prompt said in terms that trusting `…\herdr pilot\aaw-smoke` **applies to the
  repository root** `C:\Users\mharvey2\Coding\Advanced-AI-Workflows`;
- codex could not stage or commit inside its sandbox, because a linked worktree's Git metadata
  lives in the parent repo's `.git/worktrees/`. Its own words: *"The repository's Git metadata
  lives outside this workspace's writable sandbox, so staging/committing was blocked before any
  commit was made."*

A Herdr worktree is a **working-directory** boundary, not a trust or filesystem boundary. The
controller/worker separation in this programme is therefore enforced by policy and review, not by
the worktree mechanism. Loop 003's worktree-ownership document must say this explicitly.

---

## 4. The trivial edit, and F3 — why the agent report is not evidence

The agent was asked to create `PILOT-NOTE.md`, stage only it, and commit. It reported
`17327c697285a26731e90de835bc4fa0d399ad52`.

Controller-side re-derivation, run independently:

```
branch:        pilot/herdr-smoke
base SHA:      386de0a6c5b484119758bf66889f0fd408e93c7e
head SHA:      17327c697285a26731e90de835bc4fa0d399ad52   <- matches the claim
author:        Mungo Harvey <mharvey2@ed.ac.uk>
subject:       pilot: disposable smoke file

changed paths base..HEAD:  PILOT-NOTE.md
diff --stat:               1 file changed, 1 insertion(+)
status --porcelain:        (empty — clean)
content:                   Herdr pilot smoke file - disposable.

controller checkout HEAD:  386de0a…  (unchanged)
git ls-remote --heads origin 'pilot/*':  (empty — never pushed)
```

Every claim held. **The earlier one did not.**

Asked how many lines `ROADMAP.md` has, the agent ran
`(Get-Content -LiteralPath ROADMAP.md | Measure-Object -Line).Lines`, got `98`, and answered
*"ROADMAP.md has 98 lines"* with no caveat. Ground truth:

```
total lines (wc -l):  139
non-blank lines:      98
blank lines:          41
```

`Measure-Object -Line` counts lines *within* each input string and contributes nothing for an empty
one, so piping `Get-Content` through it silently drops every blank line. The answer was confidently
wrong by 30%, produced by a correct-looking tool invocation whose output was quoted verbatim.

Nothing in the agent's transcript flagged it. Nothing in Herdr's state model flagged it — the agent
went cleanly to `done`. Only re-running the measurement from the controller caught it. This is the
concrete case that justifies the programme rule: **`idle`, `done`, and terminal silence are not
completion evidence, and neither is a plausible number.**

### An operational note on prompt delivery

Submitting a prompt to a codex agent resting in `done` once landed as keystrokes in the TUI rather
than as text in the composer, opening codex's `/hooks` settings screen. Two `esc` presses recovered
it and the re-issued prompt worked normally. Not reproduced deliberately, but automation that fires
prompts at agents should read the pane back and confirm the prompt actually appears in the composer
before treating the turn as started.

---

## 5. Cross-model review (ACC-18) — the mechanism that replaced Plannotator

| Role | Provider | Model |
|---|---|---|
| Implementer | codex 0.146.0 | `gpt-5.6-terra medium` |
| Reviewer | opencode 1.18.23 | `Qwen/Qwen3.5-397B-A17B-FP8` (ELM Proxy, Edinburgh) |

Different provider **and** different model — the ACC-18 requirement, met without special
arrangement. The reviewer was pointed at the commit SHA and asked for a fixed four-line form:

```
MODEL: Qwen/Qwen3.5-397B-A17B-FP8
SCOPE: yes
CONTENT: Herdr pilot smoke file - disposable.
VERDICT: PASS - The commit only adds a single-line disposable smoke file as indicated by the
         commit message.
```

Review turn: 16.2 s. Both factual claims — scope and content — match the controller's independent
verification exactly.

The gate that replaced Plannotator is demonstrated on real output. Note it was demonstrated on a
one-line commit that was genuinely correct; this proves the *mechanism*, not the reviewer's ability
to catch a subtle fault.

**Worth carrying into loop 003:** the pilot commit was authored `Mungo Harvey <mharvey2@ed.ac.uk>`
with no agent attribution. Worker agents inherit the human's Git identity by default, so the Git
policy needs to say how agent-authored commits are to be marked.

---

## 6. F4 — detach and reattach could not be exercised

Herdr 0.8.2's session verbs are `list`, `attach`, `stop`, `delete`. There is **no CLI detach**;
detaching is the GUI keybinding `Ctrl+B`, `Q`. The available CLI routes were rejected:

- `herdr session stop` would terminate the only running session — which hosts this controller's own
  Claude agent. Not attempted.
- `herdr session attach` would seize the controller shell's stdin. Not attempted.

So item 9 is recorded as a **testability gap in the CLI**, not as a Herdr failure and not as a pass.
What was established instead, safely:

```
session   default   running   socket C:\Users\mharvey2\AppData\Roaming\herdr\herdr.sock
server    PIDs 60672 / 63176, started 05:45:41

agents at the end of the pilot:
  claude    working  w2:p1  term_659ebf938aa4c2  session 9795be8d-a9a0-436b-ba5b-fd72298244da
  claude    idle     w2:p2  term_659ebf97ae6e93  session 6c6349ea-1c58-4a90-820a-df097cedb2b8
  codex     done     w3:p1  term_659ed58674b5d4  session 01a03cc4-c099-7fc2-813b-02744dbf7d05
  opencode  done     w3:p2  term_659ed714c9e5a5  session ses_fc3369ec4ffe2uK4motj5qRaoL
```

Agents live in the persistent server and are addressed through the socket; every `herdr` command in
this pilot was a separate short-lived client process, and identity (`terminal_id`, agent session id)
stayed stable across all of them and across pane splits over roughly forty minutes. That is
consistent with session persistence but it is not the detach/reattach test.

**Action for the operator:** press `Ctrl+B`, `Q` in the Herdr window, reopen it, and confirm this
Claude pane and its session id survive. One minute of work, and it closes ACC-10.

---

## 7. Removal without `--force`, and F2

`--force` was never passed, at any point, to anything.

**First attempt**, with both agents still live in the worktree:

```
$ herdr worktree remove --workspace w3
{"error":{"code":"worktree_remove_failed",
          "message":"error: failed to delete 'C:/Users/mharvey2/Coding/herdr pilot/aaw-smoke': Permission denied"}}
```

The correct response to that is not `--force`. Windows was holding the directory because two agent
processes had it as their working directory. Closing the two pilot panes released it:

```
$ herdr pane close w3:p2   ->  ok
$ herdr pane close w3:p1   ->  ok
```

**Second attempt** then reported the workspace was already gone:

```
$ herdr worktree remove --workspace w3
{"error":{"code":"workspace_not_found","message":"workspace w3 not found"}}
```

### F2 — the first removal had already succeeded

Inspecting the state after the "failure":

```
directory contents:            (empty — only . and ..)
worktree .git pointer file:    absent
main repo .git/worktrees/:     absent — no registration left
git worktree list:             only the controller checkout
```

So `herdr worktree remove` had deleted every file and deregistered the Git worktree, and failed
only on the final `rmdir` of the now-empty directory. It reported `worktree_remove_failed` **after
completing the destructive part**, and closing the panes then removed the workspace record so the
retry could not find it.

The operational hazard is precise: an operator who sees `worktree_remove_failed` and reaches for
`--force` would be forcing an operation that has already happened. The remedy that worked — close
the panes, then remove the empty directory — needs no force at all.

The empty directory was removed with `rmdir` after confirming it held zero entries.

**ACC-17 holds.** A clean worktree was removed without `--force`.

---

## 8. Final state — nothing left behind

```
$ git worktree list
C:/Users/mharvey2/Coding/Advanced-AI-Workflows  386de0a [docs/herdr-v0.2-import]

$ git branch --list 'pilot/*'
(none — "Deleted branch pilot/herdr-smoke (was 17327c6)")

$ git ls-remote --heads origin 'pilot/*'
(none — never pushed)

$ herdr worktree list
docs/herdr-v0.2-import -> C:/Users/mharvey2/Coding/Advanced-AI-Workflows
```

`C:\Users\mharvey2\Coding\herdr pilot\` and its `aaw-smoke\` child are both gone. The disposable
branch was never merged and never pushed. The controller checkout stayed at `386de0a` throughout,
with no changes other than the pre-existing untracked `find-files.js`.

---

## 9. Incidental fix made during this loop

`cursor-agent` was on `PATH` for PowerShell but invisible to Git Bash, because Git Bash does not
consider `.cmd` when resolving a bare command name. Since this project's agents shell out through
Bash, the loop-001 outcome was only half true. Added
`C:\Users\mharvey2\.local\bin\cursor-agent` — an extensionless POSIX wrapper that execs the `.cmd`
beside it. Windows shells are unaffected, because an extensionless file is not in `PATHEXT`.

```
$ command -v cursor-agent
/c/Users/mharvey2/.local/bin/cursor-agent
$ cursor-agent --version
2026.08.11-e8db854
```

---

## 10. Workstream 0 exit gate

| Criterion | Status |
|---|---|
| Herdr installed natively | met |
| Integrations for all four runtimes | met, and assertable via `tools/herdr-env.sh --assert` |
| Cursor runtime available | met — from both PowerShell and Git Bash |
| Worktree creation, including paths with spaces | **met** |
| `working` / `idle` / `blocked` reported correctly | **met**, with `done` as a fourth state |
| Clean worktree removal without `--force` | **met** (see F2 for the misleading error) |
| Session preserved across detach/reattach | **open** — F4, one manual operator step |
| Recorded repository heads | met |
| Branch/tag/push policy | partial — loop 003 |

Step 4's stop condition — *"do not proceed to real sync work if Herdr cannot reliably create
worktrees, detect the chosen agents, or preserve the session"* — is satisfied on the first two
clauses outright. The third is evidenced but not proven, and the proof costs the operator one
keystroke pair.
