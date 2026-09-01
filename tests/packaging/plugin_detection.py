#!/usr/bin/env python3
"""Check that plugin-scoped detection reads `enabledPlugins`, not just the cache path.

Rule 5 in `.aaw/detect.py` exists because a plugin's files sit in the cache whether
the plugin is switched on or off. A sentinel probe under the cache therefore reports
a disabled plugin as installed, and - crucially - it reports that on every machine
where the plugin has ever been installed. It is a check that cannot fail.

So this file cannot be a check that cannot fail either. Two things guard that:

* **Every case asserts its own preconditions.** A case that "passes" because its
  fixture was never built is reported FATAL, not ok.
* **The last case mutates `detect.py`** - it removes the enabled gate and re-runs the
  disabled-plugin case against the mutant. If the mutant still reports MISSING, the
  gate is not what produced the earlier answer, every case above it is decorative,
  and this file says so.

Everything runs against fake homes under a temporary directory. The live profile is
never read and never written: `home=` is passed explicitly to `detect()` so this test
cannot pass by accident because of what happens to be installed on the machine
running it.

Known limit, recorded rather than papered over: only `<home>/.claude/settings.json`
is read. A plugin can also be enabled in a project's own settings, and a registry
entry can carry `"scope": "project"` with a `projectPath` - the real superpowers
entry on this machine does. Detection ignores both, so a plugin enabled only for
some other project reads as not enabled here. That is the conservative direction,
and it is the direction the AAW routing block needs, but it is a limit and not a
proof of correctness.

Exit 0 = every case behaved. 1 = a case failed. 2 = the test could not run.
"""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DETECT_PATH = os.path.join(REPO, ".aaw", "detect.py")
AUDIT_PATH = os.path.join(REPO, "tools", "aaw-audit.py")

KEY = "superpowers@claude-plugins-official"
OTHER_KEY = "code-review@claude-plugins-official"

PASS = []
FAIL = []


def ok(msg):
    PASS.append(msg)
    print("  ok    %s" % msg)


def bad(msg, detail=""):
    FAIL.append(msg)
    print("  FAIL  %s" % msg)
    if detail:
        for line in str(detail).splitlines():
            print("        %s" % line)


def fatal(msg):
    print("plugin-detection: FATAL - %s" % msg)
    raise SystemExit(2)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_json(path, doc):
    write(path, json.dumps(doc, indent=2) + "\n")


def make_skill(root, name):
    write(os.path.join(root, ".claude", "skills", name, "SKILL.md"),
          "---\nname: %s\n---\n" % name)


def make_home(tmp, label, hand_copy=False, registry=True, sentinel=True,
              enabled=None, settings_text=None):
    """Build a fake user profile and return (home, expected_plugin_install_path).

    `enabled` is what `enabledPlugins[KEY]` should be: True, False, or None for
    "the key is simply absent". `settings_text` writes raw bytes instead, for the
    malformed case.
    """
    home = os.path.join(tmp, label)
    os.makedirs(os.path.join(home, ".claude", "skills"), exist_ok=True)

    if hand_copy:
        make_skill(home, "brainstorming")

    install_path = os.path.join(home, ".claude", "plugins", "cache",
                                "claude-plugins-official", "superpowers", "6.1.1")
    if registry:
        # Mirrors the real registry's shape, including the project scope the live
        # entry carries, so the fixture cannot pass on a shape reality does not use.
        write_json(os.path.join(home, ".claude", "plugins", "installed_plugins.json"), {
            "version": 1,
            "plugins": {
                KEY: [{
                    "scope": "project",
                    "projectPath": os.path.join(tmp, "some-other-project"),
                    "installPath": install_path,
                    "version": "6.1.1",
                }],
            },
        })
    if sentinel:
        write(os.path.join(install_path, "skills", "brainstorming", "SKILL.md"),
              "---\nname: brainstorming\n---\n")

    settings_path = os.path.join(home, ".claude", "settings.json")
    if settings_text is not None:
        write(settings_path, settings_text)
    else:
        doc = {"enabledPlugins": {OTHER_KEY: True}}
        if enabled is not None:
            doc["enabledPlugins"][KEY] = enabled
        write_json(settings_path, doc)

    return home, install_path


def superpowers(detect, project, home):
    return detect.detect(project, home=home)["components"]["superpowers"]


def main():
    if not os.path.isfile(DETECT_PATH):
        fatal("%s does not exist" % DETECT_PATH)
    if not os.path.isfile(AUDIT_PATH):
        fatal("%s does not exist" % AUDIT_PATH)

    detect = load_module(DETECT_PATH, "aaw_detect_under_test")
    for attr in ("detect", "enabled_plugins", "plugin_install_paths"):
        if not hasattr(detect, attr):
            fatal("detect.py has no %s(); this test is written against a version "
                  "that does not exist" % attr)

    tmp = tempfile.mkdtemp(prefix="aaw-plugin-detect-")
    try:
        project = os.path.join(tmp, "project")
        os.makedirs(project, exist_ok=True)
        print("plugin-detection: temp root %s" % tmp)
        print("")

        # ------------------------------------------------------------------
        # 1. enabled plugin, no hand-copy: installed, and reported as a plugin
        # ------------------------------------------------------------------
        home, install_path = make_home(tmp, "enabled", enabled=True)
        if not os.path.isfile(os.path.join(install_path, "skills", "brainstorming",
                                           "SKILL.md")):
            fatal("fixture 'enabled' has no plugin sentinel; case 1 would pass blind")
        entry = superpowers(detect, project, home)
        if entry["installed"] and entry["scope"] == "plugin":
            ok("enabled plugin is installed, scope=plugin")
        else:
            bad("enabled plugin is installed, scope=plugin", json.dumps(entry, indent=2))
        if entry.get("install_path") == install_path:
            ok("install_path comes from the registry, not a guessed cache layout")
        else:
            bad("install_path comes from the registry, not a guessed cache layout",
                "got %r\nwant %r" % (entry.get("install_path"), install_path))

        # ------------------------------------------------------------------
        # 2. plugin present but switched off: MISSING, and the reason is recorded
        # ------------------------------------------------------------------
        off_home, off_install = make_home(tmp, "disabled", enabled=False)
        entry = superpowers(detect, project, off_home)
        if not entry["installed"] and entry["scope"] == "none":
            ok("enabledPlugins false: MISSING")
        else:
            bad("enabledPlugins false: MISSING", json.dumps(entry, indent=2))
        if entry.get("plugin_present_not_enabled") == KEY:
            ok("enabledPlugins false: the reason is recorded, not silently dropped")
        else:
            bad("enabledPlugins false: the reason is recorded, not silently dropped",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 3. key absent entirely is the same as false - this is the live state
        # ------------------------------------------------------------------
        absent_home, _ = make_home(tmp, "key-absent", enabled=None)
        entry = superpowers(detect, project, absent_home)
        if not entry["installed"] and entry.get("plugin_present_not_enabled") == KEY:
            ok("key absent from enabledPlugins: MISSING, reason recorded")
        else:
            bad("key absent from enabledPlugins: MISSING, reason recorded",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 4. a hand-copy in the skills directory still wins over an enabled plugin
        # ------------------------------------------------------------------
        both_home, _ = make_home(tmp, "both", hand_copy=True, enabled=True)
        entry = superpowers(detect, project, both_home)
        if entry["installed"] and entry["scope"] == "global":
            ok("a hand-copy outranks an enabled plugin (the harness loads it)")
        else:
            bad("a hand-copy outranks an enabled plugin (the harness loads it)",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 5. unreadable settings fails closed
        # ------------------------------------------------------------------
        broken_home, _ = make_home(tmp, "malformed", settings_text="{ this is not json")
        entry = superpowers(detect, project, broken_home)
        if not entry["installed"]:
            ok("malformed settings.json fails closed (MISSING, not installed)")
        else:
            bad("malformed settings.json fails closed (MISSING, not installed)",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 6. enabled but the recorded path holds no sentinel: MISSING, and NO reason
        # ------------------------------------------------------------------
        # The flag means "the files are here and the switch is off". If it also
        # fired when the files were absent it would stop meaning anything.
        hollow_home, _ = make_home(tmp, "hollow", enabled=True, sentinel=False)
        entry = superpowers(detect, project, hollow_home)
        if not entry["installed"] and "plugin_present_not_enabled" not in entry:
            ok("enabled but no files on disk: MISSING with no misleading reason")
        else:
            bad("enabled but no files on disk: MISSING with no misleading reason",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 7. the audit surfaces case 2 as a finding, end to end through the CLI
        # ------------------------------------------------------------------
        proc = subprocess.run(
            [sys.executable, AUDIT_PATH, "--project", project, "--home", off_home,
             "--format", "json"],
            capture_output=True, text=True)
        try:
            doc = json.loads(proc.stdout)
        except ValueError:
            doc = None
        if doc is None:
            bad("audit CLI emits JSON on the disabled fixture",
                (proc.stdout or proc.stderr)[:400])
        else:
            ids = [f.get("id") for f in doc.get("findings", [])]
            if "plugin-present-not-enabled" in ids:
                ok("audit reports [plugin-present-not-enabled]")
            else:
                bad("audit reports [plugin-present-not-enabled]",
                    "findings: %s" % ids)

        # ------------------------------------------------------------------
        # 8. the mutation case: prove the enabled gate is what produced case 2
        # ------------------------------------------------------------------
        with open(DETECT_PATH, "r", encoding="utf-8") as fh:
            source = fh.read()
        needle = "if key not in enabled:"
        count = source.count(needle)
        if count != 1:
            fatal("expected exactly one enabled gate (%r) in detect.py, found %d. "
                  "The mutation cannot be applied, so this test cannot prove "
                  "anything." % (needle, count))
        mutant_source = source.replace(needle, "if False:  # MUTANT: gate removed")
        if mutant_source == source:
            fatal("the mutation did not change detect.py; a mutation that does not "
                  "apply is not a test")
        mutant_path = os.path.join(tmp, "detect_mutant.py")
        write(mutant_path, mutant_source)
        mutant = load_module(mutant_path, "aaw_detect_mutant")

        mutant_entry = superpowers(mutant, project, off_home)
        if mutant_entry["installed"]:
            ok("mutation: removing the enabled gate DOES flip case 2 to installed "
               "- the gate is load-bearing")
        else:
            bad("mutation: removing the enabled gate DOES flip case 2 to installed "
                "- the gate is load-bearing",
                "The mutant still reports MISSING, so case 2 passed for some other\n"
                "reason and every case above it proves less than it appears to.\n"
                + json.dumps(mutant_entry, indent=2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    total = len(PASS) + len(FAIL)
    if FAIL:
        print("plugin-detection: FAIL - %d/%d cases" % (len(PASS), total))
        return 1
    print("plugin-detection: PASS - %d/%d cases" % (len(PASS), total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
