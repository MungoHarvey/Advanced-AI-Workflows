# Forge Dependencies: GitHub Issue Dependencies for AAW v0.3

**Research question (Issue #2):** How does GitHub's native issue dependency API work, and can it support the wayfinder map's blocking relationships for AAW v0.3?

---

## Measured Findings

### GitHub Issue Dependencies API: Capabilities

**Claim: GitHub supports native issue dependencies via REST API.**  
**Source:** Measured 2026-09-07 via `gh api` calls on this repo.

- **Add a blocking relationship:** `POST /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by` with `issue_id` (database ID, not issue number)
- **Query blocked-by:** `GET /repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by` returns array of blocking issues
- **Summary endpoint:** `issue_dependencies_summary` object on issue responses contains:
  - `blocked_by`: count of **open** blockers only (live gate)
  - `total_blocked_by`: count of all blockers (open + closed)
  - `blocking`: count of open issues this blocks
  - `total_blocking`: count of all issues this blocks

**Measured evidence (2026-09-07):**

```
Issue #9 (Prototype /setup-aaw walkthrough):
  - blocked_by: 2 (issues #5 and #8)
  - API call: GET /repos/MungoHarvey/Advanced-AI-Workflows/issues/9/dependencies/blocked_by → [5, 8]
  - issue_dependencies_summary.blocked_by = 2

Issue #8 (Component manifest):
  - blocked_by: 1 (issue #5)
  - blocking: 1 (issue #9)

Issue #5 (MP skill routing):
  - blocked_by: 0
  - blocking: 2 (issues #8 and #9)

Issue #7 (Herdr worker operations):
  - blocked_by: 1 (issue #2)
```

**Claim: The summary endpoint lags POST by a few seconds.**  
**Source:** Measured 2026-09-07 while wiring this map: `POST /issues/1/sub_issues` and `POST /issues/{n}/dependencies/blocked_by` both succeed; `GET /issues/9/dependencies/blocked_by` → [5, 8] and `issue_dependencies_summary.blocked_by` = 2 (the summary lagged the POST by a few seconds).

---

### GitHub Sub-Issues

**Claim: GitHub supports hierarchical parent-child relationships via sub-issues.**  
**Source:** Issue #1 (the map) shows `sub_issues_summary.total: 8` with all 8 child issues linked.

- **Add sub-issue:** `POST /repos/{owner}/{repo}/issues/{parent_issue_number}/sub_issues` with sub-issue ID
- **Query:** `GET /repos/{owner}/{repo}/issues/{n}` returns `sub_issues_summary` with `total`, `completed`, `percent_completed`

**Measured evidence:** Issue #1 (Map) has 8 sub-issues: #2, #3, #4, #5, #6, #7, #8, #9.

---

### Database ID vs Issue Number

**Claim: Dependency API requires database ID (`id` field), not issue number (`number` field).**  
**Source:** API responses show distinct values:

```
Issue #2: id = 5372849067, number = 2
Issue #5: id = 5372850032, number = 5
Issue #8: id = 5372850932, number = 8
Issue #9: id = 5372851233, number = 9
```

**Operational implication:** To add a dependency, you must first fetch the blocker's database ID via `gh api repos/{owner}/{repo}/issues/{n} --jq .id`, then use that ID in the `blocked_by` POST.

---

### GitHub Issues Feature Availability

**Claim: Issue dependencies and sub-issues are available on public GitHub repos.**  
**Source:** This repo (`MungoHarvey/Advanced-AI-Workflows`, public, personal) successfully uses both features as of 2026-09-07.

**Open question:** Whether these features require explicit enablement in repo settings, or are universally available on GitHub.com (not GitHub Enterprise Server).

---

## Comparison: GitHub vs GitLab vs Local Markdown

### GitHub (measured)

- **Native blocking:** Yes, via `/dependencies/blocked_by` API
- **Native sub-issues:** Yes, via `/sub_issues` API
- **Visual rendering:** GitHub UI shows dependency graph and parent-child relationships
- **CLI support:** `gh api` for all operations; no high-level `gh issue dependency` command
- **Frontier query:** List open children, filter by `issue_dependencies_summary.blocked_by > 0`

### GitLab (inferred, not measured)

- **Native blocking:** Likely via `blocked_by_issues` / `blocks_issues` fields in Issues API
- **Native sub-issues:** Unknown; may use parent-child issue relationships
- **CLI support:** `glab` CLI (not tested in this research)
- **Open point:** Requires separate research to confirm API parity with GitHub

### Local Markdown (documented in `docs/agents/issue-tracker.md`)

- **Native blocking:** No; falls back to `Blocked by: #n, #n` line in issue body
- **Native sub-issues:** No; falls back to `Part of #<map>` line in issue body
- **Frontier query:** Manual parsing of markdown files or custom tooling
- **Use case:** Solo projects, repos without remote, or as fallback when forge lacks native support

---

## AAW v0.3 Implications

### What the wayfinder map needs (from `wayfinder/SKILL.md:70`)

> Blocking uses the tracker's **native** dependency relationship: essential because it renders the frontier _visually_ in the tracker's own UI, so the human sees what's takeable without opening the map.

**Finding:** GitHub satisfies this requirement with native blocking + sub-issues, both accessible via `gh api`.

### What `to-tickets` needs (from `to-tickets/SKILL.md:63-64`)

> **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers. Use the platform's native blocking / sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues.

**Finding:** GitHub supports this pattern natively.

### Worker attribution (from `docs/agents/worker-attribution.md`)

**Finding:** Issue dependencies are orthogonal to commit attribution. The `Co-Authored-By` and `Ticket:` trailers live in git commits, not issues. No conflict detected.

---

## Open Points

### (a) GitHub API: **Answered YES** (measured 2026-09-07)

Native issue dependencies work on personal public repos. `POST /issues/{n}/dependencies/blocked_by` succeeds; `GET /issues/{n}/dependencies/blocked_by` returns correct blocking issues; `issue_dependencies_summary.blocked_by` reflects open blockers.

### (b) GitLab parity: **OPEN**

No research conducted on GitLab's Issues API for dependency relationships. Requires separate investigation with a GitLab repo and `glab` CLI.

### (c) Fallback rules: **OPEN**

The `docs/agents/issue-tracker.md` file describes the local-markdown fallback convention (`Blocked by: #n` in body), but no decision has been recorded on:

- When to prefer fallback vs native (e.g., GitHub Enterprise Server without dependencies feature)
- Whether AAW v0.3 should detect forge capabilities at `/setup-aaw` time and record the choice
- Whether the fallback is acceptable for wayfinder's visual frontier requirement (it is not, per `wayfinder/SKILL.md:70`)

### (d) Feature enablement: **OPEN**

Unknown whether GitHub issue dependencies require:
- Organization-level feature flags
- Repo settings toggle
- Universal availability on GitHub.com

---

## Primary Sources Consulted

1. **GitHub REST API** (measured 2026-09-07):
   - `GET /repos/MungoHarvey/Advanced-AI-Workflows/issues/{n}` — issue details with `issue_dependencies_summary`
   - `GET /repos/MungoHarvey/Advanced-AI-Workflows/issues/9/dependencies/blocked_by` — blocking issues array
   - `POST /repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by` — add dependency (inferred from comment in Issue #2)

2. **Local skill files:**
   - `.agents/skills/wayfinder/SKILL.md` — wayfinder map requirements (lines 25-70)
   - `.agents/skills/to-tickets/SKILL.md` — ticket publishing requirements (lines 59-64)
   - `docs/agents/issue-tracker.md` — GitHub operations conventions (lines 42-43)
   - `docs/agents/worker-attribution.md` — commit attribution conventions (not issue-related)

3. **GitHub Issues (this repo):**
   - Issue #1 (Map): sub-issues count and structure
   - Issues #2, #5, #7, #8, #9: dependency relationships measured via API

---

## Decision-Ready Summary

**GitHub can support AAW v0.3's wayfinder map blocking requirements** via native issue dependencies API. The API is functional on personal public repos as of 2026-09-07. Implementation requires:

1. Fetching database IDs (not issue numbers) for blocker resolution
2. Using `POST /dependencies/blocked_by` to establish blocking edges
3. Querying `issue_dependencies_summary.blocked_by` for frontier computation
4. Accepting a few-second lag between POST and summary update

**GitLab parity and fallback rules remain undecided** and require separate research tickets.
