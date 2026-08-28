# loop-004-1 — what the specification claims, and what I checked

**Todo:** `loop-004-1` (phase-6, ralph-loop-004).
**Specification:** `2026-08-28-loop-004-1-adapter-specification.md` (verbatim, 510 lines, 24
sections).
**Outcome asked for:** *"Two adapters are specified against the published contract before code
exists, so neither is reverse-engineered from the Claude Code one."*

**Result:** accepted. Every repository claim I checked was correct to the line. It also produced
two findings the loop did not ask for, one of which means **loop-004-2 as written cannot build what
this specifies** — amended below.

---

## Why the citations were checked rather than read

The envelope said: *"Cite file and line for anything you assert about this repository. A claim
without a citation will be checked and, if wrong, sent back."* A citation is only worth having if
somebody follows it. This loop's whole value is that the builder does not have to re-derive the
contract — so a wrong line number here propagates into two adapters and is discovered, if at all,
in loop-004-4.

Checked controller-side, in the same worktree, at `fbc559b`:

| Claim | Cited as | Verified |
|---|---|---|
| Launcher repair diagnostic exits 3 | `platforms/python/ap_launcher.py` | `EXIT_UNREACHABLE = 3` at line 86; raised or returned at 387, 398, 407, 420, 439 |
| Global install prefers `USERPROFILE` over `HOME` | `setup/claude-code/install.sh:115-200` | `ap_home_fs()` at 129-136 tries `USERPROFILE` first, `HOME` only as fallback — with the reason in the comment above it |
| MSYS paths normalised with `cygpath -m` | same | lines 131, 152, 193, 400; `-u` for the POSIX form, `-m` for the native form Python reads |
| Runtime placement is outside the scaffold guard | `setup/claude-code/install.sh:305-416` | confirmed — this is loop-001's fix |
| Host patterns are `core_only` | `path_audit.py:76-110` | line 78: *"core_only=True means the pattern is only checked under core/ roots"*; the three host rules carry `True` |
| Core scoping is a string comparison | `path_audit.py:312-333` | line 323: `is_core_root = root_rel.startswith("core/")` |
| `platforms/codex/` is not scanned | `path_audit.py:135-148` | `DEFAULT_SCANNED_ROOTS` has seven entries, none of them the new adapter directories |
| The audit exits 1 on an unsuppressed violation | `path_audit.py:421-434` | `return 0` on clean or all-suppressed, `return 1` after printing violations |
| `permission-config` carries a named retirement exception | `path_audit.py:118-130` | verbatim, including the retirement plan |
| The doc defines six contracts | `docs/adapting-to-new-platforms.md` | `## The Six Adapter Contracts` at line 9; Contract 6 at 77; Minimum Adapter Checklist at 167; *What Not to Change* at 296 |
| Cowork satisfies contract 6 by not needing it | `:186-188` | verbatim: *"the one adapter that satisfies contract 6 by not needing it"* |
| The worker never commits | `core/agents/worker.md:241-251` | *Hard Contract (non-negotiable)*, guard (a): *"NEVER commit. The main thread owns all git sequencing."* |
| Codex cannot commit from this worktree | `.git:1` | `gitdir: C:/Users/mharvey2/Coding/advanced-planning/.git/worktrees/loop-003-hostneutral` — outside the checkout, therefore outside the sandbox |
| The envelope schema forbids state writes | `external-task-envelope.schema.json:94-103` | `contains: {const: ".advanced-plans/state/"}` — enforced by the schema, not by convention |
| Both new providers are already enumerated | `:54-62` | `enum: ["claude", "codex", "opencode", "cursor", "agy"]` |
| Six canonical schemas under `core/state/` | — | six `.schema.json` files, exactly the six named |
| Production state I/O does not validate | `state_manager.py` | grep for `schema`/`validate` returns one hit, in an unrelated docstring example. The claim is right |
| The capable validator lives under tests | `platforms/python/tests/minischema.py:1-31` | *"Supports exactly the keywords used by core/state/\*.schema.json. Raises UnsupportedKeyword for any unknown keyword"* |
| `companion-detection` advertises the deprecated companion | `SKILL.md:2-3` | its `description:` names Plannotator |
| Cowork loads skills from `skills/<name>/SKILL.md` | `platforms/cowork/agents/worker-prompt.md:58-61` | verbatim |

**Not verifiable here, and the specification is honest about which those are.** Everything it says
about how Codex and OpenCode themselves behave — `$skill` mention syntax, skill discovery order,
native subagents, `AGENTS.md` precedence — rests on upstream documentation it fetched during the
run, all six URLs cited. I did not re-fetch them. loop-004-2 and -3 must prove those on the CLIs,
which is what their checks already say: *"install into a scratch project and run a module there"*.
A specification is not evidence about a host.

## Finding 1 — the specification prescribes work at paths its own build loops forbid

This is the one that would have stopped loop-004-2 dead.

The specification answers the collision question the envelope asked — *what happens when both
adapters are installed into one project?* — with a shared payload:
`platforms/shared/agent-skills/advanced-planning/`, created once by loop-004-2 and consumed
unchanged by loop-004-3, with a digest conflict rather than a silent overwrite.

That is the right answer. It is also **not buildable under the loop as written**:

- `loop-004-2.allowed_paths` is `["platforms/codex/", "setup/codex/", "docs/"]`.
- `loop-004-3.allowed_paths` is `["platforms/opencode/", "setup/opencode/", "docs/"]`.

`platforms/shared/` is in neither. A builder obeying its `allowed_paths` — which is the whole
mechanism by which these loops are constrained — would have had to either violate them or make two
diverging copies, which is precisely the outcome the collision decision exists to prevent.

## Finding 2 — §7.3 requirement 4 cannot be satisfied by anything that currently exists

The specification checked, rather than assumed, whether production code validates state against the
canonical schemas. It does not: `state_manager.py` serialises, parses, and checks one completion
enum. The repository's real validator is `minischema.py`, a 374-line library sitting under
`platforms/python/tests/` — the one directory the AST check excludes, a defect already carried open
from an earlier loop.

So *"validate the same core JSON schemas"* is a requirement no adapter can meet by wiring itself to
existing code. The specification's conclusion is that a shared production module
(`platforms/python/state_validate.py`) is a **prerequisite**, built once and reached through
`ap.py`, and that *"until that exists and is reached through `ap.py`, neither adapter may claim
§7.3 State I/O compliance."*

`platforms/python/` is also outside both build loops' `allowed_paths`.

Note what this is: the specification found that a requirement the plan has been carrying since it
was written has never been implementable. It found it by reading the code the requirement would
have to use, not by reading the requirement.

## The amendment

Both findings are the same shape — a correct design that the plan's own path constraints forbid —
and both are fixed the same way, by widening the constraint to the shared location rather than by
weakening the design. Applied to `loops.md`:

1. `loop-004-2.allowed_paths` gains `platforms/shared/` and `platforms/python/`, with the reason in
   a comment. It gains two checks: the shared payload is created there and installed byte-identical
   to both hosts, and `state_validate.py` exists, is reached through `ap.py`, and validates all six
   schemas.
2. `loop-004-3.allowed_paths` gains `platforms/shared/` **read-only in effect**: it gains a check
   that it MUST NOT create a divergent copy, and that installing in either order leaves one
   identical tree.
3. `loop-004-4`'s fixture run gains the both-orders install as an explicit case, since that is the
   only place the collision decision is actually exercised on a real host.

`core/` remains forbidden to all three. Nothing here relaxes the no-fork rule.

## What the specification decided that nobody had

Recorded because these are design decisions now, not discoveries waiting in loop-004-4:

- **The collision resolves to one shared byte-identical copy**, with an install conflict on
  mismatch and a rule that uninstalling one adapter must not remove the copy the other still
  registers. Ownership metadata is host-neutral, under `.advanced-plans/`.
- **Two core skills are excluded from the allowlist**, not forked: `companion-detection` (it
  advertises the deprecated companion) and `permission-config` (Claude-specific, and already
  carrying the audit's one retirement exception). *"Exclusion is not a fork."*
- **When a core skill does not work on a host there are exactly three permitted responses** — wrap
  it, omit it and say so, or declare the action unsupported — and a fourth that is forbidden:
  editing it. If none of the three preserves the contract, that is a cross-platform core change
  request, and neither build loop may make it.
- **Role model tiers cannot be guaranteed portably.** Claude Code's Sonnet-orchestrator /
  Haiku-worker distinction has no portable equivalent once host-private agent files are off the
  table. The honest answer is that native runs use host policy, and strict per-role selection
  requires the external Herdr route. That is a real capability loss, stated rather than papered
  over.
- **`compact` does not compact the host conversation.** It compacts AAW artefacts and prints the
  host's own command, or *"start a new session and run the resume trigger."* No adapter may claim
  the context was compacted.
- **The human gate is the baseline, not a fallback.** Three literal responses (`APPROVE`, `REVISE`,
  `STOP`), decomposition blocked until one arrives, `resume` returning to the outstanding review,
  and auto mode staying stopped. Plannotator appears nowhere: *"not installed, detected,
  recommended, or invoked by either adapter."* That is the deprecation carried into the new hosts
  correctly.

## The finding it recorded against CI

*"Current CI will not automatically check even the generic path errors in those new directories
unless they are explicitly included in the scan."* `DEFAULT_SCANNED_ROOTS` has seven entries and
`platforms/codex/`, `platforms/opencode/` and `platforms/shared/` are none of them. Two of the three
directories this loop creates will be unscanned by the audit ralph-loop-003 spent five todos
building.

This joins `core/schemas/` and `core/state/` on the same list — named now in six places, still not
scheduled. It is a **scan-surface** problem, not a rule problem, and it is the same defect in a new
place: a check that reports green over ground it does not examine.

## Verification — controller-side

```
codex exec exit code                     0
tree state before and after              clean (sandbox was read-only)
inline copy vs trailing copy             identical, 510 lines each
citations followed                       21 of 21 correct to the line
AAW repository                           evidence only; no advanced-planning file touched
```

No code was written by this todo and none was asked for. `advanced-planning` remains at `fbc559b`,
**local**; no push has been approved for it.
