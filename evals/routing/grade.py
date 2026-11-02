#!/usr/bin/env python3
"""Grade routing-eval runner tables against evals/routing/cases.md.

  grade.py RUN.md [RUN.md ...]    print per-case pass/fail and totals per run

A runner table row is `| # | stage skill | domain skills | other skills |`. A case passes when the
run's stage skills match the key (or one accepted alternative; for "A + B" the stage is A and B must be
loaded in any column), every required domain skill appears
anywhere in the row, and no must-not skill appears anywhere in the row. A reference file path
(`<skill>/references/<file>.md`, or `<skill> references/<file>.md`) is a read of that file, not a load
of the skill, and is removed before matching; the router tells some stages to read another skill's
reference directly. Case 27's maintenance-file check cannot be read from the table; it is graded on
the skill columns only and marked `*`.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = re.compile(r"\b(?:wf-[a-z-]+|ai-workflow|frontend-craft|figma-inspect|design-patterns|seo|worktree"
                   r"|react-native-animations|apple-neural-engine|realtime-vision-pipeline|skill-creator"
                   r"|figma-design-to-code|design-in-figma|code-review)\b")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


REFERENCE = re.compile(r"\b[a-z-]+(?:/| )references/[\w.-]+\.md|\(references/[^)]*\)")


def names(text):
    return set(SKILL.findall(REFERENCE.sub("", text)))


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


def grade(path, key):
    results = {}
    for line in open(path, encoding="utf-8"):
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
        results[n] = why
    return results


def main(paths):
    key = load_key()
    runs = {os.path.basename(p): grade(p, key) for p in paths}
    print("| # | " + " | ".join(runs) + " |")
    print("|---|" + "---|" * len(runs))
    for n in sorted(key):
        mark = "*" if n == 27 else ""
        row = [("✓" if not r.get(n) else "✗ " + "; ".join(r[n])) if n in r else "—" for r in runs.values()]
        print(f"| {n}{mark} | " + " | ".join(row) + " |")
    totals = [sum(1 for n in key if n in r and not r[n]) for r in runs.values()]
    print("| **Total** | " + " | ".join(f"**{t}/{len(key)}**" for t in totals) + " |")


if __name__ == "__main__":
    main(sys.argv[1:])
