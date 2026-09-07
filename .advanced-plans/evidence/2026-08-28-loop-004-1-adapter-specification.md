<!--
Controller provenance block. Everything below the horizontal rule is the
specifier's output verbatim, as produced by the run described here. Nothing in
it has been edited, reordered or abridged.
-->

# loop-004-1 — the Codex and OpenCode adapter specification (verbatim)

**Todo:** `loop-004-1` (phase-6, ralph-loop-004) — the first of five.
**Produced by:** `codex exec`, model `gpt-5.6-sol`, reasoning effort `xhigh`, sandbox
`read-only`, approval `never`. Session `01a048ac-0794-7582-92b2-cfd087d728e0`, 450,647 tokens.
**Command:**

```
codex exec -m gpt-5.6-sol -c model_reasoning_effort=xhigh -s read-only --skip-git-repo-check - \
  < loop-004-1-envelope.md
```

**cwd:** `~/.herdr/worktrees/advanced-planning/loop-003-hostneutral` (branch `loop-003-hostneutral`,
HEAD `fbc559b`). Read-only: the tree was clean before and after, and the sandbox forbade writes.

**Why a different provider from the builders.** loops 004-2 and 004-3 are assigned to `opencode`.
A specification written by the same provider that builds against it cannot catch the case where the
builder's reading of the contract is the thing that is wrong. Phase 5 established the pattern.

**Provenance check.** `codex exec` prints its final message twice — once inline in the transcript
and again as a trailing block after the token count. Both copies were extracted separately
(raw lines 18445-18954 and 18957-19466) and compared: **identical**, 510 lines each. What follows
is that text.

The controller's verification of its claims is a separate file:
`2026-08-28-loop-004-1-specification-verified.md`. Read that before building from this.

---

# Codex and OpenCode Advanced Planning Adapter Specification

## Status and scope

This specification governs the adapters to be added under `platforms/codex/`, `setup/codex/`, `platforms/opencode/`, and `setup/opencode/`. It also defines the one shared skill payload both adapters install.

The adapters wrap the existing core. They must not modify `core/schemas/`, `core/skills/`, `core/agents/`, or `core/state/`; the published adapter contract explicitly makes those canonical and immutable from an adapter’s perspective (`docs/adapting-to-new-platforms.md:296-305`).

Normative terms `MUST`, `MUST NOT`, `SHOULD`, and `MAY` are used deliberately.

## Sources actually read

The repository pass was performed in the requested order:

1. `docs/adapting-to-new-platforms.md` was read in full, including all six contracts, the shared-runtime contract, the Minimum Adapter Checklist, the Cowork worked example, and the “What Not to Change” section (`docs/adapting-to-new-platforms.md:9-182`, `docs/adapting-to-new-platforms.md:186-247`, `docs/adapting-to-new-platforms.md:296-305`).

2. `platforms/claude-code/` and `setup/claude-code/` were inventoried. The platform installer, README, guidance template, settings and hooks were read; the phase, loop, gate, resume-related and compaction command files were read where they define routing, state, spawning, checkpoint, and runtime behavior. The setup README and shell installer were read in full; the corresponding PowerShell installer and uninstallers were inspected through their scaffold, runtime, global-home, rewrite, skills, and removal sections. The runtime placement outside the scaffold guard is visible at `setup/claude-code/install.sh:305-416`; global rewriting and home resolution are at `setup/claude-code/install.sh:115-200` and `setup/claude-code/install.sh:203-267`.

3. All files in `platforms/cowork/` and `setup/cowork/` were read. Cowork routes natural-language intents through one skill (`platforms/cowork/SKILL.md:21-46`), passes complete role prompts through its Agent tool (`platforms/cowork/SKILL.md:98-153`), uses separate `skills/` and state paths (`platforms/cowork/SKILL.md:265-297`), and packages a mounted copy of the source and adapter (`setup/cowork/create-zip.sh:1-17`, `setup/cowork/create-zip.sh:50-69`).

4. `platforms/python/ap_launcher.py` was read in full. The related runtime resolver in `install_audit.py`, state I/O in `state_manager.py`, the Python README, launcher tests, and the zero-dependency schema validator presently located under tests were also inspected. The launcher’s resolution order and diagnostics are defined at `platforms/python/ap_launcher.py:39-66`, `platforms/python/ap_launcher.py:206-246`, and `platforms/python/ap_launcher.py:269-390`; module dispatch is at `platforms/python/ap_launcher.py:393-448`.

5. `docs/path-conventions.md` and `platforms/python/path_audit.py` were read in full. The canonical data layout is defined at `docs/path-conventions.md:65-117`; host-neutrality is defined at `docs/path-conventions.md:145-180`.

Supplemental reads included `core/agents/orchestrator.md`, `core/agents/worker.md`, `core/agents/README.md`, the gate-review prompts, all six state schemas, the core-skill inventory, and the host-incompatible companion and permission skills. Current official Codex and OpenCode documentation was checked for host behavior: [Codex skills](https://developers.openai.com/codex/skills), [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Codex subagents](https://developers.openai.com/codex/subagents), [OpenCode skills](https://opencode.ai/docs/skills), [OpenCode rules](https://opencode.ai/docs/rules), and [OpenCode agents](https://opencode.ai/docs/agents/).

## Shared adapter structure

The implementations MUST produce this logical layout:

```text
platforms/
├── shared/
│   └── agent-skills/
│       └── advanced-planning/
│           ├── SKILL.md
│           └── references/
│               ├── orchestrator-prompt.md
│               ├── worker-prompt.md
│               ├── gate-reviewer-prompt.md
│               └── manual-review.md
├── codex/
│   └── README.md
└── opencode/
    └── README.md

setup/
├── codex/
│   ├── install.sh
│   └── install.ps1
└── opencode/
    ├── install.sh
    └── install.ps1
```

`platforms/shared/agent-skills/advanced-planning/` is the sole source of the routing skill. Loop 004-2 owns creation of that shared payload. Loop 004-3 consumes and tests it but MUST NOT create a divergent OpenCode copy.

Each project installer places the same payload at:

```text
.agents/skills/advanced-planning/SKILL.md
```

It also installs the approved core planning skills as byte-identical copies or links under:

```text
.agents/skills/<name>/SKILL.md
```

The approved core-skill allowlist is:

- `phase-plan-creator`
- `ralph-loop-planner`
- `plan-todos`
- `plan-skill-identification`
- `plan-subagent-identification`
- `progress-report`
- `schema-design`

`companion-detection` is excluded because it advertises the deprecated review companion (`core/skills/companion-detection/SKILL.md:2-3`, `core/skills/companion-detection/SKILL.md:40-53`). `permission-config` is excluded because it is Claude-specific; the path audit currently carries a named retirement exception for precisely that reason (`platforms/python/path_audit.py:118-130`). Exclusion is not a fork.

## Contract 1 — Entry point

The published contract requires a defined and tested mapping from user triggers into the planning cycle (`docs/adapting-to-new-platforms.md:13-23`).

Both hosts use `advanced-planning` as a routing skill. Neither adapter creates Claude-style command files. Codex MUST create no custom prompt or command files under `.codex/`. OpenCode MUST create no `.opencode/commands/` entries; although OpenCode supports custom slash commands, the supplied host contract selects skills as the entry model and restricts `opencode.json` to plugins, permissions, or extra instructions.

### Exact user triggers

| Action | Codex | OpenCode | Difference and reason |
|---|---|---|---|
| Phase | `$advanced-planning phase <goal>` | `Use the advanced-planning skill: phase <goal>` | Codex documents explicit `$skill` mentions. Stable OpenCode documentation exposes skills through the model’s native `skill` tool but does not define an equivalent guaranteed user-side `$skill` syntax. |
| Loop | `$advanced-planning loop next` | `Use the advanced-planning skill: loop next` | Same semantic action; different host invocation syntax. |
| Gate | `$advanced-planning gate current` | `Use the advanced-planning skill: gate current` | Same semantic action; different host invocation syntax. |
| Resume | `$advanced-planning resume` | `Use the advanced-planning skill: resume` | Same recovery state machine; different host invocation syntax. |
| Compact | `$advanced-planning compact current` | `Use the advanced-planning skill: compact current` | Both compact AAW artefacts. Host conversation compaction remains a separate, explicit host action. |

Codex supports explicit skill mention through `$` and discovers repository skills under `.agents/skills` ([Codex skills](https://developers.openai.com/codex/skills)). OpenCode discovers `.agents/skills/<name>/SKILL.md` and loads a selected skill through `skill({name: "advanced-planning"})` ([OpenCode skills](https://opencode.ai/docs/skills)).

For OpenCode, each documented prompt above is successful only after the host visibly loads `advanced-planning` through its skill mechanism. If the skill is hidden or denied, the action MUST stop with `advanced-planning skill not loaded`; it MUST NOT imitate the workflow from general model knowledge.

### Action semantics

- `phase <goal>` creates the next `.advanced-plans/phases/phase-N/plan.md`, runs the manual human review gate, and only after approval runs loop decomposition, todo population, skill assignment, and agent assignment. It updates `.advanced-plans/PLANNING.md`.

- `loop next` performs exactly one orchestrator → worker cycle. Auto-chaining requires an explicit additional argument such as `loop next --auto`; it is not the default.

- `gate current` runs independent gate reviewers against the current completed phase, validates every verdict, and either closes the phase or creates validated retry context.

- `resume` validates existing state before deciding what to do:
  - an outstanding human review is reprinted;
  - a matching valid `loop-complete.json` is finalized without rerunning the worker;
  - a valid `loop-ready.json` without matching completion resumes that assignment;
  - dirty or contradictory recovery state stops for explicit user/controller direction;
  - invalid JSON is never overwritten automatically.

- `compact current` generates and validates the phase handoff and cold/hot compaction artefacts. Existing compaction code establishes that artefact preparation cannot self-invoke host context compaction and must require explicit consent (`platforms/claude-code/commands/phase-compact.md:432-464`, `platforms/claude-code/commands/phase-compact.md:521-524`). Accordingly, neither adapter may claim that the host conversation was compacted. If the host exposes a native context-compaction command, the adapter prints it for the user; otherwise it prints “start a new session and run the resume trigger.”

The router MUST reject ambiguous or unknown action words rather than choosing a nearby destructive action.

## Contract 2 — Agent spawning

The main thread owns all spawning; orchestrator and worker must never spawn one another (`docs/adapting-to-new-platforms.md:25-37`). The core protocol repeats this ownership rule (`core/agents/orchestrator.md:125-150`, `core/agents/worker.md:241-251`).

| Question | Codex | OpenCode | Difference and reason |
|---|---|---|---|
| Primary mechanism | Native Codex subagent workflow | Native OpenCode Task/subagent workflow | Both have native delegation, but neither uses Claude Code’s Agent syntax or Claude model names. |
| Orchestrator role | A fresh native subagent spawned by the main Codex thread | A fresh native subagent invoked by the primary OpenCode agent | Host-native mechanism differs. |
| Worker role | A second fresh native subagent, started only after valid `loop-ready.json` | A second fresh native subagent, started only after valid `loop-ready.json` | Same sequencing contract. |
| Prompt delivery | Main thread reads the complete shared prompt reference, appends project root, state path, loop identity, opening checkpoint SHA and prior handoff, and sends the resulting full text as the delegated task | Primary agent passes the same complete text as the Task payload | A path alone is not an acceptable prompt. |
| External fallback | Herdr/AAW task | Herdr/AAW task | Same fallback contract. |

Current Codex releases support subagents and allow `AGENTS.md` or skill instructions to request delegation; Codex coordinates spawning, waiting and collection ([Codex subagents](https://developers.openai.com/codex/subagents)). OpenCode provides primary and subagent roles and invokes subagents through its Task mechanism ([OpenCode agents](https://opencode.ai/docs/agents/)).

The adapter MUST capability-check native delegation before opening a loop. If native delegation is unavailable or disabled, it MAY use an external task only if a Herdr/AAW integration is actually available. That fallback consists of:

1. constructing and validating an immutable `external-task-envelope`;
2. setting `provider` to `codex` or `opencode` and `manager` to `herdr`;
3. including the complete role prompt and task context in the dispatched task;
4. forbidding the external worker from modifying `.advanced-plans/state/`;
5. collecting and validating `collected-evidence` before the controller updates state.

The envelope requires `.advanced-plans/state/` in `forbidden_paths` (`core/state/external-task-envelope.schema.json:94-103`); collected evidence is explicitly controller-computed and must be validated before state advances (`core/state/collected-evidence.schema.json:3-6`, `core/state/collected-evidence.schema.json:47-50`).

If neither native delegation nor a real external integration exists, Contract 2 is unsatisfied and `loop next` and `gate current` MUST stop. The adapter must not execute both logical roles in one context and call that delegation.

Neither portable adapter can guarantee Claude’s “Sonnet-tier orchestrator / Haiku-tier worker” model distinction without host-specific agent definitions. Codex custom agent prompt files are excluded by the supplied host contract, and OpenCode agent configuration would create another host-private prompt layer. Native runs therefore use the model selected by host/project policy. If strict per-role model selection is required, the external Herdr/AAW route is mandatory. This affects model-tier optimization, not sequencing or state correctness.

## Contract 3 — State directory

| Codex | OpenCode | Difference |
|---|---|---|
| `.advanced-plans/state/` | `.advanced-plans/state/` | None. |

Both orchestrator and worker prompts, the router, validation calls and recovery logic MUST use:

```text
.advanced-plans/state/loop-ready.json
.advanced-plans/state/loop-complete.json
.advanced-plans/state/history.jsonl
.advanced-plans/state/archive/
```

Gate verdicts remain under `.advanced-plans/gate-verdicts/`, and phase retry context remains under its canonical phase directory (`docs/path-conventions.md:79-93`, `docs/path-conventions.md:98-115`).

The reason this is not a host-private directory is operational, not cosmetic: Codex, OpenCode, external workers, future hosts and resumed sessions must observe one state bus. A `.codex/` or `.opencode/` state directory would split the current loop, history and recovery point into competing copies, making cross-host resume and controller validation unsafe. The runtime contract uses the same reasoning for its shared manifest (`docs/adapting-to-new-platforms.md:99-104`).

No `STATE_DIR` override may silently redirect installed operation to a host directory.

## Contract 4 — Skills directory

| Codex | OpenCode | Difference |
|---|---|---|
| `.agents/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | None in project layout; only the host’s discovery implementation differs. |

Codex registers these skills by scanning `.agents/skills` from the current directory to the repository root; it does not require a registry file. Duplicate names are not merged ([Codex skills](https://developers.openai.com/codex/skills)).

OpenCode registers them by scanning `.agents/skills` and advertising permitted entries through the native skill tool ([OpenCode skills](https://opencode.ai/docs/skills)). No `opencode.json` entry is required for normal discovery.

The worker MUST load the skill named by each todo immediately before that todo, verify the outcome, then discard its task-specific influence before the next todo. Cowork’s worker demonstrates this per-todo protocol but uses the wrong path for these hosts (`platforms/cowork/agents/worker-prompt.md:41-100`). Codex and OpenCode must use `.agents/skills/`, never Cowork’s `skills/`.

### Collision decision

When both adapters are installed in one project, they share one copy. They do not overwrite independent Codex and OpenCode variants.

The rules are:

1. The routing skill installed by both adapters is sourced from the same shared directory and MUST be byte-identical.
2. Each installed core skill MUST be byte-identical to its canonical `core/skills/<name>/` source.
3. If the destination already has identical content, installation reports `shared; unchanged`.
4. If any destination file differs, installation fails with both digests and the conflicting path. It MUST NOT overwrite.
5. Project installation also checks ancestor and global skill locations for a divergent `advanced-planning` name. An identical duplicate may be tolerated; a divergent duplicate is an activation conflict and must be reported.
6. Uninstall must not remove the shared copy while the other adapter remains registered. Shared ownership metadata must be host-neutral and may live under `.advanced-plans/`, not under a host-private state directory.

For project installs, digest comparison is raw bytes. For global installs, the shared router’s launcher path is necessarily rewritten; comparison therefore uses both the raw installed digest and an `install_audit`-style normalized digest in which the absolute launcher path is converted back to the canonical relative form.

## Contract 5 — Checkpoints

Both adapters use Git checkpoint SHAs. Neither copies Cowork’s snapshot mechanism, which exists specifically for environments without Git (`platforms/cowork/checkpoint.sh:1-12`).

The worker never commits. Although earlier portions of the core worker document still contain commit and rollback instructions (`core/agents/worker.md:34-37`, `core/agents/worker.md:176-177`, `core/agents/worker.md:231-235`), its later Hard Contract explicitly assigns all Git sequencing to the main thread (`core/agents/worker.md:241-251`). The adapter wrapper MUST make the Hard Contract controlling and MUST NOT edit the core document.

| Checkpoint | Codex | OpenCode |
|---|---|---|
| Opening | External Herdr/AAW controller records or creates the opening commit and returns its full SHA before Codex spawns the orchestrator | Primary OpenCode session records HEAD or commits approved pending changes before spawning |
| Closing | Codex returns a structured checkpoint request; the external controller validates the diff, commits it outside the Codex sandbox, and returns the full closing SHA | Primary OpenCode session validates the worker result and commits approved paths after valid completion |
| Worker | Receives opening SHA as immutable context; never stages, commits or resets | Same |
| Failure | Stop until the controller supplies the checkpoint; never report loop completion without it | Fall back to external controller if available; otherwise stop |

The checked-out `.git` file points to `C:/Users/mharvey2/Coding/advanced-planning/.git/worktrees/loop-003-hostneutral`, outside this linked worktree (`.git:1`). Codex subagents inherit the parent sandbox ([Codex subagents](https://developers.openai.com/codex/subagents)). Therefore neither the Codex main thread nor its subagents may be instructed to run `git commit` here. The committing actor is the Herdr/AAW controller that created and manages the linked worktree.

A clean opening tree does not require an empty commit: the existing full HEAD SHA is the opening checkpoint. A loop that legitimately makes no changes may retain the same SHA, but if its completion record claims changes, the mismatch is a failure. Closing commits must stage only the controller-approved path set, not unrelated user changes.

## Contract 6 — Shared Python runtime

This contract is mandatory for both adapters. Installed projects do not contain `platforms/python/`, so bare `python -m platforms.python...` or source-relative `python platforms/python/...` calls work only by accident from the source checkout (`docs/adapting-to-new-platforms.md:77-85`).

| Requirement | Codex | OpenCode | Difference |
|---|---|---|---|
| Project manifest | `.advanced-plans/runtime.json` | `.advanced-plans/runtime.json` | None |
| Project launcher | `.advanced-plans/bin/ap.py` copied from `platforms/python/ap_launcher.py` | Same | None |
| Global manifest and launcher | `<home>/.advanced-plans/runtime.json`, `<home>/.advanced-plans/bin/ap.py` | Same | None |
| Global skill location | `<home>/.agents/skills/` | `<home>/.agents/skills/` | None |
| Module call | `python ".advanced-plans/bin/ap.py" <module> ...` | Same | None |
| Inline bootstrap | `runpy.run_path(r'.advanced-plans/bin/ap.py')['bootstrap']()` | Same | None |

Every installer path MUST:

1. Copy `platforms/python/ap_launcher.py` to `.advanced-plans/bin/ap.py`.
2. Write `.advanced-plans/runtime.json` with an absolute, interpreter-readable `source_root`.
3. Perform both operations outside any “`.advanced-plans` already exists; skip scaffold” guard.
4. Refresh both files on every non-dry-run install or upgrade.
5. Preserve existing planning data.
6. Invoke every shared Python module through the launcher.
7. Run project-relative launcher calls from the project root.
8. Preserve and propagate launcher exit code `3`.
9. Support `ADVANCED_PLANNING_ROOT` as the explicit override.
10. Under MSYS/Git Bash, normalize `source_root` and absolute launcher paths with `cygpath -m`.

These requirements are the published contract (`docs/adapting-to-new-platforms.md:87-110`, `docs/adapting-to-new-platforms.md:137-157`) and are implemented in the existing installer outside its scaffold guard (`setup/claude-code/install.sh:305-416`).

### `--global` / `-Global`

Each global installer MUST perform all three documented obligations:

1. write `<home>/.advanced-plans/runtime.json` and copy `<home>/.advanced-plans/bin/ap.py`;
2. rewrite every executable launcher callsite in the globally copied routing skill and references to the absolute launcher path;
3. resolve `<home>` from `USERPROFILE` before `HOME`.

The contract states all three at `docs/adapting-to-new-platforms.md:112-125`. The shell reference implementation distinguishes filesystem and native-Python path forms and gives `USERPROFILE` precedence (`setup/claude-code/install.sh:115-200`).

Because these adapters have no command files, “commands it copies” means every copied skill or support file containing an executable launcher callsite. Omitting the rewrite on the ground that there are no slash commands would reproduce the original installation defect.

Source callsites must retain the exact substitutable forms:

```text
python ".advanced-plans/bin/ap.py"
runpy.run_path(r'.advanced-plans/bin/ap.py')
```

Only the path is rewritten globally; quotes and raw prefixes are already present (`docs/adapting-to-new-platforms.md:127-135`).

Project and global runtime records are deliberately shared. A later explicit install refreshes the shared `source_root`; it does not create per-host manifests. Skill payload mismatches remain install conflicts.

## §7.3 requirement 1 — Discovery

| Codex | OpenCode |
|---|---|
| Install the shared router and approved core skills into `.agents/skills/`. Codex discovers them automatically; restart the session if a fresh installation is not visible. | Install the same files. OpenCode discovers and advertises them through its skill tool. If an existing permission rule denies the skill, report the exact rule and stop. |

Both installers add an idempotent fenced section to project-root `AGENTS.md`, preserving all user content and rejecting malformed or duplicate fences. Codex reads project guidance from root toward the current directory ([Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)); OpenCode uses project `AGENTS.md` as its native rules file ([OpenCode rules](https://opencode.ai/docs/rules)).

Use separate fence identifiers:

```text
<!-- advanced-planning:codex:start -->
...
<!-- advanced-planning:codex:end -->
```

```text
<!-- advanced-planning:opencode:start -->
...
<!-- advanced-planning:opencode:end -->
```

Both may coexist.

Codex MUST install no `.codex/` prompt, command, agent, state or skill copy. OpenCode SHOULD create no `.opencode/` content by default. It MAY merge `opencode.json` only when an actual plugin, permission exception, or extra-instruction setting is required; it must preserve existing configuration and must not place planning state or duplicate skills there.

## §7.3 requirement 2 — Invocation

The five exact triggers in Contract 1 are the public API. Internally, both route to the same five verbs:

```text
phase
loop
gate
resume
compact
```

The router MUST map these verbs directly, not by calling Claude command files. It MUST use `.advanced-plans/` paths and the shared launcher, and MUST preserve the current phase/loop identity across host changes.

OpenCode’s natural-language trigger is an honest limitation: stable documentation does not expose a Codex-like direct `$skill` mention. The adapter compensates by requiring observable native skill loading, not by creating an undeclared slash-command layer.

## §7.3 requirement 3 — Delegation

Both hosts primarily use their native subagents, with a validated external Herdr/AAW task as fallback.

The main thread is always the coordinator:

```text
main/controller
├── orchestrator
└── worker
```

The orchestrator and worker run sequentially and never nest. Gate reviewers are fresh and independent; they must not read one another’s verdict files. Prompt delivery always includes the full role prompt, not merely a filesystem path.

External workers do not write controller-owned state. They return evidence; the controller validates it and performs state transitions. The external schemas already recognize both providers (`core/state/external-task-envelope.schema.json:54-62`, `core/state/collected-evidence.schema.json:27-43`).

## §7.3 requirement 4 — State I/O

Both adapters must validate the same six canonical schemas:

- `core/state/loop-ready.schema.json`
- `core/state/loop-complete.schema.json`
- `core/state/gate-verdict.schema.json`
- `core/state/gate-failure-context.schema.json`
- `core/state/external-task-envelope.schema.json`
- `core/state/collected-evidence.schema.json`

Validation occurs:

- before a producer atomically publishes JSON;
- every time a consumer reads JSON;
- before dispatching an external task;
- before advancing state from collected evidence;
- before aggregating gate verdicts;
- before accepting retry context.

The existing production `state_manager.py` only serializes, parses and performs a limited completion-status enum check; it does not validate against the core schemas (`platforms/python/state_manager.py:50-102`, `platforms/python/state_manager.py:273-281`, `platforms/python/state_manager.py:286-361`). The repository’s capable zero-dependency validator currently lives under tests and declares support for the exact schema keyword subset (`platforms/python/tests/minischema.py:1-31`).

Therefore loop 004-2 MUST add a production shared module such as `platforms/python/state_validate.py`, using only the standard library and the canonical schemas. Loop 004-3 MUST reuse it. Until that exists and is reached through `ap.py`, neither adapter may claim §7.3 State I/O compliance.

The validator’s CLI should take a schema basename and a target document, for example:

```text
python ".advanced-plans/bin/ap.py" state_validate loop-ready .advanced-plans/state/loop-ready.json
```

It must resolve the schema from the recorded source root, not expect `core/` to exist in the installed project. It must reject unknown schema keywords rather than silently ignoring them.

No adapter may copy schemas into a host-private directory or rewrite canonical document paths.

## §7.3 requirement 5 — Human gate

The default review mechanism for both hosts is manual and host-neutral.

After producing a phase plan, the adapter prints the plan and exactly this instruction:

```text
REVIEW .advanced-plans/phases/phase-N/plan.md

Reply with exactly one:
APPROVE phase-N
REVISE phase-N: <instructions>
STOP phase-N
```

Until one of those responses is received:

- loop decomposition must not begin;
- no approval event may be recorded;
- `resume` must return to the outstanding review;
- auto mode must remain stopped.

`APPROVE` continues. `REVISE` reruns phase planning with the supplied feedback and presents the revised plan again. `STOP` preserves the plan and exits.

Codex must not claim an automatic plan-review hook. OpenCode MAY use a future native review plugin only if it returns an explicit approval or rejection result; absence, failure, timeout, or ambiguous output falls back to the manual instruction. No absent hook may silently approve or skip the gate.

Plannotator is not installed, detected, recommended, or invoked by either adapter.

## Host-neutrality boundary

The adapters may name `.codex/`, `.opencode/`, native tools, and host permission syntax inside their own `platforms/` and `setup/` files. The audit’s host-specific patterns are marked `core_only=True` (`platforms/python/path_audit.py:76-110`), and it determines that scope using `root_rel.startswith("core/")` (`platforms/python/path_audit.py:312-333`).

The current default roots do not yet include `platforms/codex/` or `platforms/opencode/` at all (`platforms/python/path_audit.py:135-148`). Thus the current audit provides two distinct findings:

- host-specific text under the new platform directories is architecturally permitted;
- current CI will not automatically check even the generic path errors in those new directories unless they are explicitly included in the scan or covered by adapter tests.

The adapters MUST NOT:

- edit any file under `core/`;
- insert `.agents/`, `.codex/`, `.opencode/`, native tool names, model names, or host permission syntax into core files;
- add a new path-audit exception for their implementation;
- install a modified shadow copy of a core skill under the same skill name;
- teach a shared core skill to rewrite state into a host-private directory.

The host-neutrality audit exits `1` for unsuppressed violations (`platforms/python/path_audit.py:421-434`).

## No-fork rule

Every builder must provide two proofs:

1. `core/` remained unchanged: no diff under `core/skills`, `core/agents`, `core/state`, or `core/schemas`.
2. Every installed core skill matches its source by digest.

The digest record must include, for each file:

```text
source relative path
installed relative path
source SHA-256
installed SHA-256
match: true
```

A tree digest must also be calculated by sorting relative file paths and hashing the path-plus-file-digest sequence. Symlink or junction mode hashes the resolved content as well as recording the link target.

When a core skill contains behavior that cannot work on a host, the adapter has three permitted responses:

1. translate or override the behavior in the platform routing wrapper;
2. omit the non-planning skill from the documented allowlist and report the omission;
3. declare the affected action unsupported and stop.

It must not edit the skill, install a modified copy, or shadow it with another skill of the same name. If wrapper-level adaptation cannot preserve the core contract, the builder must raise a separate cross-platform core change request; loop 004-2 or 004-3 must not make that change.

## Required divergence from Cowork

| Area | Cowork precedent | Required Codex/OpenCode behavior | Why |
|---|---|---|---|
| Entry | Broad natural-language routing only (`platforms/cowork/SKILL.md:21-46`) | Codex uses explicit `$advanced-planning`; OpenCode uses an explicit natural-language request followed by observable skill loading | Host skill invocation differs. |
| Spawning | Claude-specific Agent tool and Sonnet/Haiku parameters (`platforms/cowork/SKILL.md:110-153`) | Native Codex subagents or OpenCode Task subagents; external Herdr fallback | Neither host implements Cowork’s Agent mechanism or Claude model names. |
| State | Separate workspace state and `planning-state.md` (`platforms/cowork/SKILL.md:265-297`) | `.advanced-plans/state/` and `.advanced-plans/PLANNING.md` | Cross-host state must remain shared. |
| Skills | `skills/<name>/SKILL.md` (`platforms/cowork/agents/worker-prompt.md:58-61`) | `.agents/skills/<name>/SKILL.md` | Required shared discovery location. |
| Checkpoints | Snapshot script (`platforms/cowork/SKILL.md:102-108`, `platforms/cowork/SKILL.md:166-169`) | Git SHA checkpoints; Codex commits through the external controller | Both new hosts operate on Git worktrees. |
| Runtime | No shared Python requirement because Cowork invokes no Python (`docs/adapting-to-new-platforms.md:186-188`) | Mandatory launcher, manifest, global rewrite and repair diagnostics | Both new adapters use shared Python modules. |
| Packaging | Self-contained mounted zip (`setup/cowork/create-zip.sh:1-17`) | Project/global installers, AGENTS guidance and discovered skills | Codex and OpenCode run in ordinary repositories. |
| Host tools | Cowork prompt names Agent and TodoWrite (`platforms/cowork/agents/worker-prompt.md:223-232`) | Host-native delegation and task tracking only | Copying those names would create dead instructions. |

Cowork is useful as a sequencing example, not as an install layout, prompt syntax, state layout, checkpoint implementation, runtime design, or model policy.

## Ambiguities resolved

1. **Meaning of “loop”:** it means execute the next pending loop, not merely generate loop stubs. Phase creation performs decomposition after human approval.

2. **OpenCode explicit invocation:** stable OpenCode documentation does not define a Codex-style direct skill mention. The exact natural-language prompt plus an observable native skill load is the contract.

3. **Shared skill collision:** both adapters share one byte-identical copy. Silent overwrite is forbidden; a mismatch is an install conflict.

4. **Shared payload ownership:** loop 004-2 creates `platforms/shared/agent-skills/advanced-planning`; loop 004-3 consumes it.

5. **Native versus external delegation:** native subagents are primary; validated Herdr/AAW dispatch is fallback. If neither exists, the action is unsupported.

6. **Role-specific model tiers:** a portable skill cannot guarantee separate host model tiers. External dispatch is required when strict per-role model selection is mandatory.

7. **Checkpoint ownership:** the worker never commits. OpenCode’s primary session normally commits; the external controller always commits for Codex linked-worktree runs.

8. **Clean checkpoint:** a clean HEAD SHA is a valid opening checkpoint; no empty commit is required.

9. **Global “command” rewrite:** because these hosts use a routing skill rather than command files, every executable callsite in the globally copied skill payload is subject to the absolute-launcher rewrite.

10. **Compact action:** the action compacts AAW artefacts. It does not claim to compact host conversation context automatically.

11. **Human gate:** manual review is the baseline, not an optional fallback that may be skipped.

12. **Core skills with incompatible content:** exclude or wrap; never edit or fork.

13. **Schema validation:** current production state I/O is insufficient. A shared production validator is a prerequisite, not an adapter-specific duplicate.

14. **Path-audit scope:** host tokens are permitted under `platforms/`, but the new directories are not presently included in default scanning.

## Minimum acceptance checklist

Both adapters are complete only when all applicable items pass:

- [ ] All five documented triggers invoke the correct action.
- [ ] Codex explicit `$advanced-planning` activation is tested.
- [ ] OpenCode visibly loads the skill before acting.
- [ ] Project `AGENTS.md` merge is idempotent and preserves user content.
- [ ] The shared routing skill is installed at `.agents/skills/advanced-planning/SKILL.md`.
- [ ] Approved core skills are installed under `.agents/skills/` with matching SHA-256 digests.
- [ ] Installing Codex then OpenCode and OpenCode then Codex leaves one identical shared skill tree.
- [ ] Divergent existing skill content causes a clear failure and no overwrite.
- [ ] Orchestrator, worker and gate prompts are self-contained when delivered.
- [ ] Orchestrator and worker never spawn each other.
- [ ] Native and external delegation paths are separately tested.
- [ ] Absence of both delegation mechanisms fails explicitly.
- [ ] Every state producer and consumer validates against the canonical core schema.
- [ ] Invalid state prevents dispatch or advancement and is not silently replaced.
- [ ] All state paths resolve to `.advanced-plans/state/`.
- [ ] Manual phase review blocks until an explicit valid response.
- [ ] No deprecated review companion behavior is installed or invoked.
- [ ] Opening and closing checkpoint SHAs are recorded.
- [ ] Codex never attempts `git commit`; controller acknowledgement is required.
- [ ] OpenCode workers never commit; only the primary session or external controller does.
- [ ] Project installers always refresh `runtime.json` and `bin/ap.py`, including when `.advanced-plans/` already exists.
- [ ] Global installers write the global runtime, rewrite all executable skill callsites, and prefer `USERPROFILE` over `HOME`.
- [ ] MSYS paths are normalized for native Python.
- [ ] A project outside the source checkout successfully reaches every Python module through the launcher.
- [ ] A moved or missing checkout produces the launcher’s repair diagnostic and exit code `3`.
- [ ] No source callsite uses bare `-m`, `python3`, `sys.path.insert(0, '.')`, or `python platforms/python/...`.
- [ ] No file under `core/` changes; before/after core digests match.
- [ ] No new path-audit exception is added.
- [ ] Each adapter README covers project setup, global setup, exact five-action quick start, shared-skill behavior, checkpoint ownership, and at least these three failures: skill not discovered, runtime source unreachable, and delegation/checkpoint unavailable.

The published Minimum Adapter Checklist independently requires tested entry points, self-contained role prompts, consistent state and skill paths, opening and closing checkpoints, runtime/global correctness, and setup plus failure documentation (`docs/adapting-to-new-platforms.md:167-182`).
