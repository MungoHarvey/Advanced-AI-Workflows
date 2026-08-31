# Multi-model code review — compiled

**Target:** whole files: platforms/python/ap_launcher.py platforms/python/install_audit.py platforms/python/path_audit.py platforms/python/ast_check.py platforms/python/state_validate.py platforms/python/minischema.py platforms/python/versioning.py platforms/python/history_log.py  
**Repo:** `/c/Users/mharvey2/Coding/advanced-planning`  
**Run:** 20260831-142809  
**Diff size:** 95865 bytes

## Reviewers

| Reviewer | Status | Critical | Important | Minor | Verdict |
|---|---|---|---|---|---|
| `claude` | ok | 5 | 17 | 5 | **No** |
| `cursor` | ok | 3 | 8 | 2 | **With Fixes** |
| `opencode` | ok | 4 | 5 | 4 | **With Fixes** |

> **The reviewers disagree on the verdict** — `claude` says *No*, `cursor` says *With Fixes*, `opencode` says *With Fixes*. Read the disagreement before the consensus; it is usually the more informative half.

## Consensus findings (1)

*Raised independently by more than one model. Weight these highest.*

### C1. install_audit exits 0 when there is nothing to compare
*Raised by `claude`, `cursor`*  ⚠ **severity disagreement:** `claude`=Important, `cursor`=Critical

<details><summary><code>claude</code> (Important)</summary>

- **`install_audit` exits 0 when there is nothing to compare** — `platforms/python/install_audit.py:453`
  What: `if not results: print("NOTE: no layer pairs found to compare — nothing to audit"); return 0`. Verified: `--root /tmp/nonexistent --layers source,project` → exit 0.
  Why: `/sync-install --check` in a project that was never installed reports success. `TestCIAuditsALayerItCanActuallyHave` protects the CI invocation specifically, not the module contract, so any other caller inherits the false green.
  Fix: return 2 when a layer explicitly requested by `--layers` is absent; keep exit 0 only for `all` when at least one pair was audited.

</details>

<details><summary><code>cursor</code> (Critical)</summary>

- **`install_audit` exits 0 when it compared nothing** — `platforms/python/install_audit.py:453`
  What: After skipping a missing project `.claude/` and/or global `~/.claude/` (guards at 432 and 443 that test directory presence, not `commands|agents|schemas`), `if not results: ... return 0`. `audit_pair` also `continue`s when a source surface dir is absent (234–236), so a wrong `--root` with an empty `.claude` yields zero verdicts, `has_drift` is false, and the CLI prints `RESULT: all layers current`.
  Why: An operator or a workflow that forgot `--global` install, pointed `--root` at the wrong tree, or lost `platforms/claude-code/commands` still gets exit 0. That is a check whose subject is “we did not raise,” not “these files match.” `/sync-install` then says nothing to do.
  Fix: Return 2 (or 1) when a requested layer pair produced no file verdicts, or when every `SURFACES` source dir was missing. Require the installed layer to contain at least one audited surface, not merely `.claude/`. Print which pair was skipped and that the run is inconclusive.

</details>

## Single-reviewer findings (51)

*One model saw it and the others did not — either a real blind spot in the others, or a false positive. Adjudicate individually.*

### Critical

- **install_audit cannot see the one file every installer copies out — the launcher** — `claude` only
    What: `SURFACES` covers `commands`, `agents`, `schemas` only. Seven installers copy `platforms/python/ap_launcher.py` to `<project>/.advanced-plans/bin/ap.py` (`setup/claude-code/install.sh:246,449`, `setup/codex/install.sh:235,548`, `setup/opencode/install.sh:235,548`, the three `.ps1` twins, `platforms/claude-code/install.sh:132,219`). Nothing compares that copy against source. `.claude/skills/` is likewise unaudited even though `install.sh:302-306` *copies* skills when `--symlink` is not passed.
    Why: fix a bug in `ap_launcher.py`, run `/sync-install`, and the audit prints `RESULT: all layers current` while every installed project keeps executing the old launcher. This is the highest-value drift target in the release — it is executable code shipped standalone — and it is the one surface the drift auditor is structurally blind to. CI job 5 inherits the blindness.
    Fix: add `("platforms/python", "…")` as a special-cased single-file surface mapping `ap_launcher.py → .advanced-plans/bin/ap.py` (installed base is `.advanced-plans`, not `.claude`, so `audit_pair` needs a per-surface installed root), and add `("core/skills", "skills")` skipping the comparison when the installed path is a symlink.

- **create_retry_version silently overwrites an in-progress retry file** — `claude` only
    What: `dest.write_text(source.read_text(...))` with no existence check, no backup, no guard. The function is documented as "Create a versioned copy"; it is in fact an unconditional overwrite.
    Why: `/next-phase` on a second gate failure calls `create_retry_version(loops.md, attempt_number=2)` again. `freeze_loop_file` has by then already rewritten the *source* file's todos to `status: frozen` (`versioning.py:243`), so the second call copies the frozen original over `loops-v2.md` — destroying every todo the retry worker completed and replacing their statuses with `frozen`. Non-idempotent, unrecoverable, and the caller has no way to detect it happened.
    Fix: raise `FileExistsError` when `dest.exists()` and the content differs, or take an explicit `overwrite: bool = False`. Return the existing path unchanged when the content is identical, so a genuine re-run stays idempotent.

- **get_active_version returns the wrong answer for every real input** — `claude` only
    What: `_TABLE_ROW_RE` assumes a table shaped `| phase | loop_file | …`. The real `.advanced-plans/PLANS-INDEX.md:17` is `| Phase | Name | File | Status | Loops | Outcome |`, and the phase cell holds `1`, not `phase-1`. I ran it: `get_active_version(".advanced-plans/PLANS-INDEX.md", phase="phase-1")` → `None`; `phase="1"` → `'Core Architecture Design'` — the **Name** column.
    Why: silent `None`, no exception, so a caller reads "no versioned retry exists" and proceeds against the wrong file. `CLAUDE.md:68` and `docs/gate-review-architecture.md:307` both present this as the API backing `/next-phase`'s retry logic. It survives because `test_versioning.py:274-310` only ever feeds it a synthetic fixture in the shape the regex expects — a test that verifies the mock, not the artefact. (Blast radius today is limited: I found no *code* caller, only docs and plan artefacts.)
    Fix: parse the header row to locate the `File`/`Active File` column by name instead of by position, normalise `phase` to accept both `2` and `phase-2`, and replace the synthetic fixture with a test that reads the repository's own `PLANS-INDEX.md`.

- **path_audit excludes every file when the checkout path happens to contain "docs"** — `claude` only
    What: `_is_excluded` does a bare substring test (`seg in posix`) against `file_path.as_posix()`, which in `audit()` is an **absolute** path (`root_abs.rglob("*")`, `path_audit.py:326`). Verified: `_is_excluded(Path('/home/ci/docs-build/advanced-planning/core/skills/x/SKILL.md'), DEFAULT_EXCLUDED_SEGMENTS)` → `True`.
    Why: clone the repo under any directory whose path contains `docs` (`~/docs/`, `/srv/docs-build/`, a CI workspace named `docs`) and the audit scans zero files, prints `CLEAN -- path-convention audit passed`, and exits 0. CI job 4 goes green having checked nothing. The same substring test silently drops a legitimately-named `core/skills/api-docs/SKILL.md` today.
    Fix: compute `rel = f.relative_to(repo_root).as_posix()` and match on path *segments* (`rel.split("/")`) or a `rel.startswith(seg + "/")` prefix test. Separately, fail the run when zero files were scanned — see the recommendation below.

- **ast_check exits 0 when it checked nothing** — `claude` only
    What: `if not all_files: print("No .py files found to check."); return 0`. `_collect_py_files` (`ast_check.py:183`) demotes a bad path to a stderr `WARN` and drops it. Verified: `python -m platforms.python.ast_check platforms/pythn/` → `WARN … skipped` / `No .py files found to check.` / **exit 0**.
    Why: CI's only zero-dependency enforcement is `ast_check platforms/python/ --exclude tests/ --exclude examples/`. Rename or restructure that directory, typo the path in a workflow edit, and the check passes forever while external imports land freely. The exclusion logic compounds it: `ast_check.py:244` matches a pattern against any part of the **absolute** path, so a checkout under a directory named `tests` excludes every file and reaches the same exit 0.
    Fix: return 2 with an explicit error when the resolved file set is empty, and return 2 (not a warning) for a path argument that does not exist. Match `--exclude` against the path relative to cwd, not the absolute path.

- **path_audit reports CLEAN for roots it never opened** — `cursor` only
    What: Missing scan roots are `continue`d with no counter. Success text at 429–431 interpolates `DEFAULT_SCANNED_ROOTS` regardless of what existed. `--verbose` is parsed (387) and never used, so there is no “files actually read” line.
    Why: Rename `core/skills` → `core/skill`, drop `.claude/commands` from the checkout, or run `--root` at an empty tree: zero files, `CLEAN -- path-convention audit passed (scanned roots: [...])`, exit 0. The printed list is a constant, not a fact from disk — the same defect class as interpolating a path then “checking” it.
    Fix: Count files opened per root. Exit 2 if a configured root is missing (except a documented optional set). Print the roots and file counts that were actually scanned. Wire `--verbose` or delete the flag.

- **inject_failure_context always “succeeds” with empty context** — `cursor` only
    What: Sidecar fields are filled with `.get(..., default)` (`attempt` 1, strings `""`, lists `[]`). A real gate-verdict uses `loops_to_revert` (list of strings) and `failure_notes`, not `loops_reverted` / `do_not_repeat` / `summary`. `next-phase.md` passes `verdict=verdict_dict` as that failing verdict. The write still returns a path.
    Why: On gate fail, workers read `retry-context.json` that looks valid and contains no loops and no `do_not_repeat`. Remediation runs blind while the operator believes context was injected. Tests only pass a pre-shaped `_SAMPLE_VERDICT`, so they cannot fail this.
    Fix: Require the gate-failure-context keys (or map from gate-verdict explicitly). Reject/empty-check before write. Validate with `state_validate` against `gate-failure-context`. Change `/next-phase` to pass the mapped dict, not the raw verdict.

- **ap_launcher.py reads manifest before checking it exists** — `opencode` only
    What: After `sibling_manifest()` and `global_manifest()`, the code does `if manifest is not None:` and immediately reads the file. But `global_manifest()` returns a *path string* constructed from `global_home()`, not a verified file path. The `os.path.isfile()` check happens at line 298, but only in the `if manifest is None` branch. If `sibling_manifest()` returns `None` and `global_manifest()` returns a path to a non-existent file, line 302 raises `FileNotFoundError` instead of falling through to `_launcher_checkout()`.
    Why: A user with a global install that was subsequently deleted gets a raw traceback naming `pathlib.Path.read_text`, not the structured "no global record" diagnostic. This is the exact failure mode the guard exists to replace.
    Fix: Move the `os.path.isfile(candidate)` check from line 298 into the `global_manifest()` branch unconditionally, or restructure so `global_manifest()` returns `None` when the file is absent (it already does at line 298, but the logic is inverted — the check should happen before assignment).

- **state_validate.py imports the package it validates against** — `opencode` only
    What: Line 38 imports `from platforms.python.minischema import validate`, and `_get_schema_dir()` (lines 67-69) imports `platforms.python` to resolve the schema directory. This module is called via `ap_launcher.py`, which exists precisely because the package is *not* reachable in installed projects. If the runtime is unreachable, this import fails with `ModuleNotFoundError` before the guard can report.
    Why: The guard in `ap_launcher.py` exits 3 with a named repair, but `state_validate.py` short-circuits it by importing the unreachable package directly. A project with a stale manifest gets "no module named 'platforms'" instead of "runtime.json has no source_root".
    Fix: Make `state_validate.py` call `ap_launcher.bootstrap()` before importing `minischema`, or resolve the schema path via `ap_launcher.resolve()` and import minischema conditionally after bootstrap. Alternatively, move schema resolution into `ap_launcher` and have `state_validate` accept the schema as a dict argument.

- **ast_check.py loads allow-set per file, not per run** — `opencode` only
    What: `check_file()` calls `load_allowed_imports()` on every invocation (line 110), and `main()` loops over files calling `check_file()` (lines 256-258). For N files, the constraints JSON is read and parsed N times.
    Why: This is O(N) disk reads for what should be O(1). For a directory with 100 files, that is 100 reads of the same 200-byte JSON. Not a correctness bug, but a performance defect that scales poorly.
    Fix: Load the allow-set once in `main()` and pass it as a parameter to `check_file()`. Change `check_file(path, allowed=None)` to accept the pre-loaded set.

- **versioning.py::get_active_version() regex matches header rows** — `opencode` only
    What: The regex `_TABLE_ROW_RE` matches any line starting with `| phase | loop_file |`. The code attempts to skip header rows with `re.match(r"^[-:]+$", row_phase)` (line 196) and a list of header-like strings (lines 201-203). But a table with a phase literally named "phase" or "loop file" would match and be skipped incorrectly.
    Why: False negative — a phase whose name collides with a header string returns `None` instead of the loop file path. Unlikely but testable.
    Fix: Skip the first data row after the header separator explicitly (track whether a separator row has been seen), rather than pattern-matching header-like content. Or require the phase name to start with "phase-" followed by digits.

### Important

- **A missing source surface is skipped, not reported** — `claude` only
    What: `if not source_dir.exists(): continue`.
    Why: rename `platforms/claude-code/commands/` and the audit compares zero commands, `has_drift` is `False`, and the run prints `RESULT: all layers current` while every installed command is orphaned. The source tree is the one thing this module can assume; its absence is a bug, not a defensive skip.
    Fix: append a synthetic `FileVerdict(verdict="source-surface-missing")` and treat it as drift.

- **_file_hash returns the hash of the empty string for an unreadable file** — `claude` only
    What: `except OSError: raw = ""`.
    Why: two unreadable files compare equal, so a permission-denied or locked installed file reports `current`. A genuinely empty source file also collides with an unreadable installed one. On Windows a file held open by an editor is a routine trigger.
    Fix: let `OSError` propagate, or return a sentinel (`None`) and emit an `unreadable` verdict that counts as drift.

- **The launcher-path normalisation blinds the audit to a wrong launcher path** — `claude` only
    What: `LAUNCHER_PATH_RE` collapses *any* absolute path ending in `.advanced-plans/bin/ap.py` to the canonical relative form before hashing.
    Why: the rewrite is the single line a `--global` install computes at install time, and it is therefore the line most likely to be wrong — baked against a different `HOME` (the exact Git-Bash-vs-PowerShell divergence `ap_launcher.py:58-62` exists to handle), or pointing into a deleted profile. Every one of those hashes as `current`. The normalisation is right for the drift verdict; the problem is that nothing else checks the value it erased.
    Fix: capture the matched paths and emit a separate non-drift check — the rewritten path must exist and must resolve under the expected install root — reported alongside the verdict.

- **Two documented path_audit rules are not implemented** — `claude` only
    What: the module docstring (`path_audit.py:41,44`) lists `.agents/` as a banned host directory and slash-command syntax (`/plan-and-phase`, `/next-loop`, `/run-gate`) as a B2 violation. Neither appears in any regex. Verified: none of the six patterns matches `"Run /next-loop then /run-gate"`, and `\.(claude|cursor|opencode|codex|gemini)/` omits `agents`.
    Why: this is a documented check that cannot fail, and it has live subjects — `core/skills/companion-detection/SKILL.md:10,15` and `core/skills/phase-plan-creator/references/phase-plan-template.md:255` contain slash commands today, under a scanned root, and CI job 4 is green. Anyone reading the docstring believes host-neutrality is enforced when a third of it is not.
    Fix: add `re.compile(r"(?<![\w/])/(plan-and-phase|next-loop|next-phase|run-gate|phase-compact|decompose-phase|loop-status|…)\b")` as a `core_only` pattern and add `agents` to the host-directory alternation — then triage the violations that appear, with `EXCEPTIONS` entries where the reference is genuinely unavoidable.

- **core/schemas/ is a core surface that path_audit never scans** — `claude` only
    What: `DEFAULT_SCANNED_ROOTS` includes `core/agents` and `core/skills` but not `core/schemas`, which `install_audit.SURFACES:170` treats as an installed surface.
    Why: `core/schemas/handoff.schema.md:85` and `core/schemas/README.md:20` contain slash commands. Host-neutrality is enforced on two thirds of `core/` and silently unenforced on the third.
    Fix: add `"core/schemas"` to `DEFAULT_SCANNED_ROOTS`.

- **The suffix allowlist silently skips file types that live under the scanned roots** — `claude` only
    What: `{".md", ".txt", ".yaml", ".yml", ".json", ".sh", ".ps1", ""}` — no `.py`, `.js`, `.toml`, `.jsonc`, `.cmd`.
    Why: today the scanned roots hold only `.md`/`.sh`/`.ps1`, so the gap is latent — but it is silent. Drop a `.py` helper into `platforms/shared/` and it is exempt from host-neutrality with no indication anywhere that it was skipped.
    Fix: invert it — a *deny*-list of known binary suffixes plus a null-byte sniff — so a new text format is scanned by default rather than exempted by default.

- **Nothing detects a stale EXCEPTIONS entry** — `claude` only
    What: exceptions are keyed by `(rel_path, pattern_name)` and consulted only when a violation fires. Rename or delete `core/skills/permission-config/SKILL.md`, or reword it so it no longer trips the rule, and the entry becomes dead weight that nothing reports.
    Why: the module's stated contract is that suppression is never silent (`path_audit.py:120`). An exception whose subject no longer exists is silent suppression of nothing — it survives review indefinitely and its retirement plan is never revisited. Separately, the key is per-file-per-pattern rather than per-line, so *new* `settings.json` references added anywhere in that file are suppressed too.
    Fix: after the scan, report any `EXCEPTIONS` key that matched zero violations as `UNUSED EXCEPTION` and exit non-zero; add the matched line's content to the key so a new occurrence is not covered by an old waiver.

- **minischema accepts a $-anchored pattern with a trailing newline** — `claude` only
    What: `re.search` with Python semantics — `$` matches before a terminal `\n`. Verified: `validate("a"*40 + "\n", {"type":"string","pattern":"^[0-9a-f]{40}$"})` → `[]` (valid).
    Why: `collected-evidence.schema.json:61,68` and `external-task-envelope.schema.json:78` use exactly that pattern for `base_sha`/`head_sha`. A sha captured from `git rev-parse` and interpolated into JSON with its trailing newline intact validates clean, then fails downstream in `git checkout` with a far less legible error. ECMA-262, which draft-07 specifies, would reject it.
    Fix: compile with `re.search(pattern, instance)` after rejecting embedded newlines, or translate a trailing `$` to `\Z` before compiling.

- **items as an array and additionalProperties as a subschema validate nothing** — `claude` only
    What: `_validate_impl` handles `items` only as a single schema (a list falls through `isinstance(schema, dict)` at line 117 and returns `[]`), and handles `additionalProperties` only when it `is False` (line 181). `_check_schema_keywords:48` compounds it by treating a subschema-valued `additionalProperties` as a properties *map*, so it neither validates it nor rejects it.
    Why: verified — `validate([1,2], {"type":"array","items":[{"type":"string"}]})` returns `[]`. The module's whole safety argument is "unknown constructs raise `UnsupportedKeyword`"; these two are known keywords used in an unsupported *form*, which is the one case that degrades to silent acceptance. Add tuple-form `items` to any state schema and CI job 2 still prints `OK`.
    Fix: raise `UnsupportedKeyword` in `_check_schema_keywords` when `items` is a list, and either implement or reject `additionalProperties` as a dict.

- **A module's sys.exit("message") is swallowed by the launcher** — `claude` only
    What: `except SystemExit as exc: if isinstance(exc.code, int): return exc.code; return 0 if not exc.code else 1` — the non-int payload is discarded without printing.
    Why: `core/constraints.json` justifies the `runpy` allow-set widening on the grounds that it "reproduces `python -m <module>` semantics exactly". Under `-m`, a string exit code is written to stderr and the process exits 1; under `ap.py` the operator gets exit 1 and complete silence. Any future module that uses the idiomatic `sys.exit("something went wrong")` loses its only diagnostic when run through the shipped path.
    Fix: `sys.stderr.write("%s\n" % exc.code)` before returning 1.

- **A stale global record silently overrides the checkout you are standing in** — `claude` only
    What: `_launcher_checkout()` is consulted only after the global manifest lookup succeeds or fails. This matches the documented order (`ap_launcher.py:49-56`), so it is intentional — but step 4's stated purpose, "makes the source repository work with no manifest at all", is false whenever `<home>/.advanced-plans/runtime.json` exists.
    Why: concrete case, and this repository is exactly it — `.advanced-plans/runtime.json` is absent here, so `find_manifest` raises `Boundary("project")` at the repo root, `sibling_manifest` returns `None`, and the global record wins. A developer running `python platforms/python/ap_launcher.py state_validate …` from inside checkout A, with a global install pointing at checkout B, runs B's modules against A's files. Exit 0, no diagnostic, and only `--check` reveals it.
    Fix: move `_launcher_checkout()` ahead of the global lookup, or keep the order and have `--check`-style provenance printed to stderr whenever the resolved root is not an ancestor of the working directory.

- **history_log crashes on non-object JSON and uses a private exit-code convention** — `claude` only
    What: `json.loads` accepts `[1,2]` or `5`; `append_event` then calls `dict(event_dict)` (line 42) and raises `ValueError`/`TypeError` as an uncaught traceback. Invalid JSON returns 1, where `ast_check`, `path_audit`, `install_audit` and `state_validate` all return 2 for a usage error.
    Why: this CLI is invoked from slash-command bodies with shell-interpolated JSON — quoting accidents are the expected failure, and the caller sees a Python traceback naming `history_log.py:42` instead of a message naming the audit log. The exit-code inconsistency means a caller cannot distinguish "bad input" from "append failed" across the toolchain.
    Fix: `if not isinstance(event, dict): print("error: event must be a JSON object", file=sys.stderr); return 2`, and change the invalid-JSON return to 2.

- **freeze_loop_file substitutes across the whole document, in place, with no backup** — `claude` only
    What: `_FREEZE_RE.sub("status: frozen", content)` over the entire markdown file — frontmatter, prose, fenced examples, template blocks alike.
    Why: `loops.md` files in this repo embed example todo blocks and execution-prompt text (`.advanced-plans/phases/phase-5/loops.md` runs to 750+ lines of mixed frontmatter and narrative). Freezing a phase rewrites documentation that describes `status: pending` as well as the live todos, and the operation is destructive with no `.bak` and no dry-run.
    Fix: parse the YAML frontmatter block and substitute only within it (the repo already has `plan_io` for frontmatter handling), or at minimum bound the regex to the `todos:` block.

- **read_text/write_text round-trips rewrite every line ending on Windows** — `claude` only
    What: `read_text` decodes with universal newlines to `\n`; `write_text` re-encodes with `newline=None`, translating to `os.linesep`. Same at `versioning.py:244` and `versioning.py:148`.
    Why: on Windows, freezing a single todo status rewrites an LF-checked-out file entirely to CRLF, producing a whole-file git diff that buries the one-line semantic change and defeats review of a gate-failure retry. `install_audit` normalises EOL so *it* won't notice; git will. The repo already has `test_line_endings.py`, so this is a known concern that these functions sit outside.
    Fix: pass `newline=""` to the write (via `path.open("w", encoding="utf-8", newline="")`) so the bytes round-trip unchanged.

- **VALID_SCHEMAS is a hardcoded string set, not a fact read off disk** — `claude` only
    What: the six names are frozen in source; `core/state/` is the actual registry.
    Why: this is the interpolated-subject shape from the brief. Add a seventh schema to `core/state/` and the CLI refuses it with "Unknown schema basename" naming only the six — a correct file, a wrong error, and no hint that the list is the thing that is stale. Nothing ever asserts the two agree.
    Fix: derive it — `{p.name[:-len(".schema.json")] for p in _get_schema_dir().glob("*.schema.json")}` — and keep a test asserting the six canonical names are a subset.

- **ast_check skips relative imports entirely** — `claude` only
    What: `if node.module:` — a relative `from . import minischema` has `node.module is None` and is silently allowed.
    Why: `core/constraints.json` documents the `__import__` escape hatch as a known, accepted hole; this one is undocumented and easier to reach by accident. It also matters for the standalone-launcher story: a relative import in a shipped module would pass this check and break at runtime in the installed copy.
    Fix: when `node.module is None`, check `node.level > 0` and either allow it explicitly with a comment or report it, but do not fall through the branch invisibly.

- **get_active_version cannot read the real PLANS-INDEX** — `cursor` only
    What: Regex takes column 1 as phase id (`phase-2`) and column 2 as loop file. Live `.advanced-plans/PLANS-INDEX.md` “Phases” table is `| 2 | Claude Code Adapter | [phase-2/plan.md](...) | ... |`. Tests invent `| phase-1 | .advanced-plans/.../loops.md |`.
    Why: Callers asking for `phase="phase-2"` get `None` on every real index. Retry/advance logic that trusts this API picks the wrong file or thinks the phase has no loops.
    Fix: Parse the Phases table that exists (numeric phase, resolve `phases/phase-N/loops.md` / `loops-vN.md` from disk or a dedicated column). Fixture the test on a cut of the real file.

- **ast_check passes on an empty set; relative imports are invisible** — `cursor` only
    What: `if node.module:` skips `from .foo import bar`. CLI at 251–253: no files after collect/exclude → `No .py files found to check.` return 0. Constraints.json is never loaded in that path.
    Why: A bad `--exclude`, a typo path, or `from .requests_wrapper import ...` keeps CI green. `platforms` was added to the allow-set specifically because hiding imports is worse; relative import is that hole.
    Fix: Treat empty `all_files` as exit 2. Flag `ImportFrom` with `node.level > 0` as a violation in this package (or resolve and check). Load constraints even when the file list is empty so a missing policy file still fails.

- **Host-neutrality regexes do not implement the rules in the same file** — `cursor` only
    What: Wrong-nesting and deprecated tokens require `/`, so `.claude\.advanced-plans` and `.claude\plans\` in `.ps1` never match. Host-directory omits `.agents/` though B1 lists it (97). B2 lists slash commands; the regex is only `Claude Code|Cowork|Agent tool|...` (103) — no `/plan-and-phase`.
    Why: The documented detectors cannot fire. A Phase-9-class token written with Windows separators in `setup/claude-code`, or `/next-loop` in `core/skills`, ships as CLEAN.
    Fix: Accept `[\\/]` in path tokens. Add `.agents/` and a slash-command pattern, or delete those claims from the module docstring so the check’s subject is the regex.

- **freeze_loop_file mutates any status: pending substring** — `cursor` only
    What: `_FREEZE_RE` is a whole-file substitute, in place, no backup. Prose or `content:` values that mention `status: pending` become `status: frozen`.
    Why: A retry freeze can corrupt todo text or comments; a second run is not a no-op if those strings mattered. `create_retry_version` at 95 also overwrites `loops-vN.md` with no exists-guard.
    Fix: Restrict to YAML `todos[].status` (use `plan_io` or a line-anchored `^\\s+status:\\s*(pending|in_progress)\\s*$`). Refuse to overwrite an existing versioned file unless `exist_ok`.

- **state_validate library docs describe an API that does not exist** — `cursor` only
    What: Tells callers to `except ValidationError as e: print(e.errors)` and `except SchemaError as e: print(e.message)`. `ValidationError` is a `NamedTuple` (151), never raised; `validate_document` returns a list. `SchemaError` has `.problem`/`.fix`, not `.message`.
    Why: Adapter authors copy the module docstring, their `except` never runs or AttributeErrors, and they treat validation as optional. CLI is honest; the library contract is not.
    Fix: Make `ValidationError` an exception that carries `errors`, or rewrite the docstring to the real return-list API. Align `SchemaError` attribute names.

- **Usage and unreachable share exit 3 in the launcher** — `cursor` only
    What: Empty argv and unknown `--flags` return `EXIT_UNREACHABLE`. The module docstring says 3 means “the runtime is unreachable.”
    Why: A slash command that forgot the module name is indistinguishable from a stale `source_root`. The whole point of 3 vs module non-zero is lost for half the failure modes.
    Fix: Use 2 for usage (match the other CLIs), keep 3 for `Unreachable` only.

- **history_log CLI accepts any JSON and names neither product nor repair** — `cursor` only
    What: `json.loads` then `dict(event_dict)` with no type or `event` key check. Non-objects raise `TypeError` uncaught. Invalid JSON prints `error: invalid JSON`.
    Why: `[]` or `{"foo":1}` becomes a greppable-looking history line with only a timestamp. Callers cannot tell a dropped event from a bad payload. Contrast `ap_launcher.Unreachable.report`.
    Fix: Require a dict with `event`. Catch `TypeError`. Prefix `advanced-planning:` and say to pass one JSON object.

- **minischema lists additionalProperties as supported but only implements false** — `cursor` only
    What: An object-valued `additionalProperties` schema is walked as if it were a property map (keyword check) and then ignored at validate time. `format` is ignored by design; date-time fields in state docs are unconstrained.
    Why: Today’s `core/state` schemas only use `false`, so CI `validate({}, schema)` stays green. The next schema that constrains extras silently accepts them. `state_validate` will report valid for documents the schema author thought were locked down.
    Fix: If value is a dict, validate extra properties against that subschema; if neither bool nor schema, raise `UnsupportedKeyword`. Do not advertise `format` as a validation keyword, or implement `date-time`.

- **ap_launcher.py::sibling_manifest() checks ancestor relationship incorrectly** — `opencode` only
    What: The condition `_is_ancestor(os.path.dirname(ap_dir), os.path.abspath(start or os.getcwd()))` returns `True` when the launcher's project encloses the cwd, and returns `None` to refuse. But `_is_ancestor(parent, child)` returns `True` when `parent == child` (line 118), so a launcher invoked from its own project root would be refused.
    Why: A project-installed launcher invoked from the project root would incorrectly skip its own manifest and fall through to global lookup.
    Fix: Change `_is_ancestor` to return `False` when `parent == child`, or change the condition to use strict containment (`child.startswith(parent + os.sep)` without the equality).

- **install_audit.py hash comparison is EOL-normalised but not encoding-error-normalised** — `opencode` only
    What: `_file_hash()` reads with `errors='replace'` (line 153), which replaces undecodable bytes with `�`. But this is non-deterministic across Python versions if the default replacement character changes.
    Why: Two files with identical binary content but different encoding errors could hash differently if one is read on Python 3.10 and another on 3.12.
    Fix: Read as binary and hash the raw bytes, or document that UTF-8 with `errors='replace'` is the canonical form. Prefer binary read for hash comparison.

- **path_audit.py exclusion list has Windows path variant but not POSIX** — `opencode` only
    What: `DEFAULT_EXCLUDED_SEGMENTS` includes `"platforms\\python\\tests"` (line 163) but not `"platforms/python/tests"` as a distinct entry. The `_is_excluded()` function normalises to forward slashes (line 228), so `"platforms\\python\\tests"` becomes `"platforms/python/tests"` and matches. But a future maintainer might add a POSIX variant and create a duplicate.
    Why: Maintenance hazard, not a current bug. The comment says "Windows path separator variant" but the normalisation makes it redundant.
    Fix: Remove line 163 and add a comment that normalisation handles both separators. Or use `os.path.join()` to construct the segment and normalise it once at module load.

- **minischema.py does not validate additionalProperties recursively** — `opencode` only
    What: The `additionalProperties: false` check (lines 180-191) only checks the immediate instance's keys against the immediate `properties` allow-list. It does not recurse into nested objects.
    Why: A schema with `properties: {foo: {type: object, additionalProperties: false}}` would not catch extra properties inside `foo`.
    Fix: The recursion happens via the `properties` handler (lines 168-178), which calls `_validate_impl` on each property value. The `additionalProperties` check should be applied in that recursive call. Currently it is not, because the check is at the current schema level only. Move the check into the property recursion or apply it to all nested objects.

- **history_log.py CLI does not validate JSON before appending** — `opencode` only
    What: The CLI parses the JSON string (line 65) but does not validate that it is an object (dict). A user could pass `'[]` or `'"string"'` and it would be appended as a valid JSONL line.
    Why: history.jsonl is defined as a sequence of JSON objects (events). A non-object line breaks parsers that expect `dict` records.
    Fix: After `json.loads()`, check `isinstance(event, dict)` and exit with an error if not.

### Minor

- **load_allowed_imports() is called once per file** — `claude` only
    What: `check_file` re-reads and re-parses `core/constraints.json` for every file checked.
    Why: 20 files, 20 file reads and JSON parses. Negligible today; it also means the allow-set could theoretically differ mid-run if the file changes.
    Fix: hoist it into `main` and pass the set to `check_file` (default `None` → load once and cache in a module global).

- **A non-UTF-8 source file gives a traceback instead of exit 2** — `claude` only
    What: `source = path.read_text(encoding="utf-8")` sits outside the `try` that catches `SyntaxError`, and `main`'s `try` only wraps `_collect_py_files`.
    Why: one latin-1 file anywhere under `platforms/python/` turns a clean CI failure message into a `UnicodeDecodeError` traceback.
    Fix: catch `(OSError, UnicodeDecodeError)` and emit a `Violation` with the reason, matching the `SyntaxError` handling directly below.

- **help crashes under python -OO and degrades silently if the docstring is reworded** — `claude` only
    What: `__doc__.split("Usage\n-----\n", 1)[-1]` — `__doc__` is `None` when docstrings are stripped, and `[-1]` returns the *entire* docstring if the heading text ever changes.
    Why: the failure mode is a launcher whose help either raises `AttributeError` or dumps 80 lines of design rationale, in a file whose whole purpose is legible failure.
    Fix: `doc = __doc__ or ""`, and assert the marker is present rather than relying on `[-1]`.

- **Exit 3 means three different things** — `claude` only
    What: `EXIT_UNREACHABLE` is returned for no-arguments (line 398), unknown option (line 420), and module-not-in-runtime (line 439), as well as for genuine unreachability.
    Why: `ap_launcher.py:35-37` states the contract as "a caller can tell 'the runtime is unreachable' from 'the module ran and returned non-zero'". A caller that branches on 3 to recommend re-running the installer will do so for a typo in the module name — which the code itself takes care to distinguish in its *message* (line 431-438) and then throws away in its exit code.
    Fix: add `EXIT_USAGE = 2` for the argument errors and keep 3 for resolution failures only.

- **_now_iso is dead code** — `claude` only
    What: defined, documented, never called.
    Why: it implies timestamps are recorded somewhere in the retry pipeline; `inject_failure_context` writes none.
    Fix: delete it, or use it — `retry-context.json` would be more useful with a `written_at`.

- **verbose on path_audit is dead** — `cursor` only
    What: Flag help says it prints each scanned file; `main` never reads `args.verbose`.
    Why: Operators cannot see that a root was skipped; the CLEAN lie is harder to notice.
    Fix: Implement it or remove it.

- **_file_hash treats unreadable files as empty** — `cursor` only
    What: `OSError` → `raw = ""`. Two unreadable files hash equal → `current`.
    Why: Permission or locking problems look like a clean install.
    Fix: Record `unreadable` and fail the pair.

- **ap_launcher.py docstring says "Standard library only" but imports pathlib** — `opencode` only
    What: The docstring says "Standard library only, and it must not import the package it is resolving" (lines 78-79), and `pathlib` is imported at line 83. `pathlib` is standard library, so this is fine, but the docstring could be misread as "no imports at all".
    Why: Clarity issue, not a bug.
    Fix: Rephrase to "Standard library only (including pathlib, json, os, sys, runpy)".

- **install_audit.py type hint uses Optional[Dict[str, str]] but default is None** — `opencode` only
    What: The function signature says `env: Optional[Dict[str, str]] = None` (line 87), and line 106 does `env = os.environ if env is None else env`. This is correct, but the type hint should be `Optional[Dict[str, str]]` with a note that `None` means "use os.environ".
    Why: Pedantic, but the hint is accurate.
    Fix: None needed.

- **path_audit.py has unused import** — `opencode` only
    What: `from typing import List, NamedTuple` imports `List` and `NamedTuple`, but `List` is used and `NamedTuple` is used. No unused imports.
    Why: I initially thought this was an issue, but re-reading shows both are used. No fix needed.
    Fix: None.

- **state_validate.py type hint for argv uses list[str]** — `opencode` only
    What: `def main(argv: list[str] | None = None) -> int:` uses the PEP 604 syntax `list[str]`, which requires Python 3.10+. The project says Python 3.10+ is required, so this is fine.
    Why: Consistency check — other files use `List[str]` from typing (e.g., `ast_check.py:211`).
    Fix: Standardise on one style. Prefer `list[str]` for Python 3.10+ codebases.

## Strengths noted

**`claude`**

- `ap_launcher.py:301-339` is genuinely well-built error handling: every failure path names the manifest file, the key, and a concrete repair command, and the three degradation modes a hand-edited manifest can produce (unparseable, valid-JSON-but-not-an-object, key present but wrong type) are each caught with a distinct message rather than falling through to `AttributeError`.
- `find_manifest` (`ap_launcher.py:238`) stops on `.git` as a *file* as well as a directory, which correctly catches linked worktrees and submodules — a real distinction that most implementations of this walk get wrong.
- `minischema._json_type` (`minischema.py:72`) checks `bool` before `int`, and `_json_equals` uses that to keep `True != 1` — the classic Python/JSON-Schema trap, handled deliberately with the reason written down.
- `minischema` fails loud on unknown keywords rather than ignoring them (`minischema.py:44`), and CI job 2 uses that as a structural schema check. That is the opposite of the defect class in the brief and it is the right design.
- `install_audit._file_hash` normalising EOL *and* the install-time launcher rewrite before hashing (`install_audit.py:157-158`) is correct reasoning — an audit that reports permanent false drift is an audit nobody reads — and `TestLauncherPathNormalisation.test_normalisation_does_not_mask_a_real_edit` guards the obvious failure of that idea.
- CI job 4 installs into the runner's global layer before auditing it, with a comment explaining why `source,project` could not pass, plus `TestCIAuditsALayerItCanActuallyHave` to stop that regressing. That is exactly the right defence against a skipped-and-therefore-green audit — it just wasn't applied to the other three modules.

**`cursor`**

`ap_launcher.py` is the one module that actually matches the release story: stdlib-only, no `platforms` import, USERPROFILE-before-HOME, boundary stops that refuse borrowed manifests, and failures that name the product, the file/key, and the repair, then exit 3. `install_audit._file_hash` treating `--global` launcher-path rewrite as install rather than drift is the right check subject. CI tests in `test_install_audit.py` that parse `ci.yml` so an audit of a missing layer cannot go silent are the right kind of test. `minischema` correctly treats JSON `true`/`1` as distinct. `state_validate._get_schema_dir` anchors on the package, not cwd.

**`opencode`**

- **Guard-with-repair pattern consistently applied**: `ap_launcher.py`'s `Unreachable` exception carries both problem and fix, and every failure path names the manifest file and the repair command (lines 274-278, 305-339, 350-366). This is the antithesis of the "checks that cannot fail" defect.

- **Boundary detection in `find_manifest()` is real**: The upward walk stops at `.advanced-plans/` (project marker) and `.git` (repo root), raising `Boundary` rather than silently borrowing an outer manifest (lines 231-246). This closes the vendoring/submodule hole that cross-vendor review found.

- **Hash normalisation in `install_audit.py` is correct and necessary**: EOL normalisation (`\r\n` → `\n`) plus the launcher-path canonicalisation regex (lines 131-159) prevents false-positive STALE verdicts on `--global` installs that rewrite the absolute path.

- **Exception mechanism in `path_audit.py` is honest**: Suppressed violations are always printed with reason and retirement plan (lines 418-425); silent suppression is impossible by construction.

- **`minischema.py` enforces keyword allow-list before validating**: `_check_schema_keywords()` walks the schema tree first (lines 37-60), so an unsupported keyword is caught immediately rather than silently ignored.

## Recommendations

**`claude`**

- **Give every audit a non-empty-subject assertion.** Four of the five Critical findings and two Important ones are the same bug wearing different clothes: the subject was absent, the loop body never ran, and the exit code was 0. Add one shared invariant to `ast_check`, `path_audit` and `install_audit` — *record how many units were actually examined, and fail with exit 2 if that count is zero* — and print the count in the success line (`CLEAN -- 47 files scanned across 11 roots`). A success message that carries its own denominator is the cheapest defence against this whole class, and it makes the failure visible in CI logs rather than requiring a test to catch it.
- **Two tests in this release verify a fixture rather than the artefact.** `test_versioning.py:274` asserts `get_active_version` works against a synthetic table that does not resemble `.advanced-plans/PLANS-INDEX.md`; `test_path_audit.py:450` (`test_docs_dir_is_excluded`) asserts the exclusion works using a `tmp_path` that happens not to contain "docs" in its own prefix. Where a module's contract is with a specific file in this repository, at least one test should read that file.
- **Route every destructive write in `versioning.py` through one guarded helper.** Three functions write files in place (`create_retry_version`, `inject_failure_context`, `freeze_loop_file`); none checks for an existing target, none preserves line endings, none offers a dry-run. A single `_safe_write(path, content, *, overwrite=False)` that refuses an unexpected overwrite and writes with `newline=""` would close four findings at once.
- **State the audit's blind spots in its own output.** `install_audit` deliberately normalises the launcher path away and deliberately does not compare skills or the launcher itself. Print that: `NOTE: not compared — skills/ (symlinked), .advanced-plans/bin/ap.py`. A reader who knows what an audit does not check can compensate; one who assumes total coverage cannot.

**`cursor`**

Fail closed: any audit CLI with zero compared files is exit 2, and the summary must list what was actually opened. Add one test per auditor that asserts a missing subject is not exit 0 (you already did this for CI×`install_audit`; extend it to `path_audit.main`, `ast_check.main`, and `inject_failure_context` given a raw `gate-verdict`). Point `get_active_version` tests at a real PLANS-INDEX excerpt so the parser cannot drift from the artefact.

**`opencode`**

- **Add a "checks that cannot fail" lint pass**: Write a script that searches for `if os.path.exists()` followed by early returns that skip the check entirely, or regex patterns that match empty strings. Run it in CI alongside `ast_check.py` and `path_audit.py`.

- **Test the guard paths**: `ap_launcher.py`'s `Unreachable` exceptions are the critical path. Add tests that delete the runtime checkout, corrupt the manifest JSON, and set `ADVANCED_PLANNING_ROOT` to a non-checkout, and assert exit 3 with the expected diagnostic.

- **Document the "false-positive trap" in `install_audit.py` more prominently**: The comment at lines 120-131 explains why the launcher path is canonicalised, but this is easy to miss. Add a one-line summary at the top of the hashing section: "NOTE: launcher path rewrite is normalised away — do not remove".

## Assessments verbatim

**`claude`**

**Ready to merge?** No

**Reasoning:** Five defects were reproduced against the working tree, not inferred: `ast_check`, `path_audit` and `install_audit` each return exit 0 on an empty subject; `get_active_version` returns `None` or the wrong column for every real phase id; and `create_retry_version` overwrites the retry file the caller's previous cycle was editing. The audit-blindness findings matter most because they are the release's own stated defect class reappearing in the modules that exist to catch it — CI is currently green partly because three of its five jobs can pass without examining anything.

**Confidence:** High — I executed `get_active_version` against the real `PLANS-INDEX.md`, `ast_check` against a nonexistent path, `install_audit` against a nonexistent root, `_is_excluded` against a `docs`-containing checkout path, and `minischema.validate` for the trailing-newline and tuple-`items` cases; all five behaved as described. Not verified: the installer scripts' behaviour beyond grepping their `ap_launcher.py` copy lines, whether the shipped slash-command bodies call `get_active_version` (I found no code caller, only documentation references), and the runtime `.claude/` copies, which `.gitignore` excludes from this checkout.

**`cursor`**

**Ready to merge?** With fixes

**Reasoning:** The launcher and hash normalisation are sound, but the check layer still has vacuous exit-0 paths (`install_audit`, `path_audit`, `ast_check`) and a sidecar writer that cannot fail to write useful context. Those are the release’s stated defect class; they should not ship as-is.

**Confidence:** High — all cited lines were read in-tree; I did not run pytest (Ask mode) and did not open anything outside the repo (global `~/.claude` / `runtime.json` behaviour inferred from code and CI tests).

**`opencode`**

**Ready to merge?** With fixes

**Reasoning:** Three critical issues (manifest read before existence check, package import in state_validate, per-file allow-set load) would cause real failures in production. The rest are important but not blockers.

**Confidence:** High — all eight files were read in full, and findings are grounded in specific lines. Could not verify: test coverage (no test files were read), runtime behaviour under Windows vs POSIX (no cross-platform tests were executed), and the actual schema files in `core/state/` (not in scope per instructions).

---

*Grouping is mechanical — by file, exact or nearby line, and title word overlap. It is tuned to under-merge rather than over-merge, so the same issue may appear twice under different wording. Raw reviews are in this directory as `review-<model>.md`.*
