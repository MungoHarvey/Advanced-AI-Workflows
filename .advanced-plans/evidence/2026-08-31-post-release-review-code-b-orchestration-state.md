# Multi-model code review — compiled

**Target:** whole files: platforms/python/handoff_digest.py platforms/python/state_manager.py platforms/python/context_meter.py platforms/python/codex_gate.py platforms/python/plan_io.py platforms/python/remediation_controller.py platforms/python/handoff.py platforms/python/remediate.py  
**Repo:** `/c/Users/mharvey2/Coding/advanced-planning`  
**Run:** 20260831-143621  
**Diff size:** 109191 bytes

## Reviewers

| Reviewer | Status | Critical | Important | Minor | Verdict |
|---|---|---|---|---|---|
| `claude` | ok | 5 | 17 | 9 | **No** |
| `cursor` | ok | 2 | 11 | 2 | **No** |
| `opencode` | ok | 5 | 5 | 4 | **With Fixes** |

> **The reviewers disagree on the verdict** — `claude` says *No*, `cursor` says *No*, `opencode` says *With Fixes*. Read the disagreement before the consensus; it is usually the more informative half.

## Consensus findings (5)

*Raised independently by more than one model. Weight these highest.*

### C1. Stale-state guard is keyed on a field one of its two writers never emits
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Critical)</summary>

- **Stale-state guard is keyed on a field one of its two writers never emits** — `platforms/python/state_manager.py:443`
  What: `archive_cross_phase_state` returns `None` ("nothing to archive") when `loop-ready.json` has no `phase` key. But `write_loop_ready` — the module's own documented public writer (`state_manager.py:88-100`) — writes no `phase` field, and `core/state/loop-ready.schema.json` neither requires nor declares `phase` at all. Only the markdown orchestrator template (`platforms/claude-code/agents/ralph-orchestrator.md:158`) and `prepare_loop_ready` (`state_manager.py:259`) emit it.
  Why: `/next-loop` Step 3a calls this at every loop start (`platforms/claude-code/commands/next-loop.md:78-83`) and prints "No stale cross-phase state to archive." A `loop-ready.json` produced via `write_loop_ready` is *never* archived, so phase N-1's assignment is handed to phase N's worker while the operator is told the bus is clean. This is the exact failure S9 exists to prevent, and it is invisible: schema validation passes, the function returns success. `test_no_archive_when_phase_field_absent` (`platforms/python/tests/test_orchestrator_state_cleanup.py:142`) enshrines the skip as intended, so no test can catch it.
  Fix: treat a missing `phase` as *unknown, therefore stale* — archive it (the file is by definition not attributable to the current phase). Add `phase` to `write_loop_ready`'s signature and payload, and add it to `required` in `core/state/loop-ready.schema.json`. Then invert the test at line 142.

</details>

<details><summary><code>cursor</code> (Critical)</summary>

- **Stale-state archive is a no-op for the orchestrator’s writer** — `state_manager.py:443`
  What: `archive_cross_phase_state` returns immediately when `phase` is missing. `write_loop_ready` (the API the orchestrator prompt still calls) never writes `phase` (`state_manager.py:88-100`). Only `prepare_loop_ready` sets it (`state_manager.py:259`). Tests lock the skip in (`test_orchestrator_state_cleanup.py` documents “phase field absent → skip”).
  Why: After a phase boundary, a `loop-ready.json` from the previous phase is left in place and consumed as the current assignment. The worker executes the wrong loop; `/next-loop` prints “No stale cross-phase state to archive.” The guard cannot fire on the files the primary writer produces.
  Fix: Write `phase` in `write_loop_ready` (derive from `loop_file` the same way `prepare_loop_ready` does). Treat missing `phase` as stale, not matching. Archive (or refuse) rather than skip.

</details>

### C2. Every state-bus write is non-atomic
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Important)</summary>

- **Every state-bus write is non-atomic** — `platforms/python/state_manager.py:102`
  What: `path.write_text(...)` truncates then writes, at `state_manager.py:102`, `:269`, `:349`, `:387` and `plan_io.py:241`.
  Why: this is a cross-process bus. An interrupt (Ctrl-C, agent timeout, the very mid-loop death this module models) between truncate and flush leaves a zero-length or half-written `loop-ready.json`. Every reader — `read_loop_ready` (`:281`), `archive_cross_phase_state` (`:440`), the orchestrator preflight — calls `json.loads` bare and dies with a `JSONDecodeError` that names a parse column, not the real cause. `loops.md` is worse: a truncated write loses the plan.
  Fix: write to `path.with_suffix(".tmp")` then `os.replace(tmp, path)` — atomic on both POSIX and Windows. `os` is already in the `core/constraints.json` allow-set, so this stays zero-dependency.

</details>

<details><summary><code>cursor</code> (Important)</summary>

- **State bus writes are non-atomic; reads are unvalidated** — `state_manager.py:102`
  What: `write_text` overwrites `loop-ready.json` / `loop-complete.json` in place (`state_manager.py:102`, `269`, `349`). `read_loop_ready` / `read_loop_complete` `json.loads` with no schema check (`state_manager.py:281`, `361`). Corrupt or truncated files raise into the worker/main thread, or extra/missing fields are accepted.
  Why: A crash mid-write leaves a half JSON that the next process cannot parse. A previous-shape file (no `handoff_injected`) is accepted until a later `.get` fails far from the write.
  Fix: Write to a temp file in the same directory and `os.replace`. Validate against `core/state/loop-ready.schema.json` / `loop-complete.schema.json` on read (or share `state_validate`).

</details>

### C3. find_next_loop docstring claims numeric phase ordering that sorted() does not provide
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Important)</summary>

- **`find_next_loop` docstring claims numeric phase ordering that `sorted()` does not provide** — `platforms/python/plan_io.py:274`
  What: line 274 is `sorted(plans_path.glob("*/loops.md"))`, a lexicographic sort. The docstring at `plan_io.py:251-253` states it sorts "numerically since they are named `phase-N/`". It does not: `phase-10` sorts before `phase-2`.
  Why: this repo is at phase 16, so the condition is live today. Any pending todo left behind in `phase-10`…`phase-16` is returned ahead of one in `phase-2`…`phase-9`, and the reported "next loop" is from the wrong phase. Note `prepare_loop_ready` is not affected (it takes an explicit file), so the fast path and the legacy path can disagree about which loop is next.
  Fix: `sorted(..., key=lambda p: int(re.search(r"phase-(\d+)", p.parent.name).group(1)))` with a fallback for non-conforming names, and correct the docstring.

</details>

<details><summary><code>cursor</code> (Important)</summary>

- **`find_next_loop` does not sort phases numerically** — `plan_io.py:274`
  What: Docs claim directory names sort numerically (`plan_io.py:251-253`). `sorted(glob("*/loops.md"))` is lexicographic: `phase-10` before `phase-2`.
  Why: Scanning `.advanced-plans/phases` with leftover pending todos in `phase-10` returns that loop while `phase-2` is still the live phase. Python adapters that pass the phases root execute the wrong loop.
  Fix: Sort by the integer in `phase-N`. Optionally require a current-phase argument and do not walk completed/future phases.

</details>

### C4. Segment approx_tokens sums cumulative per-turn occupancy
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Important)</summary>

- **Segment `approx_tokens` sums cumulative per-turn occupancy** — `platforms/python/context_meter.py:171`
  What: `tok = sum(_usage_for_record(r) for r in seg_records)`, where each record's occupancy already includes all prior context (`input + cache_read + cache_creation`).
  Why: the figure is an integral of the context curve, not a token count. Printed under the header `Approx Tok` in the report table (`context_meter.py:366`), a 200-turn segment reports tens of millions of "tokens" for a 200k window. Nothing in the report labels it as anything other than a token count.
  Fix: report `max()` (peak occupancy) or the delta between the segment's first and last record, and rename the column to match.

</details>

<details><summary><code>cursor</code> (Important)</summary>

- **Segment `approx_tokens` sums cumulative occupancy** — `context_meter.py:171`
  What: `_usage_for_record` returns full-turn occupancy (`input + cache_read + cache_creation`), then `detect_segments` sums that across messages.
  Why: The occupancy line from `last_usage` is a real API figure. The report’s per-segment totals and “projected saving” (`context_meter.py:407-418`) are block counts scaled as if they were tokens. Operators compact on a number that cannot be true.
  Fix: Report last-turn occupancy only for token figures. Attribute by block counts without multiplying by `ctx`. Do not sum per-message occupancy.

</details>

### C5. Dead code and misleading module docstrings
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Minor)</summary>

- **Dead code and misleading module docstrings** — `platforms/python/handoff_digest.py:19`
  What: `import os` (`:19`) is unused; the module docstring (`:13-14`) lists `textwrap`, which is never imported. `plan_io._FIELD_RE` (`plan_io.py:42`) and `handoff_digest._extract_deliverables`'s `in_table` (`:567`) are assigned and never read. `handoff.py:34-36` imports `re` and `Optional`, neither used, while `json` is imported inside a function (`handoff.py:68`).
  Why: harmless individually, but the docstrings are the stated contract for the zero-dependency CI invariant, so an inaccurate import list makes that contract harder to audit.
  Fix: remove the unused names; correct the docstring import lists.

</details>

<details><summary><code>cursor</code> (Minor)</summary>

- **Unused imports / dead regex** — `handoff.py:34`
  What: `handoff.py` imports `re` and `Optional` unused. `plan_io.py` defines `_FIELD_RE` unused (`plan_io.py:42`). `handoff_digest.py` imports `os` and `textwrap` unused.
  Why: AST allow-set noise only; no runtime break.
  Fix: Remove them.

</details>

## Single-reviewer findings (50)

*One model saw it and the others did not — either a real blind spot in the others, or a false positive. Adjudicate individually.*

### Critical

- **validate_diff_allowlist never consults the allowlist** — `claude` only
    What: the docstring says "Validate that all changed paths are in the allowlist and none are in never-touch", but the loop body only calls `is_path_never_touch`. `is_path_in_allowlist` is never invoked from this function — nothing rejects a path that is merely *not allowlisted*.
    Why: this is the anti-gate-gaming spine for `/next-phase --auto`. A remediation diff touching `.github/workflows/ci.yml`, `setup/claude-code/install.sh`, `core/constraints.json`, `CLAUDE.md`, or `pytest.ini` passes with `ok=True` and re-gates. Disabling the CI job that produced the failing criterion is precisely the gaming vector the allowlist was written to block, and it is unblocked. The test suite cannot catch it: every case in `TestValidateDiffAllowlist` (`platforms/python/tests/test_remediation_controller.py:181-229`) uses either an allowlisted path or a never-touch path — no case uses a path that is neither, so the missing half of the predicate has no coverage.
    Fix: add `elif not is_path_in_allowlist(p): violations.append(p)` after the never-touch check, and add a test asserting `validate_diff_allowlist([".github/workflows/ci.yml"])` returns `ok=False`.

- **Criteria-coverage check passes vacuously when the criteria list is empty** — `claude` only
    What: `missing = [c for c in frozen_criteria if c not in covered]` over an empty `frozen_criteria` yields `[]`, so `ok=True` regardless of what the verdict contains — including a verdict with no `criteria_outcomes` key at all.
    Why: `frozen_criteria` is produced by the markdown command parsing bullets out of `criteria-frozen.md`. If that parse returns nothing (heading renamed, bullets reformatted, file empty), the "full `criteria_outcomes` required from every re-gate verdict" guard silently reports satisfied and the re-gate pass stands. Subject absent ⇒ check returns success. `test_empty_frozen_criteria_always_passes` (`platforms/python/tests/test_remediation_controller.py:410`) locks this in as intended behaviour.
    Fix: return `(False, ["<no frozen criteria parsed>"])` when `frozen_criteria` is empty — an unparseable criteria file must escalate, not pass. Same for `verdict` lacking a `criteria_outcomes` key entirely (currently indistinguishable from an empty list).

- **update_todo_status can write the status of a different todo** — `claude` only
    What: the pattern is `(- id:\s*"?<id>"?.*?status:\s*)(\w+)` under `re.DOTALL`, applied to the **whole file**, with `loop_name` accepted as a parameter but never used to scope the search. If the matched todo has no `status:` field (an unpopulated stub — the exact case `--full` exists for), `.*?` runs past the end of that todo, past the end of the loop block, and captures the *next* todo's `status:` line, which is then rewritten.
    Why: the worker calls this per todo. A stub todo silently marks a later, unrelated todo `completed`; that todo is then never executed and `find_next_loop`/`prepare_loop_ready` skip it. The function returns `True`, so the caller sees success. Secondary hazard on the same line: `"?` is optional on both sides, so `- id: "loop-001-1"` matches inside `- id: "loop-001-10"`; with `count=1` and file order deciding, a reordered or hand-edited loops.md updates the wrong todo.
    Fix: locate the loop block first (reuse `_LOOP_BLOCK_RE` + `_LOOP_NAME_RE` as `parse_loop_frontmatter` does), bound the search to that block, terminate the middle at the next `- id:` (`(?:(?!\n\s*- id:)[\s\S])*?`), and require the closing quote to match the opening one. Return `False` when the todo has no `status:` field rather than reaching forward.

- **Critical findings with no location are silently discarded whenever any loop is flagged for revert** — `claude` only
    What: a `critical` finding whose `location` is empty falls to the `else` branch; it is added to `unfixable` **only if `structural_set` is empty**. When `loops_to_revert` is non-empty the finding is appended to nothing — not `localized`, not `unfixable`, not `conflict`. It vanishes from the returned triage entirely.
    Why: the comment asserts "structural re-run covers it", but nothing establishes any relationship between the reverted loop ids and that finding. In `/next-phase --auto`, a single unrelated `loops_to_revert` entry is enough to make every location-less critical finding disappear; the controller sees an empty `unfixable` list, does not escalate, and re-gates. Under `core/state/gate-verdict.schema.json` `location` is required but has no `minLength`, so `""` is schema-valid and reachable.
    Fix: always append to `unfixable`; add a separate `covered_by_structural` bucket if the controller genuinely wants to distinguish them, so the finding is visible either way.

- **validate_diff_allowlist never checks the allowlist** — `cursor` only
    What: Docstring says every changed path must be allowlisted and none never-touch (`remediation_controller.py:171-182`). The body only appends `is_path_never_touch` hits. `is_path_in_allowlist` is unused here. Tests never pass `README.md` / `docs/` / `.github/` and expect failure.
    Why: A remediation diff of `platforms/python/foo.py` plus `docs/gate-override-policy.md`, CI YAML, or `CHANGELOG.md` returns `ok=True`. The allowlist half cannot fail. Combined with a real source edit, off-allowlist files can be rewritten during self-heal.
    Fix: Flag any path that is never-touch **or** not allowlisted. Add a test whose only extra file is off-allowlist and assert `ok is False`.

- **Silent skip on empty prior_handoff** — `opencode` only
    What: `_populated()` checks `pending_todos` but `prior_handoff` normalisation (`handoff["done"] = prior_handoff.get("done", "") or ""`) silently converts `None` to `""`.
    Why: A missing/`None` handoff field (e.g. corrupted `loop-complete.json`) is indistinguishable from an intentional empty string; downstream agents lose the signal that context was absent.
    Fix: Raise `ValueError` or return `{"ok": False, "reason": "handoff_missing"}` when any of the three keys is absent (not just empty).

- **Unbounded file walk in repo-root detection** — `opencode` only
    What: The `for _ in range(10)` loop walks up from `phase_dir` looking for `.git` but starts at `phase_dir` itself, not its parent.
    Why: If `.advanced-plans/phases/phase-N/` *itself* contains a `.git` (e.g. nested repo accident), `repo_root` is set incorrectly, producing wrong relative paths in `complete_ref`, `plan_ref`, etc.
    Fix: Start at `phase_dir.parent` (`repo_root = phase_dir.parent`) and cap iterations at a safe bound (e.g. 20), then validate `(repo_root / ".git").is_dir()` before proceeding.

- **Missing exception on write failure — state_manager.py:126, handoff_digest.py:410** — `opencode` only
    What: `path.write_text()` can raise `OSError` (disk full, permission denied) but no try/except surrounds it; caller assumes success.
    Why: A failed write leaves `loop-ready.json` or `handoff.md` absent; the worker/orchestrator proceeds with stale or missing state, causing silent phase drift.
    Fix: Wrap writes in `try: ... except OSError as e: raise RuntimeError(f"state write failed: {e}")` to force caller visibility.

- **Identity-overfit check bypass** — `opencode` only
    What: The identity check compares `d.get("phase")` and `d.get("attempt")` but does not verify `expected_phase`/`expected_attempt` are non-empty/non-zero.
    Why: If the caller passes `expected_phase=""` or `expected_attempt=0`, *any* verdict passes the check (e.g. `"" != "phase-12"` → False only if verdict also has empty phase).
    Fix: Add `if not expected_phase or expected_attempt < 1: return {"ok": False, "reason": "invalid expected values"}` before the identity check.

- **Placeholder injection silent on missing key** — `opencode` only
    What: `inject_handoff()` uses `handoff.get(key, "")` — a missing key (e.g. typo in placeholder) is replaced with `""` silently.
    Why: A malformed placeholder (`[inject prior.handoff_summary.need]`) produces an empty string, not an error; the prompt loses context without warning.
    Fix: Raise `KeyError(f"unknown handoff placeholder: {placeholder}")` when `key not in handoff`.

### Important

- **Remediation cycle bound cannot trip when history is absent or the phase string differs** — `claude` only
    What: returns `0` if `history.jsonl` does not exist, and counts only events where `event.get("phase") == phase` by exact string equality (`remediation_controller.py:67`).
    Why: the bound is what stops the self-heal looping. `history.jsonl` is untracked state that can be missing in a fresh clone or a throwaway worktree (Loop-058 ran the self-heal exercise in exactly such a worktree), and a caller passing `"13"` where events record `"phase-13"` — or vice versa — counts zero forever. Both produce an unbounded triage→fix→re-gate loop with no error.
    Fix: raise or return a sentinel when the history file is absent so the caller must decide explicitly; normalise the phase key on both sides (`str(p).removeprefix("phase-")`) before comparing.

- **Mid-loop-death detection is conjunctive on dirty, which the framework's own commit discipline clears** — `claude` only
    What: `return ready_is_newer and dirty`. The mtime half is nearly always true (loop-ready is written after loop-complete by construction), so `dirty` is the whole decision.
    Why: the worker commits as it goes, so a worker that dies after committing its last todo leaves a **clean** tree with `loop-ready.json` still pointing at an unfinished loop. The IRON RULE check returns `False`, `/next-loop` spawns a fresh orchestrator, and the half-finished loop's remaining todos are silently skipped. The check can only fire in the subset of deaths that happen to leave uncommitted work.
    Fix: compare identity, not filesystem timestamps — `read_loop_ready(...)["loop_name"] != read_loop_complete(...)["loop_name"]` (or `loop_complete is None` with a ready present) is the real signal; keep `dirty` as an additional trigger, not a precondition.

- **Read functions create directories as a side effect** — `claude` only
    What: `_state_path` calls `mkdir(parents=True, exist_ok=True)` and is used by `read_loop_ready`, `read_loop_complete`, `read_history` and therefore `get_status`.
    Why: `get_status("/wrong/path")` creates `/wrong/path` and reports a clean, empty state bus instead of failing. A typo'd or stale `state_dir` is indistinguishable from a genuinely fresh programme, and the reader silently manufactures the evidence for its own answer.
    Fix: split into `_state_path_for_write` (mkdir) and `_state_path_for_read` (no mkdir); readers return `None`/`[]` only when the directory exists.

- **Two divergent parsers for the same loops.md** — `claude` only
    What: `prepare_loop_ready`'s inline `_LOOP_BLOCK_RE` matches any ```` ```yaml ```` fence, whereas `plan_io._LOOP_BLOCK_RE` (`plan_io.py:37-40`) requires a preceding `##` heading. The todo parsers are near-identical copies with subtly different exit conditions.
    Why: a ```` ```yaml ```` example block in loops.md prose that happens to carry a `name:` line is a loop to the fast path and invisible to the documented path. CLAUDE.md states the two-agent pattern remains authoritative and the fast path is an optimisation of it — a fast path that selects a *different* loop breaks that equivalence, and the fast path writes `loop-ready.json` directly with no orchestrator to catch it.
    Fix: delete the inline copy and import `plan_io._LOOP_BLOCK_RE` / `_parse_todos`. One parser, one behaviour.

- **Gate summary keys on a severity value the schema cannot produce** — `claude` only
    What: `important = [f for f in findings if f.get("severity") == "important"]`. The severity enum in `core/state/gate-verdict.schema.json` is `["critical", "warning", "info"]`.
    Why: `important` is always empty, so the `elif important:` branch at `handoff_digest.py:258-260` is unreachable. A gate verdict carrying real findings but no `failure_notes` produces a handoff digest whose Gate review section reads "Attempt 1 pass at confidence 90 ." with no mention of any finding. This is the "two spellings of the same field" shape: the filter looks like a check and can never match.
    Fix: filter on `"critical"`, or on `severity in ("critical", "warning")`.

- **Digest fabricates a verdict path that does not exist** — `claude` only
    What: when no verdict files are found, `gate_verdict_refs` is set to a synthesised `phase-N-attempt-1-phase-goals-agent.json` string, which is then written into the handoff frontmatter (`:500`) and, via `latest_verdict_ref` (`:405`), into the Gate review body (`:461`).
    Why: `handoff.md` is the artefact that survives compaction and is the retention anchor named in CLAUDE.md's Compaction Instructions. A future session following that pointer finds nothing. When `phase_num` fell back to the raw value (see next finding) it emits a literally impossible `phase-?-attempt-1-...` path. The digest asserts a citation it did not verify.
    Fix: emit an empty list and a `gate_verdict_refs: []` / "(no verdict files found)" marker, or raise.

- **_derive_next_action crashes on a non-integer phase** — `claude` only
    What: `int(str(phase_num)) + 1` is unguarded. `phase_num` is `"?"` whenever neither `complete.md` nor `plan.md` frontmatter carries a `phase` key (`handoff_digest.py:336-340` deliberately falls back to the raw value).
    Why: `generate_handoff_digest` documents only `SystemExit` and `FileNotFoundError` (`:304-308`). `/run-gate` Step 10.4 now runs the digest inline on a gate pass and auto-commits — an uncaught `ValueError` there aborts phase closeout *after* the phase has been marked complete and the pointer advanced, leaving the programme half-closed.
    Fix: wrap in `try/except (ValueError, TypeError)` and fall back to `"Start the next phase"`.

- **Codex verdicts are excluded from the handoff's verdict refs** — `claude` only
    What: the globs cover only `*-phase-goals-agent.json` (`:381`) and `*-code-review-agent.json` (`:386`). The codex backend writes `phase-N-attempt-M-codex.json` (`platforms/claude-code/commands/run-gate.md:336`); both `phase-14-attempt-1-codex.json` and `phase-16-attempt-1-codex.json` exist on disk today.
    Why: the cross-model second opinion — including the Phase 14 codex dissent that the override policy was written for — is dropped from the resume digest. The reader of `handoff.md` sees a two-agent gate where a three-backend gate ran.
    Fix: glob `f"{phase_label}-attempt-*.json"` and exclude the `.lastmsg`/`.raw` companions, rather than enumerating agent names.

- **_load_verdict swallows every exception and returns {}** — `claude` only
    What: bare `except Exception: return {}`.
    Why: a truncated or malformed verdict is indistinguishable from "no verdict". Generation continues down the `else` branch at `:460-461` and emits `Gate verdict: passed.` — a corrupt gate record is rendered as a clean pass in the one artefact meant to survive compaction.
    Fix: catch `json.JSONDecodeError`/`OSError` specifically and propagate a distinguishable marker into the digest, e.g. `Gate review: verdict file unreadable ({path})`.

- **Deliverables table columns are indexed after empty cells are dropped** — `claude` only
    What: `cols = [c.strip() for c in stripped.split("|") if c.strip()]` filters empty cells, then `cols[2]` is read as Location (`:580`).
    Why: a row with an empty middle cell shifts every later column left by one, so the "Files touched (pointers, not contents)" section names the wrong path — the section whose entire purpose is to be a correct pointer. The output is confidently wrong rather than absent.
    Fix: split without filtering, drop only the leading/trailing empties produced by the outer pipes, and index positionally.

- **Post-compaction saving projects token savings from block counts** — `claude` only
    What: `recoverable_frac` is computed as a ratio of *block counts*, then multiplied by `ctx` *tokens* at `:410` to produce "Compaction would free ~Xk tokens" (`:417`).
    Why: block counts are not proportional to tokens — one `tool_result` can be 50k characters and one `text` block 20. The number driving a compaction decision is arithmetically unfounded. Compounding it, `_classify_block_text` (`context_meter.py:257`) buckets any text over 500 chars as `raw_tool_io`, so long assistant prose is counted as recoverable, and the narrative at `:400` then labels it "raw tool I/O (file reads + bash output) -- recoverable from disk". It is not recoverable from disk. The trailing "heuristic estimates" note (`:420`) does not cover an attribution that is categorically wrong.
    Fix: weight by `len(text)` per block (a real proxy) instead of counting blocks, and stop routing untyped long text into `raw_tool_io` — classify by block `type` only.

- **A malformed Codex fail degrades to "skipped", so Codex can only ever block on perfect JSON** — `claude` only
    What: any `validate_verdict` rejection returns `{"ok": False, "reason": ...}`, which `/run-gate` converts into `gate_codex_skipped` with no `codex.json`. Rejections include `confidence` arriving as `0.9` instead of `90` (`_REQUIRED_FIELDS` demands `int`, `:45`) and `agent` being `"codex-cli"` (`:182`).
    Why: the degradation is asymmetric. A Codex `pass` that is malformed costs nothing; a Codex `fail` that is malformed is discarded and the gate proceeds on the two in-house agents. The dissenting signal is exactly the one this backend was added to capture.
    Fix: when extraction succeeds but validation fails **and** the extracted object has `verdict == "fail"`, escalate rather than skip — surface it to the operator instead of dropping it.

- **Same-location criticals are treated as contradictory by construction** — `claude` only
    What: `if len(group) > 1` marks *any* two critical findings sharing a `location` string as a conflict, which routes them to escalate-do-not-fix.
    Why: `location` is documented in the schema as "File path, function, or loop identifier" — file-level granularity is the common case. Two genuine, independent critical bugs in one file are the normal shape of a gate fail, and they now short-circuit the self-heal into a STOP. Nothing in the grouping inspects the findings' *prescriptions* for actual contradiction.
    Fix: require the descriptions to be materially different in prescription (or, more honestly, drop the conflict bucket and let the fix agent handle multiple findings in one file) — grouping by string identity does not detect contradiction.

- **LLM-authored handoff text is interpolated into the next agent's prompt unescaped** — `claude` only
    What: `result.replace(placeholder, handoff.get(key, ""))`, iterating a dict in insertion order — `done`, then `failed`, then `needed`.
    Why: `handoff.done` is free text written by the previous worker (an LLM) and lands verbatim in the next worker's prompt. Because `done` is substituted first, a `done` string containing the literal `[inject prior.handoff_summary.needed]` is itself substituted on the following pass — one loop's output can rewrite the next loop's instructions. The same text also flows into `build_context_block` (`handoff.py:147-152`) with no delimiter, so a `done` value containing `\nNeeded: <something else>` forges a field. This is a trust boundary between loops, and it has no guard.
    Fix: do a single-pass substitution (`re.sub` with a callback over one alternation pattern) so replaced text is never rescanned; strip newlines and the literal `[inject ` token from handoff values before injection; delimit the fields in `build_context_block`.

- **Handoff digest invents a verdict path when none exist** — `cursor` only
    What: If `gate-verdicts/` is missing or has no matching files, `gate_verdict_refs` is set to a hardcoded `…-attempt-1-phase-goals-agent.json` string. `_load_verdict` on a corrupt file returns `{}` (`handoff_digest.py:228-233`) and is treated as “no verdict.”
    Why: Compact/`/run-gate` closeout writes a digest that points at a file that was never produced. Resume reads a phantom path; gate summary becomes `Gate verdict: passed` from the CLI default (`handoff_digest.py:273`, `355`), not from disk.
    Fix: Fail (or record `refs: []` and `status` unknown) when no verdict files exist. Do not swallow JSON errors into `{}`. Do not default `--gate-verdict` to `passed`; take `verdict` from the loaded JSON.

- **gate_attempt does not locate verdict files** — `cursor` only
    What: The docstring says `gate_attempt` is used to locate verdict files. The only use is interpolating `failed_v{gate_attempt}` (`handoff_digest.py:353`). Discovery is an unfiltered glob of all attempts (`handoff_digest.py:380-398`).
    Why: Callers who pass `--gate-verdict failed` and `gate_attempt=2` still summarise `pg_verdicts[-1]` (lexicographic last), which can be the wrong attempt. Interface does not match behaviour.
    Fix: Filter globs with the attempt number, or drop the parameter from the public contract.

- **update_todo_status ignores loop_name** — `cursor` only
    What: `loop_name` is a required argument and is never read. The regex searches the whole markdown file (`plan_io.py:232-236`).
    Why: The first `- id: <todo_id>` … `status:` pair in any loop is rewritten. Duplicate or mistyped ids update the wrong loop; the caller still believes they scoped the write.
    Fix: Restrict the substitution to the `##` / ` ```yaml ` block whose `name:` matches `loop_name`. Return `False` if that block has no such todo.

- **prepare_loop_ready treats in-progress loops as stubs** — `cursor` only
    What: A loop with only `in_progress` (and completed) todos is “not all_done”, then `pending_todos` is empty, `_populated` fails, return `agent_needed`.
    Why: Mid-loop resume never gets `loop-ready.json`. The fast path spawns the orchestrator as if the loop were an empty stub.
    Fix: Treat `in_progress` as populated work: write `loop-ready` with those todos, or return a dedicated `resume` reason. Do not reuse `agent_needed`.

- **Two history timestamp keys** — `cursor` only
    What: `append_history` injects `recorded_at` via `.isoformat()` (`state_manager.py:43-45`, `382-383`). `history_log.append_event` injects `timestamp` as `…Z`. Gate events from commands use `timestamp`.
    Why: Anything that greps or schemas `timestamp` misses library-appended lines. `count_gate_fail_cycles` keys on `event`/`phase` only, so it still works; other consumers and humans do not. Same field, two spellings.
    Fix: One key (`timestamp`), one UTC format. Stop adding `recorded_at` unless it is in the history schema.

- **count_gate_fail_cycles skips bad lines and missing files as zero** — `cursor` only
    What: Absent file → `0`. `JSONDecodeError` → `continue` (`remediation_controller.py:63-66`).
    Why: A truncated last line or a wrong path under-counts `gate_fail`. The bound of 2 remediation cycles looks unused; self-heal keeps running.
    Fix: Missing file can stay 0. Malformed lines should raise or count as fail. Do not treat parse failure as “no fails.”

- **Unlocated critical findings vanish if any loop is reverted** — `cursor` only
    What: Coverage is `if not structural_set`, not “this finding’s loop is in `loops_to_revert`.”
    Why: One reverted loop suppresses every location-less critical finding. Controllers see empty `unfixable` and proceed to localised fixes only.
    Fix: Drop unlocated findings only when they name a loop that is actually in `loops_to_revert` (or require a loop id on the finding).

- **Module claims “pure, no I/O” while doing I/O** — `cursor` only
    What: `count_gate_fail_cycles`, `validate_criteria_hash`, and `has_sentinel` read the filesystem. `validate_criteria_hash` raises `FileNotFoundError` instead of returning `False` (`remediation_controller.py:273-275`).
    Why: Callers that treat `False` as “hash mismatch” crash on a missing freeze file, or skip the check in a wrapper and continue.
    Fix: Fix the docstring. Return `False` (or a result object) when the file is absent.

- **Regex escape missing in todo update** — `opencode` only
    What: `id_pattern` uses `rf'...{re.escape(todo_id)}...'` correctly, but the status capture `(\w+)` allows *any* word char, not just valid statuses.
    Why: A corrupted plan file with `status: done_now_later` would be "successfully" updated to a new value, leaving invalid state.
    Fix: Change `(\w+)` to `(pending|in_progress|completed|cancelled)` and verify `count == 1` before returning `True`.

- **No validation of gate_verdict argument** — `opencode` only
    What: `generate_handoff_digest()` accepts `gate_verdict` but only checks `str(gate_verdict).startswith("failed")`; any string is accepted.
    Why: A typo (`"faled"`) produces `status: "faled"` in the digest, breaking downstream parsers expecting `passed|failed_vM`.
    Fix: Validate `gate_verdict` against `^passed$|^failed_v\d+$` and raise `ValueError` on mismatch.

- **_parse_simple_yaml_block does not handle nested lists** — `opencode` only
    What: The `_parse_todos()` loop exits on any non-indented line, but a multi-line string value (e.g. `content: |-\n  line1\n  line2`) breaks parsing.
    Why: Complex todo content with literal blocks is truncated; `todos_count` is under-reported.
    Fix: Add literal-block (`|`, `>`) handling: track indent level and accumulate until dedent.

- **activity_attribution double-counts tool_use** — `opencode` only
    What: `tool_use` blocks are counted in `"other"` but `tool_result` blocks are `"raw_tool_io"`; the narrative (`format_report`) claims "raw tool I/O" is ~X% but excludes tool_use overhead.
    Why: The "How context is being used" percentages do not sum to 100% of blocks; misleading projection of recoverable tokens.
    Fix: Either include `tool_use` in `raw_tool_io` or add a separate "tool_overhead" bucket and report it.

- **No dry-run for state archiving** — `opencode` only
    What: `archive_cross_phase_state()` always renames files; no `dry_run` flag exists.
    Why: Testing the stale-state cleanup requires mocking `Path.rename`; a dry-run mode would allow verification without mutation.
    Fix: Add `dry_run: bool = False` parameter; when True, return the *would-be* archive path without renaming.

### Minor

- **Empty frontmatter is parsed as body** — `claude` only
    What: `in_fm` starts `False`, so the *closing* `---` of an empty frontmatter block is consumed as the opener and never breaks the loop.
    Why: a `complete.md` beginning `---\n---\n` has its whole body scanned for `key: value` lines, producing bogus `phase`/`title` values that go straight into the digest frontmatter. Narrow, but it fails silently rather than returning `{}`.
    Fix: set `in_fm = True` before the loop; the first `---` encountered then correctly terminates it.

- **Declared invariants that nothing enforces** — `claude` only
    What: `MAX_TOKEN_CEILING = 2000` (`:32`) and `REQUIRED_SECTIONS` (`:34-42`) are referenced nowhere in the repo (verified by grep across `*.py` and `*.md`). `--ceiling` (`:663`) accepts any integer, so a caller passing `--ceiling 100000` disables the only bloat guard. `REQUIRED_SECTIONS` looks like a schema-conformance check but the sections are hardcoded in the f-string at `:504-522`, so even if it were used it would be a tautology — a check whose subject is a string the same function interpolated.
    Fix: clamp `--ceiling` to `MAX_TOKEN_CEILING`, and either delete `REQUIRED_SECTIONS` or use it to validate the *parsed* digest headings (which would then be capable of failing).

- **Scalar values containing # are silently dropped** — `claude` only
    What: `^(\w[\w_]*):\s*"?([^"#\n]*)"?\s*$` excludes `#` from the value class, so a line like `task_name: "Fix #12 regression"` fails to match and the key is not recorded at all.
    Why: the key vanishes rather than being partially captured, so `frontmatter.get("task_name", "")` returns `""` and the loop is prepared with a blank task name. Same class of loss for any value containing a quote.
    Fix: strip an unquoted trailing comment explicitly instead of banning `#` from the value.

- **isinstance(True, int) lets booleans through as attempt/confidence** — `claude` only
    What: the generic `isinstance(d[field], expected_type)` check accepts `"attempt": true` and `"confidence": false`.
    Why: `confidence: false` then compares as `0`; `attempt: true` compares equal to `expected_attempt == 1` at `:248`, so a bool sails through the identity-overfit check too.
    Fix: special-case `bool` — `if expected_type is int and isinstance(d[field], bool): reject`.

- **Subagent-vs-subagent disagreement is not reported as a conflict** — `claude` only
    What: conflicts are only computed across the codex/non-codex partition (`:317-329`).
    Why: `code-review-agent` passing while `phase-goals-agent` fails is a real disagreement worth surfacing; `result` is correctly `"fail"`, but `conflicts` is empty so nothing reports *why*.
    Fix: compare all unordered pairs, or compute `{v.get("verdict") for v in verdicts}` and report when its size exceeds one.

- **Attempt files are ordered lexicographically** — `claude` only
    What: `sorted(glob(...))[-1]` (`:397-402`) picks "the most recent" verdict by filename string.
    Why: `attempt-9` sorts after `attempt-10`, so from the tenth attempt onward the digest summarises the wrong verdict. Same root cause as the `find_next_loop` ordering bug; no phase has reached attempt 10 yet.
    Fix: sort on the integer extracted from `attempt-(\d+)`.

- **A failed stdin payload silently falls back to a different transcript** — `claude` only
    What: when `--stdin-hook` yields `None` (unparseable payload, or no `transcript_path` key), `transcript` stays `None` and line 466-467 substitutes `find_current_transcript()` — the newest jsonl for the cwd.
    Why: in `PreCompact` hook mode the tool then measures and reports on a *different session's* transcript, with output indistinguishable from a correct run.
    Fix: when `--stdin-hook` was requested and the payload did not yield a path, print the reason and return non-zero rather than falling back.

- **prepare_loop_ready's docstring describes a predicate over all todos; the code checks only the pending subset** — `claude` only
    What: the docstring says "the loop's `todos[]` must be non-empty AND every todo must have..."; `_populated` is called on `pending_todos` (`:248-250`), and `todos_count` (`:263`) likewise counts only `status == "pending"` — excluding `in_progress` todos.
    Why: a loop being resumed after a mid-loop death has its `in_progress` todos omitted from `todos_count`, so the worker is told to expect fewer todos than remain.
    Fix: align the docstring with the pending-subset behaviour, and count `pending` + `in_progress` in `todos_count`.

- **Dead ceiling and section constants** — `cursor` only
    What: `MAX_TOKEN_CEILING` and `REQUIRED_SECTIONS` are never consulted. `--ceiling 999999` is accepted. Required headings are not verified after render.
    Why: Schema comments look like enforcement. They are not.
    Fix: Clamp ceiling to `MAX_TOKEN_CEILING` and assert `REQUIRED_SECTIONS` appear in the rendered digest, or delete the constants.

- **Magic number in token ceiling** — `opencode` only
    What: `DEFAULT_TOKEN_CEILING = 1500` and `MAX_TOKEN_CEILING = 2000` are module-level constants but `MAX_TOKEN_CEILING` is never enforced.
    Why: A caller can pass `token_ceiling=5000` and `enforce_ceiling()` will accept it.
    Fix: Add `if token_ceiling > MAX_TOKEN_CEILING: raise ValueError(...)` in `generate_handoff_digest()`.

- **Unused import** — `opencode` only
    What: `import re` is present but `_PLACEHOLDER_MAP` uses `.replace()`, not regex.
    Why: Dead code; minor but violates "no unused imports" convention.
    Fix: Remove `import re`.

- **Inconsistent return type annotation** — `opencode` only
    What: `verdict: Union[dict[str, Any], list[dict[str, Any]]]` but returns `dict[str, list]` — the union is only for input.
    Why: Confusing for type checkers; should be `verdict: dict[str, Any] | list[dict[str, Any]]` (PEP 604) or clarify in docstring.
    Fix: Use `verdict: dict[str, Any] | list[dict[str, Any]]` (Python 3.10+ syntax) or add `# type: ignore` with comment.

- **Docstring example outdated** — `opencode` only
    What: Docstring shows `write_loop_ready(state, loop_name="ralph-loop-001", ...)` but the function signature uses keyword-only args after `*`.
    Why: Minor mismatch; users may try positional args and get `TypeError`.
    Fix: Update example to show keyword-only usage explicitly.

## Strengths noted

**`claude`**

- **`aggregate_verdicts` fails closed.** A verdict file that is missing *or* unparseable lands in `missing` (`codex_gate.py:297-304`), and `overall` requires `not missing` as well as all-pass (`codex_gate.py:310-314`). An empty verdict list also returns `"fail"` (`codex_gate.py:306-307`). This is the correct direction for a gate and is easy to get wrong.
- **`prepare_loop_ready` treats an empty `todos[]` as "needs work", not "done"** (`state_manager.py:231-234`). The `len(todos) > 0 and all(...)` guard is exactly the fix for the `all([])` trap that would otherwise skip every unpopulated stub as complete.
- **`validate_criteria_hash` lets `FileNotFoundError` propagate** (`remediation_controller.py:274`) rather than catching it and returning a boolean. A deleted `criteria-frozen.md` therefore cannot be mistaken for "hash matched".
- **`write_loop_complete` validates the status enum before any write** (`state_manager.py:329-330`), so an invalid status never reaches disk.
- **`extract_verdict_json`'s duplicate-block relaxation is correctly scoped** (`codex_gate.py:106-119`): blocks are parsed and compared as objects, and genuinely-differing blocks still return `None`. The Loop-056 fix did not widen into "take the last block".
- **`read_handoff` documents that it raises** rather than silently defaulting (`handoff.py:65-66`), and the code matches (`data["handoff"]` at `handoff.py:72`).

**`cursor`**

`extract_and_validate` actually compares Codex `phase`/`attempt` to caller-supplied identity rather than trusting the sample verdict (`codex_gate.py:239-255`). Identical fenced JSON blocks resolve to the last copy instead of degrading (`codex_gate.py:106-118`). `prepare_loop_ready` refuses to write `loop-ready.json` when pending todos fail the populated predicate (`state_manager.py:250-255`). `write_loop_complete` rejects illegal `status` values (`state_manager.py:329-330`). `ascii_safe` is a real Windows encoding guard, not a comment (`handoff_digest.py:58-81`).

**`opencode`**

- **Zero-dependency discipline enforced**: All eight files correctly use only stdlib (json, pathlib, re, hashlib, etc.). CI AST checker constraint is honoured throughout.
- **Defensive parsing**: `codex_gate.py`'s handling of duplicate fenced JSON blocks (identical → accept last; differing → reject) is precise and well-motivated by observed codex behaviour.
- **Stale-state protocol**: `state_manager.py`'s `archive_cross_phase_state()` and `detect_mid_loop_death()` implement the S9/S8 guards with correct mtime logic and dirty-tree gating.
- **Path normalisation**: Consistent use of forward-slash conversion (`_normalise()` in `remediation_controller.py`, `.as_posix()` in `state_manager.py`) avoids Windows path leakage.
- **Lenient-but-safe validation**: `codex_gate.validate_verdict()` tolerates unknown fields while rejecting missing required fields, wrong types, and enum violations — correct trust-boundary shape.

## Recommendations

**`claude`**

- **The recurring shape in this release is "absent subject ⇒ return success".** Four of the five Criticals and two Importants are instances: missing `phase` field, missing allowlist branch, empty `frozen_criteria`, missing `history.jsonl`, missing `status:` line, location-less findings. A cheap structural fix: make every guard in `remediation_controller.py` and `state_manager.py` return a three-valued result (`pass` / `fail` / `indeterminate`) and have callers treat `indeterminate` as `fail`. Booleans cannot express "I could not check", which is why these all collapse into "pass".
- **Two of these defects are load-bearing in tests.** `test_no_archive_when_phase_field_absent` and `test_empty_frozen_criteria_always_passes` assert the vacuous behaviour as correct. When fixing, invert those tests rather than deleting them — they document the exact hazard.
- **Add a negative-coverage rule to the test suite**: for every predicate that gates a destructive or safety-critical action, require at least one test whose input is *outside* both the allow-set and the deny-set. The `validate_diff_allowlist` gap survived because every existing case was drawn from one list or the other.
- **Extract one loops.md parser.** `state_manager.prepare_loop_ready` currently carries a hand-copied variant of `plan_io`'s parser with different fence and exit rules. Two parsers over the same file format on the same critical path will keep diverging.

**`cursor`**

Share one YAML todo parser between `plan_io` and `prepare_loop_ready` (the inline copy will drift). Add a test that `write_loop_ready` output is archived when `current_phase` differs, without hand-planting a `phase` key. Add a test that `validate_diff_allowlist(["platforms/python/x.py", "README.md"])` fails. I did not run pytest (Ask mode); tests exist under `platforms/python/tests/test_{state_manager,remediation_controller,plan_io,handoff_digest,codex_gate,context_meter,remediate,handoff,orchestrator_state_cleanup}.py`.

**`opencode`**

- **Add schema validation at write time**: `write_loop_ready()` and `write_loop_complete()` should validate their payloads against `core/state/*.json` schemas before writing — catch drift early, not at read time.
- **Introduce atomic writes**: Replace `path.write_text()` with a `write_atomic(path, content)` helper (write to temp, `os.replace`) to prevent partial writes on crash.
- **Enforce `MAX_TOKEN_CEILING`**: The constant exists but is unused; enforce it in `generate_handoff_digest()` to prevent accidental ceiling inflation.
- **Add `__slots__` or dataclasses**: `remediation_controller.py`'s pure functions could be grouped into a dataclass for stricter typing and easier testing.

## Assessments verbatim

**`claude`**

**Ready to merge?** No

**Reasoning:** Three of the Criticals sit in the anti-gate-gaming and stale-state safety spine and all fail open — `validate_diff_allowlist` never checks the allowlist, the criteria-coverage check passes on an empty list, and the cross-phase archive skips exactly the payloads its own public writer produces. `update_todo_status`'s unbounded `.*?` and `triage_findings`'s silent drop are independent data-integrity bugs on the loop execution path.

**Confidence:** High — every cited line was read in the file, and the cross-file claims were verified on disk (the `loop-ready` schema's field list, the gate-verdict severity enum, the existence of `phase-14-attempt-1-codex.json`, and the two tests that enshrine the vacuous passes). Not verified: the body of `platforms/claude-code/commands/next-phase.md`, so I have not confirmed how `--auto` consumes `count_gate_fail_cycles` / `validate_diff_allowlist` — the fail-open behaviour of the predicates themselves is confirmed regardless of how the command wires them.

**`cursor`**

**Ready to merge?** No

**Reasoning:** The two safety checks that matter for silent cross-process failure — cross-phase archive and remediation allowlist — do not observe the facts the rest of the system writes. Remaining issues (invented verdict refs, unused `loop_name`, lex phase order, non-atomic state files) will show up as the wrong loop or a digest that looks successful.

**Confidence:** High — every cited line was read in `C:/Users/mharvey2/Coding/advanced-planning`. Not verified: live pytest, Claude transcript layout under `~/.claude/projects` (`context_meter.find_current_transcript`), and how callers pass `git diff --name-only` paths into `validate_diff_allowlist`.

**`opencode`**

**Ready to merge?** With fixes

**Reasoning:** Three critical issues (repo-root walk, write-failure silence, identity-overfit bypass) can cause silent state corruption or incorrect gate verdicts; all are narrow and fixable without redesign.

**Confidence:** High — all eight files were read line-by-line; findings cite exact lines. Could not verify: runtime behaviour of CLI wrappers (`run-gate.md`, `/next-phase`) that call these modules, or the contents of `core/state/*.json` schemas (not in target list).

---

*Grouping is mechanical — by file, exact or nearby line, and title word overlap. It is tuned to under-merge rather than over-merge, so the same issue may appear twice under different wording. Raw reviews are in this directory as `review-<model>.md`.*
