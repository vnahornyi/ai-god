# Worst-case data

A component that looks right with demo data was built against kind data: names that fit one line,
counts that need no plural, every optional field filled. This pass undoes that, one rendered value at
a time. Adapted for React Native from Emil Kowalski's `break-ui` skill
(github.com/emilkowalski/skills, MIT, read 2026-10-27).

`states-and-platform.md` → Content edge cases says *that* these cases must hold; this file is *how*
to find the ones a component was never built against. Values for the developer's own locales live in
the local overlay (`style/worst-case-data-locales.md`); read that file too when it exists.

## Contents

- [Rules](#rules)
- [Build: map, feed, look](#build-map-feed-look)
- [Review](#review)
- [Catalog](#catalog)
- [What you see and what causes it](#what-you-see-and-what-causes-it)
- [Truncate, wrap or clamp](#truncate-wrap-or-clamp)

## Rules

1. **Plausible or schema-backed, never random.** Each worst case is either something a real user
   produces or the actual limit from the validation schema, API type, DB column or `maxLength`.
   `"aaaaaaaa…"` and 5,000-character names prove nothing and get dismissed.
2. **Change the data, not the component.** The worst case enters where demo data does — the mock,
   the story, the fixture, the test props. Never edit markup or styles to produce a break.
3. **Long text is not the whole job.** What ships broken is usually short: `1 items`, a missing
   avatar, an orphaned `—` where an optional role was, an empty list, a badge that grew in
   translation.
4. **Report before fixing.** Several breaks are design or product decisions (truncate or wrap, what
   an empty role shows). Styles stay developer-owned (`figma-inspect`): propose the fix, apply a style
   change only when visual work is assigned.
5. **No toggle, story or fixture is committed without the developer's yes.** Use what the project
   already has to render the component with other data; anything new is scratch unless approved.

## Build: map, feed, look

**1. Map every rendered value** — before or during Gate 1 for a component that renders data:

| Field | Source | Type | Limit | Optional? |
| --- | --- | --- | --- | --- |
| `name` | `customer.fullName` | string | 255 (`schema.ts:14`) | no |
| `itemsCount` | `order.items.length` | int | — | no |
| `role` | `customer.title` | string | 120 | yes |

Include what people forget: counts in headers, relative times, badge and status text, labels that
come from data, accessibility labels, images, and the list itself — its length is a value. Note where
the client and server disagree: a 50-character input that saves to a 255-character column means
longer values already exist.

**2. Feed one worst-case dataset** that hits every applicable catalog row at once, spread across the
first rows (row 1 the long name, row 2 the long email, row 3 the one-letter name) — that is what is
on screen. Plus three cases that are not one dataset: **empty** (0 items), **one** (every count at
exactly 1), **huge** (the realistic upper bound; 1,000+ rows if unpaginated).

**3. Look under the environment worst cases**: the smallest supported screen, the largest system
font scale, the second locale, dark mode, RTL if the app ships an RTL locale. Without a device or
simulator, reason from the code and say which findings were seen and which were inferred.

**4. Report** in Gate 3: every break with its field, the value that caused it, what happens, a fix
and `file:line`; then the decisions for the developer (one line each with a recommendation); then
what already held up. A short report on a sturdy component is a good result.

## Review

For a diff that adds or changes a data-rendering component: map the rendered values from the diff,
then for each ask which catalog rows apply and whether the code handles them — plural through the
i18n layer, a fallback for a missing optional field, an `onError` image fallback, a number formatted
by locale. A finding needs the concrete value and what it does on screen; "might overflow" without a
value is an opinion. Severity comes from the review contract.

## Catalog

Use `example.com` / `.test` domains for emails and URLs.

### People and names

| Value | Breaks |
| --- | --- |
| `Anna-Katharina Schwarzenberg-Müller` | Long, hyphenated; wraps, and the hyphen is a break point |
| `Maximilian Alexander von Hohenberg-Lichtenstein` | Several parts; naive initials, overflow in single-line rows |
| `Åsa Ölçer-Žižek` | marks above the cap height (`Å`, `Ž`) — clipped by a tight `lineHeight` with `overflow: 'hidden'`; sorting |
| `Li` / `X` | Very short; empty-looking name column, one-character initials |
| `Christopher Alexander Montgomery III` | Latin with a suffix; initials `CI` |
| `🦊 Fox` | Emoji first; `name[0]` returns half a surrogate pair |
| `👩🏽‍💻 Priya` | ZWJ sequence; `.length` is 7+, slicing splits it |
| `  Ann   Lee ` | Leading, trailing and repeated spaces; empty "words" in initials |
| *(missing)* | Only a phone or email; the UI needs a fallback |

### Contacts, identifiers, files

| Value | Breaks |
| --- | --- |
| `bartholomew.fitzgerald@northwind-industries-holdings.example.com` | Unbreakable; pushes siblings off the row |
| `first.last+orders@example.com` | Plus-addressing; validation rejecting `+`, truncation hiding the meaningful part |
| `+380 (67) 123-45-67` vs `0671234567` | Formatting drift between input, storage and display |
| `9f8e7d6c-5b4a-4c3d-8e2f-1a0b9c8d7e6f` | Order or tracking id; middle truncation candidate |
| `Return_invoice_FINAL_v12_signed.pdf` | End truncation hides the version and extension |

### Labels and copy from data

| Value | Breaks |
| --- | --- |
| `Men's waterproof trail running shoes for rough terrain, wide fit` | Product title in a card; two-line clamp, row height |
| `Invitation expired 12 days ago` | Long status badge squeezing the name |
| The same label in the project's longest locale | Second-locale length; a fixed-width button overflows |
| Twelve tags on one item | Wraps into a wall; needs a `+8` overflow |
| `""` / `"   "` / `Untitled` | Missing title; collapsed heading, zero-height row |
| `<b>` / `&amp;` / `**bold**` | Must render as literal text |
| A newline inside a single-line field | Doubles the row or silently disappears |

### Numbers and money

| Value | Breaks |
| --- | --- |
| `0` | "0 items", empty progress bar, division by zero in a percentage |
| `1`, `2`, `5`, `11`, `21`, `22` | Locales with several plural forms (Slavic, Arabic: one / few / many) pick a different form for each; a hardcoded `count + ' items'` fails most of them |
| `1284` | Thousands separator: `1 284` in many European locales, `1,284` in `en` |
| `12345678.9` as UAH | `12 345 678,90 ₴` — width of totals; locale-hardcoded separators |
| `-42.5` | Negative sign, refund colour logic |
| `0.1 + 0.2` | `0.30000000000000004` rendered raw |
| `142%`, `-3%` | Progress and discount badges past their bounds |
| `null` / `undefined` / `NaN` | Rendered literally |
| A live value `99 → 100` | Width jitter without tabular figures |

### Collections

| Value | Breaks |
| --- | --- |
| 0 items | Whether an empty state exists, and which one (empty vs filtered-empty) |
| 1 item | A grid that looks broken with one card; "1 of 1" |
| Exactly page size, and page size + 1 | Off-by-one in "showing 40 of 40", an empty page 2 |
| 1,000+ unpaginated | Render time, memory, scroll |
| One item ten times taller | Rows stretching in a grid |
| Two items with identical names | A list where the name is the only distinguishing field |

### Time

| Value | Breaks |
| --- | --- |
| Now | "0 seconds ago" instead of "just now" |
| 12 days, 11 months, 3 years ago | Relative-time thresholds; switch to an absolute date |
| A future date | "in 3 days" vs "-3 days ago" |
| `1970-01-01` | A zero timestamp shown as a real date |
| `2026-12-31T23:30:00-08:00` | A different day in UTC and in Kyiv |

Format with `Intl.RelativeTimeFormat` / `Intl.DateTimeFormat` or the project's date layer — and check
the JS engine actually has the API for that locale (Hermes builds and polyfills vary).

### Images

| Value | Breaks |
| --- | --- |
| An image URL that 404s | No `onError` fallback; blank or broken box |
| No image at all | The fallback itself: initials, placeholder, size parity |
| 4000×200 or 200×4000 | Distortion without `resizeMode: 'cover'`; card height blown out |
| Transparent dark logo in dark mode | Invisible |
| A slow image | Layout jump without fixed dimensions or `aspectRatio` |

### States and environment

| Condition | Breaks |
| --- | --- |
| Partial data — some optional fields filled, others not, in one list | Misaligned rows |
| Every enum value at once (`active`, `invited`, `expired`, `blocked`) | Badge widths vary |
| No permission | Disabled actions; does the row keep its layout? |
| The current user in the list | "You" labels, actions that must not apply to yourself |
| Smallest supported screen (320 pt wide) | Every overflow above at once |
| Largest system font scale | Fixed heights clip growing text |
| Dark mode | Hardcoded colours, invisible borders and logos |
| RTL, if shipped | Icons, chevrons, paddings, order of trailing actions |

## What you see and what causes it

| What you see | Usual cause in React Native | Fix |
| --- | --- | --- |
| Avatar or icon squished into an oval | A fixed box in a row is allowed to shrink | `flexShrink: 0` on the fixed box |
| Text pushes a trailing action (•••, button) off-screen | The text column does not shrink | `flex: 1` / `flexShrink: 1` and `minWidth: 0` on the text column, `flexShrink: 0` on the action |
| A long email or URL runs past the edge or breaks mid-glyph unpredictably | Unbreakable string, no line policy | `numberOfLines` + `ellipsizeMode` per field (see below) |
| A badge wraps onto two lines | The badge shrinks | `flexShrink: 0` on the badge, decide what yields instead |
| Avatar centred against a three-line name looks adrift | `alignItems: 'center'` on rows of varying height | top-align once text can wrap |
| Marks above the cap height (`Å`, `Ž`) or emoji clipped at the top | Fixed `lineHeight` with `overflow: 'hidden'` | looser `lineHeight`, no clipping on text |
| Wrong initials (one letter for a two-letter name, `�` for an emoji-first name) | `name.split(' ')[0][0]` | grapheme-aware split (or the project's helper), first + last word, icon fallback |
| An orphaned `—` or empty line for a missing optional field | A placeholder rendered for nothing | omit the line, or reserve its height intentionally |
| "1 items", "21 items" | Hardcoded plural | the i18n layer's plural (ICU `plural` / Lingui `<Plural>`), never `count + ' …'` |
| Numbers jitter while updating, columns misalign | Proportional figures | `fontVariant: ['tabular-nums']` |
| `1284`, `1,284.000000001`, `NaN` | A raw number rendered | the project's number/currency formatter with the user's locale; guard null |
| A translated button label overflows | Fixed `width` | width from content with `minWidth` |
| Blank image box | No `onError` | fall back to initials or a placeholder |
| Truncated text with no way to read it | `numberOfLines` and nothing else | the full value in a detail view or an accessibility label |
| Scrolling 1,000 rows stutters | Every row rendered | a virtualized list (the project's), or pagination — say which |

## Truncate, wrap or clamp

Every long string forces the choice — per field, not globally, and it is the design's or the
developer's call when the design does not show it:

- **Wrap** what the user needs in full to identify something — names, titles in a detail view. Two
  lines is normal; four means the column is too narrow.
- **Truncate at the end** (`ellipsizeMode: 'tail'`) for secondary metadata where the start carries
  meaning: a description, a last-message preview.
- **Truncate in the middle** (`ellipsizeMode: 'middle'`, single line) when items differ at the end:
  file names, emails sharing a domain, ids.
- **Clamp** (`numberOfLines: 2`) for previews in cards, so card heights stay predictable.
- **Never truncate** prices, amounts, dates or anything the user compares — give them the room.
