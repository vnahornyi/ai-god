# 2026-11-09 — routing eval on real skill loads

First run of `evals/routing/run_real.py`: one fresh `claude -p` session per prompt, tools limited to
Skill and Read, no MCP, an empty working directory, one run per prompt and model. Skills and router at
`110fad8`; `run_real.py` and cases 31–35 land in the commit that adds this file. Graded with the
stricter `grade.py` from `76a3141`. Raw tables and load orders: `raw/2026-11-09-*`.

| Mapping | All 35 | Cases 1–30 | Last self-report on cases 1–30 |
|---|---|---|---|
| Opus 5.5 · medium | 30 | 25 | 29 |
| Sonnet 5.5 · medium | 31 | 26 | 29 |
| Haiku 5.5 · xhigh | 28 | 23 | 29 |

The self-report column came from another method and a looser grader, and its tables were not kept, so
the gap is an indication, not a measured effect. Runs have n = 1 per case.

## Misses

| Case | Opus | Sonnet | Haiku | Miss |
|---|---|---|---|---|
| 1 | | ✗ | | `frontend-craft` not loaded |
| 3 | | ✗ | ✗ | `frontend-craft` not loaded; Sonnet loaded no stage |
| 8 | ✗ | | ✗ | `react-native-animations` not loaded |
| 16 | ✗ | ✗ | ✗ | `frontend-craft` not loaded; Haiku also missed `react-native-animations` |
| 20 | | | ✗ | `wf-plan` loaded with `wf-implement` |
| 26 | ✗ | | ✗ | `frontend-craft` not loaded |
| 27 | ✗ | | ✗ | `wf-jira-task` loaded for a request to add a skill |
| 28 | ✗ | ✗ | ✗ | `frontend-craft` not loaded |

Domain skills account for most misses. The router loads them when "the actual files in scope" trigger
them, and these sessions have no repository, so part of this is the empty directory and not a router
fault. The fixture run below separates the two.

## In a repository (`--fixture`)

The same 35 prompts and key, in a copy of `evals/routing/fixture-rn` (a small React Native app), with
read-only Glob and Grep added. Raw: `raw/2026-11-09-fixture-*`.

| Mapping | Empty directory | Fixture repository |
|---|---|---|
| Opus 5.5 · medium | 30 | 34 |
| Sonnet 5.5 · medium | 31 | 32 |
| Haiku 5.5 · xhigh | 28 | 32 |

| Case | Opus | Sonnet | Haiku | Miss |
|---|---|---|---|---|
| 8 | | | ✗ | `react-native-animations` not loaded |
| 9 | | ✗ | | no stage loaded |
| 16 | | ✗ | | `frontend-craft` not loaded |
| 26 | | | ✗ | `frontend-craft` not loaded |
| 27 | ✗ | | ✗ | `wf-jira-task` loaded with `wf-implement` |
| 28 | | ✗ | | `frontend-craft` not loaded |

Most empty-directory misses came from the missing repository, so no router change follows from them.
Case 27 is the one miss repeated on the same mappings in both conditions. `run_real.py` counts a Read
of a `SKILL.md` as a load, so a session reading that skill as an example of the format would score the
same; the first runs did not record which it was. Three reruns each on Opus and Haiku, with `run_real.py` logging how each skill arrived, show `wf-jira-task` was only read every time, so case 27 is a measurement artifact and not a routing miss (`raw/2026-11-09-case27-*`). The table and scores above are left as run. The other misses each appear on one mapping, once.
In case 33 (commit) Sonnet and Haiku loaded nothing, not even the router; the key accepts that.

## Decisions from this run

- **No fallback row in the router.** Cases 31–35 (questions that need tools, running tests, commit,
  comparing repositories, a rename) were added because the router has no row for them. All passed on
  every mapping on the unchanged router, so there is no observed failure to fix.
- The router was skipped only where it may be: pure questions (10, 22, 23), plus direct loads of the
  right skill (17 on Sonnet and Haiku; 19 and 30 on Sonnet).

## Not verified

Other runtimes. Variance between runs. Behaviour in a larger, real repository. What the sessions did
after loading their skills.
