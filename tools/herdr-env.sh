#!/usr/bin/env bash
# Run Herdr with HOME pinned to the real Windows profile.
#
# Git Bash on this machine exports HOME=/m/ (the AD "Home directory" attribute, mapped to
# M:\). Herdr honours HOME when it is set, so from Git Bash it probes M:\.claude\,
# M:\.codex\, M:\.config\opencode\ and M:\.cursor\ - none of which exist - and reports every
# integration as "not installed". They are installed and current under C:\Users\mharvey2.
#
# Windows PowerShell leaves HOME unset, so herdr falls back to USERPROFILE and has always
# resolved correctly there. The bug is shell-specific, not machine-wide. Use
# tools/herdr-env.ps1 on the PowerShell side.
#
# USERPROFILE is the correct source of truth. Never resolve a global path through HOME, ~,
# or HOMEDRIVE on this machine.
#
# Usage:
#   tools/herdr-env.sh integration status
#   tools/herdr-env.sh --assert
#
# Background: .advanced-plans/evidence/2026-08-26-baseline-audit.md section 7.

set -euo pipefail

if [ -z "${USERPROFILE:-}" ]; then
    echo "USERPROFILE is not set. Cannot resolve the real profile; refusing to guess." >&2
    exit 2
fi

# Native Windows form for the tools, POSIX form for this shell.
WIN_PROFILE="$USERPROFILE"
POSIX_PROFILE="$(cygpath -u "$USERPROFILE")"

export HOME="$POSIX_PROFILE"
export HOMEDRIVE="${WIN_PROFILE:0:2}"
export HOMEPATH="${WIN_PROFILE:2}"

# The AAW v0.2 target runtime set. Herdr supports many more; "not installed" is the correct
# answer for those and must not fail the assertion.
TARGETS="claude codex opencode cursor"

if [ "${1:-}" = "--assert" ]; then
    echo "profile root : $WIN_PROFILE"
    echo "target set   : $TARGETS"
    echo

    status="$(herdr integration status 2>&1)"
    failures=""

    for name in $TARGETS; do
        line="$(printf '%s\n' "$status" | grep -E "^[[:space:]]*${name}[[:space:]]*:" | head -1 || true)"

        if [ -z "$line" ]; then
            failures="${failures}
  - ${name} : herdr reported no status line at all"
            continue
        fi

        echo "  $line"

        case "$line" in
            *"not installed"*)
                failures="${failures}
  - ${name} : reports \"not installed\"" ;;
        esac

        reported="$(printf '%s\n' "$line" | sed -n 's/.*(\([A-Za-z]:[^)]*\)).*/\1/p')"
        if [ -n "$reported" ]; then
            case "$reported" in
                "$WIN_PROFILE"*) : ;;
                *) failures="${failures}
  - ${name} : path resolves outside the profile - ${reported}" ;;
            esac
        fi
    done
    echo

    if [ -n "$failures" ]; then
        echo "ASSERTION FAILED"
        printf '%s\n' "$failures"
        echo
        echo "The environment has drifted. Run Herdr through this launcher, and see"
        echo "baseline audit section 7 for why HOME cannot be trusted on this machine."
        exit 1
    fi

    echo "ASSERTION PASSED - every target runtime resolves under the real profile."
    exit 0
fi

if [ "$#" -eq 0 ]; then
    echo "Usage: tools/herdr-env.sh <herdr arguments>"
    echo "       tools/herdr-env.sh --assert"
    exit 2
fi

exec herdr "$@"
