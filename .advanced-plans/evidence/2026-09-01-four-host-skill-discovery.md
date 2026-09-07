# Four hosts, one project: the phase's headline criterion fails, and now with a mechanism

**Date:** 2026-09-01
**Todo:** `loop-005-4` (phase 6, controller collects; each host reports for itself)
**Fixtures:** `scratchpad/loop-005-4/run/fixture-a` and `fixture-b`, scratch projects outside both checkouts
**Adapters under test:** `setup/{claude-code,codex,opencode,cursor}/install.sh` from herdr worktree `loop-005-cursor`
**Hosts:** codex 0.152.0 (`gpt-5.6-sol`, xhigh, read-only), opencode (Qwen), claude, cursor-agent

---

## The outcome, first

The criterion is *"every target host discovers the SAME named core planning skills, not
host-specific copies that have drifted."* It **fails**, and the interesting part is that
it does not fail the way the todo anticipated. The files are identical. What differs is
**which copy each host actually reads.**

| Host | HOME | Discovered `phase-plan-creator`? | Which copy, by its own quoted token |
|---|---|---|---|
| codex | fake | yes | `.agents/skills` — the copy its own adapter installed ✅ |
| opencode | fake | yes | **`.claude/skills`** — claude-code's copy, not its own ❌ |
| claude | real | yes | **neither** — the global `~/.claude/skills` copy ❌ |
| cursor | real | **no** — never listed it | n/a; served global skills ❌ |

One host of four reads the copy its adapter installed. The bodies never drifted; the
*resolution* did.

---

## What each check returned

**Check 1 — install all four into one project and list what each discovers.** Done.
Fixture A: four adapters into one project, every `install.sh` exit 0, fake HOME holding
**0 entries before and 0 after** — the installers wrote nothing outside the project.

**Check 2 — the name set is identical across all four. FAIL, in both directions.**

- `claude-code` (`.claude/skills`, 9) carries `companion-detection` and `permission-config`
  that the others lack — deliberately: `APPROVED_SKILLS` in the other three installers
  excludes them by name.
- `codex`/`opencode`/`cursor` (`.agents/skills`, 8) carry `advanced-planning`, the shared
  routing skill, which claude-code does not install because it routes via
  `.claude/commands/` (12 slash commands) and writes no fence at all.

So the failure is structural, not drift. Two hosts, two routing designs. **This check is
stricter than the criterion it serves** — the phase asks about *core planning* skills, and
those are identical; the extra names are host-scoped by design. Recorded as a defect in
the check, not in the product.

**A comparison that could not fail, disclosed as such.** Three of the four hosts read the
*same directory*: `.agents/skills`. Comparing codex to opencode to cursor compares a
directory with itself. `compare.py` prints those pairs as **CANNOT FAIL** and refuses to
count them as passes; only `.claude/skills` vs `.agents/skills` has a subject.

**Check 3 — content identical by digest. PASS over 7 shared names, byte-identical.**

| Skill | sha256 (first 16) |
|---|---|
| `phase-plan-creator` | `6c04c90fdc8fa82e` |
| `plan-skill-identification` | `c9c5fb19f121bc64` |
| `plan-subagent-identification` | `790f2d9afe37f686` |
| `plan-todos` | `71989ea0178bd73e` |
| `progress-report` | `c4a13a7b68c1ebcc` |
| `ralph-loop-planner` | `c1609b8140e11d85` |
| `schema-design` | `21e77ab42da375e6` |

The shared-name count is printed, and a zero would have been reported **VACUOUS** rather
than as a clean sweep. It is 7.

**Check 4 — run under a fake HOME. CANNOT BE HONOURED, and that is a measurement.**

The todo asks for a fake HOME so a globally installed copy cannot supply the answer. On
this machine, three of four hosts defeat it, each differently:

- **claude** under a fake HOME exits 1, `Not logged in · Please run /login`. The fake HOME
  strips its credentials.
- **cursor** under a fake HOME exits 127: `no bundled CLI found under <fakehome>\AppData\Roaming\Cursor\...`.
  Its launcher resolves its own binary relative to the profile.
- **codex** starts fine but **ignores the fake HOME for skill discovery**. Its own stderr
  names the real profile while `HOME` and `USERPROFILE` both point elsewhere:
  `failed to load skill C:\Users\mharvey2\.agents\skills\hook-converter-template\SKILL.md`.
  Two such lines per run. Whatever codex resolves the global skills directory from on
  Windows, it is neither environment variable.
- **opencode** is the only host the fake HOME actually isolates.

So check 4's stated mechanism does not work here. **The per-surface canary is the
substitute**, and it is strictly stronger: it does not care where a host looks, because
only one specific file on disk contains the string it has to quote.

---

## The instrument was wrong twice before it was right

Both failures were mine, and both were caught by the hosts rather than by me.

**First: the canary produced invalid YAML.** `description:` is a *double-quoted* scalar,
and the injection appended the token after the closing quote. codex named it exactly —
`invalid YAML: did not find expected key at line 2 column 427` — and both codex and
opencode then correctly refused the skill. The run read as a discovery failure when it was
an instrument failure. Fixed by injecting *inside* the scalar, and the injector now
**re-parses the frontmatter with PyYAML and confirms the token survives into the parsed
`description` before it writes anything.**

**Second: the token was truncated away.** With valid YAML, codex listed
`phase-plan-creator` and still answered `TOKEN=ABSENT`, alongside its own warning:
*"Skill descriptions were shortened to fit the skills context budget."* The token sat at
the end of a long description. A probe point the host is free to discard measures the
budget, not the discovery. Moved to the front of the scalar; codex then quoted it.

Both are the phase's defect class pointed at me: a check whose subject is a string the
check itself constructed. The one thing that went right is that neither failure was
silent.

**A third, smaller one worth recording:** I ran `grep -c` against a probe output that did
not exist, got `0`, and nearly reported it as "codex stayed inside the fake HOME". A grep
over a missing file and a grep over a clean file both return zero. Caught before it
entered the record; it is the same VACUOUS trap the digest table guards against.

---

## Findings

**F19 — the shared routing skill ships with no YAML frontmatter, and no test checks.**
`platforms/shared/agent-skills/advanced-planning/SKILL.md` begins `# advanced-planning`
and contains **zero `---` delimiters**. Of eleven shipped `SKILL.md` files it is the only
one, and it is the routing skill — the one carrying all five planning verbs to the runtime
for three of the five platforms. codex refuses it outright
(`missing YAML frontmatter delimited by ---`); opencode silently omits it. **No test
anywhere asserts frontmatter on a shipped skill**, which is why it shipped. Severity is
high: three adapters install a routing skill that no host can load.

**F20 — opencode reads `.claude/skills` and it wins.** opencode quoted
`AP5D4C-74898A1`, the `.claude/skills` token, for a skill its own adapter installed to
`.agents/skills`. On the first run it also listed `companion-detection` and
`permission-config` — the two skills the non-Claude adapters exclude from
`APPROVED_SKILLS` on purpose. **The exclusion list is not enforced at the discovery
layer:** in any project where claude-code is also installed, opencode serves the
claude-code copies, exclusions included.

**F21 — on a real profile, claude and cursor serve global copies over the project's.**
claude quoted a description ending `...what's the approach."` — verbatim the global
`~/.claude/skills/phase-plan-creator`, while the fixture copy begins with the token. It
also warned `Ignoring 4 permissions.allow entries from .claude/settings.json: this
workspace has not been trusted`, so *untrusted-workspace* is a live alternative cause and
is **not** discriminated here; either way the project copy did not win. cursor never
listed `phase-plan-creator` at all and returned four names, one of which (`autoplan`) is a
global gstack skill.

**F22 — `platforms/cowork` cannot be built on this machine.** `setup/cowork/create-zip.sh`
dies at line 62, exit 127, `zip: command not found` (`7z` also absent). **No test anywhere
references `create-zip.sh`.** Content comparison for the fifth platform was therefore
derived source-level from the script's own `zip -r core/ platforms/cowork/` line: cowork's
9 skills equal claude-code's 9, byte-identical, and the 7 cross-host skills are identical
across **all five** platforms.

**F23 — a host's skill *list* is not stable evidence; the token is.** The same opencode
invocation against the same fixture listed 10 names on one run and 7 on the next. The list
is a model's prose answer to "list the planning skills"; the token is a verbatim string
that can only have come from one file. Check 2's name-set comparison is built on the
unstable half, which is a second reason to treat its FAIL as a check defect rather than a
product defect.

---

## Corroborating detail

- codex is **0.152.0**, not the 0.150.1 recorded in `CLAUDE.md`; it has been upgraded
  since that note was written.
- The three-way fence coexistence is confirmed here for the first time: all three of the
  codex/opencode/cursor fences sit in one `AGENTS.md` without collision. loop-004-4 proved
  two; this proves three, which is what loop-004-1's collision decision actually claimed.
- Both canary tokens were verified absent from the entire repo checkout before every
  probe, so a match cannot have come from the source tree.

## Artefacts

`scratchpad/loop-005-4/`: `build_fixture_a.sh`, `build_fixture_b.sh`, `canary.py`,
`compare.py`, `probe.sh`, `run/canary.txt`, `run/prompt.txt`, `run/probes3/{claude,codex,opencode,cursor}.txt`.
Each probe output records host, invocation, cwd, HOME treatment, start/finish timestamps
and exit code, per the `tests/adherence/MANIFEST.json` precedent, so a withheld permission
is never mistaken for a routing failure.

---

## Addendum, 2026-09-01: F19 resolved and proven from installed output

F19 was fixed the same day it was found, as an unplanned todo taken before `loop-005-5`
on the user's decision — `005-5` writes the five-adapter contract tables, and would
otherwise have documented a router that three of five hosts cannot load.

**advanced-planning `32b436c`** (opencode/Qwen3.5, herdr worktree `loop-005-cursor`,
worker retired and pane closed at completion):

- frontmatter added to `platforms/shared/agent-skills/advanced-planning/SKILL.md`. The
  five verbs in the description — `phase`, `loop`, `gate`, `resume`, `compact` — were
  checked against the file's own *When to Use* table rather than accepted from the
  worker. They match.
- `platforms/python/tests/test_skill_frontmatter.py`, 56 cases, globbing every
  `SKILL.md` under `core/skills/` and `platforms/` so a new skill is covered without
  editing the test. It carries a **vacuity guard** that fails below 10 discovered files —
  a frontmatter test that discovers nothing would otherwise pass over an empty set, which
  is the failure this phase has now found twelve times. The one deliberate exception,
  `platforms/cowork/SKILL.md` carrying `name: advanced-planning` inside a directory called
  `cowork`, is a named constant that **asserts** the expected name rather than skipping
  the file.

**The proof is controller-side, and from installed output rather than from the source.**

| Step | Result |
|---|---|
| new test, as committed | 56 passed |
| frontmatter stripped (mutation run here, not by the worker) | **5 failed, 51 passed** — every failure naming `platforms/shared/agent-skills/advanced-planning/SKILL.md` |
| restored | 56 passed, working tree byte-identical |
| fixture rebuilt from the fixed worktree, codex re-probed | load errors naming that file: **1 before → 0 after** |
| codex's skill list | now includes `advanced-planning`, 8 skills, still quoting the `.agents/skills` token |
| full suite | 950 passed / 1 skipped, up from 894/1 by exactly the 56 added |

The mutation is the evidence, not the pass: it failed in a discriminating way — five
related properties, one named file, everything else still green — rather than turning the
suite uniformly red.

Being unplanned, this consumes no planned todo, following the `loop-004` coverage-first
precedent; `todos_total` is unchanged. The commit sits **unpushed** in the worktree with
three others, per the standing decision; advanced-planning has still never had a push
approved.

**F20, F21, F22 and F23 remain open.** F20 in particular is not obviously ours to fix —
opencode merging both project surfaces and preferring `.claude/skills` is host behaviour,
and the adapter's response may belong in the contract tables `loop-005-5` is about to
write rather than in code.
