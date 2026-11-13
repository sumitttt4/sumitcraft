---
name: design-system-build
description: Turn a set of coherent design decisions into design tokens and reusable components, then check them like code. Compiles tokens JSON (colour, space, radius, type, motion, aliases) into CSS custom properties with a generated reduced-motion block, and checks WCAG contrast for every foreground/background pair that will really be used, broken references, non-increasing scales, duplicate values, missing interaction states, and hard-coded colours or sizes that bypass the tokens. Use when the user says "set up design tokens", "make a design system", "turn this style into components", "check my colour contrast", "our CSS has magic numbers everywhere", or wants a UI kit that stays consistent. Not for extracting another company's brand (brand-kit) or judging a finished screen (design-critique).
---

# Design system in implementation

A design system is a small number of decisions, written once and reused everywhere. It earns its keep only if the decisions are checkable: every text colour readable on the backgrounds it actually sits on, one spacing scale, every interactive component with hover, focus, disabled and error states, and no stray values that drift away from the system.

`<skill>` is the folder with this SKILL.md. `scripts/tokens.py` is standard-library Python 3.9+ (`py` on Windows). Everything is local.

## Steps

1. **Collect the decisions** the user has already made (a brand kit, an existing stylesheet, a mockup, or a direction they chose). If a decision is genuinely a matter of taste and has not been made, offer two or three inspectable options (palette, type scale, spacing and motion, written as token files) and let the user choose. Do not invent a personal style for them.
2. **Write `tokens.json`**: groups for colour, space, radius, font, motion and anything layout needs, plus `pairs` (every foreground/background combination the UI will use, marked `text`, `large-text` or `ui`) and `components` (tokens each component uses and the states it defines). Use `{group.name}` aliases when two names are one decision. Format and checks: top of `scripts/tokens.py`; full example: `examples/garden-ui/tokens.json`.
3. **Compile and check:**
   ```
   python <skill>/scripts/tokens.py tokens.json --css tokens.css --report token-report.md
   ```
   Fix every failure at the token level, not with one-off overrides. A failing pair is a design decision to revisit with the user, not a number to fudge.
4. **Build the components** on the CSS variables only, with every state: default, hover, focus-visible (a visible ring), active where it matters, disabled, invalid for inputs. Use a responsive layout that works at 375px without horizontal scroll.
5. **Audit the stylesheet** for values that bypass the system:
   ```
   python <skill>/scripts/tokens.py --audit-css components.html
   ```
6. **Look at it.** Screenshot the component page at phone and desktop widths (`<skill>/../design-critique/scripts/before_after.mjs page.html page.html`), tab through it with a keyboard, and check reduced motion. Then report: tokens, check results, what is provisional, and what still needs the user's taste decision.

## Rules

- Contrast is checked on the pairs that are actually used, not on the palette in the abstract.
- One decision, one name. A second name for the same value is an alias, on purpose.
- The generated CSS is never edited by hand; the JSON is the source.
- Tokens copied from another company's brand stay out of distributable files unless rights permit.

## Example

`examples/garden-ui/` (an original, made-up product): `tokens.json` passes all 32 checks; `tokens-broken.json` is a deliberately broken copy that fails 11 (contrast, a missing reference, a non-increasing scale, duplicates, missing card states, a duration in seconds); `components.html` uses only the variables and passes the CSS audit. The first draft of the passing file actually failed 3 checks (recorded in `examples/garden-ui/evidence/`), which is why the checks run before anything is built.

Contract, prerequisites and validation status: [contract.md](contract.md).
