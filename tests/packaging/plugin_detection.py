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

Cases 9 to 12 exist because the first version of this file recorded those two
things as a "known limit" instead of testing them, and the limit turned into a
wrong answer within the hour. Running `/plugin` inside a project wrote the
enablement to the PROJECT settings file and installed a SECOND copy of the plugin
at a newer version scoped to that project. Detection, reading only the user file
and taking whichever registry entry came first, reported the plugin as not enabled
while the harness had it loaded, and would have pointed at another project's older
version. A limit you have written down is still a defect; these are the cases.

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


def plugin_entry(install_root, version, project_path=None):
    """One registry entry, in the shape the live registry actually uses."""
    entry = {
        "scope": "project",
        "installPath": os.path.join(install_root, ".claude", "plugins", "cache",
                                    "claude-plugins-official", "superpowers", version),
        "version": version,
    }
    if project_path:
        entry["projectPath"] = project_path
    return entry


def make_home(tmp, label, hand_copy=False, registry=True, sentinel=True,
              enabled=None, settings_text=None, entries=None,
              project_enabled=None, project=None):
    """Build a fake user profile and return (home, first_plugin_install_path).

    `enabled` is what the USER settings file should say for KEY: True, False, or
    None for "the key is simply absent". `project_enabled` is the same for the
    PROJECT settings file, which is where `/plugin` actually writes when it is run
    from inside a project. `settings_text` writes raw bytes instead, for the
    malformed case. `entries` replaces the registry entries entirely.
    """
    home = os.path.join(tmp, label)
    os.makedirs(os.path.join(home, ".claude", "skills"), exist_ok=True)

    if hand_copy:
        make_skill(home, "brainstorming")

    # The default fixture is a single entry that applies here: owned by the
    # project under test when one is named, machine-wide when none is. Cases that
    # care about ownership pass `entries` and say who owns what.
    if entries is None:
        entries = [plugin_entry(home, "6.1.1", project)]
    install_path = entries[0]["installPath"] if entries else None

    if registry:
        write_json(os.path.join(home, ".claude", "plugins", "installed_plugins.json"),
                   {"version": 1, "plugins": {KEY: entries}})
    if sentinel:
        for entry in entries:
            write(os.path.join(entry["installPath"], "skills", "brainstorming",
                               "SKILL.md"),
                  "---\nname: brainstorming\nversion: %s\n---\n" % entry["version"])

    settings_path = os.path.join(home, ".claude", "settings.json")
    if settings_text is not None:
        write(settings_path, settings_text)
    else:
        doc = {"enabledPlugins": {OTHER_KEY: True}}
        if enabled is not None:
            doc["enabledPlugins"][KEY] = enabled
        write_json(settings_path, doc)

    if project_enabled is not None:
        if not project:
            fatal("project_enabled was given with no project to write it into")
        write_json(os.path.join(project, ".claude", "settings.json"),
                   {"enabledPlugins": {KEY: project_enabled}})

    return home, install_path


def superpowers(detect, project, home):
    return detect.detect(project, home=home)["components"]["superpowers"]


def main():
    if not os.path.isfile(DETECT_PATH):
        fatal("%s does not exist" % DETECT_PATH)
    if not os.path.isfile(AUDIT_PATH):
        fatal("%s does not exist" % AUDIT_PATH)

    detect = load_module(DETECT_PATH, "aaw_detect_under_test")
    for attr in ("detect", "enabled_plugins", "plugin_installs",
                 "entries_for_project"):
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
        # 8. the project's own settings file counts - this is what /plugin writes
        # ------------------------------------------------------------------
        # Running /plugin from inside a project writes the enablement HERE and
        # leaves the user file untouched. Reading only the user file reports a
        # plugin the harness has already loaded as not enabled. That is not a
        # hypothetical: it happened on this machine on 2026-09-01.
        proj8 = os.path.join(tmp, "project-enabled")
        os.makedirs(proj8, exist_ok=True)
        home8, install8 = make_home(tmp, "user-silent", enabled=None,
                                    project=proj8, project_enabled=True)
        if os.path.isfile(os.path.join(home8, ".claude", "settings.json")):
            with open(os.path.join(home8, ".claude", "settings.json"),
                      encoding="utf-8") as fh:
                if KEY in fh.read():
                    fatal("fixture 'user-silent' names the key in the USER file; "
                          "case 8 would pass without reading the project file")
        entry = superpowers(detect, proj8, home8)
        if entry["installed"] and entry["scope"] == "plugin":
            ok("enabled in the PROJECT settings file: installed")
        else:
            bad("enabled in the PROJECT settings file: installed",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 9. the chain has an order: the more specific file wins, both ways
        # ------------------------------------------------------------------
        proj9 = os.path.join(tmp, "project-local-on")
        os.makedirs(proj9, exist_ok=True)
        home9, _ = make_home(tmp, "user-false", enabled=False, project=proj9)
        write_json(os.path.join(proj9, ".claude", "settings.local.json"),
                   {"enabledPlugins": {KEY: True}})
        entry = superpowers(detect, proj9, home9)
        if entry["installed"]:
            ok("project-local true overrides user false")
        else:
            bad("project-local true overrides user false", json.dumps(entry, indent=2))

        proj10 = os.path.join(tmp, "project-off")
        os.makedirs(proj10, exist_ok=True)
        home10, _ = make_home(tmp, "user-true", enabled=True,
                              project=proj10, project_enabled=False)
        entry = superpowers(detect, proj10, home10)
        if not entry["installed"] and entry.get("plugin_present_not_enabled") == KEY:
            ok("project false overrides user true")
        else:
            bad("project false overrides user true", json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 10. two installs: this project's version wins, not the first listed
        # ------------------------------------------------------------------
        # The live registry holds one entry per install and a plugin can be
        # installed at a different version for a different project. The other
        # project's entry is deliberately listed FIRST, so a resolver that takes
        # whichever entry comes first picks the wrong version and this fails.
        proj11 = os.path.join(tmp, "project-two-installs")
        os.makedirs(proj11, exist_ok=True)
        home11 = os.path.join(tmp, "two-installs")
        entries11 = [
            plugin_entry(home11, "6.1.1", os.path.join(tmp, "some-other-project")),
            plugin_entry(home11, "6.3.0", proj11),
        ]
        home11, _ = make_home(tmp, "two-installs", enabled=None, entries=entries11,
                              project=proj11, project_enabled=True)
        entry = superpowers(detect, proj11, home11)
        if entry.get("version") == "6.3.0":
            ok("two installs: this project's version wins, not the first listed")
        else:
            bad("two installs: this project's version wins, not the first listed",
                "version=%r install_path=%r" % (entry.get("version"),
                                                entry.get("install_path")))
        if entry.get("install_path") == entries11[1]["installPath"]:
            ok("two installs: install_path is this project's, not the other one's")
        else:
            bad("two installs: install_path is this project's, not the other one's",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 11. another project's install does not count as this project's
        # ------------------------------------------------------------------
        proj12 = os.path.join(tmp, "project-borrower")
        os.makedirs(proj12, exist_ok=True)
        # The one entry in the registry is owned by a third project, so it is
        # nobody's business here even though the plugin is enabled and the files
        # are on disk.
        entries12 = [plugin_entry(os.path.join(tmp, "elsewhere-only"), "6.1.1",
                                  os.path.join(tmp, "some-other-project"))]
        home12, _ = make_home(tmp, "elsewhere-only", enabled=True,
                              entries=entries12, project=proj12)
        entry = superpowers(detect, proj12, home12)
        if not entry["installed"] and "plugin_present_not_enabled" not in entry:
            ok("an install owned by another project does not apply here")
        else:
            bad("an install owned by another project does not apply here",
                json.dumps(entry, indent=2))

        # ------------------------------------------------------------------
        # 12-14. the mutation cases: prove each new behaviour is load-bearing
        # ------------------------------------------------------------------
        # A case that passes is only worth what it would have caught. Each of the
        # three behaviours below is removed from a copy of detect.py, and the
        # fixture that depends on it is re-run against that copy. If the mutant
        # gives the same answer as the real thing, the case above proved nothing
        # and this says so in those words.
        with open(DETECT_PATH, "r", encoding="utf-8") as fh:
            source = fh.read()

        def mutant_of(needle, replacement, label):
            count = source.count(needle)
            if count != 1:
                fatal("expected exactly one %s in detect.py, found %d. The mutation "
                      "cannot be applied, so this test cannot prove anything."
                      % (label, count))
            mutated = source.replace(needle, replacement)
            if mutated == source:
                fatal("the %s mutation did not change detect.py; a mutation that "
                      "does not apply is not a test" % label)
            path = os.path.join(tmp, "detect_mutant_%s.py" %
                                label.replace(" ", "_").replace("-", "_"))
            write(path, mutated)
            return load_module(path, "aaw_detect_mutant_" + os.path.basename(path))

        # 12. the enabled gate
        gate = mutant_of("if key not in enabled:",
                         "if False:  # MUTANT: gate removed", "enabled gate")
        mutant_entry = superpowers(gate, project, off_home)
        if mutant_entry["installed"]:
            ok("mutation: removing the enabled gate flips case 2 to installed")
        else:
            bad("mutation: removing the enabled gate flips case 2 to installed",
                "The mutant still reports MISSING, so case 2 passed for some other\n"
                "reason and the cases above it prove less than they appear to.\n"
                + json.dumps(mutant_entry, indent=2))

        # 13. the settings chain beyond the user file
        chain = mutant_of(
            '    ("project", "project", (".claude", "settings.json")),\n'
            '    ("project-local", "project", (".claude", "settings.local.json")),\n',
            "    # MUTANT: project scopes removed\n", "settings chain")
        mutant_entry = superpowers(chain, proj8, home8)
        if not mutant_entry["installed"]:
            ok("mutation: reading only the user settings file breaks case 8")
        else:
            bad("mutation: reading only the user settings file breaks case 8",
                "The mutant still reports installed, so case 8 is not testing the\n"
                "project settings file - which is the one /plugin actually writes.\n"
                + json.dumps(mutant_entry, indent=2))

        # 14. per-project selection of a registry entry
        order = mutant_of(
            "    return sorted(here, key=_version_key) + sorted(anywhere, key=_version_key)",
            "    return list(entries)  # MUTANT: registry order, no ownership",
            "entry selection")
        mutant_entry = superpowers(order, proj11, home11)
        if mutant_entry.get("version") == "6.1.1":
            ok("mutation: taking registry order picks the other project's 6.1.1")
        else:
            bad("mutation: taking registry order picks the other project's 6.1.1",
                "The mutant did not pick the wrong version, so case 10 is not\n"
                "testing ownership or version order at all.\n"
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
