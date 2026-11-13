---
name: visual-reference-analysis
description: Study a visual reference (a poster, page, screenshot, frame, product shot) by measuring its structure (palette and coverage, value distribution, saturation, where the detail sits by thirds, quiet space, balance, dominant line direction), then writing a reasoned analysis of composition, hierarchy, type, colour, texture and interaction, and finally making an original study that applies the principles without copying the reference's protected assets. Use when the user says "analyse this design", "why does this look good", "break down this poster/layout", "what makes this work", "I want something in this spirit", or shares a reference image for inspiration. Not for extracting a company's brand kit (brand-kit) or reviewing the user's own UI against a brief (design-critique).
---

# Visual reference analysis

Looking at a reference and saying "nice" teaches nothing. This skill measures what can be measured, reasons about what cannot, and then proves the understanding by making something new with the same principles and none of the same assets.

`<skill>` is the folder with this SKILL.md. Needs Python 3.9+ with numpy, and ffmpeg (or `FFMPEG`). Local only: the image is never uploaded.

## Steps

1. **Check the source and rights.** Where is the reference from, and what may be done with it? Analysis for learning is fine; copying its artwork, logo, photography, characters or wording into new work is not. Keep third-party references out of anything distributable.
2. **Measure:**
   ```
   python <skill>/scripts/analyze_image.py reference.png --out analysis
   ```
   It writes `analysis.md` (palette with coverage, dark/mid/light shares, chroma, detail by thirds, quiet space, detail centroid, mirror similarity, edge direction), `analysis.json`, and `overlay.svg` (grid shares, centroid and palette drawn over the image). Open the overlay and check the numbers agree with what you see.
3. **Write the analysis** as a table: composition, hierarchy, type, colour and value, texture, interaction (for UI or motion references), direction. Each row says what is there (with the measurement where one exists) and why it works or what it costs. Then list **principles to reuse** and **things not to reuse**. See `examples/poster-study/notes.md`.
4. **Make an original study**: new subject, new shapes, new words, the same principles. Render it and run the analyser on it too. Matching *structure* numbers (one accent colour, a similar quiet-space share, opposite-corner balance) with different content is the point; matching pixels is copying.
5. **Show both side by side** and report what transferred, what did not, and which choices are taste calls for the user (offer alternatives rather than picking a personal style for them).

## Rules

- Measurements describe structure. They do not score beauty and do not replace looking.
- Never trace, re-colour or crop a protected reference into the study.
- Type in studies is set in code, so it is legible and editable.

Contract, prerequisites and validation status: [contract.md](contract.md).
