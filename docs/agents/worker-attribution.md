# Worker commit attribution

A commit written by a delegated worker must say so. Twice now one has not, and both
times the commit was authored as the repository owner: `05d1e55` and `0f138de`, both
written by opencode/Qwen workers in the `loop-008-gate` worktree.

## The two trailers

Every commit a worker authors ends with:

```
Co-Authored-By: <provider> via herdr worker <worker-name>
Loop: <loop-id>
```

So for the opencode/Qwen worker `aplaunch-fix` on loop-007-9:

```
Co-Authored-By: opencode (Qwen) via herdr worker aplaunch-fix
Loop: loop-007-9
```

Controller commits keep the controller's own trailers instead. A commit never carries
both sets — the question the trailers answer is *who wrote this*, and two answers is no
answer.

## Where this is enforced

**In the worker envelope, at dispatch.** Not afterwards.

This is the whole point, and it is why this file exists rather than a note in an
evidence document. A missing trailer cannot be repaired without rewriting history, and
rewriting a commit to correct a trailer is a worse trade than leaving the record wrong
and writing it down. Both existing commits were left alone for exactly that reason.

So the `COMMIT:` line of every worker envelope states the two trailers verbatim and says
why they are wanted. A worker asked to "follow the repo conventions" will not find this
file — it reads its cwd, and the convention lives here, in the controller's checkout.
Naming the trailers in the envelope is the only mechanism that has been observed to
work.

## Why it matters more than tidiness

The programme's standing rule is that a worker's own summary is not evidence, and that
the controller reads the diff and runs the checks itself. That rule has teeth only while
it is possible to tell, later, which commits were worker output and therefore which ones
had to be independently verified. A worker commit authored as the owner erases the
distinction the verification discipline depends on.

## Related

- `.advanced-plans/evidence/2026-09-03-loop-007-9-profile-boundary.md` — where the gap
  was recorded, with both affected SHAs.
