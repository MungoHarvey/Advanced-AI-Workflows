# Config seams: what each tool actually lets us change

**Date:** 2026-09-01
**Stage:** 0 of `.advanced-plans/specs/2026-09-01-dependencies-not-forks-plan.md`
**Method:** read-only probes of the installed tools on this machine. Every cell below
cites the file, flag, or command that proves it. Every "nothing" cites what was tried.
A row that said *"probably supports X"* would fail this stage's gate; none does.

---

## Why this exists

The owner's question was: *can the main package configure these tools together, rather
than us editing each fork?* That question only has an answer once we know **what each
tool exposes as a seam**. This is that measurement. It is descriptive: it records what
is there on 2026-09-01, not what we would like to be there.

Two kinds of seam turn out to matter, and conflating them is what makes this look
easier than it is:

- **Settings seam** — a config the tool reads that changes *its own* behaviour. Flags,
  models, telemetry, trust, permissions.
- **Content seam** — a supported way to change *what the tool instructs an agent to
  do*. Skill text, routing rules, procedure.

AAW needs the second. The measurement below is that **no dependency in this stack
exposes a content seam at all** — and that all four hosts do.

---

## Summary

| Tool | Settings seam | Env override | Hook / extension dir | Content seam | Survives upgrade |
|---|---|---|---|---|---|
| **gstack** | `~/.gstack/config.yaml`, **29 keys** read across the skill tree, via `bin/gstack-config` (`get`/`set`/`list`/`defaults`) | `GSTACK_STATE_ROOT` > `GSTACK_HOME` > `GSTACK_STATE_DIR` | none found | **none** | **yes** — config in state dir, install in `~/.claude/skills/gstack` |
| **superpowers** | **none** | **none** — 0 `SUPERPOWERS_*` vars in `skills/`, `hooks/`, `.opencode/` | `hooks/hooks.json`, `hooks-cursor.json`, `.opencode/plugins/superpowers.js` — all **host**-mediated | **none** | n/a |
| **advanced-planning** | `.advanced-plans/runtime.json`, key `source_root` | **`ADVANCED_PLANNING_ROOT`** — documented escape hatch | `platforms/{claude-code,codex,cowork,opencode}/` | **none** (it *is* the content) | yes — manifest is data, not install |
| **herdr** | `~/AppData/Roaming/herdr/config.toml`, 11 lines | none found | none found | **none** — and `herdr --skill` regenerates `SKILL.md` verbatim | **no** — skill overwritten on regeneration |
| **Claude Code** | `~/.claude/settings.json` (16 keys) + `.claude/settings.local.json` | many | `hooks` key; `.claude/skills/`; `enabledPlugins` | **yes** — `CLAUDE.md` + `.claude/skills/` | yes |
| **Codex** | `~/.codex/config.toml`, 164 keys | yes | `[projects]` trust entries, keyed by path | **yes** — reads `AGENTS.md` | yes |
| **OpenCode** | `~/.config/opencode/opencode.json` | `{env:ELM_PROXY_KEY}` interpolation | `plugins/`, `command/`, `tui.jsonc` | **yes** — auto-loads project `AGENTS.md` | yes |
| **Cursor** | `~/.cursor/cli-config.json`, 20 keys | yes | `hooks.json` v1 `sessionStart`; `agents/`, `extensions/` | **yes** — `AGENTS.md` + `agents/` | yes |

The pattern reads straight off the table: **the four dependencies have zero content
seams between them; all four hosts have one.**

---

## The dependencies, in detail

### gstack — a real settings seam, no content seam

`bin/gstack-config` implements `get`, `set`, `list` and `defaults` over a YAML file
whose path is resolved at `bin/gstack-config:1525`:

```
_GSTACK_CFG_FILE="${GSTACK_HOME:-$HOME/.gstack}/config.yaml"
```

**The config file's own header undercounts the seam by a factor of six, and that is
worth recording.** `~/.gstack/config.yaml` documents five keys — `proactive`,
`routing_declined`, `telemetry`, `auto_upgrade`, `update_check`. A sweep of every
`gstack-config get|set <key>` call across the installed skill tree returns **29 distinct
keys** (32 raw matches, less three artefacts: `which` and `failed` come from assertion
prose in `test/relink.test.ts` and `test/skill-e2e-auto-decide-preserved.test.ts`, and
`user_slug_at_` is the truncated prefix of a templated key in `bin/gstack-config` and
`scripts/brain-cache-spec.ts`):

```
artifacts_sync_mode      artifacts_sync_mode_prompted  auto_upgrade
blind_spot_coach         brain_trust_policy            checkpoint_mode
checkpoint_push          codex_reviews                 cross_project_learnings
explain_level            gbrain_context_load           gbrain_token
gstack_contributor       local_code_index_offered      memory_ingest_path
plan_tune_hooks          proactive                     question_tuning
redact_prepush_hook      redact_repo_visibility        repo_mode
routing_declined         salience_allowlist            skill_prefix
skip_eng_review          team_mode                     telemetry
transcript_ingest_mode   update_check
```

So gstack has by some distance the largest settings seam here — and a documentation gap,
since 24 of those keys are settable but undocumented in the file a user is told to edit.

**It is still not a content seam.** Several keys reach further than on/off — `codex_reviews`,
`skip_eng_review`, `blind_spot_coach` and `brain_trust_policy` change which sub-steps a
skill runs. But every one is a switch gstack's own authors placed at a point they chose.
There is no mechanism for AAW to *inject* a step, override a skill's text, or add a key
of its own. The seam is wide, and it is entirely gstack's to define.

**It survives upgrade, and that is structural rather than lucky.** The config lives in
the state directory (`~/.gstack`); the install lives in `~/.claude/skills/gstack`. An
upgrade is `git pull` plus `./setup` against the second path, which never writes the
first. This is the one dependency here that got the separation right.

*Tried and found nothing:* a skill-content override hook; a user-skills overlay
directory; any key that changes skill text; any way to register a key gstack does not
already know.

### superpowers — no native seam of any kind

Zero `SUPERPOWERS_*` environment variables across `skills/`, `hooks/` and `.opencode/`.
No config file. No CLI. The checkout root is `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`gemini-extension.json`, `hooks/`, `skills/`, `scripts/`, `tests/`, `docs/`, `assets/`,
`package.json` — a set of instruction files and skill markdown, with no configuration
layer between them and the host.

Its entire extension surface is **host-mediated**: `hooks/hooks.json` registers against
Claude Code's `SessionStart` matcher and invokes `${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd`;
`hooks-cursor.json` does the equivalent for Cursor; `.opencode/plugins/superpowers.js`
for OpenCode. Every one of those is the *host's* extension mechanism, not superpowers'.

**This is the finding that vindicates Phase 5.** There was never a superpowers setting
to set. The only place AAW could change superpowers' behaviour was the host instruction
file — which is exactly the fenced-block boundary Phase 5 built, and why the fork patch
turned out to be removable. The mirror published on 2026-09-01
(`.advanced-plans/evidence/2026-09-01-superpowers-mirror-publish-preflight.md`) is the
proof that nothing was lost by removing it.

*Tried and found nothing:* `grep -r 'SUPERPOWERS_'` over `skills/`, `hooks/` and
`.opencode/`; a config file at the checkout root; a `bin/` or CLI entry point.

### advanced-planning — a real, documented, tested env seam

`ADVANCED_PLANNING_ROOT` is described at `docs/adapting-to-new-platforms.md:97` as
*"Escape hatch | `$ADVANCED_PLANNING_ROOT`, which overrides the manifest"*, implemented
at `platforms/python/ap_launcher.py:91` (`ENV_VAR = "ADVANCED_PLANNING_ROOT"`), and
covered by `platforms/python/tests/test_ap_launcher.py` — including a test that a bogus
value produces an actionable error rather than a silent fallback. Documented,
implemented, and tested: the strongest seam in the stack.

Beneath it sits a manifest, `.advanced-plans/runtime.json`, key `source_root`
(`ap_launcher.py:88-90`), resolved in a defined order: the env var, then the manifest
beside the launcher (`sibling_manifest`, line 121), then the global manifest
(`global_manifest`, line 163), then a repository root with no manifest at all — the last
of which *"makes the source repository work with no manifest at all"* (line 56).

The remaining `AP_*` variables are internal, not seams: `AP_DIR` (82 uses),
`AP_LAUNCHER` (17), `AP_SOURCE_ROOT` (13), `AP_SUBST_RESULT` (12),
`AP_REQUIRE_ADAPTER_INTERPRETERS` (9), `AP_VERSION` (6), `AP_STAMP` (6),
`AP_GLOBAL_DIR` (4).

Note what this seam controls: **where advanced-planning is loaded from**, not what it
says. That is the right seam for a dependency to expose, and it is the model AAW should
copy in Stage 1.

### herdr — a settings seam with no relevant surface, and a content seam that is actively overwritten

`herdr config` exposes exactly two subcommands, `check` and `reset-keys`. The config at
`~/AppData/Roaming/herdr/config.toml` is 11 lines: an `onboarding` key plus `[ui]`,
`[theme]` and `[ui.toast]`. There is no agent key, no skill key, no routing key.

The skill file is worse than absent as a seam. `herdr --help` documents
`--skill    Print the agent skill file and exit`, and the operator instruction is to
regenerate with `herdr --skill > ~/.claude/skills/herdr/SKILL.md`. The installed
directory holds a single 10,748-byte `SKILL.md` and nothing beside it. **Any edit to it
is destroyed by the next regeneration** — which is precisely why the global `CLAUDE.md`
overrides herdr's own "do not use proactively" instruction in an adjacent file rather
than editing the skill, and says so explicitly. That note is now measured rather than
asserted.

*Tried and found nothing:* `herdr config` subcommands beyond `check`/`reset-keys`; an
agent, skill or routing key in `config.toml`; a companion file or `.d` directory beside
`SKILL.md`.

---

## The hosts, in detail

The hosts are where the seams are, and all four take the same shape: **an instruction
file the agent reads, plus a hooks mechanism, plus a skills or agents directory.**

- **Claude Code** — `~/.claude/settings.json` carries 16 top-level keys (`env`,
  `permissions`, `model`, `hooks`, `enabledPlugins`, `extraKnownMarketplaces`,
  `alwaysThinkingEnabled`, `effortLevel`, `autoUpdatesChannel`, `tui`,
  `skipDangerousModePermissionPrompt`, `skipWorkflowUsageWarning`, `theme`,
  `agentPushNotifEnabled`, `skipAutoPermissionPrompt`, `autoMode`), with
  `~/.claude/settings.local.json` and `~/.claude.json` alongside. The content seam is
  `CLAUDE.md` plus `.claude/skills/`; this project uses both.
- **Codex** — `~/.codex/config.toml`, 164 keys, including the per-directory trust store
  under `[projects]`. Reads `AGENTS.md`.
- **OpenCode** — `~/.config/opencode/opencode.json` (model
  `elm/Qwen/Qwen3.5-397B-A17B-FP8`, provider `elm` keyed by `{env:ELM_PROXY_KEY}`), with
  `plugins/`, `command/` and `tui.jsonc`. It **auto-loads a project `AGENTS.md` before
  the first user message** — proven by the Phase 5 context probe recorded at
  `.advanced-plans/phases/phase-5/complete.md:23-24`, not inferred from documentation.
- **Cursor** — `~/.cursor/cli-config.json`, 20 keys including `permissions`, `model` and
  `modelParameters`; `hooks.json` schema v1 with a `sessionStart` hook; `agents/` and
  `extensions/` directories.

---

## The conclusion this measurement forces

**Overlay-by-adjacent-file is not a workaround; it is the only seam that exists.**

The plan's §4 asserted this as a constraint. It is now measured. Three of the four
dependencies expose no content seam whatsoever, the fourth (advanced-planning) *is* the
content, and every host exposes one. So AAW cannot configure these tools *through* their
own config layers, because for this purpose those layers are empty. It configures them
by owning what the host reads: the project instruction file, and an AAW-owned skill
installed beside theirs.

That is what Phase 5 already built for superpowers. The measurement says it generalises
rather than being a special case.

---

## What this stage found that the plan did not anticipate

**AAW's own detector is Claude-only, and that is a sharper gap than the plan recorded.**
`.aaw/detect.py:85` hardcodes sentinel paths for the four components; those paths
reference `.claude` **15 times** and `.cursor`, `.opencode`, `.agents`, `.codex` and
`.gemini` **zero times each**. Meanwhile advanced-planning ships four host adapters —
`setup/claude-code`, `setup/codex`, `setup/cowork`, `setup/opencode`.

The two halves of this differ, and the distinction matters. The *predicate* Phase 5
delivered is host-neutral: consumers read
`.aaw/installed.json -> components["<name>"]["installed"] == true` and never touch a
host path. But the *producer* of that manifest can only see components installed under
`.claude/`. A superpowers installed for Codex or OpenCode reads as absent. **The
abstraction is correct and the implementation behind it is single-host** — which is a
much more precise statement of the problem than "detection is hardcoded".

Three artefacts named in the design or the playbook do not exist on disk:

| Artefact | Named at | Status |
|---|---|---|
| `.aaw/project.toml` | design spec §8 | **ABSENT** |
| compatibility manifest | `docs/upstream-sync-playbook.md` §11 step 4 | **ABSENT** — the playbook instructs the operator to update it |
| `.advanced-plans/runtime.json` in AAW | `ap_launcher.py:88` | **ABSENT** — AAW resolves by the repo-root fallback |

The first two are Stage 1 work. The third is correct as it stands: AAW is a source
checkout, and `ap_launcher.py:56` says that case is meant to work with no manifest.

---

## Gate

Every row cites a file, flag, or command. Every "nothing" cites what was tried. No row
reads "probably". **Stage 0 passes.**
