# E7 — Spec-axis review of a promo-code change

The change under review is `src/promo.ts` (new file; treat the whole file as the diff). There is no
repository history, PR or Jira; the ticket below is the full spec.

**Ticket PROJ-41 — Promo code at checkout**

Acceptance criteria:

- AC1: The entered code is trimmed and matched case-insensitively.
- AC2: An unknown code returns the error `code_invalid`; a known but expired code returns `code_expired`.
- AC3: An order carries at most one code; applying a second code replaces the first.
- AC4: A discount never makes the order total negative.
- AC5: The discount line shows the applied code and the discounted amount.
- AC6: The promo field should feel responsive.

Business rules (from the plan):

| ID | Condition | Expected |
|---|---|---|
| BR-1 | A percentage code | applies to the item subtotal only, never to the delivery fee |
| BR-2 | A fixed-amount code | subtracts its amount from the item subtotal |
