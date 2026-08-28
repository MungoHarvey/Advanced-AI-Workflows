# loop-002-1 — where the two run-contract schemas live

**Todo:** `loop-002-1` (phase-6, ralph-loop-002). Read-only; `allowed_paths: ["none — read-only"]`.
**Deliverable asked for:** *"A short note stating the chosen location and form for each of the two
schemas, the reason, and the ci.yml change required."*
**Outcome asked for:** *"The two schemas join an existing convention instead of founding a third one."*
**Reviewed by:** codex `gpt-5.6-terra` medium, `codex exec -s read-only`, independent envelope.

---

## The decision

Both go to `core/state/`, as draft-07 JSON Schema, named for the artefact:

| Artefact | File |
|---|---|
| Immutable external task envelope (design §9.2) | `core/state/external-task-envelope.schema.json` |
| Collected evidence contract (design §9.3) | `core/state/collected-evidence.schema.json` |

Naming follows the repository's own terms — `plan.md:48–49` and the `loop-002-3` todo both say
**"collected evidence"**. An earlier draft of this note said "collected result"; that phrasing
entered through the review envelope, not from the repository, and is corrected here.

`loop-002-2` and `loop-002-3` both carry `allowed_paths: ["core/schemas/", "core/state/", "docs/"]`
— all three locations are open to them. This note is what narrows that to one.

## The reason

The organising principle is **not** prose-vs-JSON, and not mutability.

- `core/schemas/*.schema.md` specifies formats of **planning documents a human or agent authors** —
  `handoff`, `phase-plan`, `ralph-loop`, `todo`. These are markdown-with-frontmatter, so there is
  nothing a JSON validator could run against; prose is the only available form.
- `core/state/*.schema.json` specifies **contracts exchanged at a process boundary** —
  `loop-ready` (orchestrator→worker), `loop-complete` (worker→main thread), `gate-verdict`,
  `gate-failure-context`. `core/state/README.md` is titled *"State Bus Protocol"* and its Files
  table carries *Written By* / *Read By* columns naming orchestrator, worker and main thread.

Mutability is **not** the line: `gate-verdict` is an immutable record and lives in `core/state/`
regardless. Format follows role.

Both new artefacts are boundary contracts of exactly that kind. The envelope is validated by the
controller *before dispatch*; the collected evidence is validated *before it advances any state*.
Neither is a document a planner writes. They are the same species as `loop-ready` and
`loop-complete`, one level up — controller/worker rather than orchestrator/worker.

A supporting detail neither README states: **a prose spec may delegate its machine-checkable part
to a JSON Schema in `core/state/`.** `core/schemas/ralph-loop.schema.md:133` — *"See
`core/state/gate-failure-context.schema.json` for the full JSON Schema"* — and
`core/schemas/todo.schema.md:104` references `core/state/loop-ready.schema.json`. The reverse never
happens: no `core/state/*.json` points back at a prose file.

That settles whether the two new schemas need prose companions. **They do not.** Neither appears
inside any authored document, so there is nothing for a `core/schemas/` entry to describe that the
JSON Schema's own `description` fields cannot carry. If one is ever wanted, the established pattern
is a prose file that *points at* the JSON, not one that duplicates it.

## The ci.yml change required

**Nothing.**

Job 2 (`schema-validation`, `.github/workflows/ci.yml:43–49`) selects `core/state` and globs
`*.json`. Two new files in that directory are picked up with no edit at all.

This is a positive argument for the location rather than a convenience: the alternative directory
is **not covered by any glob**, so a schema placed there would be validated by nothing.

### But that job's check is not sufficient — and that is a finding, not a caveat

`ci.yml:50–58` performs `json.loads()` and nothing else. It proves the file *parses as JSON*. It
does not prove the file is a valid JSON Schema, and it never loads a fixture.

Two defect classes ship today. Both were **run**, not asserted — job 2's exact logic, against:

1. **A typo'd keyword.** `{"requried": ["run_id"]}` → no errors reported. The constraint silently
   does not exist.
2. **A non-schema object.** `{"hello": "world"}` → no errors reported.

Codex independently named the same class with a different example (`"type": "objekt"`).

Class 1 is the one that matters for this loop. `loop-002-4` requires ≥5 invalid fixtures *"each
failing for a different named reason"* — and a typo'd keyword makes every one of those assertions
vacuous while the suite still reports green.

**So `loop-002-5`'s real work is strengthening the check, not extending the glob.** Its stated
outcome — *"a malformed schema stops the build instead of shipping"* — is currently only half true,
and that is a defect in the existing job, independent of these two new files.

## The plan is half wrong, and should be corrected

`plan.md:48–49` gives the deliverable location as:

```
| External task envelope     | JSON Schema | advanced-planning: core/schemas/ |
| Collected evidence schema  | JSON Schema | advanced-planning: core/schemas/ |
```

**"JSON Schema" is right. `core/schemas/` is wrong.** It would put a `.json` file in the directory
that holds only prose specifications — founding exactly the third convention this todo exists to
prevent — and would place it outside the only glob that validates schemas.

Recorded here rather than silently ignored: `loop-002-2` and `loop-002-3` must write to
`core/state/`, and the plan's table should be amended to match.

## The third location: `docs/` is a real convention, and the controller was wrong about it

`docs/` holds `phase-complete.schema.md`, `phase-handoff.schema.md`, `phase-manifest-entry.schema.md`.

The controller's independent answer, written before the review, called this **drift** — the
`core/schemas/` convention misfiled. **That was wrong.** Codex called it a deliberate third,
feature-scoped convention, and brought the load-bearing fact, which was then verified directly:

**All three carry `> **Status: LOCKED** (date). Changes require an explicit decision logged in
CLAUDE.md.` None of the four `core/schemas/*.schema.md` carries any status marker at all.**
`Status: LOCKED` appears in exactly four files repo-wide: those three and `CLAUDE.md`. 3/3 against
0/4 is a shared property, not an accident of filing.

The distinction is real and load-bearing: these three specify **compaction artefacts whose format
is frozen**, because a reader resuming a phase must parse an artefact written by a much older
version of the framework. `core/schemas/` formats evolve with the planner; these cannot.

What the controller *did* get right is the index gap — but it misread its cause:

- `core/schemas/README.md:18–25` heads a section **"Compaction Schemas (`docs/`)"** and indexes only
  `phase-complete` and `phase-manifest-entry`.
- `CLAUDE.md:76` likewise opens *"**Two** locked schema documents govern the compaction artefacts…"*
  and lists the same two.
- Yet `docs/phase-handoff.schema.md` is itself **LOCKED 2026-05-19**, and CLAUDE.md's own decision
  log immediately below records the 2026-05-19 reframing that *"Adds per-phase `handoff.md` resume
  digest"*.

So the omission is a **stale count of "two"**, written 2026-05-13 and never updated when the third
arrived six days later — duplicated into a second index. It is not evidence that `docs/` is
unprincipled. Worth fixing (`core/skills/schema-design/SKILL.md:3` names `phase-handoff.schema.md`
as the *style exemplar* every new schema document should mirror, and
`platforms/claude-code/commands/phase-compact.md:320` requires conformance to it), but it is a
one-line documentation defect in advanced-planning, not a finding about where the new schemas go.

**Consequence for this todo: there are genuinely three conventions, and the two new schemas belong
to `core/state/`.** Not `docs/` — neither is a compaction artefact, and neither is LOCKED; both will
evolve as the controller does. The stated outcome holds: they join an existing convention rather
than founding a fourth.

## Review record

The controller's answer was written in full **before** codex's was read, including a recorded
prediction of where the two would disagree. That ordering is what makes the agreement below worth
anything.

| | Controller (pre-review) | codex | Outcome |
|---|---|---|---|
| Q1 principle | authorship — who writes the artefact | role — contracts at a process boundary | **Agree** on rejecting prose-vs-JSON; codex adds that mutability is not the line either (`gate-verdict` is immutable and still `core/state/`) |
| Q2 `docs/` | drift, misfiled `core/schemas/` | deliberate third convention | **codex right, controller wrong** — settled by the LOCKED marker, verified 3/3 vs 0/4 |
| Q3 location | `core/state/` | `core/state/` | Agree |
| Q3 form | JSON Schema | draft-07 JSON Schema | Agree |
| Q3 ci.yml | nothing | nothing | Agree |
| Q3 sufficiency | insufficient — typo'd keyword, run and observed | insufficient — `"type": "objekt"` | Agree, arrived at independently |
| The plan | "wrong" | "half wrong — form right, directory wrong" | **codex's phrasing adopted**; it is the more precise reading |
| Envelope filename | `task-envelope` | `external-task-envelope` | **codex right** — matches `plan.md:48` |
| Evidence filename | — | `collected-result` | **Both wrong** — the repository says `collected evidence` (`plan.md:49`, `loop-002-3`); "result" came from the review envelope |

Predictions logged before reading: agreement on location (**held**); codex might claim the glob
needs extending (**did not** — it agreed no change is needed); Q2 flagged as least confident
(**and that is precisely where the controller was wrong**).

## Carried to loop-002-3, not settled here

Design **§9.3's worked example sets `"status": "review_required"`**, while **§10's lifecycle names
that state `Review`**. `loop-002-3`'s check requires the status enumeration to be *"drawn from the
§10 lifecycle"*, so the two cannot both stand. §10's full set: Declared, Prepared, Running, Blocked,
Review, Completed, Failed, Interrupted, Cancelled.

This is a decision about the design document, not only about the schema, and belongs to `002-3`.

## Checked after the review, because neither side had done it

**Is any filename already constrained by a consumer?** No. A search of `*.py`, `*.yml`, `*.json`,
`*.sh` and `*.ps1` outside `.advanced-plans/` for `task.envelope`, `external.task`,
`collected.evidence` and `collected.result` returns **nothing**. No code reads either artefact yet,
so the names above are free and are chosen to match the plan's own wording rather than to fit an
existing caller.

**One further observation on job 2**, from reading it rather than inferring it: it globs `*.json`,
not `*.schema.json`, and its `except` catches `json.JSONDecodeError` alone. Today `core/state/`
holds only schemas — the *runtime* state files live in `.advanced-plans/state/` — so the loose glob
is harmless now. It stops being harmless the moment `loop-002-4` adds fixtures, since a fixture
placed in `core/state/` would be silently counted as a validated schema. Another input to
`loop-002-5`: fixtures belong under `platforms/python/tests/`, which `loop-002-4`'s
`allowed_paths` already requires.
