# loop-003-5 — CI picks the rule up, and CI's description of it is now true

**Todo:** `loop-003-5` (phase-6, ralph-loop-003) — the last of the five.
**Repository:** `advanced-planning`, branch `loop-003-hostneutral`, commits `10ce182` (worker),
`fbc559b` (controller).
**Executed by:** `opencode`, Qwen3.5 397B (ELM), agent `hostneutral`, pane `wS:p1`. One round.
**Outcome asked for:** *"The enforcement is in CI, and CI's own description of it is true."*

**Result:** no workflow change was needed to make the rule run — that half was verified rather than
assumed. A workflow change *was* needed for the second half, because the comment describing the step
was wrong in three ways, one of which predates this loop entirely.

---

## Check 1 — the rule reaches CI with no workflow edit, proven not reasoned

Job 4 runs the audit bare:

```yaml
      - name: Path convention audit (deprecated + host-neutrality)
        run: |
          python -m platforms.python.path_audit
```

Reading that and concluding *"no arguments, so a new rule must be picked up"* is an assumption. The
supporting facts are real — `_build_parser` exposes only `--root` and `--verbose`, so there is no
rule-selection surface a workflow could get out of step with, and the rule list is entirely internal
to the module — but the loop asked for verification, so the CI command was run in the form CI runs
it, with the numeric exit code:

```
python -m platforms.python.path_audit ; echo $?
    PASSED WITH 7 SUPPRESSED -- ... (scanned roots: [7 roots])
    exit=0

append "See the Claude Code host directory at .claude/commands/ for config."
to core/agents/README.md
    VIOLATIONS -- 2 path-convention violation(s) found:
      core/agents/README.md:111: [host-directory (.claude/|.cursor/|.opencode/|.codex/|.agents/|.gemini/)]
    exit=1                            ← caught by a rule that did not exist before 003-2

git checkout -- core/agents/README.md
    exit=0
git status --short
    (empty)
```

I planted in `core/agents/`; the worker planted in `core/skills/`. Both core roots are therefore
covered by an observed red/green transition rather than by one and an inference about the other.

**Two environment questions, asked because a green run on Windows is not evidence about
ubuntu-latest:**

- **Does `core/constraints.json` exist in a fresh checkout?** Yes — `git ls-files` confirms it is
  tracked. This matters because `find_repo_root` walks up from `__file__` looking for that file, and
  its absence returns exit 2, which fails the build for the wrong reason and would look like a
  violation to anyone reading only the exit code.
- **Could a path-separator difference change which files the core-only rules apply to?** No.
  `is_core_root = root_rel.startswith("core/")` compares against entries of `DEFAULT_SCANNED_ROOTS`,
  which are forward-slash string literals, not filesystem paths. The exception lookup is likewise
  normalised with `.as_posix()`. Both are platform-independent by construction, which is why the
  Windows result transfers.

That second question is the one that could have made this todo produce a workflow change. It did not,
but the reason it did not is a property of the code, and it is now written down.

## Check 2 — the comment, wrong in three ways

The worker was asked to find the defects before being shown mine. It found the same three:

1. **Three signatures listed, six rules in force.** The comment predates 003-2.
2. **The scanned-root list did not match `DEFAULT_SCANNED_ROOTS`** — it named six roots; the code has
   seven, omitting `platforms/cowork`. **This was already false before this loop began.** The
   comment describing the check was inaccurate before the new rules made it incomplete, which is
   the same failure mode as the checks this phase keeps finding, expressed in a comment.
3. **No mention of the exception mechanism.** After 003-3 a passing run can print
   `PASSED WITH 7 SUPPRESSED` and exit 0. A reader seeing that in a CI log had nothing in the
   workflow telling them suppressions exist, are printed, or are expected.

The step *name* was also now a partial description — `Audit for deprecated/corrupted path tokens`,
which is what shows in the GitHub Actions UI. The worker changed it to
`Path convention audit (deprecated + host-neutrality)` and gave its reasoning, which is the right
call: the name is the only part of the step most readers ever see.

Its reasoning contained a wrong number — it justified the rename by saying the host-neutrality rules
*"found 26 of the 36 original violations"*. All 36 came from the three new rules (16 + 11 + 9, per
003-2's table). Nothing turns on it; the decision is right regardless. Recorded because the pattern
of a confident figure that was never measured is the through-line of this whole loop.

## The controller edit, and why the replacement was not yet true

`fbc559b`. The rewritten comment cited `docs/path-conventions.md §7.3` as the authority for the
whole audit. In that document §7.3 is the **Host-Neutrality Rule** section; the older rules are
documented separately under **Deprecated Path Tokens**. A reader following the pointer for the
deprecated-token half landed in a section that does not describe them — which is a smaller version
of exactly the defect this todo exists to fix.

It had also **dropped** the root list rather than correcting it. That looks like the safe move — an
enumeration in a comment drifts, and pointing at the doc avoids maintaining it twice — except that
§7.3 names only `core/agents/` and `core/skills/`, so the full seven-root surface would have been
recorded nowhere outside the source. A wrong list was replaced by no list plus a pointer that does
not carry the information.

Both corrected: each half now cites the section that actually documents it, and the root list points
at `DEFAULT_SCANNED_ROOTS` itself, which cannot drift because it is the thing being described.

```
        # Scans the roots in path_audit.DEFAULT_SCANNED_ROOTS for two families of
        # violation: (a) deprecated/corrupted path tokens, everywhere it scans
        # (docs/path-conventions.md, "Deprecated Path Tokens"); (b) host-neutrality
        # under core/ only -- host directories, host-only tool names, host
        # permission syntax (same doc, "Host-Neutrality Rule (§7.3)").
        # Exits non-zero if any violation is found. Known exceptions are keyed by
        # (file, rule), are printed in full with reason and retirement plan, and do
        # not blind that file to other rules; a run with only exceptions prints
        # "PASSED WITH N SUPPRESSED" and exits 0.
```

The `(file, rule)` sentence is doing real work: it is the property 003-3 found had been traded away
silently, and the workflow is where someone adding an exception is most likely to be reading.

## A reported exit code that was not an exit code

The worker's reply gave its runs as `exit=True` and `exit=False`. Those are PowerShell's `$?`, a
boolean, not the numeric status the envelope asked for and not what CI acts on. The direction was
right and the conclusion holds, but it had not seen the number it reported. Every exit code in this
file is one I ran.

Small, and the second time this worker has reported a figure it did not observe — after the
`603 passed, 28 skipped` in 003-2 that never reconciled. The defence is unchanged: run it
controller-side.

## Verification — controller-side

```
git log --oneline -2      fbc559b, 10ce182 on loop-003-hostneutral
git status --short        clean
git diff --stat f35b4a6..HEAD
    .github/workflows/ci.yml | 17 +++++++-------
    1 file changed, 10 insertions(+), 7 deletions(-)
```

**Only `ci.yml` changed across both commits**, which is what makes re-running the full suite
unnecessary rather than skipped: no Python was touched since `f35b4a6`, where it was measured at
`1 failed, 636 passed`. What was re-run:

```
yaml.safe_load(.github/workflows/ci.yml)
    4 jobs parse; job 4's steps intact       ← a comment edit that breaks the YAML breaks every job

python -m platforms.python.path_audit ; echo $?
    exit 0, 7 suppressed

python -m pytest platforms/python/tests/test_path_audit.py -q
    22 passed
```

The YAML parse is the check this todo could actually have failed: an edit inside a workflow file is
one indentation error away from disabling the job it documents, and a disabled job is a green build.

## ralph-loop-003 closes here

Five todos. What exists now that did not before: a host-neutrality rule scoped to `core/`, `core/`
actually host-neutral under it, an exception mechanism that prints what it hides and names what
would retire it, a fixture test proving the command goes red and green on the same tree, and a CI
step whose description matches what it does.

**What the loop found that it was not looking for**, in order:

1. The repository had written down its own Claude-only vocabulary four times, in example `outcome:`
   fields, and nobody had turned it into a check — disproving my own 003-1 record.
2. The first rule detected the English words *Task* and *Agent*: 32 false positives out of 37.
3. Five exceptions had been granted for lines that *forbid* the token they were flagged for,
   trading six words of rewriting for a permanent hole in a `(file, rule)`-keyed allow-list.
4. Two tests asserted nothing, one of which I had recorded in writing as the proof of the exception
   mechanism.
5. The CI comment describing the audit was already wrong before the loop started.

Every one was found by running or reading the thing itself. None would have been found by reading a
worker's reply, and one of them was mine.

## Still open at loop close

- **`core/skills/permission-config/` needs relocating to `platforms/claude-code/skills/`** — its own
  todo. It is the only thing between the audit and a genuinely unsuppressed run, and the seven
  exceptions exist to keep it visible until someone does it.
- **`core/schemas/` and `core/state/` are outside every scanned root.** The success criterion is
  enforced for `core/agents/` and `core/skills/` only. Named in five places across this loop and
  still not scheduled.
- **`PreToolUse`/`PostToolUse`** are Claude-only identifiers absent from the rule's vocabulary.
- **`path_audit.py`'s own `description` string** still reads *"deprecated/corrupted path tokens"* —
  the same staleness just fixed in `ci.yml`, one layer down, and outside this todo's `allowed_paths`.
  It is what `--help` prints.
- The nine `path_audit.py` module defects from 003-1, of which the silently swallowed `OSError` and
  `_is_excluded`'s unanchored substring matching can still make a green run mean nothing. That second
  one now matters more than it did: `DEFAULT_EXCLUDED_SEGMENTS` contains the bare string `docs`, and
  unanchored matching excludes any path merely containing it.
- The branch remains **local**. No push has been approved for `advanced-planning`.
