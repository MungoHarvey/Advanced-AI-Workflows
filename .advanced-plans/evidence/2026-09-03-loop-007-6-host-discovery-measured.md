# loop-007-6 — host discovery: what the adapter controls, what the host controls, and the copy nobody was reading

Date: 2026-09-03
Repository under test: advanced-planning, worktree `loop-008-gate` at `1fb0f38`
Fixtures: `scratchpad/l0076/fixture` (canaried) and `scratchpad/l0076/fixture-clean` (digest table), both outside every checkout
Hosts: claude 2.1.252, codex 0.152.0, opencode 1.18.27, cursor-agent 2026.08.31-4057e58
Discharges: criterion 1 — *every target host discovers the same named core planning skills, not host-specific copies that drift*

## Method, and why it is not the one the todo asked for

The todo asks for a fake HOME. loop-005-4 measured that three of four hosts defeat it
here — claude loses its credentials, cursor cannot find its own binary, codex resolves
the global skills root from neither `HOME` nor `USERPROFILE`. That has not changed, so
the substitute stands and is stronger: **a per-surface canary token**, injected at the
front of the `description` scalar and re-parsed with PyYAML before anything is written.
A token can only have come from one file, so which copy answered is visible in the
content rather than inferred from where a host is believed to look.

Front, not back, and inside the quoted scalar: loop-005-4 measured codex truncating long
descriptions to a context budget (a token at the end measures the budget) and both codex
and opencode correctly refusing a skill whose YAML the injector had broken (a token after
the closing quote measures the injector). `canary.py` refuses to write unless the token
survives `yaml.safe_load`.

Every probe records host, invocation, cwd, HOME treatment, timestamps and exit code, so a
withheld permission is never mistaken for a routing failure. Each probe says *do not open
or read any files with tools* — a host that greps the file proves nothing about
discovery, and codex quoting a token without reads shows the prompt elicits a real quote
when the tokened copy is the one loaded.

Absence control: both tokens were confirmed absent from the fixture and from
`~/.claude/skills/phase-plan-creator` before injection.

## The four-surface digest table — the headline

Computed on a **canary-free** install, so the tokens cannot flatter it. Seven names are
shared by the two project surfaces; a zero would have been refused as VACUOUS.

| skill | proj `.claude` | proj `.agents` | global `~/.claude` | global `~/.agents` |
|---|---|---|---|---|
| `phase-plan-creator` | `6c04c90fdc8fa82e` | `6c04c90fdc8fa82e` | **`6bbda5714807f4c6`** | absent |
| `plan-skill-identification` | `c9c5fb19f121bc64` | `c9c5fb19f121bc64` | **`14904a433408316f`** | absent |
| `plan-subagent-identification` | `790f2d9afe37f686` | `790f2d9afe37f686` | **`c48626c1c8d4a103`** | absent |
| `plan-todos` | `71989ea0178bd73e` | `71989ea0178bd73e` | **`54b4ea73d72ff2a9`** | absent |
| `progress-report` | `c4a13a7b68c1ebcc` | `c4a13a7b68c1ebcc` | `c4a13a7b68c1ebcc` | absent |
| `ralph-loop-planner` | `c1609b8140e11d85` | `c1609b8140e11d85` | **`e56a9a0fd4e5b492`** | absent |
| `schema-design` | `21e77ab42da375e6` | `21e77ab42da375e6` | **`35140be5d3d92c59`** | absent |

**The two project surfaces are byte-identical on all seven.** The seven digests match
loop-005-4's exactly, which is a cross-check on both runs. The failure the criterion
actually names — identical names, drifted bodies — is in the **global** layer: 6 of 7
differ, and those files are dated **Jun 16**.

Most of the drift is cosmetic (code-fence language tags, blank lines, `*emphasis*` versus
`_emphasis_`). Two are not:

- `plan-skill-identification` — the stale global copy's **frontmatter description**
  differs, and its body still hard-codes `` Glob `.claude/skills/*/SKILL.md` `` where
  source now says `[skills_directory]`. The host-neutrality fix is absent from the copy
  two of four hosts actually read.
- `plan-subagent-identification` — the global copy still says *"(e.g. Claude Code)"*,
  removed in source.

Same date, same cause as the stale `~/.claude/commands/run-gate.md` found earlier today:
this machine's global advanced-planning install is roughly two and a half months behind.

## Which copy each host answered from

Both project surfaces tokened; the global copy left alone.

| host | quoted | reads |
|---|---|---|
| codex | `CANARYAGENTS3M8X` | project `.agents/skills` — its own adapter's copy ✅ |
| opencode | no token | global `~/.claude/skills` ❌ |
| claude | no token | global `~/.claude/skills` ❌ (confounded, below) |
| cursor | no token, and named no skill at all | neither ❌ |

## F20 — the mechanism is not what the finding said

loop-005-4 recorded *"opencode resolves `.claude/skills`, claude-code's copy, rather than
its own adapter's."* Measured today, that is the right effect from the wrong mechanism,
and the correction matters because it changes who can fix it.

opencode's own embedded documentation, read out of the binary, states the layout: project
skills at `.opencode/skills`, an `opencode.json` key `skills.paths` taking a directory
list, and external skills auto-loaded from `~/.claude/skills` and `~/.agents/skills`.

Three arms, all answering token-free:

| arm | result |
|---|---|
| default — skill only at project `.agents/skills` | global copy answered |
| `opencode.json` with `skills: {paths: [".agents/skills"]}` | global copy answered |
| skill copied to `.opencode/skills`, opencode's documented project path | global copy answered |

The control that settles it: two **uniquely named** skills with no global namesake,
`zebrafixture-agents` in `.agents/skills` and `zebrafixture-opencode` in
`.opencode/skills`. opencode quoted **both** canaries.

So opencode does load project skills from both surfaces. What it does not do is prefer
them: **on a name collision with a global `~/.claude/skills` skill, the global copy
wins**, and no configuration the adapter can install changes that.

The same control run on codex returns `A=CANARYZAGENTS9W1`, `B=NOTFOUND` — codex reads
`.agents/skills` and not `.opencode/skills`, exactly as designed.

**Verdict: host behaviour for the resolution, ours for the collision.** The collision
exists only because a `--global` install of this framework put the same seven names in
`~/.claude/skills` and then went stale. That half is ours, and it is already detectable
by our own shipped instrument — see the remedy below.

## F21 — claude reproduces, and cannot be discriminated from here

claude answered token-free: the global copy won over the project's `.claude/skills`.

It also reprinted the warning loop-005-4 recorded: *"Ignoring 4 permissions.allow entries
from .claude/settings.json: this workspace has not been trusted."* That warning is about
`permissions.allow`, not about skills, but it does not rule out trust gating project skill
loading as well. **The alternative cause is not eliminated.**

Discriminating it means setting `hasTrustDialogAccepted` for the fixture in
`~/.claude.json` — a trust write to the operator's profile, which broadens provider
permissions and is outside this session's authority. It is also, precisely, what
`loop-007-7` is for. Recorded as **un-discriminated, with the reason**, rather than
resolved either way.

A no-write A/B was looked for and rejected on its merits: 39 trusted projects hold a
project-local `phase-plan-creator`, three of them differing from the global copy — but
they differ only in the **body**, and all three carry an identical `description`, which is
the field the probe quotes. A probe that cannot distinguish its two hypotheses is not a
probe.

## F23 — resolved, and the instability was somewhere else

Four cursor runs on the same fixture, same prompt. Every one declined to name a single
project planning skill and quoted no canary — including the fourth, run after a canaried
skill was planted in `.cursor/skills`, the project analogue of cursor's own global skills
root (`~/.cursor/skills`, 180 skills, containing none of ours).

The omission **reproduces 4/4**. It is not intermittent, and cursor's list is not the
unstable half: the 10-names-then-7 instability loop-005-4 recorded was opencode's, and the
canary method retires the question either way, because a token is a verbatim string from
one file rather than a model's prose.

Cursor answered from the `AGENTS.md` fence in every run, and in three of four it reported
`.agents/skills` as *"Cursor discovers these automatically"* — which is our own adapter
README's sentence, handed back to us as though it were an observation. It is the claim
under test, and it is false as installed.

`cursor-agent --help` has **no skills concept at all**: zero occurrences of the word, and
a `generate-rule` subcommand instead. Its mechanism is rules and `AGENTS.md`.

**Verdict: host constraint under this invocation** — with one alternative not eliminated,
that `-p --mode ask` may itself restrict skill loading where an interactive agent mode
would not. `--mode ask` is the shape ROUTING.md prescribes for read-only work, and it is
the shape every reviewer here runs in, so the constraint is real for our uses even if a
richer mode would lift it.

## The remedy the product already ships, unwired

`install_audit` has a `--layers source,global` mode, and it is not hypothetical:

```
python -m platforms.python.install_audit --layers source,global
=== source -> global (C:\Users\mharvey2\.claude) [DRIFT DETECTED] ===
Summary: 1 current, 26 stale, 0 missing, 0 source-missing, 13 extra  (total: 40)
RESULT: drift detected -> run /sync-install to refresh stale/missing files      [rc=1]
```

Twenty-six stale files, found by our own instrument, in the layer two of four hosts
actually read. It is wired into `ci.yml:174` and `docs/release-checklist.md`, and
`/sync-install` fixes it.

**The gap: `/run-gate`'s Step 1 preflight audits `--layers source,project` only** — the
layer the hosts were measured *not* to prefer. The gate looks at the copy that was right
and never at the copy that answered.

## Criterion 1, and why it is being rewritten rather than waived

Criterion 1 as written asks every host to discover the same named skills. Measured, three
of four host outcomes turn on behaviour no adapter can configure: opencode's collision
precedence (three arms), cursor's absent skill loader (four runs), and claude's
precedence, which cannot even be discriminated without a trust write. A criterion whose
subject is the host is not falsifiable by the thing we ship.

The rewrite is recorded in `plan.md` with its reason, per this loop's own check 5, and it
deliberately does **not** narrow until it fits. It moves the subject from the host to the
adapter and keeps the failure it names:

> Every layer a target host is measured to read is covered by the shipped install audit,
> and the gate preflight runs it over those layers, so a drifted copy is reported before a
> run rather than discovered after one. The per-host discovery table is maintained as
> recorded constraint, with each entry marked adapter defect or host behaviour and the
> measurement that decided it.

The old criterion's substance is preserved: drifted copies under identical names still
fail it. What changes is that failing it is now something our code can detect.

## Correction, added 2026-09-03 after loop-007-7 — right layer, wrong files

The section above says twenty-six stale files were found by our own instrument "in the
layer two of four hosts actually read", and treats that as the remedy meeting criterion 1.
Both halves of that sentence are true and they are about **different files**. Putting them
in one sentence made the remedy look complete when it is not.

`install_audit.SURFACES` (`install_audit.py:168-172`) is exactly three entries — commands,
agents, schemas. **There is no skills surface.** The twenty-six stale files were commands,
agents and schemas. The drift the digest table measured, and the drift the hosts were
serving, was in **skills**, which that audit has never looked at and still cannot.

So the instrument criterion 1 names is blind to the files criterion 1 is about. The global
layer was indeed stale and indeed the layer the hosts read; the audit simply was not
reporting the part of it that mattered.

A second defect, found the same way: the gate preflight's `--layers all` resolves its
project half as `find_repo_root(__file__) / ".claude"` (`install_audit.py:439,449`) — the
**framework** checkout, never the project the gate is running in. Measured from the AAW
project: it audited this worktree's own `.claude`, which holds only `settings.json`,
reported 27 MISSING and exited 1. The gate's warning would fire permanently, which makes
real drift indistinguishable from the noise.

Criterion 1 as rewritten is therefore **not met**, and the regression test written with it
passes anyway — asserting that a layer argument is parser-valid and mentions `global`
cannot see an omitted surface. Both defects are `loop-007-8`.

One thing did improve without the audit's help: `loop-007-7`'s global install refreshed the
skills as a side effect, and all nine now hash identically to source. The precedence
behaviour F20 and F21 describe is unchanged — the global copy still wins a name collision —
but it is now the same bytes, so the collision is harmless until the next drift. Which is
precisely the drift nothing is currently watching for.

## Artefacts

`scratchpad/l0076/`: `canary.py`, `digest.py`, `probe.sh`, `probes/{claude,codex,opencode,cursor}.txt`,
`probes/{opencode-configured,opencode-dotopencode,unique-codex,unique-opencode,unique-cursor,cursor-run2,cursor-run3}.txt`,
`fixture/`, `fixture-clean/`. No write was made to any repository checkout, to
`~/.claude/`, to `~/.agents/`, or to `~/.claude.json` at any point.
