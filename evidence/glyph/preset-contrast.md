# Glyph starter-kit presets, measured in Chromium

WCAG 2.x ratios of the computed colours (4.5:1 for normal text). Measured by SumitCraft; the presets are Glyph's.

| Preset | Text on bg | Muted on bg | Button text on accent | Overflow at 375 px |
|---|---:|---:|---:|---:|
| default | 19.80 | 6.05 | 19.80 | 0 px |
| bold | 19.68 | 10.48 | 3.28 | 0 px |
| brutalist | 21.00 | 12.63 | 8.59 | 0 px |
| cinematic | 18.69 | 8.08 | 18.69 | 0 px |
| commerce | 19.80 | 6.05 | 18.88 | 0 px |
| dark-technical | 20.12 | 8.19 | 20.12 | 0 px |
| editorial | 16.75 | 6.50 | 18.25 | 0 px |
| luminous | 19.17 | 5.86 | 17.72 | 0 px |
| luxury | 17.48 | 5.28 | 18.88 | 0 px |
| playful | 16.50 | 5.81 | 5.10 | 0 px |
| retro | 13.09 | 5.48 | 4.30 | 0 px |
| trust | 17.85 | 7.58 | 6.70 | 0 px |
| warm-organic | 13.88 | 6.08 | 5.76 | 0 px |

Below 4.5:1: bold button 3.28:1, retro button 4.30:1

## Findings for Glyph (not changed here; the bundle is kept as published)

Buttons use 14px weight-500 text (`.g-btn`), which is normal-size text under WCAG, so 4.5:1 applies.

| Preset | Pair | Measured | Smallest same-hue fix |
|---|---|---:|---|
| bold | `#fff` on `--g-accent: #ff4f2b` | 3.28:1 | `#e52700` (4.54:1) |
| retro | `#fff` (inherited `--g-on-accent`) on `--g-accent: #d9480f` | 4.30:1 | `#d2460f` (4.54:1) |

Alternatives that keep the bright accent: dark text on the accent, or 18.66px+ bold button text. Glyph's own
`review/contrast.json` covers its website tokens, not these starter presets.
