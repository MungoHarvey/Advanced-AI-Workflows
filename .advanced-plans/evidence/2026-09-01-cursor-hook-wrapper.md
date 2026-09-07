# cursor-agent runs a PowerShell hook wrapper through a POSIX shell

**Date:** 2026-09-01
**Subject:** `cursor-agent` 2026.08.25-3e8eec8 (bundled under the Cursor IDE's `anysphere.cursor-agent-worker` globalStorage)
**Status:** root cause found by reading the shipped bundle. Read-only investigation — nothing on this machine was reconfigured.
**Why it matters here:** this is the blocker that stopped `loop-005-3` at step 4. It is not the adapter's fault and not this programme's to fix, so it is written up for upstream.

---

## The symptom

Every shell command `cursor-agent` attempts on this machine is refused before it runs:

```
Hook blocked with message: --: eval: line 1: syntax error near unexpected token `&'
--: eval: line 1: `$OutputEncoding = [System.Text.Encoding]::UTF8; Get-Content -LiteralPath
'…\cursor-hooks-XXXXXX\payload.json' -Raw | & { $input | python
"…\fair-data-prep\0.4.1/hooks/block_prune.py" }'
```

A POSIX shell is being handed PowerShell and dies at the `&` of the call operator.

## It is not the hook

The hook that triggers it declares a plain, portable, shell-agnostic command:

```json
{"matcher": "Bash", "hooks": [{"type": "command",
 "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/block_prune.py\""}]}
```

There is no PowerShell in it. `cursor-agent` adds the wrapper.

## It is not the environment, and not a second binary

Ruled out by controlled pairs, each re-run in the same fixture with the same one-line
prompt (`git rev-parse HEAD`, delivered on stdin):

| Hypothesis | Test | Result |
|---|---|---|
| `$SHELL` selects the interpreter | `env -u SHELL` vs inherited `SHELL=/usr/bin/bash` | **both fail** — identical error |
| `MSYSTEM` / MinGW markers select it | `env -u MSYSTEM`, then also `-u MINGW_PREFIX -u MSYSTEM_PREFIX` | **both fail** |
| Git Bash and PowerShell launch different builds | resolve `cursor-agent` in each shell | **same build** — Git Bash takes the extensionless POSIX shim, which is 12 lines that `exec` the very `cursor-agent.cmd` PowerShell resolves |

What *does* change the outcome is the shell the CLI is launched from: launched from
PowerShell the same probe returns the sha and the hook runs; launched from Git Bash it
fails as above, every time.

## The cause, read out of the shipped bundle

Three defects in one function, all in the command-hook execution path
(`190.index.js`, wrapper builder in `index.js`). Deminified:

**1. The transport mode can never be the one the code tests for.**

```js
getCommandHookPayloadTransportMode() {
  return this.options?.commandHookPayloadTransport === "stdin"
    ? "windows_temp_file"
    : "argv_heredoc";
}
shouldUseCommandHookDirectStdinTransport() {
  return "stdin" === this.getCommandHookPayloadTransportMode();
}
```

The getter returns only `"windows_temp_file"` or `"argv_heredoc"`, so
`shouldUseCommandHookDirectStdinTransport()` is **always false** and the direct-stdin
path — the one branch that would pass the hook command through untouched — is
unreachable. The names are also crossed: the option value `"stdin"` selects the
temp-file mode.

**2. The temp-file wrapper is PowerShell unconditionally.**

```js
function Z(payloadPath, command) {
  const n = payloadPath.replace(/'/g, "''");
  const r = /* prefix bare commands with & */;
  return `$OutputEncoding = [System.Text.Encoding]::UTF8; ` +
         `Get-Content -LiteralPath '${n}' -Raw | & { $input | ${r} }`;
}
```

No platform check, no shell check, no alternative branch.

**3. The fallback branch is PowerShell too, because its condition is hardcoded.**

```js
const e = !0;                                  // hardcoded true
...
C = e ? `@'\n${v}\n'@ | & ${cmd}`              // PowerShell here-string
      : `${cmd} <<'CURSOR_HOOK_EOF'\n${v}\nCURSOR_HOOK_EOF`;   // unreachable
```

The POSIX heredoc form — the only shell-neutral text in the function — cannot be
reached.

The resulting string is then executed by `this.shellExecutor`, the agent's ordinary
shell. Nothing in the path reconciles the two: the executor's shell is chosen by one
mechanism and the payload's syntax by another, and only one of them knows about
PowerShell. The bundle does know how to run `powershell.exe` and `pwsh` elsewhere —
they appear in the executor's shell table — but the hook path never consults it.

**Consistent with every observation:** the wrapper is always PowerShell, so the hook
succeeds exactly when the executor's shell happens to be PowerShell and fails when it
is POSIX.

**Not tested, so not claimed:** how this behaves on macOS or Linux. Reading the code
suggests the mismatch would arise anywhere the executor is a POSIX shell, but that is
an inference from the bundle, not a measurement, and command hooks are presumably
exercised on those platforms.

## No configuration escapes it

Both reachable transport modes emit PowerShell, so setting
`commandHookPayloadTransport` either way does not help. Nothing was changed on this
machine to confirm that, per the operator's instruction — it follows from the code
above.

## Minimal reproduction

1. Declare any `PreToolUse` command hook on `Bash` whose command is plain (`python foo.py`).
2. From a POSIX shell on Windows (Git Bash), run
   `cursor-agent -p --trust --auto-review --model <model> < prompt.txt`
   where the prompt asks for one shell command.
3. The hook is refused with `syntax error near unexpected token \`&'`.
4. Run the identical command from PowerShell: it succeeds.

## Suggested fix

Choose the payload syntax from the same fact that chooses the shell, rather than
independently. Failing that, the unreachable POSIX heredoc branch in (3) is already
written and would be correct for a POSIX executor — it needs a real condition instead
of `const e = !0`.

## Operator note

Until this is fixed upstream, `cursor-agent` cannot run shell commands on this machine
when launched from Git Bash, in any project. Launching it from PowerShell is a working
path and needs no configuration change. Removing or disabling the plugin hook would
also clear it, but that is a permissions decision and belongs to the operator, not to
this programme.
