# Multi-model code review — compiled

**Target:** whole files: setup/claude-code/install.ps1 setup/claude-code/install.sh setup/claude-code/uninstall.ps1 setup/claude-code/uninstall.sh setup/codex/install.ps1 setup/codex/install.sh setup/codex/uninstall.ps1 setup/codex/uninstall.sh   
**Repo:** `/c/Users/mharvey2/Coding/advanced-planning`  
**Run:** 20260831-140618  
**Diff size:** 133686 bytes

## Reviewers

| Reviewer | Status | Critical | Important | Minor | Verdict |
|---|---|---|---|---|---|
| `claude` | ok | 4 | 7 | 5 | **No** |
| `cursor` | ok | 5 | 6 | 0 | **No** |
| `opencode` | ok | 3 | 4 | 3 | **With Fixes** |

> **The reviewers disagree on the verdict** — `claude` says *No*, `cursor` says *No*, `opencode` says *With Fixes*. Read the disagreement before the consensus; it is usually the more informative half.

## Consensus findings (5)

*Raised independently by more than one model. Weight these highest.*

### C1. Installer unconditionally destroys an existing .claude/settings.json, and the uninstaller documents the opposite
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Critical)</summary>

- **Installer unconditionally destroys an existing `.claude/settings.json`, and the uninstaller documents the opposite** — `setup/claude-code/install.sh:565`
  What: `cat > "$SETTINGS" <<EOF` truncates `$PROJECT/.claude/settings.json` with no existence check, no backup, and no `settings.planning.json` fallback. `setup/claude-code/install.ps1:454` does the same via `WriteAllText`. Meanwhile `setup/claude-code/uninstall.ps1:157-161` (and the matching comment in `uninstall.sh`) justifies *keeping* the file with "install.ps1 writes settings.json only when none exists and saves settings.planning.json otherwise" — that is true of the older `platforms/claude-code/install.sh:110-116`, and false of both files under review. Neither setup installer ever writes `settings.planning.json`, yet both uninstallers hunt for it.
  Why: A user with hooks, `env`, or a `permissions` block in `.claude/settings.json` loses all of it, silently, on install or on any re-install/upgrade — the printed output says only "Writing settings.json...". This repo's own `.claude/settings.json` (a `planning` block, no `permissions`) would be replaced by one carrying a `permissions.allow` block. The uninstaller then declines to remove the file on a stated premise that does not hold, so the interface is wrong in both directions.
  Fix: Mirror `platforms/claude-code/install.sh`: if `settings.json` exists and differs, write `settings.planning.json` and tell the user to merge; otherwise write `settings.json`. Then the uninstaller's comment becomes true. Add a test asserting a pre-existing `settings.json` survives install byte-identical.

</details>

<details><summary><code>cursor</code> (Critical)</summary>

- **Claude install always overwrites `.claude/settings.json`; uninstall documents the opposite** — `setup/claude-code/install.ps1:435` (and `setup/claude-code/install.sh:565`)
  What: Both installers `WriteAllText` / `cat >` settings with no “write only if absent” and no `settings.planning.json` sidecar. Uninstall comments and `setup/claude-code/README.md` claim the installer writes only when none exists.
  Why: Re-install destroys the user’s Claude Code hooks/permissions. Uninstall then “keeps” the file it just replaced, so recovery is gone. That is an interface lie plus data loss.
  Fix: Match the documented merge: write only if missing; otherwise write `settings.planning.json` and leave `settings.json` alone.

</details>

### C2. A missing or malformed skill-ownership.json fails open: codex's uninstall deletes the other adapter's skills and the shared launcher
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Critical)</summary>

- **A missing or malformed `skill-ownership.json` fails open: codex's uninstall deletes the other adapter's skills and the shared launcher** — `setup/codex/uninstall.sh:192`
  What: `except (json.JSONDecodeError, ValueError): pass` leaves `data` as `{"schema_version":1,"skills":{}}`, so every approved skill resolves to zero owners and takes the `REMOVE` branch (line 219). `setup/codex/uninstall.ps1:126` has the identical `catch { # Malformed - treat as empty }`. Because no skill is `KEEP`, `SHARED_OWNERS` stays 0 and `bin/ap.py` plus `runtime.json` are removed as well.
  Why: This is exactly the failure the ownership mechanism exists to prevent. The registry can be absent for ordinary reasons — an install that predates it, a truncated write, or an install where `python` was unavailable (see below, `write_ownership` is the *last* step of `install.sh`, so an abort there leaves skills installed and no registry). Running codex's uninstall then removes `.agents/skills/advanced-planning/` that OpenCode installed and the launcher every OpenCode skill invokes, leaving that adapter installed but inert. Note that `install.sh` treats malformed JSON as a hard error (`sys.exit(1)`) — the uninstall is the lenient one, which is backwards for the destructive direction.
  Fix: Fail closed. If the registry is absent or unparseable, remove nothing, report what was found, and require an explicit `--force` (or point the user at the file). At minimum, do not remove `bin/ap.py` when ownership cannot be established.

</details>

<details><summary><code>cursor</code> (Critical)</summary>

- **Missing or malformed `skill-ownership.json` is fail-open deletion** — `setup/codex/uninstall.sh:192` (and `setup/codex/uninstall.ps1:126`)
  What: Install refuses malformed JSON. Uninstall catches parse errors, treats the registry as empty, and for every approved skill that exists on disk emits `REMOVE`. Codex `install.sh` even documents that an empty owner list removes shared skills (`setup/codex/install.sh:500`).
  Why: Delete or corrupt the registry (or skip it after a partial install) and `uninstall --yes` wipes `advanced-planning` plus the seven core skills even when OpenCode still uses them. A crafted invalid file is enough; no valid merge is required.
  Fix: If the file is missing or invalid, abort uninstall (or keep all skill dirs). Never infer “sole owner” from absence.

</details>

### C3. Symlink (and -Global -Symlink) recursively deletes the destination skills tree before creating the junction
*Raised by `claude`, `cursor`*  ⚠ **severity disagreement:** `claude`=Critical, `cursor`=Important

<details><summary><code>claude</code> (Critical)</summary>

- **`-Symlink` (and `-Global -Symlink`) recursively deletes the destination skills tree before creating the junction** — `setup/claude-code/install.ps1:64`
  What: `Do-Junction` does `if (Test-Path $link) { Remove-Item $link -Recurse -Force }`. Called with `$SkillsDest = $HOME\.claude\skills` at line 171 (global) and `$ClaudeDir\skills` at line 408 (project).
  Why: `install.ps1 -Global -Symlink` deletes the user's entire `~/.claude/skills/` tree — every globally-installed skill from any source, not just this framework's — with no prompt, no dry-run distinction beyond the flag, and no mention in the header comment, which describes `-Symlink` only as "creates a junction … instead of copying". On a machine with a populated global skills directory this is unrecoverable data loss. The project form has the same shape against a project's own `.claude/skills/`.
  Fix: Refuse to junction over a path that exists and is not already a reparse point; require the user to remove it themselves, or move it aside to `skills.bak-<timestamp>`. The POSIX twin does not delete (it has the opposite bug — see below), so the two installers currently disagree about a destructive operation.

</details>

<details><summary><code>cursor</code> (Important)</summary>

- **Installer `Do-Junction` still uses `Remove-Item -Recurse -Force`** — `setup/claude-code/install.ps1:64`
  What: Uninstall switched to `Directory.Delete($path, $false)` because following a junction would delete the checkout. Install `Do-Junction` still `Remove-Item -Recurse -Force` on the dest (no reparse check), including `Test-Path` without `-LiteralPath`.
  Why: If dest is a junction into `core\skills`, a `--symlink` / self-install replace can delete source files on a host where `Remove-Item` follows reparse points. Uninstall’s comment already treats that as patch-level-dependent.
  Fix: Use the same unlink-only deletion as uninstall before creating the junction.

</details>

### C4. runtime.json is assembled by string interpolation, so VERSION content or the checkout path controls source_root
*Raised by `claude`, `cursor`*  ⚠ **severity disagreement:** `claude`=Important, `cursor`=Critical

<details><summary><code>claude</code> (Important)</summary>

- **`runtime.json` is assembled by string interpolation, so `VERSION` content or the checkout path controls `source_root`** — `setup/claude-code/install.sh:457`
  What: `AP_VERSION="$(cat "$REPO_ROOT/VERSION" …)"` and `AP_SOURCE_ROOT` are interpolated into an unquoted heredoc at lines 459-466 with no JSON escaping; `setup/codex/install.sh:249` and `:563-569` do the same via `printf '%s'`. Neither escapes `"` or `\`. `ap_launcher.py` inserts `source_root` into `sys.path` and `runpy.run_module`s out of it (`platforms/python/ap_launcher.py:388-430`), and Python's `json.loads` keeps the *last* duplicate key.
  Why: A `VERSION` file containing `0.17.0", "source_root": "/tmp/evil` produces a syntactically valid manifest whose `source_root` is attacker-chosen, and every subsequent slash command then imports and executes code from that path — persisting after the original checkout is deleted. Being honest about reach: a user who runs `install.sh` from a hostile repo has already granted it code execution, so this is not a privilege-boundary crossing; its real value is (a) a persistent redirect that survives removal of the repo, and (b) the non-adversarial case — a checkout path containing `"` or `\` on Linux, or a stray character in `VERSION`, yields malformed JSON and the launcher reports itself broken. Both PowerShell installers use `ConvertTo-Json` and are safe, so this is a POSIX-only divergence.
  Fix: Build the manifest with `python -c` (already a hard dependency) or escape `\` and `"` before interpolation. Validate the written file parses before reporting success.

</details>

<details><summary><code>cursor</code> (Critical)</summary>

- **Shell `runtime.json` is unescaped string interpolation into JSON** — `setup/claude-code/install.sh:252` (same pattern at `setup/claude-code/install.sh:459` and `setup/codex/install.sh:249` / `setup/codex/install.sh:565`)
  What: `printf` / unquoted heredoc embed `source_root` and `version` with `%s` / `$VAR` and no JSON escaping. A checkout whose `VERSION` (or path) contains `"` can close the version string and inject a second `"source_root"`. CPython `json.load` keeps the last duplicate key. PowerShell uses `ConvertTo-Json` and is not affected.
  Why: `--global` writes `$HOME/.advanced-plans/runtime.json`, which `ap_launcher.py` consults for every project. A malicious clone can point the machine-wide runtime at an attacker-controlled tree (`platforms/python/…`) that outlives the clone.
  Fix: Write the manifest with `json.dump` (or equivalent) in all POSIX installers; never `printf` user/repo strings into JSON.

</details>

### C5. symlink against an existing skills directory creates a nested skills/skills link and prints success anyway
*Raised by `claude`, `cursor`*

<details><summary><code>claude</code> (Important)</summary>

- **`--symlink` against an existing skills directory creates a nested `skills/skills` link and prints success anyway** — `setup/claude-code/install.sh:298`
  What: `do_ln` runs `ln -sf "$REPO_ROOT/core/skills" "$GLOBAL_DIR/skills"`. When the destination already exists as a directory, `ln -sf` places the link *inside* it, producing `~/.claude/skills/skills -> …/core/skills`. Line 539 has the same call for the project install. The script then says `+ skills/ -> …/core/skills (symlinked)`.
  Why: The global branch never `mkdir`s `skills` in the symlink path, so on a fresh home this works — and on any machine that already has `~/.claude/skills/` (a previous copy-install, or any other skill source) it silently does the wrong thing while reporting the right thing. No skill is discoverable at the expected path, and nothing in the output distinguishes the two outcomes. Also note the PowerShell twin resolves the same situation by recursively deleting the tree (Critical above) — the two installers have opposite, both-wrong behaviours for identical input.
  Fix: Test the destination first: if it is an existing non-link directory, error out (or move it aside) rather than letting `ln -sf` reinterpret the operation; use `ln -sfn` once the destination is known to be a link.

</details>

<details><summary><code>cursor</code> (Important)</summary>

- **`--symlink` `ln -sf` does not replace an existing skills directory** — `setup/claude-code/install.sh:298` (and `setup/claude-code/install.sh:539`)
  What: POSIX `ln -sf target dest` when `dest` is a directory creates `dest/skills` instead of replacing `dest`. Self-install `rm -rf` first; `--symlink` does not. PowerShell `Do-Junction` removes first.
  Why: A second install with `--symlink` leaves the old copy in place and adds a nested link. Uninstall may then unlink the wrong node or leave a junction/copy mix.
  Fix: Unlink/remove `dest` if it exists (directory or link), then `ln -s`, matching `Do-Junction`.

</details>

## Single-reviewer findings (27)

*One model saw it and the others did not — either a real blind spot in the others, or a false positive. Adjudicate individually.*

### Critical

- **The collision check reports "shared; unchanged" for a destination with no overlapping filenames, so the installer silently installs nothing and then claims owne** — `claude` only
    What: `check_collision` returns 0 only when `$_dst` does not exist; otherwise it compares only files present in *both* trees and falls through to `return 2` ("identical, skip copy") at line 315. `Test-ApCollision` has the same structure (`setup/codex/install.ps1:122`, `:159`). A destination directory that exists but shares no filename with the source therefore reports as identical, the `do_cp` is skipped, and `write_ownership` still registers `codex` as an owner of that skill name.
    Why: If a user already has an unrelated `.agents/skills/schema-design/` (or `advanced-planning/`) from another vendor, the install prints `shared; unchanged: schema-design`, ships none of the skill, and records codex as its owner. The subsequent `uninstall.sh --yes` sees codex as the sole owner and `remove_path` does `rm -rf` on that third-party directory (`setup/codex/uninstall.sh:283`). That is deletion of a directory this installer never created, produced by a check whose stated purpose is "refusing to overwrite".
    Fix: Treat "destination exists but a source file is missing there" as a collision, not as identity — compare the file *sets*, not just the intersection. Separately, only register ownership for a skill this run actually installed or verified byte-identical.

- **Install writes follow dest symlinks; a malicious clone can retarget them** — `cursor` only
    What: `cp`, `cat >`, `[IO.File]::WriteAllText`, and `Copy-Item -Force` all follow a pre-existing symlink at `.advanced-plans/runtime.json`, `bin/ap.py`, `skill-ownership.json`, or `.claude/settings.json`. There is no `O_NOFOLLOW` / unlink-then-create. Self-install (`--project` on the clone) writes into that tree.
    Why: A hostile repo can plant those names as symlinks to `~/.bashrc`, `~/.ssh/authorized_keys`, etc. The installer then overwrites the symlink target with launcher JSON or Python. This is the reachable “unexpected write” from an untrusted checkout; `--global` is not this vector (it writes under the profile, not the clone).
    Fix: Refuse to write if the dest is a symlink/reparse point, or open with `O_NOFOLLOW` / create a temp file and `rename` over a non-link.

- **Claude uninstall always deletes the shared launcher — setup/claude-code/uninstall.sh:201 (and setup/claude-code/uninstall.ps1:175)** — `cursor` only
    What: Claude uninstall removes `.advanced-plans/bin/ap.py` and `runtime.json` with no ownership check. Codex/OpenCode share that directory (project and `~/.advanced-plans` for `--global`).
    Why: Uninstalling Claude Code after a Codex/OpenCode install bricks the other host: skills remain, `ap.py` is gone, invocations fail before any diagnostic. This is one host removing another host’s runtime, not a third-party JSON trick.
    Fix: Same KEEP/SharedOwners rule as Codex, keyed off `skill-ownership.json` (and treat Claude as an owner if you start recording it), or leave the launcher unless this process created a Claude-only marker.

- **Unquoted $REPO_ROOT in shell installers allows injection — install.sh:252, install.sh:459-466, codex/install.sh:249-250 embed $REPO_ROOT directly into JSON with** — `opencode` only
    What: The repo root path is interpolated into `runtime.json` without escaping.
    Why: An attacker who can create a directory with a name like `"; echo pwned; "` could inject malicious content into the JSON or, in the heredoc case, execute commands.
    Fix: Use `printf '%s' "$REPO_ROOT" | jq -Rs .` to properly JSON-escape the path, or validate the path contains only safe characters before embedding.

- **ap_subst infinite loop on self-referential replacement — install.sh:179-193 and codex/install.sh:168-182. If $_sub_n appears within $_sub_r, the loop never term** — `opencode` only
    What: The substitution loop does not check whether the replacement text itself contains the pattern.
    Why: While the current patterns (`python ".advanced-plans/bin/ap.py"`) do not contain themselves, a future change to a self-referential pattern would hang the installer.
    Why it matters concretely: This is a latent DoS in the installer — not currently exploitable, but a correctness bug that would block installs if the pattern ever changed.
    Fix: Add a guard: `if [ "$_sub_r" = *"$_sub_n"* ]; then return 1; fi` at function entry.

- **Remove-ApInstalledFrom traverses junctions despite the guard — uninstall.ps1:86-108. The function checks if $Dest is a reparse point, but Get-ChildItem -Literal** — `opencode` only
    What: The logic is correct as written, but the comment at line 88-96 describes a hazard that the code only partially mitigates — it relies on the early return at line 97-100 never being bypassed.
    Why: A future maintainer might "fix" the early return, not realizing it is the safety guard.
    Fix: Add an inline assertion: `if (Test-IsReparsePoint $Dest) { throw "Should have unlinked earlier" }` immediately before the `foreach` loop.

### Important

- **After a normal sole-owner uninstall the AGENTS.md fence is never removed** — `claude` only
    What: `remove_if_empty "$AGENTS_DIR"` (line 288) removes `.agents/` once its `skills/` child is emptied, and only then is `_agents_file="$AGENTS_DIR/../AGENTS.md"` tested with `[ -f ]`. A path through a deleted directory component does not resolve (verified), so `remove_agents_fence` returns immediately. `setup/codex/uninstall.ps1:243-244` fails the same way for a stronger reason: `Resolve-Path "$AgentsDir\..\AGENTS.md" -ErrorAction SilentlyContinue` returns `$null` when `.agents` no longer exists, and the call is skipped.
    Why: This is the *common* path — a user with only the codex adapter uninstalls, and their `AGENTS.md` keeps the `advanced-planning:codex` block forever, contradicting the file header's "remove what install.sh installed, and nothing else". The existing test misses it: `test_agents_md_fences_removed` runs on `shared_fixture`, where ownership is `['codex','opencode']`, so every skill is KEEP, `.agents/skills` is non-empty, `.agents` survives, and the fence removal works. `test_residual_trees_identical` in the sole-owner fixture passes because *both* languages leave the fence.
    Fix: Compute the AGENTS.md path from the project root passed in (not `.agents/..`), and remove the fence *before* `remove_if_empty "$AGENTS_DIR"`. Add the fence assertion to the sole-owner fixture.

- **Directory.Delete on a file symlink throws, aborting the claude-code uninstall after a self-install** — `claude` only
    What: `Remove-ApPath` routes every reparse point to `[System.IO.Directory]::Delete($Path, $false)`. In self-install mode `install.ps1:350-352` creates *file* symlinks for each agent `.md` in `.claude\agents\`. Those carry the `ReparsePoint` attribute but are not directories, and `Directory.Delete` calls `RemoveDirectory`, which fails with `ERROR_DIRECTORY`. With `$ErrorActionPreference = "Stop"` the whole uninstall aborts at the first agent.
    Why: A self-installed developer machine (the documented dev-mode workflow in CONTRIBUTING.md) cannot be uninstalled: commands and skills are removed, the run dies partway through agents, and `bin/ap.py` — deliberately ordered last — is never reached. That leaves precisely the "commands without a launcher" state the file header says it exists to avoid. Only triggers where symlink creation succeeded (Developer Mode or elevated); otherwise install fell back to `Copy-Item` and the path is a plain file.
    Fix: Branch on directory-ness first: `if (reparse -and (Get-Item).PSIsContainer) { Directory::Delete } elseif (reparse) { File::Delete } else { … }`.

- **A skill named Keys (or Values/SyncRoot) in the registry silently drops every third-party registration** — `claude` only
    What: `$skillsHash` is a `Hashtable`; `foreach ($k in $skillsHash.Keys)` uses member access, which resolves a *key* named `Keys` in preference to the `.Keys` property. Verified in PowerShell 7.6.5: with `$skillsHash["Keys"]=@("opencode")` present, that loop iterates `opencode` instead of the real key set, so the "keep non-approved-skill entries from other adapters" pass at line 201 runs zero real iterations.
    Why: This is the crafted-ownership-file subversion the review brief asks about, and it needs no malice — any adapter that registers a skill under one of those names causes codex's uninstall to rewrite `skill-ownership.json` containing only the approved-skill entries, erasing every other adapter's registration. The next uninstall by that adapter then sees zero owners and deletes shared files (chains into the fail-open issue above). The Python twin uses `data["skills"].items()` and is unaffected, so the two implementations disagree.
    Fix: `foreach ($k in @($skillsHash.PSBase.Keys))` — or build `$remainingSkills` from `$skillsHash.GetEnumerator()`.

- **A bare-string owner entry deletes the skill's files while leaving its registration behind** — `claude` only
    What: In the decision pass, `if not isinstance(owners, list): owners = []` discards a malformed `"skills": {"plan-todos": "opencode"}` entry, so the skill is treated as unowned and printed as `REMOVE` (line 219) → `rm -rf`. In the write-back pass at line 231 the *original* value is re-read and normalised to `["opencode"]`, so the registration is written back out.
    Why: The registry ends up asserting that `opencode` owns a skill directory that this run just deleted, and — because no skill was `KEEP` — `SHARED_OWNERS` stays 0 and the shared launcher goes too. The normalisation comment at line 228-231 says it exists to avoid destroying a third-party registration; it preserves the registration and destroys the files instead, which is the worse half. The PowerShell twin normalises in both passes and does not diverge this way.
    Fix: Normalise once, up front, before the decision pass — then both passes see the same value.

- **python is a hard, unchecked install-time dependency invoked at the last step** — `claude` only
    What: `write_ownership` shells out to `python` (bare, not `python3`). There is no preflight; on a distro where only `python3` exists, `set -e` aborts the installer after all skills have been copied and `AGENTS.md` merged.
    Why: The failure mode is a fully-installed adapter with *no* `skill-ownership.json`, which is the precise input that makes the uninstaller fail open and delete another adapter's skills (Critical above). The installer already validates `core/` and the routing skill up front; the interpreter deserves the same treatment.
    Fix: Preflight `command -v python || command -v python3` alongside the existing `core/` check, use the resolved name, and fail before any file is copied.

- **ConvertTo-Json can collapse owner lists to a string; POSIX install then drops other owners — setup/codex/install.ps1:282 (same write in setup/codex/uninstall.ps** — `cursor` only
    What: Windows PowerShell often serialises a one-element array as a JSON string. `write_ownership` in `setup/codex/install.sh:427` does `if not isinstance(existing, list): existing = []`, then appends `"codex"`.
    Why: After a PS install/uninstall, a later `install.sh` can replace `["opencode"]` with `["codex"]` and the next Codex uninstall will delete skills OpenCode still needs. Uninstall’s I.4 path normalises strings; install does not.
    Fix: Emit arrays with `ConvertTo-Json` (`-AsArray` / wrap) and in POSIX install normalise a bare string to `[existing]` like uninstall, never to `[]`.

- **KEEP/REMOVE is a |-delimited stdout protocol** — `cursor` only
    What: Python prints `KEEP|skill|{','.join(owners)}`. The shell splits on `|`. An owner string containing `|` or a newline becomes extra records (e.g. a fake `REMOVE|plan-todos|`).
    Why: Anyone who can write `skill-ownership.json` (or a merge that copies attacker strings into owners) can make uninstall delete skills that still have other owners. PowerShell does not use this channel. Not reachable from a clone unless that clone is also the `--project` tree and already got a write into the registry.
    Fix: NUL-delimited or JSON lines for decisions; never interpolate owner names into a `|` grammar.

- **SharedOwners only looks at this adapter’s approved skill names — setup/codex/uninstall.ps1:134 (and setup/codex/uninstall.sh:200)** — `cursor` only
    What: KEEP (and therefore keeping `ap.py`) runs only for names in the hardcoded approved list. A remaining third-party skill in the same registry does not set the flag (I.1 leaves the foreign entry and still allows launcher removal).
    Why: After Codex is the last *approved* owner, `ap.py` is removed while non-approved skills that use the launcher stay on disk, inert.
    Fix: Keep the launcher if any remaining `skills.*` owners are non-empty, not only approved-list KEEP.

- **Set-ApCallSites / ap_rewrite_call_sites splice the launcher into quoted command text — setup/claude-code/install.ps1:115 (and setup/claude-code/install.sh:233)** — `cursor` only
    What: The absolute launcher is concatenated into `python "…"` and `runpy.run_path(r'…')` with no escaping. The path comes from `USERPROFILE`/`HOME`.
    Why: A `"` or `'` in the profile path breaks the quoting in every globally installed command/skill. Those snippets are later executed by the host agent. Not repo-controlled; alarming if the environment is untrusted. Empty home is already refused.
    Fix: Reject launcher paths containing quotes/newlines, or emit JSON/`repr`-safe literals.

- **settings.json overwrite loses user hooks — claude-code/install.ps1:435-454 and install.sh:565-582. The installer writes settings.json unconditionally, but the c** — `opencode` only
    What: The installer overwrites a user's `settings.json` that may contain unrelated configuration.
    Why: User loses custom tool permissions, allow rules, or other settings they added.
    Fix: Read existing `settings.json`, merge the `planning` block and extend `permissions.allow` with the four rules, then write back. Only create fresh if absent.

- **project argument parsing in uninstall.sh is fragile — uninstall.sh:229-232. The line if [ -n "${2:-}" ] && [ "${2#--}" = "$2" ]; then PROJECT_DIR="$2"; shift; f** — `opencode` only
    What: A user could accidentally pass `--yes` as the project path.
    Why: The script would then attempt to uninstall from a directory literally named `--yes` (which fails `test -d`), but the error message would be confusing.
    Fix: Add an explicit check: `case "$2" in --*) echo "Error: --project requires a path" >&2; exit 1;; esac`.

- **Collision check hashes temp files in place, leaving them readable — codex/install.ps1:134-140 and codex/install.sh:283-289. The temp file created by [System.IO.** — `opencode` only
    What: Sensitive launcher paths are written to the system temp directory.
    Why: On a multi-user machine, another user could read the temp file before it is deleted (lines 143-144, 294-296).
    Fix: Create the temp file in a private directory (`$env:TEMP` with restricted ACLs on Windows, `mktemp -d` with `chmod 700` on Unix), or avoid writing the rewritten content to disk by comparing in memory.

- **remove_agents_fence in codex/uninstall.sh uses non-portable sed — uninstall.sh:153-154. The command sed '/^$/N;/^\n$/d' is GNU-specific; BSD/macOS sed would fai** — `opencode` only
    What: The cleanup of blank lines after fence removal behaves differently or fails on macOS.
    Why: Users on macOS get a malformed `AGENTS.md` with extra blank lines, or the script exits non-zero.
    Fix: Use a portable approach: `sed -e '/^$/N;/^\n$/d'` works on GNU sed but not BSD; better to skip this cleanup entirely or use a Python one-liner.

### Minor

- **PowerShell scaffold writes a PowerShell literal into YAML, with a BOM and no trailing newline** — `claude` only
    What: The here-string emits `active_branches: @()` where the POSIX twin (`setup/codex/install.sh:~600`) emits `active_branches: []`; line 458 writes it with `Out-File -Encoding UTF8 -NoNewline`, which in Windows PowerShell 5.1 prepends a BOM — the same defect the runtime.json code two hundred lines earlier goes out of its way to avoid with `UTF8Encoding::new($false)`.
    Why: `@()` parses as the string `"@()"`, not a list, so any consumer of `PLANNING.md`'s `active_branches` gets a string; and a leading BOM ahead of `---` breaks frontmatter detection for a plain-utf-8 reader. Two installers produce materially different `PLANNING.md` for the same command.
    Fix: `[]`, and `[System.IO.File]::WriteAllText(… , [System.Text.UTF8Encoding]::new($false))` with a trailing newline, matching the runtime.json path in the same file.

- **remove_installed_from is defined and never called** — `claude` only
    What: 30 lines implementing the source-derived removal and the `[ -L ]`-before-`[ -d ]` link guard, dead since ownership-based removal replaced it.
    Why: It is the most security-relevant-looking function in the file, so a reader (or reviewer) reasonably assumes the codex uninstall is protected by its link guard when in fact all removal goes through `process_ownership` → `remove_path`.
    Fix: Delete it, or route the skills removal through it.

- **The AGENTS.md fence removal rewrites the whole file and resets its permissions** — `claude` only
    What: `sed '/^$/N;/^\n$/d'` is applied to the entire file, not the fence region, collapsing blank-line runs anywhere in the user's document; the result is then `mv`d from `mktemp` (mode 0600) over `AGENTS.md`, replacing the original file's mode and ownership. The PowerShell twin's `\n{3,}` → `\n\n` also rewrites globally, and is a no-op on CRLF files, so the two produce different output.
    Why: `AGENTS.md` is a user-authored, usually version-controlled file; an uninstall reformatting it and making it group-unreadable is an unrequested mutation, and shows up as spurious diff noise.
    Fix: Edit in place preserving the inode (write via a temp in the same directory, `cat > "$_agents_file"`, or `cp --preserve=mode`), and restrict the blank-line cleanup to the junction left by the removed fence.

- **The PowerShell claude-code installer creates no .advanced-plans/ scaffold files** — `claude` only
    What: The `else` branch creates `phases/specs/state/logs` and runs the legacy migration, but unlike `install.sh:393-434` it never writes `PLANNING.md` or `README.md`.
    Why: A Windows-installed project has no programme dashboard, so the first `/loop-status` or `/next-loop` has nothing to read — a platform-dependent difference in what "installed" means.
    Fix: Port the two heredocs, using the BOM-free writer already in the file.

- **PROJECT_REAL is computed and never used** — `claude` only
    What: Dead assignment; `setup/codex/install.sh:~608` has the identical dead line.
    Why: It reads as though the project path is being canonicalised before use, which it is not — every later use is the raw `$PROJECT_DIR`.
    Fix: Remove it, or use it as the canonical project path (the latter would also make self-install detection agree with the resolved path).

- **Inconsistent error messages — install.ps1:73 says "Run Get-Help .\install.ps1" while install.sh:104-105 says "Run this script from the advanced-planning root". ** — `opencode` only

- **$SelfInstall is set but never used in install.ps1 — Lines 26-27, 225-228 set it, but the self-install branch at line 322 checks it only for messaging. The actua** — `opencode` only

- **Do-Copy uses -Force — install.ps1:50-56. This overwrites existing files without warning, which is intentional for idempotency but should be documented in the fu** — `opencode` only

## Strengths noted

**`claude`**

- The uninstallers' central design choice — remove a *known set of names derived from the checkout* rather than `rm -rf` a directory — is correct and is what makes the shared `.advanced-plans/` directory safe to uninstall from. `remove_if_empty` / `Remove-ApDirIfEmpty` refusing to delete a directory the uninstall did not empty is the right guard.
- The reparse-point/symlink guard ordering is genuinely right: `Remove-ApInstalledFrom` checks `Test-IsReparsePoint $Dest` *before* `Get-ChildItem` walks it (`setup/claude-code/uninstall.ps1:96-99`), and `remove_installed_from` checks `[ -L "$_dest" ]` before `[ -d ]` (`setup/claude-code/uninstall.sh:141-146`). Without that ordering both would resolve names through the junction and delete the user's checkout. The comments explain exactly why, and the `-L`-before-`-d` ordering in `remove_path` is also correct.
- Dry run is genuinely non-mutating on every path I traced in all four installers/uninstallers: `Do-MkDir`/`Do-Copy`/`do_cp`/`do_mkdir` gate, the migration block gates, `runtime.json`/`settings.json`/scaffold writes gate, `Set-ApCallSites`/`ap_rewrite_call_sites` are skipped, and `Remove-ApPath`/`remove_path` return before deleting. The only writes under dry run are to `%TEMP%`/`mktemp` inside the collision check.
- `ap_rewrite_call_sites` avoiding `sed -i` for a measured MSYS CRLF reason, and never opening a file that contains no call site, is a real correctness win over the obvious implementation — and it is pinned by `test_line_endings.py` / `test_rewrite_preserves_crlf`.
- The ownership *design* (drop this adapter's registration, keep the files while another owner remains, keep `ap.py` when `SHARED_OWNERS`) is the right shape, and `SHARED_OWNERS` being deliberately separate from `KEPT` is a subtle correctness point that the comment calls out.
- `test_adapter_lifecycle.py` is unusually good for installer code — real subprocess runs of both languages, differential sh-vs-ps1 comparison, foreign-registration survival.

**`cursor`**

Home resolution prefers `USERPROFILE` then `$env:HOME`/`HOME`, and refuses an empty home instead of installing at `/`. Codex/OpenCode uninstalls treat destination junctions/symlinks as unlink-only before walking names, keep planning artefacts, and default to dry-run until `--yes`/`-Yes`. Call-site rewrite avoids `sed -i` (CRLF). Ownership merge is tested for well-formed and string-shaped third-party entries (`test_adapter_lifecycle.py` I.1–I.4). Codex `--global` writes `skill-ownership.json` specifically so a later uninstall does not see an empty owner list.

**`opencode`**

1. **Junction/symlink handling is excellent** — The uninstall scripts correctly detect reparse points and unlink rather than recurse, preventing deletion of the source checkout. The guards in `uninstall.ps1:87-100` and `uninstall.sh:107-110` are well-reasoned.

2. **Dry-run default is a strong safety pattern** — Both uninstall scripts require explicit confirmation (`-Yes`/`--yes`) before acting, with clear messaging about what would be deleted.

3. **Ownership tracking for shared skills** — The `skill-ownership.json` mechanism in the codex uninstallers correctly prevents one adapter from removing another's skills, with proper merge logic.

4. **Home resolution consistency** — Both install and uninstall scripts use the same `USERPROFILE` → `HOME` → `$HOME` fallback chain, pinned by tests.

5. **Call-site rewriting preserves line endings** — The shell installer's `ap_rewrite_call_sites` function correctly handles trailing newlines and avoids `sed -i` on Windows due to text-mode issues.

## Recommendations

**`claude`**

- **The two languages need differential tests for the destructive paths, not just the residual trees.** `test_residual_trees_identical` passes when both implementations are wrong in the same way (the AGENTS.md fence). Add assertions on *what should be gone*, not only on sh-vs-ps1 agreement.
- **The ownership registry needs a schema check, not a try/except.** Validate `schema_version`, that `skills` is an object, and that every value is a list of strings — then refuse to act on anything else. Three of the findings above (fail-open, bare-string owners, `Keys` shadowing) are one validation function away from being impossible.
- **The approved-skills list is duplicated in four places** (`setup/codex/install.sh:36`, `install.ps1:33`, `uninstall.sh:174`, `uninstall.ps1:114`). If uninstall's list drifts behind install's, the drifted skill is orphaned on disk *and* left in the registry. Since `python` is already a hard dependency, read the list from one JSON file.
- On TOCTOU specifically: `Remove-ApPath`'s check-then-delete and `remove_path`'s `[ -L ]`/`[ -d ]`/`[ -f ]` cascade are races in principle, but every target is under the invoking user's own `$HOME` or project, so an attacker who can win the race can already write those paths directly. I do not consider this reachable and would not change it.

**`cursor`**

Give Claude Code an ownership token (or a dedicated runtime refcount) so uninstall of one adapter cannot drop `ap.py`. Add a test: Codex+Claude in one project, Claude uninstall, Codex still runs. Add a test: missing/malformed `skill-ownership.json` must not delete shared skills. Drive all `runtime.json` writes through one Python helper used by every POSIX installer.

**`opencode`**

1. **Add a preflight check for path safety** — Before embedding `$REPO_ROOT` in JSON, validate it contains no quotes, backslashes (on Unix), or shell metacharacters. Fail with a clear message if the checkout path is unsafe.

2. **Merge `settings.json` instead of overwriting** — Treat `settings.json` as user-owned; only add the planning hooks and permission rules. This aligns with the stated intent in the uninstall scripts.

3. **Add regression tests for junction/unlink behavior** — The comments describe threats that were "not reproduced" on current PowerShell versions. Add a CI test that creates a junction, runs the uninstall, and verifies the target files survive.

4. **Document the `--symlink`/`-Symlink` limitation** — The shell installer supports `--symlink` for skills only in the global install path, but the project install path uses it differently. Clarify in the usage header.

## Assessments verbatim

**`claude`**

**Ready to merge?** No

**Reasoning:** Four defects cause unrequested destruction of files the installer did not create — silent replacement of an existing `.claude/settings.json`, `rm -rf` of a third-party skill directory reached via a collision check that mistakes "no overlapping filenames" for "identical", removal of another adapter's skills and the shared launcher whenever the ownership registry is absent or unparseable, and recursive deletion of `~/.claude/skills/` under `-Global -Symlink`. The first is also an interface lie, since both uninstallers justify their behaviour with a claim about the installer that is false of these files.

**Confidence:** High — I read all eight files, confirmed the POSIX path-resolution and PowerShell hashtable behaviours by running them (`[ -f missing/../x ]` false; `@{}.PSObject.Properties.Name` returns the adapter properties; a key named `Keys` shadows `.Keys` in `foreach`), traced `source_root` into `sys.path`/`runpy` in `ap_launcher.py`, and confirmed the AGENTS.md test gap by reading `shared_fixture` in `test_adapter_lifecycle.py`. Two items I reasoned about rather than executed, since proving them requires mutating the filesystem: `[System.IO.Directory]::Delete` throwing on a file symlink (documented `RemoveDirectory` behaviour; the finding is also conditional on symlink creation having succeeded during self-install), and `ln -sf` placing the link inside an existing destination directory. I did not review `setup/opencode/`, which was excluded from the envelope; per the brief, every codex finding above should be assumed to apply there.

**`cursor`**

**Ready to merge?** No

**Reasoning:** Unescaped POSIX `runtime.json`, symlink-following writes on self-install, Claude’s unconditional launcher/settings clobber, and fail-open ownership on uninstall are exploitable or directly destructive across hosts; they are not style nits.

**Confidence:** High — reviewed the eight target files plus `ap_launcher.py` resolution and `test_adapter_lifecycle.py` ownership cases. Did not execute the scripts. Did not open `setup/opencode/*` (assumed to match Codex per the brief). Did not verify `Remove-Item -Recurse` vs junctions on this Windows build.

**`opencode`**

**Ready to merge?** With fixes

**Reasoning:** The scripts are well-engineered with strong safety properties (dry-run default, junction handling, ownership tracking), but the unquoted `$REPO_ROOT` in JSON is a genuine injection vulnerability, and the `settings.json` overwrite is a data-loss risk. Both are straightforward to fix.

**Confidence:** High — I have read all eight files in full. The only unverified aspects are platform-specific behaviors (e.g., BSD `sed` compatibility, macOS symlink handling) that I inferred from the code structure and comments.

---

*Grouping is mechanical — by file, exact or nearby line, and title word overlap. It is tuned to under-merge rather than over-merge, so the same issue may appear twice under different wording. Raw reviews are in this directory as `review-<model>.md`.*
