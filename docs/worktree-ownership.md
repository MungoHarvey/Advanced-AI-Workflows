# Worktree ownership

Who owns each checkout, what an owner may write, and what no worker may write. This is the written
contract that ACC-07 and ACC-08 are tested against in phase 8.

Companion: [`programme-git-policy.md`](programme-git-policy.md) for branch, tag, and push rules.

---

## 1. One owner per checkout

Every checkout in this programme has **exactly one** owner at a time.

| Owner | Meaning |
|---|---|
| `herdr` | Created by `herdr worktree create` and managed through Herdr. Removed with `herdr worktree remove`. |
| `claude` | A Claude Code session is the sole writer. |
| `cursor` | A Cursor / `cursor-agent` session is the sole writer. |
| `aaw` | The AAW controller checkout. The only checkout that may write programme state. |
| `none` | Read-only reference, or dormant. No agent writes it. |

Ownership is recorded when the checkout is created — in the loop's `worktree_owner` field, and in
the evidence record for the loop. A checkout whose owner is not written down has no owner, and no
agent may write it.

**No double ownership.** Two agents must never hold the same checkout, even for read-mostly work.
If a second agent needs the same branch, it gets its own worktree.

**No nesting.** A worktree is never created inside another checkout's working tree. Paths live
beside each other, not within.

Transferring ownership means: the current owner's agent is stopped, the tree is confirmed clean,
and the new owner is written down. There is no implicit hand-off.

---

## 2. The controller is the sole writer of programme state

Exactly one checkout — `C:\Users\mharvey2\Coding\Advanced-AI-Workflows`, owner `aaw` — writes
programme state. No worker worktree writes any of it, on any branch, under any circumstances.

### Standard programme forbidden set

Forbidden for every worker todo in this programme, without exception:

`.advanced-plans/state/`, `.advanced-plans/PLANNING.md`, `.advanced-plans/PLANS-INDEX.md`,
`.advanced-plans/phases/*/complete.md`, `.advanced-plans/gate-verdicts/`,
`.advanced-plans/evidence/`

This list is reproduced in the header of every `loops.md` in this programme and must stay identical
in all of them. If it changes, it changes everywhere in the same commit.

A worker may **read** any of these. Reading the plan is how a worker knows its scope. Writing is
what turns a worker into a second controller, and that is the failure this rule exists to prevent.

---

## 3. What a worktree is not

The phase 3 pilot established this by experiment, and it corrects a natural assumption.

**A Herdr worktree bounds the working directory. It bounds nothing else.**

Two escalations in the pilot both reached out of the worktree and into the parent repository:

- codex's directory-trust prompt stated that trusting the worktree
  `C:\Users\mharvey2\Coding\herdr pilot\aaw-smoke` **applies to the repository root**
  `C:\Users\mharvey2\Coding\Advanced-AI-Workflows`. Trust granted in a disposable worktree is
  granted to the controller checkout too.
- a linked worktree's Git metadata lives in the parent repo's `.git/worktrees/`, so the agent could
  not stage or commit inside its sandbox. Committing required approving an operation that writes
  outside the worktree.

Consequences, stated plainly:

1. The controller/worker separation is enforced by **policy and review**, not by the worktree
   mechanism. Do not describe a worktree as a sandbox.
2. Granting an agent directory trust in any worktree grants it for the whole repository. Treat that
   grant as a decision about the repository, not about the worktree.
3. An agent that can commit in a worktree can write the parent repo's Git metadata. It is contained
   by what it is *told* not to touch, and by the controller checking afterwards.

If real containment is needed — an untrusted change, an unfamiliar upstream — use a separate clone,
not a worktree of the repository you care about.

---

## 4. Removal

```bash
herdr worktree remove --workspace <id>        # never --force
```

`--force` is not to be passed. A refusal is information; overriding it destroys the information and
possibly the work.

**Before removing:** confirm `git status --porcelain` in the worktree is empty. A dirty worktree is
never removed, forced or otherwise.

**If removal reports failure, do not reach for `--force`.** The pilot found that
`herdr worktree remove` can report `worktree_remove_failed` *after* it has already deleted every
file and deregistered the Git worktree, failing only on the final `rmdir` because an agent process
still held the directory as its working directory. Forcing at that point would force an operation
that has already happened.

The correct sequence when removal reports a permission failure:

1. read the error — if it names a path, that path is locked, not corrupt;
2. `herdr pane close <pane>` for every pane whose cwd is inside the worktree;
3. check what is actually left — `git worktree list`, `ls -A <path>`, and the main repo's
   `.git/worktrees/`;
4. if only an empty directory remains, `rmdir` it after confirming it holds zero entries;
5. delete the branch if it was a `pilot/` branch.

**Attempt the removal first. Do not close panes as a precaution.** Phase 4 loop 001 applied step 2
above pre-emptively, before trying to remove anything. The pane was the *only* pane in its
workspace, so closing it destroyed the workspace, and Herdr then answered both `worktree list` and
`worktree remove` with `workspace_not_found` — the directory and the Git registration were still
there, but Herdr no longer had a handle on either. Recovery was `git worktree remove <path>`
followed by `git branch -d`, both exit 0 and neither forced. The Herdr-managed path was simply
lost. Order matters: remove, then close panes only if removal fails.

**A worktree can be dirty on line endings alone.** The same loop found `M gstack/llms.txt` in a
worktree nothing had edited. `git diff --numstat` was empty and `git ls-files --eol` showed an empty
`attr/` column — no `.gitattributes` rule, so `core.autocrlf=true` leaves the file stat-dirty with
identical content. Check the content diff before concluding a worktree holds work. Clear it with a
targeted `git checkout -- <path>`, never `git reset --hard`.

Record the exact command and its exit code either way.

---

## 5. Current ownership

| Checkout | Owner | Branch | Notes |
|---|---|---|---|
| `C:\Users\mharvey2\Coding\Advanced-AI-Workflows` | `aaw` | `docs/herdr-v0.2-import` | controller; sole writer of programme state |
| `C:\Users\mharvey2\Coding\gstack-fork` | `none` | `main` | untouched; `origin/main` still at `a5dc03bd` |
| `C:\Users\mharvey2\Coding\aaw worktrees\gstack-sync-2026-08-26` | `herdr` | `sync/upstream-2026-08-26` | phase 4 loop 001, workspace `w5`. Local only, never pushed |
| `C:\Users\mharvey2\Coding\aaw worktrees\aaw-packaging-repair` | `herdr` | `feat/aaw-packaging-repair` | phase 4 loops 002-003, workspace `wA`. Local only, never pushed |
| `C:\Users\mharvey2\Coding\superpowers` | `none` | `main` | phase 5 loop 002 will create a `herdr`-owned port worktree beside it |
| `C:\Users\mharvey2\Coding\advanced-planning` | `none` | `main` | read-only until phase 6 |
| `C:\Users\mharvey2\Coding\gstack` | `none` | — | pre-existing dirty checkout, deliberately untouched |

Phases 4 and 5 update this table when they create their worktrees, and again when they remove them.
