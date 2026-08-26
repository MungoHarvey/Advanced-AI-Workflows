# Fork divergence re-audit — gstack and Superpowers

**Collected:** 2026-08-26, after `git fetch --prune --tags` on both remotes of both forks
**Covers:** phase 4 loop 001 todos 1–2, and phase 5 loop 001 todo 1
**Nature:** read-only. No branch, worktree, tag, or commit was created in either repository.

**Result: both forks reproduce the baseline exactly. Zero delta.** The fetch brought nothing new,
so the numbers below are not a coincidence of caching — they are the current remote state.

---

## gstack — `C:\Users\mharvey2\Coding\gstack-fork`

| | Observed | Baseline |
|---|---|---|
| `origin/main` | `a5dc03bdd64124b302cb56927f0866edc0c11879` | same |
| `upstream/main` | `ad8400543cd9ce8d07641362db48d44a95417e33` | same |
| merge base | `029356e1f0693f22cb1fa4524c9b0f28ceab5a1b` | same |
| `rev-list --left-right --count upstream/main...origin/main` | `89  3` | 89 and 3 |
| merge base is an ancestor of `upstream/main` | yes | — |

### Net patch — the test that matters

```
$ git diff --stat 029356e1… origin/main
(empty)
```

**The fork carries no net tree patch.** All three fork-only commits are merges of upstream into the
fork:

```
a5dc03bd Merge branch 'garrytan:main' into main
973fedc8 Merge pull request #2 from garrytan/main
58479465 Merge pull request #1 from garrytan/main
```

`git log --merges` over the same range returns those three and nothing else, so there are no
non-merge fork commits hiding in the count.

This is the check that must **not** be done as `git diff upstream/main origin/main`. That form asks
how far *behind* the fork is — it would report the whole 89-commit upstream advance as a diff and
look alarming while proving nothing about whether the fork has changes of its own.

**Consequence for phase 4 loop 001:** the gstack sync is a clean re-base of the fork onto current
upstream. There is nothing fork-specific to preserve, port, or reconcile.

---

## Superpowers — `C:\Users\mharvey2\Coding\superpowers`

| | Observed | Baseline |
|---|---|---|
| `origin/main` | `fde9f972a2a49fcaa116f53d59444f002589c34a` | same |
| `upstream/main` | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | same |
| merge base | `f2cbfbefebbfef77321e4c9abc9e949826bea9d7` | same |
| `rev-list --left-right --count upstream/main...origin/main` | `241  4` | 241 and 4 |

### Net patch

```
$ git diff --stat f2cbfbef… origin/main
 skills/brainstorming/SKILL.md     | 61 +++++++++++++++++++++++++++++++++------
 skills/using-superpowers/SKILL.md | 22 +++++++++++++-
 2 files changed, 73 insertions(+), 10 deletions(-)
```

Exactly the two files the baseline named, and no others. The four fork-only commits:

```
fde9f97 fix(brainstorming): update AP-detected default from .claude/plans/ to .advanced-plans/specs/
b874847 Merge pull request #1 from obra/main
f2d65a6 feat: use AskUserQuestion tool for brainstorming questions
dfd7ff5 feat: conditional integration with Advanced Planning and Plannotator
```

**Note for the behaviour matrix.** `dfd7ff5` is *"conditional integration with Advanced Planning and
Plannotator"* — the fork patch is half about a tool this project deprecated on 2026-08-26. This is
what the design's SP-4 row already anticipated: port the Advanced Planning half of the
companion-tools behaviour and drop the Plannotator half. The matrix must say so explicitly rather
than porting `dfd7ff5` wholesale.

The fork is 241 commits behind upstream against a 73-line patch. The design's instruction to build
the port branch from current `upstream/main` and re-apply the behaviour — never to copy the stale
fork files — is well founded.

---

## What this does not establish

- Nothing was built, tested, or installed. The gstack suite and the Windows install smoke are phase
  4 loop 001 todos 4–5 and have not been run.
- No sync or port branch exists yet, and no backup tag has been created. Both are the next
  writes in phase 4, and both are local-only until a push gate.
