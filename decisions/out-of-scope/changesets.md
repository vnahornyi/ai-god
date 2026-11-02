# Out of scope — changesets or a CHANGELOG

**Idea.** Track ai-god releases with changesets or a hand-written CHANGELOG.

**Why not.** ai-god has one developer and no versioned consumers: it is installed by symlink from
`main`. The commit history, the eval result files and these decision records already say what
changed and why; a changelog would be a second home for the same meaning.

**Reopen when.** ai-god is published as a plugin or package that others install by version.
