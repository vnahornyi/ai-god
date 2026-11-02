# Out of scope — subagents that commit, merge or push on their own

**Idea.** Let implementation subagents commit their work (or enable auto-merge) so parallel tasks
finish without the developer.

**Why not.** Every commit in ai-god goes through a staged set the developer saw (decision 0002).
A subagent's commit would skip that stop, and the orchestrating session could not show the full set
before it lands. Subagents never stage, commit or push (global Git rule 5).

**Reopen when.** Never by an agent's proposal. Only the developer can change the Git rules, in chat.
