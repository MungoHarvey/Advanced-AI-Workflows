# Releasing

How a version of Advanced AI Workflows is cut, tagged, and published on GitHub.

This repository follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), matching the convention already
used by [advanced-planning](https://github.com/MungoHarvey/advanced-planning).

---

## What a version means here

AAW is an integration layer, not a library. Its public surface is the set of artefacts it
tells users to install and the routing contract between the component tools. Version numbers
describe *that* surface, not the component tools' own versions.

| Bump | When |
|---|---|
| **major** | A documented install path, skill name, or routing contract is removed or changed incompatibly. |
| **minor** | A new component, runtime, skill, or command is supported; a tool is deprecated. |
| **patch** | Fixes and documentation corrections that leave the install surface unchanged. |

Component tool versions are recorded in the compatibility manifest, not in this version number.
A release states the exact commits of gstack, advanced-planning, and superpowers it was tested
against.

---

## Source of truth

| Artefact | Role |
|---|---|
| `VERSION` | The single authoritative version string. One line, no `v` prefix. |
| `CHANGELOG.md` | Human-readable history. Every release has an entry; `[Unreleased]` accumulates between releases. |
| Git tag `vX.Y.Z` | Annotated tag on the release commit. The tag, not the branch, is the release. |
| GitHub Release | Published from the tag, body drawn from the changelog entry. |

`VERSION`, the changelog heading, and the tag must agree. A release where they disagree is a bug.

---

## Procedure

Run from a clean checkout on the release branch.

### 1. Verify the tree is releasable

```bash
git status --porcelain          # expect: empty
git log --oneline -1            # note the release commit
```

Confirm every documented install source is actually tracked — the v0.1 blocking defect was a
skill that the docs told users to install but that had never been committed:

```bash
git ls-files .claude/skills/    # every skill referenced by README/SETUP must appear
```

> From v0.2 this check is a packaging test that fails on any missing documented install source,
> rather than a manual step.

### 2. Decide the number

Read `[Unreleased]` in `CHANGELOG.md` and apply the bump table above. Deprecating a component
is a **minor** bump; removing its documented install path is **major**.

### 3. Update `VERSION` and the changelog

```bash
printf '0.2.0\n' > VERSION
```

In `CHANGELOG.md`: rename `[Unreleased]` to `[0.2.0] - YYYY-MM-DD`, open a fresh empty
`[Unreleased]` above it, and update the two link definitions at the foot of the file.

### 4. Commit

```bash
git add VERSION CHANGELOG.md
git commit -m "release: v0.2.0"
```

### 5. Tag

Annotated, never lightweight — the tag message is part of the record.

```bash
git tag -a v0.2.0 -m "v0.2.0 — <one-line summary>"
git tag -n99 v0.2.0     # verify before pushing
```

### 6. Push — human gate

Pushing a tag is an external write and is **not** self-approvable by an agent. It requires
explicit human authorisation naming the tag and the branch.

```bash
git push origin <branch>
git push origin v0.2.0
```

### 7. Publish the GitHub Release

```bash
gh release create v0.2.0 --title "v0.2.0 — <summary>" --notes-file <(sed -n '/## \[0.2.0\]/,/^## \[/p' CHANGELOG.md | sed '$d')
```

Check the rendered release body before announcing it anywhere.

---

## Retrospective tags

`v0.1.0` was tagged on 2026-08-26 against `3422a8c` (2026-06-08), the closeout commit for
phases 1–2, because the repository had no release history despite v0.1 being complete and
smoke-tested. Retrospective tags are legitimate for recovering history, but:

- tag the commit that *was* the release, never a later one;
- say in the changelog entry that the tag was applied retrospectively and when;
- never move or delete a tag once pushed — supersede it with a new version instead.

---

## Rules

1. **The tag is the release.** Branches move; tags do not.
2. **Never move a published tag.** If a release is wrong, cut the next patch version.
3. **Push and release are human gates.** An agent may prepare and tag locally; it may not push.
4. **`VERSION`, changelog, and tag agree**, or the release does not happen.
5. **A release claims only what was tested.** If an integration was simulated rather than
   exercised, it does not appear in the release notes as supported.
