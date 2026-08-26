# Herdr operations for Advanced AI Workflows on Windows

This is the practical operating guide for running Advanced AI Workflows (AAW) with persistent Claude Code, Codex, OpenCode, and Cursor sessions on native Windows.

Herdr is the session, pane, and worktree manager. Advanced Planning remains the planner. AAW remains the workflow policy and evidence layer.

> **Machine-level herdr knowledge lives in `~/Coding/herdr-ops`** — the runtime
> capability matrix, the numbered blockers B1–B7, and the distilled operating
> rules. This document covers what is specific to *this programme*: worktree
> ownership, envelopes, gates, and the run audit trail. Where the two overlap,
> `herdr-ops` is authoritative on herdr behaviour and this document on AAW policy.

## Recommended setup

- Windows Terminal
- PowerShell 7 where available
- Git for Windows
- native Herdr stable channel
- the agent CLIs you actually intend to use
- one named Herdr session for AAW work

Run Herdr directly. Do not put AAW-managed agents behind psmux or another nested multiplexer. Nested terminal management makes agent status, current-directory detection, and session identity harder to observe. Psmux can remain installed for unrelated shell workflows.

## 1. Preflight

In PowerShell:

```powershell
$PSVersionTable.PSVersion
git --version

Get-Command claude -ErrorAction SilentlyContinue
Get-Command codex -ErrorAction SilentlyContinue
Get-Command opencode -ErrorAction SilentlyContinue
Get-Command cursor-agent -ErrorAction SilentlyContinue
Get-Command agent -ErrorAction SilentlyContinue
```

Only install Herdr integrations for CLIs that are present and authenticated. AAW does not copy credentials between providers.

Use absolute paths throughout this guide. Resolve each repository once:

```powershell
# Adjust to your checkout locations. These are the audited paths on the reference machine.
$AawRoot = (Resolve-Path 'C:\Users\mharvey2\Coding\Advanced-AI-Workflows').Path
$GstackRoot = (Resolve-Path 'C:\Users\mharvey2\Coding\gstack-fork').Path
$PlanningRoot = (Resolve-Path 'C:\Users\mharvey2\Coding\advanced-planning').Path
$SuperpowersRoot = (Resolve-Path 'C:\Users\mharvey2\Coding\superpowers').Path

# Global locations MUST resolve from USERPROFILE, never HOME/HOMEDRIVE/~ - on a managed
# Windows profile those can point at a mapped network drive. See baseline audit section 7.
$GlobalRoot = (Resolve-Path $env:USERPROFILE).Path
```

Do not use Git Bash `~` for global install or cleanup targets. The v0.1 smoke exercise demonstrated that its home can differ from `%USERPROFILE%`.

### 1.1 Always invoke Herdr through the launcher

On a managed Windows profile the logon process injects `HOMEDRIVE`/`HOMEPATH` from the Active
Directory home-folder attribute, and Git Bash derives `HOME` from those. Herdr honours `HOME` when
it is set and falls back to `USERPROFILE` when it is not, so the failure is **shell-specific**:
PowerShell (where `HOME` is normally unset) resolves correctly, while Git Bash probes
`M:\.claude\`, `M:\.codex\`, and so on, and reports every integration as `not installed`.

Two launchers pin `HOME`, `HOMEDRIVE` and `HOMEPATH` from `USERPROFILE` for the child process only,
then hand off to `herdr` with your arguments:

```bash
tools/herdr-env.sh integration status     # Git Bash - the one that matters here
tools/herdr-env.sh --assert               # doctor check; exit 1 if any target runtime is wrong
```

```powershell
tools\herdr-env.ps1 integration status
tools\herdr-env.ps1 -Assert
```

`--assert` / `-Assert` checks only the four target runtimes — `claude`, `codex`, `opencode`,
`cursor`. Herdr 0.8.2 ships integrations for seventeen runtimes and `not installed` is the correct
answer for the thirteen this project does not use, so a check that fails on any occurrence of that
string would fail permanently. The assertion exits non-zero if a target reports `not installed` or
resolves to a path outside the real profile.

Run `tools/herdr-env.sh --assert` after any Windows profile change, any Herdr update, and any
sign-out and sign-in. See
[`.advanced-plans/evidence/2026-08-26-phase-3-loop-001-environment-pin.md`](../.advanced-plans/evidence/2026-08-26-phase-3-loop-001-environment-pin.md)
for the verification, including the negative test.

**`cursor-agent`.** The Cursor IDE bundles a complete CLI inside its extension storage and does not
put it on `PATH`. If `Get-Command cursor-agent` finds nothing, look under
`%USERPROFILE%\AppData\Roaming\Cursor\User\globalStorage\anysphere.cursor-agent-worker\agent-cli\.local\share\cursor-agent\versions\`
before installing anything. A shim at `%USERPROFILE%\.local\bin\cursor-agent.cmd` that resolves the
newest version directory at run time survives Cursor upgrades.

## 2. Install Herdr stable

Use Herdr's official native Windows installer:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
```

If endpoint controls prohibit fileless PowerShell, follow Herdr's documented `install.cmd` alternative instead of weakening the endpoint policy.

Open a new PowerShell and verify:

```powershell
herdr --version
herdr channel set stable
herdr update
```

Stable is the normal AAW channel. Preview is appropriate only for a specific Windows fix that has been tested against a disposable AAW pilot.

## 3. Create a named AAW session

Use a named session so scripts and later terminals address the same server:

```powershell
$env:HERDR_SESSION = 'aaw'
herdr
```

Inside Herdr, `Ctrl+B`, then `Q`, detaches. Closing Windows Terminal also leaves local persistent panes running. Reattach later with:

```powershell
$env:HERDR_SESSION = 'aaw'
herdr session attach aaw
```

Inspect sessions from any PowerShell:

```powershell
herdr session list --json
```

Keep `HERDR_SESSION=aaw` set in every PowerShell that issues automation commands. Without it, a command may address the default session instead.

## 4. Install provider integrations

Herdr can detect processes without every integration, but current official integrations improve status, current-directory reporting, native session identity, and supported session restore.

```powershell
herdr integration install claude
herdr integration install codex
herdr integration install opencode
herdr integration install cursor
herdr integration status
```

Re-run the install command for any integration shown as outdated. Restart or reload an affected provider session if its integration requires startup-time registration.

The provider CLIs remain responsible for sign-in. Start each once normally and complete its authentication before attempting unattended dispatch.

## 5. Create the AAW controller workspace

The controller workspace is the sole writer to `.advanced-plans/state/` and the other authoritative planning files.

```powershell
$Controller = herdr workspace create `
    --cwd $AawRoot `
    --label 'aaw control' `
    --no-focus | ConvertFrom-Json

$ControllerWorkspace = $Controller.result.workspace.workspace_id
$ControllerPane = $Controller.result.root_pane.pane_id

herdr agent start aaw-controller `
    --kind claude `
    --pane $ControllerPane `
    --timeout 120000
```

The workspace response exposes the workspace, tab, and root-pane IDs. Save them in the current PowerShell session; do not scrape IDs from the terminal screen.

Start with the prompt in `docs/herdr-kickoff-prompt.md`:

```powershell
$PromptPath = Join-Path $AawRoot 'docs\herdr-kickoff-prompt.md'
$Prompt = Get-Content -Raw $PromptPath

herdr agent prompt aaw-controller $Prompt `
    --wait `
    --until idle `
    --until done `
    --until blocked `
    --timeout 7200000
```

If the controller is already working, do not send another long prompt and assume the wait applies only to the new turn. Herdr documents that a wait can be satisfied by the currently active turn. Inspect the agent first.

## 6. Create a worker worktree

Every concurrent writing task receives a separate Herdr worktree. Example:

```powershell
$Created = herdr worktree create `
    --cwd $SuperpowersRoot `
    --branch 'sync/upstream-2026-08-26' `
    --base upstream/main `
    --label 'superpowers upstream port' `
    --no-focus | ConvertFrom-Json

$WorkerWorkspace = $Created.result.workspace.workspace_id
$WorkerPane = $Created.result.root_pane.pane_id

herdr agent start superpowers-sync `
    --kind codex `
    --pane $WorkerPane `
    --timeout 120000
```

Then submit a bounded prompt:

```powershell
$Task = @'
Read the AAW design spec and docs/upstream-sync-playbook.md supplied in the
task context. Work only in this existing Herdr-owned worktree. Do not create a
second worktree, push, merge, force-reset, or edit a default branch. Implement
the stated behaviour and run the declared checks. Finish with: changed paths,
commands and exit codes, unresolved risks, and the current commit/status.
'@

herdr agent prompt superpowers-sync $Task `
    --wait `
    --until idle `
    --until done `
    --until blocked `
    --timeout 7200000
```

When Herdr owns the worktree:

- do not start Cursor with `--worktree`;
- do not ask Claude Code to create a native worktree;
- do not run Superpowers' worktree creation step again; and
- tell the agent that isolation is already prepared.

### Expect a first-run trust dialog

A newly created worktree is a directory the provider has never seen, so `claude` and `cursor` both present a workspace-trust prompt on start; `opencode` does not. Because AAW creates a worktree per loop, this fires on **every** claude/cursor worker start, not once per machine. Clearing it requires `herdr agent send-keys`, which means an operator. Plan for it in any fan-out that starts those two runtimes.

## 7. Operate a running agent

### Inspect state

```powershell
herdr agent list
herdr agent get superpowers-sync
herdr agent explain superpowers-sync --verbose
```

Herdr states have narrow meanings:

| Herdr observation | Meaning for AAW |
|---|---|
| `working` | agent appears active; wait or inspect |
| `idle` | ready for input in a seen tab; collect evidence before judging success |
| `done` | ready for input after unseen background work; still requires evidence |
| `blocked` | recognised question or approval UI; user action is required |
| `unknown` | agent is present but classification is uncertain; not success |

### Read output

For an idle agent:

```powershell
herdr agent read superpowers-sync `
    --source recent-unwrapped `
    --lines 160
```

For a working or blocked full-screen agent, use a passive visible read:

```powershell
herdr agent read superpowers-sync `
    --source visible
```

Long alternate-screen history reads may require the agent to be idle. If a complete result cannot be recovered reliably, prompt the agent when idle to write a Markdown report in its worktree and return the path.

### Wait deliberately

```powershell
herdr agent wait superpowers-sync `
    --until idle `
    --until done `
    --until blocked `
    --timeout 1800000
```

Omitting `--timeout` waits indefinitely. AAW automation should always set a task-appropriate timeout and treat timeout as an observation, not automatic failure or permission to terminate the agent.

### Handle a blocked agent

`herdr agent prompt` intentionally refuses to submit a normal prompt while an agent is already blocked. Read the visible UI, focus the agent inside the Herdr session, and answer the actual approval or question. For a simple UI selection, `herdr agent send-keys <name> <key>` is available, but do not guess at an approval choice.

Useful commands:

```powershell
herdr agent read superpowers-sync --source visible
herdr agent focus superpowers-sync
herdr session attach aaw
```

**Cursor's blocked state is not trustworthy.** Verified 2026-08-26: cursor-agent sat at a full-screen "Workspace Trust Required" modal while Herdr reported `idle` with `interactive_ready: true`, and `state_change_seq` did not move across the entire modal-to-cleared transition. It *does* report `blocked` for mid-turn shell-approval dialogs, but then lags — still `blocked` after the dialog was answered and the pane showed "Running". Read the pane before dispatching to a cursor agent; do not act on its state alone. Claude reports the same conditions correctly on two channels (`agent_not_ready` at start, `agent_blocked` at prompt).

Cursor also requires approval for **every** non-allowlisted shell command — one trivial commit task produced two separate approval stops. Unattended cursor work needs its allowlist pre-configured or it will stall repeatedly mid-task.

The controller records the question and the user's response in the run audit trail.

### Follow up after collection

Only send a correction prompt when the agent is idle/done and the collector has found a concrete defect:

```powershell
herdr agent prompt superpowers-sync `
    'The independent check found <specific issue>. Correct only that issue, rerun <checks>, and report the new evidence.' `
    --wait `
    --timeout 3600000
```

## 8. Collect evidence

An agent reaching `idle` or `done` is not proof of completion. The controller must independently inspect the worktree.

Until `aaw collect` exists, collect at least:

```powershell
git -C '<absolute-worktree-path>' status --short
git -C '<absolute-worktree-path>' diff --check
git -C '<absolute-worktree-path>' diff --stat '<base-sha>...HEAD'
git -C '<absolute-worktree-path>' diff '<base-sha>...HEAD'
git -C '<absolute-worktree-path>' log --oneline --decorate --max-count 12
```

Then run the task's declared test, lint, build, and package checks from the worktree. Record each exact command and exit code. Confirm every changed path is inside the task's allowed scope.

The result needs four independent pieces:

1. agent summary/transcript;
2. Git status and diff;
3. check commands and exit codes; and
4. review verdict from a different provider or a human.

Only the controller copies a redacted result into `.advanced-plans/evidence/` and advances Advanced Planning state.

## 9. Choose agents by role

Do not rotate providers merely for variety. Assign a provider based on role and use a different one for independent review where practical.

| Role | Recommended starting choice | Reason |
|---|---|---|
| AAW/Advanced Planning controller | Claude Code | current planning workflow is strongest and already implemented there |
| bounded implementation | Codex, OpenCode, Cursor, or Claude | task envelope makes the provider replaceable |
| upstream sync audit | Codex or Claude | strong repository/diff inspection; use another provider for review |
| independent code/spec review | provider different from implementer | reduces correlated assumptions |
| quick read-only investigation | native subagent or lightweight Herdr pane | no worktree or durable run overhead unless resumability is needed |

The provider list is policy, not a queue. A runtime that is unauthenticated, unavailable, or poor at a task is skipped explicitly.

### Verified runtime capability constraints (2026-08-26)

| Runtime | Loads an injected skill | Commits from a linked worktree | Startable unattended in a fresh worktree |
|---|---|---|---|
| opencode | yes | yes | **yes — the only one** |
| claude | yes | yes | no — trust dialog on every new worktree |
| cursor | yes | yes | no — trust modal, then approval per shell command |
| codex | not retested | **no** | no |

**Codex cannot `git commit` inside a Herdr worktree.** A linked worktree's Git metadata lives in the parent repository's `.git/worktrees/`, outside codex's sandbox (pilot F1). Any envelope whose evidence requirement is `git_commit` must therefore go to opencode or claude, or the controller must perform the commit itself after collection. This is a per-runtime sandbox property, not a limitation of the worktree mechanism.

Commit attribution differs by runtime: cursor adds a `Co-authored-by: Cursor` trailer; codex inherits the operator's Git identity unmarked. See `programme-git-policy.md`.

## 10. Native provider features versus Herdr

Some providers can create their own background agents or worktrees. Use exactly one manager for a run:

- choose Claude-native Agent View when the whole run is Claude-only and Claude owns every spawned worktree;
- choose Cursor `--worktree` when Cursor alone owns the run and Herdr is not creating that worktree;
- choose Herdr for cross-provider work, durable Windows panes, externally controlled prompt/wait/read, or a common worktree policy;
- never have Herdr create the checkout and then enable a provider's second worktree layer.

Provider-native subagents inside one Herdr pane are allowed for read-only exploration or task-local reasoning. They do not become separately managed AAW runs unless the controller emits separate task envelopes.

## 11. Detach, restore, and update

Herdr persists local sessions after the client detaches or Windows Terminal closes. Official provider integrations can also report native session references used for supported agent restore after a Herdr server restart.

Check integrations before relying on restore:

```powershell
herdr integration status
```

If a server restart restores only a normal shell rather than the provider session, mark the AAW run `interrupted`. Inspect Git and transcript state, then either resume the provider explicitly or start a continuation run. Never infer completion from a restored shell.

Windows Herdr updates require running the installer/update path and restarting active Herdr sessions; live server handoff is Unix-only. Before updating during active work:

1. collect current Git state and provider session references;
2. stop creating new runs;
3. let critical writes settle;
4. update Herdr;
5. restart/reattach; and
6. verify each run before resuming.

## 12. Safe completion and cleanup

Before push:

- inspect the complete diff;
- run declared checks;
- obtain independent review;
- confirm the branch and remote;
- ask for the external-write gate.

Before removing a worktree:

```powershell
herdr workspace get $WorkerWorkspace
git -C '<absolute-worktree-path>' status --short
```

If clean, terminal, and no longer needed:

```powershell
herdr worktree remove --workspace $WorkerWorkspace
```

Herdr removes the checkout through Git and leaves the branch. If it refuses, inspect why. Do not add `--force` to a routine cleanup.

Closing a Herdr workspace is not the same as removing its Git worktree. Use `workspace close` only when you intentionally want to preserve the checkout outside the Herdr UI.

### Ordering: remove the worktree before closing anything

The order is not cosmetic. **`herdr worktree remove` first, pane/workspace close only after.** Removal is Git-aware: it deregisters the worktree from the parent repository's `.git/worktrees/` and leaves the branch. Closing the pane first destroys the only thing holding that path open, and the worktree registration is then orphaned — Herdr can no longer remove it properly and you are left tidying directories by hand.

Two ordering traps observed on 2026-08-26:

- **Deleting the parent repository first orphans every worktree under it.** `rm -rf` on the parent checkout removes `.git/worktrees/`, after which `herdr worktree remove` cannot do a clean job on any child worktree. Remove the worktrees, then the parent.
- **Closing the worker pane before removing the worktree** has the same effect for that one worktree.

### `Permission denied` on removal is a lock, not a policy refusal

```
{"error":{"code":"worktree_remove_failed",
 "message":"error: failed to delete '<path>': Permission denied"}}
```

On Windows this means a live process still has that directory as its working directory — usually the worker pane's shell, which persists after the agent itself has exited. **`--force` does not help**, because the obstacle is a filesystem lock rather than a Git safety check; passing it only risks forcing a removal that may already be partly done (pilot F2). The working sequence is:

1. `herdr worktree remove --workspace <ws>` — attempt it first, without `--force`;
2. if it fails on a lock, `herdr pane close <ws>:<pane>` to release the working directory;
3. retry the removal.

Check whether the directory still exists before concluding the removal failed. Pilot F2 recorded `worktree_remove_failed` being reported *after* the destructive part had already completed, so the error alone does not tell you what state you are in.

### Budget for auto-created parent workspaces

`herdr worktree create --cwd <repo>` creates a workspace for the new worktree **and** one for the parent repository if it is not already open. Cleanup debt is therefore roughly double the number of worktrees created. The parent workspace is a worktree-group root, so closing its pane returns `confirmation_required: "closing this pane would close a worktree group"` and needs an explicit confirmation — plan for an operator step, or leave the group root open.

## 13. First pilot checklist

Run this before dispatching the real package updates:

- [ ] Herdr stable starts natively in PowerShell.
- [ ] Named session `aaw` appears in `herdr session list --json`.
- [ ] Available provider integrations report current.
- [ ] One provider starts in a disposable repository and reaches idle.
- [ ] A read-only prompt reaches working, then idle/done.
- [ ] A deliberate harmless question produces a visible blocked state.
- [ ] A disposable Herdr worktree is created on a non-default branch.
- [ ] The worker changes one allowed file and runs one check.
- [ ] A different provider reviews the diff.
- [ ] Detach and reattach preserve the session.
- [ ] Clean worktree removal succeeds without `--force`.
- [ ] No `.advanced-plans/state/` file was written from the worker worktree.

## 14. Troubleshooting boundaries

### Herdr cannot classify an agent

Run:

```powershell
herdr agent explain <agent-name> --verbose
herdr integration status
```

Capture Herdr version, Windows version, terminal, shell, named session, relevant logs, and exact reproduction steps for an upstream report.

### Current directory appears stale after `cd`

Herdr documents live PowerShell directory tracking as dependent on shell/integration reporting. Create a workspace or pane with the correct starting `--cwd` rather than relying on a later `cd`, and keep the official integration installed.

### Cursor rendering flickers

Herdr's native Windows path uses ConPTY. The default drawn cursor favours stability. Only change `host_cursor` if an IME or terminal-specific need justifies the trade-off described in the Herdr Windows documentation.

### Direct terminal attach fails on Windows

Herdr documents `herdr terminal attach` as unsupported on native Windows. Reattach to the Herdr session UI and focus the agent instead. Do not redesign AAW around the unsupported command.

### `agent_prompt_stalled` immediately after starting an agent

`herdr agent start` can return `agent_started` with `agent_status: "idle"` and `interactive_ready: true` while the provider's TUI is still painting its splash screen. A prompt sent at that moment is rejected:

```
{"error":{"code":"agent_prompt_stalled",
 "message":"agent prompt produced no observed state change within 5000 ms; status is idle and state_change_seq remained 87"}}
```

The reported ready state is not a guarantee the composer will accept input. **Retry the prompt** — one retry was sufficient in testing. This is not a multi-line or bracketed-paste problem: multi-line prompts submit correctly once the agent is warm.

### Agent is done but output is incomplete

Read `recent-unwrapped` while idle. If the alternate-screen transcript remains incomplete, have the agent write a task report file in the worktree, then verify its claims independently.

## Official Herdr references

- [Windows support](https://herdr.dev/docs/windows-beta/)
- [Agents](https://herdr.dev/docs/agents/)
- [Agent automation](https://herdr.dev/docs/agent-automation/)
- [CLI reference](https://herdr.dev/docs/cli-reference/)
- [Session state and restore](https://herdr.dev/docs/session-state/)
