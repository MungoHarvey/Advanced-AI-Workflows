**Request 1 — strategy (gstack absent, so no `/office-hours`)**

Three distinct complaints are being collapsed into one slogan:

1. **Stderr progress** — every record prints `processing record i of n`; noisy and can dominate I/O on large files.
2. **`--limit`** — `0` means “no limit”, which is easy to misread; no help text explains it.
3. **CSV path** — formatter is naive `","`.join with no escaping; “JSON” is `str(row)`.

I would start with (1): gate progress behind `--verbose` (or drop it). That is the one change that hits every run and matches both “slow” and “confusing”. Then document `--limit`. Leave CSV correctness as a separate ticket unless complaints remain after the noise is gone.

---

**Request 2 — brainstorming · classification: Architectural**

This project has superpowers but not Advanced Planning; for a plugin surface this size, Advanced Planning would help with phased delivery — noted once, not blocking.

**Approaches**

| Approach | Cost | Forecloses |
|---|---|---|
| A. `importlib.metadata` entry points (`formatctl.formatters`) | Packaging ceremony; clear for PyPI plugins | Ad-hoc single-file drop-ins without install |
| B. Scan a `plugins/` dir / `$FORMATCTL_PLUGIN_PATH` | Easy local hacks | Standard install story; name collisions |
| C. Keep `FORMATTERS` + manual `register()` called from user code | Tiny change | True third-party install without editing core |

**Chosen: A** — entry points for discovered formatters; keep built-in `json`/`csv` as first-party entry points or a small built-in registry merged at startup. Reject B as primary (optional later). Reject C as insufficient for “without editing `FORMATTERS`”.

**Design commits to:** load formatters via entry points; `--format` choices = builtins ∪ plugins; plugin API = callable `(row: list[str]) -> str` (or a tiny protocol with `name` + `render`); fail loudly on duplicate names; `src/cli.py` stays import-safe (discovery in `main` / explicit loader, not at import time).

Approval treated as granted. **Next step after approval:** `writing-plans` (Advanced Planning is not installed, so no `/plan-and-phase`). Spec path for this project: `docs/superpowers/specs/2026-08-27-formatter-plugins.md` (not written — session is read-only).

---

**Request 3 — eng review lens (gstack / `/run-gate` unavailable)**

Assuming the plugin work is done, against that design and current `src/cli.py`:

- **Pass if:** entry-point discovery is lazy (not at import), builtins still work, duplicate plugin names error, `--format` help lists discovered names, no new hard dependency without a commit rationale.
- **Watch:** CSV still unescaped; stderr progress still unconditional — unrelated to plugins but still the Request 1 pain.
- **Block shipping follow-ons if:** `FORMATTERS` remains the only extension point, or `parse_args` freezes `choices` before plugins load.

No phase gate here (Advanced Planning not installed).

---

```
## Request 1
routed_to: NONE
reason: Ambiguous scope needing strategic review before a plan (front-door rule 1). gstack is not installed per .aaw/installed.json, so there is no /office-hours command; worked the options out in conversation and recommended fixing stderr progress first.
classification: NONE
spec_file: NONE

## Request 2
routed_to: brainstorming
reason: Clear design work with multiple plausible approaches before implementation (front-door rule 4). superpowers is installed, so the brainstorming skill applies; Advanced Planning is not, so the design artefact stays at the skill default under docs/superpowers/specs/.
classification: Architectural
spec_file: docs/superpowers/specs/2026-08-27-formatter-plugins.md
terminal_step: writing-plans

## Request 3
routed_to: NONE
reason: Second opinion on completed work (front-door rule 6). gstack is not installed, so no /plan-eng-review or similar; Advanced Planning is not installed, so no /run-gate. Reviewed directly under an eng-review lens.
classification: NONE
spec_file: NONE

## Environment
components_installed: superpowers only (installed: true, scope: project). gstack, advanced-planning, gstack-to-plans, and plannotator are all installed: false. Determined solely by reading .aaw/installed.json (did not infer from .advanced-plans/ or skill directories on disk).
```
