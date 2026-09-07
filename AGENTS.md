# AGENTS.md

## Working agreement

The framework that used to sit here was retired on 2026-09-07. What replaced it is
six standing habits, kept in full at
`herdr-ops/WORKING-AGREEMENT.md`
and summarised here because this is the file every runtime loads first.

1. **One bounded unit of work per session.** A ticket or a pull request is the bound,
   never an iteration counter.
2. **One specialist skill in context at a time.** Load it, act on it, drop it.
3. **Finish with three sentences: done, failed, needed.** In one place, as the ticket
   comment or the PR summary.
4. **The implementer never marks its own work done.** A different vendor's CLI reviews
   the diff against the ticket's acceptance lines.
5. **Every task carries an observable outcome condition.** A criterion that cannot fail
   is not a criterion.
6. **Workers do not spawn workers.** The controller sequences everything.

Planning happens inside the installed skills — grilling, wayfinder, to-spec, to-tickets,
implement, code-review — and dispatch happens in herdr. There is no `/plan-and-phase`,
`/new-phase`, `/next-loop`, `/run-gate` or `/setup-aaw` in this repo any more, and no
`.aaw/installed.json` to read. If you find a document that names one, it predates the
collapse.

## Agent skills

### Issue tracker

Issues and specs live in this repo's GitHub Issues, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage labels, unchanged (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root and ADRs under `docs/adr/`, created lazily by `/domain-modeling`. See `docs/agents/domain.md`.

### Worker attribution

A commit authored by a delegated worker ends with `Co-Authored-By: <provider> via herdr worker <name>` and `Ticket: #<n>`, stated verbatim in the worker's envelope at dispatch — it cannot be repaired afterwards without rewriting history. See `docs/agents/worker-attribution.md`.
