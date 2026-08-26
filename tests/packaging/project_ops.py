#!/usr/bin/env python3
"""The file operations `setup-with-claude` performs, executable, for testing.

    python tests/packaging/project_ops.py install   --project P [--source S]
    python tests/packaging/project_ops.py uninstall --project P
    python tests/packaging/project_ops.py fingerprint --project P

Why this exists, stated plainly so nobody mistakes it for the product
--------------------------------------------------------------------

`setup-with-claude` is a conversation. You cannot assert that a conversation is
idempotent. What you *can* assert is that the file operations it documents are:
apply them twice and the tree is unchanged, undo them and the user's own content
survives.

This module performs exactly the writes the skill documents:

  1. append the fenced routing block to CLAUDE.md, between the aaw-routing markers;
  2. merge the four `.advanced-plans/**` permissions and the PostToolUse Write hook
     into `.claude/settings.json`, without duplicating what is already there;
  3. copy the `gstack-to-plans` glue skill into the project.

The manifest is not written here - `tools/aaw-audit.py --write-manifest` does that,
and the test drives it, so that the thing under test is the shipped tool rather
than a reimplementation of it.

This is test scaffolding. If it and the skill disagree, that is a finding about one
of them, and the skill is the specification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SKILL_DIR = os.path.join(REPO, ".claude", "skills", "setup-with-claude")
ROUTING_SOURCE = os.path.join(SKILL_DIR, "references", "claude-md-routing.md")
SETTINGS_SOURCE = os.path.join(SKILL_DIR, "references", "settings-snippet.json")
GLUE_SOURCE = os.path.join(REPO, ".claude", "skills", "gstack-to-plans")

EXIT_NEEDS_HUMAN = 3   # a guard in the skill says to ask; a script cannot, so it stops
OURS = "aaw-hook"   # the marker Step U6 uses to recognise the hook we added
BEGIN = "<!-- aaw-routing:begin -->"
END = "<!-- aaw-routing:end -->"


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read().replace("\r\n", "\n")


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ---------------------------------------------------------------- CLAUDE.md

def routing_block():
    text = read(ROUTING_SOURCE)
    i, j = text.index(BEGIN), text.index(END) + len(END)
    return text[i:j]


def strip_block(text):
    """Remove the fenced block and the blank lines the insert added around it."""
    if BEGIN not in text or END not in text:
        return text
    i = text.index(BEGIN)
    j = text.index(END) + len(END)
    before, after = text[:i], text[j:]
    return before.rstrip("\n") + ("\n" if before.strip() else "") + after.lstrip("\n")


def install_routing(project):
    path = os.path.join(project, "CLAUDE.md")
    existing = read(path) if os.path.isfile(path) else ""
    # Replace rather than append when a block is already there. Appending is how a
    # "refresh" ends up with two routing blocks and a user wondering which one wins.
    body = strip_block(existing).rstrip("\n")
    parts = [body] if body else []
    parts.append(routing_block())
    write(path, "\n\n".join(parts) + "\n")


def uninstall_routing(project):
    """Return "removed", "absent", "kept", or "refused"."""
    path = os.path.join(project, "CLAUDE.md")
    if not os.path.isfile(path):
        return "absent"

    raw = read(path)
    if (BEGIN in raw) != (END in raw):
        # Step U1. One marker without the other means somebody edited CLAUDE.md
        # by hand and we no longer know where the block ends. Guessing here would
        # delete the user's own writing, so refuse and leave the file alone.
        sys.stderr.write(
            "project_ops: refused to edit CLAUDE.md - aaw-routing markers are "
            "incomplete. Nothing was changed.\n")
        return "refused"
    if BEGIN not in raw:
        return "kept"
    text = strip_block(raw).rstrip("\n")
    # Step U3's guard is "empty or whitespace-only", not "empty". A CLAUDE.md left
    # holding three blank lines is still, to the user, a file they did not write.
    if text.strip():
        write(path, text + "\n")
        return "removed"
    os.remove(path)
    return "removed"


# ---------------------------------------------------------------- settings.json

def snippet():
    doc = json.loads(read(SETTINGS_SOURCE))
    perms = doc["permissions"]["allow"]
    matcher = _strip_annotations(doc["hooks"]["PostToolUse"][0])
    return perms, matcher


def _strip_annotations(value):
    """Drop `_comment`-style keys: they document the reference file, not the install.

    The snippet carries `_comment` and `_merge_instructions` for the human reading
    it. Nobody intends `_merge_instructions` to land in a project settings.json,
    and the same argument disqualifies `_comment`.
    """
    if isinstance(value, dict):
        return {k: _strip_annotations(v) for k, v in value.items()
                if not k.startswith("_")}
    if isinstance(value, list):
        return [_strip_annotations(v) for v in value]
    return value


def _survivors(post, matcher):
    """The PostToolUse entries that would remain after our hook is removed."""
    kept = []
    for item in post:
        if item.get("matcher") != matcher["matcher"]:
            kept.append(item)
            continue
        if [h for h in item.get("hooks", []) if OURS not in (h.get("command") or "")]:
            kept.append(item)
    return kept


def hook_commands(matcher):
    return [h.get("command") for h in matcher.get("hooks", [])]


def install_settings(project):
    # No sort_keys anywhere in this file. json.load preserves key order, so an
    # unchanged input round-trips to the same bytes, and an uninstall really does
    # give the user back the file they wrote rather than a reformatted copy of it.
    path = os.path.join(project, ".claude", "settings.json")
    doc = json.loads(read(path)) if os.path.isfile(path) else {}
    perms, matcher = snippet()

    allow = doc.setdefault("permissions", {}).setdefault("allow", [])
    for entry in perms:
        if entry not in allow:          # no duplicates on a second run
            allow.append(entry)

    post = doc.setdefault("hooks", {}).setdefault("PostToolUse", [])
    target = None
    for item in post:
        if item.get("matcher") == matcher["matcher"]:
            target = item
            break
    if target is None:
        post.append(json.loads(json.dumps(matcher)))
    else:
        # Add to the existing Write matcher rather than creating a second one.
        # Two matchers for "Write" is not an error Claude Code reports; it just
        # runs both, and the duplicate survives every later refresh.
        have = {c for c in hook_commands(target) if c}
        for hook in matcher.get("hooks", []):
            if hook.get("command") not in have:
                target.setdefault("hooks", []).append(json.loads(json.dumps(hook)))

    write(path, json.dumps(doc, indent=2) + "\n")


def uninstall_settings(project):
    """Step U6. Returns "removed", "absent", or "refused".

    U6 ends with a guard: if removing our entries would leave an empty array that
    another tool also uses, show the diff and ask rather than writing blindly. A
    non-interactive script cannot ask, so it does the other half of that sentence -
    it does not write - and says which array it would have emptied. Silently
    deleting the key, which is what it did before review, is precisely the "writing
    blindly" the step forbids.
    """
    path = os.path.join(project, ".claude", "settings.json")
    if not os.path.isfile(path):
        return "absent"
    original = read(path)
    doc = json.loads(original)
    perms, matcher = snippet()

    would_empty = []
    allow = doc.get("permissions", {}).get("allow")
    if isinstance(allow, list) and allow and not [a for a in allow if a not in perms]:
        would_empty.append("permissions.allow")
    post_check = doc.get("hooks", {}).get("PostToolUse")
    if isinstance(post_check, list) and post_check and not _survivors(post_check, matcher):
        would_empty.append("hooks.PostToolUse")
    if would_empty:
        sys.stderr.write(
            "project_ops: refused to edit settings.json - removing our entries would "
            "empty %s, which Step U6 says to confirm with the user first. Nothing was "
            "changed.\n" % " and ".join(would_empty))
        return "refused"

    allow = doc.get("permissions", {}).get("allow")
    if isinstance(allow, list):
        doc["permissions"]["allow"] = [a for a in allow if a not in perms]

    post = doc.get("hooks", {}).get("PostToolUse")
    if isinstance(post, list):
        kept = []
        for item in post:
            if item.get("matcher") != matcher["matcher"]:
                kept.append(item)
                continue
            # Step U6 identifies our hook by the `aaw-hook` marker in the command,
            # not by an exact string match, so a reformatted command is still
            # recognised. Another tool's hook on the same matcher is not ours to
            # delete, and taking it would be the worst kind of uninstall.
            others = [h for h in item.get("hooks", [])
                      if OURS not in (h.get("command") or "")]
            if others:
                item["hooks"] = others
                kept.append(item)
        doc["hooks"]["PostToolUse"] = kept

    result = json.dumps(doc, indent=2) + "\n"
    if result == original:
        # Nothing of ours was in there. Writing an identical file is harmless
        # until the day it is not identical - a reformat, a changed newline -
        # so do not write at all.
        return "unchanged"
    write(path, result)
    return "removed"


# ---------------------------------------------------------------- glue skill

def install_glue(project, source=GLUE_SOURCE):
    """Step 6. Case B - already installed - is "note it and continue"."""
    dest = os.path.join(project, ".claude", "skills", "gstack-to-plans")
    if os.path.isdir(dest):
        # It used to rmtree first. That is not what Step 6 says, and the difference
        # is not cosmetic: a user who added a note or a second file to the glue skill
        # directory would have lost it on the next refresh. Reviewed and corrected.
        sys.stderr.write("project_ops: gstack-to-plans already installed - left as it is\n")
        return "present"
    shutil.copytree(source, dest)
    return "installed"


def uninstall_glue(project):
    dest = os.path.join(project, ".claude", "skills", "gstack-to-plans")
    if os.path.isdir(dest):
        shutil.rmtree(dest)


def uninstall_manifest(project):
    # The superseded v0.1 file, if this project still carries one.
    legacy = os.path.join(project, ".claude", "integrations.json")
    if os.path.isfile(legacy):
        os.remove(legacy)
    d = os.path.join(project, ".aaw")
    f = os.path.join(d, "installed.json")
    if os.path.isfile(f):
        os.remove(f)
    # Only if empty. Another tool may have put something in .aaw/, and an uninstall
    # that takes a directory it does not own with it is why people stop running them.
    if os.path.isdir(d) and not os.listdir(d):
        os.rmdir(d)


# ---------------------------------------------------------------- fingerprint

def fingerprint(project):
    """A stable hash of every file in the project, for before/after comparison."""
    rows = []
    for root, dirs, files in os.walk(project):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, project).replace(os.sep, "/")
            with open(full, "rb") as fh:
                blob = fh.read()
            # No line-ending normalisation. It used to fold CRLF to LF here, which
            # made every "byte-identical" claim in the test one step weaker than it
            # sounded: a change that only touched line endings was invisible. If the
            # install rewrites a user file with different endings, that IS a change
            # to the file and the test should say so.
            rows.append("%s  %s" % (hashlib.sha256(blob).hexdigest(), rel))
    return "\n".join(rows) + ("\n" if rows else "")


# ----------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(prog="project_ops")
    parser.add_argument("action", choices=["install", "uninstall", "fingerprint"])
    parser.add_argument("--project", required=True)
    parser.add_argument("--source", default=GLUE_SOURCE,
                        help="glue skill source directory")
    args = parser.parse_args(argv)

    project = os.path.abspath(args.project)
    if not os.path.isdir(project):
        sys.stderr.write("project_ops: not a directory: %s\n" % project)
        return 2

    if args.action == "install":
        install_routing(project)
        install_settings(project)
        install_glue(project, args.source)
    elif args.action == "uninstall":
        # Step U1 is unambiguous: if either marker is absent, STOP, and do not
        # proceed to the remaining uninstall steps until the user has said to. An
        # earlier version of this file carried on and a comment claiming the skill
        # said so. It does not. The comment was wrong and the behaviour with it.
        if uninstall_routing(project) == "refused":
            return EXIT_NEEDS_HUMAN
        if uninstall_settings(project) == "refused":
            return EXIT_NEEDS_HUMAN
        uninstall_glue(project)
        uninstall_manifest(project)
    else:
        sys.stdout.write(fingerprint(project))
    return 0


if __name__ == "__main__":
    sys.exit(main())
