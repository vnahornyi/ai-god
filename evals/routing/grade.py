#!/usr/bin/env python3
"""Grade routing-eval runner tables against evals/routing/cases.md.

  grade.py RUN.md [RUN.md ...]    print per-case pass/fail and totals per run

A runner table row is `| # | stage skill | domain skills | other skills |`. A case passes when the
run's stage skills match the key (or one accepted alternative; for "A + B" the stage is A and B must be
loaded in any column), every required domain skill appears
anywhere in the row, and no must-not skill appears anywhere in the row. A reference file path
(`<skill>/references/<file>.md`, `<skill> references/<file>.md`, or `<skill> (references only)`) is a read of that file, not a load
of the skill, and is removed before matching; the router tells some stages to read another skill's
reference directly. Case 27's maintenance-file check cannot be read from the table; it is graded on
the skill columns only and marked `*`.

Two rows the key's matching alone would pass also fail: a skill outside this repo on a case a project
skill covers (cases.md: third-party skills are must-not there; the review engine that `wf-review`
and `wf-peer-review` run is not third-party), and a cell that is not a list of skill names, which
cannot be graded.

  grade.py --self-test            run the built-in cases
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = re.compile(r"\b(?:wf-[a-z-]+|ai-workflow|frontend-craft|figma-inspect|design-patterns|seo"
                   r"|worktree|react-native-animations|apple-neural-engine|realtime-vision-pipeline"
                   r"|skill-creator|figma-design-to-code|design-in-figma|code-review)(?![\w-])")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


REFERENCE = re.compile(r"\b[a-z-]+(?:/| )references/[\w.-]+\.md|\(references/[^)]*\)|\b[a-z-]+ \(references[^)]*\)")
NAME = re.compile(r"[a-z][a-z0-9-]*(?::[a-z0-9-]+)?")


def names(text):
    return set(SKILL.findall(REFERENCE.sub("", text)))


def project_skills():
    root = os.path.join(HERE, "..", "..", "skills")
    # wf-worklog is a personal skill in the private overlay; the key names it.
    personal = os.path.join(HERE, "..", "..", "local", "skills")
    mine = set(os.listdir(personal)) if os.path.isdir(personal) else set()
    # run_real.py records overlay skills as "personal".
    return set(os.listdir(root)) | {"wf-worklog", "personal"} | mine


def foreign_and_unreadable(columns, project):
    """Skill names outside this repo, and tokens that are not a skill name at all."""
    foreign, unreadable = set(), []
    for column in columns:
        text = re.sub(r"\([^)]*\)", "", REFERENCE.sub("", column)).replace("`", "")
        for token in re.split(r",|;|\+|\band\b", text):
            token = token.strip().rstrip(".")
            if not token or token.lower() == "none" or token in ("—", "-"):
                continue
            if not NAME.fullmatch(token):
                unreadable.append(token)
            elif token not in project:
                foreign.add(token)
    return foreign, unreadable


def load_key():
    key = {}
    for line in open(os.path.join(HERE, "cases.md"), encoding="utf-8"):
        if not re.match(r"^\| \d+ \|", line):
            continue
        n, _prompt, stage, domain, must_not = cells(line)
        stage_sets, also = [], set()
        if "+" in stage:
            first, *rest = [s.strip() for s in stage.split("+")]
            stage_sets = [names(first)]
            also = names(" ".join(rest))
        else:
            for option in re.split(r"\bor\b", stage.split(",")[0]):
                option = option.strip()
                stage_sets.append(set() if option.startswith("none") else names(option))
        key[int(n)] = {
            "stage": stage_sets,
            "also": also,
            "domain": names(domain),
            "must_not": names(must_not),
            "no_wf": "any wf-*" in must_not,
        }
    return key


def grade(lines, key):
    results = {}
    project = project_skills()
    for line in lines:
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        c = cells(line)
        n = int(c[0])
        row = names(" ".join(c[1:]))
        k = key[n]
        stage = names(c[1]) - {"ai-workflow"} - k["also"]
        why = []
        if not k["also"] <= row:
            why.append(f"missing {sorted(k['also'] - row)}")
        if stage not in k["stage"]:
            why.append(f"stage {sorted(stage) or 'none'}")
        if not k["domain"] <= row:
            why.append(f"missing {sorted(k['domain'] - row)}")
        bad = (k["must_not"] & row) | ({s for s in row if s.startswith("wf-")} if k["no_wf"] else set())
        if bad:
            why.append(f"loaded {sorted(bad)}")
        foreign, unreadable = foreign_and_unreadable(c[1:], project)
        if row & {"wf-review", "wf-peer-review"}:
            foreign.discard("code-review")
        covered = any(k["stage"]) or k["also"] or k["domain"]
        if covered and foreign:
            why.append(f"third-party {sorted(foreign)}")
        if unreadable:
            why.append(f"unreadable {unreadable}")
        results[n] = why
    return results


def self_test():
    key = load_key()
    cases = [
        ("| 4 | wf-implement | none | none |", True),
        ("| 4 | wf-implement | none | docx, simplify |", False),
        ("| 5 | wf-review | none | code-review |", True),
        ("| 4 | wf-implement | none | code-review |", False),
        ("| 7 | wf-peer-review | none | wf-review/references/ai-review-guard.md |", True),
        ("| 7 | wf-peer-review | none | wf-review (references only) and all of it |", False),
        ("| 1 | wf-plan | figma-inspect, frontend-craft (Plan mode) | none |", True),
        ("| 14 | none | none | wf-worklog |", True),
        ("| 22 | none | none | deep-research |", True),
        ("| 22 | wf-plan | none | none |", False),
        ("| 36 | wf-implement | figma-inspect, frontend-craft | none |", True),
        ("| 36 | wf-implement | figma-inspect-extra, frontend-craft | none |", False),
    ]
    failures = 0
    for row, should_pass in cases:
        n = int(cells(row)[0])
        why = grade([row], key)[n]
        if (not why) != should_pass:
            failures += 1
            print(f"FAIL {row} -> {why or 'pass'}")
    print(f"self-test: {failures} failure(s)")
    return 1 if failures else 0


def main(paths):
    key = load_key()
    runs = {os.path.basename(p): grade(open(p, encoding="utf-8"), key) for p in paths}
    print("| # | " + " | ".join(runs) + " |")
    print("|---|" + "---|" * len(runs))
    for n in sorted(key):
        mark = "*" if n == 27 else ""
        row = [("✓" if not r.get(n) else "✗ " + "; ".join(r[n])) if n in r else "—" for r in runs.values()]
        print(f"| {n}{mark} | " + " | ".join(row) + " |")
    totals = [sum(1 for n in key if n in r and not r[n]) for r in runs.values()]
    print("| **Total** | " + " | ".join(f"**{t}/{len(key)}**" for t in totals) + " |")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    main(sys.argv[1:])
