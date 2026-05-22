<!-- aaw-routing:begin -->
## Advanced AI Workflows Routing

This block is managed by `setup-with-claude`. To remove it cleanly, run
`/setup-with-claude --uninstall`. Do not edit the fenced markers manually.

### Front-Door Rules

When a user presents a new request, route to the right tool using these rules — in order:

1. **Ambiguous scope, unclear problem, or need for strategic review**
   → Invoke `/office-hours` (gstack)
   Use when: the user is not sure where to start, the problem spans multiple subsystems,
   or a second opinion on strategy is wanted before committing to a plan.

2. **Clear scope, unfamiliar codebase or new project**
   → Invoke `/plan-and-phase` (advanced-planning)
   Use when: the user knows what to build but this codebase or project is new. The command
   runs an exploration step before phase planning. Supply the gstack design doc content as
   the description argument if one has been archived.

3. **Clear scope, familiar codebase (continuing work)**
   → Invoke `/new-phase` (advanced-planning)
   Use when: the user knows what to build and the codebase is already understood from prior
   work. Skips the exploration step. Supply the gstack design doc content as the description
   argument if one has been archived.

4. **Need ideation mid-execution, stuck on options, or exploring trade-offs**
   → Use the `brainstorming` skill (superpowers)
   Use when: a todo or task requires exploring approaches before implementing. Invoke by
   reading `.claude/skills/brainstorming/SKILL.md` and following it.

5. **Need a structured implementation plan from a spec**
   → Use the `writing-plans` skill (superpowers)
   Use when: a spec or design doc is approved and a detailed task-by-task plan is needed.

6. **Need a second opinion on a plan, design, or completed work**
   → Invoke `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, or `/codex`
   (gstack)
   Use when: a phase plan or design is ready for structured review before execution begins,
   or after execution for a retrospective quality check.

7. **Visual review of a plan or diff**
   → Invoke `/plannotator-annotate` (plannotator, if installed)
   Use when: plannotator is installed (`.claude/commands/plannotator-annotate.md` exists)
   and the user wants a visual annotation of the phase plan or a code diff.
   Note: plannotator also fires automatically via its `EnterPlanMode`/`ExitPlanMode` hooks
   whenever Claude Code enters or exits plan mode — no explicit invocation needed for that.

### Superpowers Preference Overrides

When using the superpowers `brainstorming` skill, save design docs to:
`.advanced-plans/specs/`
(overrides the skill's default of `.claude/plans/` which targets a stale path)

When using the superpowers `writing-plans` skill, save plans to:
`.advanced-plans/specs/`
(overrides the skill's default of `docs/superpowers/plans/`)

Both skills honour user-stated preferences — no patch to superpowers is required.
All design docs and plans — whether from gstack, superpowers brainstorming, or
superpowers writing-plans — land under `.advanced-plans/specs/`. One archive, one
place to look.

### Companion-Detection Reference

Advanced-planning's companion-detection skill (invoked during `/plan-and-phase`) already
detects whether superpowers and plannotator are installed and recommends them where
appropriate. This meta-project does NOT replicate that logic — it relies on
companion-detection's existing behaviour.

### Closing Instruction — /gstack-to-plans Fallback

AFTER any gstack planning skill writes a design doc, invoke `/gstack-to-plans` if it
has not already fired.

This applies to: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`,
`/plan-design-review`, `/codex` — any gstack skill that produces a design doc under
`~/.gstack/projects/{slug}/`.

The auto-trigger hook in `.claude/settings.json` fires this automatically when a
matching file is written. This closing instruction is the manual fallback for when
the hook misfires or is disabled: always invoke `/gstack-to-plans` explicitly after
a gstack planning session if you are not certain the hook already ran.
<!-- aaw-routing:end -->
