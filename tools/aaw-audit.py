#!/usr/bin/env python3
"""Audit an AAW installation without asking anybody anything.

    python tools/aaw-audit.py [--project PATH] [--home PATH] [--format text|json]
                              [--require NAME[,NAME...]] [--write-manifest [--now ISO]]

The conversational `setup-with-claude` skill stays the front end for humans. This
is the same detection rules with no conversation attached, so installation health
becomes something a machine can assert in CI rather than something you find out by
asking Claude and reading the reply.

Exit codes, which are the actual output as far as a CI job is concerned:

    0  healthy    - every required component installed, and if a manifest exists
                    it is valid and agrees with the filesystem
    1  findings   - at least one thing is wrong, each one printed with an id
    2  cannot run - the audit itself could not reach an answer (bad arguments, an
                    unreadable project, no detection module). Never reported as a
                    pass, because "I could not check" and "I checked and it is
                    fine" are different answers and CI must be able to tell them
                    apart.

Determinism
-----------

Two runs against unchanged inputs produce byte-identical output. Nothing here
reads the clock, the process id, the environment beyond the profile it is told to
use, or any iteration order that is not sorted. `--write-manifest` needs a
timestamp, so it takes one with `--now` and refuses to invent one in a run whose
output is supposed to be reproducible.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
AAW_DIR = os.path.join(REPO, ".aaw")

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_CANNOT_RUN = 2

DEFAULT_REQUIRED = ["gstack", "advanced-planning"]

ISO_UTC = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


def load_detect():
    if AAW_DIR not in sys.path:
        sys.path.insert(0, AAW_DIR)
    try:
        import detect  # noqa: E402
    except ImportError as exc:
        raise RuntimeError("cannot import .aaw/detect.py from %s - %s" % (AAW_DIR, exc))
    return detect


def _import_validator_by_path():
    """`validate-manifest.py` has a hyphen, so it cannot be imported by name."""
    import importlib.util
    path = os.path.join(REPO, "tests", "packaging", "validate-manifest.py")
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location("aaw_validate_manifest", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def audit(project, home, required):
    """Return (findings, result). Findings are sorted and stable."""
    detect = load_detect()
    result = detect.detect(project, home=home)
    findings = []

    for name in sorted(required):
        entry = result["components"].get(name)
        if entry is None:
            findings.append({
                "id": "unknown-required-component",
                "component": name,
                "detail": "%r was required but this stack does not know it" % name,
            })
        elif not entry["installed"]:
            findings.append({
                "id": "required-component-missing",
                "component": name,
                "detail": "%s is required and its sentinel does not exist" % name,
            })

    for item in sorted(detect.stale_data(result), key=lambda d: d["path"]):
        findings.append({
            "id": "data-without-owner",
            "component": item["belongs_to"],
            "detail": "%s exists but %s is not installed. The data is intact; "
                      "installing the component will pick it up."
                      % (item["path"], item["belongs_to"]),
        })

    findings.extend(audit_manifest(project, result))
    findings.sort(key=lambda f: (f["id"], f["component"], f["detail"]))
    return findings, result


def audit_manifest(project, result):
    """Check a manifest if one exists. A missing manifest is reported, not fatal."""
    path = os.path.join(os.path.abspath(project), ".aaw", "installed.json")
    if not os.path.isfile(path):
        return [{
            "id": "manifest-absent",
            "component": "-",
            "detail": "%s does not exist. Detection fell back to sentinel probing, "
                      "which is correct but records nothing for the next reader." % path,
        }]

    findings = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as exc:
        return [{
            "id": "manifest-unreadable",
            "component": "-",
            "detail": "%s could not be read as JSON - %s" % (path, exc),
        }]

    validator = _import_validator_by_path()
    if validator is None:
        findings.append({
            "id": "manifest-unverified",
            "component": "-",
            "detail": "the manifest validator is not available, so the manifest was "
                      "read but not checked against the schema",
        })
    else:
        try:
            schema = validator.load_json(validator.SCHEMA_PATH)
            errors = validator.validate_builtin(schema, doc)
        except Exception as exc:
            errors = None
            findings.append({
                "id": "manifest-unverified",
                "component": "-",
                "detail": "the manifest validator could not run - %s" % exc,
            })
        if errors:
            for message in sorted(errors):
                findings.append({
                    "id": "manifest-invalid",
                    "component": "-",
                    "detail": message,
                })

    # A manifest that claims something the filesystem denies is worse than none,
    # because it is believed. Check every sentinel it names.
    for name in sorted(doc.get("components", {})):
        entry = doc["components"][name]
        if not isinstance(entry, dict) or not entry.get("installed"):
            continue
        sentinel = entry.get("sentinel")
        if sentinel and not os.path.isfile(sentinel):
            findings.append({
                "id": "manifest-stale",
                "component": name,
                "detail": "the manifest says %s is installed, but its sentinel %s "
                          "does not exist" % (name, sentinel),
            })
        live = result["components"].get(name)
        if live is not None and not live["installed"] and sentinel is None:
            findings.append({
                "id": "manifest-stale",
                "component": name,
                "detail": "the manifest says %s is installed and detection disagrees" % name,
            })
    return findings


def render_text(findings, result, required):
    lines = []
    lines.append("AAW installation audit")
    lines.append("  project: %s" % result["project_root"])
    lines.append("  platform: %s" % result["platform"])
    lines.append("")
    lines.append("  %-18s %-11s %-8s %s" % ("COMPONENT", "STATUS", "SCOPE", "LOCATION"))
    for row in _rows(result):
        lines.append("  %-18s %-11s %-8s %s" % row)
    lines.append("")
    lines.append("  DATA")
    for item in result["data_directories"]:
        lines.append("  %-9s %-18s %s"
                     % ("present" if item["present"] else "absent",
                        item["belongs_to"], item["path"]))
    lines.append("")
    lines.append("  required: %s" % ", ".join(sorted(required)))
    lines.append("")
    if findings:
        lines.append("FINDINGS (%d)" % len(findings))
        for f in findings:
            lines.append("  [%s] %s" % (f["id"], f["detail"]))
        lines.append("")
        lines.append("audit: FINDINGS - %d" % len(findings))
    else:
        lines.append("audit: HEALTHY")
    return "\n".join(lines) + "\n"


def _rows(result):
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


def render_json(findings, result, required):
    doc = {
        "audit_version": 1,
        "project_root": result["project_root"],
        "platform": result["platform"],
        "required": sorted(required),
        "components": result["components"],
        "data_directories": result["data_directories"],
        "findings": findings,
        "healthy": not findings,
    }
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def write_manifest(project, result, now, generated_by):
    if not ISO_UTC.match(now):
        raise ValueError("--now must be UTC ISO 8601 like 2026-08-26T15:00:00Z, got %r" % now)
    doc = {k: v for k, v in result.items() if k != "data_directories"}
    doc["generated_at"] = now
    doc["generated_by"] = generated_by
    target_dir = os.path.join(os.path.abspath(project), ".aaw")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "installed.json")
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="aaw-audit",
        description="Audit an AAW installation. Non-interactive and deterministic.")
    parser.add_argument("--project", default=".", help="project root to audit (default: cwd)")
    parser.add_argument("--home", default=None,
                        help="override the user profile. Intended for tests, so an audit "
                             "can be run against a fake profile without touching the real one.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--require", default=",".join(DEFAULT_REQUIRED),
                        help="comma-separated components that must be installed "
                             "(default: %s)" % ",".join(DEFAULT_REQUIRED))
    parser.add_argument("--write-manifest", action="store_true",
                        help="write .aaw/installed.json from what was detected")
    parser.add_argument("--now", default=None,
                        help="UTC ISO 8601 timestamp for --write-manifest. Required with it: "
                             "this tool does not read the clock, so that two runs over "
                             "unchanged inputs produce identical output.")
    args = parser.parse_args(argv)

    project = os.path.abspath(args.project)
    if not os.path.isdir(project):
        sys.stderr.write("aaw-audit: not a directory: %s\n" % project)
        return EXIT_CANNOT_RUN

    required = [r.strip() for r in args.require.split(",") if r.strip()]

    # Order matters, and the test caught this rather than a reading of the code:
    # the manifest is written first and the findings are computed afterwards.
    # Auditing before the write meant a run that had just created a perfectly good
    # manifest still reported it absent and exited 1, so `--write-manifest` on a
    # healthy project could never succeed on its first use.
    if args.write_manifest and args.now is None:
        sys.stderr.write(
            "aaw-audit: --write-manifest needs --now. This tool does not read the "
            "clock, so that its output is reproducible; pass the timestamp in.\n")
        return EXIT_CANNOT_RUN

    try:
        detect = load_detect()
        home = args.home if args.home is not None else detect.user_profile()
        if args.write_manifest:
            target = write_manifest(project, detect.detect(project, home=home),
                                    args.now, "aaw-audit 1")
            sys.stderr.write("aaw-audit: wrote %s\n" % target)
        findings, result = audit(project, home, required)
    except (OSError, ValueError) as exc:
        sys.stderr.write("aaw-audit: cannot run - %s\n" % exc)
        return EXIT_CANNOT_RUN
    except Exception as exc:
        sys.stderr.write("aaw-audit: cannot run - %s\n" % exc)
        return EXIT_CANNOT_RUN

    if args.format == "json":
        sys.stdout.write(render_json(findings, result, required))
    else:
        sys.stdout.write(render_text(findings, result, required))

    return EXIT_FINDINGS if findings else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
