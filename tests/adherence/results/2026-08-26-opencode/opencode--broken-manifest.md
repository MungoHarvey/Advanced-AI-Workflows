## Request 1
routed_to: NONE
reason: The installed.json manifest is malformed (truncated JSON), so per AGENTS.md I must treat all components as NOT installed. Without gstack installed, there is no /office-hours command to run. I worked the ambiguity in conversation instead.
classification: NONE
spec_file: NONE

The maintainer's report that "formatctl is slow and confusing" has three distinct complaint sources: (1) per-record progress noise on stderr, (2) the --limit flag, (3) the whole CSV path. These are three different problems:

**Problem A: stderr noise** — Line 21 prints "processing record X of Y" for every row. This is O(n) output that dominates runtime on large files and clutters pipes.

**Problem B: --limit flag** — The flag exists but its purpose is unclear. Is it for testing? Sampling? Performance? It slices after reading the whole file (line 18), so it does not help performance.

**Problem C: "the whole CSV path"** — The tool reads a TSV file (per README) but the complaint says "CSV". This suggests users do not understand what the tool does or what format it expects.

**Recommended approach:** Treat these as three separate issues, not one "slow and confusing" problem. Start with Problem A (remove per-line stderr printing — it is the only thing that actually makes it slow), then rename or document --limit, then fix the TSV/CSV confusion in the help text. Do not design a plugin system or refactor until the actual complaints are isolated.

## Request 2
routed_to: NONE
reason: The installed.json manifest is malformed, so advanced-planning is NOT installed. Per AGENTS.md rule 5, when Advanced Planning is not installed, use the writing-plans skill if superpowers is installed, and write the plan in conversation if neither is. The manifest does not confirm superpowers is installed, so I wrote the design in conversation.
classification: Architectural
spec_file: .claude/specs/plugin-format-registry.md

**Plugin Registry Design for formatctl**

**Goal:** Allow third parties to register custom output formats without editing `FORMATTERS` in `src/cli.py`.

**Constraints:**
- Keep `src/cli.py` importable without side effects (per AGENTS.md house rules)
- British spelling in prose, American in code identifiers
- Never add a dependency without saying why in the commit message

**Design:**

1. **Registry API** — Add a `register_format(name, formatter)` function that third parties call. The registry is a dict stored at module scope, populated at import time.

2. **Discovery mechanism** — Use entry points (setuptools) or a simple convention: any module named `formatctl_<formatname>` on sys.path is imported and given a chance to register. Entry points are more robust but require a dependency; convention-based discovery is zero-dep but fragile.

3. **Formatter signature** — A formatter is a callable taking `(row: list[str]) -> str`. Same as current `FORMATTERS` values.

4. **Built-in formats** — `json` and `csv` remain built-in, registered at module init. Third-party formats shadow built-ins if they register the same name (documented behaviour).

5. **Error handling** — A format that fails to import is logged (stderr) and skipped. The registry does not fail open.

6. **CLI help** --format choices are computed from the registry at runtime, not hardcoded.

**File structure:**
```
src/
  cli.py              # main CLI, imports registry
  registry.py         # new module: register_format(), FORMATTERS dict
  formats/
    __init__.py
    builtin.py        # json, csv formatters
```

**API example:**
```python
# Third-party module: formatctl_xml.py
from formatctl.registry import register_format

def to_xml(row):
    return "<row>" + "".join(f"<f>{v}</f>" for v in row) + "</row>"

register_format("xml", to_xml)
```

**What the approved design artefact is:** This markdown block is the design. In a project with Advanced Planning installed, this would be written to `.advanced-plans/specs/plugin-format-registry.md`.

**Terminal step (what comes after approval):** Implement the registry module, refactor `cli.py` to use it, add the discovery hook, write tests for the registry API and discovery mechanism, then update the README to document how third parties register formats.

## Request 3
routed_to: NONE
reason: The installed.json manifest is malformed, so gstack is NOT installed. Per AGENTS.md rule 6, without gstack there is no /review or /codex command to run. I would do the review manually.
classification: NONE
spec_file: NONE

**Review approach for Request 2's plugin system:**

Since no review tools are available (gstack not installed), I would:

1. **Read the diff** — Compare the new `registry.py` and `formats/` module against the original `cli.py` to verify:
   - No side effects at import time (per house rules)
   - The `register_format()` API is stable and documented
   - Discovery mechanism does not import arbitrary code (security)

2. **Verify the API boundary** — Ensure third-party formatters cannot access anything except the `row` argument they are given. No file system, no network, no subprocess.

3. **Check error paths** — A broken third-party module should not crash the tool. It should log and skip.

4. **Test the help text** — `--format` choices should reflect the registry, not hardcoded values.

5. **Run the tool** — Verify built-in `json` and `csv` still work, then verify a third-party format can be registered and used.

**What would do the review:** In a project with gstack installed, I would invoke `/review` for pre-landing PR review, or `/codex` for a second opinion. Without gstack, the review is manual — read the diff, run the tool, verify the API boundary.

## Environment
components_installed: NONE — The `.aaw/installed.json` file is malformed (truncated JSON, ConvertFrom-Json fails with "Unterminated string"). Per AGENTS.md: "If `.aaw/installed.json` is missing, unreadable, or malformed, treat every component as NOT installed". No `.advanced-plans/` directory exists. Global gstack skills exist at `~/.claude/skills/gstack/` but the project manifest does not confirm installation, so per the routing rules I cannot treat them as installed for this project.
