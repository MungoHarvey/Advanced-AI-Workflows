#!/usr/bin/env bash
# Check that the non-interactive audit is non-interactive, deterministic, and
# returns an exit code that means something.
#
# Everything runs against temporary projects and a fake user profile. The live
# profile is never read for detection and never written: `--home` exists so that
# this test cannot pass by accident because of what happens to be installed on the
# machine running it.
#
# Exit 0 = every case behaved. 1 = a case failed. 2 = the test could not run.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
AUDIT="$REPO/tools/aaw-audit.py"

PY=""
for candidate in python3 python py; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1 || continue
  PY="$candidate"
  break
done
[ -n "$PY" ] || { echo "audit: FATAL - no Python 3.8+ interpreter found"; exit 2; }
[ -f "$AUDIT" ] || { echo "audit: FATAL - $AUDIT does not exist"; exit 2; }

TMP="$(mktemp -d)" || { echo "audit: FATAL - cannot create a temporary directory"; exit 2; }
trap 'rm -rf "$TMP"' EXIT

pass=0
fail=0

ok()   { pass=$((pass + 1)); echo "  ok    $1"; }
bad()  { fail=$((fail + 1)); echo "  FAIL  $1"; }

mkskill() {  # mkskill <root> <name>
  mkdir -p "$1/.claude/skills/$2"
  printf -- '---\nname: %s\n---\n' "$2" > "$1/.claude/skills/$2/SKILL.md"
}

# --------------------------------------------------------------------------
# the fixtures
# --------------------------------------------------------------------------
PROFILE="$TMP/fake-profile"
mkdir -p "$PROFILE/.claude/skills"
mkskill "$PROFILE" gstack

HEALTHY="$TMP/healthy"
mkdir -p "$HEALTHY"
mkskill "$HEALTHY" phase-plan-creator
mkskill "$HEALTHY" gstack-to-plans

STALE="$TMP/stale-data-only"
mkdir -p "$STALE/.advanced-plans/phases"
printf 'current_phase: 3\n' > "$STALE/.advanced-plans/PLANNING.md"

echo "audit: using $PY, temp root $TMP"
echo ""

# --------------------------------------------------------------------------
# 1. a healthy project exits 0
# --------------------------------------------------------------------------
"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" \
      --write-manifest --now 2026-08-26T15:00:00Z > "$TMP/healthy-1.txt" 2> "$TMP/healthy-1.err"
code=$?
if [ "$code" -eq 0 ]; then
  ok "healthy project exits 0"
else
  bad "healthy project exits 0 (got $code)"
  sed 's/^/        /' "$TMP/healthy-1.txt" | tail -8
fi

# --------------------------------------------------------------------------
# 2. determinism: two runs, byte-identical, in both formats
# --------------------------------------------------------------------------
"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" > "$TMP/det-text-1.txt" 2>/dev/null
"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" > "$TMP/det-text-2.txt" 2>/dev/null
if cmp -s "$TMP/det-text-1.txt" "$TMP/det-text-2.txt"; then
  ok "two text runs are byte-identical"
else
  bad "two text runs are byte-identical"
  diff "$TMP/det-text-1.txt" "$TMP/det-text-2.txt" | head -6 | sed 's/^/        /'
fi

"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" --format json > "$TMP/det-json-1.txt" 2>/dev/null
"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" --format json > "$TMP/det-json-2.txt" 2>/dev/null
if cmp -s "$TMP/det-json-1.txt" "$TMP/det-json-2.txt"; then
  ok "two json runs are byte-identical"
else
  bad "two json runs are byte-identical"
  diff "$TMP/det-json-1.txt" "$TMP/det-json-2.txt" | head -6 | sed 's/^/        /'
fi

# The output must carry no timestamp at all. A field that changes per run would
# make the two comparisons above pass only because they ran in the same second.
if grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}' "$TMP/det-json-1.txt"; then
  bad "audit output carries no timestamp"
  grep -nE '[0-9]{4}-[0-9]{2}-[0-9]{2}T' "$TMP/det-json-1.txt" | head -3 | sed 's/^/        /'
else
  ok "audit output carries no timestamp"
fi

# --------------------------------------------------------------------------
# 3. the manifest it wrote must satisfy the shipped schema
# --------------------------------------------------------------------------
if [ -f "$HEALTHY/.aaw/installed.json" ]; then
  "$PY" "$HERE/validate-manifest.py" "$HEALTHY/.aaw/installed.json" > "$TMP/val.txt" 2>&1
  if [ $? -eq 0 ]; then
    ok "the manifest the audit wrote validates against the schema"
  else
    bad "the manifest the audit wrote validates against the schema"
    sed 's/^/        /' "$TMP/val.txt" | head -6
  fi
else
  bad "--write-manifest produced .aaw/installed.json"
fi

# --------------------------------------------------------------------------
# 4. an unhealthy project exits 1, and says which things are wrong
# --------------------------------------------------------------------------
"$PY" "$AUDIT" --project "$STALE" --home "$PROFILE" > "$TMP/stale.txt" 2>/dev/null
code=$?
if [ "$code" -eq 1 ]; then
  ok "stale-data project exits 1"
else
  bad "stale-data project exits 1 (got $code)"
fi

for finding in required-component-missing data-without-owner manifest-absent; do
  if grep -q "\[$finding\]" "$TMP/stale.txt"; then
    ok "reports [$finding]"
  else
    bad "reports [$finding]"
  fi
done

# ACC-02 restated as an assertion on the audit's own output: the data directory is
# reported present, and the component that owns it is still MISSING.
if grep -qE '^  advanced-planning  MISSING' "$TMP/stale.txt" \
   && grep -qE '^  present   advanced-planning' "$TMP/stale.txt"; then
  ok "ACC-02: data present and component MISSING, reported together"
else
  bad "ACC-02: data present and component MISSING, reported together"
  sed 's/^/        /' "$TMP/stale.txt" | head -14
fi

# --------------------------------------------------------------------------
# 5. a manifest the filesystem contradicts is a finding, not a pass
# --------------------------------------------------------------------------
LIAR="$TMP/lying-manifest"
mkdir -p "$LIAR"
mkskill "$LIAR" phase-plan-creator
"$PY" "$AUDIT" --project "$LIAR" --home "$PROFILE" \
      --write-manifest --now 2026-08-26T15:00:00Z >/dev/null 2>&1
rm -rf "$LIAR/.claude/skills/phase-plan-creator"
"$PY" "$AUDIT" --project "$LIAR" --home "$PROFILE" > "$TMP/liar.txt" 2>/dev/null
code=$?
if [ "$code" -eq 1 ] && grep -q "\[manifest-stale\]" "$TMP/liar.txt"; then
  ok "a manifest whose sentinel has gone is reported stale"
else
  bad "a manifest whose sentinel has gone is reported stale (exit $code)"
  sed 's/^/        /' "$TMP/liar.txt" | tail -8
fi

# --------------------------------------------------------------------------
# 6. cannot-run is exit 2, and is not confused with either of the others
# --------------------------------------------------------------------------
"$PY" "$AUDIT" --project "$TMP/does-not-exist" --home "$PROFILE" >/dev/null 2>&1
[ $? -eq 2 ] && ok "a missing project exits 2" || bad "a missing project exits 2"

"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" --write-manifest >/dev/null 2>&1
[ $? -eq 2 ] && ok "--write-manifest without --now exits 2" \
             || bad "--write-manifest without --now exits 2"

"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" \
      --write-manifest --now "yesterday" >/dev/null 2>&1
[ $? -eq 2 ] && ok "--now with a non-ISO value exits 2" \
             || bad "--now with a non-ISO value exits 2"

# --------------------------------------------------------------------------
# 7. it is genuinely non-interactive: no stdin, and it must not hang
# --------------------------------------------------------------------------
"$PY" "$AUDIT" --project "$HEALTHY" --home "$PROFILE" < /dev/null > /dev/null 2>&1
[ $? -eq 0 ] && ok "runs to completion with stdin closed" \
             || bad "runs to completion with stdin closed"

echo ""
if [ "$fail" -eq 0 ]; then
  echo "audit: PASS - $pass/$pass checks"
  exit 0
fi
echo "audit: FAIL - $fail of $((pass + fail)) checks"
exit 1
