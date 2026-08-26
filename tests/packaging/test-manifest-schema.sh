#!/usr/bin/env bash
# Check the AAW installation-manifest schema.
#
# Two things are checked, and they are different questions:
#
#   1. the shipped example manifest still validates against the shipped schema —
#      a documented example that does not satisfy its own contract is worse than
#      no example, because it will be copied;
#   2. the fixture corpus behaves as declared, every valid- file valid and every
#      invalid- file invalid, with the built-in validator cross-checked against
#      `jsonschema` whenever that package is importable.
#
# Exit 0 = both hold. 1 = a check failed. 2 = the checker could not run.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

# Resolve an interpreter rather than assuming `python` is on PATH under the name
# this machine happens to use. `py` is the Windows launcher; on a POSIX box only
# the first two exist.
#
# Two passes, and the order matters. A machine can easily have several Python 3
# installations where only one of them has `jsonschema`, and taking the first one
# found would quietly drop the cross-check against the reference implementation
# while still reporting PASS. So: prefer an interpreter that can run the stronger
# check, and fall back to any usable one only when none can.
PY=""
usable=""
for candidate in python3 python py; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1 || continue
  [ -n "$usable" ] || usable="$candidate"
  if "$candidate" -c 'import jsonschema' >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done
[ -n "$PY" ] || PY="$usable"

if [ -z "$PY" ]; then
  echo "manifest-schema: FATAL - no Python 3.8+ interpreter found (tried python3, python, py)"
  exit 2
fi

echo "manifest-schema: using $PY ($("$PY" --version 2>&1))"

status=0

echo "manifest-schema: validating the shipped example against the shipped schema"
"$PY" "$HERE/validate-manifest.py" "$REPO/.aaw/installed.example.json"
example_exit=$?
if [ "$example_exit" -eq 2 ]; then
  echo "manifest-schema: FATAL - the validator could not run"
  exit 2
fi
[ "$example_exit" -eq 0 ] || status=1

echo ""
echo "manifest-schema: running the fixture corpus"
"$PY" "$HERE/validate-manifest.py" --self-check
corpus_exit=$?
if [ "$corpus_exit" -eq 2 ]; then
  echo "manifest-schema: FATAL - the validator could not run"
  exit 2
fi
[ "$corpus_exit" -eq 0 ] || status=1

echo ""
if [ "$status" -eq 0 ]; then
  echo "manifest-schema: PASS"
else
  echo "manifest-schema: FAIL"
fi
exit "$status"
