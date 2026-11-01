# Estimation model

## Contents

- The scale
- What the estimate must cover
- Step 0 — Risk profile (decides which lines exist)
- Block A — Development (raw)
- Block B — Additional time, always shown
- Reporting format (chat only)
- Source

Estimate in hours: compute raw lines, then snap the total to the company scale. The scale value is
the estimate; the raw lines make it auditable.

Two workers are priced, and mixing them up is the main source of error:

- **Development** — the STRONG_GENERAL implementation model with the developer driving it.
  *Calibration: the Development table below was set when implementation ran on Opus 5 at medium.
  Implementation now runs on the adapter's trial mapping for STRONG_GENERAL (since 2026-10-13); these
  numbers are **unmeasured for it** — an implementation artifact, not a measurement. Recalibrate from
  the project memory `implementation-log` (written by `wf-retro`) once five rows share one
  implementer: compare `Dev est. h` with `Actual h`, take the median deviation, adjust the table,
  remove this note.*
- **Everything else** — reviewing the diff, testing on devices, regressions, review rounds,
  coordination — is an average developer at human speed. These lines do not shrink because AI wrote
  the code.

## The scale

The default scale. When the local overlay has `company/estimation.md` (global instructions → Local
overlay), its scale and source win. No other values.

**0.5 · 1 · 3 · 7 · 18 · 28 · 40 hours.**

| Value | Typically |
|---|---|
| `0.5` | A bug or a minimal improvement, a couple of lines |
| `1` | A bug with a complicated reproduction |
| `3` | A very concrete, well-understood small scope |
| **`7`** | **A small task — the target size** |
| `18` | A feature / a module |
| `28` | A module in two parts (admin + front, web + app) |
| `40` | Needs a decomposition conversation before it is written anywhere |

**Round up, with a tolerance that scales with the gap.** Take the lower value only while
`raw ≤ lower + 0.35 × (upper − lower)`:

| Between | Round down while raw ≤ |
|---|---|
| `0.5` → `1` | 0.7 |
| `1` → `3` | 1.7 |
| `3` → `7` | 4.4 |
| `7` → `18` | 10.9 |
| `18` → `28` | 21.5 |
| `28` → `40` | 32.2 |

**Above `7`, offer a decomposition** — the pieces, their seams (contract → shared logic → UI →
tests), dependency order and each piece's value — and let the developer choose between it and the
larger value. Use `18` only when you can name what makes the deliverable indivisible. **Above `28`**,
stop: present the raw total and a split into functionally complete tasks; the split is agreed with
the project manager before any number is written. Tasks of `18`+ carry a work plan in the ticket
(`wf-jira-task`).

Estimate and logged time are independent: never trim a log to an estimate or an estimate to a log.

## What the estimate must cover

Walk this before computing — omissions are why estimates land a gradation low:

- [ ] Reading into the existing logic **and its tests**
- [ ] Planning the task, including the planning session itself
- [ ] Writing the work plan into the ticket
- [ ] Agreeing the API ⇄ frontend protocol and the typing
- [ ] Doing the work, writing tests
- [ ] Testing before QA — browsers, iOS, Android, sizes
- [ ] Impact on other platforms
- [ ] Someone else reviewing the PR, and the rework after it
- [ ] Releasing; documentation

Epic-level planning, release and shared documentation are estimated once for the epic.

## Step 0 — Risk profile (decides which lines exist)

Multipliers price risk; where there is none they are zero.

1. **Blast radius** — `none` (new files nothing imports, or behind an unused flag) · `local` (one
   screen/module, consumers countable on one hand) · `shared` (many consumers, one platform) ·
   `cross-platform` (shared code consumed by several platforms). Count importers with `rg`; do not
   guess.
2. **User-visible change** — `none` · `one flow` · `several flows`.
3. **Proof of correctness** — `compiler` · `tests` · `manual`.

## Block A — Development (raw)

| Line | How |
|---|---|
| Implementation (model + developer) | table below, modifiers applied once |
| Escalations to the frontier model | only when the plan has ⚠️ UNVERIFIED facts / stop conditions or the contract changes: `0.3–1` per expected escalation (*unmeasured*) |
| Reading into existing logic and tests | `0.2` mechanical · otherwise `0.5–1` |
| Self-review of the diff | 30% of implementation |
| Tests, when in scope | 20% of implementation with a setup to copy, 30% without; `0` when proof = `compiler` or tests are a separate ticket (name it) |
| Coordination | `0.5–2` when the task depends on backend, design or another team (say on whom); else `0` |

Implementation hours (*unmeasured for the trial model — see calibration above*):

| Situation | Hours |
|---|---|
| Mechanical change — move/rename, config, dependency bump, import rewiring; no new logic, any file count | 0.2–1 |
| Port from the sibling platform, logic already shared | 0.5–1 |
| Port, logic must first be lifted into shared code | 1.5–3 |
| New feature on an existing API contract | 2–5 |
| New feature with a new or changed contract | 4–10 |
| Test suite for existing behaviour | 1.5–4 |

Modifiers: +25% for shared code consumed by several platforms · +25% for migrations, persisted state,
push or deep links. No modifier for "unfamiliar" or "legacy".

## Block B — Additional time, always shown

Every line appears, even at `0` — then with the reason. Each line states **how** it was counted.

| Line | How it is counted | Zero when |
|---|---|---|
| **Regression pass** | list the existing flows that consume the touched code × `0.1–0.3` h per flow (`local` ≈ 0.3 total, `shared` 0.5–1, `cross-platform` 1–2) | blast = `none` |
| **Device testing by the developer** | the matrix: iOS × N, Android × N, browsers × N, themes/sizes that matter × time per pass (≈ 20% of implementation per platform, min `0.5`) | user-visible = `none` (the regression line covers re-checking) |
| **Review rounds** | expected rounds — `1` for blast `none`/`local`, `2` for `shared`, `2–3` for `cross-platform` or a contract change — × rework per round (`0.2–1` h) + `0.3` for reading reviewer comments | never zero |
| Defect-fix buffer | 10% `local` · 20% `shared` · 30% `cross-platform` of (implementation + tests) | blast = `none` or proof = `compiler` |
| Design polish | hours to match the mockup in every theme, even when the developer does it by hand | no UI change |

Do not double-count: device testing prices **new** behaviour; the regression pass prices **existing**
behaviour.

## Reporting format (chat only)

```markdown
> AI advice, not an estimate. Development calibrated on <model>; the trial model is unmeasured — check it.
**Risk profile:** blast `…` · visible `…` · proof `…`

### A. Development (raw)
| Line | Optimistic | Realistic |
|---|---|---|
| … | | |
| **A. Raw development** | | |

### B. Additional time
| Line | How counted | Optimistic | Realistic |
|---|---|---|---|
| Regression pass | 4 flows × 0.2 | | |
| Device testing | iOS + Android × 1 pass | | |
| Review rounds | 2 rounds × 0.5 + 0.3 | | |
| … | | | |
| **B. Total additional** | | | |

### Summary
A raw `X` h · B `Y` h · **A+B raw `Z` h → gradation `N`**
What would push it to the next gradation: … (+h each)
Assumptions: …
```

Round each line to 0.1 h. Give optimistic (nothing surprises) and realistic (one thing does); the
gradation is taken from the realistic total. When a key input is unknown (no design, unclear
contract), give the gradation for both branches instead of averaging.

**Floor test:** new files nothing imports, proven by the compiler, is a `0.5` or a `1`. **Ceiling
test:** a `cross-platform` blast radius with `manual` proof is where Block B earns its keep — do not
trim it to make the number look nicer.

## Source

The company estimation standard in the local overlay (`company/estimation.md`), when present. It
wins over this file.
