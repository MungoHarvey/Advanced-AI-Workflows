# What upstream Superpowers changed under the fork — 2026-08-26

**Loop**: `phase-5` / `ralph-loop-001` — todo `loop-001-3`
**Provider**: opencode / **Qwen3.5 397B** (`elm/Qwen/Qwen3.5-397B-A17B-FP8`, ELM
proxy, Edinburgh), herdr agent `spread3`, pane `w2:p4`, read-only in
`C:/Users/mharvey2/Coding/superpowers`
**Controller**: Claude Opus (AAW controller checkout) — commissioned the worker,
then re-ran every check independently. See *Controller verification* below.

**Refs**: merge-base `f2cbfbe` · `upstream/main b36e082` (v6.3.0)

---

## Commands run

```
git diff  f2cbfbe b36e082 -- skills/brainstorming/SKILL.md
git diff  f2cbfbe b36e082 -- skills/using-superpowers/SKILL.md
git grep -n -i -E "advanced.planning|advanced_planning|plannotator" b36e082 -- skills/
git show  b36e082:skills/brainstorming/SKILL.md
```

Diffstat, upstream-side drift on the two forked files:

```
 skills/brainstorming/SKILL.md     | 142 ++++++++++++++++++++++++++++++--------
 skills/using-superpowers/SKILL.md |  90 +++++-------------------
 2 files changed, 132 insertions(+), 100 deletions(-)
```

`brainstorming` grew (+142/-8, net +134). `using-superpowers` **shrank**
(+14/-67, net -53) — upstream moved content out to `references/`.

---

## The router — quoted verbatim from `b36e082:skills/brainstorming/SKILL.md:22`

> ## Three Paths
>
> Before your first question, classify the request and say the
> classification out loud — "this looks bounded, so I'll present a short
> design here rather than write a spec" — so your human partner can
> override it:
>
> - **Spike** — a feasibility question ("can we...", "is it possible...",
>   "quick and dirty is fine") whose output is an answer, not code you
>   keep. Present the question and what you'll try in 2-3 sentences, get
>   a nod, then find out as cheaply as correctness allows. No design
>   doc, no spec file. Report findings as a recommendation; anything you
>   built stays labeled throwaway.
> - **Bounded** — a well-scoped change to code that already exists in
>   this repo: a new flag, a small endpoint, a one-file fix.
>   Understanding the kind of app is not enough — bounded means the flow
>   you are changing is already here to read. If there is no existing
>   flow to change, the task is not bounded. Ask the clarifying
>   questions that matter, present a short design IN CHAT (a few
>   sentences to a few short paragraphs), and STOP. Implementation
>   starts only after your human partner says yes to that design — a
>   bounded task's approval is as hard a gate as an architectural
>   one. No spec file, no implementation plan document.
> - **Architectural** — new projects, new subsystems, changes that
>   restructure how components fit together or alter interfaces others
>   depend on. Follow the full process: questions, approaches, sectioned
>   design, written spec, then the writing-plans skill.
>
> When in doubt between two paths, take the heavier one. The ratchet is
> one-way: hidden complexity discovered mid-task upgrades the path —
> stop, say so, and step up. Nothing downgrades mid-task.

**This is the finding that matters most for the port.** At the merge-base,
`brainstorming` had *one* path and *one* terminal state (`writing-plans`), so
the fork's SP-2 could redirect "the" terminal state and be correct. Upstream now
has **three paths and three terminal states**, and only the Architectural one
ends at `writing-plans`. Spike ends at a reported recommendation; Bounded ends
at direct implementation with no plan document at all.

Consequence for SP-2: the port must attach **only to the Architectural path**.
An SP-2 that redirects unconditionally would drag every feasibility probe and
one-file fix into a full phase-plan decomposition — the exact over-process
outcome upstream added the router to prevent. This refinement has been carried
back into the behaviour matrix.

---

## Advanced Planning and Plannotator in upstream `skills/`

```
git grep -n -i -E "advanced.planning|advanced_planning|plannotator" b36e082 -- skills/
-> no output, exit status 1
```

**Zero hits.** Upstream's `skills/` tree does not mention either tool. The
architectural path terminates at upstream's own `writing-plans` skill, not at
any external planning system. The fork's integration is entirely downstream
innovation, which is why it survives only as a patch.

---

## What a file copy would destroy

Replacing upstream's two files with the fork's copies would revert, in
`skills/brainstorming/SKILL.md`:

1. **The three-path router itself** — Spike / Bounded / Architectural
   classification, and the requirement to state the classification aloud so the
   user can override it.
2. **The Spike path** — the whole feasibility-probe pattern, including the rule
   that anything built stays labelled throwaway.
3. **The Bounded path** — short design in chat, hard approval gate, no spec file,
   no plan document.
4. **The ratchet rule** — "when in doubt take the heavier one"; upgrade mid-task,
   never downgrade.
5. **The path-classification Red Flags table** — seven rationalisations,
   including "I'll call it bounded and skip the spec" and "they approved the
   spike, so the follow-up is approved too".
6. **Three distinct terminal states**, replaced by the merge-base's single one.
7. **The just-in-time visual companion**, replaced by the merge-base's
   offer-upfront behaviour.
8. **The rewritten Process Flow digraph** (three entry points, three terminals).

And in `skills/using-superpowers/SKILL.md`:

9. **The per-harness reference pointers** — `references/codex-tools.md`,
   `pi-tools.md`, `antigravity-tools.md`, `hermes-tools.md`. This is the only
   net *addition* on that file, and the only thing on it a copy would lose.

---

## Controller verification

Per the programme rule that a worker's own summary is not evidence, every claim
above was re-run by the controller. Results: the grep returns zero hits
(exit 1); the diffstat matches exactly; `## Three Paths` is at line 22 of
`b36e082:skills/brainstorming/SKILL.md`; the quoted block is byte-faithful to
the source.

**One correction to the worker's report.** Its verdict section listed four
`using-superpowers` items as things a copy would *lose* — the 15-node flow
digraph, the Rigid-vs-Flexible skill-types distinction, and the three-tier
instruction-priority rules. That is inverted. Upstream **removed** those; the
fork, being older, still has them. Independent check:

```
git show f2cbfbe:skills/using-superpowers/SKILL.md | grep -c digraph   -> 1
git show b36e082:skills/using-superpowers/SKILL.md | grep -c digraph   -> 0
```

Copying the fork over upstream would *reintroduce* that removed material, not
lose it. The worker's own section (1) had it right — it listed all of them under
"What upstream removed" — and then contradicted itself in section (4). Only
item 9 above survives as a genuine loss on that file.

The error is worth recording rather than silently fixing: it is exactly the
failure mode that makes a worker's summary inadmissible on its own, and it would
have made the port's justification wrong in a way that a reviewer reading only
the verdict would not catch.
