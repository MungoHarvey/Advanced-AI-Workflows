# Advanced AI Workflows

The vocabulary of a repo that configures AI coding agents: which skills a project gets, how their presence is proven, and how work moves from a foggy idea to merged code across several agent runtimes.

## Language

### Installation

**Component**:
A unit of installation that the manifest can say is present or absent. v0.3 has four: `mp-skills`, `gstack`, `aaw-tools`, `tracker`.
_Avoid_: tool, package, plugin (a harness plugin is one *scope* a component can have, not a component)

**Manifest**:
`.aaw/installed.json` — the written answer to "which components are installed here", produced by the detector after a sentinel was confirmed.
_Avoid_: config, registry

**Sentinel**:
A file whose existence (and, for pinned skills, whose content hash) proves a component is installed. A data directory is never a sentinel.
_Avoid_: marker, probe

**Lock**:
`skills-lock.json` — the pin of every skill installed from a skills source: source repo, path, content hash. The source of truth for `mp-skills` and `aaw-tools`; the manifest only records what the lock proves.
_Avoid_: manifest (that is the other file)

**Skills source**:
A git repository that skills are pinned from. Matt Pocock's `mattpocock/skills` and this repository are both skills sources.

### Routing

**Spine**:
The Matt Pocock skill set as a whole; the planning-and-build path every AAW repo gets and that wins whenever another skill overlaps it.
_Avoid_: core, framework

**Gap-filler**:
A skill kept from gstack because the spine has no equivalent. Gated on the `gstack` component and routed to by name; gstack itself installs whole.
_Avoid_: subset, extension

**Main flow**:
The default path through the spine: grill → (prototype) → spec → tickets → implement. Taken from MP's own router.

**On-ramp**:
A starting situation that merges onto the main flow: triage, a bug, or a foggy effort (wayfinder).
_Avoid_: entry point, front door (the old seven-rule vocabulary)

### Work

**Map**:
The single tracker issue that indexes an effort's decisions, fog and scope; wayfinder's canonical artefact.

**Decision ticket**:
A child issue of a map whose resolution is a decision, not a deliverable.
_Avoid_: task, todo, loop (advanced-planning's retired unit)

**Frontier**:
The open, unblocked, unclaimed child tickets of a map — what can be taken now.

**Claim**:
Assigning a ticket to oneself before any work, plus (for a herdr worker) a first comment naming the worker. The assignee is the claim.

**Gate**:
A review by a model different from the implementer's, recorded as a verdict, at a PR and at a map's close.
_Avoid_: phase gate, run-gate (the retired phase-boundary form)
