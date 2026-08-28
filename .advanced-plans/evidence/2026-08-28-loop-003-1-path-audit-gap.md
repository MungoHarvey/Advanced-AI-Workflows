# loop-003-1 — what the path audit checks, and the gap against §7.3

**Todo:** `loop-003-1` (phase-6, ralph-loop-003). `allowed_paths: ["none — read-only"]`.
**Outcome asked for:** *"The change is understood as adding a rule that applies only under `core/`,
not as widening a rule that would then fire on legitimate installed-runtime paths."*

**Executed by:** `codex exec -m gpt-5.6-sol -c model_reasoning_effort=high -s read-only`, prompt on
stdin, in the `advanced-planning` checkout. **One-shot, not an interactive pane** — which also
avoided a directory-trust dialog that an interactive `codex` hit on this repository. Nothing was
written. Twelve findings, and every one I checked held.

---

## Routing note: one-shot was the right call and nearly wasn't

An interactive pane was started first (`herdr pane run … codex.cmd -m gpt-5.6-sol …`) and settled
at **`blocked` on a "Do you trust the contents of this directory?" modal**. Per the operating
rules a dialog is the operator's to clear, not the worker's, so the pane was closed unanswered and
the task rerouted to `codex exec`, which is non-interactive and has no trust gate. The status line
confirmed what actually ran:

```
model: gpt-5.6-sol   reasoning effort: high   sandbox: read-only   approval: never
```

This is the codex counterpart of the rule already recorded for `cursor` and `claude`: **a fresh
directory triggers a first-run trust dialog, and codex is not exempt.** For read-only analysis
`codex exec` sidesteps it entirely. Worth carrying into CLAUDE.md.

Two incidental observations from the run: codex is **0.150.1** here, not the 0.149.1 recorded in
CLAUDE.md; and two skills under `~/.agents/skills/` fail to load on every codex start
(`hook-converter-template`, `plugin-to-skill-converter` — *"missing YAML frontmatter delimited by
---"*). Neither affects this work.

## What the audit checks today — confirmed

Three regexes, and that is the entire violation registry (`path_audit.py:59–74`):

```
doubled-prefix      \.advanced-\.advanced-
wrong-nesting       \.claude/\.advanced-plans
deprecated-token    \.claude/plans/
```

Seven default scanned roots (`path_audit.py:82–90`), of which **two are core**
(`core/agents`, `core/skills`), three are host-adapter surfaces
(`platforms/claude-code/commands`, `…/agents`, `platforms/cowork`) and two are installed-runtime
(`.claude/commands`, `.claude/agents`, neither of which exists in the source checkout). CI runs it
bare (`ci.yml:132`), so the defaults are the effective CI scope. Current violations: **0**.

## The finding that changes how loop-003-2 must be run

`platforms/python/tests/test_path_audit.py:237–252` is
`TestFalsePositiveGuard::test_claude_skills_ref_is_not_flagged`. It writes

```python
clean_file = root / "core" / "agents" / "worker.md"
clean_file.write_text("Load skill from `.claude/skills/plan-todos/SKILL.md`.\n")
...
assert violations == [], "Legitimate .claude/skills/ reference was falsely flagged"
```

**The suite currently asserts, as a named false-positive guard, exactly the behaviour §7.3
forbids** — a host directory inside `core/`, in the file `core/agents/worker.md`, declared
*legitimate* in the test's own name and docstring. And it is not hypothetical: `core/agents/worker.md`
is one of five real files under `core/` that carry host tokens today (measured controller-side).

Loop-003-2's `allowed_paths` are `["platforms/python/path_audit.py", "docs/path-conventions.md"]`.
So the todo as written **cannot be completed without leaving the suite red**, and has no path to
fix it: the test file first becomes writable in loop-003-4. That is a scoping defect in the plan,
not in the todo's intent. Amended — see `phases/phase-6/plan.md`, *Amendment — 2026-08-28, after
loop-003-1*.

## The tension, stated precisely

The docstring asserts (`path_audit.py:34–35`) that a bare `.claude/commands/` or `.claude/skills/`
reference is legitimate and must not be flagged. That is **true for the installed-runtime and
adapter surfaces and false for `core/`**, which `docs/path-conventions.md:31–36` defines as
"Platform-agnostic definitions". A rule widened uniformly across the existing roots would newly
fail:

- adapter command Markdown under `platforms/claude-code/commands/` that documents installing into
  `.claude/commands/` — pinned by `test_path_audit.py:219–235`;
- legitimate material under the scanned `.claude/commands/` and `.claude/agents/` runtime roots;
- installer scripts explaining what they create beneath `.claude/`, which
  `docs/path-conventions.md:133–138` classifies as non-stale.

So the rule must be **scope-dependent**, not a wider pattern. `core/agents/` and `core/skills/` are
already scanned roots, so nothing needs adding to the scope — the work is a rule that fires only
under `core/`.

## The gap against §7.3, by category

| §7.3 category | Detectable today |
|---|---|
| host directories | **partially, and only for `.claude/`** — via two compound tokens. A bare `.claude/`, `.claude/skills/`, `.cursor/`, `.opencode/`, `.codex/` is not a signature |
| host-only tool and agent names | **no** — no pattern describes a tool or agent identifier |
| host permission syntax | **no** — no permission grammar is inspected |
| "core files" as a whole | **no** — only `core/agents` and `core/skills` are scanned. `core/schemas/` and `core/state/`, both canonical parts of `core/` per `docs/path-conventions.md:31–36`, are outside every root |

That last row is a decision loop-003-2 must **name rather than make silently**: widening the roots
to all of `core/` is a larger change than adding a rule, and it will surface hits in files nobody
has looked at.

Codex correctly marked one thing **unverified**: the concrete inventory of Claude-only tool names
and the grammar of host permission syntax exist nowhere in the repository. Neither vocabulary is
written down, so 003-2 is defining it, not implementing it.

> **Correction, 2026-08-28, after loop-003-2.** The first half of that is wrong, and running the
> rule is what disproved it. The inventory *is* written down — in example `outcome:` fields inside
> the core skills' own reference docs: `core/skills/ralph-loop-planner/references/todo-schema.md:154`
> ("No occurrences of 'Claude Code', 'Cowork', 'slash command', 'Agent tool', or 'TodoWrite' appear
> in any core/skills/ SKILL.md file"), `core/skills/plan-todos/references/todo-schema.md:134` (the
> same plus `.claude/`), and two shorter variants at `:96` and `:110`. The project had stated its own
> definition of a Claude-only name four times, as worked examples of a verifiable todo, and nobody
> had turned it into a check. 003-2's rule is built from that list rather than an invented one — see
> `2026-08-28-loop-003-2-host-neutrality-rule.md`. The claim about permission *grammar* stands: no
> such grammar is written down anywhere.

## Nine defects in the module, none of which this loop asked about

Verified controller-side, not taken on the worker's word:

- **`_is_excluded` does not match segments or prefixes** despite the name and docstring. It is
  `if seg in posix` — unanchored, case-sensitive substring containment over the whole path
  (`path_audit.py:147–167`). A hypothetical `core/skills/docs-writer/SKILL.md` is silently excluded
  by the `"docs"` entry. Confirmed by probe: `docs-writer` excluded `True`, `document-release`
  excluded `False`.
- **The docstring's `README*`, `CHANGELOG*`, `*.schema.md` exclusions do not exist.** Grepped:
  the only occurrence of those names in the module is the docstring line claiming them
  (`path_audit.py:27`). There is no filename exclusion anywhere.
- Consequently `README.md`, `CHANGELOG.md` and `*.schema.md` **are** scanned — `Path.suffix` is
  the final suffix, so `x.schema.md` is `.md`.
- **The suffix filter is an allowlist, not the "binary-looking files" check its comment claims**
  (`path_audit.py:248–249`). `.py` is silently skipped, so no Python file in a scanned root is ever
  audited.
- The docstring says the doubled-prefix rule also covers the backslash form
  `\\.advanced-\\.advanced-`; the regex has no such alternative (`path_audit.py:29–31` vs `62–65`).
- **The audit checks one of the five deprecated tokens its own source of truth lists.**
  `docs/path-conventions.md:118–129` names `plans/` (top-level), `.claude/plans/`, `.claude/state/`,
  `plans/gate-verdicts/` and `/new-loop`. Only `.claude/plans/` is implemented — and two implemented
  rules are not in the document at all.
- `--verbose` is parsed and never read (`path_audit.py:280–284`, `301–325`). The option does
  nothing its help text describes.
- A missing scanned root is skipped silently (`path_audit.py:235–239`) and an `OSError` while
  reading returns "no violations" (`path_audit.py:183–187`). Both turn absent coverage into a clean
  result — which is how `.claude/commands` and `.claude/agents`, absent from this checkout, count as
  scanned today.
- The CI comment (`ci.yml:135–140`) and the test helper (`test_path_audit.py:37–49`) both omit
  `platforms/cowork` from their copies of the root list. Two independent transcriptions of the same
  list, both wrong in the same way.

## Verification

Every claim above that I checked, held: the test at 237–252, the absent README/CHANGELOG exclusion,
the deprecated-token table, the suffix allowlist, the test helper's missing root, `_is_excluded`'s
substring semantics, and the dead `--verbose`. Two of them (`_is_excluded`, `--verbose`) I had
measured **before** dispatching, precisely so the answer could be checked rather than believed;
codex found both independently and eight more.

## Carried into 003-2

- The amendment above must be honoured: the false-positive guard is **inverted and renamed**, not
  deleted. A test asserting the old wrong behaviour should become one asserting the new right
  behaviour, so the guard survives the change rather than being removed by it.
- Whether the scanned roots widen to all of `core/` is a named decision, not a silent one.
- The nine module defects are real but out of scope here. The two that could make loop-003-3's run
  *lie* are the silent-`OSError` and the substring exclusion; the rest are cosmetic or documentary
  and belong in their own todo.
