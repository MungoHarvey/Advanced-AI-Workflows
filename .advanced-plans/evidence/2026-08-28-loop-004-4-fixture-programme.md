# loop-004-4 — the fixture programme, run on the hosts themselves

- **Date:** 2026-08-28
- **Status:** **CLOSED 2026-08-29.** opencode: both stages, verified
  controller-side. codex: stage 1 verified; **stage 2 deliberately not run**, by
  operator decision taken on the measured 98% weekly quota below — not an
  omission, and its marginal yield was low because codex stage 1 had already
  replicated both host findings. Check 1 is therefore satisfied on opencode only,
  and this record says so rather than rounding it up.
  Everything below is measured; nothing is projected.
- **Hosts:** opencode (`fxoc`, pane `w2:p1A`), codex (`fxcx`, pane `w2:p1B`)
- **Fixtures:** `<scratchpad>/fixtures-004-4/fx-opencode`, `fx-codex`
- **Repositories touched:** none. This loop writes only fixtures and this record.

## What this loop is for

> Run the fixture programme on each host, on that host — one phase, one loop, one
> external task — and record what actually happened rather than what the adapter
> intends.

It was designed as **two stages** precisely so the skill's human gate is genuinely
exercised: stage 1 asks for `phase` and says *stop at the gate*; stage 2 supplies
the approval. A single-shot exercise could not tell obedience from momentum.

## The invocation manifest (from the host's own datastore, not its self-report)

opencode records the session in `~/.local/share/opencode/opencode.db`. Queried from
a copy, read-only:

| Field | Value |
|---|---|
| model | `Qwen/Qwen3.5-397B-A17B-FP8`, provider `elm` |
| agent | `build` |
| session | `ses_fb6242628ffeImXpXTOVVtBV8L` |
| tokens | 429,355 in / 1,866 out |

The host self-reported the same model. That agreement is worth having, but the
database is the evidence — `argv` and self-report are both hearsay by comparison.

The host was asked for three identity facts and **declined the one it could not
observe** ("I cannot observe the exact command line I was launched with"), which is
what the envelope asked for rather than a guess.

## Stage 1 — the gate held, and this is proved from disk

The pane's scrollback caps at 38 lines and the report had scrolled off, so the
transcript was reconstructed from the session database (33 parts, 8 messages).

The host read the installed skill first (`.agents/skills/advanced-planning/SKILL.md`),
then wrote the plan, then printed the gate instruction verbatim:

```
REVIEW .advanced-plans/phases/phase-1/plan.md
Reply with exactly one:
  APPROVE phase-1 / REVISE phase-1: <instructions> / STOP phase-1
```

**Filesystem verdict, against the pre-run snapshot:** exactly **one** file added
(`.advanced-plans/phases/phase-1/plan.md`), **zero** removed, **zero** modified,
27 paths actually compared. `state/` empty, no `loop-ready.json`, no `history.jsonl`.

The comparison was proven to be capable of failing: a planted one-line edit to
`README.md` made the same check report `1 modified`, and the file was restored to
its recorded sha `7e98df7437f1`.

## Stage 1's real finding: the `phase` verb never touches the runtime

Extracted from the tool-call records (the *command* fields only — see the honesty
note below):

| | |
|---|---|
| tool calls | `bash` ×8, `read` ×1, `write` ×1 |
| `ap.py` invocations | **0** |
| `ap.py` existence tests | 1 (`Test-Path` → `True`) |

The host confirmed the runtime was present and then never called it. This is **not
disobedience** — the skill itself documents that `plan_io` has no `create_phase_plan`,
and the host said so unprompted. But it means Contract 6 ("reach the runtime only
through `ap.py`") is *unenforceable* for the first of the five verbs: there is
nothing to reach. The adapter installs a router whose opening verb routes nowhere.

## Stage 1's second finding: opencode's `bash` tool is PowerShell on Windows

Of the 8 commands issued through the tool named `bash`, **7 use PowerShell-only
cmdlets** (`Test-Path -LiteralPath`, `Get-ChildItem -Force`, `New-Item -ItemType`,
`Get-Command | Select-Object`) and all succeeded with authentic PowerShell output.
Exactly **one** (`python --version`) is valid POSIX `sh`.

Any skill, envelope or contract that prescribes POSIX shell will not run as written
on the opencode host on Windows. Nothing in the adapter says so.

## Stage 2 — approval sent; decomposition happened; then a dialog

`APPROVE phase-1` was delivered inline in the prompt (never as a path outside the
worktree — opencode gates on those). Measured from disk, attributed by mtime:

| File | mtime | Author |
|---|---|---|
| `phases/phase-1/plan.md` | 20:32:53 | stage 1 |
| `state/history.jsonl` | 20:43:19 | stage 2 |
| `phases/phase-1/loops.md` | 20:43:55 | stage 2 |

The approval event it appended:

```json
{"event":"phase_approved","phase":"phase-1","timestamp":"2026-08-28T19:43:19Z"}
```

It used the **`timestamp`** key, not `ts` — which is the tool's own convention and
further evidence that the 22 `ts` entries in the programme log are hand-append drift.

The host then stalled at a permission dialog before writing the envelope. **The
operator granted it, and stage 2 then completed.** Final state: 31 files, an
`envelope-001.json`, a second history event, and a modified `PLANNING.md`.

### Stage 2 used the runtime seven times — which *scopes* the stage-1 finding

| | stage 1 (`phase`) | stage 2 (post-approval) |
|---|---|---|
| `ap.py` invocations | **0** | **7** |

Stage 2 called `history_log`, `state_validate` (twice exploring the interface,
once for real), `--help` and `--check`. So the runtime is reachable and *is* used
wherever a function exists. The stage-1 finding therefore narrows to exactly what
it should be: **it is the `phase` verb that has no runtime path**, not the runtime
that is unreachable. Read from the live session DB read-only (127 parts, 24 shell
commands), never from a copy.

### The dialog was caused by the binding, and the transcript proves it

The host ran `ap.py --check` (which prints the resolved `source_root`) and then
issued three commands against
`...\.herdr\worktrees\advanced-planning\loop-004-cigate\core\schemas`, the last a
recursive search of that whole worktree for `*envelope*`. It was following the
installed runtime's own resolution, exactly as the corrected finding below states.
**It was not wandering.**

### The envelope validates cleanly — and describes a repository that does not exist

`envelope-001.json` passes `state_validate external-task-envelope` with **exit 0**,
controller-side. The same invocation form was proven able to fail in the same
breath: deleting `base_sha` gives exit 1, *"Missing required property: 'base_sha'"*.

But the fixture **is not a git repository** (`fatal: not a git repository`), and the
envelope declares `repository`, `base_ref: "main"`, `base_sha` of forty zeros,
`branch: "phase-1/health-flag"` and `isolation: "worktree"`. Invalid-fixtures exist
for `envelope-base-ref-without-sha.json` and `envelope-base-sha-abbreviated.json`,
so *shape* is policed. **Reality is not.** A forty-zero SHA is well-formed and
meaningless, and nothing downstream would discover that until a worker tried to
check the branch out.

**The host found this itself and disclosed it, unprompted**, after tabulating all
three git probes at exit 128:

> *"Git metadata: The envelope schema requires `base_ref` and `base_sha`
> (40-character SHA). This fixture directory is not a git repository, so I could
> not resolve real values. I used placeholder values (`main` and 40 zeros). The
> validation still passed because the schema validates format, not semantic
> correctness."*

That is the finding stated better than I had it, by the host under test.

## The finding this loop actually turned up

The host asked for permission to read
`~\.herdr\worktrees\advanced-planning\loop-004-cigate\core\state`.

My first reading was that it had wandered outside its fixture. **That was wrong, and
worth recording as wrong**, because the truth is more structural. `runtime.json`, written by
`setup/opencode/install.sh`, contains:

```json
{ "schema_version": 1,
  "source_root": "C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-004-cigate",
  "version": "0.16.0", "written_by": "setup/opencode/install.sh",
  "written_at": "2026-08-28T19:28:52Z" }
```

**The install bakes the installing checkout's path into the installed project.**
`ap.py` is a thin dispatcher that resolves the runtime to that `source_root`; the
host was following the installed runtime's own resolution, correctly. Consequences:

- The "fixture project" is **not self-contained and not isolated**. Every verb it
  runs executes code from a *herdr worktree of a local, unpushed branch*.
- Herdr worktrees are transient, so a project installed from one is bound to a path
  that will predictably disappear. **Nothing warns at install time.**
- `ADVANCED_PLANNING_ROOT` is unset, so nothing was overriding this — it is the
  default behaviour of the installer.
- The mechanism is `AP_SOURCE_ROOT="$REPO_ROOT"`, replicated verbatim across **six**
  installer files (`setup/{claude-code,codex,opencode}/install.{sh,ps1}`). A project
  install points at the checkout it was installed from, by design; the hazard is
  installing from a checkout that is itself disposable.
- **No real project on this machine is affected.** A bounded sweep of `~/Coding` and
  `~/.herdr/worktrees` finds `runtime.json` only in two scratch install dirs inside
  the `loop-004-codex` worktree — a worker's own test artefacts. The control for that
  sweep found all 4 fixture copies, so the negative is real and not vacuous. This is
  latent, not live.

**A correction to my own finding, measured after I first wrote it.** I had written
that a removed checkout makes installs *"silently break"*. **That is wrong, and the
truth is to the runtime's credit.** Repointing a copied fixture's `source_root` at a
nonexistent path gives, on both `--check` and a real verb:

```
advanced-planning: …/runtime.json records source_root = 'C:/nonexistent/…', but there
is no platforms\python\__init__.py under it - the checkout has most likely been moved,
renamed or deleted
advanced-planning: fix: re-run the installer …, or run /sync-install, or edit …
```

Exit `3`. It names the file, the key, and three fixes. That is precisely the loud,
actionable failure this phase has been demanding everywhere else — so the defect is
narrower than I first stated: not silent breakage, but an install-time binding to a
disposable checkout with no warning **at install time**.

This also *rehabilitates* the runtime: `state_validate external-task-envelope` works
fine from the fixture, resolving the schema and reporting 15 missing required
properties on a deliberately-wrong document — while `no-such-schema` is rejected by
name. Both directions checked. The verb is real; it is the **binding** that is wrong.

## A third finding: the decomposition assigns a skill that is not installed

All five todos in the generated `loops.md` carry `skill: "using-superpowers"`.
The fixture installs eight skills and that is not one of them. The host invented a
plausible skill name rather than choosing from what the adapter had put on disk —
and nothing in the flow would have caught it.

## The codex half — stage 1, and the findings it replicates

codex keeps a per-session rollout at
`~/.codex/sessions/2026/08/29/rollout-...-01a04c3e-....jsonl` (70 records). That
file, not the pane and not the host's summary, is the evidence below.

### The invocation manifest, from the rollout

| Field | Value |
|---|---|
| model / effort | **`gpt-5.6-terra` / `medium`** (`turn_context`, the only such record) |
| cli_version | `0.150.1`, originator `codex-tui` |
| sandbox | `workspace-write`, `network_access: false`, write confined to the fixture |
| approval_policy | `on-request` |
| tokens | 248,215 in / 4,314 out (816 reasoning) |
| **service_tier** | **absent from `turn_context`** — consistent with `features.fast_mode = false` |

### Stage 1: the gate held, proved from disk

Against `snap-fx-codex-before.txt` (27 rows): **1 added**
(`.advanced-plans/phases/phase-1/plan.md`), **0 removed**, **0 modified**, over
**27 common paths actually compared**. `state/` empty, no `loop-ready.json`, no
`history.jsonl`. The check was proven able to fail in the same form: a planted
line in `README.md` produced `README.md a5759e3ddffd -> a02f9bd15d71`, and the
file was restored to its recorded sha `a5759e3ddffd`.

The plan carries the gate in its *content* too, not merely on disk — its final
section reads *"Not decomposed. This section remains intentionally deferred
pending `APPROVE phase-1`."*

### Finding 1 replicates on a second, independent host

| | opencode stage 1 | codex stage 1 |
|---|---|---|
| tool calls | `bash` ×8, `read` ×1, `write` ×1 | `exec` ×8 (7 shell + 1 `apply_patch`) |
| **`ap.py` invocations** | **0** | **0** |
| `ap.py` existence tests | 1 (`Test-Path`) | 1 (`Test-Path`) |

Two hosts, two adapters, two vendors, same result: **the `phase` verb never
touches the runtime.** It is a property of the skill, not of a host.

The count was taken from the extracted `cmd` fields only, and the extractor was
checked both ways: a planted `python .advanced-plans/bin/ap.py state_validate x`
raises the count to 1. This matters, because the single `ap.py` *mention* in the
codex transcript sits in a `;`-joined line
(`python --version; Test-Path -LiteralPath .advanced-plans/bin/ap.py; ...`) —
a naive "contains python and ap.py" test scores it as an invocation. That is
defect instance 7 exactly; splitting on `;` before testing is what avoids it.

### Finding 2 generalises: *both* hosts run PowerShell on Windows

All 7 codex shell commands are PowerShell — `Get-Content -Raw -LiteralPath`,
`Test-Path -LiteralPath`, `New-Item -ItemType Directory -Force`,
`Get-ChildItem -Force | Select-Object -ExpandProperty`. As with opencode, exactly
one fragment (`python --version`) is valid POSIX `sh`, and it is embedded in a
`;`-joined PowerShell line.

So this is not "opencode's `bash` tool is misnamed". **On Windows, neither host
executes POSIX shell**, and any skill, envelope or contract that prescribes it
will not run as written on either. Nothing in either adapter says so.

### A new finding: the host misreported its own model

codex was asked for three identity facts. It correctly declined two — the launch
command line (*"cannot determine from the available environment"*) and the
reasoning effort. Then it **asserted the third and got it wrong**:

> *"Model: GPT-5.6 Sol."*

Its own `turn_context` records `gpt-5.6-terra`, effort `medium`; it was launched
`codex.cmd -m gpt-5.6-terra -c model_reasoning_effort=medium`; and the pane status
line read `gpt-5.6-terra med…`. Three independent channels against one self-report.

This is worth separating from the disclosure pattern recorded elsewhere in this
programme. A host that carefully declines what it cannot observe can still state a
*wrong* fact confidently about itself — because **a self-report is a string the
model produced, not a fact it read.** That is this phase's defect class, appearing
in the one place there is no filesystem to check against. It is also direct support
for the standing rule that out-of-band evidence beats asking a worker what it is:
here the rollout file is that evidence, and it is better than `argv`, which a
`pane run` launch does not populate usefully.

## The quota finding — codex *does* expose usage, and it is nearly exhausted

Every `token_count` event in the rollout carries a `rate_limits` object. In this
session, all **9 of 9** carried one, identical:

```json
{"primary": {"used_percent": 98.0, "window_minutes": 10080,
             "resets_at": 1788452855}, "secondary": null}
```

`window_minutes: 10080` is seven days; `resets_at` is **2026-09-03 16:27 UTC**.
It is not a one-off — reading the last value from each of the eight most recent
rollouts gives a monotone series across two days, every one naming the same reset:

| session (local mtime) | model / effort | `used_percent` |
|---|---|---|
| 08-28 14:07 | terra / medium | 85 |
| 08-28 14:09 | terra / medium | 86 |
| 08-28 15:00 | **sol / xhigh** | **94** |
| 08-28 16:14 | terra / medium | 95 |
| 08-28 17:00 | luna / medium | 95 |
| 08-28 17:03 | **sol / xhigh** | **97** |
| 08-28 20:02 | sol / high | 98 |
| 08-29 07:41 | terra / medium | **98** |

**Two consequences.**

1. **CLAUDE.md's "No CLI in this fleet exposes usage or quota" is too strong.** It
   is right that no *subcommand* reports it — `codex --help` has no usage verb.
   But the number is on disk, in a documented per-session file, updated every
   turn. Quota-aware routing for codex can be *proactive*, not merely reactive to
   rate-limit errors. The claim should be narrowed to the other CLIs.
2. **codex is at 98% of its weekly limit with five days to reset.** The pane
   confirms it independently: after finishing stage 1 it painted *"Approaching
   rate … Switch to gpt-5…"* with a three-option menu.

The value is account-wide at the moment of writing, so the deltas above are *not*
attributable solely to the session that recorded them — other panes ran in between.
What is attributable is the shape: the two `sol`/`xhigh` sessions bracket the
largest single jumps (86→94 and 95→97). That is consistent with, but does not by
itself prove, xhigh Sol being the expensive call.

### And herdr reports that pane as `done`, not `blocked`

`agent list` gives `fxcx` `agent_status: "done"`, seq 1011, while the pane is
sitting on that three-option menu awaiting a keypress. The *task* did complete —
so `done` is not a lie — but **a follow-up prompt sent now would be consumed by the
menu, not by codex.** CLAUDE.md records lagging/selective `blocked` detection for
cursor and correct two-channel reporting for claude; it says nothing about this
shape on codex, where a system-initiated modal appears *after* a completed turn.
Read the pane before dispatching to a codex agent, exactly as the cursor rule says.

## Honesty note — the defect class, sixth and seventh instances, both mine

This phase's recurring defect is *a check whose subject is a string it built rather
than a fact it read*. It appeared twice more today, in my own controller work:

1. **The snapshot diff.** I compared a `sha256[:12] + path` snapshot against a fresh
   `md5sum` listing using `cut -c35-` — two different hash widths and a different
   column offset. Every path was mangled; the "modified" comparison joined on nothing
   and reported **`0 modified` over 0 rows compared**. The vacuity guard I had added
   after the last instance is what caught it, by printing `paths compared: 0`.
2. **`grep -c 'python .*ap\.py'`** returned `1` and I nearly recorded "ap.py was
   invoked once". The match was **envelope prose in the transcript**, not a command.
   Deciding it from the extracted `command` fields alone gives the true answer: **0**.

A third near-miss was caught by running rather than grepping: I had `state_validate`
down as absent from `ap.py` on the strength of one `grep` over 448 lines. Executing
it showed the verb works. **Do not conclude a capability is missing from a grep.**

The rule holds and keeps earning its place: run the check in both directions, require
it to change, and print the row count so a vacuous pass cannot masquerade as a clean one.

### A retraction, before it reached the record

I was drafting the envelope finding as *the host invented plausible git metadata
rather than reporting that it could not be resolved*. **That is the opposite of
what happened.** The host ran all three git probes, tabulated their exit-128
failures, named the placeholders it had used and explained why validation passed
anyway. It reported the impossibility and then proceeded with disclosed
placeholders — which is the correct behaviour, and it is the framing above.

The near-miss is worth recording because of where it came from: I had the finding
before I had read the host's own words for it, and the finding *sounded* better
with a culprit. Note the symmetry with the codex model misreport in the same loop —
disclosure and manufacture both occurred today, in different hosts, and only
reading the underlying record distinguishes them.

### An environment trap that produced two identical failures

The Bash tool's **quoted** heredoc (`python - <<'PY'`) collapses `\\` to `\` before
Python sees it: `s = "a\\b"` arrives as `"a\b"` and prints `len: 2`. This broke the
same extraction regex twice with a misleading `re.error: unterminated character
set`, because `[^"\\]` became `[^"\]`. A Windows path in a heredoc'd string fails
earlier still, at compile time, with `truncated \UXXXXXXXX escape`. Both counts
above were therefore taken with **no regex at all** — `json.JSONDecoder().raw_decode`
for extraction and `str.split(';')` for the segment test.

## Dialogs — all operator-cleared, none answered by a worker or by me

| Host | Pane | Dialog | Outcome |
|---|---|---|---|
| opencode `fxoc` | `w2:p1A` | *Access external directory* `…\loop-004-cigate\core\state` | operator cleared; stage 2 completed |
| codex `fxcx` | `w2:p1B` | *Do you trust the contents of this directory?* | operator cleared; stage 1 completed |
| codex `fxcx` | `w2:p1B` | *Approaching rate … Switch to gpt-5…* (3 options) | **open — blocks stage 2** |

`--wait` returned exit 0 on the opencode prompt **while the agent sat at the
dialog** — the documented returns-on-`blocked` trap, and a reminder that a
background task's exit status is not evidence of completion. The third dialog is
worse in kind: `agent_status` reads `done`, not `blocked`, so nothing but reading
the pane reveals it.

## Carried

- **CLAUDE.md correction, now measured.** The note saying codex *"does not gate on
  directory trust at all here"* is **wrong**. `~/.codex/config.toml` holds a
  `[projects]` trust store with **29 entries, every one `trust_level = "trusted"`**;
  `fx-codex` is absent from it and codex is showing the trust dialog. The earlier
  probe that concluded otherwise almost certainly matched the *"Ask Codex"* splash
  before the dialog painted — the same unsound readiness gate that invalidated
  today's isolation experiment.
- **`herdr pane wait-output --regex "Ask Codex"` is not a readiness gate for codex.**
  The prompt paints first and the dialog replaces it. Use `agent_status`.
- Pane scrollback caps around 38 lines on these panes; `--source visible|recent|
  recent-unwrapped|detection` all returned the same 38. The host's own session
  database is the durable record, not the terminal.
- Four codex probe panes (`w2:p1C`–`w2:p1F`) were created for the invalidated
  isolation experiment and have been closed.
- The `using-superpowers` assignment above deserves a check in the real flow.
- **codex stage 2 was not run, by decision.** Two things it alone would have
  settled remain open: whether codex *also* invents a skill name the way opencode
  did (`using-superpowers`), and whether its envelope differs from opencode's.
  Neither is load-bearing for any conclusion above. If it is ever worth closing,
  the fixture is intact and the quota resets 2026-09-03 16:27 UTC.
- **The `w2:p1B` pane is still parked on the rate-limit modal.** It was not
  answered, per the rule that dialogs are the operator's.
- **CLAUDE.md, two corrections earned here.** (a) *"No CLI in this fleet exposes
  usage or quota"* — narrow it to exclude codex, whose rollout files carry
  `rate_limits` per turn; (b) add the `done`-over-a-modal shape to the pane-reading
  rule, which currently names only cursor.
- The `phase`-verb finding is now replicated on two hosts, so it is a property of
  the skill. Worth a permanent test rather than another fixture run.
- The envelope schema polices shape, not reality. A semantic check — *does
  `repository` resolve to a git repo, does `base_sha` exist in it* — is the obvious
  follow-on, and would have caught a forty-zero SHA.
