#!/usr/bin/env bash
# Build the adherence fixtures, then grade the recorded results against the
# current routing block.
#
# Like tests/packaging/run-all.sh this does not stop at the first failure: when
# the block has drifted it has usually drifted in more than one place, and a
# runner that hides the second fault behind the first turns one debugging
# session into three.
#
# Exit 0 = fixtures built and every recorded result matched (or is a recorded
# divergence). 1 = at least one check failed. 2 = a check could not run, which
# is a different problem and must not be reported as a pass.
#
# NOTE: this does NOT re-measure any runtime. The measurement needs live model
# calls and, for two of the five runtimes, an operator-granted permission flag.
# See README.md for the procedure.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PY="${PYTHON:-python}"

OUT="${1:-${TMPDIR:-/tmp}/aaw-adherence-fixtures}"

failed=()
fatal=()

echo "=================================================================="
echo "adherence: build_fixtures.py -> $OUT"
echo "=================================================================="
"$PY" "$HERE/build_fixtures.py" --out "$OUT"
case $? in
  0) ;;
  2) fatal+=("build_fixtures.py") ;;
  *) failed+=("build_fixtures.py") ;;
esac
echo ""

echo "=================================================================="
echo "adherence: check_results.py"
echo "=================================================================="
"$PY" "$HERE/check_results.py"
case $? in
  0) ;;
  2) fatal+=("check_results.py") ;;
  *) failed+=("check_results.py") ;;
esac
echo ""

echo "=================================================================="
if [ "${#fatal[@]}" -gt 0 ]; then
  echo "adherence: COULD NOT RUN - ${fatal[*]}"
  echo "adherence: this is not a pass and not a failure. Fix the environment,"
  echo "adherence: then run again so the check can give a real answer."
  exit 2
fi
if [ "${#failed[@]}" -gt 0 ]; then
  echo "adherence: FAIL - ${failed[*]}"
  exit 1
fi
echo "adherence: PASS - 2/2 checks"
exit 0
