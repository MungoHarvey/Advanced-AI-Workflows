#!/usr/bin/env bash
# Plugin-scoped detection: a plugin counts only when it is enabled.
#
# The cases live in plugin_detection.py because they build fake user profiles and
# compare structured results, which is Python's job rather than the shell's. This
# wrapper exists so the check joins run-all.sh with the same exit-code contract as
# its siblings.
#
# Exit 0 = every case behaved. 1 = a case failed. 2 = the test could not run.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES="$HERE/plugin_detection.py"

PY=""
for candidate in python3 python py; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1 || continue
  PY="$candidate"
  break
done
[ -n "$PY" ] || { echo "plugin-detection: FATAL - no Python 3.8+ interpreter found"; exit 2; }
[ -f "$CASES" ] || { echo "plugin-detection: FATAL - $CASES does not exist"; exit 2; }

"$PY" "$CASES"
exit $?
