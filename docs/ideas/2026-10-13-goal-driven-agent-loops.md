# Goal-Driven Agent Loops: Development Idea

13/10/2026 · Mungo

## Summary

Build a small, committed structure that lets several coding agents work in parallel worktrees towards one goal without the plan drifting. The idea rests on three moves borrowed from multi-person software engineering: give every fact one home, derive status rather than write it, and enforce the rules mechanically at three boundaries (agent hooks, git hooks, CI). People and agents maintain by hand only two kinds of file: the project goal and one brief per workstream. Tickets live in the tracker, progress lives in git, and everything else is generated.

## Problem and motivation

Coding agents now run unattended in loops, but a long programme of work outlives any one session, any one worktree and any one `/goal`. Without shared, durable state, four failures recur:

- **Lost context.** Each new session starts blind and guesses what earlier sessions did.
- **Premature "done".** An agent declares victory on work that was never verified end to end.
- **Drift.** Parallel worktrees fork the plan, the terminology and the interfaces; the more files people must keep updated, the faster they drift.
- **Supervision load.** With several agents in herdr, it is hard to know which needs a decision, and notifications either never arrive or arrive constantly.

Claude Code's `/goal` helps within one session, but it holds one goal per session, can only be replaced rather than edited, and its evaluator judges only what appears in the transcript. The durable goal therefore has to live outside the session.

## Goals and non-goals

**Goals**

1. One goal, held durably and kept unchanged, that every controller and agent works towards across sessions and worktrees.
2. Progress tracked from evidence (commits, passing checks, closed tickets), never from an agent's own claim.
3. Parallel workstreams in separate worktrees that cannot fork the plan or the shared language.
4. The fewest hand-maintained files that will do the job, so there is little to drift.
5. Notifications at decision gates only, escalated up a clear ladder.
6. A structure that is committed with the code, works in any repo, and fits herdr and Matt Pocock's skills.

**Non-goals**

- Building a new issue tracker or agent runtime; existing tools (git, the tracker, herdr, Claude Code hooks) are reused.
- Fully autonomous merging to main; merges and plan changes stay behind a human gate.
- Exploratory tree search over experiments (as in autoresearch). That is a separate pattern for metric-driven ML work, noted but out of scope here.

## Key principles

1. **One home per fact.** The goal lives in `GOAL.md`, work items in the tracker, progress in git, decisions in decision records. Nothing is recorded twice.
2. **Derive, don't maintain.** Status is computed from git and the tracker on demand and never committed. Every generated file is one less file to drift.
3. **One writer per file.** Each file has exactly one owner: you, the project controller, or a workstream controller. Shared files are where parallel work breaks.
4. **Read the plan from main.** Worktrees never edit `.plan/`; they read `origin/main`'s copy, so every lane sees the same plan.
5. **Evidence before done.** A ticket closes only when a commit carrying its trailer exists and its checks pass. An agent's word is not evidence.
6. **Intent is human, execution is agent.** You own the north star and approve each brief; agents own tickets and code within them.
7. **Enforce at boundaries, not by memory.** Rules are checked by hooks while agents work, at commit, and at merge, not by instructions agents may forget.
8. **Immutable decisions.** Briefs freeze on approval and decision records are superseded, never edited, so history cannot quietly change.
9. **Summaries flow up, never transcripts.** Each tier reads the tier below through events and summaries, keeping every controller's context small.
10. **Escalate, don't broadcast.** Workers report to their workstream controller, controllers to the project controller, and only the project controller notifies you, at gates.
11. **Minimal first, then iterate.** Build one enforcement ring on one repo, prove it, then add the next.

## Background: what the discussion established

The design came out of one conversation on 13/10/2026; each step narrowed it.

1. **Loops are now the unit of work.** Boris Cherny's progression runs from editing code, to prompting an agent, to writing loops that prompt it. Recurring loops (`/loop`, routines) handle chores such as PR babysitting. Run-until-done loops (Ralph, now `/goal`) keep progress in files and git so each restart begins fresh. Tree search over experiments (evo, Meta's spdl autoresearch) branches in parallel worktrees for metric-driven ML work.
2. **Sentiment is enthusiastic but tempered.** "Loop engineering" was named in June 2026 (Steinberger, Osmani, Cherny). The consensus: the verifier is the bottleneck, the maker must be separate from the checker, state belongs on disk, and token cost is the main brake. Cherny himself has warned about it.
3. **`/goal` cannot carry a long programme.** Per the docs, a goal is session-scoped, one per session, replaceable but not editable, and judged by a small model reading the transcript only. It is a wrapper round a prompt-based Stop hook. A durable goal file is therefore needed outside it.
4. **herdr already covers worktrees and notifications.** It creates worktrees as grouped workspaces, emits `worktree.created`, runs plugin hooks on events, reports agent state (working, blocked, done, idle), sends system notifications, and exposes `herdr agent wait` and an event stream. It is pre-1.0 (docs at v0.9.3) and moves quickly.
5. **Matt Pocock's skills supply Goal and Steps.** `/grill-with-docs` and `/to-spec` produce the goal and a shared `GLOSSARY.md` plus decision records; `/to-tickets` produces tracer-bullet tickets with blocking links; `/implement` and `/implement-spec` drive TDD and close with `/code-review`; `/wayfinder` maps work larger than a session.
6. **Formats should be chosen for write safety.** Anthropic found agents less likely to wrongly overwrite JSON than Markdown. Read-accuracy benchmarks (TOON) vary by model and data shape. Beads shows a working multi-agent pattern: JSONL in git, a SQLite cache, and hash IDs that avoid merge collisions.
7. **Your controller hierarchy fits.** A project controller acts as project manager; one workstream controller per worktree is started by its own grilling session and manages tickets and agents.
8. **Software teams already solved drift.** They use one source of truth per fact, ticket trailers on commits, immutable decision records, CODEOWNERS and branch protection, short-lived branches, and mechanical gates. Claude Code hooks, committed in `.claude/settings.json`, let the same gates run inside every agent loop.

## Final design

The design has four parts: three tiers of control, a minimal committed structure, three rings of enforcement, and a notification ladder.

```
                 You: north star and approvals
                              |
                     Project controller            ^  summaries up
              (workstreams, merge order, glossary) |
                   /                    \          |
   Workstream controller A      Workstream controller B
   (worktree; grilling,         (worktree; grilling,
    spec, tickets)               spec, tickets)
            |                            |         |
         Workers                      Workers      v  plan down
   (one ticket each,            (one ticket each,
    trailered commits)           trailered commits)
            \                            /
      git history + tracker: status is derived, never written
```

Briefs, tickets and `/goal` conditions flow down from main; only gate events and summaries flow up, and status comes from git and the tracker.

### Tiers of control

- **You** own the north star, approve each workstream brief, and approve merges to main.
- **Project controller (the project manager).** Owns the workstream list, cross-workstream dependencies, merge order, and the shared glossary and decision records. It reads workstream events and never worker transcripts.
- **Workstream controller (one per herdr worktree).** Starts with its own grilling session (`/grill-with-docs`, then `/to-spec`, then `/to-tickets`). It owns its tickets and runs them through `/implement-spec`, or through worker panes where closer supervision is needed. Its `/goal` is its brief's acceptance criteria.
- **Workers** each implement one ticket, commit with trailers, and report back to their workstream controller.

### Committed structure

```
.plan/GOAL.md          north star and invariants; changed by PR only, owned by you
.plan/ws/<name>.md     one brief per workstream; frozen on approval, changed by PR only
GLOSSARY.md, docs/adr/ shared language and decisions; the project controller merges proposals
tickets                in the tracker (/to-tickets), with blocking links
git history            commits carry Ticket: and Workstream: trailers
STATUS                 generated on demand from git and the tracker, never committed
```

Only the goal and the briefs are maintained by hand. Worktrees read the plan with `git show origin/main:.plan/GOAL.md` and never write to `.plan/`.

### Three rings of enforcement

1. **While agents work: Claude Code hooks** in the committed `.claude/settings.json`.
    - `SessionStart` puts the derived status, the brief and the current ticket into context.
    - `PreToolUse` on Edit and Write denies writes to `.plan/**` from inside worktrees.
    - `PostToolUse` validates any file the orchestrator writes; a failure goes back to the agent.
    - `Stop` blocks the end of a turn until tests pass, commits carry trailers, and the branch is not too far behind main.
    - `onFailure: "block"` makes a crashed or missing hook block the action instead of letting it pass (Claude Code v2.1.295 or later).
2. **At commit: git hooks** in a committed folder set by `core.hooksPath`, so every worktree shares them. `commit-msg` requires the trailers; `pre-commit` checks the plan files' structure.
3. **At merge: CI and branch protection.** Required checks re-run the same validators, and changes to `.plan/` need your approval. This ring is the backstop, because agents can bypass local git hooks.

### Notifications

herdr sends system notifications when an agent finishes or needs input. Escalation runs workers to workstream controller (via `herdr agent wait`), workstream controller to project controller (via events), and project controller to you via `herdr notification show`, only at gates: a decision needed, a workstream blocked, or a merge ready. Controllers react to events rather than polling, so idle controllers cost little.

## Options considered and decisions

| Decision | Options weighed | Chosen | Why |
| --- | --- | --- | --- |
| Where the durable goal lives | Rely on `/goal`; a goal file; a tracker epic | Goal file in `.plan/` on main | `/goal` is session-scoped and transcript-only |
| State format | Markdown checklist; Markdown with frontmatter; JSON; JSONL event log; git-backed tracker (Beads) | Tracker plus commit trailers, status derived | Fewest hand-maintained files; JSONL logs or Beads kept in reserve |
| Where Steps live | Tracker; local-files tracker in the vault; goal file with mirrored tickets | Tracker | No duplication; ticket links and blocking come free |
| Tiers | Full three tiers; drop separate workers (`/implement-spec`); drop workstream controllers | Three tiers, with `/implement-spec` as the default inside a workstream | Keeps grilling per workstream while cutting coordination |
| Orchestrator driver | `/loop` in one session; cloud routine; custom Stop hook | Event-driven controllers with Stop hooks for gates | Survives idle time; checks evidence the `/goal` judge cannot see |
| Plan edits | Agents edit freely; agents propose by PR | PR only, CODEOWNERS on `.plan/` | Same review discipline as code |
| Enforcement | Instructions only; hooks; hooks plus CI | Three rings | Instructions are forgotten; CI is the backstop |

## Risks and open questions

**Risks**

- **Token cost.** Multiple controllers and workers multiply spend. Mitigation: event-driven controllers, turn and token caps in every `/goal`, and `/implement-spec` in place of extra worker panes.
- **Language drift across workstreams.** Parallel grilling sessions sharpen different vocabularies. Mitigation: the project controller owns `GLOSSARY.md` and the decision records; workstreams propose changes.
- **Reward hacking.** An agent may satisfy a check rather than the intent. Mitigation: a separate checker (`/code-review`), evidence from git rather than claims, and human gates at merge.
- **Tool churn.** herdr is pre-1.0 and Pocock's skills rename often (`/to-prd` became `/to-spec`). Mitigation: pin versions and keep the plan format independent of either tool.
- **Merge order.** Worktrees cannot see each other's changes. Mitigation: the project controller sequences merges; `Stop` gates check how far behind main a branch is.

**Open questions**

- Can herdr plugin hooks fire on agent status changes, or only through a long-running `events.subscribe` connection? The docs show only `worktree.created` as a hook.
- Which tracker: GitHub or GitLab, per repo?
- How should `STATUS` mirror into the Obsidian vault, given the vault is the source of truth for personal tasks?
- What threshold counts as "too far behind main" for the `Stop` gate?
- How does this fit the planned context-window and handoff mod, which could share the brief and log formats?

## Phased plan

Each phase ends at a gate that decides whether the next still earns its place.

1. **Phase 1: contract and ring 1 on one repo.** Write the `GOAL.md` and brief templates, the commit trailer convention, and three hooks: `SessionStart` context, the `.plan/` write block, and the `Stop` gate. *Gate:* one workstream completes a ticket end to end with no hand-editing of state.
2. **Phase 2: two workstreams in herdr.** Add the project controller, a second worktree, the escalation ladder and gate notifications. *Gate:* the two workstreams run in parallel without drift in plan or glossary, and you are notified only at gates.
3. **Phase 3: rings 2 and 3.** Add committed git hooks and CI checks with branch protection on `.plan/`. *Gate:* a deliberately bad commit or plan edit is caught at the right ring.
4. **Phase 4: decide on extensions.** Choose whether to add JSONL lane logs or Beads, a herdr plugin for lane bootstrap on `worktree.created`, and a `STATUS` mirror into the vault. *Gate:* each extension fixes a failure seen in phases 1 to 3, not a hypothetical one.

## Sources

- [Claude Code docs: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal)
- [Claude Code docs: Hooks reference](https://code.claude.com/docs/en/hooks)
- [Anthropic: Effective harnesses for long-running agents (26/11/2025)](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Addy Osmani: Loop Engineering (07/06/2026)](https://addyosmani.com/blog/loop-engineering/)
- [The New Stack: Loop engineering (10/06/2026)](https://thenewstack.io/loop-engineering/)
- [The Neuron: Boris Cherny and Cat Wu on agent loops](https://theneuron.ai/explainer-articles/claude-code-creators-boris-cherny-and-cat-wu-explain-how-to-use-agent-loops/)
- [NewsBytes: Cherny on token costs](https://www.newsbytesapp.com/news/science/boris-cherny-warns-rising-token-costs-complicate-ai-coding-experiments/tldr)
- [AlphaSignal: Most developers do not need agent loops yet](https://alphasignalai.substack.com/p/most-developers-do-not-need-agent)
- [The Register: Ralph Wiggum loop (27/01/2026)](https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/)
- [evo plugin (PyPI)](https://pypi.org/project/evo-hq-cli/0.2.0/)
- [Meta spdl autoresearch](https://facebookresearch.github.io/spdl/main/autoresearch/autoresearch.html)
- [herdr: Configuration](https://herdr.dev/docs/configuration/), [Plugins](https://herdr.dev/docs/plugins/), [Socket API](https://herdr.dev/docs/socket-api/)
- [mattpocock/skills README](https://github.com/mattpocock/skills)
- [TOON format benchmarks](https://github.com/johannschopplich/toon)
- [Beads (pkg.go.dev)](https://pkg.go.dev/github.com/steveyegge/beads@v0.19.0)

General software-engineering practices (trailers, decision records, CODEOWNERS, short-lived branches) are described from general knowledge and were not separately cited.
