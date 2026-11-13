# Interaction study: <name>

| Field | Decision |
|---|---|
| Trigger | What starts it (click, tap, key, hover, focus, scroll, timer). Hover alone is never the only way in. |
| States | Every state, including the in-between ones: closed, opening, open, closing, disabled, error, empty. |
| Timing | Duration and easing for each transition, and why (distance travelled, size, importance). |
| Interruption | What happens if the trigger fires again mid-transition (reverse from the current position, never jump or queue). |
| Keyboard and focus | Keys that operate it, where focus goes on open, where it returns on close, focus trap or not, visible focus ring. |
| Screen reader | Role and state attributes (aria-expanded, aria-controls, live region), what is announced. |
| Reduced motion | What replaces the motion under prefers-reduced-motion (instant, or opacity only). |
| Recovery | How the user gets out from any state (Escape, outside click, back button) and what happens on failure. |
| Checks | The observable checks `check_study.mjs` (or a person) should confirm. |
