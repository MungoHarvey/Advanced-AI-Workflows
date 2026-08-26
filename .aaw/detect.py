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

Nothing here writes anything. Detection that mutates the thing it is detecting is
how you get a probe that always passes.
"""

from __future__ import annotations

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


def component_specs(project_root, home):
    """The sentinel each component is detected by, in the order they are checked.

    `locations` is ordered: the first sentinel that exists wins, and its scope is
    the scope recorded. A component that can be installed either globally or
    project-locally lists both.
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
            "notes": "A .advanced-plans/ directory is data, not an installation. See data_directories.",
        },
        {
            "name": "superpowers",
            "locations": [
                ("project", _j(project_root, ".claude", "skills", "brainstorming"),
                 _j(project_root, ".claude", "skills", "brainstorming", "SKILL.md")),
                ("global", _j(home, ".claude", "skills", "brainstorming"),
                 _j(home, ".claude", "skills", "brainstorming", "SKILL.md")),
            ],
            "version_file": None,
            "notes": "",
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


def detect(project_root, home=None, env=None):
    """Return the manifest body describing this project. Reads only."""
    project_root = os.path.abspath(project_root)
    home = os.path.abspath(home if home is not None else user_profile(env))

    components = {}
    for spec in component_specs(project_root, home):
        entry = None
        for scope, install_path, sentinel in spec["locations"]:
            if os.path.isfile(sentinel):
                entry = {
                    "installed": True,
                    "scope": scope,
                    "install_path": install_path,
                    "sentinel": sentinel,
                    "version": read_version(install_path, spec["version_file"]),
                }
                break
        if entry is None:
            entry = {"installed": False, "scope": "none"}
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
