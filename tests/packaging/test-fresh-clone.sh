#!/usr/bin/env bash
#
# Packaging test: does a FRESH CLONE of this repository contain the install sources the
# documentation names?
#
# The point is the fresh clone. Checking the working tree proves nothing, because an untracked
# file is present there and absent for everyone else. This is what let
# .claude/skills/gstack-to-plans/SKILL.md be documented, installed, and never committed.
#
# Two checks, and it is worth being precise about which is which. The first walks
# required-sources.txt and asserts each listed path is present, non-empty and tracked. That
# list is curated by hand, so on its own it says nothing about paths nobody added to it. The
# second closes part of that gap from the other side: it scans the install docs for
# .claude/skills/... paths and fails on any that the list does not declare. Together they
# cover the omission that caused the original defect. They are not a completeness proof.
#
# Usage:
#   tests/packaging/test-fresh-clone.sh [--repo <path>] [--ref <ref>] [--keep]
#
#   --repo   repository to clone from  (default: the repo containing this script)
#   --ref    ref to check out in the clone (default: HEAD)
#   --keep   do not delete the temporary clone, and print its path
#
# Git runs here with the user's global and system config switched off, so two people
# running this get the same answer. That is isolation of git's configuration, not of
# the profile as a whole: the clone still happens under the real user account.
#
# Exit 0 = every required source is present, non-empty, and tracked.
# Exit 1 = at least one is missing. Every failure is listed; it does not stop at the first.

set -uo pipefail

# Run git without the user's global or system configuration. A reviewer pointed out
# that this script claimed profile isolation while every git invocation inherited
# whatever ~/.gitconfig happens to say - core.autocrlf, init.defaultBranch, a
# filter driver - so the result depended on the machine as much as on the commit.
# These two variables are read by git 2.32 and later; on an older git they are
# ignored and the test is no worse off than it was.
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null

SELF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$SELF_DIR/required-sources.txt"

REPO=""
REF="HEAD"
KEEP=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --ref)  REF="$2";  shift 2 ;;
    --keep) KEEP=1;    shift ;;
    -h|--help) sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$REPO" ]; then
  REPO="$(git -C "$SELF_DIR" rev-parse --show-toplevel)" || {
    echo "FATAL: could not locate the repository from $SELF_DIR" >&2; exit 2; }
fi

[ -f "$MANIFEST" ] || { echo "FATAL: manifest not found: $MANIFEST" >&2; exit 2; }

TMP="$(mktemp -d 2>/dev/null)" || { echo "FATAL: mktemp -d failed" >&2; exit 2; }
CLONE="$TMP/clone"
cleanup() {
  if [ "$KEEP" -eq 1 ]; then
    echo "kept: $TMP"
  else
    rm -rf "$TMP"
  fi
}
trap cleanup EXIT

echo "packaging: cloning $REPO at $REF"
if ! git clone --quiet --no-hardlinks --no-local "$REPO" "$CLONE" 2>"$TMP/clone.err"; then
  echo "FATAL: clone failed" >&2; sed 's/^/  /' "$TMP/clone.err" >&2; exit 2
fi
if ! git -C "$CLONE" checkout --quiet "$REF" 2>"$TMP/checkout.err"; then
  echo "FATAL: checkout of $REF failed" >&2; sed 's/^/  /' "$TMP/checkout.err" >&2; exit 2
fi

echo "packaging: clone at $(git -C "$CLONE" rev-parse --short HEAD)"

# The set of tracked paths, read once. Membership is checked against this rather than by
# invoking git per path.
TRACKED="$TMP/tracked.txt"
git -C "$CLONE" ls-files > "$TRACKED"

checked=0
failed=0
: > "$TMP/declared.txt"

while IFS= read -r line; do
  # strip comments and surrounding whitespace. The trailing-whitespace sed also removes a
  # trailing CR, so a CRLF checkout of the manifest is handled; .gitattributes pins it to LF
  # anyway so the test does not depend on that side effect.
  path="${line%%#*}"
  path="$(printf '%s' "$path" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
  [ -n "$path" ] || continue

  checked=$((checked + 1))
  echo "$path" >> "$TMP/declared.txt"

  if [ ! -e "$CLONE/$path" ]; then
    echo "  MISSING   $path"
    failed=$((failed + 1))
    continue
  fi
  if [ ! -s "$CLONE/$path" ]; then
    echo "  EMPTY     $path"
    failed=$((failed + 1))
    continue
  fi
  if ! grep -qxF "$path" "$TRACKED"; then
    # Present in the clone but not tracked would mean the manifest names something Git is not
    # carrying. In a clone that should be impossible, so it indicates a broken test, not a
    # broken package — report it as a failure either way rather than passing quietly.
    echo "  UNTRACKED $path"
    failed=$((failed + 1))
    continue
  fi
  echo "  ok        $path"
done < "$MANIFEST"

# --------------------------------------------------------------------------
# Is the manifest itself complete?
# --------------------------------------------------------------------------
# Everything above checks that the listed paths exist. It cannot check that the list
# names everything the documentation does - a reviewer's point, and a fair one, since
# the headline claim was exactly that. So: scan the install documentation for paths
# that look like install sources, and fail if one of them is not on the list.
#
# The pattern is deliberately narrow - repo-relative paths under .claude/skills/ that
# the docs mention - because that is the shape of the defect this file exists to catch.
# It is not a proof of completeness. It is one class of omission, closed.
EXCLUDED_RE='^\.claude/skills/(gstack|brainstorming|phase-plan-creator|superpowers)/'
DOCS=""
for doc in SETUP.md README.md .claude/skills/setup-with-claude/SKILL.md; do
  [ -f "$CLONE/$doc" ] && DOCS="$DOCS $CLONE/$doc"
done

MENTIONED="$TMP/mentioned.txt"
: > "$MENTIONED"
if [ -n "$DOCS" ]; then
  # shellcheck disable=SC2086
  grep -ohE '\.claude/skills/[A-Za-z0-9._-]+/[A-Za-z0-9._/-]+\.(md|json|py)' $DOCS \
    | sed 's/[.,;:)]*$//' | sort -u > "$MENTIONED"
fi

undeclared=0
while IFS= read -r cand; do
  [ -n "$cand" ] || continue
  echo "$cand" | grep -qE "$EXCLUDED_RE" && continue
  [ -e "$CLONE/$cand" ] || continue          # a path the docs name that does not exist
                                             # here is a docs bug, not a packaging one
  if ! grep -qxF "$cand" "$TMP/declared.txt" 2>/dev/null; then
    echo "  UNDECLARED $cand"
    echo "             the docs name it and required-sources.txt does not list it"
    undeclared=$((undeclared + 1))
  fi
done < "$MENTIONED"

if [ "$undeclared" -gt 0 ]; then
  failed=$((failed + undeclared))
  checked=$((checked + undeclared))
fi

echo
if [ "$checked" -eq 0 ]; then
  echo "packaging: FAIL — the manifest listed no paths, so nothing was checked"
  exit 1
fi

if [ "$failed" -eq 0 ]; then
  echo "packaging: PASS — $checked/$checked required install sources present in a fresh clone"
  exit 0
fi

echo "packaging: FAIL — $failed of $checked required install sources missing or unusable in a fresh clone"
echo
echo "A source named by the documentation is not in the clone. Either commit it, or stop"
echo "documenting it. Check .gitignore first: a whitelist that admits only some skill"
echo "directories is what caused this the last time."
exit 1
