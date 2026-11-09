#!/usr/bin/env python3
"""Measure real skill loads: one fresh `claude -p` session per prompt in evals/routing/cases.md.

  run_real.py --model ALIAS --out RUN.md [--effort LEVEL] [--cases 1,5,31] [--jobs 4] [--fixture]

--fixture runs each session in a copy of evals/routing/fixture-rn, a small React Native app, and adds
the read-only Glob and Grep so the session can see what is in scope.

Unlike the self-report runner brief in cases.md, nothing tells the session it is being measured.
Each session gets only the Skill and Read tools and no MCP servers, in an empty directory, so a
prompt such as "create a Jira ticket" can load skills but cannot act. RUN.md is a table for grade.py;
RUN.md.jsonl keeps every session's load order as the raw record. Claude Code only: other runtimes
keep the runner brief.
"""
import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.realpath(os.path.join(HERE, "..", "..", "skills"))
FIXTURE = os.path.join(HERE, "fixture-rn")
READ_SKILL = re.compile(r"/skills/([a-z0-9-]+)/SKILL\.md$")
TIMEOUT = 300


def prompts():
    out = {}
    for line in open(os.path.join(HERE, "cases.md"), encoding="utf-8"):
        if re.match(r"^\| \d+ \|", line):
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            out[int(cols[0])] = cols[1]
    return out


def loads(stream):
    """Skill names in load order, from Skill calls and from reads of a SKILL.md."""
    found, error = [], None
    for raw in stream.splitlines():
        try:
            event = json.loads(raw)
        except ValueError:
            continue
        if event.get("type") == "result" and event.get("is_error"):
            error = str(event.get("result"))[:200]
        if event.get("type") != "assistant":
            continue
        for block in event["message"].get("content", []):
            if block.get("type") != "tool_use":
                continue
            args = block.get("input", {})
            name = args.get("skill") if block["name"] == "Skill" else None
            if block["name"] == "Read":
                m = READ_SKILL.search(args.get("file_path", ""))
                name = m.group(1) if m else None
            if name and name not in found:
                found.append(name)
    return found, error


def run_one(number, prompt, opts):
    tools = "Skill,Read,Glob,Grep" if opts.fixture else "Skill,Read"
    command = ["claude", "-p", prompt, "--model", opts.model, "--output-format", "stream-json",
               "--verbose", "--tools", tools, "--allowedTools", tools,
               "--strict-mcp-config", "--no-session-persistence"]
    if opts.effort:
        command += ["--effort", opts.effort]
    with tempfile.TemporaryDirectory() as work:
        if opts.fixture:
            work = os.path.join(work, "app")
            shutil.copytree(FIXTURE, work)
            # Stored without the dot so the repo's ignore rule for plans does not hide it.
            os.rename(os.path.join(work, "dot-claude"), os.path.join(work, ".claude"))
        try:
            done = subprocess.run(command, cwd=work, capture_output=True, text=True,
                                  timeout=TIMEOUT, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return number, [], "timeout"
    found, error = loads(done.stdout)
    if done.returncode and not error:
        error = f"exit {done.returncode}: {done.stderr[:200]}"
    return number, found, error


def row(number, found, project):
    names = [s.split(":")[-1] if s.split(":")[-1] in project else s for s in found]
    stage = [s for s in names if s.startswith("wf-")] + [s for s in names if s == "ai-workflow"]
    domain = [s for s in names if s in project and not s.startswith("wf-") and s != "ai-workflow"]
    other = [s for s in names if s not in project and not s.startswith("wf-")]
    return f"| {number} | {', '.join(stage) or 'none'} | {', '.join(domain) or 'none'} | {', '.join(other) or 'none'} |"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort")
    parser.add_argument("--out", required=True)
    parser.add_argument("--cases")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--fixture", action="store_true")
    opts = parser.parse_args()
    cases = prompts()
    if opts.cases:
        cases = {n: cases[n] for n in map(int, opts.cases.split(","))}
    project = set(os.listdir(SKILLS)) | {"wf-worklog"}
    with concurrent.futures.ThreadPoolExecutor(opts.jobs) as pool:
        results = sorted(pool.map(lambda c: run_one(c[0], c[1], opts), cases.items()))
    with open(opts.out, "w", encoding="utf-8") as table, open(opts.out + ".jsonl", "w", encoding="utf-8") as raw:
        table.write("| # | stage skill | domain skills | other skills |\n|---|---|---|---|\n")
        for number, found, error in results:
            raw.write(json.dumps({"case": number, "loads": found, "error": error}, ensure_ascii=False) + "\n")
            if error:
                print(f"case {number}: {error}")
            else:
                table.write(row(number, found, project) + "\n")


if __name__ == "__main__":
    main()
