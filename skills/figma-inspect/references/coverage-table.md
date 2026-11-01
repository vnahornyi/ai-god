# Coverage table

Kept in the chat or in the task's plan — never as a separate file.

```markdown
Frame: <name> · node `<id>` · states in scope: default, empty, error, dark
Inventory: <N> nodes · Table: <N> rows ✅

| Layer path | Node id | What it is for the skeleton | Status |
|---|---|---|---|
| Modal / Header / Title | `I…;18795:336154` | text — "Товари" → i18n key `…` | mapped |
| Modal / Header / Close | `I…;18795:336153` | action — close modal | mapped |
| Card / Message M | `I…;20487:511440` | state — review status message (`Message=on`) | mapped |
| Card / Button-2.0 | `I…;20486:511176` | action — "Оцінити товар" (`Button=on`) | mapped |
| Card / foto / image | `I…;12136:274807` | image — product photo | mapped |
| HomeIndicator | `I…;20527:400019` | system chrome | decor — dev styles |
```

**What it is:** container · text (content → i18n key) · action · list · state (variant value) ·
image · component `<Name>` · decor.

**Status:**
- `mapped` — present in the skeleton;
- `hidden` — not visible in any state in scope; listed, not built;
- `decor — dev styles` — purely visual, the developer handles it;
- `out of scope — approved by dev <date>`.

**States from variant axes** get their own rows, one per value the logic must handle
(`Message=on/off`, `Button=on/off`, message text variants).

**Gate:** inventory count = row count, and no interactive element or state left unmapped.

**Developer's style list** at the end: component → node id → what needs styling.
