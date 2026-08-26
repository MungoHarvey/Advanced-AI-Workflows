#!/usr/bin/env bash
#
# Packaging test: does a FRESH CLONE of this repository contain every install source the
# documentation names?
#
# The point is the fresh clone. Checking the working tree proves nothing, because an untracked
# file is present there and absent for everyone else. This is what let
# .claude/skills/gstack-to-plans/SKILL.md be documented, installed, and never committed.
#
# Usage:
#   tests/packaging/test-fresh-clone.sh [--repo <path>] [--ref <ref>] [--keep]
#
#   --repo   repository to clone from  (default: the repo containing this script)
#   --ref    ref to check out in the clone (default: HEAD)
#   --keep   do not delete the temporary clone, and print its path
#
# Exit 0 = every required source is present, non-empty, and tracked.
# Exit 1 = at least one is missing. Every failure is listed; it does not stop at the first.

set -uo pipefail

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

while IFS= read -r line; do
  # strip comments and surrounding whitespace
  path="${line%%#*}"
  path="$(printf '%s' "$path" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
  [ -n "$path" ] || continue

  checked=$((checked + 1))

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
