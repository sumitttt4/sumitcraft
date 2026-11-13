---
name: design-critique
description: Critique a rendered interface against its brief and refine it with the smallest coherent changes, then prove what changed with before/after screenshots and pixel diffs at the same widths. Each problem is tied to evidence (a measured contrast, size or spacing, a screenshot region) and to a line in the brief, not to personal taste. Use when the user says "critique this UI", "review my design", "what's wrong with this screen", "make this better", "polish this page", or wants a design refinement they can check. Not for comparing a build to a fixed spec (design-to-code-inspection) or extracting a brand (brand-kit).
---

# Design critique and refinement

A useful critique names a problem, shows the evidence, says which goal it breaks, and proposes the smallest change that fixes it. Then the change is checked on the real pixels. "Make it more modern" is not a finding. "The primary button's text is 1.41:1 on its background, so the one action the brief cares about is the faintest thing on screen" is.

`<skill>` is the folder with this SKILL.md. Needs Node 18.19+ with Playwright's Chromium. Runs locally.

## Steps

1. **Get the brief.** Who it is for, the one job of the screen, constraints (devices, accessibility, brand). If there is no brief, write a three-line one with the user before critiquing. Without a goal, critique turns into taste.
2. **Render what users see.** Screenshot the real page at the widths that matter (`scripts/before_after.mjs` with the same file twice gives clean screenshots), and look at them. Critique the pixels, not the source.
3. **List problems with evidence.** One row each: where, the evidence (measured contrast, size, spacing, alignment; quote the screenshot region), the brief line it breaks, severity (blocks the job / slows it / cosmetic). Measure contrast with the WCAG formula (`<skill>/../design-system-build/scripts/tokens.py --pair FG BG`). Note what works, so a fix does not break it.
4. **Separate taste from problems.** If a point is a matter of style (a typeface, a palette direction), do not "fix" it silently: offer two or three inspectable alternatives and let the user choose.
5. **Make the smallest coherent change** for each blocking problem, in a copy of the page. Group changes that are one decision (a spacing scale, a label pattern). Leave everything else alone.
6. **Prove it:**
   ```
   node <skill>/scripts/before_after.mjs before.html after.html --widths 375,1280 --out before_after
   ```
   Look at `<width>-diff.png` (magenta = changed) and the after shots. The change should sit where you meant it to, and nothing else should move. Re-measure each problem's evidence.
7. **Report** the table (problem, evidence before, evidence after, change), what was intentionally left alone, and open taste questions. A worked example is `examples/signup-form/critique.md`.

## Rules

- Every finding has evidence and a brief line. No unexplained adjectives.
- Change the minimum. Redesigning everything makes the before/after meaningless.
- A changed-pixel share is a locator, not a score.
- Do not copy another product's protected assets while "improving" a design.

Contract, prerequisites and validation status: [contract.md](contract.md).
