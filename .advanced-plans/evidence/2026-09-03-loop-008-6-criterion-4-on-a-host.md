# loop-008-6 — criterion 4 measured on a real host, and the reason in the shipped prose is now wrong

Date: 2026-09-03
Host: opencode 1.18.27, Qwen3.5 397B via the ELM proxy, herdr agent `host-006`
Fixture: a throwaway consuming project in the session scratchpad, outside both checkouts
Discharges: criterion 4, on a host rather than in a test

## The fixture

Built controller-side and installed the way a consuming project is, not run
against the source checkout — loop-004-4 established that the installer binds a
project to its installing checkout, so a run against the repo proves nothing
about a consumer.

| | |
|---|---|
| installing checkout | `git archive` export of `8cf17b5` (the loop-008-8 fix) |
| installer | `setup/opencode/install.sh --project <fixture>` |
| what it installed | `.agents/skills/` (8 skills incl. the routing skill), `.advanced-plans/bin/ap.py`, `AGENTS.md` |
| baseline | `dd0532360c0eedd961a6e45fb87dee5e3d3cfe58`, taken after the install was committed |

## The verdict

Criterion 4 has a measured pass **and** a measured fail on a non-Claude host,
against an installed copy. Both runs executed the command **read out of the
installed `SKILL.md`**, with only the literal `<loop-base-ref>` placeholder
substituted:

```
python ".advanced-plans/bin/ap.py" evidence_gate loop-complete .advanced-plans/state/loop-complete.json --baseline dd0532360c0eedd961a6e45fb87dee5e3d3cfe58 --no-verdicts-requested
```

| run | committed since baseline | exit | stderr |
|---|---|---|---|
| pass | `src/app.py` | 0 | (empty) |
| fail | `src/app.py`, `.claude/settings.json` | 1 | `path_scope: .claude/settings.json (forbidden)` |

The fail branch carries **two** commits with the forbidden write as the second,
so the multi-commit baseline is exercised rather than assumed.

## The host's own report does not support its own conclusion

The worker concluded that the gate "gives the same verdict when run from a
subdirectory (the path-scope check is keyed from the repo root regardless of
cwd)". That conclusion is **true** — but nothing it ran shows it.

Its subdirectory run was `cd src; python "..\.advanced-plans/bin/ap.py" ...`,
issued in a shell that was **already** in `src`. The `cd` failed with
`Set-Location: Cannot find path ...\fixture-006\src\src`, and the command that
followed therefore ran from the repository root. Its "SUBDIR RUN" is a second
root run. The error is printed in its own transcript, directly above the
conclusion, and it dismissed it as cosmetic. It also silently rewrote the
launcher path rather than running the shipped command as instructed.

This is the second time in two loops that a worker reached a correct conclusion
on evidence that does not reach it. Agreement between the controller and the
host is a prompt to check, never a substitute for checking.

## What the controller measured instead

Three runs, controller-side, reading the same shipped command out of the same
installed `SKILL.md`:

| run | invocation | exit | result |
|---|---|---|---|
| A | shipped command **verbatim**, from `src/` | 2 | `python: can't open file '...\fixture-006\src\.advanced-plans\bin\ap.py'` |
| B | same gate from `src/`, launcher and document resolved to the repo root | 1 | `path_scope: .claude/settings.json (forbidden)` |
| C | the same resolved form from the repo root | 1 | byte-identical to B |

B and C being identical is the proof the worker's conclusion needed and did not
have: **the gate itself is cwd-independent**, which is exactly the property
`8cf17b5` added and what the loop-008-8 round-two class pins. A is a different
failure at a layer above — the shipped command names the launcher by a
repository-root-relative path, so from a subdirectory Python cannot find `ap.py`
and the run dies before the gate is entered.

That failure is loud (exit 2, a file-not-found on stdout) rather than silent, so
it is safe. It is not, however, what the shipped prose says will happen.

## The finding: the fix moved the reason out from under the documentation

`SKILL.md` step 7 does state the precondition, so this is not an undocumented
trap — that is what a first reading suggested and it was wrong. What it gets
wrong is **why**:

> Run it **from the project root**: the path-scope allow-list is derived from
> the working directory's own top-level entries, while git reports
> repository-relative paths, so the same in-scope change reports as a violation
> when the command is run one directory down.

Every clause of that reason is now false. `default_worker_scope(repo_root)`
takes the root as a parameter and the F4 fix passes the resolved value, so the
allow-list is not derived from the working directory; run B proves the same
in-scope change does **not** report as a violation one directory down. The
precondition survives its own justification: it is still real, but now because
of the relative launcher path in the command, not because of anything about
scope derivation.

The adjacent exit-code table is wrong in the same way:

> Exit code `2`: malformed invocation — should not happen with the shipped command.

Run A is the shipped command, unmodified, producing exit 2.

This is the loop-008-8 pattern one layer up. F4 fixed the library and left the
prose describing the failure mode it had just removed, while a new and louder
one took its place at the command layer. Neither the gate's tests nor the
skill's own text can see this; only running the shipped command from a
subdirectory does.

Recorded, not fixed. The correction belongs with whoever next edits the shipped
block, alongside the stale module docstring recorded under loop-008-8.

## The invocation manifest, read off the host's datastore

Not taken from the worker's summary. `~/.local/share/opencode/opencode.db`,
opened read-only, `session` row `ses_f99b87b61ffeMX60gBwF7sb2GI`:

| field | value |
|---|---|
| directory | the fixture path |
| agent | `build` |
| model | `{"id":"Qwen/Qwen3.5-397B-A17B-FP8","providerID":"elm"}` |
| version | `1.18.27` |
| tokens in / out | 1350759 / 2878 |
| cost | 0.0 (ELM proxy, off-quota) |
| messages / parts | 25 / 105 |
| created → updated | 2026-09-03T07:59:18Z → 2026-09-03T08:01:44Z |

The `directory` field is the load-bearing one: it is the host's own record that
the session ran in the fixture, which is what makes "against the installed copy"
a measured claim rather than a stated one. `version` also corrects `CLAUDE.md`,
which still records opencode 1.18.25.

## Fixture state at close

Working tree clean. Two branches, `run-pass` at `1c96fbe` and `run-fail` at
`704546f`. Nothing under `.agents/` or `.advanced-plans/` was touched by any
commit on either branch, which was the load-bearing half of the worker's
FORBIDDEN list and is verified here from `git log --name-only` rather than from
the worker's word. Pane `w2:p2G` retired.
