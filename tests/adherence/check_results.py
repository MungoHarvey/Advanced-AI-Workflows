# -*- coding: utf-8 -*-
"""Check recorded ACC-RESULT reports against expected.json.

The adherence rounds cannot run in CI - they need live model calls, and two of
the five runtimes need an operator-granted permission flag. What *can* be
mechanical is the grading, and until now it was done by eye.

Two checks run over every result:

1. **Expectation match.** Does `routed_to` fall in the allowed set for that
   fixture and request? Does the spec go where the block says? Is the terminal
   step the one the block routes to?

2. **Fabrication check.** Every non-NONE command or skill named in `routed_to`
   or `terminal_step` must appear verbatim in the routing block. A runtime that
   invents a plausible-sounding command has failed, even if the command it
   invented would have been a good idea.

A recorded result that predates a change to the block can legitimately fail
check 1. That is reported as a mismatch against the block the expectations were
authored for, and the results directory's date is printed next to it, so the
reader can tell "the runtime was wrong" from "the instruction changed".

Usage
-----
    python tests/adherence/check_results.py                 # every results/ dir
    python tests/adherence/check_results.py --results DIR   # just one
    python tests/adherence/check_results.py --json          # machine-readable

Exit 0 if every result matched, 1 if any did not, 2 if the check could not run.
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BLOCK = os.path.join(REPO, ".claude", "skills", "setup-with-claude",
                     "references", "claude-md-routing.md")

NONE_VALUES = {"none", "n/a", "na", "", "-"}
# "NONE (review done directly)" is NONE with an explanation attached.
NONE_HEAD = re.compile(r"^\s*(none|n/a|na)\b", re.I)
# Everything that reads as "there is no command; do the work in conversation".
CONVERSATION = re.compile(
    r"\bconversation\b|\bdirectly\b|\bno (?:such )?(?:command|skill|tool)\b"
    r"|\bnot available\b|\bdoes not exist\b|\bmyself\b", re.I)


def is_none(v):
    if v is None:
        return True
    return v.strip().lower() in NONE_VALUES or bool(NONE_HEAD.match(v))


def parse_result(path):
    """Parse an ACC-RESULT report into {request: {field: value}} plus environment.

    Tolerant on purpose: agy wraps its report in a fence and appends an exit
    line, cursor prints it to stdout with surrounding prose. The shape that
    matters is '## Request N' followed by 'key: value' lines.
    """
    text = io.open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    text = re.sub(r"^```[a-zA-Z]*\n|\n```\s*$", "\n", text.strip())
    out, env, cur = {}, None, None
    for line in text.split("\n"):
        m = re.match(r"^\s*#{1,4}\s*Request\s+(\d+)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = {}
            continue
        if re.match(r"^\s*#{1,4}\s*Environment\s*$", line):
            cur = "_env"
            env = {}
            continue
        m = re.match(r"^\s*([a-z_]+)\s*:\s*(.*)$", line)
        if m and cur:
            k, v = m.group(1), m.group(2).strip()
            (env if cur == "_env" else out[cur])[k] = v
    return out, (env or {})


# A slash command is /foo, but NOT the /foo inside src/cli.py or
# docs/superpowers/plans/ - a path segment must not read as a command name, or
# every file path in a prose answer looks like a fabrication.


def named_tokens(value):
    """Every command or skill name a field mentions, in order of appearance.

    Order matters: the FIRST one is the route, and the rest are usually the
    branches being explained away ("...only when Advanced Planning is installed;
    here it is false"). Grading on the whole set accuses a runtime of taking a
    route it explicitly declined.
    """
    if is_none(value):
        return []
    found = []
    for m in re.finditer(r"(?<![\w./-])/[a-z][a-z0-9-]+(?![\w./-])|`[^`]+`",
                         value):
        tok = m.group(0)
        if tok.startswith("`"):
            tok = tok.strip("`")
            # A backticked name is a name whether or not it carries the slash.
            if not re.fullmatch(r"/?[a-z][a-z0-9-]*", tok):
                continue
        if tok not in found:
            found.append(tok)
    if not found:
        bare = value.strip().split()[0].strip(".,;:`") if value.strip() else ""
        if re.fullmatch(r"[a-z][a-z0-9-]{2,}", bare):
            found = [bare]
    return found


def head_token(value):
    """The one name a field is actually routing to, or None."""
    toks = named_tokens(value)
    return toks[0] if toks else None


def check_one(fixture_spec, parsed, block_text, read_only=False):
    problems, fabricated, skipped = [], [], []
    for req, spec in sorted(fixture_spec["requests"].items()):
        got = parsed.get(req)
        if got is None:
            problems.append("request %s: missing from the report" % req)
            continue
        routed = got.get("routed_to", "")
        allowed = spec.get("routed_to_any_of")

        if allowed == []:
            if not is_none(routed):
                problems.append(
                    "request %s: routed_to=%r, expected NONE - %s"
                    % (req, routed, spec["why"]))
        elif allowed:
            if not any(a.lower() in routed.lower() for a in allowed):
                problems.append(
                    "request %s: routed_to=%r, expected one of %s"
                    % (req, routed, ", ".join(allowed)))

        sf = got.get("spec_file", "")
        forbidden = spec.get("spec_file_forbidden_prefix")
        if forbidden and not is_none(sf):
            if forbidden.rstrip("/") in sf.replace("\\", "/"):
                problems.append("request %s: spec_file=%r is under %s, which "
                                "this project has given it no evidence exists"
                                % (req, sf, forbidden))

        prefix = spec.get("spec_file_prefix")
        if prefix:
            if is_none(sf):
                # A read-only run could not write the file, so a NONE here is a
                # permission decision, not a routing one. Grading it would fail
                # the runtime for something the operator withheld.
                if read_only:
                    skipped.append("request %s: spec location not verifiable - "
                                   "the run was read-only" % req)
                else:
                    problems.append("request %s: spec_file is NONE, expected a "
                                    "path under %s" % (req, prefix))
            elif prefix.rstrip("/") not in sf.replace("\\", "/"):
                problems.append("request %s: spec_file=%r, expected a path under %s"
                                % (req, sf, prefix))

        if "terminal_step_any_of" in spec:
            ts = got.get("terminal_step", "")
            allow_ts = spec["terminal_step_any_of"]
            if allow_ts == []:
                # Must not ROUTE to a command or skill; mentioning one while
                # explaining why it does not apply here is fine, and describing
                # the work in prose is the answer being looked for.
                # The answer is in the first sentence; what follows is usually
                # the runtime listing the routes it considered and rejected.
                # "Write the plan directly, in conversation. Not `/new-phase`,
                # not `writing-plans` - neither is installed here" is a correct
                # answer that names three commands.
                head = head_token(ts)
                first = re.split(r"(?<=[.;])\s", ts.strip(), maxsplit=1)[0]
                if head and not CONVERSATION.search(first):
                    problems.append(
                        "request %s: terminal_step routes to %r, expected no "
                        "command - %s" % (req, head,
                                          spec.get("terminal_step_note",
                                                   spec["why"])))
            elif not any(a.lower() in ts.lower() for a in allow_ts):
                problems.append("request %s: terminal_step=%r, expected one of %s"
                                % (req, ts, ", ".join(allow_ts)))

        for field in ("routed_to", "terminal_step"):
            for tok in named_tokens(got.get(field, "")):
                if tok not in block_text:
                    fabricated.append("request %s: %s names %r, which does not "
                                      "appear in the block" % (req, field, tok))
    return problems, fabricated, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--results", action="append",
                    help="a results directory (repeatable); default: all of them")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not os.path.isfile(BLOCK):
        print("cannot run: routing block not found at %s" % BLOCK)
        return 2
    block_text = io.open(BLOCK, encoding="utf-8", newline="").read()
    expected = json.loads(io.open(os.path.join(HERE, "expected.json"),
                                  encoding="utf-8").read())

    dirs = args.results
    if not dirs:
        base = os.path.join(HERE, "results")
        dirs = [os.path.join(base, d) for d in sorted(os.listdir(base))
                if os.path.isdir(os.path.join(base, d))]
    if not dirs:
        print("cannot run: no results directories")
        return 2

    rows, failed = [], 0
    for d in dirs:
        label = os.path.basename(d.rstrip(os.sep))
        # MANIFEST.json says how each run was invoked. Its 'mode' is what tells
        # a read-only run apart from one that declined to write.
        manifest, mpath = {}, os.path.join(d, "MANIFEST.json")
        if os.path.isfile(mpath):
            manifest = json.loads(io.open(mpath, encoding="utf-8").read())
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            name = fn[:-3]
            if "--" not in name:
                continue
            runtime, fixture = name.split("--", 1)
            spec = expected["fixtures"].get(fixture)
            if spec is None:
                rows.append(dict(set=label, runtime=runtime, fixture=fixture,
                                 status="SKIP",
                                 detail=["no expectation for this fixture"]))
                continue
            mode = manifest.get("runs", {}).get(runtime, {}).get("mode", "write")
            parsed, _env = parse_result(os.path.join(d, fn))
            problems, fabricated, skipped = check_one(
                spec, parsed, block_text, read_only=(mode == "read-only"))

            known = [k for k in expected.get("known_divergences", [])
                     if k["set"] == label and k["runtime"] == runtime
                     and k["fixture"] == fixture]
            diverged = []
            for k in known:
                hit = [p for p in problems if k["match"] in p]
                if hit:
                    problems = [p for p in problems if p not in hit]
                    diverged += ["%s [known: %s]" % (h, k["reason"]) for h in hit]

            status = "PASS"
            if fabricated:
                status = "FABRICATED"
            elif problems:
                status = "MISMATCH"
            elif diverged:
                status = "DIVERGED"
            elif skipped:
                status = "PASS (read-only)"
            if status in ("FABRICATED", "MISMATCH"):
                failed += 1
            rows.append(dict(set=label, runtime=runtime, fixture=fixture,
                             mode=mode, status=status,
                             detail=fabricated + problems + diverged + skipped))

    if args.json:
        print(json.dumps(dict(block_at_authoring=expected["block_at_authoring"],
                              rows=rows), indent=2))
    else:
        width = max(len(r["runtime"]) for r in rows)
        print("expectations authored against block %s\n"
              % expected["block_at_authoring"])
        for r in rows:
            print("  %-10s  %-*s  %-18s  %s"
                  % (r["set"], width, r["runtime"], r["fixture"], r["status"]))
            for line in r["detail"]:
                print("      - %s" % line)
        n_div = sum(1 for r in rows if r["status"] == "DIVERGED")
        print("\nadherence: %d/%d matched, %d known divergence(s)"
              % (len(rows) - failed - n_div, len(rows), n_div))
        if n_div:
            print("adherence: a DIVERGED cell is a recorded result the current"
                  "\nadherence: block would no longer produce. It does not fail the"
                  "\nadherence: run, but it does mean that cell's evidence is stale."
                  "\nadherence: Re-run the round to close it; see expected.json.")
        if failed:
            print("adherence: FAIL - see the cells marked MISMATCH or FABRICATED.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
