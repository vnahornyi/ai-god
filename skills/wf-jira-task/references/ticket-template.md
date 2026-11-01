# Ticket template

Use the block for the language the developer chose. Keep every heading; write `—` where a section
does not apply.

## EN

```markdown
**Title:** <verb + object, ≤ 80 chars>

## Context
Why: the user or business problem. Links: docs, design (frame name), epic.

## Scope
- behaviour, screens, platforms included

## Out of scope
- …

## Acceptance criteria
- [ ] conditions a user or QA can observe — not "code is written"

## Work plan
| # | Block | What I do | What takes time here | Share |
|---|---|---|---|---|
| 1 | Reading into current logic | how <module> works today, its tests | legacy X, two platforms | ~10% |
| 2 | Agreeing the contract | field `…` with backend (who) | waiting for an answer | ~5% |
| 3 | Implementation: <part 1> | … | … | … |
| 4 | Implementation: <part 2> | … | … | … |
| 5 | Tests | scenarios covered | … | … |
| 6 | Device testing | iOS (…), Android (…), browsers | device matrix | … |
| 7 | Regression | existing flows using the changed code | … | … |
| 8 | Review and rework | ~N rounds expected | … | … |
| 9 | Release / docs | if applicable | … | … |

## Dependencies & risks
- risk → effect on the estimate (e.g. "field missing in API → next gradation")

## Estimate
<the developer's number, or "not set">
```

## UA

```markdown
**Назва:** <дієслово + обʼєкт, ≤ 80 символів>

## Контекст
Навіщо: проблема користувача або бізнесу. Посилання: дока, дизайн (назва фрейму), епік.

## Обсяг
- поведінка, екрани, платформи, що входять

## Поза обсягом
- …

## Критерії приймання
- [ ] умови, які може побачити користувач або QA — не "код написано"

## План робіт
| # | Блок | Що роблю | Що тут забирає час | Частка |
|---|---|---|---|---|
| 1 | Розібратись у поточній логіці | як працює <модуль>, його тести | легасі X, дві платформи | ~10% |
| 2 | Узгодити контракт | поле `…` з бекендом (хто) | очікування відповіді | ~5% |
| 3 | Реалізація: <частина 1> | … | … | … |
| 4 | Реалізація: <частина 2> | … | … | … |
| 5 | Тести | які сценарії покриваю | … | … |
| 6 | Тестування на пристроях | iOS (…), Android (…), браузери | матриця пристроїв | … |
| 7 | Регресія | наявні флоу, що користуються зміненим кодом | … | … |
| 8 | Ревʼю та правки | очікувано ~N раундів | … | … |
| 9 | Реліз / документація | якщо застосовно | … | … |

## Залежності й ризики
- ризик → вплив на оцінку (напр. "поля нема в API → наступна градація")

## Оцінка
<цифра девелопера або "не вказано">
```

Drop the **Share / Частка** column when there is no number the developer gave or accepted.
