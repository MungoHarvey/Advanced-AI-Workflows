# Superpowers mirror publish — preflight

**Date:** 2026-09-01
**Repository:** `MungoHarvey/superpowers` (checkout `C:/Users/mharvey2/Coding/superpowers`)
**Closes:** the Phase 5 carried item *"The mirror is prepared, not published."*
**Status:** preflight COMPLETE. The publish itself is the operator's to run.

---

## Why this exists

Phase 5 passed its gate on 2026-08-26 having proved the Superpowers fork needs no patch: all four
intents moved to the AAW-owned fenced block, and `mirror/upstream-2026-08-26` is byte-identical to
`upstream/main`. It then stopped, because publishing the mirror force-pushes a default branch —
outside the controller's authority under `docs/herdr-kickoff-prompt.md`.

The gate has been uncleared since. On 2026-09-01 the owner authorised the reversible half: push
the backup tag, re-verify, and hand over the force-push line.

## Ordering constraint

**The backup tag must reach the remote before the force-push, not after.** The Phase 5 record
names the tag and names the command but does not state their order. Until today the tag existed
only on this machine, so a `--force-with-lease` that landed first would have left the sole copy
of the pre-port head on one laptop.

## Baseline, measured before any write

| Ref | SHA |
|---|---|
| `origin/main` (fork, patched) | `fde9f97` |
| `upstream/main` (obra) | `b36e0829c6d0` |
| `mirror/upstream-2026-08-26` (local) | `b36e0829c6d0` |
| `pre-aaw-port-2026-08-26` (local tag) | `fde9f97` |

`mirror/upstream-2026-08-26` and `upstream/main` are **the same commit** — `git diff` empty,
`rev-list` 0 in both directions. The backup tag points at exactly the commit the force-push
overwrites.

The tag was **not** present on the remote at baseline (`git ls-remote --tags origin` — no match).

## Action taken

```
git push origin refs/tags/pre-aaw-port-2026-08-26
 * [new tag]         pre-aaw-port-2026-08-26 -> pre-aaw-port-2026-08-26
```

Confirmed on the remote:

```
071000cfacfddbef3c689511ce3c6ba7c72b41c0  refs/tags/pre-aaw-port-2026-08-26
fde9f972a2a49fcaa116f53d59444f002589c34a  refs/tags/pre-aaw-port-2026-08-26^{}
```

An annotated tag object dereferencing to `fde9f97`. Nothing else was written.

## Reversibility, proven rather than assumed

Every commit that the force-push removes from `origin/main` was checked individually for
reachability from the pushed tag, with `git merge-base --is-ancestor`:

| Commit | | |
|---|---|---|
| `fde9f97` | fix(brainstorming): AP-detected default → `.advanced-plans/specs/` | **SAFE** |
| `b874847` | Merge pull request #1 from obra/main | **SAFE** |
| `f2d65a6` | feat: use AskUserQuestion tool for brainstorming questions | **SAFE** |
| `dfd7ff5` | feat: conditional integration with Advanced Planning and Plannotator | **SAFE** |

All four are ancestors of the tag now on the remote. The publish is recoverable from the
remote alone, without this machine.

## The remaining command — the operator's to run

```
git -C C:/Users/mharvey2/Coding/superpowers push origin mirror/upstream-2026-08-26:main --force-with-lease
```

`--force-with-lease` refuses if `origin/main` has moved since the fetch above, so a concurrent
change aborts rather than being overwritten.

### Post-publish verification

```
git -C C:/Users/mharvey2/Coding/superpowers fetch origin
git -C C:/Users/mharvey2/Coding/superpowers diff upstream/main...origin/main   # expect empty
```

Then re-run the adherence matrix under `advanced-planning tests/adherence/`, and record the
published SHA in the compatibility manifest once Stage 1 of
`specs/2026-09-01-dependencies-not-forks-plan.md` exists.

### To undo

```
git -C C:/Users/mharvey2/Coding/superpowers push origin pre-aaw-port-2026-08-26^{}:main --force
```

## Not done here

- The force-push itself.
- Any change to `mirror/upstream-2026-08-26`, `main`, or the working tree.
- The compatibility manifest, which does not yet exist (Stage 1).
