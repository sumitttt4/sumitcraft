---
name: design-to-code-inspection
description: Compare an implemented web page with a supplied reference or written spec at several viewport widths, and report measured mismatches (box sizes and positions, font sizes and weights, colours, radii, element counts, visibility, tap-target size, horizontal overflow, and optional reference-screenshot pixel difference) instead of a vague quality score. Use when the user says "does this match the design", "check my implementation against the mockup/spec", "pixel check", "compare to the Figma export", "responsive check", or before handing a UI build back to a designer. Not for judging whether the design itself is good (use design-critique) or for building tokens (use design-system-build).
---

# Design-to-code inspection

A design review that says "looks a bit off" cannot be acted on. This skill turns the reference into a list of measurable expectations, measures the real page in a real browser at each width, and reports expected next to measured. A person still looks at the screenshots: numbers say *where* the build differs, people decide *which* differences matter.

`<skill>` below is the folder that holds this SKILL.md. Needs Node 18.19+ with Playwright and its Chromium (run the SumitCraft doctor if unsure). Everything runs locally; a URL is only opened if you give one.

## Steps

1. **Get the reference.** A written spec, design tokens, a design-tool export with measurements, or reference screenshots at known widths. If only a picture exists, ask for the 3 to 6 numbers that matter most (content width, type sizes, key colours, spacing) rather than guessing them from pixels.
2. **Write `spec.json`** next to the page (format at the top of `scripts/inspect_layout.mjs`; full example in `examples/pricing-card/spec.json`). One check per decision in the reference: a box dimension, a style property, a count, a minimum tap target. Pick widths the product actually supports (default 375, 768, 1280).
3. **Run it:**
   ```
   node <skill>/scripts/inspect_layout.mjs spec.json --out inspection
   node <skill>/scripts/inspect_layout.mjs spec.json --reference-dir refs   # also diff refs/<width>.png
   ```
   It writes `inspection/report.md`, `report.json` and `shot-<width>.png`, and exits 1 on any mismatch. Every page also gets a horizontal-overflow check.
4. **Look at the shots** at every width, then sort the mismatches: real build bugs, spec errors (the reference was wrong or ambiguous), and acceptable differences (font rendering, sub-pixel rounding). Write the sorting into the report rather than deleting checks.
5. **Fix and re-run** until the remaining mismatches are all explained. Report: widths checked, mismatches found and fixed, mismatches accepted and why, and anything the spec did not cover.

## Rules

- Report measurements, never a "premium" or "polish" score.
- Pixel diffs vary with fonts, OS and anti-aliasing. Treat a reference-pixel failure as "go look", and compare only screenshots from the same browser and platform.
- Inspect only pages the user owns or is building. Use fictional data in fixtures.
- Do not edit the reference to make the check pass. If the reference was wrong, say so and record it.

## Example

`examples/pricing-card/` holds an original fixture: `spec.json`, `index.html` with four planted problems (fixed card width that overflows on phones, 8px instead of 12px radius, a 36px-tall button, 12px fine print) and `fixed.html` that meets the spec. Running the command on each shows the check failing on the bad version (10 mismatches across 3 widths) and passing on the fixed one.

Contract, prerequisites and validation status: [contract.md](contract.md).
