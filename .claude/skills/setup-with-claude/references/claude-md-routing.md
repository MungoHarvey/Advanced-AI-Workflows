<!-- aaw-routing:begin -->
## Advanced AI Workflows Routing

This block is managed by `setup-with-claude`. To remove it cleanly, run
`/setup-with-claude --uninstall`. Do not edit the fenced markers manually.

Everything outside these two markers belongs to whoever wrote this file. This block adds
routing; it does not override, reorder, or claim precedence over instructions written
above or below it. Where it conflicts with the rest of this file, the rest of this file
wins.

### How to Tell What Is Installed

Several rules below apply only when a companion tool is actually installed. **Read the
installation manifest at `.aaw/installed.json` to find out.** A component is installed
when, and only when:

```
.components["<component>"]["installed"] == true
```

for `advanced-planning`, `gstack`, or `superpowers`.

Three things follow from that, and they matter:

- **Do not test for a directory.** A `.advanced-plans/` folder is *data* — a project can
  hold plans copied from elsewhere without having the framework installed. Presence of the
  folder is not presence of the tool.
- **Do not probe harness-specific paths.** The manifest is written by the detector, which
  is the only component allowed to know where a particular harness keeps its skills. Every
  rule below reads the manifest instead.
- **If `.aaw/installed.json` is missing, unreadable, or malformed, treat every component as
  NOT installed** and follow the plain upstream behaviour of whatever skill you are in. Do
  not guess, and do not write to a path that this project has given you no evidence exists.

Below, "**when Advanced Planning is installed**" always means exactly that predicate, and
so does the same phrasing for `gstack` and `superpowers`.

**Every route below that names a command or a skill belonging to a companion tool is
gated on that tool.** If you ever find one that is not — because this block was edited,
truncated, or is an older version — treat it as gated anyway and fall back to plain
behaviour. Recommending a command that this project has given you no evidence exists is
the failure this section exists to prevent, and a rule that forgot to say "when installed"
is not permission to guess.

### Front-Door Rules

When a user presents a new request, route to the right tool using these rules — in order:

1. **Ambiguous scope, unclear problem, or need for strategic review**
   → **When gstack is installed:** invoke `/office-hours`.
   → **When it is not:** there is no command to run. Work the ambiguity out in
   conversation — name the options, say which you would pick and why — and do not invent
   a substitute command.
   Use when: the user is not sure where to start, the problem spans multiple subsystems,
   or a second opinion on strategy is wanted before committing to a plan.

2. **Clear scope, unfamiliar codebase or new project**
   → **When Advanced Planning is installed:** invoke `/plan-and-phase`. The command runs
   an exploration step before phase planning.
   → **When it is not:** explore the codebase first, then plan — with the `writing-plans`
   skill if superpowers is installed, and in conversation if it is not.
   Use when: the user knows what to build but this codebase or project is new. Supply the
   gstack design doc content as the description argument if one has been archived.

3. **Clear scope, familiar codebase (continuing work)**
   → **When Advanced Planning is installed:** invoke `/new-phase`. It skips the
   exploration step.
   → **When it is not:** plan directly — with the `writing-plans` skill if superpowers is
   installed, and in conversation if it is not.
   Use when: the user knows what to build and the codebase is already understood from prior
   work. Supply the gstack design doc content as the description argument if one has been
   archived.

4. **Need ideation mid-execution, stuck on options, or exploring trade-offs**
   → **When superpowers is installed:** use the `brainstorming` skill. Load it from
   wherever this harness keeps its skills and follow it. See *Brainstorming* below for the
   three additions this project makes to it.
   → **When it is not:** explore the approaches in conversation. The *Brainstorming*
   section below still describes what this project wants from that conversation, but there
   is no skill to load and no three-path classification to announce.
   Use when: a todo or task requires exploring approaches before implementing.

5. **Need a structured implementation plan from a spec**
   → **When Advanced Planning is installed:** invoke `/new-phase` (or `/plan-and-phase`
   for a codebase not yet explored), passing the spec as the description. Phase planning
   is this project's route from an approved spec to executable work, and for that job it
   **supersedes** `writing-plans` — see *Brainstorming*, addition 3.
   → **When it is not installed:** use the `writing-plans` skill if superpowers is
   installed, and write the plan in conversation if neither tool is.
   Use when: a spec or design doc is approved and a detailed task-by-task plan is needed.

6. **Need a second opinion on a plan, design, or completed work**
   → **When gstack is installed:** invoke `/plan-ceo-review`, `/plan-eng-review`,
   `/plan-design-review`, or `/codex`.
   → **When it is not:** review the work directly, and say which lens you are applying —
   the value is the second perspective, not the command that summons it.
   Use when: a phase plan or design is ready for structured review before execution begins,
   or after execution for a retrospective quality check.

7. **Review at a phase boundary**
   → **When Advanced Planning is installed:** invoke `/run-gate`.
   → **When it is not:** this project has no phases, so there is no boundary to gate.
   Review the completed work directly and do not manufacture a phase to hold the review.
   Use when: a phase's work is complete and it must be reviewed before advancing.
   The gate reviewer runs on a different model from the implementer, reads the diff,
   check output, and phase success criteria, and writes a verdict to
   `.advanced-plans/gate-verdicts/`. Every finding is resolved or explicitly waived
   by the user before the phase advances.
   Note: plannotator was deprecated on 2026-08-26. Do not route to it or detect it.

### Brainstorming

The `brainstorming` skill classifies each request into one of three paths — **Spike**,
**Bounded**, or **Architectural** — and says the classification out loud before its first
question. That classification is the skill's, not this block's. Follow it.

**Where this section names a spec location, a terminal state, or a question format that
differs from the skill's built-in default, this section wins — for those three things
only.** They are project-level instructions, and a skill's built-in default is what applies
in a project that has said nothing on the subject. This project has said something about
exactly three things.

Two limits on that, and both are absolute. It is a claim over the **skill's** defaults and
never over the user's own writing: instructions outside this block's markers still win, as
the top of the block says. And everything the three additions do not mention — the
classification itself, the approval gates, the questions asked, the shape of the design —
stays exactly as the skill has it. Override those three defaults, and nothing else.

This project adds three things, and **two of the three apply to the Architectural path
only.** Spike and Bounded behave exactly as the skill has them: a Spike ends in a reported
recommendation, a Bounded task ends in a short design in chat followed by implementation.
Neither produces a spec file, and neither leads into phase planning. Do not upgrade a
request into phase planning because this project has Advanced Planning installed — that
would drag every feasibility probe and one-file fix into a full decomposition, which is the
exact over-process the three-path router exists to prevent.

**1. Clarifying questions — all three paths.**
When you ask the user clarifying questions and the answers are a small set of known
alternatives, ask them with the harness's structured question tool (`AskUserQuestion` in
Claude Code) rather than as free prose. One question at a time, with the options spelled
out and a recommendation named. Where the harness has no such tool, ask in prose as usual —
this is a presentation preference, not a gate. It does not change what you ask or when the
user's approval is required.

**2. Where the written spec goes — Architectural path only.**
When Advanced Planning is installed, write the approved spec to **`.advanced-plans/specs/`**.
When it is not installed, use the skill's own default location, unchanged. Never write to
`.advanced-plans/specs/` on the strength of this block alone — the manifest must say the
framework is there.

**3. What happens after the spec is approved — Architectural path only.**
The skill's own terminal step is the `writing-plans` skill. When Advanced Planning is
installed, go to **phase planning** instead (`/plan-and-phase` for a codebase you have not
explored, `/new-phase` for one you have), passing the approved spec as the description.
When Advanced Planning is not installed, use `writing-plans` exactly as the skill says.

### Where Plans and Specs Are Written

When Advanced Planning is installed, the `writing-plans` skill's output also belongs in
`.advanced-plans/specs/`, overriding its default of `docs/superpowers/plans/`. When it is
not installed, leave that default alone.

The intent is one archive: design docs from gstack, specs from `brainstorming`, and plans
from `writing-plans` all land under `.advanced-plans/specs/` in a project that has Advanced
Planning — one place to look. In a project that does not, nothing is redirected anywhere,
and no `.advanced-plans/` path is invented.

This section says where `writing-plans` writes **if it runs**. It is not an instruction to
run it. In a project with Advanced Planning, the step after an approved architectural spec
is phase planning, not `writing-plans` — rule 5 above and addition 3 under *Brainstorming*
both say so, and this section does not reopen the question. `writing-plans` still runs when
a user asks for it directly, or when a phase loop injects it as a todo's skill; that is the
output being redirected here.

Both skills honour user-stated preferences, so this is a preference and not a patch — no
change to superpowers is required for any of it.

### Companion Tools

**Read `.aaw/installed.json` to decide what is installed here.** This section reasons about
one tool being present and another absent, and that judgement is the manifest's to make.
Do not infer that Advanced Planning is installed from a `.advanced-plans/` directory, or
that superpowers is installed from a skills directory — a project can hold either as data.

When a user is planning work in a project where Advanced Planning is installed and
`superpowers` is not, say so once and offer it: the methodology skills (`brainstorming`,
`writing-plans`, TDD, systematic debugging) are what the loops inject per todo. The reverse
also holds — in a project with `superpowers` but no Advanced Planning, a programme large
enough to need phases is worth mentioning Advanced Planning for.

Recommend the tool, then drop it. Do not re-offer within a session, and do not block on it.

Plannotator is **not** part of this stack. It was deprecated on 2026-08-26 and replaced by
the cross-model gate reviewer described in rule 7. Do not recommend, detect, install, or
route to it, and treat any companion list that still names it as out of date.

### Closing Instruction — /gstack-to-plans Fallback

**When gstack is installed:** after any gstack planning skill writes a design doc,
invoke `/gstack-to-plans` if it has not already fired. **When it is not**, no gstack skill
can have written a design doc, so this rule never applies — do not go looking for one.

This applies to: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`,
`/plan-design-review`, `/codex` — any gstack skill that produces a design doc under
`~/.gstack/projects/{slug}/`.

Where this harness supports write hooks, `setup-with-claude` installs one that fires this
automatically when a matching file is written. This closing instruction is the manual
fallback for when the hook misfires, is disabled, or is unavailable on this harness: always
invoke `/gstack-to-plans` explicitly after a gstack planning session if you are not certain
the hook already ran.
<!-- aaw-routing:end -->
