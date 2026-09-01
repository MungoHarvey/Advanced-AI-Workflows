#!/usr/bin/env python3
"""Decide what Advanced AI Workflows has installed in a project.

One set of rules, used by both the conversational `setup-with-claude` skill and
the non-interactive audit, so the two can never drift into disagreeing about what
"installed" means.

Why this exists
---------------

Detection used to be a path probe, and the probe lied in both directions.

It produced false positives. `advanced-planning` was reported installed if
`.advanced-plans/` existed at the project root. `.advanced-plans/` is where the
tool writes its *data*: it survives uninstalling the tool, it can be copied into
a project with a template, and it can be created by a person who read the docs.
A data directory is not an installation. That is ACC-02.

It produced false negatives too. `gstack` installs into the user profile, so a
project-local probe cannot see it, and on a machine where HOME and USERPROFILE
disagree even a global probe can miss it depending on which shell is running.

The rules
---------

1. A component is installed if and only if its **sentinel file** exists. The
   sentinel is a file the component's own installer writes - a SKILL.md, not a
   directory the component merely uses.
2. Data directories are reported separately, as data. `.advanced-plans/` present
   without `phase-plan-creator/SKILL.md` means "data present, tool absent", which
   is a real and useful state: it usually means the tool was removed, or the
   project was copied from one that had it.
3. Global locations resolve from `USERPROFILE` on Windows, never from `HOME` and
   never from `~`. On this machine those disagree.
4. Every path reported is absolute and native. A caller that wants to display a
   shortened path may shorten it; the recorded value stays absolute.
5. A component delivered as a harness **plugin** is installed only when that
   plugin is *enabled*. A plugin's files sit in the cache whether it is switched
   on or off, so a sentinel under the cache proves nothing by itself - probing it
   alone would report a disabled plugin as installed, which is a check that
   cannot fail. The deciding fact is `enabledPlugins` in the harness settings,
   and only an explicit `true` counts there: `false` and absent both mean the
   harness will not load it.
6. There is no single settings file and no single install. `enabledPlugins` is a
   chain - user, then project, each with a `.local` companion - and `/plugin`
   writes whichever scope the user was in, so reading only the user file reports
   an already-loaded plugin as absent. The registry likewise holds one entry per
   install, and a plugin can be installed at a different version for a different
   project; the entry that applies here is the one naming this project, else a
   machine-wide one, and never some other project's. Both halves of this rule
   were written after the version without them gave the wrong answer about the
   machine it was running on.

Nothing here writes anything. Detection that mutates the thing it is detecting is
how you get a probe that always passes.
"""

from __future__ import annotations

import json
import os
import sys

SCHEMA_VERSION = 1


def user_profile(env=None):
    """The user's home directory, resolved the way this programme requires.

    On Windows, USERPROFILE is authoritative. HOME is not consulted: on a domain
    machine it can be redirected to a network drive by the AD home-folder
    attribute while the real profile stays on C:, and a component installed under
    the real profile then looks absent. On POSIX, HOME is the normal answer.
    """
    env = os.environ if env is None else env
    if os.name == "nt":
        profile = env.get("USERPROFILE")
        if profile:
            return profile
        drive, path = env.get("HOMEDRIVE"), env.get("HOMEPATH")
        if drive and path:
            return drive + path
        raise RuntimeError("USERPROFILE is not set; cannot resolve the user profile")
    home = env.get("HOME")
    if not home:
        raise RuntimeError("HOME is not set; cannot resolve the user profile")
    return home


def platform_name():
    if os.name == "nt":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def _j(*parts):
    return os.path.normpath(os.path.join(*parts))


#: Where the harness records which plugins it will load. There is not one file:
#: settings are a chain, and `/plugin` writes the enablement into whichever scope
#: the user was in. Enabling a plugin from inside a project writes the PROJECT
#: file and leaves the user file untouched, so reading only the user file reports
#: a plugin the harness has already loaded as not enabled. Measured on this
#: machine 2026-09-01, within an hour of the version that read only the user file.
#:
#: Listed least specific first; a later file overrides an earlier one for the same
#: key. All are read, none is written.
SETTINGS_CHAIN = (
    ("user", "home", (".claude", "settings.json")),
    ("user-local", "home", (".claude", "settings.local.json")),
    ("project", "project", (".claude", "settings.json")),
    ("project-local", "project", (".claude", "settings.local.json")),
)

#: Where the harness records where each installed plugin's files were unpacked.
PLUGIN_REGISTRY_RELPATH = (".claude", "plugins", "installed_plugins.json")


def _read_json(path):
    """Parse a JSON file, or return None if it is missing or unreadable.

    Malformed is treated the same as absent on purpose. A caller that cannot read
    the settings cannot prove anything is enabled, and the honest answer to
    "is this enabled?" when the evidence is unreadable is no.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def enabled_plugins(home, project_root=None):
    """The set of plugin keys the harness will actually load, for this project.

    Reads the whole settings chain, least specific first, so a later scope
    overrides an earlier one for the same key. Only an explicit ``true`` counts:
    ``false`` and a key that is simply absent both mean the harness will not load
    the plugin, and its cached files are inert.

    A file that is missing or unreadable contributes nothing and does not veto the
    others. That is the honest reading - an unparseable file is not evidence of
    anything, in either direction - and it still fails closed when nothing in the
    chain says ``true``.
    """
    merged = {}
    for _scope, base, relpath in SETTINGS_CHAIN:
        root = home if base == "home" else project_root
        if not root:
            continue
        data = _read_json(_j(root, *relpath))
        if not isinstance(data, dict):
            continue
        enabled = data.get("enabledPlugins")
        if not isinstance(enabled, dict):
            continue
        merged.update(enabled)
    return {key for key, value in merged.items() if value is True}


def plugin_installs(home):
    """Map each plugin key to the registry entries recorded for it.

    Read from the harness's own registry rather than reconstructed from a cache
    layout, because the path carries a version segment that changes on every
    upgrade. A guessed path would go stale silently; a recorded one cannot.

    Entries are returned whole, not reduced to paths, because the same plugin can
    be installed more than once - a different version per project - and choosing
    between them needs `projectPath` and `version`, not just the path.
    """
    data = _read_json(_j(home, *PLUGIN_REGISTRY_RELPATH))
    if not isinstance(data, dict):
        return {}
    plugins = data.get("plugins")
    if not isinstance(plugins, dict):
        return {}
    out = {}
    for key, entries in plugins.items():
        if not isinstance(entries, list):
            continue
        kept = [e for e in entries if isinstance(e, dict) and e.get("installPath")]
        if kept:
            out[key] = kept
    return out


def _version_key(entry):
    """Sortable version, highest first. Unparseable sorts last, never first."""
    parts = str(entry.get("version") or "").split(".")
    try:
        return (0, tuple(-int(p) for p in parts))
    except ValueError:
        return (1, ())


def entries_for_project(entries, project_root):
    """The registry entries that apply to this project, most specific first.

    A registry entry can name the project it was installed for. An entry naming
    *this* project is the one that applies; an entry naming no project is a
    machine-wide install and applies everywhere. An entry naming a **different**
    project does not apply here, and treating it as if it did is how detection
    ends up reporting some other project's older version - which is exactly what
    the first version of this code would have done on this machine, silently,
    because it took whichever entry the registry happened to list first.

    Within a tier, the highest version wins.
    """
    here, anywhere = [], []
    for entry in entries:
        owner = entry.get("projectPath")
        if not owner:
            anywhere.append(entry)
        elif os.path.normcase(os.path.normpath(owner)) == \
                os.path.normcase(os.path.normpath(project_root)):
            here.append(entry)
    return sorted(here, key=_version_key) + sorted(anywhere, key=_version_key)


def component_specs(project_root, home):
    """The sentinel each component is detected by, in the order they are checked.

    `locations` is ordered: the first sentinel that exists wins, and its scope is
    the scope recorded. A component that can be installed either globally or
    project-locally lists both.

    A location is one of two forms:

    * ``(scope, install_path, sentinel)`` - a path on disk. Installed iff the
      sentinel file exists.
    * ``{"scope": "plugin", "plugin": <key>, "sentinel": (<parts>, ...)}`` - a
      harness plugin. Installed iff the plugin is **enabled** *and* the sentinel
      exists beneath the path the harness recorded for it. Presence alone is not
      enough; see rule 5 in the module docstring.

    Path locations are listed before plugin ones so that a copy the user placed
    in a skills directory is reported as the thing in force, which is what the
    harness will load.
    """
    return [
        {
            "name": "gstack",
            "locations": [
                ("global", _j(home, ".claude", "skills", "gstack"),
                 _j(home, ".claude", "skills", "gstack", "SKILL.md")),
            ],
            "version_file": None,
            "notes": "gstack installs globally; a project-local probe cannot see it.",
        },
        {
            "name": "advanced-planning",
            "locations": [
                ("project", _j(project_root, ".claude", "skills", "phase-plan-creator"),
                 _j(project_root, ".claude", "skills", "phase-plan-creator", "SKILL.md")),
                ("global", _j(home, ".claude", "skills", "phase-plan-creator"),
                 _j(home, ".claude", "skills", "phase-plan-creator", "SKILL.md")),
            ],
            "version_file": "VERSION",
            "notes": "A .advanced-plans/ directory is data, not an installation. "
                     "The audit JSON lists any such directories under data_directories; "
                     "the installed.json manifest carries components only.",
        },
        {
            "name": "superpowers",
            "locations": [
                ("project", _j(project_root, ".claude", "skills", "brainstorming"),
                 _j(project_root, ".claude", "skills", "brainstorming", "SKILL.md")),
                ("global", _j(home, ".claude", "skills", "brainstorming"),
                 _j(home, ".claude", "skills", "brainstorming", "SKILL.md")),
                {
                    "scope": "plugin",
                    "plugin": "superpowers@claude-plugins-official",
                    "sentinel": ("skills", "brainstorming", "SKILL.md"),
                },
            ],
            "version_file": None,
            "notes": "Also ships as a harness plugin. A plugin copy counts only "
                     "when the plugin is enabled - the cached files are present "
                     "either way, so their existence decides nothing.",
        },
        {
            "name": "gstack-to-plans",
            "locations": [
                ("project", _j(project_root, ".claude", "skills", "gstack-to-plans"),
                 _j(project_root, ".claude", "skills", "gstack-to-plans", "SKILL.md")),
                ("global", _j(home, ".claude", "skills", "gstack-to-plans"),
                 _j(home, ".claude", "skills", "gstack-to-plans", "SKILL.md")),
            ],
            "version_file": None,
            "notes": "The glue skill shipped by this repository.",
        },
    ]


# Directories a component writes but does not install. Their presence is reported
# and never treated as evidence that anything is installed.
DATA_DIRECTORIES = [
    {
        "path": (".advanced-plans",),
        "belongs_to": "advanced-planning",
        "meaning": "Advanced Planning's plan and state artefacts.",
    },
    {
        "path": (".claude", "integrations.json"),
        "belongs_to": "setup-with-claude",
        "meaning": "The v0.1 bookkeeping file. Superseded by .aaw/installed.json; "
                   "its recorded paths use ~ and cannot be resolved reliably.",
    },
]

DEPRECATED = {
    "plannotator": {
        "deprecated": "2026-08-26",
        "notes": "Deprecated by this programme. Not installed and not detected. "
                 "A pre-existing install elsewhere is left untouched.",
    },
}


def read_version(root, version_file):
    if not version_file:
        return "unknown"
    path = _j(root, version_file)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            value = fh.read().strip()
    except OSError:
        return "unknown"
    return value if value else "unknown"


def _resolve_plugin_location(location, enabled, installs, project_root):
    """Resolve a plugin location to (install_path, sentinel, version), or say why not.

    Returns ``(resolved, disabled_key)``. ``resolved`` is the triple when the
    plugin is enabled and its sentinel is on disk. ``disabled_key`` is the plugin
    key when the files are there but the plugin is switched off - a state worth
    reporting rather than silently calling absent, because it is one settings
    toggle away from being the installation.

    The version comes from the registry rather than a VERSION file, because a
    plugin does not necessarily ship one and the harness already recorded which
    version it unpacked.
    """
    key = location["plugin"]
    sentinel_parts = location["sentinel"]
    found = None
    for entry in entries_for_project(installs.get(key, []), project_root):
        base = entry["installPath"]
        sentinel = _j(base, *sentinel_parts)
        if os.path.isfile(sentinel):
            found = (base, sentinel, entry.get("version") or "unknown")
            break
    if found is None:
        return None, None
    if key not in enabled:
        return None, key
    return found, None


def detect(project_root, home=None, env=None):
    """Return the manifest body describing this project. Reads only."""
    project_root = os.path.abspath(project_root)
    home = os.path.abspath(home if home is not None else user_profile(env))

    enabled = enabled_plugins(home, project_root)
    installs = plugin_installs(home)

    components = {}
    for spec in component_specs(project_root, home):
        entry = None
        disabled_plugin = None
        for location in spec["locations"]:
            if isinstance(location, dict):
                resolved, disabled_key = _resolve_plugin_location(
                    location, enabled, installs, project_root)
                if disabled_key and disabled_plugin is None:
                    disabled_plugin = disabled_key
                if resolved is None:
                    continue
                install_path, sentinel, version = resolved
                scope = location["scope"]
            else:
                scope, install_path, sentinel = location
                if not os.path.isfile(sentinel):
                    continue
                version = read_version(install_path, spec["version_file"])
            entry = {
                "installed": True,
                "scope": scope,
                "install_path": install_path,
                "sentinel": sentinel,
                "version": version,
            }
            break
        if entry is None:
            entry = {"installed": False, "scope": "none"}
        if disabled_plugin:
            entry["plugin_present_not_enabled"] = disabled_plugin
        if spec["notes"]:
            entry["notes"] = spec["notes"]
        components[spec["name"]] = entry

    for name, extra in DEPRECATED.items():
        entry = {"installed": False, "scope": "none"}
        entry.update(extra)
        components[name] = entry

    data = []
    for item in DATA_DIRECTORIES:
        path = _j(project_root, *item["path"])
        data.append({
            "path": path,
            "present": os.path.exists(path),
            "belongs_to": item["belongs_to"],
            "meaning": item["meaning"],
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "platform": platform_name(),
        "project_root": project_root,
        "components": components,
        "data_directories": data,
    }


def status_rows(result):
    """Rows for a human-readable table: (component, status, scope, location)."""
    rows = []
    for name in sorted(result["components"]):
        entry = result["components"][name]
        if entry.get("deprecated"):
            status = "deprecated"
        elif entry["installed"]:
            status = "installed"
        else:
            status = "MISSING"
        rows.append((name, status, entry["scope"], entry.get("install_path", "-")))
    return rows


def data_rows(result):
    """Rows for the data table: (path, present, belongs_to)."""
    return [(d["path"], "present" if d["present"] else "absent", d["belongs_to"])
            for d in result["data_directories"]]


def stale_data(result):
    """Data directories present while the component that owns them is not installed.

    This is the state the old probe reported as 'installed'. Reporting it plainly
    is the point of ACC-02: the user is told the data is there AND that the tool
    is not, rather than being told a comfortable half-truth.
    """
    out = []
    for item in result["data_directories"]:
        owner = result["components"].get(item["belongs_to"])
        if item["present"] and owner is not None and not owner["installed"]:
            out.append(item)
    return out


def disabled_plugins(result):
    """Components whose plugin copy is on disk but switched off: [(name, key)].

    The counterpart of `stale_data` for rule 5. A component in this state reads
    MISSING, and that is correct - the harness will not load it - but the reason
    is a settings toggle rather than an absent install, and saying so is the
    difference between a useful report and a puzzling one.
    """
    out = []
    for name in sorted(result["components"]):
        entry = result["components"][name]
        key = entry.get("plugin_present_not_enabled")
        if key and not entry["installed"]:
            out.append((name, key))
    return out
