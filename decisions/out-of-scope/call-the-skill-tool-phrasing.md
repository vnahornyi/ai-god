# Out of scope — "Call the Skill tool" phrasing in skills and the router

**Idea.** Word routing lines as runtime tool calls ("Call the Skill tool with `wf-plan`") because
some guides report that explicit tool names trigger loading more reliably.

**Why not.** Skills are agent-neutral: they name capabilities, and the adapters map them to each
runtime's tools. A tool name in a skill is wrong for the other runtimes, and `bin/lint-skills`
flags runtime tool names as a leak. The routing eval scores the current wording 30 / 29 / 29 of 30
(2026-11-02); no miss traces to phrasing.

**Reopen when.** A routing-eval miss is shown to come from the wording, and an adapter-level fix
cannot address it.
