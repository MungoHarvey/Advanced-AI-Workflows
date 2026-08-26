# Programme Git policy

The branch, tag, and gate rules for the AAW v0.2 programme. Names are decided here, once, so that
no phase improvises one inside a worktree.

Companion documents: [`worktree-ownership.md`](worktree-ownership.md) for who may write what,
[`upstream-sync-playbook.md`](upstream-sync-playbook.md) for the sync procedure,
[`releasing.md`](releasing.md) for the AAW release procedure.

---

## 1. The three human gates

An agent may prepare all of the following and must not perform any of them without an explicit,
in-session human authorisation naming the exact ref:

1. **push** — any `git push`, including a first push of a new branch;
2. **pull request** — opening, editing, or merging one;
3. **tag push** — creating a tag locally is allowed; pushing it is not.

Also prohibited outright, with or without authorisation, for the duration of this programme:
force-push, `git reset --hard`, rebasing a shared branch, deleting a remote ref, and removing a
dirty worktree.

Authorisation is per ref and does not carry forward. Approval to push
`docs/herdr-v0.2-import` on 2026-08-26 authorised that branch and the tag `v0.1.0`; it authorised
nothing else.

**Local commits on a non-default branch need no gate.** That is the intended working rhythm: commit
early and often locally, and stop at the network boundary.

---

## 2. Branch naming

One prefix per kind of work. The prefix is what makes the gate obvious at a glance.

| Prefix | Means | Push gate |
|---|---|---|
| `docs/` | documentation and programme planning | yes |
| `feat/` | a feature or repair on a product repository | yes |
| `sync/` | an upstream sync branch on a fork | yes |
| `port/` | a behavioural port onto current upstream | yes |
| `pilot/` | disposable; exists to be destroyed | **never pushed, never merged** |

`pilot/` branches are the exception worth stating plainly: they are not gated, they are forbidden.
A `pilot/` branch must be deleted at the end of the loop that created it.

### Branches this programme uses

| Repository | Branch | Phase | Created from |
|---|---|---|---|
| Advanced-AI-Workflows | `docs/herdr-v0.2-import` | 3 (controller) | `main` — **pushed 2026-08-26, authorised** |
| Advanced-AI-Workflows | `feat/aaw-packaging-repair` | 4, loops 002–003 | the phase-4 base |
| Advanced-AI-Workflows | `pilot/herdr-smoke` | 3, loop 002 | `386de0a` — **used and deleted 2026-08-26** |
| gstack-fork | `sync/upstream-2026-08-26` | 4, loop 001 | freshly fetched `upstream/main` |
| superpowers | `port/aaw-routing-2026-08-26` | 5, loop 002 | current `upstream/main` |

Planned but not yet decomposed, named here so phases 6 and 7 do not invent alternatives:
`feat/multi-runtime-adapters` in Advanced Planning, and
`feat/herdr-multi-runtime-orchestration` in AAW.

A sync or port branch is created from a **freshly fetched upstream ref**, never by copying the
stale fork tree. `git log -1` on the new branch must match `upstream/main` exactly before any
programme change lands on it.

---

## 3. Tag naming

| Pattern | Purpose | Example |
|---|---|---|
| `v<major>.<minor>.<patch>` | an AAW release | `v0.1.0` |
| `pre-upstream-sync-<yyyy-mm-dd>` | a fork's head immediately before an upstream sync | `pre-upstream-sync-2026-08-26` |
| `pre-port-<yyyy-mm-dd>` | a fork's head immediately before a behavioural port | `pre-port-2026-08-26` |

All tags are **annotated** (`git tag -a`), never lightweight, so the tagger, date, and reason are
recorded in the object.

If a tag name already exists, inspect it and choose a unique suffix such as `-2`. Never move or
overwrite an existing tag; a backup tag that can be moved is not a backup.

Backup tags are retained until at least the next successful AAW release.

---

## 4. The check command for each repository

Run before creating a branch, and again before asking for a push gate. A failure is recorded as a
failure and never summarised as passing.

### Advanced-AI-Workflows (controller)

```bash
git status --porcelain                # expect only the known untracked scratch file
git worktree list                     # expect exactly the checkouts you intend
tools/herdr-env.sh --assert           # exit 0; every target runtime under the real profile
```

There is no build. The packaging tests arrive in phase 4 loop 003 at `tests/packaging/`; once they
exist, they join this list.

### gstack-fork

```bash
git fetch --prune --tags upstream
git rev-list --left-right --count upstream/main...origin/main
git merge-base upstream/main origin/main
git diff --stat "$(git merge-base upstream/main origin/main)" origin/main    # expect empty
```

The last command is the net-patch test and the order matters. **Do not** use
`git diff upstream/main origin/main`: that asks how far *behind* the fork is, returns a large and
alarming diff, and proves nothing about whether the fork carries changes of its own.

Then the documented gstack build/test command and the Windows install smoke, each with its exit
code recorded.

### superpowers

```bash
git fetch --prune --tags upstream
git rev-list --left-right --count upstream/main...origin/main
git diff --stat "$(git merge-base upstream/main origin/main)" origin/main
```

Baseline expectation: the net patch is confined to `skills/brainstorming/SKILL.md` and
`skills/using-superpowers/SKILL.md`. Anything else is a finding, not a surprise to be absorbed.

### advanced-planning

```bash
git status --porcelain
git describe --tags --always
```

Read-only for phases 3 to 5. It becomes writable in phase 6.

---

## 5. Commit authorship

Worker agents inherit the machine's Git identity. The pilot commit in phase 3 loop 002 was authored
`Mungo Harvey <mharvey2@ed.ac.uk>` with nothing to indicate an agent wrote it.

Every commit produced by an agent in this programme carries a trailer naming the model and the
session:

```
Co-Authored-By: <model> <noreply@anthropic.com>
Claude-Session: <session URL>
```

The `Author` field stays the human's. The trailer is what makes agent-authored work greppable later
without rewriting identity, which would be the worse cure.

---

## 6. Committing to the right paths

`git add <path>` followed by a bare `git commit` commits **the whole index**, not the paths just
added. That mistake swept an unrelated staged deletion into an evidence commit earlier in this
programme.

Use the pathspec form, which commits only the named paths regardless of what else is staged:

```bash
git commit -F - -- <path> [<path> ...]
```

---

## 7. Line endings

`core.autocrlf=true` on this machine would check `.sh` files out with CRLF, and Git Bash fails on
those with `$'\r': command not found`. `.gitattributes` pins `*.sh` to `eol=lf` and `*.ps1`,
`*.cmd`, `*.bat` to `eol=crlf`. Any new shell script added to this repository is covered
automatically; do not override it per file.

---

## 8. Order of operations at a push gate

When a branch is ready and the gate is being requested, present in this order:

1. the exact commands, verbatim, in the order they will run;
2. the branch and the full head SHA;
3. the commits, oldest first, with their subjects;
4. the checks that were run and their exit codes;
5. the PR order, if more than one repository is involved.

Then stop and wait. `idle`, `done`, and terminal silence are not authorisation either.
