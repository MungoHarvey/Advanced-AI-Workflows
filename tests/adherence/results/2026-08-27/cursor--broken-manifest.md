Confirmed: `.aaw/installed.json` is truncated mid-key under `components.gstack`, so every companion is treated as **not** installed. No `/office-hours`, brainstorming skill, phase commands, or gate — work happens in conversation only.

---

### Request 1 — strategy (no gstack)

Complaints bundle three different problems:

1. **Per-record stderr progress** — unconditional `processing record N of M` on every row; feels noisy and “slow”.
2. **`--limit`** — `0` means “no limit”; easy to misread.
3. **CSV path** — trivial `",".join(r)` with no escaping; may be a quality complaint, not speed.

**Recommendation I would pick:** fix (1) first — quiet by default, progress only with `--verbose` (or similar). Re-check complaints after that; only then touch `--limit` UX/docs and CSV correctness. Do not redesign the whole CSV path until the noise is gone.

---

### Request 2 — plugin design (approved; no file written)

**Goal:** third parties register formats without editing `FORMATTERS` in `src/cli.py`.

**Approach:** setuptools/`importlib.metadata` entry points, group e.g. `formatctl.formatters`, value `module:callable`. Built-ins (`json`, `csv`) stay as defaults; discovered plugins merge into the registry used for `--format`. Contract: `(row: list[str]) -> str`. Duplicate names and load failures → clear errors. Discovery at `main()`/argparse time, **not** at import (house rule: `src/cli.py` must stay importable without side effects).

**Rejected:** cwd plugin-folder scan (fragile); requiring core edits (status quo).

**Next after this approved design:** with neither Advanced Planning nor `writing-plans` available → write the implementation plan in conversation, then implement.

---

### Request 3 — review (direct; no gate)

Eng lens on the assumed plugin work vs current stub:

- Extension must not require editing a hard-coded `FORMATTERS` dict.
- Entry-point load must not run at import time.
- Built-in `json`/`csv` and dynamic `--format` choices must still work; duplicate/broken plugins must fail clearly.
- Add registration/discovery tests (README notes no tests yet).

Current `src/cli.py` would not pass that bar until the design is implemented.

---

```
## Request 1
routed_to: NONE
reason: Ambiguous scope needing a strategic second opinion maps to /office-hours when gstack is installed; the manifest is malformed so gstack is treated as not installed, so there is no command — work the ambiguity out in conversation.
classification: NONE
spec_file: NONE

## Request 2
routed_to: NONE
reason: Designing a third-party formatter plugin system is ideation/architecture work that would use the brainstorming skill when superpowers is installed; malformed manifest means not installed, so design in conversation with no skill to load and no .advanced-plans/specs/ write.
classification: NONE
spec_file: NONE
terminal_step: Write the implementation plan in conversation (neither Advanced Planning phase planning nor writing-plans is available), then implement.

## Request 3
routed_to: NONE
reason: Review before building on completed work maps to /run-gate when Advanced Planning is installed (or gstack review commands when gstack is); neither is installed per the malformed manifest, so review the work directly with no command to invoke.
classification: NONE
spec_file: NONE

## Environment
components_installed: none (advanced-planning, gstack, superpowers, and gstack-to-plans all treated as not installed). Determined by reading .aaw/installed.json, which is truncated/malformed mid-key under components.gstack; project rules require treating every component as NOT installed when the manifest is malformed, without inferring install state from on-disk skill directories.
```
