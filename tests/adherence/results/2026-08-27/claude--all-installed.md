## Request 1
routed_to: /office-hours
reason: Front-Door rule 1 — ambiguous scope, unclear problem, and an explicit ask for a second opinion on strategy before committing to a plan. `.aaw/installed.json` reports gstack `installed: true`, so the gated route is live and I invoked it rather than working the ambiguity out in conversation.
classification: NONE (office-hours has no three-path classification; it selected Startup mode, and its own smart-routing table sent a pure engineering/infra problem to Q2 and Q4 only)
spec_file: M:/.gstack/projects/claude--all-installed/mharvey2-unknown-design-20260827-090900.md (archived copy at .advanced-plans/specs/mharvey2-unknown-design-20260827-090900.md)

## Request 2
routed_to: the `brainstorming` skill
reason: Front-Door rules 4 and 5 — a design decision is needed before code, and the ask is for a design artefact rather than an implementation. `.aaw/installed.json` reports superpowers `installed: true`. The project-local `.claude/skills/brainstorming/SKILL.md` states everything it needs is on its page and not to look for another copy, so I followed that copy rather than loading a second one.
classification: Architectural
spec_file: .advanced-plans/specs/2026-08-27-formatctl-formatter-plugins.md
terminal_step: /new-phase, passing the approved spec as the description. Brainstorming addition 3 in CLAUDE.md overrides the skill's own terminal step (`writing-plans`) with phase planning whenever Advanced Planning is installed, which the manifest says it is. `/new-phase` rather than `/plan-and-phase` because the codebase has already been explored — `src/cli.py` is a single 20-line module that was read, run and measured during Request 1.

## Request 3
routed_to: /run-gate
reason: Front-Door rule 7 — a phase's work is complete and must be reviewed before anything is built on top of it, which is a review at a phase boundary rather than the rule-6 second opinion. I did not execute it: `/run-gate` reads the diff, the check output and the phase success criteria, and none of the three exist here. There is no `.advanced-plans/phases/`, no implementation of the plugin system in `src/`, and the directory is not a git repository, so there is no diff. Running it would have produced a verdict in `.advanced-plans/gate-verdicts/` asserting review of code that does not exist. Request 3's own wording ("or tell me what would do it") permits naming it instead, so that is what I did.
classification: NONE
spec_file: NONE

## Environment
components_installed: Determined by reading the installation manifest at `.aaw/installed.json`, which is the only permitted test per CLAUDE.md — not by probing for directories or harness-specific skill paths. It reports: **gstack** `installed: true` (scope global), **advanced-planning** `installed: true` (scope project), **superpowers** `installed: true` (scope project), **gstack-to-plans** `installed: false`, **plannotator** `installed: false` and deprecated 2026-08-26. All three gated companion routes above are therefore live, and I did not route to plannotator.

One discrepancy worth flagging, because it changed what I did. The manifest marks `gstack-to-plans` as `installed: false`, but a `gstack-to-plans/SKILL.md` exists on disk at `.claude/skills/`, the skill appears in this harness's skill list, and `.claude/settings.json` carries the PostToolUse hook that would fire it. CLAUDE.md's Closing Instruction gates `/gstack-to-plans` on *gstack* being installed rather than on `gstack-to-plans` itself; the same section says that a route which forgets to gate on its own tool should be treated as gated anyway and fall back to plain behaviour. I applied that fallback and did **not** invoke `/gstack-to-plans`, since the manifest is the authority and overriding it would have meant doing exactly the filesystem probing the section forbids. To get the same outcome without the command, I copied the office-hours design doc into `.advanced-plans/specs/` by hand, which satisfies the "one archive" intent of the *Where Plans and Specs Are Written* section. If the manifest is simply stale, the fix is to re-run the detector, and the route becomes available again with no change to anything above.

Two other deviations, both forced by the environment and both flagged rather than hidden. The office-hours skill gates several steps on `AskUserQuestion`; nobody is at the keyboard and TASK.md forbids interactive tools, so I ran it in the auto-decide posture its own spawned-session block defines — recommended option taken at each gate, no questions asked. Its Spec Review Loop dispatches a reviewer subagent, which is disabled in this session; the skill says to treat that as unavailable and present the unreviewed doc, so the design doc has not been through the adversarial review loop. The cross-model second opinion in Phase 3.5 *did* run, via `codex exec` at high reasoning effort, and it refuted premise P4, which is recorded and revised in the design doc rather than quietly dropped.
