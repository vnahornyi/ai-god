# 0001 — No handoff, state, segment, review or fixes-plan files

**Context.** The first `ai-workflow` (archive commit `f44129b`) moved work between stages through
files: handoffs, segments, review gates, a state script (`workflow.py`). The lifecycle was rewritten
in `30fde35` (−1,080 lines across 19 files) and the leftovers removed in `400aecf`.

**Decision.** A task has at most one file: its plan, written by `wf-plan` and corrected in place.
Everything else — review findings, fixes, escalations, the next action — lives in the conversation,
`git status` and the diff. A context switch carries one compact prompt, not a file. The developer
deletes plans; the agent never stages one.

**Consequences.**
- One home per meaning: a fact is not kept in both a file and the conversation.
- Nothing for the developer to clean up after a task; nothing stale for the next session to trust.
- A new session must be briefed in a prompt (`ai-workflow` §6); that prompt is the only carrier.
- The only file `wf-retro` writes is its row in the project's implementation log.

**Source.** `global/AGENTS.md` → Task routing; `ai-workflow` §4 and §6; root `AGENTS.md` → One
home per meaning.
