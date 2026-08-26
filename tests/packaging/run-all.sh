#!/usr/bin/env bash
# Run every packaging check and report all of them.
#
# Deliberately does not stop at the first failure. When packaging is broken it is
# usually broken in more than one place, and a runner that hides the second fault
# behind the first turns one debugging session into three.
#
# Exit 0 = every check passed. 1 = at least one failed. 2 = a check could not run,
# which is a different problem and must not be reported as a pass.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CHECKS=(
  "test-fresh-clone.sh"
  "test-manifest-schema.sh"
)

failed=()
fatal=()

for check in "${CHECKS[@]}"; do
  echo "=================================================================="
  echo "packaging: $check"
  echo "=================================================================="
  bash "$HERE/$check"
  code=$?
  case "$code" in
    0) ;;
    2) fatal+=("$check") ;;
    *) failed+=("$check") ;;
  esac
  echo ""
done

echo "=================================================================="
if [ "${#fatal[@]}" -gt 0 ]; then
  echo "packaging: COULD NOT RUN - ${fatal[*]}"
  echo "packaging: this is not a pass and not a failure. Fix the environment,"
  echo "packaging: then run again so the check can give a real answer."
  exit 2
fi
if [ "${#failed[@]}" -gt 0 ]; then
  echo "packaging: FAIL - ${failed[*]}"
  exit 1
fi
echo "packaging: PASS - ${#CHECKS[@]}/${#CHECKS[@]} checks"
exit 0
