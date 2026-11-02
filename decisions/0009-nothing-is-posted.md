# 0009 — Nothing is posted on the developer's behalf

**Context.** Review threads, PR comments and replies are public and read as the developer's own
voice. A drafted reply invites pasting it unread; a posted one cannot be taken back cleanly.

**Decision.** The agent posts no comment, reply, review, approval, reaction or resolved thread
anywhere, and drafts no reply text. Review output explains each point — claim, whether the premise
holds, evidence, verdict — and the developer writes any comment. The only writes outside the repo
are the title and description of the developer's own PR and own tracker issue, and creating a
tracker issue on the developer's explicit request, after the developer has seen the exact text.

**Consequences.** `ai-review-replies` explains each AI comment instead of wording a reply;
`wf-peer-review` and `wf-implement` list points worth raising, not comments to paste. `gh pr
comment`, `gh pr review` and `gh issue comment` are denied in the runtimes that have a permission
layer. The guard's learning loop still reads the developer's own replies once posted.

**Source.** The developer, 2026-11-02; `global/AGENTS.md` → Publishing.
