# Worker commit attribution

A commit written by a delegated worker must say so.

**Corrected 2026-09-03.** This document opened by claiming that two commits, `05d1e55`
and `0f138de`, had been authored as the repository owner without attribution trailers.
That was wrong. Both carry `Co-Authored-By: <provider> via herdr worker <name>` and
`Loop: <id>` (the trailer this convention used before ticket numbers replaced loop ids on 2026-09-07), present at creation and not amended in, which `git log` and `git reflog`
both confirm. The phase 6 gate found the error by opening the commits, which the author
of this document had not done.

The convention below stands on its own merits and is unchanged. What changed is the
reason for writing it down: it is a convention worth stating because a worker cannot
find it from inside its own checkout, not because it had already been breached.

## The two trailers

Every commit a worker authors ends with:

```
Co-Authored-By: <provider> via herdr worker <worker-name>
Ticket: #<n>
```

So for the opencode/Qwen worker `aplaunch-fix` on ticket #42:

```
Co-Authored-By: opencode (Qwen) via herdr worker aplaunch-fix
Ticket: #42
```

Controller commits keep the controller's own trailers instead. A commit never carries
both sets — the question the trailers answer is *who wrote this*, and two answers is no
answer.

## Where this is enforced

**In the worker envelope, at dispatch.** Not afterwards.

This is the whole point, and it is why this file exists rather than a note in an
evidence document. A missing trailer cannot be repaired without rewriting history, and
rewriting a commit to correct a trailer is a worse trade than leaving the record wrong
and writing it down. So the envelope is the only place the convention can be made to
hold: by the time a commit exists, it is too late to add one cheaply.

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

- `.advanced-plans/evidence/2026-09-03-loop-007-9-profile-boundary.md` carried the
  same correction. It was deleted in the 2026-09-07 collapse and survives only in git
  history.
