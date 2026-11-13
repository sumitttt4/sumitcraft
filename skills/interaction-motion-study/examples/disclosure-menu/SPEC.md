# Interaction study: garden actions menu (disclosure)

| Field | Decision |
|---|---|
| Trigger | Click or tap on the "Actions" button; Enter or Space when focused. Never hover alone. |
| States | closed, opening (180 ms), open, closing (180 ms). No disabled state in this study. |
| Timing | 180 ms, ease-out `cubic-bezier(.2, 0, 0, 1)`, 4 px drop and 2% scale: a small panel travelling a short distance. Opening and closing use the same curve so a reversal looks continuous. |
| Interruption | One attribute (`data-open`) drives a CSS transition, so a second press mid-way reverses from the current position. `visibility` switches with a delay on close only, so the panel cannot be clicked while invisible. |
| Keyboard and focus | Enter/Space opens and moves focus to the first link; Arrow keys move between links; Escape closes and returns focus to the button; Tab out of the menu closes it. 3 px focus ring. |
| Screen reader | `<button aria-expanded aria-controls>`; links in a list. Disclosure pattern, not `role=menu`, because these are navigation links. |
| Reduced motion | Duration becomes 0 ms: the panel appears instantly. |
| Recovery | Escape, outside press, Tab away. Nothing can be lost by closing. |
| Checks | `check_study.mjs index.html` (all 8 pass). `hover-only.html` shows the common mistakes and fails 6 of 8. |

Provisional choices: the timing values and easing are a neutral starting point, not a measured preference.
