"""The gstack-to-plans PostToolUse hook fires on the paths this platform produces.

The hook is a one-line node script embedded in `settings-snippet.json`, and the
thing it decides is whether a written file sits under the user's
`.gstack/projects/` directory. That makes it exactly the kind of check this
programme keeps finding broken: **its subject is a string it constructed**, not a
fact read off the machine.

It was broken. Until 2026-09-01 the shipped command compared the written path
against `os.homedir() + '/.gstack/projects/'`. `os.homedir()` returns a *native*
path, so on Windows that prefix is `C:\\Users\\name/.gstack/projects/` - backslashes
up to the home directory, forward slashes after it. No real path takes that shape.
Measured on the machine that found it: a native Windows path was silent, a fully
forward-slash path was silent, and the only input that fired was the mixed form
nothing produces. The hook had been inert on Windows for its whole life.

Nothing caught it, and the reason is worth stating plainly. The snippet's own note
asserted the hook worked on Windows because `os.homedir()` is cross-platform -
true, and beside the point, since the bug was in the separators, not the home. The
only test that existed was REG-7, which checks that the hook does *not* fire on
unrelated writes. **A hook that never fires passes that test perfectly.** A check
that cannot fail is not a check, and a negative-only test of a trigger is one.

So these cases are positive first. Three path shapes that MUST produce output, three
that MUST NOT, and then a mutation that puts the old concatenation back and asserts
the native-path case goes silent - which is the only thing that proves these cases
would have caught the bug that was actually shipped.

The command is read out of `settings-snippet.json` rather than copied here. The
shipped artefact is the subject; a copy in the test would let the two drift and the
test would go on passing against a string nobody installs.


One more trap, found while writing this file and worth more than the case it broke.
The first version ran the hook with `subprocess.run(["bash", ...])`. On Windows that
does not mean what it says: `shutil.which("bash")` finds Git Bash, but CreateProcess
resolves the bare name to `C:\\Windows\\System32\\bash.exe`, the WSL launcher - and
which one you get depends on which Python started the process. Under the Store
`python3` the wrapper happens to pick, `bash` was Git Bash and the cases fired. Under
conda `python` it was WSL, which does not propagate the environment at all, so
`CLAUDE_TOOL_INPUT_PATH` arrived empty and **every** case went silent.

That is the same failure again, one level up: a silent hook reads as "did not fire",
so the three negative cases would have passed, the positive ones would have failed
loudly this time - but a test with only negative cases would have gone green while
proving nothing. So the shell is no longer looked up by name. It is chosen, probed
with a sentinel that must survive the round trip, and the node inside it must report
the same platform as the test process. If no shell on this machine can deliver an
environment variable to the hook, that is a FATAL and not a pass.

Exit 0 = every case behaved. 1 = a case failed. 2 = the test could not run.
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SNIPPET = os.path.join(REPO, ".claude", "skills", "setup-with-claude",
                       "references", "settings-snippet.json")

MARKER = "[aaw-hook]"

passed = 0
failed = 0


def ok(what):
    global passed
    passed += 1
    print("  ok    %s" % what)


def bad(what, detail):
    global failed
    failed += 1
    print("  FAIL  %s" % what)
    for line in str(detail).splitlines():
        print("        %s" % line)


def fatal(why):
    print("hook-path: FATAL - %s" % why)
    raise SystemExit(2)


def _probe(shell, script, env=None):
    try:
        proc = subprocess.run([shell, "-c", script], env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None
    return proc.stdout.decode("utf-8", "replace").strip()


def pick_shell():
    """A shell that can actually hand the hook its input, proven rather than assumed.

    Bare "bash" is not usable here: on Windows the name resolves through
    CreateProcess to the WSL launcher in System32 regardless of what is on PATH,
    and WSL propagates no environment across the boundary. A hook run there is
    silent for a reason that has nothing to do with the hook.
    """
    seen = []
    candidates = []
    which = shutil.which("bash")
    if which:
        candidates.append(which)
    for extra in (
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     "Git", "bin", "bash.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Git",
                     "bin", "bash.exe"),
        "bash",
    ):
        if extra and extra not in candidates:
            candidates.append(extra)

    sentinel = "aaw-shell-probe-42"
    env = dict(os.environ)
    env["CLAUDE_TOOL_INPUT_PATH"] = sentinel

    for shell in candidates:
        got = _probe(shell, 'printf "%s" "$CLAUDE_TOOL_INPUT_PATH"', env)
        if got is None:
            seen.append("%s: could not be started" % shell)
            continue
        if got != sentinel:
            seen.append("%s: env did not survive (got %r)" % (shell, got))
            continue
        plat = _probe(shell, "node -e \"process.stdout.write(process.platform)\"", env)
        if plat != sys.platform:
            seen.append("%s: node there reports platform %r, this process is %r"
                        % (shell, plat, sys.platform))
            continue
        return shell, seen
    return None, seen


SHELL = None


def run(command, written_path):
    """Run the hook command the way a harness would: through a shell, with the
    written path in the environment, and nothing else told to it."""
    env = dict(os.environ)
    env["CLAUDE_TOOL_INPUT_PATH"] = written_path
    proc = subprocess.run([SHELL, "-c", command], env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "replace")


def fires(command, written_path):
    code, out = run(command, written_path)
    if code != 0:
        # The hook must never fail a tool call. That is a defect in its own right,
        # so report it here rather than letting it read as "did not fire".
        bad("hook exited %d on %r" % (code, written_path),
            "A PostToolUse hook that exits non-zero is a hook that breaks writes.")
    return MARKER in out


def main():
    global SHELL
    if not os.path.isfile(SNIPPET):
        fatal("%s does not exist" % SNIPPET)

    SHELL, rejected = pick_shell()
    if SHELL is None:
        fatal("no shell on this machine can run the hook with its input:\n"
              + "\n".join("    " + line for line in rejected)
              + "\n    Without one, every case would go silent and the negative "
                "cases would pass for the wrong reason.")
    if rejected:
        print("hook-path: rejected shells")
        for line in rejected:
            print("    %s" % line)

    with open(SNIPPET, encoding="utf-8") as fh:
        snippet = json.load(fh)
    try:
        entries = snippet["hooks"]["PostToolUse"]
        entry = [e for e in entries if e.get("matcher") == "Write"][0]
        command = entry["hooks"][0]["command"]
    except (KeyError, IndexError, TypeError) as exc:
        fatal("settings-snippet.json has no PostToolUse Write hook to test (%s)" % exc)

    if MARKER not in command:
        fatal("the hook command does not mention %s, so this test cannot tell "
              "firing from silence" % MARKER)

    # The home directory comes from node inside the CHOSEN shell, so it is the
    # same node the hook will use. Asking the outer Python, or a different node,
    # is how a test ends up describing a machine the hook never runs on.
    home = _probe(SHELL, "node -e \"process.stdout.write(require('os').homedir())\"")
    if not home:
        fatal("node could not report a home directory")

    projects = os.path.join(home, ".gstack", "projects", "some-project")
    design = "some-project-design-20260901120000.md"

    native = os.path.join(projects, design)
    posix = native.replace("\\", "/")
    # The one shape the broken version accepted: native home, forward slashes after.
    mixed = home + "/.gstack/projects/some-project/" + design

    print("hook-path: the shipped PostToolUse Write hook")
    print("  shell    %s" % SHELL)
    print("  home     %s" % home)
    print("  native   %s" % native)

    # ------------------------------------------------------------------
    # 1-4. shapes that MUST fire
    # ------------------------------------------------------------------
    # Which of these a harness actually passes is not something this test can
    # know, and that is the point: the hook must not depend on guessing right.
    for label, path in (("native separators", native),
                        ("forward slashes", posix),
                        ("mixed separators", mixed)):
        if fires(command, path):
            ok("fires on a design doc written with %s" % label)
        else:
            bad("fires on a design doc written with %s" % label,
                "Silent on %r.\nThis is the shipped bug: the hook is inert for "
                "this path shape." % path)

    # Case differs on Windows only; on POSIX this is a genuinely different file
    # and silence is correct, so the assertion follows the platform.
    upper = os.path.join(projects, design).replace("some-project",
                                                   "SOME-PROJECT", 1)
    if sys.platform == "win32":
        if fires(command, upper):
            ok("fires when the path differs only by case (Windows is case-insensitive)")
        else:
            bad("fires when the path differs only by case",
                "Silent on %r. On Windows that is the same directory." % upper)

    # ------------------------------------------------------------------
    # 5-8. shapes that MUST stay silent
    # ------------------------------------------------------------------
    elsewhere = os.path.join(home, "Coding", "some-repo", "notes-design-20260901.md")
    if not fires(command, elsewhere):
        ok("silent on a design-shaped filename outside .gstack/projects/")
    else:
        bad("silent on a design-shaped filename outside .gstack/projects/",
            "Fired on %r. The hook must not comment on ordinary writes." % elsewhere)

    wrong_name = os.path.join(projects, "notes.md")
    if not fires(command, wrong_name):
        ok("silent on a non-design file inside .gstack/projects/")
    else:
        bad("silent on a non-design file inside .gstack/projects/",
            "Fired on %r." % wrong_name)

    if not fires(command, ""):
        ok("silent when the harness passes no path at all")
    else:
        bad("silent when the harness passes no path at all",
            "Fired on an empty CLAUDE_TOOL_INPUT_PATH. An empty path resolves to "
            "the working directory, so this is a real way to fire on nothing.")

    # A near miss: the sibling directory whose name merely starts the same way.
    # A prefix comparison that forgets its trailing separator accepts this.
    sibling = os.path.join(home, ".gstack", "projects-archive", design)
    if not fires(command, sibling):
        ok("silent on .gstack/projects-archive/, which only shares a prefix")
    else:
        bad("silent on .gstack/projects-archive/",
            "Fired on %r. The prefix comparison is missing its separator." % sibling)

    # ------------------------------------------------------------------
    # 9. the mutation: put the shipped bug back and watch a case break
    # ------------------------------------------------------------------
    # Everything above passes against the fixed hook. That alone does not show the
    # cases would have caught the bug - only re-introducing it does.
    norm = ("const norm=s=>{const r=path.resolve(s).split(path.sep).join('/');"
            "return process.platform==='win32'?r.toLowerCase():r;};")
    if command.count(norm) != 1:
        fatal("expected exactly one normalisation helper in the hook command, "
              "found %d. The mutation cannot be applied, so this test cannot "
              "prove anything." % command.count(norm))
    broken = command.replace(norm, "const norm=s=>s;")
    broken = broken.replace(
        "const prefix=norm(path.join(os.homedir(),'.gstack','projects'))+'/';",
        "const prefix=os.homedir()+'/.gstack/projects/';")
    if broken == command:
        fatal("the mutation did not change the hook command; a mutation that does "
              "not apply is not a test")

    mutant_fired = fires(broken, native)
    if sys.platform == "win32":
        if not mutant_fired:
            ok("mutation: the old concatenation goes silent on a native path")
        else:
            bad("mutation: the old concatenation goes silent on a native path",
                "The mutant still fired, so the cases above are not testing "
                "separator normalisation and would not have caught the shipped bug.")
    else:
        # On POSIX the separators already agree, so the old form worked there and
        # the mutation is expected to be a no-op. Saying so is more honest than
        # skipping: the bug was platform-specific, and a test that pretended
        # otherwise would be asserting something false about this machine.
        if mutant_fired:
            ok("mutation: on POSIX the old concatenation still fires, as expected "
               "- the bug was Windows-only and this case cannot see it here")
        else:
            bad("mutation: on POSIX the old concatenation still fires",
                "It did not, which means something other than the separators is "
                "also wrong. Investigate before trusting the cases above.")

    print("")
    if failed:
        print("hook-path: FAIL - %d/%d cases" % (passed, passed + failed))
        return 1
    print("hook-path: PASS - %d/%d cases" % (passed, passed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
