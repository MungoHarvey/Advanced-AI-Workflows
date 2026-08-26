# Herdr operations for Advanced AI Workflows on Windows

This is the practical operating guide for running Advanced AI Workflows (AAW) with persistent Claude Code, Codex, OpenCode, and Cursor sessions on native Windows.

Herdr is the session, pane, and worktree manager. Advanced Planning remains the planner. AAW remains the workflow policy and evidence layer.

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
$AawRoot = (Resolve-Path 'C:\src\Advanced-AI-Workflows').Path
$GstackRoot = (Resolve-Path 'C:\src\gstack').Path
$PlanningRoot = (Resolve-Path 'C:\src\advanced-planning').Path
$SuperpowersRoot = (Resolve-Path 'C:\src\superpowers').Path
$PlannotatorRoot = (Resolve-Path 'C:\src\plannotator').Path
```

Do not use Git Bash `~` for global install or cleanup targets. The v0.1 smoke exercise demonstrated that its home can differ from `%USERPROFILE%`.

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

### Agent is done but output is incomplete

Read `recent-unwrapped` while idle. If the alternate-screen transcript remains incomplete, have the agent write a task report file in the worktree, then verify its claims independently.

## Official Herdr references

- [Windows support](https://herdr.dev/docs/windows-beta/)
- [Agents](https://herdr.dev/docs/agents/)
- [Agent automation](https://herdr.dev/docs/agent-automation/)
- [CLI reference](https://herdr.dev/docs/cli-reference/)
- [Session state and restore](https://herdr.dev/docs/session-state/)
