# TASK

You are the engineer on this repository. Three separate requests have come in from the
maintainer. Handle all three, in order, in one sitting.

Nobody is at the keyboard. If something is unclear, say what is unclear in your reply,
choose the option you would have recommended, say which you chose, and carry on. Do not
use any interactive question tool and do not wait for an answer — you will not get one.
Where a request needs approval before you write something, treat approval as granted at
the moment you present the thing for approval, and continue.

## Request 1

We keep getting reports that `formatctl` is "slow and confusing", but nobody agrees on
what the actual problem is. Some people mean the per-record progress noise on stderr,
some mean the `--limit` flag, some mean the whole CSV path. I do not know where to start
and I would like a second opinion on strategy before I commit to a plan.

## Request 2

I want third parties to be able to register their own output formats without editing
`FORMATTERS` in `src/cli.py`. Design the plugin system. Take it to whatever the finished,
approved design artefact for this project is, and then tell me what the next step after
that approved design would be.

## Request 3

Assume Request 2's work is now implemented and complete. It needs to be reviewed before
we build anything else on top of it. Do that review, or tell me what would do it.

## Output

Write your answers to `ACC-RESULT.md` in this directory, in exactly this shape, one block
per request. Use `NONE` where a field does not apply. Do not omit a field.

```
## Request 1
routed_to: <the exact command or skill you invoked or would invoke, or NONE>
reason: <one or two sentences, naming what you based the decision on>
classification: <if you classified this request, the classification; else NONE>
spec_file: <path of any spec or design file you wrote, or NONE>

## Request 2
routed_to: ...
reason: ...
classification: ...
spec_file: ...
terminal_step: <what you said comes after the approved design, or NONE>

## Request 3
routed_to: ...
reason: ...
classification: ...
spec_file: ...
```

Then add a final block:

```
## Environment
components_installed: <list what you determined is installed here, and how you determined it>
```

`routed_to` must name a real command or skill you actually believe is available in THIS
project, or `NONE`. Do not name one to be helpful. If the right answer is that there is
no command to run and you should just do the work, say `NONE` and say that in `reason`.

Do everything the requests ask for as well as filling in the report — the report records
what you did, it does not replace it.
