#!/usr/bin/env python3
"""Validate an AAW installation manifest against .aaw/installed.schema.json.

Usage:
    python tests/packaging/validate-manifest.py <manifest.json> [<manifest.json> ...]
    python tests/packaging/validate-manifest.py --self-check

Exit codes:
    0  every manifest is valid
    1  at least one manifest is invalid
    2  the validator itself could not run (missing file, unreadable schema,
       or a schema keyword this validator does not implement)

Two validators, deliberately.

The `jsonschema` package is the reference implementation and is used whenever it
imports. It is not assumed present: a CI runner or a user's machine may not have
it, and requiring a pip install to check a manifest would mean the check does not
get run. So there is also a built-in validator covering the subset of JSON Schema
this repository's schema actually uses.

The danger with a hand-rolled subset is that it silently ignores a keyword it does
not know and passes a document it should reject. That is closed here: the built-in
validator walks the schema first and **exits 2** if it meets any keyword outside
its supported set. It refuses rather than under-checks.

One check that is not a schema check.

`generated_at` has a `pattern`, and a pattern fixes the shape of a string and nothing
more: `2026-99-99T99:99:99Z` matches it and is not a date. JSON Schema's `format:
"date-time"` is an annotation that a Draft 2020-12 validator is not obliged to enforce,
and the built-in validator here does not implement formats at all, so putting it in the
schema would look like a check without being one. `semantic_errors()` does it instead,
outside both validators, and the audit that writes manifests does the same check before
writing (`tools/aaw-audit.py`).

`--self-check` runs both validators over the fixture corpus and fails if they
disagree on any fixture, so the fallback is measured against the reference on
every run of the packaging tests rather than trusted.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCHEMA_PATH = os.path.join(REPO, ".aaw", "installed.schema.json")
FIXTURE_DIR = os.path.join(HERE, "fixtures", "manifest")

# Every keyword the built-in validator understands. Anything else is a hard stop.
SUPPORTED = {
    "$schema", "$id", "$ref", "$defs", "title", "description",
    "type", "const", "enum", "required", "properties", "additionalProperties",
    "propertyNames", "minProperties", "minLength", "pattern", "allOf", "anyOf",
    "not", "if", "then",
}

TYPES = {
    "object": dict, "array": list, "string": str,
    "integer": int, "number": (int, float), "boolean": bool, "null": type(None),
}


def semantic_errors(doc):
    """Checks the schema cannot express, applied on top of it. See the note above.

    Deliberately kept out of validate_builtin(): --self-check measures the built-in
    validator against jsonschema, and that comparison only means anything while both
    are answering the same question - does this document satisfy the schema.
    """
    if not isinstance(doc, dict):
        return []
    value = doc.get("generated_at")
    if not isinstance(value, str):
        return []                  # a non-string is the schema's finding, not this one
    if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", value):
        return []                  # so is the wrong shape; do not report it twice
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        return ["/generated_at: %r has the right shape but is not a real UTC instant "
                "- %s" % (value, exc)]
    return []


class Unsupported(Exception):
    """The schema uses a keyword the built-in validator does not implement."""


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# built-in validator
# --------------------------------------------------------------------------

def audit_keywords(schema, where="#"):
    """Raise Unsupported if the schema uses anything we do not implement."""
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        return
    for key, value in schema.items():
        if key not in SUPPORTED:
            raise Unsupported("%s: unsupported keyword %r" % (where, key))
        if key in ("properties", "$defs"):
            for name, sub in value.items():
                audit_keywords(sub, "%s/%s/%s" % (where, key, name))
        elif key in ("allOf", "anyOf"):
            for i, sub in enumerate(value):
                audit_keywords(sub, "%s/%s/%d" % (where, key, i))
        elif key in ("not", "if", "then", "propertyNames", "additionalProperties"):
            audit_keywords(value, "%s/%s" % (where, key))


def resolve(root, schema):
    seen = 0
    while isinstance(schema, dict) and "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            raise Unsupported("only local $ref is supported, got %r" % ref)
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        schema = node
        seen += 1
        if seen > 20:
            raise Unsupported("$ref chain too deep - probable cycle")
    return schema


def check(root, schema, doc, path, errors):
    """Append a message to `errors` for each way `doc` fails `schema`."""
    schema = resolve(root, schema)
    if schema is True or schema == {}:
        return
    if schema is False:
        errors.append("%s: schema forbids any value here" % path)
        return

    if "type" in schema:
        expected = schema["type"]
        names = expected if isinstance(expected, list) else [expected]
        ok = False
        for name in names:
            py = TYPES[name]
            if isinstance(doc, bool) and name != "boolean":
                continue  # bool is an int in Python; JSON Schema disagrees
            if isinstance(doc, py):
                ok = True
                break
        if not ok:
            errors.append("%s: expected type %s, got %s"
                          % (path, "/".join(names), type(doc).__name__))
            return

    if "const" in schema and doc != schema["const"]:
        errors.append("%s: expected %r, got %r" % (path, schema["const"], doc))
    if "enum" in schema and doc not in schema["enum"]:
        errors.append("%s: %r is not one of %r" % (path, doc, schema["enum"]))
    if "pattern" in schema and isinstance(doc, str):
        if re.search(schema["pattern"], doc) is None:
            errors.append("%s: %r does not match %s" % (path, doc, schema["pattern"]))
    if "minLength" in schema and isinstance(doc, str) and len(doc) < schema["minLength"]:
        errors.append("%s: shorter than minLength %d" % (path, schema["minLength"]))

    if isinstance(doc, dict):
        if "minProperties" in schema and len(doc) < schema["minProperties"]:
            errors.append("%s: needs at least %d propert(y|ies), has %d"
                          % (path, schema["minProperties"], len(doc)))
        for name in schema.get("required", []):
            if name not in doc:
                errors.append("%s: missing required property %r" % (path, name))
        props = schema.get("properties", {})
        for name, value in doc.items():
            child = "%s/%s" % (path, name)
            if "propertyNames" in schema:
                check(root, schema["propertyNames"], name, "%s (name)" % child, errors)
            if name in props:
                check(root, props[name], value, child, errors)
            elif "additionalProperties" in schema:
                extra = schema["additionalProperties"]
                if extra is False:
                    errors.append("%s: property %r is not allowed here" % (path, name))
                else:
                    check(root, extra, value, child, errors)

    for sub in schema.get("allOf", []):
        check(root, sub, doc, path, errors)

    if "anyOf" in schema:
        if not any(not probe(root, sub, doc) for sub in schema["anyOf"]):
            errors.append("%s: matches none of the allowed alternatives" % path)

    if "not" in schema:
        if not probe(root, schema["not"], doc):
            errors.append("%s: matches a forbidden shape" % path)

    if "if" in schema:
        if not probe(root, schema["if"], doc) and "then" in schema:
            check(root, schema["then"], doc, path, errors)


def probe(root, schema, doc):
    """Return the error list for a subschema without recording it."""
    errors = []
    check(root, schema, doc, "#", errors)
    return errors


def validate_builtin(schema, doc):
    audit_keywords(schema)
    errors = []
    check(schema, schema, doc, "", errors)
    return errors


# --------------------------------------------------------------------------
# reference validator
# --------------------------------------------------------------------------

def validate_reference(schema, doc):
    """Return an error list, or None if jsonschema is not installed."""
    try:
        import jsonschema
    except ImportError:
        return None
    validator = jsonschema.Draft202012Validator(schema)
    return ["%s: %s" % ("/" + "/".join(str(p) for p in e.path), e.message)
            for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path))]


# --------------------------------------------------------------------------

def validate_file(schema, path):
    try:
        doc = load_json(path)
    except (OSError, ValueError) as exc:
        return ["%s: could not be read as JSON - %s" % (path, exc)]
    return validate_builtin(schema, doc) + semantic_errors(doc)


def self_check(schema):
    """Both validators must agree, valid/invalid, on every fixture."""
    if not os.path.isdir(FIXTURE_DIR):
        print("validate-manifest: no fixture directory at %s" % FIXTURE_DIR)
        return 2
    names = sorted(n for n in os.listdir(FIXTURE_DIR) if n.endswith(".json"))
    if not names:
        print("validate-manifest: fixture directory is empty")
        return 2

    reference_available = validate_reference(schema, {}) is not None
    failures = 0
    for name in names:
        path = os.path.join(FIXTURE_DIR, name)
        expect_valid = name.startswith("valid-")
        if not expect_valid and not name.startswith("invalid-"):
            print("  FAIL  %s - fixture name must start with valid- or invalid-" % name)
            failures += 1
            continue

        doc = load_json(path)
        mine_schema = validate_builtin(schema, doc)
        mine = mine_schema + semantic_errors(doc)
        got_valid = not mine

        if got_valid != expect_valid:
            print("  FAIL  %s - expected %s, got %s"
                  % (name, "valid" if expect_valid else "invalid",
                     "valid" if got_valid else "invalid"))
            for line in mine[:4]:
                print("        %s" % line)
            failures += 1
            continue

        if reference_available:
            theirs = validate_reference(schema, doc)
            # Schema findings against schema findings. semantic_errors() has no
            # counterpart in jsonschema, so including it here would report a
            # disagreement that is really the two validators being asked different
            # questions.
            if bool(theirs) != bool(mine_schema):
                print("  FAIL  %s - validators disagree: built-in says %s, "
                      "jsonschema says %s"
                      % (name, "valid" if not mine_schema else "invalid",
                         "valid" if not theirs else "invalid"))
                failures += 1
                continue
        print("  ok    %s (%s)" % (name, "valid" if got_valid else "invalid as expected"))

    print("")
    if reference_available:
        print("manifest-schema: built-in validator cross-checked against jsonschema "
              "on all %d fixtures" % len(names))
    else:
        print("manifest-schema: jsonschema is not installed here, so the built-in "
              "validator ran alone. It is keyword-audited, not cross-checked, on this run.")

    if failures:
        print("manifest-schema: FAIL - %d of %d fixtures" % (failures, len(names)))
        return 1
    print("manifest-schema: PASS - %d/%d fixtures behaved as declared" % (len(names), len(names)))
    return 0


def main(argv):
    if not os.path.isfile(SCHEMA_PATH):
        print("validate-manifest: schema not found at %s" % SCHEMA_PATH)
        return 2
    try:
        schema = load_json(SCHEMA_PATH)
    except ValueError as exc:
        print("validate-manifest: schema is not valid JSON - %s" % exc)
        return 2

    try:
        audit_keywords(schema)
    except Unsupported as exc:
        print("validate-manifest: %s" % exc)
        print("validate-manifest: refusing to validate with a validator that would "
              "ignore part of the schema. Implement the keyword or narrow the schema.")
        return 2

    if argv and argv[0] == "--self-check":
        return self_check(schema)

    if not argv:
        print(__doc__.strip().split("\n\n")[1])
        return 2

    bad = 0
    for path in argv:
        errors = validate_file(schema, path)
        if errors:
            bad += 1
            print("INVALID  %s" % path)
            for line in errors:
                print("         %s" % line)
        else:
            print("valid    %s" % path)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
