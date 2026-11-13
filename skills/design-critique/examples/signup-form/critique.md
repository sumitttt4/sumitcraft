# Critique: Larkfield sign-up (fixture)

Checked against `brief.md` at 375px and 1280px from the rendered page, not the source. Contrast values were computed
with the WCAG 2.x formula; everything else was read off the screenshots. Smallest coherent change first.

| # | Problem (where) | Evidence | Brief line it breaks | Change made |
|---|---|---|---|---|
| 1 | Labels are placeholders, so they vanish while typing | `#c4c4c4` on white = 1.74:1; filled fields show no label at all | "labels that stay visible" | Real `<label>` above each field |
| 2 | Primary action is the weakest thing on screen | white on `#b9e4bf` = 1.41:1; Cancel is visually equal or stronger | "one obvious primary action" | Solid `#1f6f3a` (6.19:1), Create account first in DOM and on the right |
| 3 | Error says "Invalid" and relies on red | 11px text, `#e53935` 4.23:1, no icon, not linked to the field | "errors that say how to fix them" | Fix-it wording, 14px, `#b3261e` (6.54:1), icon, `aria-describedby`, `aria-invalid` |
| 4 | Field borders nearly invisible | `#e3e3e3` = 1.28:1 (non-text needs 3:1) | older phones, low vision | `#8a8a8a` (3.45:1) |
| 5 | No visible keyboard focus | `outline: none` on inputs | keyboard friendly | `:focus-visible` outlines on inputs and buttons |
| 6 | Tap targets about 36px tall | measured from screenshot | works on phones | `min-height: 44px` |
| 7 | Uneven vertical rhythm (9, 14, 18, 22px gaps) | measured from screenshot | calm | one 16px field gap, 24px before actions |

Not changed on purpose: layout width, heading, colour of the page, copy tone. Those were not problems against the
brief, and changing them would make the before/after harder to read.

Before/after evidence: `node <skill>/scripts/before_after.mjs before.html after.html --widths 375,1280`.
At 375px about 7% of pixels changed, all inside the form box; nothing outside the form moved. The diff image and the
"after" screenshot were inspected by eye.
