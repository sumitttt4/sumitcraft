# Token check: tokens.json

32 checks, **0 failed**.

| Check | Subject | Measured | Needs | |
|---|---|---|---|---|
| contrast | color.ink on color.surface (text: body copy) | 16.88:1 | 4.5:1 | ok |
| contrast | color.ink-muted on color.surface (text: help text) | 7.69:1 | 4.5:1 | ok |
| contrast | color.ink on color.canvas (text: page text) | 14.97:1 | 4.5:1 | ok |
| contrast | color.on-accent on color.accent (text: primary button) | 6.19:1 | 4.5:1 | ok |
| contrast | color.on-accent on color.accent-hover (text: primary button, hover) | 8.26:1 | 4.5:1 | ok |
| contrast | color.danger on color.surface (text: error message) | 6.54:1 | 4.5:1 | ok |
| contrast | color.border on color.surface (ui: input border) | 3.58:1 | 3.0:1 | ok |
| contrast | color.focus on color.surface (ui: focus ring) | 16.88:1 | 3.0:1 | ok |
| contrast | color.disabled-ink on color.disabled-bg (text: disabled label (not required by WCAG, kept readable on purpose)) | 5.20:1 | 4.5:1 | ok |
| scale | space | xs=4, sm=8, md=16, lg=24, xl=40 | strictly increasing in written order | ok |
| scale | font.size | sm=14, md=16, lg=20, xl=28 | strictly increasing in written order | ok |
| states | button | has default, hover, focus-visible, active, disabled | default, hover, focus-visible, disabled | ok |
| refs | button uses color.accent | defined | a defined token | ok |
| refs | button uses color.accent-hover | defined | a defined token | ok |
| refs | button uses color.on-accent | defined | a defined token | ok |
| refs | button uses color.focus | defined | a defined token | ok |
| refs | button uses color.disabled-bg | defined | a defined token | ok |
| refs | button uses color.disabled-ink | defined | a defined token | ok |
| refs | button uses radius.control | defined | a defined token | ok |
| refs | button uses control.min-height | defined | a defined token | ok |
| states | input | has default, hover, focus-visible, invalid, disabled | default, hover, focus-visible, disabled | ok |
| refs | input uses color.border | defined | a defined token | ok |
| refs | input uses color.focus | defined | a defined token | ok |
| refs | input uses color.danger | defined | a defined token | ok |
| refs | input uses radius.control | defined | a defined token | ok |
| refs | input uses control.min-height | defined | a defined token | ok |
| states | card | has default, hover, focus-visible, disabled | default, hover, focus-visible, disabled | ok |
| refs | card uses color.surface | defined | a defined token | ok |
| refs | card uses radius.card | defined | a defined token | ok |
| refs | card uses space.lg | defined | a defined token | ok |
| motion | motion.duration.quick | 120ms | a value in ms | ok |
| motion | motion.duration.settle | 220ms | a value in ms | ok |
