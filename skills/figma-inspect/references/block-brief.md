# Block brief

The prompt for one background subagent in `figma-inspect` → Visual work, step 4. Fill every `<…>`; leave out a section only
when it is empty. Keep it to this block: no other block's rows, no Figma links, no conversation history.

```text
You style one block of a UI so it matches a Figma design. Work only inside <absolute worktree path>.
Subagents never stage, commit, or push.

Block: <name>.
Files you may edit: <absolute paths>. Edit no other file; if the block needs one, stop and report.
Do not add or change logic, handlers, data, navigation, text or i18n keys. Do not open Figma.

Project conventions:
- Styling method: <StyleSheet / styled-components / Tailwind / CSS modules …>, as in <example file>.
- Tokens: <theme file>; use a token only where the table names it.
- Components to reuse: <component → path>.
- House style: <the few rules from frontend-craft house-style that apply here>.

Values — use exactly these and nothing else; no rounding, no defaults of your own:
| element | node | property | value | source |
|---|---|---|---|---|
<rows>

Motion (when present): <rows: trigger, property, from → to, duration, easing or spring>.
Implement it as <absolute path>/skills/react-native-animations/SKILL.md says (UI thread, no animated
layout properties).

Assets, already in place: <local paths>. Reference them; create no other asset.
Visual target: <absolute path to the block's screenshot>.

Checks to run when done: <exact commands>.

Report, nothing else:
1. Files changed.
2. For each table row: the file and line where it landed, or why it could not be applied.
3. Any value you needed that is not in the table — named, not written.
4. The checks' output.
```
