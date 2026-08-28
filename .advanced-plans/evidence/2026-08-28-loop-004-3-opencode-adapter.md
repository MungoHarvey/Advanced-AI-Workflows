# loop-004-3 — the OpenCode adapter, derived not re-authored

- **Date:** 2026-08-28
- **Repository:** `advanced-planning` (LOCAL ONLY — no push has ever been approved)
- **Branch:** `loop-004-opencode`, based on `loop-004-codex`
- **Worker:** `ocadapter`, opencode / Qwen3.5 397B via the ELM proxy, pane `wV:p1`
- **Commits:** `3a95f1e` (worker), `b458a51` (controller repairs — final)
- **Status:** complete

## The instruction that shaped the loop

The Codex adapter is 1,752 lines of which only ~65 mention Codex. Everything else —
the ownership registry, the AGENTS.md fence handling, the runtime manifest, the
two-phase uninstall — is host-neutral logic that took **four rounds of repair** to
get right. The envelope therefore told the worker to `cp` the four scripts and edit
what is genuinely host-specific, rather than re-author them.

It complied. Measured divergence against the Codex originals:

| file | codex lines | differing | of which host-naming | non-host |
|---|---|---|---|---|
| `install.sh` | 607 | 48 | 48 | 0 |
| `install.ps1` | 507 | 41 | 37 | **4** |
| `uninstall.sh` | 350 | 20 | 20 | 0 |
| `uninstall.ps1` | 288 | 22 | 22 | 0 |

131 differing lines out of 1,752, and every one is host-naming except four in
`install.ps1`. Of those four, three are added comments and one is a real defect: the
header comment became *"PowerShell equivalent of install.ps1"* — of itself. Codex's
reads `install.sh`. Fixed controller-side.

The four rounds of ownership fixes were inherited rather than re-earned, which was
the entire point of deriving.

## The worker did not run its own proofs, and said so

The envelope asked for nine numbered proofs. The worker returned the code and then
stated the remaining work was *"running the installation and verifying the nine
proofs in a scratch project"* — it ran none of them. Its PATH has neither `sh` nor
`pwsh`, so it could not have run the suite honestly.

**It did not claim a pass it could not produce.** That is the outcome the envelope
asked for and it is worth recording as a success of the envelope, not a failure of
the worker. Every proof below is therefore controller-side.

## Controller verification

### Ownership — 41 checks, both orientations

`verify-ownership.sh`, parametrised over adapters, run against the same tree twice:

- `codex` as adapter / `opencode` as foreign owner — **41 PASS, 0 FAIL**
- `opencode` as adapter / `codex` as foreign owner — **41 PASS, 0 FAIL**

Both runs ended with the source-tree fingerprint unchanged, so no worker was editing
underneath the run.

### Collision — 20 checks, the loop-004-1 decision exercised for the first time

`verify-collision.sh` was written *before* the OpenCode adapter existed and validated
against a synthetic adapter, so it cannot have been shaped to fit what the worker
produced. **20 PASS, 0 FAIL:**

- both install orders produce one identical skill tree — 35 paths, and the 8
  `SKILL.md` files are digest-equal between the two orders, so "identical" means
  content and not merely names;
- `advanced-planning` is owned by `["codex","opencode"]` under either order;
- both fences coexist in one `AGENTS.md` with distinct markers and the user's content
  intact;
- uninstalling OpenCode leaves the shared skill present, the registry rewritten to
  `["codex"]`, the Codex fence untouched, the OpenCode fence gone, state intact;
- a **second** uninstall of the already-removed adapter removes nothing more.

That last one is the case four rounds of stage-D repair were about.

### No fork

All eight installed skills are digest-equal to their sources — seven to
`core/skills/`, and `advanced-planning` to `platforms/shared/`. `companion-detection`
and `permission-config` are absent, as specified. No OpenCode copy of the shared skill
exists and no second `state_validate.py` was written.

### Contract 6

With `PYTHONPATH` unset, run from the installed project rather than the checkout:

```
python .advanced-plans/bin/ap.py state_validate loop-ready real-loop-ready.json
exit=0            (measured without a pipe)
```

No bare `-m`, no `sys.path.insert` in the invocation. The `sys.path.insert` calls
inside `ap.py` itself are the launcher doing its job — that is the mechanism, not a
violation of it.

The runtime manifest records `"written_by": "setup/opencode/install.sh"`, so the
host-specific field is host-specific.

### `opencode.json`

The adapter does not reference or create one, and none appeared in an installed
project. Per §7.2 that file is touched only for plugins, permissions, or extra
instructions; skills go to `.agents/skills/` and guidance to the AGENTS.md fence. The
envelope flagged "do nothing" as probably the right answer and it was.

## Three instruments were wrong before any verdict was reached

This loop found more defects in the checking apparatus than in the thing checked.

### 1. My ownership harness — four bugs, one of them vacuous for four rounds

The first run against OpenCode reported **6 FAILs**. All six were mine.

- Two sites still planted or expected the literal `opencode` where they meant "the
  *other* owner", so swapping the adapter inverted them.
- The planted foreign entry was named and owned `opencode`, which stops being foreign
  the moment OpenCode is the adapter under test.
- **The fence check could not fail.** It read
  `grep -c 'advanced-planning:$ADAPTER'` in **single quotes**, so `$ADAPTER` was never
  expanded and it searched for a literal that cannot occur. It returned `0` and passed
  unconditionally — including through all four rounds of the Codex loop.

Proven by discrimination: with both fences present in `AGENTS.md`, the old form reads
`0` and the repaired form reads `2`; after uninstall the repaired form reads `0`.

Had these been reported before being chased, this loop would have opened with six
phantom adapter defects.

### 2. The tracked suite — five tests that became wrong the day OpenCode existed

The full run came back **11 failed, 743 passed**: ten adapter-lifecycle failures, all
`[opencode]`, plus the known pre-existing `test_self_heal_integration.py` failure on
its own hard-coded absolute path.

My harness said the adapter passed those same five properties. One instrument had to
be wrong, so the assertions were read rather than adjudicated from the counts:

```
_set_owners(project, "advanced-planning", ["opencode"])        # "pre-seed a FOREIGN owner"
assert sorted(owners) == ["codex", "opencode"]
```

The suite seeded a **sibling adapter** as its foreign owner and hard-coded the merged
expectation. That was correct when Codex was the only adapter. It became false the
moment OpenCode became the adapter under test: the seed is no longer foreign and the
expectation names an adapter that was never installed.

**These are test defects, not adapter defects** — the identical bug class to the one
in my own harness, found in the same hour.

Repaired by introducing a foreign owner that is deliberately not, and never will be,
an adapter name (`_FOREIGN = "otherhost"`), so the property stays true however many
adapters exist. All 17 hard-coded sites were converted; the only adapter literals
remaining in the file are the `_ADAPTERS` tuples themselves.

Result: **74 passed** (37 cases × 2 adapters), and the full suite is **753 passed,
1 failed** — up from 743, exactly the ten recovered cases. The single remaining
failure is the pre-existing `test_self_heal_integration.py` one, which fails on `main`
too and is untouched here.

Proven load-bearing rather than merely green — the D1 registry clobber was
reintroduced into `setup/opencode/install.sh` and the repaired A.1 caught it:

- clobber applied, 1 substitution — `1 failed, 7 passed`
- reverted — `8 passed`

The first attempt at that probe reported **0 substitutions**: the block sits at four
spaces of indentation, not eight. It printed its count, so it was caught rather than
being read as a silent pass. This is the fourth time this phase that printing the
substitution count has saved a mutation from being vacuous.

### 3. `path_audit` reported PASSED without looking at the new adapter

`DEFAULT_SCANNED_ROOTS` names `setup/codex` and did not name `setup/opencode`. The
entire new adapter — 1,755 lines across four scripts, all of them collectable `.sh`
and `.ps1` files — sat outside every scanned root, so the audit's `PASSED WITH 7
SUPPRESSED` was a statement about code it had never read.

Added the root. The audit still passes with the same 7 suppressions, so the adapter is
genuinely clean — but it is now clean *because it was checked*.

Proven load-bearing: a `.advanced-.advanced-` violation planted in
`setup/opencode/install.sh` gives `exit=1` naming the file and line; reverting gives
`exit=0`. Before the one-line addition that same violation was reported as a pass.

## A correction I owe the record

The loop-004-3 envelope said the suite *"was parametrised over adapters specifically
so that adding OpenCode is one tuple"*, and told the worker the change was
**append-only**: add the tuple, alter no existing test, and if a test fails, fix the
adapter rather than the test.

**That was wrong, and it was wrong twice.** Three assertions still hard-coded `codex`
despite the file being nominally parametrised — the worker had to de-hardcode them to
add the tuple at all, and its changes do exactly that with no assertion weakened
(`== ["codex"]` became `== [name]`; the `count == 1` and fence-count assertions are
structurally identical). Five further sites hard-coded the *fixture seeds and merged
expectations*, which the worker did not reach.

So the append-only constraint forbade the only correct fix. A worker that obeyed it
literally would have had to fail or fake the result. The instruction should have been
"parametrise whatever is still adapter-coupled, and change no assertion's meaning".

The earlier claim, recorded in the coverage evidence, that adding an adapter is "one
tuple" is withdrawn. It was one tuple plus twenty adapter-coupled sites — three the worker
had to de-hardcode to add the tuple at all, and seventeen fixture seeds and expectations
it could not reach.

## Carried

- **Property 2 still has no mutation coverage.** The clobber mutation only visits
  *approved* skills, and the foreign entry is deliberately not approved, so this
  mutation cannot reach it. Unchanged from the previous sweep, and now confirmed to
  survive the `_FOREIGN` rewrite for the same reason.
- The adapter-parametrised suite is still not wired into CI as a gate.
- `test_self_heal_integration.py:586` still fails on its own hard-coded absolute path
  `C:/Users/mharvey2/Documents/Coding/advanced-planning`. Pre-existing, unrelated,
  untouched.
- `setup/claude-code/` is still outside `DEFAULT_SCANNED_ROOTS`, the same gap that
  `setup/opencode/` had. Not fixed here because it was not in this loop's scope.

## The thing this loop is actually about

The adapter was the easy half: 131 host-specific lines, derived, and it passed every
functional check it was given on the first run.

The hard half was that **three separate checking instruments were reporting green over
ground they were not examining**, and two of them had been doing so for four rounds.
The pattern is now specific enough to state as a rule: the failure lives where a check
**interpolates or parses a string** rather than reading the filesystem or comparing
parsed JSON to a literal. The single-quoted `$ADAPTER`, the `parts[i-1]` count parse,
and the hard-coded sibling-adapter seed are the same defect wearing three coats.
