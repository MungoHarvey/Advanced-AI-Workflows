#!/usr/bin/env bash
# The gstack-to-plans PostToolUse hook fires on the paths this platform produces.
#
# The cases live in hook_path.py because they execute the shipped hook command and
# compare its output across path shapes, which needs a process runner rather than
# the shell. This wrapper exists so the check joins run-all.sh with the same
# exit-code contract as its siblings.
#
# Exit 0 = every case behaved. 1 = a case failed. 2 = the test could not run.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES="$HERE/hook_path.py"

PY=""
for candidate in python3 python py; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1 || continue
  PY="$candidate"
  break
done
[ -n "$PY" ] || { echo "hook-path: FATAL - no Python 3.8+ interpreter found"; exit 2; }
[ -f "$CASES" ] || { echo "hook-path: FATAL - $CASES does not exist"; exit 2; }

"$PY" "$CASES"
exit $?
