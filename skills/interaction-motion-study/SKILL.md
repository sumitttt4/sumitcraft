---
name: interaction-motion-study
description: Design one interaction (a menu, dialog, toast, drawer, tab switch, drag, button press) as a written specification of trigger, states, timing and easing, interruption, keyboard and focus behaviour, screen-reader semantics, reduced motion and recovery, then build a small runnable study and check its behaviour in a real browser (keyboard operation, focus return, Escape, outside press, mid-transition reversal, and no running animation under prefers-reduced-motion). Use when the user says "design this interaction", "animate this", "how should this menu/dialog behave", "motion spec", "make this accessible to keyboard users", "micro-interaction", or "reduced motion". Not for looping video (code-loop) or whole-page critique (design-critique).
---

# Interaction and motion study

Motion is behaviour, not decoration. An interaction is finished when every state is defined, a second press mid-transition does something sensible, a keyboard user can do everything a mouse user can, focus never gets lost, and people who ask for reduced motion get it. A study makes those decisions explicit and small enough to test before they go into a product.

`<skill>` is the folder with this SKILL.md. Needs Node 18.19+ with Playwright's Chromium. Local only.

## Steps

1. **Write the spec first** from `templates/study-spec.md`: trigger, states, timing (with a reason tied to distance and importance), interruption, keyboard and focus, screen-reader semantics, reduced motion, recovery, checks. If a timing or easing choice is a matter of feel the user has not decided, say it is provisional and offer two contrasting options to compare in the study.
2. **Build the smallest study page**: one HTML file, no framework unless the product needs one, driven by one state attribute so transitions reverse cleanly. Use the platform's semantics (a `<button>` with `aria-expanded` for a disclosure, `<dialog>` for a modal). `examples/disclosure-menu/` is a complete example with its `SPEC.md`.
3. **Check behaviour** (for disclosure-style interactions; extend the script for others):
   ```
   node <skill>/scripts/check_study.mjs study.html --trigger "#trigger" --panel "#panel" --out study-check
   ```
   It reports semantics, keyboard open, visible focus, Escape with focus return, outside press, mid-transition interruption, measured durations and reduced motion, with screenshots.
4. **Watch it** at normal speed, slowed (DevTools animation panel at 10%), and with reduced motion on. Automated checks cover behaviour, not feel.
5. **Report**: the spec, check results, what was watched by a person, provisional choices, and anything the checker does not cover (touch gestures, screen-reader announcements in a real reader).

## Rules

- Hover is never the only way in. Every pointer action has a keyboard path.
- Never queue animations or snap to an end state on interruption; reverse from where it is.
- Reduced motion removes movement, not information.
- Durations are decisions with reasons, not defaults copied from somewhere.

Contract, prerequisites and validation status: [contract.md](contract.md).
