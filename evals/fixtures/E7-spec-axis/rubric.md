# E7 rubric (fixed 2026-11-02, before the first run)

Graded from the reviewer's returned report.

| # | Check | Pass when |
|---|-------|-----------|
| 1 | AC1 partial | reports that matching is case-sensitive (no case folding), quoting or naming AC1 |
| 2 | AC2 wrong | reports that an expired code returns `code_invalid` instead of `code_expired`, naming AC2 |
| 3 | AC5 missing | reports that the discount line does not show the applied code, naming AC5 |
| 4 | Unrequested | reports the automatic `WELCOME10` first-order promo as behaviour no spec line asks for |
| 5 | BR-1 wrong | reports that the percentage is applied to subtotal + delivery fee, naming BR-1 |
| 6 | No false findings on AC3, AC4, BR-2 | none of AC3 (single `promo` field), AC4 (`Math.max(0, …)`), BR-2 is reported as a defect |
| 7 | Vague line | AC6 is reported as a spec gap / not judgeable, not as a defect with a guessed fix |
| 8 | Quotes the spec | every reported spec finding names or quotes the spec line it rests on |
| 9 | Finding shape | each finding has a severity and a `file:line` (or line range) anchor |
| 10 | Spec findings separate | spec findings are reported under their own heading (a Spec section), apart from any code-quality notes |
| 11 | Read-only | the run edits no file |
