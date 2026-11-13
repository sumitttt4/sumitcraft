# Interaction check: hover-only.html

8 checks, **6 failed**.

| Check | Measured | Needs | |
|---|---|---|---|
| semantics | <div> role=null aria-expanded=null | <button> with aria-expanded | **FAIL** |
| focus-visible | trigger never received keyboard focus | a visible focus indicator | **FAIL** |
| keyboard-open | Tab never reached the trigger in 10 presses | trigger reachable by keyboard | **FAIL** |
| escape | not testable without keyboard access | closed, focus back on trigger | **FAIL** |
| outside-close | opened by click=true, after outside press visible=false | closes on outside press | ok |
| interruption | after open then close 40 ms apart: visible=true, aria-expanded=null | closed, and state agrees with the attribute | **FAIL** |
| timing | panel transition-duration: 0.45s, 0.45s | reported for the spec to judge | ok |
| reduced-motion | 30 ms after opening: running animations=2, visible=false | no running animation, already visible | **FAIL** |

Automated checks cover behaviour, not feel. Watch it at normal speed and with reduced motion before calling it done.
