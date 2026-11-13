# Interaction check: index.html

8 checks, **0 failed**.

| Check | Measured | Needs | |
|---|---|---|---|
| semantics | <button> role=null aria-expanded=false | <button> with aria-expanded | ok |
| focus-visible | outline 3px solid, shadow none | a visible focus indicator | ok |
| keyboard-open | Tab reached trigger; after Enter visible=true, aria-expanded=true | visible and aria-expanded=true | ok |
| escape | after Escape visible=false, focus on trigger=true | closed, focus back on trigger | ok |
| outside-close | opened by click=true, after outside press visible=false | closes on outside press | ok |
| interruption | after open then close 40 ms apart: visible=false, aria-expanded=false | closed, and state agrees with the attribute | ok |
| timing | panel transition-duration: 0.18s, 0.18s, 0s | reported for the spec to judge | ok |
| reduced-motion | 30 ms after opening: running animations=0, visible=true | no running animation, already visible | ok |

Automated checks cover behaviour, not feel. Watch it at normal speed and with reduced motion before calling it done.
