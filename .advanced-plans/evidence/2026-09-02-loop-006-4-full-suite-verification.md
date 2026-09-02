# Two verifiers, six checks, and a check that could not pass

**Date:** 2026-09-02
**Todo:** `loop-006-4` (phase 6, full-suite verification across everything the phase added,
run from a clean checkout state)
**Repository:** advanced-planning, herdr worktree `loop-005-cursor`, branch `loop-005-cursor`
**Verifiers:** the controller (Claude Opus 5, this session) and **codex `gpt-5.6-sol` effort
high**, dispatched non-interactively via `codex exec` and deliberately kept blind to the
controller's results
**Head under test:** `14da314` — 19 commits unpushed, tree clean
**`allowed_paths`:** literally `["none — verification only"]`. Nothing in the repository was
edited by either verifier. Every finding below is recorded, not fixed.

---

## The outcome, first

Five checks pass. The sixth is red, and the red is in the plan rather than in the code: the
todo asked for a layer pair that **cannot pass in this repository by its own documented
design**, and CI removed that exact pair months ago with a test that fails the build if
anyone puts it back.

| # | Check | Controller | codex-sol | Adjudicated |
|---|---|---|---|---|
| 1 | `pytest platforms/python/tests/` | 1014 passed, 1 skipped, 556.37s | collection error, 0 ran | **PASS** — codex's sandbox, not the repo |
| 2 | `path_audit` | exit 0, 7 suppressed | exit 0, 68 files / 11 roots | **PASS**, non-vacuous |
| 3 | `install_audit --layers source,project` | exit 1, 27 missing | exit 1, 27 missing | **RED — stale check, not a code defect** |
| 4 | `ast_check` | 19 files, 0 violations | same | **PASS** |
| 5 | CI job 2's inline python | exit 0, 6 schemas | exit 0, **plus a blind spot** | **PASS but partially vacuous** |
| 6 | `git status` | clean | clean | **PASS** |

The two verifiers agreed on every number they both produced. Where they disagreed — check 1 —
the disagreement was the finding, and resolving it took a measurement rather than a
preference between two reports.

---

## Check 3: a check that cannot pass

Both verifiers measured the same thing independently:

```
$ python -m platforms.python.install_audit --layers source,project
  Summary: 0 current, 0 stale, 27 missing, 0 source-missing, 0 extra  (total: 27)
  RESULT: drift detected - run /sync-install to refresh stale/missing files
  exit 1
```

Twenty-seven of twenty-seven source files "missing" is not drift, it is a layer that was never
installed — and the repository already knows it. `install_audit.py:449-456` skips a layer whose
directory is absent, with a note. `.claude/settings.json` **is tracked**, so `.claude/` always
exists, the skip never fires, and every source file reads as missing. `.github/workflows/ci.yml`
lines 181-186 record precisely this:

> This replaced `--layers source,project`, which could not pass on a runner: `.claude/settings.json`
> IS tracked, so `.claude/` exists, install_audit's "not found -- skipped" guard never fires, and
> all 27 source files read as missing. Do not "fix" a failure here by dropping the install step
> above — a missing layer is skipped with a note and the job returns 0 having audited nothing.
> `TestCIAuditsALayerItCanActuallyHave` fails the build if either the gitignored layer or the
> uninstalled one comes back.

So the plan's check named a pair that CI has a guard test forbidding. **A check that cannot
pass is the mirror image of a check that cannot fail**, and it is the more dangerous of the
two here, because the obvious way to make it green is to change the code — which would have
broken something real to satisfy a stale line in a plan.

The substantive replacement measurement, taken read-only (the global installer was **not**
run — that would have mutated the operator's real `~/.claude`):

```
$ python -m platforms.python.install_audit --layers source,global
  Summary: 1 current, 26 stale, 0 missing, 0 source-missing, 13 extra  (total: 40)
  exit 1
```

That is a real subject with a real answer: 19 commits sit unpushed and uninstalled, so the
global layer is legitimately behind. The audit had something to look at and said what it saw.
Exit 1 here is information; exit 1 on `source,project` was noise.

### The mtime caveat in the plan was false

The todo's check 3 warned that the audit "compares by mtime" and told the verifier to treat an
invisible drift as a finding. Both verifiers found the warning itself to be the defect.
`install_audit.py:138-160` compares **EOL-normalised SHA-256 content digests**:

```python
return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:40]
```

`grep -n 'mtime' platforms/python/install_audit.py` returns nothing. The comparison is
strictly stronger than the one the plan was worried about. The claim traces to
`docs/adapting-to-new-platforms.md:182`, which still says it — a **carried finding**, not
fixed here.

Cross-model agreement is a prompt to verify, never a substitute for it, so the agreement
between the two verifiers was not what settled this. Reading the source was.

---

## Check 1: two reports, one sandbox

codex reported a **collection error and 0 tests run** while the controller measured 1014
passed. Neither report was wrong, and neither verifier was in a position to say so.

`platforms/python/tests/test_home_resolution_agreement.py:74-79` creates its marker directories
at **module scope**, in the system temp dir:

```python
_MARKER_ROOT = tempfile.mkdtemp(prefix="ap_home_agreement_")
atexit.register(shutil.rmtree, _MARKER_ROOT, True)
...
os.makedirs(_UP_VALUE)
os.makedirs(_HOME_VALUE)
```

That executes at import, i.e. during pytest collection. codex ran under `--approve-for-me`,
which implies the `workspace-write` sandbox; that sandbox denies writes outside the workspace,
including the temp dir. The file therefore failed to import, and a collection error takes the
whole run down with it.

Proven rather than assumed: run that file alone outside a sandbox and it gives **49 passed in
7.80s**.

codex reported what it saw, faithfully and without smoothing it over. Attributing it was the
controller's job, and the general rule this is an instance of is worth stating plainly:
**any sandboxed verifier will report 0 tests run for this suite**, and that number says
something about the sandbox, not about the repository.

---

## Check 5: a pass over ground it never examined

codex flagged that CI job 2 calls `validate({}, schema)` — validating the *empty instance*
against each schema — and asked what that can actually reach. The controller reproduced it
with two controls, importing `minischema` read-only and writing nothing into the repository:

```
case                                           raised?   detail
------------------------------------------------------------------------------
CONTROL: bad type value at TOP level           True      Unrecognised type value: 'strng'
CONTROL: unknown keyword NESTED in properties  True      Unsupported keyword: 'requried' at /properti
SUSPECT: bad type value NESTED in properties   False     no error - schema accepted
SUSPECT: bad type value nested two deep        False     no error - schema accepted
```

Both controls fire, so the probe reached the validator; the suspects do not, so the gap is
real. **`core/state/*.json` could carry `"type": "strng"` inside `properties` and CI job 2
would go green.** The job's own trailing comment claims it catches "unknown keywords (e.g.
'requried' typo) **and invalid type values**" — true at the top level, false one level down.

Two scope facts belong with it: the job globs `core/state/*.json` **only**, never
`core/schemas/`; and the check remains genuinely non-vacuous for what it does cover — six
schema files were found and validated, not zero.

Both are recorded, neither is fixed. This todo's `allowed_paths` is `none`.

---

## Checks 2, 4 and 6

- **`path_audit`** — exit 0, 68 files across 11 scanned roots, 7 suppressions, all of them on
  `core/skills/permission-config/SKILL.md` (the relocation already on the backlog). A pass over
  68 files is a pass over something.
- **`ast_check`** — 19 files checked, 0 violations. `platforms/python/` is still dependency-free.
- **`git status`** — clean. The plan expected `setup-antigravity.js` to appear as untracked;
  it does not, and that is correct: **untracked files are per-working-directory**, and that
  file lives in the main checkout at `C:/Users/mharvey2/Coding/advanced-planning`, not in this
  linked worktree. codex reported the absence rather than quietly matching the plan, which is
  the behaviour wanted.

---

## The instrument, before the subject

The controller's runner (`verify_064.py`) uses `subprocess.run` with a list argv, no shell and
no pipes anywhere — F25 is a piped command reporting the *pipe's* exit code, which has told
this programme "exit 0" over a real failure three times. Before any subject check ran, the
runner was made to prove it can see a red at all:

```
instrument control OK: runner sees exit 7 as 7 and exit 0 as 0
```

A harness that reports PASS unconditionally is indistinguishable from six passing checks. This
is the seventh instance in the programme of a positive control being what separates an
instrument fault from a subject fault, and check 1 above is the eighth: without re-running the
failing file outside a sandbox, "codex says 0 tests, I say 1014" is an unresolvable
disagreement between two confident reports.

---

## Disclosure: the codex boundary

codex was **not** a disinterested verifier here, and was told so in its own envelope. codex
(`gpt-5.6-luna`, effort high) authored `14da314` earlier in this phase — the commit that wired
`evidence_gate.py` into `next-loop.md` at step 7a and added the test pinning it.

The operator was shown this on 2026-09-01 and chose to keep codex-sol as the verifier, on the
ground that `14da314` had already been independently verified by the controller during
loop-006-3. So the todo's outcome clause — "by a provider that implemented none of it" — is
**not satisfied as written**, and this is the record of that. In practice codex judged 18
commits it did not touch and one it did, and none of its findings above bear on `14da314`:
check 3 concerns `install_audit` and `ci.yml`, check 5 concerns `minischema` and the CI job,
check 1 concerns its own sandbox.

Recording the unsatisfied clause was the operator's explicit instruction, chosen over rotating
to a different provider.

---

## What changed in the plan

Nothing in the repository under test. In `.advanced-plans/phases/phase-6/loops.md`,
loop-006-4 gained a `rewritten:` field on the loop-006-5 precedent, and three checks were
corrected:

- **check 3** now names `--layers source,global`, the pair CI actually runs, and states that
  drift against the global layer is expected while commits sit unpushed — what is verified is
  that the audit had a subject, not that the number is zero. The mtime caveat is gone.
- **check 5** now requires the scope to be *reported* rather than assumed.
- **check 6** now states the linked-worktree expectation: fully clean.

---

## Postscript: the controller wrote a check that could not fail

While recording this result, the script that advances `PLANNING.md` corrupted the file it
was guarding, and its own assertion passed anyway. Worth recording, because it is the
phase's subject matter turned on the phase's own tooling.

The updater read the file with `read_bytes().decode()` -- which does **not** translate line
endings, so the text still held `
` -- and wrote it back with `newline="
"`, which
translates every `
`. Every line ending became `
`. Both halves are individually
correct; the combination doubles the carriage return.

The guard was:

```python
assert after.count(b"
") == 133 and after.count(b"
") == 133
```

A file of 133 `
` lines has exactly 133 `
` and 133 `
` -- the same counts as a
clean CRLF file. **The assertion could not tell the defect from the correct state**, so it
reported success over a corrupted write. What caught it was not the guard but `git diff
--cached --numstat` reporting 133 changed lines where five were expected; `--ignore-all-space`
then showed 5, and a byte comparison against the committed blob named the five.

The distinguishing measurement is CR **total**, not CRLF count: 266 against a 133-line file.
The file was repaired in place (77457 -> 77324 bytes) and the staged blob is clean LF, matching
the repository's `* text=auto` normalisation.

Two things follow for the programme's own scripts: a line-ending assertion must count CR total,
and a script that reads bytes to measure endings must write bytes too, rather than mixing a
byte read with a newline-translating write.

---

## Carried findings

1. `docs/adapting-to-new-platforms.md:182` still says `install_audit` "compares by mtime". It
   compares SHA-256 digests.
2. CI job 2 cannot see an invalid `type` value nested inside `properties`, and its own comment
   claims it can.
3. CI job 2 scans `core/state/` only; `core/schemas/` is validated by nothing in CI.
4. A sandboxed verifier cannot run `test_home_resolution_agreement.py` at all — it fails at
   collection, taking the whole suite with it. Worth a note in the file itself.
