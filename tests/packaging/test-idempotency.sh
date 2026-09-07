#!/usr/bin/env bash
# Install, refresh, uninstall, reinstall - and prove each one is safe to repeat.
#
# ACC-16 is the headline: a refresh run twice must be a no-op on the second run.
# The rest of the file is there because a no-op is easy to fake. An install that
# does nothing is idempotent too. So every stage also asserts that the artefacts
# it was supposed to create exist, that the user's own writing is untouched, and
# that uninstall returns the project to exactly the bytes it started with.
#
# Nothing here reads or writes the live profile. The fake profile is built inside
# the temp directory and passed to the audit with --home, and the project is a
# temp directory too. If this test ever touches ~/.claude it is a bug in the test.
#
# Exit 0 = every case behaved. 1 = a case failed. 2 = the test could not run.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
OPS="$HERE/project_ops.py"
AUDIT="$REPO/tools/aaw-audit.py"
NOW="2026-08-26T16:00:00Z"

PY=""
for candidate in python3 python py; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1 || continue
  PY="$candidate"
  break
done
[ -n "$PY" ] || { echo "idempotency: FATAL - no Python 3.8+ interpreter found"; exit 2; }
[ -f "$OPS" ]   || { echo "idempotency: FATAL - $OPS does not exist"; exit 2; }
[ -f "$AUDIT" ] || { echo "idempotency: FATAL - $AUDIT does not exist"; exit 2; }

TMP="$(mktemp -d)" || { echo "idempotency: FATAL - cannot create a temporary directory"; exit 2; }
trap 'rm -rf "$TMP"' EXIT

pass=0
fail=0
ok()  { pass=$((pass + 1)); echo "  ok    $1"; }
bad() { fail=$((fail + 1)); echo "  FAIL  $1"; }

mkskill() {  # mkskill <root> <name>
  mkdir -p "$1/.claude/skills/$2"
  printf -- '---\nname: %s\n---\n' "$2" > "$1/.claude/skills/$2/SKILL.md"
}

install()   { "$PY" "$OPS" install   --project "$P" >/dev/null 2>"$TMP/ops.err"; }
uninstall() { "$PY" "$OPS" uninstall --project "$P" >/dev/null 2>"$TMP/ops.err"; }
snap()      { "$PY" "$OPS" fingerprint --project "$P" > "$1" 2>/dev/null; }
audit()     { "$PY" "$AUDIT" --project "$P" --home "$PROFILE" "$@"; }
manifest()  { audit --write-manifest --now "$NOW" > "$1" 2>"$TMP/audit.err"; }

# --------------------------------------------------------------------------
# the fixture: a project with a real user in it
# --------------------------------------------------------------------------
PROFILE="$TMP/fake-profile"
mkskill "$PROFILE" gstack

P="$TMP/project"
mkdir -p "$P/docs" "$P/.advanced-plans/phases" "$P/.claude"
mkskill "$P" phase-plan-creator          # advanced-planning, already installed

cat > "$P/CLAUDE.md" <<'EOF'
# Acme service

House rules that predate any of this and must survive every stage:

- Never commit to main.
- Run `make check` before pushing.
EOF

cat > "$P/docs/notes.md" <<'EOF'
Notes the user wrote. Nothing in this stack has any business editing them.
EOF

printf 'current_phase: 2\n' > "$P/.advanced-plans/PLANNING.md"

# A settings.json that already has the user's own permission and - the awkward
# case - their own PostToolUse hook on the same "Write" matcher we need.
cat > "$P/.claude/settings.json" <<'EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo user-owned-hook"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(git status)"
    ]
  }
}
EOF

echo "idempotency: using $PY"
echo "idempotency: project $P"
echo "idempotency: profile $PROFILE (the live profile is never read)"
echo ""

snap "$TMP/fp-before.txt"
cp "$P/.claude/settings.json" "$TMP/settings-before.json"
"$PY" "$OPS" fingerprint --project "$PROFILE" > "$TMP/fp-profile-before.txt" 2>/dev/null

echo "--- before -------------------------------------------------------"
sed 's/^/  /' "$TMP/fp-before.txt"
echo ""

# --------------------------------------------------------------------------
# 1. install
# --------------------------------------------------------------------------
echo "--- stage 1: install ---------------------------------------------"
install
manifest "$TMP/audit-1.txt"
code=$?

[ "$code" -eq 0 ] && ok "audit after install exits 0" \
                  || { bad "audit after install exits 0 (got $code)"; sed 's/^/        /' "$TMP/audit-1.txt" | tail -8; }

begins=$(grep -c 'aaw-routing:begin' "$P/CLAUDE.md")
ends=$(grep -c 'aaw-routing:end' "$P/CLAUDE.md")
[ "$begins" = "1" ] && [ "$ends" = "1" ] && ok "CLAUDE.md has exactly one fenced block" \
  || bad "CLAUDE.md has exactly one fenced block (begin=$begins end=$ends)"

grep -q 'Never commit to main' "$P/CLAUDE.md" \
  && ok "install preserved the user's CLAUDE.md content" \
  || bad "install preserved the user's CLAUDE.md content"

[ -f "$P/.claude/skills/gstack-to-plans/SKILL.md" ] \
  && ok "glue skill installed" || bad "glue skill installed"

[ -f "$P/.aaw/installed.json" ] \
  && ok "manifest written" || bad "manifest written"

"$PY" - "$P/.claude/settings.json" <<'PYEOF' > "$TMP/settings-check-1.txt" 2>&1
import json, sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))
allow = doc["permissions"]["allow"]
post = doc["hooks"]["PostToolUse"]
writers = [m for m in post if m.get("matcher") == "Write"]
cmds = [h.get("command", "") for m in writers for h in m.get("hooks", [])]
problems = []
if "Bash(git status)" not in allow:
    problems.append("the user's own permission was dropped")
for entry in ("Write(.advanced-plans/**)", "Edit(.advanced-plans/**)",
              "MultiEdit(.advanced-plans/**)", "Read(.advanced-plans/**)"):
    if allow.count(entry) != 1:
        problems.append("%s appears %d times" % (entry, allow.count(entry)))
if len(writers) != 1:
    problems.append("expected one Write matcher, found %d" % len(writers))
if not any("user-owned-hook" in c for c in cmds):
    problems.append("the user's own Write hook was dropped")
if sum("aaw-hook" in c for c in cmds) != 1:
    problems.append("expected exactly one aaw-hook command, found %d"
                    % sum("aaw-hook" in c for c in cmds))
if any("_comment" in m for m in writers):
    problems.append("the reference file's _comment was installed into settings.json")
print("\n".join(problems) if problems else "clean")
PYEOF
if [ "$(cat "$TMP/settings-check-1.txt")" = "clean" ]; then
  ok "settings.json merged: user entries kept, ours added once, one Write matcher"
else
  bad "settings.json merged: user entries kept, ours added once, one Write matcher"
  sed 's/^/        /' "$TMP/settings-check-1.txt"
fi

snap "$TMP/fp-install-1.txt"
echo ""

# --------------------------------------------------------------------------
# 2. refresh: run the whole thing again and change nothing - ACC-16
# --------------------------------------------------------------------------
echo "--- stage 2: refresh (the same run, a second time) ----------------"
install
manifest "$TMP/audit-2.txt"
code=$?
snap "$TMP/fp-install-2.txt"

[ "$code" -eq 0 ] && ok "audit after refresh exits 0" \
                  || bad "audit after refresh exits 0 (got $code)"

if cmp -s "$TMP/fp-install-1.txt" "$TMP/fp-install-2.txt"; then
  ok "ACC-16: the second run left every file byte-identical"
else
  bad "ACC-16: the second run left every file byte-identical"
  diff "$TMP/fp-install-1.txt" "$TMP/fp-install-2.txt" | head -10 | sed 's/^/        /'
fi

if cmp -s "$TMP/audit-1.txt" "$TMP/audit-2.txt"; then
  ok "ACC-16: the second run reported the same state"
else
  bad "ACC-16: the second run reported the same state"
  diff "$TMP/audit-1.txt" "$TMP/audit-2.txt" | head -10 | sed 's/^/        /'
fi

# Run it a third time. Two runs can agree because the first was the broken one.
install
manifest "$TMP/audit-3.txt" >/dev/null
snap "$TMP/fp-install-3.txt"
cmp -s "$TMP/fp-install-2.txt" "$TMP/fp-install-3.txt" \
  && ok "a third run is still a no-op" || bad "a third run is still a no-op"

begins=$(grep -c 'aaw-routing:begin' "$P/CLAUDE.md")
[ "$begins" = "1" ] && ok "three installs produced one routing block, not three" \
  || bad "three installs produced one routing block, not three (found $begins)"
echo ""

# --------------------------------------------------------------------------
# 3. uninstall
# --------------------------------------------------------------------------
echo "--- stage 3: uninstall -------------------------------------------"
uninstall

grep -q 'aaw-routing' "$P/CLAUDE.md" \
  && bad "uninstall removed the fenced block" || ok "uninstall removed the fenced block"

grep -q 'Never commit to main' "$P/CLAUDE.md" \
  && ok "uninstall preserved the user's CLAUDE.md content" \
  || bad "uninstall preserved the user's CLAUDE.md content"

[ -d "$P/.claude/skills/gstack-to-plans" ] \
  && bad "uninstall removed the glue skill" || ok "uninstall removed the glue skill"

[ -e "$P/.aaw" ] \
  && bad "uninstall removed .aaw/ (it was empty)" || ok "uninstall removed .aaw/ (it was empty)"

# The things it must not touch.
[ -f "$P/.advanced-plans/PLANNING.md" ] \
  && ok "uninstall left .advanced-plans/ alone" || bad "uninstall left .advanced-plans/ alone"
[ -f "$P/docs/notes.md" ] \
  && ok "uninstall left the user's other files alone" || bad "uninstall left the user's other files alone"
[ -f "$P/.claude/skills/phase-plan-creator/SKILL.md" ] \
  && ok "uninstall left the advanced-planning install alone" \
  || bad "uninstall left the advanced-planning install alone"

"$PY" - "$TMP/settings-before.json" "$P/.claude/settings.json" <<'PYEOF' > "$TMP/settings-check-2.txt" 2>&1
import json, sys
before = json.load(open(sys.argv[1], encoding="utf-8"))
after = json.load(open(sys.argv[2], encoding="utf-8"))
print("same" if before == after else
      "differs\nbefore: %s\nafter:  %s"
      % (json.dumps(before, sort_keys=True), json.dumps(after, sort_keys=True)))
PYEOF
if [ "$(head -1 "$TMP/settings-check-2.txt")" = "same" ]; then
  ok "settings.json is back to what the user had"
else
  bad "settings.json is back to what the user had"
  sed 's/^/        /' "$TMP/settings-check-2.txt" | head -6
fi

snap "$TMP/fp-uninstall.txt"
if cmp -s "$TMP/fp-before.txt" "$TMP/fp-uninstall.txt"; then
  ok "the whole project is byte-identical to before the install"
else
  bad "the whole project is byte-identical to before the install"
  diff "$TMP/fp-before.txt" "$TMP/fp-uninstall.txt" | head -10 | sed 's/^/        /'
fi

# Uninstalling twice must not be an error, and must not remove anything else.
uninstall
snap "$TMP/fp-uninstall-2.txt"
cmp -s "$TMP/fp-uninstall.txt" "$TMP/fp-uninstall-2.txt" \
  && ok "a second uninstall is a no-op" || bad "a second uninstall is a no-op"
echo ""

# --------------------------------------------------------------------------
# 4. install after uninstall returns to the same state
# --------------------------------------------------------------------------
echo "--- stage 4: reinstall -------------------------------------------"
install
manifest "$TMP/audit-4.txt"
code=$?
snap "$TMP/fp-reinstall.txt"

[ "$code" -eq 0 ] && ok "audit after reinstall exits 0" \
                  || bad "audit after reinstall exits 0 (got $code)"

if cmp -s "$TMP/fp-install-1.txt" "$TMP/fp-reinstall.txt"; then
  ok "reinstall returns the project to the same bytes as the first install"
else
  bad "reinstall returns the project to the same bytes as the first install"
  diff "$TMP/fp-install-1.txt" "$TMP/fp-reinstall.txt" | head -10 | sed 's/^/        /'
fi

if cmp -s "$TMP/audit-1.txt" "$TMP/audit-4.txt"; then
  ok "reinstall returns to the same manifest state"
else
  bad "reinstall returns to the same manifest state"
  diff "$TMP/audit-1.txt" "$TMP/audit-4.txt" | head -10 | sed 's/^/        /'
fi
echo ""

# --------------------------------------------------------------------------
# 5. half a fence: Step U1 says STOP, and STOP means the whole uninstall
# --------------------------------------------------------------------------
echo "--- stage 5: half a fence ----------------------------------------"
Q="$TMP/hand-edited"
mkdir -p "$Q/.claude"
printf '# Notes\n\n<!-- aaw-routing:begin -->\n## Routing\nsomebody deleted the end marker\n' \
  > "$Q/CLAUDE.md"
"$PY" "$OPS" install --project "$Q" >/dev/null 2>&1
"$PY" "$AUDIT" --project "$Q" --home "$PROFILE" --write-manifest --now "$NOW" >/dev/null 2>&1
# Break the fence again: the install just repaired it.
printf '# Notes\n\n<!-- aaw-routing:begin -->\n## Routing\nsomebody deleted the end marker\n' \
  > "$Q/CLAUDE.md"
cp "$Q/CLAUDE.md" "$TMP/hand-edited-before.md"

"$PY" "$OPS" uninstall --project "$Q" >/dev/null 2>"$TMP/refuse.err"
code=$?
[ "$code" -eq 3 ] && ok "an incomplete fence exits 3 (needs a human)" \
                  || bad "an incomplete fence exits 3 (needs a human), got $code"

cmp -s "$TMP/hand-edited-before.md" "$Q/CLAUDE.md" \
  && ok "and leaves CLAUDE.md byte-identical" \
  || bad "and leaves CLAUDE.md byte-identical"

grep -q 'refused to edit CLAUDE.md' "$TMP/refuse.err" \
  && ok "and says so instead of failing silently" \
  || bad "and says so instead of failing silently"

# Step U1 says do not proceed to the remaining uninstall steps. Prove it did not.
[ -f "$Q/.claude/skills/gstack-to-plans/SKILL.md" ] \
  && ok "U1 STOP: the glue skill was not removed either" \
  || bad "U1 STOP: the glue skill was not removed either"
[ -f "$Q/.aaw/installed.json" ] \
  && ok "U1 STOP: the manifest was not removed either" \
  || bad "U1 STOP: the manifest was not removed either"
grep -q 'advanced-plans' "$Q/.claude/settings.json" \
  && ok "U1 STOP: settings.json was not edited either" \
  || bad "U1 STOP: settings.json was not edited either"
echo ""

# --------------------------------------------------------------------------
# 6. blast radius: the fake profile came through unchanged
# --------------------------------------------------------------------------
echo "--- stage 6: blast radius ----------------------------------------"
"$PY" "$OPS" fingerprint --project "$PROFILE" > "$TMP/fp-profile-after.txt" 2>/dev/null
if cmp -s "$TMP/fp-profile-before.txt" "$TMP/fp-profile-after.txt"; then
  ok "the profile is byte-identical after install, refresh, and uninstall"
else
  bad "the profile is byte-identical after install, refresh, and uninstall"
  diff "$TMP/fp-profile-before.txt" "$TMP/fp-profile-after.txt" | head -10 | sed 's/^/        /'
fi

# Every path the manifest records must be inside the temp tree. A path pointing at
# the real profile or at the controller checkout would mean detection reached
# somewhere this test told it not to go.
"$PY" - "$P/.aaw/installed.json" "$TMP" <<'PYEOF' > "$TMP/paths.txt" 2>&1
import json, os, sys
doc = json.load(open(sys.argv[1], encoding="utf-8"))
root = os.path.realpath(sys.argv[2])
paths = [doc["project_root"]]
for name, entry in sorted(doc.get("components", {}).items()):
    for key in ("install_path", "sentinel"):
        if entry.get(key):
            paths.append(entry[key])
stray = [q for q in paths if not os.path.realpath(q).startswith(root)]
print("contained (%d paths)" % len(paths) if not stray
      else "STRAY\n" + "\n".join(stray))
PYEOF
if head -1 "$TMP/paths.txt" | grep -q '^contained'; then
  ok "$(cat "$TMP/paths.txt" | head -1 | sed 's/^contained/every recorded path is inside the temp tree -/')"
else
  bad "every recorded path is inside the temp tree"
  sed 's/^/        /' "$TMP/paths.txt" | head -6
fi
echo ""

# --------------------------------------------------------------------------
# 7. an existing glue skill is left alone - Step 6 Case B
# --------------------------------------------------------------------------
echo "--- stage 7: an existing glue skill ------------------------------"
G="$TMP/has-glue"
mkdir -p "$G/.claude/skills/gstack-to-plans"
printf -- '---\nname: gstack-to-plans\n---\nmy own edited copy\n' \
  > "$G/.claude/skills/gstack-to-plans/SKILL.md"
printf 'a note the user added next to the skill\n' \
  > "$G/.claude/skills/gstack-to-plans/NOTES.md"
"$PY" "$OPS" install --project "$G" >/dev/null 2>"$TMP/glue.err"

[ -f "$G/.claude/skills/gstack-to-plans/NOTES.md" ] \
  && ok "install did not delete a file the user added beside the glue skill" \
  || bad "install did not delete a file the user added beside the glue skill"

grep -q 'my own edited copy' "$G/.claude/skills/gstack-to-plans/SKILL.md" \
  && ok "install did not overwrite an existing glue SKILL.md" \
  || bad "install did not overwrite an existing glue SKILL.md"

grep -q 'already installed' "$TMP/glue.err" \
  && ok "and said it was already installed" || bad "and said it was already installed"
echo ""

# --------------------------------------------------------------------------
# 8. removing our entries would empty an array - Step U6 says ask first
# --------------------------------------------------------------------------
echo "--- stage 8: uninstall that would empty an array -----------------"
E="$TMP/ours-only"
mkdir -p "$E/.claude"
printf '{}\n' > "$E/.claude/settings.json"
"$PY" "$OPS" install --project "$E" >/dev/null 2>&1
cp "$E/.claude/settings.json" "$TMP/ours-only-before.json"

"$PY" "$OPS" uninstall --project "$E" >/dev/null 2>"$TMP/empty.err"
code=$?
[ "$code" -eq 3 ] && ok "exits 3 rather than writing blindly" \
                  || bad "exits 3 rather than writing blindly, got $code"
cmp -s "$TMP/ours-only-before.json" "$E/.claude/settings.json" \
  && ok "and leaves settings.json byte-identical" \
  || bad "and leaves settings.json byte-identical"
grep -q 'permissions.allow and hooks.PostToolUse' "$TMP/empty.err" \
  && ok "and names both arrays it would have emptied" \
  || { bad "and names both arrays it would have emptied"; sed 's/^/        /' "$TMP/empty.err"; }
[ -d "$E/.claude/skills/gstack-to-plans" ] \
  && ok "and stopped before removing the glue skill" \
  || bad "and stopped before removing the glue skill"
echo ""

# --------------------------------------------------------------------------
# 9. nothing of ours to remove - do not refuse, and do not reformat
# --------------------------------------------------------------------------
# Two findings from the second review pass, in one fixture, because they meet here:
# a settings.json that has never had AAW in it, formatted the way its owner formats
# it, carrying somebody else's PostToolUse entry on the same "Write" matcher we use.
# The Step U6 guard used to refuse this - it asked "would the array be empty after
# removal" and got yes, because the survivors calculation dropped a matcher that held
# none of our hooks. And the no-rewrite check compared serialised bytes, so a
# four-space file was "changed" and came back two-space.
echo "--- stage 9: nothing of ours to remove ---------------------------"
N="$TMP/not-ours"
mkdir -p "$N/.claude"
cat > "$N/.claude/settings.json" <<'JSON'
{
    "permissions": {
        "allow": [
            "Bash(git status)"
        ]
    },
    "hooks": {
        "PostToolUse": [
            {
                "matcher": "Write",
                "hooks": []
            }
        ]
    }
}
JSON
cp "$N/.claude/settings.json" "$TMP/not-ours-before.json"

"$PY" "$OPS" uninstall --project "$N" >/dev/null 2>"$TMP/notours.err"
code=$?
[ "$code" -eq 0 ] && ok "an uninstall with nothing of ours to remove does not refuse" \
  || { bad "an uninstall with nothing of ours to remove does not refuse, got $code"
       sed 's/^/        /' "$TMP/notours.err" | head -3; }

cmp -s "$TMP/not-ours-before.json" "$N/.claude/settings.json" \
  && ok "and leaves a four-space-indented settings.json byte-identical" \
  || { bad "and leaves a four-space-indented settings.json byte-identical"
       diff -u "$TMP/not-ours-before.json" "$N/.claude/settings.json" | head -14; }

grep -q '"matcher"' "$N/.claude/settings.json" \
  && ok "and does not delete somebody else's empty Write matcher" \
  || bad "and does not delete somebody else's empty Write matcher"

# Step U1, "neither marker": there is no CLAUDE.md here at all, and that is not an
# error - it is a project the routing block was never installed into. The uninstall
# must carry on rather than stop, or the other artefacts become unremovable.
[ ! -f "$N/CLAUDE.md" ] \
  && ok "and a project with no CLAUDE.md is not treated as a hand-edited one" \
  || bad "and a project with no CLAUDE.md is not treated as a hand-edited one"
echo ""

# --------------------------------------------------------------------------
# 10. AGENTS.md is an instruction file too
#
# The design spec has `aaw init` merging the block into "existing AGENTS.md and/or
# CLAUDE.md". Which of the two a harness reads is the harness's business; ours is
# to put the block where it will be read and nowhere else. Two ways to get this
# wrong: install into only CLAUDE.md and be invisible to an AGENTS.md harness, or
# create both files and leave a file in the project the user never had.
# --------------------------------------------------------------------------
echo "--- stage 10: AGENTS.md ------------------------------------------"

# 10a. AGENTS.md only.
A="$TMP/agents-only"
mkdir -p "$A"
printf '# House rules\n\nUse tabs. Never rewrite git history.\n' > "$A/AGENTS.md"
cp "$A/AGENTS.md" "$TMP/agents-only-before.md"
"$PY" "$OPS" install --project "$A" >/dev/null 2>&1

[ "$(grep -c 'aaw-routing:begin' "$A/AGENTS.md")" = "1" ] \
  && ok "AGENTS.md-only project: the block lands in AGENTS.md" \
  || bad "AGENTS.md-only project: the block lands in AGENTS.md"

[ ! -f "$A/CLAUDE.md" ] \
  && ok "and no CLAUDE.md is invented alongside it" \
  || bad "and no CLAUDE.md is invented alongside it"

head -3 "$A/AGENTS.md" > "$TMP/agents-only-head.md"
cmp -s "$TMP/agents-only-before.md" "$TMP/agents-only-head.md" \
  && ok "and the user's own AGENTS.md content survives verbatim" \
  || bad "and the user's own AGENTS.md content survives verbatim"

"$PY" "$OPS" fingerprint --project "$A" > "$TMP/fp-agents-1.txt" 2>/dev/null
"$PY" "$OPS" install --project "$A" >/dev/null 2>&1
"$PY" "$OPS" fingerprint --project "$A" > "$TMP/fp-agents-2.txt" 2>/dev/null
cmp -s "$TMP/fp-agents-1.txt" "$TMP/fp-agents-2.txt" \
  && ok "and a second install is byte-identical" \
  || bad "and a second install is byte-identical"

"$PY" "$OPS" uninstall --project "$A" >/dev/null 2>&1
cmp -s "$TMP/agents-only-before.md" "$A/AGENTS.md" \
  && ok "and uninstall returns AGENTS.md to the bytes it started with" \
  || bad "and uninstall returns AGENTS.md to the bytes it started with"

# 10b. Both files present.
B="$TMP/both-files"
mkdir -p "$B"
printf '# Claude notes\n\nProject uses pnpm.\n' > "$B/CLAUDE.md"
printf '# Agent notes\n\nProject uses pnpm.\n' > "$B/AGENTS.md"
"$PY" "$OPS" install --project "$B" >/dev/null 2>&1

if [ "$(grep -c 'aaw-routing:begin' "$B/CLAUDE.md")" = "1" ] \
&& [ "$(grep -c 'aaw-routing:begin' "$B/AGENTS.md")" = "1" ]; then
  ok "both-file project: each file gets the block exactly once"
else
  bad "both-file project: each file gets the block exactly once"
fi

"$PY" "$OPS" fingerprint --project "$B" > "$TMP/fp-both-1.txt" 2>/dev/null
"$PY" "$OPS" install --project "$B" >/dev/null 2>&1
"$PY" "$OPS" fingerprint --project "$B" > "$TMP/fp-both-2.txt" 2>/dev/null
cmp -s "$TMP/fp-both-1.txt" "$TMP/fp-both-2.txt" \
  && ok "and installing again changes neither file" \
  || bad "and installing again changes neither file"

# The two blocks must be the same text. One source file, so this is really a check
# that nothing rewrote the block on its way into one of them.
"$PY" - "$B" <<'EOF' > "$TMP/blocks-equal.txt" 2>&1
import io, os, sys
root = sys.argv[1]
def block(name):
    with io.open(os.path.join(root, name), encoding="utf-8", newline="") as fh:
        t = fh.read().replace("\r\n", "\n")
    i = t.index("<!-- aaw-routing:begin -->")
    j = t.index("<!-- aaw-routing:end -->")
    return t[i:j]
print("same" if block("CLAUDE.md") == block("AGENTS.md") else "different")
EOF
grep -qx 'same' "$TMP/blocks-equal.txt" \
  && ok "and the two files carry byte-identical block text" \
  || bad "and the two files carry byte-identical block text"

"$PY" "$OPS" uninstall --project "$B" >/dev/null 2>&1
if ! grep -q 'aaw-routing' "$B/CLAUDE.md" && ! grep -q 'aaw-routing' "$B/AGENTS.md"; then
  ok "and uninstall clears the block from both"
else
  bad "and uninstall clears the block from both"
fi

# 10c. Half a fence in AGENTS.md must stop CLAUDE.md being touched.
#
# This is the ordering bug worth a test of its own: check every file before
# writing any file. Uninstall CLAUDE.md first and then refuse on AGENTS.md and
# the project is left half-uninstalled, with an error message claiming nothing
# was changed.
H="$TMP/half-fence-agents"
mkdir -p "$H"
printf '# Claude notes\n\nkeep me\n' > "$H/CLAUDE.md"
printf '# Agent notes\n\nkeep me\n' > "$H/AGENTS.md"
"$PY" "$OPS" install --project "$H" >/dev/null 2>&1
"$PY" - "$H" <<'EOF'
import io, os, sys
p = os.path.join(sys.argv[1], "AGENTS.md")
with io.open(p, encoding="utf-8", newline="") as fh:
    t = fh.read()
with io.open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(t.replace("<!-- aaw-routing:end -->", ""))
EOF
cp "$H/CLAUDE.md" "$TMP/half-fence-claude-before.md"

"$PY" "$OPS" uninstall --project "$H" >/dev/null 2>"$TMP/refuse-agents.err"
code=$?
[ "$code" -eq 3 ] && ok "a half fence in AGENTS.md exits 3" \
                  || bad "a half fence in AGENTS.md exits 3, got $code"

grep -q 'refused to edit AGENTS.md' "$TMP/refuse-agents.err" \
  && ok "and names AGENTS.md as the file it refused" \
  || bad "and names AGENTS.md as the file it refused"

cmp -s "$TMP/half-fence-claude-before.md" "$H/CLAUDE.md" \
  && ok "and CLAUDE.md is byte-identical - checked before anything was written" \
  || bad "and CLAUDE.md is byte-identical - checked before anything was written"

# 10d. Neither file: CLAUDE.md is created, AGENTS.md is not.
E="$TMP/no-instruction-file"
mkdir -p "$E"
"$PY" "$OPS" install --project "$E" >/dev/null 2>&1
if [ -f "$E/CLAUDE.md" ] && [ ! -f "$E/AGENTS.md" ]; then
  ok "a project with neither file gets CLAUDE.md only"
else
  bad "a project with neither file gets CLAUDE.md only"
fi
echo ""

echo "--- after install ------------------------------------------------"
sed 's/^/  /' "$TMP/fp-install-1.txt"
echo ""

if [ "$fail" -eq 0 ]; then
  echo "idempotency: PASS - $pass/$pass checks"
  exit 0
fi
echo "idempotency: FAIL - $fail of $((pass + fail)) checks"
exit 1
