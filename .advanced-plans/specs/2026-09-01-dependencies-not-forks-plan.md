# Dependencies, not forks — execution plan

**Status:** PROPOSED. Not accepted, not scheduled, nothing implemented.
**Date:** 2026-09-01
**Revised:** 2026-09-01, after a coherence check against the programme record. See §9.
**Amends:** [`2026-08-26-herdr-multi-runtime-orchestration-design.md`](2026-08-26-herdr-multi-runtime-orchestration-design.md) §8, §13.1, §13.2
**Relates to:** Phase 5 (closed — see §3), Phase 7, and the §13.2 half of Phase 9. **Not** Phase 8.

---

## 1. The problem, in the owner's words

> "Editing forks and the packaged dependencies requires constant updating to the specific tools
> inside those but that can be clunky and could require heavy adjustment each update. I wonder if
> our main package can help configure each of these together rather than specific edits to the
> packages? That way these can be dependencies."

The intuition is correct, it is already the design's stated intent, and — as §3 records — the
programme has already proven it once. What is missing is the layer that would make it hold.

## 2. What is actually true today

Measured 2026-09-01 against the working copies on this machine, not inferred from the design.

| Component | Fork state in substance | Local patch on `main` | Verdict |
|---|---|---|---|
| **gstack** | true `mirror` | **none** | Already a dependency. Not the problem. |
| **superpowers** | `patch` on `main`; **a clean mirror exists on a local branch** | 73 insertions, 2 files | **Solved in Phase 5. Blocked on one command.** |
| **advanced-planning** | `owned` | n/a | A dependency AAW installs. Now `v0.19.0`. |
| **plannotator** | deprecated 2026-08-26 | n/a | Out of the stack. |
| **AAW** | `owned` | n/a | The integrator. |

**There is exactly one fork patch across the stack, it is 73 lines, and it has already been
eliminated on a branch.**

The installed gstack (`~/.claude/skills/gstack`, v1.60.1.0) sits exactly at `origin/main` from
`garrytan/gstack` — zero fork-only commits, zero net diff, one modified generated file
(`gstack/llms.txt`). Updating it costs nothing today.

Superpowers `main` still carries four fork-only commits and a 73-line net patch across
`skills/brainstorming/SKILL.md` and `skills/using-superpowers/SKILL.md`. That patch is stale — it
still advertises **Plannotator**, deprecated on 2026-08-26, and it detects Advanced Planning by
Claude-only paths. But **that staleness is known, deliberate, and already fixed elsewhere.** See
§3.

### 2.1 What is genuinely missing on the AAW side

| Artefact | Specified in | Exists? |
|---|---|---|
| `.aaw/installed.json` (runtime manifest) | Phase 5 predicate | Schema and example only; **written at install time** |
| `.aaw/project.toml` | §8 | **No** |
| Compatibility manifest (tested tag + SHA) | §13.2 | **No** |
| Component detection | — | Yes, but **hardcoded in Python** |

`.aaw/detect.py` reports what happens to be installed by probing sentinel paths listed as Python
literals in `component_specs()`. It is honest about what it finds. But **the component list is
itself hardcoded in a package file** — the same clunkiness the owner is describing, one level up.
Adding or retiring a component means editing Python.

`references/upstream-baseline-2026-08-26.json` is the compatibility manifest's ancestor: a dated
snapshot, self-marked `refresh_required_before_execution: true`, which still records
advanced-planning at `v0.16.0` (it is now `v0.19.0`). It records divergence counts but not the
things §13.2 requires — tested tag, adapter version, install method per host, or the date and
result of the compatibility suite.

And `docs/upstream-sync-playbook.md` §11 step 4 instructs the operator to "update AAW's
compatibility manifest" — **an artefact that does not exist.** A documented step that cannot be
performed is the same defect class this programme has spent three releases removing.

## 3. What Phase 5 already delivered — and why the fork still looks unfixed

This section corrects the first draft of this plan, which proposed building something that
already exists.

**Phase 5, "Superpowers Behavioural Port", is CLOSED.** Gate PASSED on attempt 1 with three
reviewers on three backends, none of them the implementer: codex (91), opencode/Qwen as
`code-review-agent` (78), claude/Opus as `phase-goals-agent` (84). Zero failed criteria.

It delivered precisely the thing this plan was going to propose:

- **All four Superpowers intents moved to an AAW-owned fenced block** in the instruction file
  (`.claude/skills/setup-with-claude/references/claude-md-routing.md`), merged idempotently into
  both `CLAUDE.md` and `AGENTS.md`, preserving user content byte-for-byte.
- **The fork patch target is zero.** Verified independently today:
  `git diff upstream/main...mirror/upstream-2026-08-26` is **empty**, and `rev-list` is 0 in both
  directions. The mirror branch and upstream are the same commit.
- **Detection is already manifest-driven and host-neutral.** The predicate is
  `.aaw/installed.json → components["<name>"]["installed"] == true`. The block contains zero
  `.claude/`, `.cursor/`, `.opencode/` or `.agents/` paths, and treats a `.advanced-plans/`
  directory as data rather than an installation — proven against a decoy fixture.
- **Plannotator is already gone from the routing surface**, present only as an explicit
  do-not-use instruction.
- A backup tag `pre-aaw-port-2026-08-26` preserves the pre-port fork head at `fde9f97`.

**So why does the fork still carry the patch?** Because publishing the mirror requires:

```
git push origin mirror/upstream-2026-08-26:main --force-with-lease
```

Force-pushing a default branch is on the kickoff prompt's not-authorised list. Phase 5 therefore
prepared and proved the mirror locally, wrote the exact command down, and stopped at a human
gate. **That gate has never been cleared.**

This is the single most important correction in this document. The answer to "can these be
dependencies?" is, for superpowers: **yes, it already is one — one authorisation away.**

## 4. The constraint that decides the rest

The seam is **overlay-by-adjacent-file, not setting-a-setting.**

Almost none of these tools expose a configuration hook for the behaviour AAW needs to change:

- **herdr** regenerates its `SKILL.md` verbatim from the binary on every upgrade, so an edit there
  is destroyed by the next `herdr --skill`. The working override lives in the user's `CLAUDE.md`
  and says so explicitly.
- **gstack** skills have no documented override hook.
- **superpowers** routing lives in a `SKILL.md` — which is why the first answer was to edit it,
  and why Phase 5's answer was to stop.

Phase 5 is the existence proof that the boundary approach works for one tool, on five runtimes.
What has never been written down is **whether it generalises** — which tools expose a real
config seam and which must be handled at the boundary. That inventory is Stage 0, and it is the
only genuinely unexplored thing in this plan.

## 5. Non-goals

- **The `aaw` registry and CLI (Phase 8).** The kickoff prompt is explicit: do not implement it
  yet. Nothing here depends on it.
- **Vendoring dependencies into AAW.** Pinning is not copying.
- **Re-doing Phase 5.** It passed. This plan consumes its output.
- **Touching gstack.** It is already a mirror. Leave it alone.

---

## 6. The plan

Four stages. Stage 2 is an authorisation, not a build.

### Stage 0 — Inventory the seams (read-only)

**Why first:** every later stage assumes a seam exists. Phase 5 proved one exists for
superpowers. Whether that generalises has never been tested, and if a tool has no seam, its
behaviour cannot move to the AAW boundary and the honest answer is a documented patch rather than
a pretence.

For gstack, superpowers, advanced-planning, herdr, and each target host (Claude Code, Codex,
OpenCode, Cursor), establish and record:

- a config file it reads, and whether an upgrade preserves it;
- an environment variable it honours;
- a hook or extension directory;
- an adjacent-file overlay that survives upgrade;
- or **nothing** — in which case that is the finding.

**Deliverable:** `docs/config-seams.md` — one row per tool, each cell citing the file, flag, or
command that proves it, and each "nothing" citing what was tried.

**Gate:** every row cites evidence. A row reading "probably supports X" fails the gate.

**Cost:** hours, read-only, no external writes. **Does not touch Phase 6.**

### Stage 1 — Make the manifest the source of truth

Two artefacts, one principle: **AAW declares, the installer obeys, and nothing is hardcoded in
Python.**

1. `.aaw/project.toml` — schema, parser, validation, per §8. Component entries carry repository,
   upstream, fork state (`mirror` / `patch` / `owned`), and the detection sentinel.
2. `.aaw/compatibility.json` — **generated**, per §13.2: repository URL, upstream URL, **tested
   tag and full commit SHA**, adapter version, installation method per host, and the date and
   result of the suite that produced it.
3. `detect.py` reads its component list from the manifest instead of `component_specs()`
   literals.

**The single most important rule in this stage:** the compatibility manifest is **generated by
the suite that tested it**, never hand-edited. A hand-maintained manifest drifts, and a drifted
manifest reports a tested SHA that nobody tested — a check that reports what nobody measured,
which is the exact defect class of the last three advanced-planning releases.

**Gate:**

- ✓ `detect.py` produces byte-identical output before and after the refactor, proving the
  manifest replaced the literals faithfully.
- ✓ Removing a component from the manifest removes it from the audit output; adding one adds it.
  **Both directions tested**, so the manifest is shown capable of changing the answer.
- ✓ A manifest whose recorded SHA does not match the installed tree is reported as drift, proven
  by inducing drift.

### Stage 2 — Publish the superpowers mirror (one authorisation)

Not a build. Phase 5 built it and proved it. What remains:

1. The owner runs, or explicitly authorises:
   `git push origin mirror/upstream-2026-08-26:main --force-with-lease`
2. Re-verify post-publish that `origin/main` and `upstream/main` are the same commit.
3. Confirm the backup tag `pre-aaw-port-2026-08-26` (at `fde9f97`) is pushed **before** the
   force-push, so the pre-port head survives on the remote and not only on this machine.
4. Record the published SHA in the Stage 1 compatibility manifest.

**Gate:**

- ✓ `git diff upstream/main...origin/main` on the fork is empty, checked against the remote.
- ✓ The backup tag exists on the remote.
- ✓ The behaviour matrix from `tests/adherence/` still passes against the published mirror.

**Note the ordering dependency:** step 3 must precede step 1. A `--force-with-lease` that
succeeds before the backup tag is pushed leaves the only copy of the pre-port head on one
laptop.

### Stage 3 — Pin, and refuse to drift silently

- Installers default to the tested manifest, **not floating `main`** (§13.2).
- `aaw doctor --latest` reports newer upstream releases and **must not silently upgrade**.
- The fenced-block contract test: user-authored content immediately above and below the fences
  survives install, refresh and uninstall **byte-identically**. Phase 5 asserts this behaviour;
  Phase 7 names the test as its highest-consequence deliverable. Write it there.

**Gate:**

- ✓ A fresh clone installs the pinned SHAs and the resulting tree matches the manifest.
- ✓ `--latest` reports an available upgrade without performing one, proven against a
  deliberately outdated pin.
- ✓ The fenced-block test fails when the guard is removed — restore-and-rerun, the discipline
  used throughout advanced-planning 0.19.0.

### Stage 4 — Close the documentation gaps this opens

- `docs/upstream-sync-playbook.md` §11 step 4 names a manifest that exists.
- `references/upstream-baseline-2026-08-26.json` is superseded by the generated manifest, or
  regenerated and dated. It records advanced-planning at `v0.16.0`; released is `v0.19.0`.
- `docs/config-seams.md` becomes the reference the routing block cites.
- README / ARCHITECTURE / SETUP describe what was observed, each integration claim citing the
  test that exercised it.

**Gate:** ✓ No document instructs an operator to use an artefact or command that does not exist.
Checked by walking every imperative step in `docs/`.

---

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| The compatibility manifest becomes a check that cannot fail | **High** | **High** | Generated by the suite, never hand-edited; a test induces drift and asserts it is reported |
| The superpowers force-push destroys the pre-port head | Low | **High** | Push the backup tag first; Stage 2 step 3 precedes step 1 |
| Fenced-block rewriting eats user-authored content | Medium | **High** | Byte-identical survival test across install / refresh / uninstall |
| Stage 0 finds most tools have no seam | Medium | Medium | A finding, not a failure: the boundary approach then applies universally and per-tool config leaves scope |
| Two gstack clones diverge | **Observed** | Low | `~/Coding/gstack` is at v1.58.4.0 with no `fork` remote; the install is at v1.60.1.0. Same stale-clone class as the known `M:/Coding/planning/superpowers`. Reconcile or retire in Stage 4 |
| Scope creeps into the Phase 8 registry | Medium | Medium | Non-goal §5, restated at each gate |

## 8. What this does not fix

Pinning makes updates **deliberate**; it does not make them **free**. When upstream superpowers
redesigns its router again, the AAW routing block may still need work — the difference is that it
will be one AAW-owned file with tests, rather than a diff inside somebody else's repository that
nothing checks.

## 9. Coherence check against the programme record

This plan was drafted before its author read the full programme state. The check found three
clashes; all are corrected above.

| Clash | Resolution |
|---|---|
| The draft's Stage 2 proposed building the superpowers boundary that **Phase 5 already built and gated** | Rewritten as an authorisation step. §3 records what Phase 5 delivered |
| The draft claimed the stale patch was unreported | **Wrong.** Phase 5 reported it and fixed it; only publication is blocked |
| The draft implied this work could start now | Authorised execution scope is **phases 3, 4 and 5**. Phases 6–9 are planned and deliberately not decomposed |

Two stale records in `PLANNING.md` were found and corrected in the same pass: the Phases table
showed phase 5 as *current, not started* while the file's own `previous_phase` field and
`phases/phase-5/complete.md` both recorded a PASSED gate, and phase 6 as *planned* while
`current_phase: 6` and 18/30 todos said otherwise. The file also still asserts that no push has
ever been approved for advanced-planning, which ceased to be true on 2026-08-31 when v0.19.0 was
released. Dated corrections were appended in the file's own house style rather than overwriting
the history.

## 10. Sequencing

`PLANNING.md` has `current_phase: 6`, in progress (18/30 todos, not yet gated). Phase 7 is
written but marked "decompose when Phase 6 passes its gate". The authorised execution scope is
phases 3–5.

So the honest position is that **Stages 1, 3 and 4 are Phase 7 work and should wait for Phase 7**,
and only two things have an argument for acting sooner:

1. **Stage 0** — read-only, cannot affect Phase 6, and its result could change the shape of every
   stage after it.
2. **Stage 2** — not a build at all. It is one authorisation on work that already passed a
   three-reviewer gate, and it is the thing that actually makes superpowers a dependency.
